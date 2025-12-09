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

SYSTEM_PROMPT = """You are a materials science AI assistant with access to computational tools:

**DATABASES:**
- JARVIS-DFT: 80,000+ DFT-calculated materials

**COMPUTATIONAL TOOLS:**
- ALIGNN: ML predictions (formation energy, bandgap, moduli)
- ALIGNN-FF: Structure relaxation
- SlakoNet: Electronic band structure
- DiffractGPT: Structure from XRD
- Intermat: Heterostructure interfaces

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

**PROPERTIES:** bandgap, formation_energy_peratom, bulk_modulus_kv, shear_modulus_gv, ehull, Tc_supercon, n-Seebeck"""


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

    def query_sync(self, query: str, verbose: bool = False) -> str:
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
