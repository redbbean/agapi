# agapi/agents/agent.py
import json
from typing import Dict, Any
import asyncio
from openai import AsyncOpenAI

from .config import AgentConfig
from .client import AGAPIClient
from .schema import TOOLS_SCHEMA
from .functions import (
    query_by_formula,
    query_by_elements,
    query_by_jid,
    query_by_property,
    find_extreme,
    alignn_predict,
    alignn_ff_relax,
    slakonet_bandstructure,
    diffractgpt_predict,
    xrd_match,
    generate_interface,
)
from IPython.display import HTML, display
import markdown

SYSTEM_PROMPT = """You are a materials science AI assistant with access to computational tools:

**DATABASES:**
- JARVIS-DFT: 80,000+ DFT-calculated materials

**COMPUTATIONAL TOOLS:**
- ALIGNN: ML predictions (formation energy, bandgap, moduli)
- ALIGNN-FF: Structure relaxation
- SlakoNet: Electronic band structure
- DiffractGPT: Structure from XRD
- Intermat: Heterostructure interfaces

**AVAILABLE PROPERTIES (80+ properties):**

*Electronic:* bandgap (optb88vdw, mbj, hse), spillage
*Energetic:* formation_energy, total_energy, ehull, exfoliation_energy
*Mechanical:* bulk_modulus, shear_modulus, elastic_tensor, poisson, density
*Magnetic:* magmom_oszicar, magmom_outcar
*Superconducting:* Tc_supercon
*Dielectric:* epsx, epsy, epsz, mepsx, mepsy, mepsz
*Piezoelectric:* dfpt_piezo_max_eij, dfpt_piezo_max_dij, dfpt_piezo_max_dielectric
*Transport:* n-Seebeck, p-Seebeck, n-powerfact, p-powerfact, ncond, pcond, nkappa, pkappa
*Effective masses:* avg_elec_mass, avg_hole_mass, effective_masses_300K
*Solar:* slme (solar cell efficiency)
*IR modes:* max_ir_mode, min_ir_mode, modes
*Electric field:* max_efg, efg
*Structural:* nat, spg, spg_symbol, crys, dimensionality, formula
*Computational:* func, encut, kpoint_length_unit

**EXAMPLE WORKFLOWS:**
1. Find material → Get POSCAR → Predict with ALIGNN
2. Query database → Calculate band structure with SlakoNet
3. XRD peaks → Predict structure with DiffractGPT
4. Two materials → Generate interface with Intermat

**KEY RULES:**
1. Always report total counts for database queries
2. For predictions, first get POSCAR (via query_by_jid or query_by_formula)
3. For XRD: format peaks as '2theta(intensity),2theta(intensity),...'
4. For interfaces: Miller indices as 'h_k_l' format
5. Chain tools logically: query → get structure → predict
6. Use normalized property names (e.g., "bandgap" → "optb88vdw_bandgap")"""


