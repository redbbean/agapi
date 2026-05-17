"""
agent_openai_sdk.py
-------------------
AGAPI materials science agent using the OpenAI Agents SDK.

Compared to agent_langgraph.py:
  Original (agent_langgraph.py)         This file
  ------------------------------------  ------------------------------------------
  LangGraph create_react_agent          OpenAI Agents SDK Agent + Runner
  StructuredTool + Pydantic schemas     @function_tool decorator
  LangChain message objects             SDK-managed conversation state
  MemorySaver checkpointing             Runner handles state internally
  trim_messages context management      max_turns iteration cap

What this tests:
  - Whether the OpenAI Agents SDK's tool schema generation differs from LangGraph's
  - Whether the SDK's built-in agent loop strategy changes task performance
  - Baseline for the future multi-agent phase (SDK has native handoff support)

Install:
    pip install openai-agents

Usage:
    from agapi.agents.agent_openai_sdk import AGAPIAgentOpenAISDK
    agent = AGAPIAgentOpenAISDK()
    response, tools = agent.query_sync_benchmark("What is the bandgap of GaN?")
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from dotenv import load_dotenv
    for _parent in Path(__file__).resolve().parents:
        _env = _parent / ".env"
        if _env.exists():
            load_dotenv(_env)
            break
except ImportError:
    pass

from .config import AgentConfig
from .client import AGAPIClient
from .agent import SYSTEM_PROMPT
import agapi.agents.functions as F

# ── OpenAI Agents SDK imports ─────────────────────────────────────────────────
# Set OPENAI_API_KEY before importing agents so the SDK doesn't error on import.
os.environ.setdefault("OPENAI_API_KEY", os.environ.get("AGAPI_KEY", AgentConfig.DEFAULT_API_KEY))

from agents import (
    Agent,
    AsyncOpenAI,
    OpenAIChatCompletionsModel,
    Runner,
    function_tool,
    set_tracing_disabled,
)

# Disable SDK tracing — it tries to phone home to platform.openai.com with
# whatever key is in OPENAI_API_KEY, which is an AGAPI key and gets rejected.
set_tracing_disabled(disabled=True)

# ── Shared API client for tool calls ─────────────────────────────────────────
# Created once at module import. The OpenAIChatCompletionsModel below uses
# _openai_client for LLM calls; _api_client is used inside each tool for
# AGAPI REST API calls.

_agapi_key = os.environ.get("AGAPI_KEY", AgentConfig.DEFAULT_API_KEY)

_api_client = AGAPIClient(
    api_key=_agapi_key,
    api_base=AgentConfig.API_BASE,
    timeout=AgentConfig.DEFAULT_TIMEOUT,
)

# Use ChatCompletions API explicitly — AGAPI supports /v1/chat/completions
# but not the newer Responses API (/v1/responses) that the SDK defaults to.
_openai_client = AsyncOpenAI(
    base_url=f"{AgentConfig.API_BASE}/api",
    api_key=_agapi_key,
)

_chat_model = OpenAIChatCompletionsModel(
    model=AgentConfig.DEFAULT_MODEL,
    openai_client=_openai_client,
)


def _j(result) -> str:
    return json.dumps(result, default=str)


# ── JARVIS-DFT queries ────────────────────────────────────────────────────────

@function_tool
def query_by_formula(formula: str) -> str:
    """Get all polymorphs of a chemical formula from JARVIS-DFT database."""
    return _j(F.query_by_formula(formula, api_client=_api_client))


@function_tool
def query_by_jid(jid: str) -> str:
    """Get detailed info for a JARVIS ID including POSCAR structure."""
    return _j(F.query_by_jid(jid, api_client=_api_client))


@function_tool
def query_by_elements(elements: str) -> str:
    """Get materials containing specific elements (comma-separated, e.g. 'Ga,N')."""
    return _j(F.query_by_elements(elements, api_client=_api_client))


@function_tool
def query_by_property(
    property_name: str,
    min_val: Optional[float] = None,
    max_val: Optional[float] = None,
    elements: Optional[str] = None,
) -> str:
    """Find materials by property range (e.g. bandgap between 1 and 2 eV)."""
    return _j(F.query_by_property(
        property_name, min_val=min_val, max_val=max_val,
        elements=elements, api_client=_api_client,
    ))


@function_tool
def find_extreme(
    property_name: str,
    maximize: bool = True,
    elements: Optional[str] = None,
    formula: Optional[str] = None,
    min_constraint: Optional[float] = None,
    max_constraint: Optional[float] = None,
    constraint_property: Optional[str] = None,
) -> str:
    """Find material with highest or lowest value of a property."""
    return _j(F.find_extreme(
        property_name, maximize=maximize, elements=elements, formula=formula,
        min_constraint=min_constraint, max_constraint=max_constraint,
        constraint_property=constraint_property, api_client=_api_client,
    ))


@function_tool
def list_jarvis_columns() -> str:
    """Return all column names available in the JARVIS-DFT database."""
    return _j(F.list_jarvis_columns(api_client=_api_client))


# ── ALIGNN ML predictions ─────────────────────────────────────────────────────

@function_tool
def alignn_predict(
    poscar: Optional[str] = None,
    jid: Optional[str] = None,
) -> str:
    """Predict material properties using ALIGNN machine learning models."""
    return _j(F.alignn_predict(poscar=poscar, jid=jid, api_client=_api_client))


# ── ALIGNN force-field tools ──────────────────────────────────────────────────

@function_tool
def alignn_ff_single_point(poscar: str) -> str:
    """Evaluate energy, forces, and stress for a structure using ALIGNN-FF (no relaxation)."""
    return _j(F.alignn_ff_single_point(poscar, api_client=_api_client))


@function_tool
def alignn_ff_optimize(
    poscar: str,
    fmax: float = 0.05,
    steps: int = 200,
    optimizer: str = "FIRE",
    relax_cell: bool = True,
) -> str:
    """Relax a crystal structure using ALIGNN force field with full trajectory."""
    return _j(F.alignn_ff_optimize(
        poscar, fmax=fmax, steps=steps, optimizer=optimizer,
        relax_cell=relax_cell, api_client=_api_client,
    ))


@function_tool
def alignn_ff_relax(
    poscar: str,
    fmax: float = 0.05,
    steps: int = 150,
) -> str:
    """Relax structure using ALIGNN force field."""
    return _j(F.alignn_ff_relax(poscar, fmax=fmax, steps=steps, api_client=_api_client))


@function_tool
def alignn_ff_md(
    poscar: str,
    temperature: float = 300.0,
    timestep: float = 0.5,
    steps: int = 50,
    interval: int = 5,
) -> str:
    """Run NVE molecular dynamics using ALIGNN force field."""
    return _j(F.alignn_ff_md(
        poscar, temperature=temperature, timestep=timestep,
        steps=steps, interval=interval, api_client=_api_client,
    ))


# ── Electronic structure ──────────────────────────────────────────────────────

@function_tool
def slakonet_bandstructure(
    poscar: str,
    energy_range_min: float = -8.0,
    energy_range_max: float = 8.0,
) -> str:
    """Calculate electronic band structure using SlakoNet."""
    return _j(F.slakonet_bandstructure(
        poscar, energy_range_min=energy_range_min,
        energy_range_max=energy_range_max, api_client=_api_client,
    ))


# ── XRD tools ─────────────────────────────────────────────────────────────────

@function_tool
def generate_xrd_pattern(
    poscar: str,
    wavelength: float = 1.54184,
    num_peaks: int = 20,
) -> str:
    """Generate powder XRD pattern description from crystal structure."""
    return _j(F.generate_xrd_pattern(
        poscar, wavelength=wavelength, num_peaks=num_peaks, api_client=_api_client,
    ))


@function_tool
def diffractgpt_predict(formula: str, peaks: str) -> str:
    """Predict structure from XRD peaks using DiffractGPT."""
    return _j(F.diffractgpt_predict(formula, peaks, api_client=_api_client))


@function_tool
def xrd_match(formula: str, xrd_pattern: str) -> str:
    """Match XRD pattern to JARVIS-DFT database."""
    return _j(F.xrd_match(formula, xrd_pattern, api_client=_api_client))


@function_tool
def pxrd_match(
    query: str,
    pattern_data: str,
    wavelength: float = 1.54184,
) -> str:
    """Match an experimental powder XRD pattern against JARVIS-DFT by cosine similarity."""
    return _j(F.pxrd_match(
        query, pattern_data, wavelength=wavelength, api_client=_api_client,
    ))


@function_tool
def xrd_analyze(
    formula: str,
    xrd_data: str,
    wavelength: float = 1.54184,
    method: str = "pattern_matching",
) -> str:
    """Analyze an experimental XRD pattern using pattern matching and/or DiffractGPT."""
    return _j(F.xrd_analyze(
        formula, xrd_data, wavelength=wavelength, method=method, api_client=_api_client,
    ))


# ── Structure manipulation ────────────────────────────────────────────────────

@function_tool
def make_supercell(poscar: str, scaling_matrix: list) -> str:
    """Create a supercell from a POSCAR structure. scaling_matrix is [nx, ny, nz]."""
    return _j(F.make_supercell(poscar, scaling_matrix, api_client=_api_client))


@function_tool
def substitute_atom(
    poscar: str,
    element_from: str,
    element_to: str,
    num_substitutions: int = 1,
) -> str:
    """Substitute atoms in a structure (e.g., replace Ga with Al)."""
    return _j(F.substitute_atom(
        poscar, element_from, element_to,
        num_substitutions=num_substitutions, api_client=_api_client,
    ))


@function_tool
def create_vacancy(
    poscar: str,
    element: str,
    num_vacancies: int = 1,
) -> str:
    """Create vacancy defects by removing atoms from a structure."""
    return _j(F.create_vacancy(
        poscar, element, num_vacancies=num_vacancies, api_client=_api_client,
    ))


@function_tool
def generate_interface(
    film_poscar: str,
    substrate_poscar: str,
    film_indices: str = "0_0_1",
    substrate_indices: str = "0_0_1",
    film_thickness: float = 16,
    substrate_thickness: float = 16,
    separation: float = 2.5,
    max_area: float = 300,
) -> str:
    """Generate heterostructure interface between two materials."""
    return _j(F.generate_interface(
        film_poscar, substrate_poscar,
        film_indices=film_indices, substrate_indices=substrate_indices,
        film_thickness=film_thickness, substrate_thickness=substrate_thickness,
        separation=separation, max_area=max_area, api_client=_api_client,
    ))


# ── Microscopy ────────────────────────────────────────────────────────────────

@function_tool
def microscopygpt_analyze(image_path: str, formula: str) -> str:
    """Analyze a microscopy image (STEM/TEM/SEM) using MicroscopyGPT."""
    return _j(F.microscopygpt_analyze(image_path, formula, api_client=_api_client))


# ── External databases ────────────────────────────────────────────────────────

@function_tool
def query_mp(formula: str, limit: int = 10) -> str:
    """Fetch crystal structures from the Materials Project via OPTIMADE."""
    return _j(F.query_mp(formula, limit=limit, api_client=_api_client))


@function_tool
def query_oqmd(formula: str, limit: int = 10) -> str:
    """Fetch crystal structures from OQMD via OPTIMADE."""
    return _j(F.query_oqmd(formula, limit=limit, api_client=_api_client))


# ── Literature search ─────────────────────────────────────────────────────────

@function_tool
def search_arxiv(query: str, max_results: int = 10) -> str:
    """Search arXiv preprints for materials science literature."""
    return _j(F.search_arxiv(query, max_results=max_results, api_client=_api_client))


@function_tool
def search_crossref(query: str, rows: int = 10) -> str:
    """Search published journal articles via the Crossref API."""
    return _j(F.search_crossref(query, rows=rows, api_client=_api_client))


# ── Protein / biology ─────────────────────────────────────────────────────────

@function_tool
def protein_fold(sequence: str) -> str:
    """Predict 3D protein structure from amino acid sequence using ESMFold."""
    return _j(F.protein_fold(sequence, api_client=_api_client))


@function_tool
def openfold_predict(
    protein_sequence: str,
    dna1: str,
    dna2: str,
) -> str:
    """Predict a protein-DNA complex 3D structure using NVIDIA OpenFold3."""
    return _j(F.openfold_predict(
        protein_sequence, dna1, dna2, api_client=_api_client,
    ))


# ── Module-level Agent ────────────────────────────────────────────────────────

_TOOLS = [
    query_by_formula, query_by_jid, query_by_elements, query_by_property,
    find_extreme, list_jarvis_columns,
    alignn_predict, alignn_ff_single_point, alignn_ff_optimize, alignn_ff_relax,
    alignn_ff_md, slakonet_bandstructure,
    generate_xrd_pattern, diffractgpt_predict, xrd_match, pxrd_match, xrd_analyze,
    make_supercell, substitute_atom, create_vacancy, generate_interface,
    microscopygpt_analyze,
    query_mp, query_oqmd,
    search_arxiv, search_crossref,
    protein_fold, openfold_predict,
]

_sdk_agent = Agent(
    name="AGAPI Materials Science Agent",
    instructions=SYSTEM_PROMPT,
    tools=_TOOLS,
    model=_chat_model,
)


# ── Agent class ───────────────────────────────────────────────────────────────

class AGAPIAgentOpenAISDK:
    """
    AGAPI agent using the OpenAI Agents SDK.

    Wraps the module-level SDK Agent with per-instance configuration.
    The SDK's Runner manages the conversation loop; tool calls use the
    module-level AGAPIClient.

    Usage:
        agent = AGAPIAgentOpenAISDK()
        response, tools_called = agent.query_sync_benchmark("What is the bandgap of GaN?")
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
        self.api_key        = api_key        or AgentConfig.DEFAULT_API_KEY
        self.model          = model          or AgentConfig.DEFAULT_MODEL
        self.temperature    = temperature    if temperature is not None else AgentConfig.DEFAULT_TEMPERATURE
        self.max_iterations = max_iterations or AgentConfig.DEFAULT_MAX_ITERATIONS
        self.timeout        = timeout        or AgentConfig.DEFAULT_TIMEOUT
        self.api_base       = api_base       or AgentConfig.API_BASE

        self.last_intermediate_steps: List[Dict[str, Any]] = []

    @staticmethod
    def _extract_tools(result) -> List[str]:
        """Extract ordered list of tool names from a Runner result."""
        tools = []
        try:
            from agents import ToolCallItem
            for item in result.new_items:
                if isinstance(item, ToolCallItem):
                    raw = getattr(item, "raw_item", None)
                    if raw is not None:
                        name = getattr(raw, "name", None)
                        if name:
                            tools.append(name)
        except Exception:
            # Fallback: inspect raw_item attributes without importing ToolCallItem
            for item in getattr(result, "new_items", []):
                raw = getattr(item, "raw_item", None)
                if raw and getattr(raw, "type", None) == "function_call":
                    name = getattr(raw, "name", None)
                    if name:
                        tools.append(name)
        return tools

    def query_sync_benchmark(self, query: str) -> tuple:
        """
        Benchmark interface — runs query and returns (response_text, tools_called).

        Returns:
            response_text (str):  Final answer from the agent.
            tools_called  (list): Ordered list of tool names called.
        """
        result = Runner.run_sync(
            _sdk_agent,
            query,
            max_turns=self.max_iterations,
        )
        tools_called = self._extract_tools(result)
        self.last_intermediate_steps = [{"tool": t} for t in tools_called]
        final_output = getattr(result, "final_output", None) or "No response generated."
        return str(final_output), tools_called

    def query_sync(self, query: str, **kwargs) -> str:
        """Original-style synchronous interface."""
        response, _ = self.query_sync_benchmark(query)
        return response
