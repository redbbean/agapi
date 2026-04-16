# agapi/agents/agent_langchain.py
"""
LangChain manual-loop implementation of the AGAPI Materials Science Agent.
Compatible with LangChain 0.3+ (no AgentExecutor required).

How this differs from the original agent.py and from agent_langchain_max.py
----------------------------------------------------------------------------
Original (agent.py)              This file                agent_langchain_max.py
-------------------------------- ------------------------ ---------------------------
AsyncOpenAI client               ChatOpenAI               ChatOpenAI
Raw dict messages {"role":...}   LangChain message types  LangChain message types
Raw JSON TOOLS_SCHEMA            StructuredTool + Pydantic StructuredTool + Pydantic
Manual for-loop                  Manual for-loop (KEPT)   create_react_agent graph
Manual tool dispatch             Manual tool dispatch      ToolNode (LangGraph)
Manual context truncation        Manual context truncation trim_messages (LangGraph)

The key architectural difference from agent_langchain_max.py: this agent uses a
hand-written for-loop (like the original). LangGraph is NOT imported. The agent
controls when to call the LLM, when to dispatch tools, and when to stop.

Install:
    pip install langchain langchain-openai

Usage:
    from agapi.agents.agent_langchain import AGAPIAgentManual

    agent = AGAPIAgentManual()
    result = agent.query_sync("Find GaN and predict its bandgap")
    print(result)

    # Benchmark interface
    response, tools_called = agent.query_sync_benchmark("Find GaN")
"""

import json
import asyncio
import inspect as _inspect
from typing import Any, Dict, List, Optional, Union

# ── LangChain core ─────────────────────────────────────────────────────────────
from langchain_openai import ChatOpenAI
from langchain_core.tools import StructuredTool
from langchain_core.messages import (
    SystemMessage,
    HumanMessage,
    AIMessage,
    ToolMessage,
)
from pydantic import BaseModel, Field, create_model

# ── AGAPI imports ──────────────────────────────────────────────────────────────
from .config import AgentConfig
from .client import AGAPIClient
from .schema import TOOLS_SCHEMA
from .functions import (
    # Core database queries
    query_by_formula,
    query_by_elements,
    query_by_jid,
    query_by_property,
    find_extreme,
    # Structure prediction / ML
    alignn_predict,
    alignn_ff_relax,
    alignn_ff_single_point,
    alignn_ff_optimize,
    alignn_ff_md,
    slakonet_bandstructure,
    # XRD
    diffractgpt_predict,
    xrd_match,
    generate_xrd_pattern,
    pxrd_match,
    xrd_analyze,
    # Structure manipulation (local, no API)
    generate_interface,
    make_supercell,
    substitute_atom,
    create_vacancy,
    # Microscopy
    microscopygpt_analyze,
    # External databases
    query_mp,
    query_oqmd,
    # Literature
    search_arxiv,
    search_crossref,
    # Protein / biology
    protein_fold,
    openfold_predict,
    # Utilities
    list_jarvis_columns,
)
from .agent import SYSTEM_PROMPT


# ── Complete function registry ─────────────────────────────────────────────────

_FUNCTION_REGISTRY: Dict[str, Any] = {
    "query_by_formula":        query_by_formula,
    "query_by_elements":       query_by_elements,
    "query_by_jid":            query_by_jid,
    "query_by_property":       query_by_property,
    "find_extreme":            find_extreme,
    "alignn_predict":          alignn_predict,
    "alignn_ff_relax":         alignn_ff_relax,
    "alignn_ff_single_point":  alignn_ff_single_point,
    "alignn_ff_optimize":      alignn_ff_optimize,
    "alignn_ff_md":            alignn_ff_md,
    "slakonet_bandstructure":  slakonet_bandstructure,
    "diffractgpt_predict":     diffractgpt_predict,
    "xrd_match":               xrd_match,
    "generate_xrd_pattern":    generate_xrd_pattern,
    "pxrd_match":              pxrd_match,
    "xrd_analyze":             xrd_analyze,
    "generate_interface":      generate_interface,
    "make_supercell":          make_supercell,
    "substitute_atom":         substitute_atom,
    "create_vacancy":          create_vacancy,
    "microscopygpt_analyze":   microscopygpt_analyze,
    "query_mp":                query_mp,
    "query_oqmd":              query_oqmd,
    "search_arxiv":            search_arxiv,
    "search_crossref":         search_crossref,
    "protein_fold":            protein_fold,
    "openfold_predict":        openfold_predict,
    "list_jarvis_columns":     list_jarvis_columns,
}


