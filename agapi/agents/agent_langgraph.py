# agapi/agents/agent_langchain.py
"""
LangChain/LangGraph implementation of the AGAPI Materials Science Agent.

What's different from the original agent.py
--------------------------------------------
Original (agent.py)                  This file
------------------------------------  ------------------------------------------
AsyncOpenAI client                    ChatOpenAI  (langchain-openai)
Raw dict messages {"role":...}        LangChain message objects (Human/AI/Tool)
Raw JSON TOOLS_SCHEMA                 StructuredTool + Pydantic schemas
Manual for-loop over iterations       LangGraph create_react_agent graph
Manual tool dispatch (_execute_fn)    ToolNode (LangGraph) via graph
Manual context truncation             LangGraph message history + trim_messages
Print statements for verbose          LangChain BaseCallbackHandler
use_tools=False (separate prompt)     use_tools=False disables tools on the LLM
auto_display_images                   Preserved (post-processing step)

What LangChain/LangGraph features are used
-------------------------------------------
- ChatOpenAI                          LLM wrapper
- StructuredTool + Pydantic           Tool definitions with typed schemas
- create_react_agent (LangGraph)      Full agent loop + ToolNode (replaces for-loop)
- MemorySaver (LangGraph)             In-process message checkpointing
- trim_messages                       Context window management
- ChatPromptTemplate                  System/user prompt construction
- BaseCallbackHandler                 Verbose logging (replaces print statements)
- HumanMessage / AIMessage /
  ToolMessage / SystemMessage         Typed message objects

Install
-------
    pip install langchain langchain-openai langgraph

Usage
-----
    from agapi.agents.agent_langchain import AGAPIAgentLG

    agent = AGAPIAgentLG()

    poscar = '''System
    1.0
    3.263 0.0 0.0
    ...'''

    result = agent.query_sync(
        f"Predict properties using ALIGNN for this structure:\\n{poscar}",
        render_html=True,
    )
    print(result)
"""

import json
import asyncio
from typing import Any, Dict, List, Optional, Union
from uuid import uuid4

# ── LangChain core ─────────────────────────────────────────────────────────────
from langchain_openai import ChatOpenAI
from langchain_core.tools import StructuredTool
from langchain_core.messages import (
    SystemMessage,
    HumanMessage,
    AIMessage,
    ToolMessage,
    trim_messages,
)
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.callbacks import BaseCallbackHandler
from pydantic import BaseModel, Field, create_model

# ── LangGraph ──────────────────────────────────────────────────────────────────
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

