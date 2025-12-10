# agapi/agents/agent.py
import json
from typing import Dict, Any, Union
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

SYSTEM_PROMPT = """You are a materials science AI assistant with access to computational tools:

**DATABASES:**
- JARVIS-DFT: 80,000+ DFT-calculated materials

**COMPUTATIONAL TOOLS:**
- ALIGNN: ML predictions (formation energy, bandgap, moduli)
- ALIGNN-FF: Structure relaxation
- SlakoNet: Electronic band structure (returns bandgap, VBM, CBM + PNG image)
- DiffractGPT: Structure from XRD
- Intermat: Heterostructure interfaces

**BANDGAP REPORTING RULES:**
- ALWAYS prefer MBJ bandgap (mbj_bandgap) - it's more accurate for semiconductors
- Only use OptB88vdW bandgap (optb88vdw_bandgap) if MBJ is not available
- When reporting bandgaps, indicate which method was used: "(MBJ)" or "(OptB88vdW)"
- For semiconductor queries (C, Si, Ge, GaN, etc.), MBJ values are experimental-quality
- SlakoNet provides tight-binding bandgap estimates

**SLAKONET BAND STRUCTURE:**
- Returns: band_gap_eV, vbm_eV, cbm_eV, and image_base64 (PNG plot)
- Best for small structures (≤10 atoms)
- When calculating band structure, report all three values and mention that image is available

**AVAILABLE PROPERTIES (80+ properties):**
*Electronic:* bandgap (prefer mbj_bandgap, fallback optb88vdw_bandgap, hse_gap), spillage
*Energetic:* formation_energy, total_energy, ehull, exfoliation_energy
*Mechanical:* bulk_modulus, shear_modulus, elastic_tensor, poisson, density
*Magnetic:* magmom_oszicar, magmom_outcar
*Superconducting:* Tc_supercon
*Dielectric:* epsx, epsy, epsz
*Transport:* n-Seebeck, p-Seebeck, n-powerfact, p-powerfact
*Structural:* nat, spg, spg_symbol, spg_number, crys, dimensionality, formula

**EXAMPLE WORKFLOWS:**
1. Find material → Get POSCAR → Predict with ALIGNN
2. Query database → Calculate band structure with SlakoNet → Compare bandgaps
3. Get structure → SlakoNet band structure → Analyze electronic properties
4. XRD peaks → Predict structure with DiffractGPT

**KEY RULES:**
1. Always report total counts for database queries
2. For bandgaps, prefer MBJ over OptB88vdW (indicate which is reported)
3. For predictions, first get POSCAR (via query_by_jid or query_by_formula)
4. For SlakoNet: Report band gap, VBM, CBM; image will be auto-displayed if enabled
5. Chain tools logically: query → get structure → predict/plot"""


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

        # Store tool results for access after query
        self.last_tool_results = []

    def _display_image(self, result: dict, verbose: bool = False):
        """Helper to display band structure image in Jupyter"""
        try:
            from IPython.display import display, Image, HTML
            import base64

            # Decode image
            image_data = base64.b64decode(result["image_base64"])

            # Create styled header with properties
            band_gap = result.get("band_gap_eV", "N/A")
            vbm = result.get("vbm_eV", "N/A")
            cbm = result.get("cbm_eV", "N/A")

            # Clean up band_gap if it's a list string
            if isinstance(band_gap, str) and "[" in band_gap:
                try:
                    import ast

                    band_gap_list = ast.literal_eval(band_gap)
                    if (
                        isinstance(band_gap_list, list)
                        and len(band_gap_list) > 0
                    ):
                        band_gap = f"{band_gap_list[0]:.4f}"
                except:
                    pass

            html = f"""
<div style="border: 3px solid #4CAF50; border-radius: 12px; padding: 20px; margin: 15px 0; max-width: 100%; background: linear-gradient(to bottom, #f8fff8, #ffffff);">
    <h3 style="margin-top: 0; color: #4CAF50; display: flex; align-items: center; gap: 10px;">
        <span style="font-size: 1.5em;">📊</span> Band Structure Plot
    </h3>
    <table style="width: 100%; border-collapse: collapse; margin: 10px 0;">
        <tr style="background: #f0f0f0;">
            <th style="padding: 10px; text-align: left; border-bottom: 2px solid #ddd; font-weight: 600;">Quantity</th>
            <th style="padding: 10px; text-align: right; border-bottom: 2px solid #ddd; font-weight: 600;">Value</th>
        </tr>
        <tr>
            <td style="padding: 10px; border-bottom: 1px solid #eee;"><strong>Band gap</strong></td>
            <td style="padding: 10px; text-align: right; border-bottom: 1px solid #eee; font-weight: 600; color: #2196F3;">{band_gap} eV</td>
        </tr>
        <tr style="background: #fafafa;">
            <td style="padding: 10px; border-bottom: 1px solid #eee;"><strong>Valence-band maximum (VBM)</strong></td>
            <td style="padding: 10px; text-align: right; border-bottom: 1px solid #eee; font-weight: 600; color: #FF5722;">{vbm} eV</td>
        </tr>
        <tr>
            <td style="padding: 10px;"><strong>Conduction-band minimum (CBM)</strong></td>
            <td style="padding: 10px; text-align: right; font-weight: 600; color: #9C27B0;">{cbm} eV</td>
        </tr>
    </table>
</div>
"""
            display(HTML(html))

            # Display image
            display(Image(data=image_data, format="png", width=800))

            if verbose:
                print(f"✓ Displayed band structure image")

        except ImportError:
            if verbose:
                print(
                    "⚠ Not in Jupyter environment - image cannot be displayed"
                )
                print(
                    f"  Image data available as base64 (length: {len(result.get('image_base64', ''))} chars)"
                )
        except Exception as e:
            if verbose:
                print(f"✗ Error displaying image: {str(e)}")

    async def query(
        self,
        query: str,
        verbose: bool = False,
        return_dict: bool = False,
        show_tool_results: bool = False,
        use_tools: bool = True,
        auto_display_images: bool = False,
    ) -> Union[str, Dict[str, Any]]:
        """
        Execute query (async)

        Args:
            query: Natural language query
            verbose: Print debug info
            return_dict: If True, return raw dict data instead of text
            show_tool_results: If True, append raw tool results to response
            use_tools: If False, disable tool calling (direct LLM response only)
            auto_display_images: If True, automatically display SlakoNet images

        Returns:
            str: Formatted text response (default)
            dict: Raw data dictionary (if return_dict=True)
        """
        # Use different system prompt when tools are disabled
        if use_tools:
            system_prompt = self.system_prompt
        else:
            system_prompt = """You are a materials science AI assistant with extensive knowledge of materials properties, computational methods, and DFT calculations.

When answering questions about materials properties:
- Provide answers based on your training knowledge
- Include typical experimental or computational values when known
- Mention uncertainty or ranges when appropriate
- Explain which computational methods (DFT, GW, hybrid functionals) typically give which results
- For common materials (Si, GaN, SiC, diamond, graphene, etc.), provide well-known literature values

You do NOT have access to databases or computational tools in this mode - answer only from your extensive training knowledge of materials science."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query},
        ]

        self.last_tool_results = []  # Reset for new query
        tool_call_history = []  # Track all tool calls

        for iteration in range(self.max_iterations):
            if verbose:
                print(f"[Iteration {iteration + 1}/{self.max_iterations}]")

            try:
                # Prepare API call parameters
                api_params = {
                    "model": self.model,
                    "messages": messages,
                    "temperature": self.temperature,
                }

                # Add tools only if use_tools=True
                if use_tools:
                    api_params["tools"] = TOOLS_SCHEMA
                    api_params["tool_choice"] = "auto"

                response = await self.openai_client.chat.completions.create(
                    **api_params
                )

                message = response.choices[0].message

                # If no tool calls OR tools disabled, return final response
                if not message.tool_calls or not use_tools:
                    final_response = (
                        message.content
                        if message.content
                        else "No response generated."
                    )

                    # Auto-display images if requested
                    if auto_display_images and self.last_tool_results:
                        for tool_result in self.last_tool_results:
                            if (
                                isinstance(tool_result, dict)
                                and "image_base64" in tool_result
                            ):
                                self._display_image(
                                    tool_result, verbose=verbose
                                )

                    # Optionally append tool results
                    if show_tool_results and tool_call_history:
                        final_response += "\n\n" + "=" * 70 + "\n"
                        final_response += "RAW TOOL RESULTS:\n"
                        final_response += "=" * 70 + "\n"
                        for i, call in enumerate(tool_call_history, 1):
                            final_response += (
                                f"\n[Tool Call {i}] {call['function_name']}\n"
                            )
                            final_response += f"Arguments: {json.dumps(call['arguments'], indent=2)}\n"
                            final_response += f"Result: {json.dumps(call['result'], indent=2)}\n"
                            final_response += "-" * 70 + "\n"

                    # Return dict or text
                    if return_dict:
                        if len(self.last_tool_results) == 1:
                            result = self.last_tool_results[0]
                        elif len(self.last_tool_results) > 1:
                            result = {"results": self.last_tool_results}
                        else:
                            try:
                                result = json.loads(message.content)
                            except:
                                result = {"response": message.content}

                        if show_tool_results:
                            result["tool_call_history"] = tool_call_history

                        return result
                    else:
                        return final_response

                messages.append(message)

                # Process tool calls (only if use_tools=True)
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

                    # Store result
                    self.last_tool_results.append(result)

                    # Track tool call history
                    tool_call_history.append(
                        {
                            "function_name": function_name,
                            "arguments": function_args,
                            "result": result,
                        }
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
                if return_dict:
                    return {"error": str(e)}
                else:
                    return f"Error: {str(e)}"

        if return_dict:
            result = (
                {"results": self.last_tool_results}
                if self.last_tool_results
                else {"error": "Max iterations reached"}
            )
            if show_tool_results:
                result["tool_call_history"] = tool_call_history
            return result
        else:
            return "Query completed."

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
    ) -> Union[str, Dict[str, Any]]:
        """
        Execute query (sync) with optional HTML rendering or dict return.

        Parameters
        ----------
        query : str
            User query to the agent.
        verbose : bool
            Show iteration debug prints.
        render_html : bool
            If True, render result as HTML in Jupyter/Colab (overrides return_dict).
        html_style : str
            "bootstrap" (default) or "css" (minimal inline css).
        max_show : int
            Max rows to show when converting materials list to a table.
        return_dict : bool
            If True (and render_html=False), return raw dict data instead of text.
        show_tool_results : bool
            If True, include raw tool results in response.
        use_tools : bool
            If False, disable tool calling (direct LLM response only).
        auto_display_images : bool
            If True, automatically display SlakoNet band structure images.

        Returns
        -------
        Union[str, Dict[str, Any]]
            Text response (default), dict (if return_dict=True), or displays HTML (if render_html=True)
        """

        # Helper functions
        def materials_to_markdown(materials: list, show: int = None) -> str:
            try:
                from tabulate import tabulate
            except ImportError:
                return json.dumps(materials, indent=2)

            if not materials:
                return "No materials found."

            cols = [
                "jid",
                "formula",
                "spg_symbol",
                "formation_energy_peratom",
                "bulk_modulus_kv",
                "bandgap",
                "bandgap_source",
                "mbj_bandgap",
                "optb88vdw_bandgap",
                "ehull",
            ]
            cols = [c for c in cols if any(c in m for m in materials)]
            mats = materials[:show] if show else materials

            rows = []
            for m in mats:
                row = []
                for c in cols:
                    v = m.get(c, "")
                    if isinstance(v, float):
                        row.append(f"{v:.4g}")
                    elif v is None:
                        row.append("")
                    else:
                        row.append(str(v))
                rows.append(row)

            headers = [c.replace("_", " ").title() for c in cols]
            return tabulate(rows, headers=headers, tablefmt="github")

        def envelope_to_markdown(
            envelope: Union[str, dict], max_show: int = None
        ) -> str:
            if isinstance(envelope, str):
                if any(
                    marker in envelope
                    for marker in ["#", "**", "|", "```", "\n-"]
                ):
                    return envelope
                else:
                    return f"**Response:**\n\n{envelope}"

            if isinstance(envelope, dict):
                if "materials" in envelope:
                    header = (
                        f"**Found {len(envelope['materials'])} materials**\n\n"
                    )
                    table = materials_to_markdown(
                        envelope.get("materials", []), show=max_show
                    )
                    return header + table
                elif "results" in envelope and isinstance(
                    envelope["results"], list
                ):
                    parts = []
                    for i, res in enumerate(envelope["results"], 1):
                        if isinstance(res, dict) and "materials" in res:
                            parts.append(f"## Result {i}\n\n")
                            parts.append(
                                materials_to_markdown(
                                    res["materials"], show=max_show
                                )
                            )
                        else:
                            parts.append(
                                f"## Result {i}\n\n```json\n{json.dumps(res, indent=2)}\n```"
                            )
                    return "\n\n".join(parts)
                elif "response" in envelope:
                    return envelope["response"]
                else:
                    return f"```json\n{json.dumps(envelope, indent=2)}\n```"

            return str(envelope)

        # Run the async query
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                try:
                    import nest_asyncio

                    nest_asyncio.apply()
                    envelope = loop.run_until_complete(
                        self.query(
                            query,
                            verbose,
                            return_dict,
                            show_tool_results,
                            use_tools,
                            auto_display_images,
                        )
                    )
                except ImportError:
                    raise RuntimeError(
                        "Install nest_asyncio for Jupyter support"
                    )
            else:
                envelope = loop.run_until_complete(
                    self.query(
                        query,
                        verbose,
                        return_dict,
                        show_tool_results,
                        use_tools,
                        auto_display_images,
                    )
                )
        except RuntimeError:
            envelope = asyncio.run(
                self.query(
                    query,
                    verbose,
                    return_dict,
                    show_tool_results,
                    use_tools,
                    auto_display_images,
                )
            )

        # If rendering HTML is requested
        if render_html:
            try:
                from IPython.display import HTML, display
                import markdown as mdlib
            except Exception:
                return envelope

            md_text = envelope_to_markdown(envelope, max_show)
            md_text = (
                md_text.replace("\u202f", " ")
                .replace("\u2212", "-")
                .replace("\u2013", "-")
                .replace("\u2014", "-")
            )

            html_body = mdlib.markdown(
                md_text, extensions=["tables", "fenced_code"]
            )

            if html_style == "bootstrap":
                bootstrap = """
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
<style>
.agapi-card { 
    max-width: 960px; 
    margin: 20px auto; 
    padding: 20px;
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    background: white;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
.agapi-card table { width: 100%; margin: 1em 0; }
.agapi-card table th, .agapi-card table td { vertical-align: middle; padding: 8px 12px; }
</style>
"""
                html_body = html_body.replace(
                    "<table>",
                    '<table class="table table-sm table-striped table-hover">',
                )
                full_html = (
                    f"{bootstrap}<div class='agapi-card'>{html_body}</div>"
                )
            else:
                css = """
<style>
.agapi-wrap { max-width: 900px; margin: 20px auto; padding: 20px; }
.agapi-wrap table { width: 100%; border-collapse: collapse; margin: 1em 0; }
</style>
"""
                full_html = f"{css}<div class='agapi-wrap'>{html_body}</div>"

            try:
                display(HTML(full_html))
                return envelope
            except Exception:
                return envelope

        return envelope

    def _execute_function(
        self, function_name: str, function_args: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute tool function"""
        function_args["api_client"] = self.agapi_client

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


# Add these functions at the END of agent.py (after the AGAPIAgent class)


async def run_agent_query(
    query: str,
    api_key: str = None,
    model: str = None,
    temperature: float = None,
    verbose: bool = False,
    return_dict: bool = False,
    show_tool_results: bool = False,
    use_tools: bool = True,
    auto_display_images: bool = False,
) -> Union[str, Dict[str, Any]]:
    """
    Async convenience function to run a query without creating an agent instance.

    Args:
        query: Natural language query
        api_key: API key (optional, uses default from config)
        model: Model name (optional, uses default)
        temperature: Temperature (optional, uses default)
        verbose: Print debug info
        return_dict: Return dict instead of text
        show_tool_results: Include raw tool results
        use_tools: Enable/disable tool calling
        auto_display_images: Automatically display SlakoNet images

    Returns:
        str or dict: Query result

    Example:
        result = await run_agent_query("Find SiC materials")
    """
    agent = AGAPIAgent(api_key=api_key, model=model, temperature=temperature)
    return await agent.query(
        query,
        verbose=verbose,
        return_dict=return_dict,
        show_tool_results=show_tool_results,
        use_tools=use_tools,
        auto_display_images=auto_display_images,
    )


def run_agent_query_sync(
    query: str,
    api_key: str = None,
    model: str = None,
    temperature: float = None,
    verbose: bool = False,
    render_html: bool = False,
    html_style: str = "bootstrap",
    max_show: int = 20,
    return_dict: bool = False,
    show_tool_results: bool = False,
    use_tools: bool = True,
    auto_display_images: bool = False,
) -> Union[str, Dict[str, Any]]:
    """
    Sync convenience function to run a query without creating an agent instance.

    Args:
        query: Natural language query
        api_key: API key (optional, uses default from config)
        model: Model name (optional, uses default)
        temperature: Temperature (optional, uses default)
        verbose: Print debug info
        render_html: Render as HTML in Jupyter
        html_style: "bootstrap" or "css"
        max_show: Max rows in tables
        return_dict: Return dict instead of text
        show_tool_results: Include raw tool results
        use_tools: Enable/disable tool calling
        auto_display_images: Automatically display SlakoNet images

    Returns:
        str or dict: Query result

    Example:
        result = run_agent_query_sync("Find SiC materials")
    """
    agent = AGAPIAgent(api_key=api_key, model=model, temperature=temperature)
    return agent.query_sync(
        query,
        verbose=verbose,
        render_html=render_html,
        html_style=html_style,
        max_show=max_show,
        return_dict=return_dict,
        show_tool_results=show_tool_results,
        use_tools=use_tools,
        auto_display_images=auto_display_images,
    )