# ─────────────────────────────────────────────────────────────────────────────
# Dynamic schema building (ported from agent_langchain_max.py)
# Avoids 29 hand-written Pydantic classes.
# ─────────────────────────────────────────────────────────────────────────────

_JSON_TO_PY: Dict[str, Any] = {
    "string":  str,
    "number":  float,
    "integer": int,
    "boolean": bool,
    "array":   list,
    "object":  dict,
}


def _json_schema_to_pydantic(tool_name: str, parameters: dict) -> type:
    """
    Dynamically build a Pydantic BaseModel from an OpenAI-style JSON schema.
    Required fields become plain types; optional fields become Optional[type].
    """
    properties = parameters.get("properties", {})
    required   = set(parameters.get("required", []))

    fields: Dict[str, Any] = {}
    for prop_name, prop_schema in properties.items():
        py_type = _JSON_TO_PY.get(prop_schema.get("type", "string"), Any)
        desc    = prop_schema.get("description", "")
        default = prop_schema.get("default", None)

        if prop_name in required:
            fields[prop_name] = (py_type, Field(description=desc))
        else:
            fields[prop_name] = (Optional[py_type], Field(default, description=desc))

    model_name = "".join(w.capitalize() for w in tool_name.split("_")) + "Input"
    return create_model(model_name, **fields)


_PY_ANNOTATION_TO_PY = {
    str: str, float: float, int: int, bool: bool,
    list: list, dict: dict,
}


def _signature_to_pydantic(func) -> type:
    """
    Build a Pydantic BaseModel from a Python function signature.
    Used for functions in functions.py that are NOT covered by TOOLS_SCHEMA.
    Skips 'api_client' (injected internally).
    """
    sig    = _inspect.signature(func)
    fields: Dict[str, Any] = {}

    for param_name, param in sig.parameters.items():
        if param_name in ("api_client", "self"):
            continue

        annotation = param.annotation
        default    = param.default

        if annotation is _inspect.Parameter.empty:
            py_type = str
        elif hasattr(annotation, "__origin__"):
            args    = getattr(annotation, "__args__", (str,))
            py_type = next((a for a in args if a is not type(None)), str)
        else:
            py_type = _PY_ANNOTATION_TO_PY.get(annotation, str)

        desc = f"{param_name} parameter"

        if default is _inspect.Parameter.empty:
            fields[param_name] = (py_type, Field(description=desc))
        else:
            fields[param_name] = (Optional[py_type], Field(default, description=desc))

    model_name = "".join(w.capitalize() for w in func.__name__.split("_")) + "Input"
    return create_model(model_name, **fields)


# ── Result truncation ──────────────────────────────────────────────────────────

_RESULT_KEEP_KEYS = [
    "status", "message", "error", "formula", "jid",
    "spg_symbol", "formation_energy_peratom", "bulk_modulus_kv",
    "bandgap", "bandgap_source", "mbj_bandgap", "optb88vdw_bandgap", "hse_gap",
    "ehull", "total", "showing", "materials", "property", "range",
    "POSCAR",
    "band_gap_eV", "vbm_eV", "cbm_eV", "image_filename",
    "formation_energy", "energy_eV", "bandgap_optb88vdw", "bandgap_mbj",
    "bulk_modulus", "shear_modulus", "piezo_max_dielectric", "Tc_supercon",
    "natoms", "forces_eV_per_A", "stress",
    "converged", "initial_energy", "final_energy", "energy_change",
    "steps_taken", "forces_max", "num_atoms", "computation_time",
    "steps_completed", "average_temperature", "final_temperature",
    "temperatures", "energies",
    "relaxed_poscar", "modified_poscar", "supercell_poscar", "final_poscar",
    "original_atoms", "supercell_atoms", "scaling_matrix",
    "original_formula", "new_formula",
    "substituted_indices", "num_substitutions",
    "removed_indices", "num_vacancies", "new_atoms",
    "peaks", "num_peaks_found", "num_peaks_reported", "peak_table",
    "description", "wavelength", "predicted_structure", "matched_structure",
    "matched_poscar", "query", "best_match", "top_matches", "similarity",
    "pdb_structure", "sequence_length", "protein_length",
    "dna1_length", "dna2_length",
    "results", "count", "total_results",
    "papers",
    "heterostructure_atoms", "film_indices", "substrate_indices",
    "film_thickness", "substrate_thickness", "separation", "elements",
    "atom_counts",
]

