"""
agent_pydanticai.py
-------------------
AGAPI materials science agent using PydanticAI.

Compared to agent_langgraph.py:
  - Framework: PydanticAI instead of LangGraph
  - Tools registered with @agent.tool using RunContext[AGAPIClient] for dep injection
  - Agent loop managed by PydanticAI (not LangGraph create_react_agent)
  - Tool call history extracted from result.all_messages()

What this tests:
  - Whether PydanticAI's typed dependency injection and schema generation changes
    model behaviour vs LangGraph's StructuredTool approach
  - Whether PydanticAI's agent loop strategy differs in practice

Install:
    pip install pydantic-ai openai

Usage:
    from agapi.agents.agent_pydanticai import AGAPIAgentPydantic
    agent = AGAPIAgentPydantic()
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

# ── PydanticAI imports ────────────────────────────────────────────────────────

from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIModel

# ── Module-level agent (tools registered once at import) ─────────────────────
# The AGAPIClient (for tool calls) is passed per-run as deps.

try:
    # pydantic-ai 0.1+: provider-based setup
    from pydantic_ai.providers.openai import OpenAIProvider
    _model = OpenAIModel(
        AgentConfig.DEFAULT_MODEL,
        provider=OpenAIProvider(
            base_url=f"{AgentConfig.API_BASE}/api",
            api_key=AgentConfig.DEFAULT_API_KEY,
        ),
    )
except ImportError:
    # older pydantic-ai: direct kwargs
    _model = OpenAIModel(
        AgentConfig.DEFAULT_MODEL,
        base_url=f"{AgentConfig.API_BASE}/api",
        api_key=AgentConfig.DEFAULT_API_KEY,
    )

_agent: Agent[AGAPIClient, str] = Agent(
    _model,
    deps_type=AGAPIClient,
    system_prompt=SYSTEM_PROMPT,
)


def _j(result) -> str:
    return json.dumps(result, default=str)


# ── JARVIS-DFT queries ────────────────────────────────────────────────────────

@_agent.tool
def query_by_formula(ctx: RunContext[AGAPIClient], formula: str) -> str:
    """Get all polymorphs of a chemical formula from JARVIS-DFT database."""
    return _j(F.query_by_formula(formula, api_client=ctx.deps))


@_agent.tool
def query_by_jid(ctx: RunContext[AGAPIClient], jid: str) -> str:
    """Get detailed info for a JARVIS ID including POSCAR structure."""
    return _j(F.query_by_jid(jid, api_client=ctx.deps))


@_agent.tool
def query_by_elements(ctx: RunContext[AGAPIClient], elements: str) -> str:
    """Get materials containing specific elements (comma-separated, e.g. 'Ga,N')."""
    return _j(F.query_by_elements(elements, api_client=ctx.deps))


@_agent.tool
def query_by_property(
    ctx: RunContext[AGAPIClient],
    property_name: str,
    min_val: Optional[float] = None,
    max_val: Optional[float] = None,
    elements: Optional[str] = None,
) -> str:
    """Find materials by property range (e.g. bandgap between 1 and 2 eV)."""
    return _j(F.query_by_property(
        property_name, min_val=min_val, max_val=max_val,
        elements=elements, api_client=ctx.deps,
    ))


@_agent.tool
def find_extreme(
    ctx: RunContext[AGAPIClient],
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
        constraint_property=constraint_property, api_client=ctx.deps,
    ))


@_agent.tool
def list_jarvis_columns(ctx: RunContext[AGAPIClient]) -> str:
    """Return all column names available in the JARVIS-DFT database."""
    return _j(F.list_jarvis_columns(api_client=ctx.deps))


# ── ALIGNN ML predictions ─────────────────────────────────────────────────────

@_agent.tool
def alignn_predict(
    ctx: RunContext[AGAPIClient],
    poscar: Optional[str] = None,
    jid: Optional[str] = None,
) -> str:
    """Predict material properties using ALIGNN machine learning models."""
    return _j(F.alignn_predict(poscar=poscar, jid=jid, api_client=ctx.deps))


# ── ALIGNN force-field tools ──────────────────────────────────────────────────

@_agent.tool
def alignn_ff_single_point(ctx: RunContext[AGAPIClient], poscar: str) -> str:
    """Evaluate energy, forces, and stress for a structure using ALIGNN-FF (no relaxation)."""
    return _j(F.alignn_ff_single_point(poscar, api_client=ctx.deps))


@_agent.tool
def alignn_ff_optimize(
    ctx: RunContext[AGAPIClient],
    poscar: str,
    fmax: float = 0.05,
    steps: int = 200,
    optimizer: str = "FIRE",
    relax_cell: bool = True,
) -> str:
    """Relax a crystal structure using ALIGNN force field with full trajectory."""
    return _j(F.alignn_ff_optimize(
        poscar, fmax=fmax, steps=steps, optimizer=optimizer,
        relax_cell=relax_cell, api_client=ctx.deps,
    ))


@_agent.tool
def alignn_ff_relax(
    ctx: RunContext[AGAPIClient],
    poscar: str,
    fmax: float = 0.05,
    steps: int = 150,
) -> str:
    """Relax structure using ALIGNN force field."""
    return _j(F.alignn_ff_relax(poscar, fmax=fmax, steps=steps, api_client=ctx.deps))


@_agent.tool
def alignn_ff_md(
    ctx: RunContext[AGAPIClient],
    poscar: str,
    temperature: float = 300.0,
    timestep: float = 0.5,
    steps: int = 50,
    interval: int = 5,
) -> str:
    """Run NVE molecular dynamics using ALIGNN force field."""
    return _j(F.alignn_ff_md(
        poscar, temperature=temperature, timestep=timestep,
        steps=steps, interval=interval, api_client=ctx.deps,
    ))


# ── Electronic structure ──────────────────────────────────────────────────────

@_agent.tool
def slakonet_bandstructure(
    ctx: RunContext[AGAPIClient],
    poscar: str,
    energy_range_min: float = -8.0,
    energy_range_max: float = 8.0,
) -> str:
    """Calculate electronic band structure using SlakoNet."""
    return _j(F.slakonet_bandstructure(
        poscar, energy_range_min=energy_range_min,
        energy_range_max=energy_range_max, api_client=ctx.deps,
    ))


# ── XRD tools ─────────────────────────────────────────────────────────────────

@_agent.tool
def generate_xrd_pattern(
    ctx: RunContext[AGAPIClient],
    poscar: str,
    wavelength: float = 1.54184,
    num_peaks: int = 20,
) -> str:
    """Generate powder XRD pattern description from crystal structure."""
    return _j(F.generate_xrd_pattern(
        poscar, wavelength=wavelength, num_peaks=num_peaks, api_client=ctx.deps,
    ))


@_agent.tool
def diffractgpt_predict(ctx: RunContext[AGAPIClient], formula: str, peaks: str) -> str:
    """Predict structure from XRD peaks using DiffractGPT."""
    return _j(F.diffractgpt_predict(formula, peaks, api_client=ctx.deps))


@_agent.tool
def xrd_match(ctx: RunContext[AGAPIClient], formula: str, xrd_pattern: str) -> str:
    """Match XRD pattern to JARVIS-DFT database."""
    return _j(F.xrd_match(formula, xrd_pattern, api_client=ctx.deps))


@_agent.tool
def pxrd_match(
    ctx: RunContext[AGAPIClient],
    query: str,
    pattern_data: str,
    wavelength: float = 1.54184,
) -> str:
    """Match an experimental powder XRD pattern against JARVIS-DFT by cosine similarity."""
    return _j(F.pxrd_match(
        query, pattern_data, wavelength=wavelength, api_client=ctx.deps,
    ))


@_agent.tool
def xrd_analyze(
    ctx: RunContext[AGAPIClient],
    formula: str,
    xrd_data: str,
    wavelength: float = 1.54184,
    method: str = "pattern_matching",
) -> str:
    """Analyze an experimental XRD pattern using pattern matching and/or DiffractGPT."""
    return _j(F.xrd_analyze(
        formula, xrd_data, wavelength=wavelength, method=method, api_client=ctx.deps,
    ))


# ── Structure manipulation ────────────────────────────────────────────────────

@_agent.tool
def make_supercell(ctx: RunContext[AGAPIClient], poscar: str, scaling_matrix: list) -> str:
    """Create a supercell from a POSCAR structure. scaling_matrix is [nx, ny, nz]."""
    return _j(F.make_supercell(poscar, scaling_matrix, api_client=ctx.deps))


@_agent.tool
def substitute_atom(
    ctx: RunContext[AGAPIClient],
    poscar: str,
    element_from: str,
    element_to: str,
    num_substitutions: int = 1,
) -> str:
    """Substitute atoms in a structure (e.g., replace Ga with Al)."""
    return _j(F.substitute_atom(
        poscar, element_from, element_to,
        num_substitutions=num_substitutions, api_client=ctx.deps,
    ))


@_agent.tool
def create_vacancy(
    ctx: RunContext[AGAPIClient],
    poscar: str,
    element: str,
    num_vacancies: int = 1,
) -> str:
    """Create vacancy defects by removing atoms from a structure."""
    return _j(F.create_vacancy(
        poscar, element, num_vacancies=num_vacancies, api_client=ctx.deps,
    ))


@_agent.tool
def generate_interface(
    ctx: RunContext[AGAPIClient],
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
        separation=separation, max_area=max_area, api_client=ctx.deps,
    ))


# ── Microscopy ────────────────────────────────────────────────────────────────

@_agent.tool
def microscopygpt_analyze(
    ctx: RunContext[AGAPIClient],
    image_path: str,
    formula: str,
) -> str:
    """Analyze a microscopy image (STEM/TEM/SEM) using MicroscopyGPT."""
    return _j(F.microscopygpt_analyze(image_path, formula, api_client=ctx.deps))


# ── External databases ────────────────────────────────────────────────────────

@_agent.tool
def query_mp(ctx: RunContext[AGAPIClient], formula: str, limit: int = 10) -> str:
    """Fetch crystal structures from the Materials Project via OPTIMADE."""
    return _j(F.query_mp(formula, limit=limit, api_client=ctx.deps))


@_agent.tool
def query_oqmd(ctx: RunContext[AGAPIClient], formula: str, limit: int = 10) -> str:
    """Fetch crystal structures from OQMD via OPTIMADE."""
    return _j(F.query_oqmd(formula, limit=limit, api_client=ctx.deps))


# ── Literature search ─────────────────────────────────────────────────────────

@_agent.tool
def search_arxiv(ctx: RunContext[AGAPIClient], query: str, max_results: int = 10) -> str:
    """Search arXiv preprints for materials science literature."""
    return _j(F.search_arxiv(query, max_results=max_results, api_client=ctx.deps))


@_agent.tool
def search_crossref(ctx: RunContext[AGAPIClient], query: str, rows: int = 10) -> str:
    """Search published journal articles via the Crossref API."""
    return _j(F.search_crossref(query, rows=rows, api_client=ctx.deps))


# ── Protein / biology ─────────────────────────────────────────────────────────

@_agent.tool
def protein_fold(ctx: RunContext[AGAPIClient], sequence: str) -> str:
    """Predict 3D protein structure from amino acid sequence using ESMFold."""
    return _j(F.protein_fold(sequence, api_client=ctx.deps))


@_agent.tool
def openfold_predict(
    ctx: RunContext[AGAPIClient],
    protein_sequence: str,
    dna1: str,
    dna2: str,
) -> str:
    """Predict a protein-DNA complex 3D structure using NVIDIA OpenFold3."""
    return _j(F.openfold_predict(
        protein_sequence, dna1, dna2, api_client=ctx.deps,
    ))


# ── Agent class ───────────────────────────────────────────────────────────────

class AGAPIAgentPydantic:
    """
    AGAPI agent using PydanticAI.

    Wraps the module-level _agent with a per-instance AGAPIClient so the
    benchmark runner can pass a specific api_key without recreating the
    tool registrations.

    Usage:
        agent = AGAPIAgentPydantic()
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

        self._client = AGAPIClient(
            api_key=self.api_key,
            api_base=self.api_base,
            timeout=self.timeout,
        )

        self.last_intermediate_steps: List[Dict[str, Any]] = []

    @staticmethod
    def _extract_tools(result) -> List[str]:
        """Extract ordered list of tool names from a PydanticAI RunResult."""
        tools = []
        try:
            from pydantic_ai.messages import ToolCallPart, ModelResponse
            for msg in result.all_messages():
                if isinstance(msg, ModelResponse):
                    for part in msg.parts:
                        if isinstance(part, ToolCallPart):
                            tools.append(part.tool_name)
        except Exception:
            pass
        return tools

    @staticmethod
    def _get_output(result) -> str:
        """Get final text output, compatible across pydantic-ai versions."""
        for attr in ("output", "data"):
            val = getattr(result, attr, None)
            if val is not None:
                return str(val)
        return "No response generated."

    def query_sync_benchmark(self, query: str) -> tuple:
        """
        Benchmark interface — runs query and returns (response_text, tools_called).

        Returns:
            response_text (str):  Final answer from the agent.
            tools_called  (list): Ordered list of tool names called.
        """
        try:
            from pydantic_ai.usage import UsageLimits
            limits = UsageLimits(request_limit=self.max_iterations)
        except ImportError:
            limits = None

        kwargs: Dict[str, Any] = {"deps": self._client}
        if limits is not None:
            kwargs["usage_limits"] = limits

        result = _agent.run_sync(query, **kwargs)
        tools_called = self._extract_tools(result)
        self.last_intermediate_steps = [{"tool": t} for t in tools_called]
        return self._get_output(result), tools_called

    def query_sync(self, query: str, **kwargs) -> str:
        """Original-style synchronous interface."""
        response, _ = self.query_sync_benchmark(query)
        return response