# ── AGAPI imports — same files as original agent.py ───────────────────────────
import inspect as _inspect
from .config import AgentConfig
from .client import AGAPIClient
from .schema import TOOLS_SCHEMA          # ← same import as original agent.py
from .functions import (                  # ← all functions from functions.py
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

# No-tool fallback prompt (mirrors original use_tools=False behaviour)
_NOTOOL_SYSTEM_PROMPT = """You are a materials science AI assistant with extensive
knowledge of materials properties, computational methods, and DFT calculations.
Answer from your training knowledge only — you do NOT have access to databases
or computational tools in this mode."""

# Complete function registry — every callable in functions.py
_FUNCTION_REGISTRY = {
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
# Verbose callback — replaces the original print statements
# ─────────────────────────────────────────────────────────────────────────────

class _VerboseCallback(BaseCallbackHandler):
    """LangChain callback that prints tool calls and LLM iterations."""

    def on_tool_start(self, serialized, input_str, **kwargs):
        name = serialized.get("name", "unknown")
        print(f"  → Tool: {name}  args: {str(input_str)[:120]}")

    def on_tool_end(self, output, **kwargs):
        preview = str(output)[:120]
        print(f"  ← Result: {preview}{'...' if len(str(output)) > 120 else ''}")

    def on_tool_error(self, error, **kwargs):
        print(f"  ✗ Tool error: {error}")

    def on_llm_start(self, serialized, prompts, **kwargs):
        print(f"[LLM call]")


# ─────────────────────────────────────────────────────────────────────────────
# Convert TOOLS_SCHEMA → LangChain StructuredTools
#
# The original agent.py passes TOOLS_SCHEMA (OpenAI JSON format) raw to the
# API. Here we parse those same schemas to build Pydantic models dynamically,
# then wrap each function as a StructuredTool — no hand-written schema classes.
# ─────────────────────────────────────────────────────────────────────────────

# JSON schema type → Python type mapping
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
        py_type    = _JSON_TO_PY.get(prop_schema.get("type", "string"), Any)
        desc       = prop_schema.get("description", "")
        default    = prop_schema.get("default", None)

        if prop_name in required:
            fields[prop_name] = (py_type, Field(description=desc))
        else:
            fields[prop_name] = (Optional[py_type], Field(default, description=desc))

    model_name = "".join(w.capitalize() for w in tool_name.split("_")) + "Input"
    return create_model(model_name, **fields)


# Result truncation — keeps essential keys from every function in functions.py
_RESULT_KEEP_KEYS = [
    # Universal
    "status", "message", "error", "formula", "jid",
    # Structure & basic properties (query_by_*, find_extreme)
    "spg_symbol", "formation_energy_peratom", "bulk_modulus_kv",
    "bandgap", "bandgap_source", "mbj_bandgap", "optb88vdw_bandgap", "hse_gap",
    "ehull", "total", "showing", "materials", "property", "range",
    # *** POSCAR from query_by_jid — capital P, exactly as functions.py returns it ***
    "POSCAR",
    # Band structure (slakonet_bandstructure)
    "band_gap_eV", "vbm_eV", "cbm_eV", "image_filename",
    # ALIGNN predict
    "formation_energy", "energy_eV", "bandgap_optb88vdw", "bandgap_mbj",
    "bulk_modulus", "shear_modulus", "piezo_max_dielectric", "Tc_supercon",
    # ALIGNN-FF single point (alignn_ff_single_point)
    "natoms", "forces_eV_per_A", "stress",
    # ALIGNN-FF optimize (alignn_ff_optimize)
    "converged", "initial_energy", "final_energy", "energy_change",
    "steps_taken", "forces_max", "num_atoms", "computation_time",
    # ALIGNN-FF MD (alignn_ff_md)
    "steps_completed", "average_temperature", "final_temperature",
    "temperatures", "energies",
    # Structure manipulation (make_supercell, substitute_atom, create_vacancy)
    "relaxed_poscar", "modified_poscar", "supercell_poscar", "final_poscar",
    "original_atoms", "supercell_atoms", "scaling_matrix",
    "original_formula", "new_formula",
    "substituted_indices", "num_substitutions",
    "removed_indices", "num_vacancies", "original_atoms", "new_atoms",
    # XRD (generate_xrd_pattern, xrd_match, diffractgpt_predict)
    "peaks", "num_peaks_found", "num_peaks_reported", "peak_table",
    "description", "wavelength", "predicted_structure", "matched_structure",
    # PXRD (pxrd_match, xrd_analyze)
    "matched_poscar", "query", "best_match", "top_matches", "similarity",
    # Protein / biology
    "pdb_structure", "sequence_length", "protein_length",
    "dna1_length", "dna2_length",
    # External databases (query_mp, query_oqmd)
    "results", "count", "total_results",
    # Literature (search_arxiv, search_crossref)
    "papers",
    # Interface
    "heterostructure_atoms", "film_indices", "substrate_indices",
    "film_thickness", "substrate_thickness", "separation", "elements",
    "atom_counts",
]

# Large POSCAR-like string fields to trim (not drop) when result is over budget
_POSCAR_KEYS = [
    "POSCAR",                 # query_by_jid — capital P as returned by API
    "relaxed_poscar", "modified_poscar", "supercell_poscar",
    "final_poscar",           # alignn_ff_optimize
    "predicted_structure",    # diffractgpt_predict
    "matched_poscar",         # pxrd_match
    "heterostructure_atoms",  # generate_interface
]

# Large list fields to truncate (cap at N items) when over budget
_LIST_TRUNCATE_KEYS = {
    "materials":    20,   # query_by_* results
    "results":      20,   # mp/oqmd results
    "papers":       10,   # arxiv/crossref results
    "temperatures": 50,   # md trajectory
    "energies":     50,   # md/optimize energy trace
    "forces_max":   50,   # optimize force trace
    "trajectory":    5,   # md/optimize trajectory (can be huge)
    "full_pattern": 0,    # xrd generate — always strip (use 'description' instead)
}

# A single query_by_jid result with a full POSCAR can be ~15-20k chars.
# Keep the budget high enough that POSCAR strings survive un-truncated.
_MAX_RESULT_CHARS = 30_000
_MAX_POSCAR_CHARS = 5_000


def _truncate_result(result: dict) -> str:
    """
    Trim large tool results to fit the context window.
    Mirrors original agent.py logic, extended for all 28 functions.
    """
    if not isinstance(result, dict):
        # Should never happen given functions.py, but be safe
        text = str(result)
        return text[:_MAX_RESULT_CHARS] if len(text) > _MAX_RESULT_CHARS else text

    raw = json.dumps(result, default=str)
    if len(raw) <= _MAX_RESULT_CHARS:
        return raw

    # Build trimmed dict — keep only known-useful keys
    trimmed = {k: result[k] for k in _RESULT_KEEP_KEYS if k in result}

    # Trim large POSCAR strings
    for key in _POSCAR_KEYS:
        if key in trimmed and isinstance(trimmed[key], str):
            val = trimmed[key]
            if len(val) > _MAX_POSCAR_CHARS:
                lines = val.splitlines()
                trimmed[key] = "\n".join(lines[:10] + ["..."] + lines[-5:])

    # Trim or drop large list fields
    for key, max_items in _LIST_TRUNCATE_KEYS.items():
        if key in trimmed:
            if max_items == 0:
                del trimmed[key]   # always strip (e.g. full_pattern)
            elif isinstance(trimmed[key], list) and len(trimmed[key]) > max_items:
                trimmed[key] = trimmed[key][:max_items]

    return json.dumps(trimmed, default=str)


# Python annotation → Pydantic-compatible type mapping for signature-derived schemas
_PY_ANNOTATION_TO_PY = {
    str: str, float: float, int: int, bool: bool,
    list: list, dict: dict,
}


def _signature_to_pydantic(func) -> type:
    """
    Build a Pydantic BaseModel from a Python function signature.
    Used for functions in functions.py that are NOT covered by TOOLS_SCHEMA.
    Skips 'api_client' (injected internally) and keyword-only params with no annotation.
    """
    sig = _inspect.signature(func)
    fields: Dict[str, Any] = {}

    for param_name, param in sig.parameters.items():
        if param_name in ("api_client", "self"):
            continue  # injected — never exposed to the LLM

        annotation = param.annotation
        default    = param.default

        # Resolve annotation to a concrete Python type
        if annotation is _inspect.Parameter.empty:
            py_type = str  # safe fallback
        elif hasattr(annotation, "__origin__"):
            # e.g. Optional[float] → float
            args = getattr(annotation, "__args__", (str,))
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


def _build_tools(api_client: AGAPIClient) -> List[StructuredTool]:
    """
    Build LangChain StructuredTools for ALL functions in functions.py:

    Strategy A — function is in TOOLS_SCHEMA (schema.py):
        Build Pydantic schema from the JSON schema (rich descriptions, same as original).

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

    tools = []
    schema_names = set()

    # ── Strategy A: schema.py-covered functions ────────────────────────────
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

    # ── Strategy B: functions.py extras not yet in schema.py ──────────────
    for name, func in _FUNCTION_REGISTRY.items():
        if name in schema_names:
            continue  # already handled above

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

class AGAPIAgentLG:
    """
    LangGraph-based AGAPI Materials Science Agent.

    Replaces the original manual for-loop with a LangGraph create_react_agent
    graph. All other public methods (query_sync / query) are drop-in compatible.

    Usage:
        agent = AGAPIAgentLG()
        result = agent.query_sync("Find GaN and predict its bandgap")
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

        # AGAPI backend (unchanged)
        self.agapi_client = AGAPIClient(
            api_key=self.api_key,
            timeout=self.timeout,
            api_base=self.api_base,
        )

        # Build typed tools
        self.tools = _build_tools(self.agapi_client)

        # ChatOpenAI — note: no bind_tools() here; create_react_agent does it
        self._llm = ChatOpenAI(
            base_url=f"{self.api_base}/api",
            api_key=self.api_key,
            model=self.model,
            temperature=self.temperature,
        )

        # ChatPromptTemplate for the system message
        # (MessagesPlaceholder carries the conversation history through the graph)
        self._prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            MessagesPlaceholder(variable_name="messages"),
        ])

        # MemorySaver: LangGraph in-process checkpointer
        # Stores full conversation state per thread_id so every query is isolated
        self._memory = MemorySaver()

        # create_react_agent wires LLM + ToolNode + message loop automatically.
        # state_modifier trims history to stay within the context window.
        self._graph = create_react_agent(
            model=self._llm,
            tools=self.tools,
            prompt=self._build_state_modifier(),
            checkpointer=self._memory,
            # recursion_limit maps to max_iterations
        )

        # Populated after every call for inspection
        self.last_intermediate_steps: List[Dict[str, Any]] = []

    def _build_state_modifier(self):
        """
        Returns a state_modifier function that:
        1. Prepends the system prompt, and
        2. Uses trim_messages to cap context (mirrors original max_context_messages).
        """
        system_msg = SystemMessage(content=self.system_prompt)

        def modifier(state):
            messages = state["messages"]
            # trim_messages keeps the most recent messages within token budget
            trimmed = trim_messages(
                messages,
                strategy="last",
                token_counter=len,          # character-count proxy; swap for tiktoken
                max_tokens=18,              # ≈ 20 messages (system + 18 history)
                start_on="human",
                include_system=False,
            )
            return [system_msg] + trimmed

        return modifier

    # ── Internal helpers ───────────────────────────────────────────────────────

    def _extract_steps(self, result: dict) -> List[Dict[str, Any]]:
        """
        Extract tool call steps from LangGraph state messages.

        LangGraph stores the full conversation as a flat list of messages.
        Each tool call produces an AIMessage (with tool_calls) followed by
        one ToolMessage per call (matched by tool_call_id). We use the id
        to match them exactly rather than relying on ordering.
        """
        # Build a map of tool_call_id -> ToolMessage content
        tool_results: Dict[str, str] = {}
        for msg in result.get("messages", []):
            if isinstance(msg, ToolMessage):
                tool_results[msg.tool_call_id] = msg.content

        # Walk AIMessages and pair each tool_call with its result
        steps = []
        for msg in result.get("messages", []):
            if isinstance(msg, AIMessage) and msg.tool_calls:
                for tc in msg.tool_calls:
                    steps.append({
                        "tool":   tc["name"],
                        "args":   tc["args"],
                        "result": tool_results.get(tc["id"]),
                    })
        return steps

    def _format_tool_trace(self, steps: List[Dict[str, Any]]) -> str:
        if not steps:
            return ""
        lines = ["\n\n" + "=" * 70 + "\nRAW TOOL RESULTS:\n" + "=" * 70]
        for i, step in enumerate(steps, 1):
            lines.append(f"\n[Tool Call {i}] {step['tool']}")
            lines.append(f"Arguments: {json.dumps(step['args'], indent=2)}")
            obs = str(step.get("result") or "")
            if len(obs) > 1000:
                obs = obs[:1000] + "\n... (truncated)"
            lines.append(f"Result: {obs}")
            lines.append("-" * 70)
        return "\n".join(lines)

    def _invoke_graph(self, query: str, verbose: bool, use_tools: bool) -> dict:
        """
        Run the LangGraph agent for a single query.
        Each query gets a fresh thread_id so histories don't bleed across calls.
        """
        callbacks = [_VerboseCallback()] if (verbose or self._verbose) else []

        config = {
            "configurable": {"thread_id": str(uuid4())},
            "recursion_limit": self.max_iterations * 4 + 1,
            "callbacks": callbacks,
        }

        if not use_tools:
            # Bypass the graph entirely — plain LLM call with no tools
            llm_notool = ChatOpenAI(
                base_url=f"{self.api_base}/api",
                api_key=self.api_key,
                model=self.model,
                temperature=self.temperature,
            )
            response = llm_notool.invoke(
                [SystemMessage(content=_NOTOOL_SYSTEM_PROMPT),
                 HumanMessage(content=query)],
                config={"callbacks": callbacks},
            )
            return {"messages": [response]}

        return self._graph.invoke(
            {"messages": [HumanMessage(content=query)]},
            config=config,
        )

    async def _invoke_graph_async(self, query: str, verbose: bool, use_tools: bool) -> dict:
        callbacks = [_VerboseCallback()] if (verbose or self._verbose) else []
        config = {
            "configurable": {"thread_id": str(uuid4())},
            "recursion_limit": self.max_iterations * 4 + 1,
            "callbacks": callbacks,
        }

        if not use_tools:
            llm_notool = ChatOpenAI(
                base_url=f"{self.api_base}/api",
                api_key=self.api_key,
                model=self.model,
                temperature=self.temperature,
            )
            response = await llm_notool.ainvoke(
                [SystemMessage(content=_NOTOOL_SYSTEM_PROMPT),
                 HumanMessage(content=query)],
                config={"callbacks": callbacks},
            )
            return {"messages": [response]}

        return await self._graph.ainvoke(
            {"messages": [HumanMessage(content=query)]},
            config=config,
        )

    @staticmethod
    def _extract_text(content) -> str:
        """
        Safely extract plain string from AIMessage content.
        Handles: plain str, None/empty, structured list blocks
        e.g. [{"type": "text", "text": "..."}] from OpenAI-compatible APIs.
        """
        if not content:
            return ""
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            parts = [b["text"] if isinstance(b, dict) and b.get("type") == "text"
                     else b for b in content if isinstance(b, (str, dict))]
            return " ".join(str(p) for p in parts if p)
        return str(content)

    def _process_result(
        self,
        result: dict,
        return_dict: bool,
        show_tool_results: bool,
        auto_display_images: bool,
        verbose: bool,
    ) -> Union[str, Dict[str, Any]]:
        messages = result.get("messages", [])

        # Walk backwards — find last AIMessage with actual text content.
        # The final message may be an AIMessage with only tool_calls and empty text.
        final_text = ""
        for msg in reversed(messages):
            if isinstance(msg, AIMessage):
                candidate = self._extract_text(msg.content)
                if candidate.strip():
                    final_text = candidate
                    break

        # If the model returned no final text (hit recursion limit, or ended on a
        # tool call with no follow-up), synthesise a minimal summary from the steps
        # so callers always receive a non-empty, useful string.
        if not final_text.strip():
            steps_preview = self._extract_steps(result)
            if steps_preview:
                lines = ["Agent completed the following steps:"]
                for i, s in enumerate(steps_preview, 1):
                    result_preview = str(s.get("result") or "")[:200]
                    lines.append(f"  {i}. {s['tool']}({json.dumps(s['args'])[:80]})")
                    lines.append(f"     → {result_preview}")
                final_text = "\n".join(lines)
            else:
                final_text = "No response generated."

        steps = self._extract_steps(result)
        self.last_intermediate_steps = steps

        # Auto-display band structure images (mirrors original behaviour)
        if auto_display_images:
            for step in steps:
                try:
                    data = json.loads(step.get("result") or "{}")
                    if "image_base64" in data:
                        self._display_image(data, verbose=verbose)
                except Exception:
                    pass

        if show_tool_results:
            final_text += self._format_tool_trace(steps)

        if return_dict:
            tool_results = []
            for s in steps:
                try:
                    tool_results.append(json.loads(s["result"] or "{}"))
                except Exception:
                    tool_results.append({"raw": s["result"]})
            out: Dict[str, Any] = {"response": final_text}
            if tool_results:
                out["tool_results"] = tool_results[0] if len(tool_results) == 1 else tool_results
            return out

        return final_text

    # ── Public API (drop-in for AGAPIAgent) ────────────────────────────────────

    def query_sync_benchmark(self, query: str) -> tuple:
        """
        Benchmark interface: run query and return (response_text, tools_called).

        Returns:
            response_text (str):  Final answer from the agent.
            tools_called (list):  Ordered list of tool names called, e.g.
                                  ["query_by_formula", "alignn_predict"].
        """
        result = self._invoke_graph(query, verbose=False, use_tools=True)
        steps  = self._extract_steps(result)
        self.last_intermediate_steps = steps

        messages = result.get("messages", [])
        final_text = ""
        for msg in reversed(messages):
            if isinstance(msg, AIMessage):
                candidate = self._extract_text(msg.content)
                if candidate.strip():
                    final_text = candidate
                    break
        if not final_text.strip():
            final_text = "No response generated."

        tools_called = [s["tool"] for s in steps]
        return final_text, tools_called

    def query_sync(
        self,
        query: str,
        verbose: bool = False,
        render_html: bool = False,
        html_style: str = "bootstrap",
        max_show: int = 20,
        return_dict: bool = False,
        show_tool_results: bool = False,
        use_tools: bool = True,
        auto_display_images: bool = False,
        max_context_messages: int = 20,
    ) -> Union[str, Dict[str, Any]]:
        """
        Synchronous query — drop-in for AGAPIAgent.query_sync.

        All original parameters are supported:
            query, verbose, render_html, html_style, max_show,
            return_dict, show_tool_results, use_tools,
            auto_display_images, max_context_messages
        """
        result = self._invoke_graph(query, verbose, use_tools)
        envelope = self._process_result(
            result, return_dict, show_tool_results, auto_display_images, verbose
        )
        if render_html and isinstance(envelope, str):
            self._render_html(envelope, html_style)
        return envelope

    async def query(
        self,
        query: str,
        verbose: bool = False,
        return_dict: bool = False,
        show_tool_results: bool = False,
        use_tools: bool = True,
        auto_display_images: bool = False,
        max_context_messages: int = 20,
    ) -> Union[str, Dict[str, Any]]:
        """Async query — drop-in for AGAPIAgent.query."""
        result = await self._invoke_graph_async(query, verbose, use_tools)
        return self._process_result(
            result, return_dict, show_tool_results, auto_display_images, verbose
        )

    # ── Image display (unchanged from original) ────────────────────────────────

    def _display_image(self, result: dict, verbose: bool = False):
        try:
            from IPython.display import display, Image, HTML
            import base64

            image_data = base64.b64decode(result["image_base64"])
            band_gap   = result.get("band_gap_eV", "N/A")
            vbm        = result.get("vbm_eV", "N/A")
            cbm        = result.get("cbm_eV", "N/A")

            if isinstance(band_gap, str) and "[" in band_gap:
                try:
                    import ast
                    bg_list = ast.literal_eval(band_gap)
                    if isinstance(bg_list, list) and bg_list:
                        band_gap = f"{bg_list[0]:.4f}"
                except Exception:
                    pass

            html = f"""
<div style="border:3px solid #4CAF50;border-radius:12px;padding:20px;margin:15px 0;
            background:linear-gradient(to bottom,#f8fff8,#fff)">
  <h3 style="margin-top:0;color:#4CAF50">📊 Band Structure</h3>
  <table style="width:100%;border-collapse:collapse">
    <tr><th>Quantity</th><th>Value</th></tr>
    <tr><td><b>Band gap</b></td><td>{band_gap} eV</td></tr>
    <tr><td><b>VBM</b></td><td>{vbm} eV</td></tr>
    <tr><td><b>CBM</b></td><td>{cbm} eV</td></tr>
  </table>
</div>"""
            display(HTML(html))
            display(Image(data=image_data, format="png", width=800))
        except ImportError:
            if verbose:
                print("⚠ Not in Jupyter — image cannot be displayed")
        except Exception as e:
            if verbose:
                print(f"✗ Image display error: {e}")

    # ── HTML rendering ─────────────────────────────────────────────────────────

    def _render_html(self, text: str, style: str = "bootstrap") -> None:
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
            body = body.replace("<table>",
                                '<table class="table table-sm table-striped table-hover">')
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
# Convenience wrappers (mirror originals)
# ─────────────────────────────────────────────────────────────────────────────

def run_agent_query_sync_lc(query: str, **kwargs) -> Union[str, Dict[str, Any]]:
    api_key     = kwargs.pop("api_key", None)
    model       = kwargs.pop("model", None)
    temperature = kwargs.pop("temperature", None)
    return AGAPIAgentLG(api_key=api_key, model=model, temperature=temperature).query_sync(query, **kwargs)


async def run_agent_query_lc(query: str, **kwargs) -> Union[str, Dict[str, Any]]:
    api_key     = kwargs.pop("api_key", None)
    model       = kwargs.pop("model", None)
    temperature = kwargs.pop("temperature", None)
    return await AGAPIAgentLG(api_key=api_key, model=model, temperature=temperature).query(query, **kwargs)