_POSCAR_KEYS = [
    "POSCAR",
    "relaxed_poscar", "modified_poscar", "supercell_poscar",
    "final_poscar",
    "predicted_structure",
    "matched_poscar",
    "heterostructure_atoms",
]

_LIST_TRUNCATE_KEYS = {
    "materials":    20,
    "results":      20,
    "papers":       10,
    "temperatures": 50,
    "energies":     50,
    "forces_max":   50,
    "trajectory":    5,
    "full_pattern":  0,
}

_MAX_RESULT_CHARS = 30_000
_MAX_POSCAR_CHARS = 5_000


def _truncate_result(result) -> str:
    """Trim large tool results to fit the context window."""
    if not isinstance(result, dict):
        text = str(result)
        return text[:_MAX_RESULT_CHARS] if len(text) > _MAX_RESULT_CHARS else text

    raw = json.dumps(result, default=str)
    if len(raw) <= _MAX_RESULT_CHARS:
        return raw

    trimmed = {k: result[k] for k in _RESULT_KEEP_KEYS if k in result}

    for key in _POSCAR_KEYS:
        if key in trimmed and isinstance(trimmed[key], str):
            val = trimmed[key]
            if len(val) > _MAX_POSCAR_CHARS:
                lines = val.splitlines()
                trimmed[key] = "\n".join(lines[:10] + ["..."] + lines[-5:])

    for key, max_items in _LIST_TRUNCATE_KEYS.items():
        if key in trimmed:
            if max_items == 0:
                del trimmed[key]
            elif isinstance(trimmed[key], list) and len(trimmed[key]) > max_items:
                trimmed[key] = trimmed[key][:max_items]

    return json.dumps(trimmed, default=str)


# ─────────────────────────────────────────────────────────────────────────────
# Tool factory
# ─────────────────────────────────────────────────────────────────────────────

def _build_tools(api_client: AGAPIClient) -> List[StructuredTool]:
    """
    Build LangChain StructuredTools for ALL functions in functions.py.

    Strategy A — function is in TOOLS_SCHEMA (schema.py):
        Build Pydantic schema from the JSON schema (rich descriptions).

    Strategy B — function is NOT in TOOLS_SCHEMA (newer additions):
        Build Pydantic schema from the Python function signature via inspect.
        Use the function's docstring as the tool description.

    Both strategies inject api_client via closure so the LLM never sees it.
    """
    def _make_run(f):
        def _run(**kwargs):
            result = f(api_client=api_client, **kwargs)
            return _truncate_result(result)
        return _run

    tools      = []
    schema_names = set()

    # Strategy A: schema.py-covered functions
    for entry in TOOLS_SCHEMA:
        fn_def      = entry.get("function", entry)
        name        = fn_def["name"]
        description = fn_def.get("description", "")
        parameters  = fn_def.get("parameters", {})

        func = _FUNCTION_REGISTRY.get(name)
        if func is None:
            continue

        schema_names.add(name)
        pydantic_model = _json_schema_to_pydantic(name, parameters)

        tools.append(StructuredTool.from_function(
            func=_make_run(func),
            name=name,
            description=description,
            args_schema=pydantic_model,
        ))

    # Strategy B: functions.py extras not yet in schema.py
    for name, func in _FUNCTION_REGISTRY.items():
        if name in schema_names:
            continue

        description    = (func.__doc__ or name).strip().splitlines()[0]
        pydantic_model = _signature_to_pydantic(func)

        tools.append(StructuredTool.from_function(
            func=_make_run(func),
            name=name,
            description=description,
            args_schema=pydantic_model,
        ))

    return tools


# ─────────────────────────────────────────────────────────────────────────────
# Main agent class
# ─────────────────────────────────────────────────────────────────────────────