class AGAPIAgent:
    """
    Unified AGAPI Agent with all computational tools.

    Usage:
        agent = AGAPIAgent()
        result = agent.query_sync("Find SiC and predict with ALIGNN")
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
    ):
        self.api_key = api_key or AgentConfig.DEFAULT_API_KEY
        self.model = model or AgentConfig.DEFAULT_MODEL
        self.temperature = (
            temperature
            if temperature is not None
            else AgentConfig.DEFAULT_TEMPERATURE
        )
        self.max_iterations = (
            max_iterations or AgentConfig.DEFAULT_MAX_ITERATIONS
        )
        self.timeout = timeout or AgentConfig.DEFAULT_TIMEOUT
        self.api_base = api_base or AgentConfig.API_BASE
        self.system_prompt = system_prompt or SYSTEM_PROMPT

        self.agapi_client = AGAPIClient(
            api_key=self.api_key, timeout=self.timeout, api_base=self.api_base
        )
        self.openai_client = AsyncOpenAI(
            base_url=f"{self.api_base}/api", api_key=self.api_key
        )

    async def query(self, query: str, verbose: bool = False) -> str:
        """Execute query (async)"""
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": query},
        ]

        for iteration in range(self.max_iterations):
            if verbose:
                print(f"[Iteration {iteration + 1}/{self.max_iterations}]")

            try:
                response = await self.openai_client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=TOOLS_SCHEMA,
                    tool_choice="auto",
                    temperature=self.temperature,
                )

                message = response.choices[0].message

                if not message.tool_calls:
                    return (
                        message.content
                        if message.content
                        else "No response generated."
                    )

                messages.append(message)

                for tool_call in message.tool_calls:
                    function_name = tool_call.function.name

                    if verbose:
                        print(f"  Calling: {function_name}")

                    try:
                        function_args = json.loads(
                            tool_call.function.arguments
                        )
                    except json.JSONDecodeError as e:
                        result = {"error": f"Invalid JSON: {str(e)}"}
                        messages.append(
                            {
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "content": json.dumps(result),
                            }
                        )
                        continue

                    result = self._execute_function(
                        function_name, function_args
                    )

                    if verbose and "error" in result:
                        print(f"  Error: {result['error']}")

                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": json.dumps(result),
                        }
                    )

            except Exception as e:
                return f"Error: {str(e)}"

        return "Query completed."

    def query_sync(
        self,
        query: str,
        verbose: bool = False,
        render_html: bool = False,
        html_style: str = "bootstrap",  # "bootstrap" or "css"
        max_show: int = 20,
    ) -> Dict[str, Any]:
        """
        Execute query (sync) and optionally render HTML in Jupyter/Colab.

        Parameters
        ----------
        query : str
            User query to the agent.
        verbose : bool
            Show iteration debug prints.
        render_html : bool
            If True, attempt to render the returned result as HTML in the notebook.
        html_style : str
            "bootstrap" (default) or "css" (minimal inline css).
        max_show : int
            Max rows to show when converting materials list to a table.

        Returns
        -------
        Dict[str, Any]
            The structured agent envelope (status/final/history or error).
        """
        import asyncio
        import json

        # Helper: convert a materials list to a Markdown table
        def materials_to_markdown(materials: list, show: int = None) -> str:
            from tabulate import tabulate

            if not materials:
                return "No materials found."

            cols = [
                "jid",
                "formula",
                "spg_symbol",
                "formation_energy_peratom",
                "bulk_modulus_kv",
                "optb88vdw_bandgap",
                "ehull",
            ]
            # ensure columns exist
            cols = [c for c in cols if any(c in m for m in materials)]
            mats = materials[:show] if show else materials

            rows = []
            for m in mats:
                row = []
                for c in cols:
                    v = m.get(c, "")
                    if isinstance(v, float):
                        # compact formatting
                        row.append(f"{v:.4g}")
                    elif v is None:
                        row.append("")
                    else:
                        row.append(str(v))
                rows.append(row)

            headers = [c.replace("_", " ").title() for c in cols]
            return tabulate(rows, headers=headers, tablefmt="github")

        # Helper: make Markdown if agent returned only structured dict
        def envelope_to_markdown(envelope: dict, max_show: int = None) -> str:
            # Prefer assistant final.reply if it's a markdown-friendly string
            final = (
                envelope.get("final") if isinstance(envelope, dict) else None
            )
            if final and isinstance(final, dict):
                # If the assistant provided reply text, use it as header
                header = final.get("reply", "")
                # If structured result exists, convert materials to table
                result_obj = final.get("result")
                if isinstance(result_obj, dict) and "materials" in result_obj:
                    table_md = materials_to_markdown(
                        result_obj.get("materials", []), show=max_show
                    )
                    md = f"**{header}**\n\n{table_md}"
                    return md
                # If result is present but not materials, pretty-print it
                if isinstance(result_obj, dict):
                    # short key-value list
                    lines = [
                        f"- **{k}**: {v}"
                        for k, v in result_obj.items()
                        if k != "materials"
                    ]
                    return f"**{header}**\n\n" + "\n".join(lines)
            # Fallback: try to string convert envelope
            try:
                return json.dumps(envelope, indent=2)
            except Exception:
                return str(envelope)

        # Run the async query in the same way as before
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                try:
                    import nest_asyncio

                    nest_asyncio.apply()
                    envelope = loop.run_until_complete(
                        self.query(query, verbose)
                    )
                except ImportError:
                    raise RuntimeError(
                        "Install nest_asyncio for Jupyter support"
                    )
            else:
                envelope = loop.run_until_complete(self.query(query, verbose))
        except RuntimeError:
            envelope = asyncio.run(self.query(query, verbose))

        # If rendering is requested, try to render HTML in the notebook
        if render_html:
            # Do imports lazily and safely
            try:
                from IPython.display import HTML, display
            except Exception:
                # Not in a notebook environment — ignore rendering
                return envelope

            try:
                import markdown as mdlib
            except Exception:
                # markdown package missing — skip rendering
                return envelope

            # Build markdown text from envelope or assume envelope is markdown string
            md_text = None
            if isinstance(envelope, dict):
                # if the assistant stored a plain markdown string in final.reply, use it
                final = envelope.get("final", {})
                if isinstance(final, dict) and final.get("reply"):
                    md_text = final.get("reply")
                # If result contains materials, convert to markdown table
                result_obj = (
                    final.get("result") if isinstance(final, dict) else None
                )
                if (
                    (not md_text)
                    and isinstance(result_obj, dict)
                    and "materials" in result_obj
                ):
                    md_text = envelope_to_markdown(envelope, max_show)
                # Fallback: stringify the envelope
                if not md_text:
                    md_text = envelope_to_markdown(envelope, max_show)
            else:
                # If older code returns raw string (markdown), handle it
                md_text = str(envelope)

            # Normalize some unicode nuisances (thin spaces, unicode minus)
            md_text = (
                md_text.replace("\u202f", " ")
                .replace("\u2212", "-")
                .replace("\u2013", "-")
                .replace("\u2014", "-")
            )

            # Convert to HTML (enable tables and fenced_code)
            html_body = mdlib.markdown(
                md_text, extensions=["tables", "fenced_code"]
            )

            # Wrap with chosen style
            if html_style == "bootstrap":
                bootstrap = """
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
    .card { max-width: 960px; margin: 12px auto; }
    .card-body table th, .card-body table td { vertical-align: middle; }
    .card-body table { width: 100%; }
    </style>
    """
                # Make the first table use bootstrap table classes for nicer default look
                html_body = html_body.replace(
                    "<table>",
                    '<table class="table table-sm table-striped">',
                    1,
                )
                full_html = f"{bootstrap}<div class='card'><div class='card-body'>{html_body}</div></div>"
            else:
                # minimal inline CSS
                css = """
    <style>
    .table-wrap { max-width: 900px; margin: 12px auto; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial; }
    .table-wrap table { width: 100%; border-collapse: collapse; }
    .table-wrap thead th { text-align: left; border-bottom: 2px solid #e6e6e6; padding: 8px 10px; }
    .table-wrap tbody td { padding: 8px 10px; border-bottom: 1px solid #f3f4f6; }
    .table-wrap tbody tr:nth-child(odd) { background: #fbfbfb; }
    .table-wrap td:nth-child(2) { text-align: right; font-weight:600; }
    </style>
    """
                full_html = f"{css}<div class='table-wrap'>{html_body}</div>"

            # Display in notebook
            try:
                display(HTML(full_html))
            except Exception:
                # If display fails, just return envelope silently
                return envelope

        return envelope

    def query_syncX(self, query: str, verbose: bool = False) -> str:
        """Execute query (sync)"""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                try:
                    import nest_asyncio

                    nest_asyncio.apply()
                    return loop.run_until_complete(self.query(query, verbose))
                except ImportError:
                    raise RuntimeError(
                        "Install nest_asyncio for Jupyter support"
                    )
            else:
                return loop.run_until_complete(self.query(query, verbose))
        except RuntimeError:
            return asyncio.run(self.query(query, verbose))

    def _execute_function(
        self, function_name: str, function_args: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute tool function"""
        function_args["api_client"] = self.agapi_client

        # Map function names to functions
        functions = {
            "query_by_formula": query_by_formula,
            "query_by_elements": query_by_elements,
            "query_by_jid": query_by_jid,
            "query_by_property": query_by_property,
            "find_extreme": find_extreme,
            "alignn_predict": alignn_predict,
            "alignn_ff_relax": alignn_ff_relax,
            "slakonet_bandstructure": slakonet_bandstructure,
            "diffractgpt_predict": diffractgpt_predict,
            "xrd_match": xrd_match,
            "generate_interface": generate_interface,
        }

        func = functions.get(function_name)
        if func:
            return func(**function_args)
        else:
            return {"error": f"Unknown function: {function_name}"}


async def run_agent_query(
    query: str,
    api_key: str = None,
    model: str = None,
    temperature: float = None,
    verbose: bool = False,
) -> str:
    """Async convenience function"""
    agent = AGAPIAgent(api_key=api_key, model=model, temperature=temperature)
    return await agent.query(query, verbose=verbose)


def run_agent_query_sync(
    query: str,
    api_key: str = None,
    model: str = None,
    temperature: float = None,
    verbose: bool = False,
) -> str:
    """Sync convenience function"""
    agent = AGAPIAgent(api_key=api_key, model=model, temperature=temperature)
    return agent.query_sync(query, verbose=verbose)