class AGAPIAgentManual:
    """
    LangChain manual-loop AGAPI Materials Science Agent.

    Uses LangChain message types and StructuredTool, but controls the agentic
    loop explicitly — a for-loop that calls the LLM, dispatches tool calls, and
    stops when there are no more tool calls (or max_iterations is reached).

    This is architecturally closest to the original agent.py; the main additions
    are typed message objects, dynamic Pydantic schemas for all 29 tools, and
    richer result truncation.

    Usage:
        agent = AGAPIAgentManual()
        result = agent.query_sync("Find GaN and predict its bandgap")

        # Benchmark interface
        response, tools_called = agent.query_sync_benchmark("Find GaN")
    """

    def __init__(
        self,
        api_key: str = None,
        model: str = None,
        temperature: float = None,
        max_iterations: int = None,
        timeout: int = None,
        api_base: str = None,
        system_prompt: str = None,
        verbose: bool = False,
    ):
        self.api_key        = api_key        or AgentConfig.DEFAULT_API_KEY
        self.model          = model          or AgentConfig.DEFAULT_MODEL
        self.temperature    = temperature    if temperature is not None else AgentConfig.DEFAULT_TEMPERATURE
        self.max_iterations = max_iterations or AgentConfig.DEFAULT_MAX_ITERATIONS
        self.timeout        = timeout        or AgentConfig.DEFAULT_TIMEOUT
        self.api_base       = api_base       or AgentConfig.API_BASE
        self.system_prompt  = system_prompt  or SYSTEM_PROMPT
        self._verbose       = verbose

        # AGAPI backend client (unchanged from original)
        self.agapi_client = AGAPIClient(
            api_key=self.api_key,
            timeout=self.timeout,
            api_base=self.api_base,
        )

        # Build tools + name→tool lookup
        self.tools = _build_tools(self.agapi_client)
        self._tool_map: Dict[str, StructuredTool] = {t.name: t for t in self.tools}

        # LLM with tools bound
        self._llm = ChatOpenAI(
            base_url=f"{self.api_base}/api",
            api_key=self.api_key,
            model=self.model,
            temperature=self.temperature,
        ).bind_tools(self.tools)

        # Populated after every query for inspection
        self.last_intermediate_steps: List[Dict[str, Any]] = []

    # ── Core tool loop (sync) ──────────────────────────────────────────────────

    def _run_loop(
        self,
        query: str,
        verbose: bool = False,
        show_tool_results: bool = False,
        max_context_messages: int = 20,
    ):
        """
        Agentic loop: LLM → tool calls → LLM → … → final answer.
        Returns (final_text: str, steps: list[dict]).
        """
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=query),
        ]
        steps: List[Dict[str, Any]] = []

        for iteration in range(self.max_iterations):
            if verbose:
                print(f"[Iteration {iteration + 1}/{self.max_iterations}]")

            # Trim history to avoid context overflow
            if len(messages) > max_context_messages:
                messages = [messages[0]] + messages[-(max_context_messages - 1):]

            response = self._llm.invoke(messages)

            # No tool calls → we have the final answer
            if not response.tool_calls:
                final_text = response.content or "No response generated."
                if show_tool_results and steps:
                    final_text += "\n\n" + "=" * 70 + "\nRAW TOOL RESULTS:\n" + "=" * 70
                    for i, step in enumerate(steps, 1):
                        final_text += f"\n[Tool Call {i}] {step['tool']}\n"
                        final_text += f"Arguments: {json.dumps(step['args'], indent=2)}\n"
                        obs = step["result"]
                        if len(obs) > 1000:
                            obs = obs[:1000] + "\n... (truncated)"
                        final_text += f"Result: {obs}\n" + "-" * 70 + "\n"
                return final_text, steps

            # Append the assistant turn (with tool_calls metadata)
            messages.append(response)

            # Execute each tool call
            for tc in response.tool_calls:
                name    = tc["name"]
                args    = tc["args"]
                call_id = tc["id"]

                if verbose:
                    print(f"  → {name}({args})")

                tool = self._tool_map.get(name)
                if tool is None:
                    result_str = json.dumps({"error": f"Unknown tool: {name}"})
                else:
                    try:
                        result_str = tool.invoke(args)
                    except Exception as exc:
                        result_str = json.dumps({"error": str(exc)})

                steps.append({"tool": name, "args": args, "result": result_str})
                messages.append(ToolMessage(content=result_str, tool_call_id=call_id))

        return "Query completed (max iterations reached).", steps

    # ── Async wrapper ──────────────────────────────────────────────────────────

    async def _run_loop_async(self, query: str, **kwargs):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, lambda: self._run_loop(query, **kwargs)
        )

    # ── Public API ─────────────────────────────────────────────────────────────

    def query_sync(
        self,
        query: str,
        verbose: bool = False,
        render_html: bool = False,
        html_style: str = "bootstrap",
        max_show: int = 20,
        return_dict: bool = False,
        show_tool_results: bool = False,
        max_context_messages: int = 20,
    ) -> Union[str, Dict[str, Any]]:
        """
        Synchronous query — drop-in for AGAPIAgent.query_sync.

        Args:
            query:                Natural language materials science query
            verbose:              Print each iteration / tool call
            render_html:          Render markdown as HTML (Jupyter only)
            html_style:           "bootstrap" or "css"
            max_show:             Max rows in HTML tables
            return_dict:          Return raw dict instead of text
            show_tool_results:    Append raw tool traces to the response
            max_context_messages: Max messages kept in history (default 20)
        """
        final_text, steps = self._run_loop(
            query,
            verbose=verbose or self._verbose,
            show_tool_results=show_tool_results,
            max_context_messages=max_context_messages,
        )
        self.last_intermediate_steps = steps

        if return_dict:
            tool_results = []
            for s in steps:
                try:
                    tool_results.append(json.loads(s["result"]))
                except Exception:
                    tool_results.append({"raw": s["result"]})
            out: Dict[str, Any] = {"response": final_text}
            if tool_results:
                out["tool_results"] = tool_results[0] if len(tool_results) == 1 else tool_results
            return out

        if render_html:
            self._render_html(final_text, html_style)

        return final_text

    def query_sync_benchmark(self, query: str) -> tuple:
        """
        Benchmark interface: run query and return (response_text, tools_called).

        Returns:
            response_text (str):  Final answer from the agent.
            tools_called (list):  Ordered list of tool names called, e.g.
                                  ["query_by_formula", "alignn_predict"].
        """
        final_text, steps = self._run_loop(query)
        self.last_intermediate_steps = steps
        tools_called = [s["tool"] for s in steps]
        return final_text, tools_called

    async def query(
        self,
        query: str,
        verbose: bool = False,
        return_dict: bool = False,
        show_tool_results: bool = False,
        max_context_messages: int = 20,
    ) -> Union[str, Dict[str, Any]]:
        """Async query — drop-in for AGAPIAgent.query."""
        final_text, steps = await self._run_loop_async(
            query,
            verbose=verbose or self._verbose,
            show_tool_results=show_tool_results,
            max_context_messages=max_context_messages,
        )
        self.last_intermediate_steps = steps

        if return_dict:
            tool_results = []
            for s in steps:
                try:
                    tool_results.append(json.loads(s["result"]))
                except Exception:
                    tool_results.append({"raw": s["result"]})
            out: Dict[str, Any] = {"response": final_text}
            if tool_results:
                out["tool_results"] = tool_results[0] if len(tool_results) == 1 else tool_results
            return out

        return final_text

    # ── HTML rendering ─────────────────────────────────────────────────────────

    def _render_html(self, text: str, style: str = "bootstrap") -> None:
        """Render markdown as styled HTML inside a Jupyter notebook."""
        try:
            from IPython.display import HTML, display
            import markdown as mdlib
        except ImportError:
            return

        cleaned = (
            text.replace("\u202f", " ")
                .replace("\u2212", "-")
                .replace("\u2013", "-")
                .replace("\u2014", "-")
        )
        body = mdlib.markdown(cleaned, extensions=["tables", "fenced_code"])

        if style == "bootstrap":
            hdr = (
                '<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/'
                'dist/css/bootstrap.min.css" rel="stylesheet">\n'
                "<style>.agapi-card{max-width:960px;margin:20px auto;padding:20px;"
                "border:1px solid #e0e0e0;border-radius:8px;background:white;"
                "box-shadow:0 2px 4px rgba(0,0,0,.1)}</style>\n"
            )
            body = body.replace(
                "<table>",
                '<table class="table table-sm table-striped table-hover">',
            )
            html = f"{hdr}<div class='agapi-card'>{body}</div>"
        else:
            hdr = (
                "<style>.agapi-wrap{max-width:900px;margin:20px auto;padding:20px}"
                ".agapi-wrap table{width:100%;border-collapse:collapse;margin:1em 0}"
                "</style>\n"
            )
            html = f"{hdr}<div class='agapi-wrap'>{body}</div>"

        display(HTML(html))


# ─────────────────────────────────────────────────────────────────────────────
# Convenience wrappers
# ─────────────────────────────────────────────────────────────────────────────

def run_agent_query_sync_lc(query: str, **kwargs) -> Union[str, Dict[str, Any]]:
    """Sync one-liner — no need to instantiate the agent manually."""
    api_key     = kwargs.pop("api_key", None)
    model       = kwargs.pop("model", None)
    temperature = kwargs.pop("temperature", None)
    return AGAPIAgentManual(api_key=api_key, model=model, temperature=temperature).query_sync(query, **kwargs)


async def run_agent_query_lc(query: str, **kwargs) -> Union[str, Dict[str, Any]]:
    """Async one-liner."""
    api_key     = kwargs.pop("api_key", None)
    model       = kwargs.pop("model", None)
    temperature = kwargs.pop("temperature", None)
    return await AGAPIAgentManual(api_key=api_key, model=model, temperature=temperature).query(query, **kwargs)