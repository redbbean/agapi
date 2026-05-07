#!/usr/bin/env python3
"""
agent_mcp_server.py
-------------------
MCP server that exposes all 28 AGAPI materials science tools over stdio.

Run as a subprocess (started automatically by agent_mcp.py):
    python agent_mcp_server.py

Uses the MCP FastMCP interface. Each tool wraps the corresponding function
from functions.py, injecting a shared AGAPIClient. Tool signatures are clean
(no api_client parameter) so the LLM never sees it.

In the agapi/agents/functions.py, it seems like the functions call the actual tools, in this MCP 
implementation, it seems like it's just returning some F function call? Can you explain in detail more 
about this?

Install:
    pip install mcp
"""

import json
import os
import sys
from pathlib import Path
from typing import Optional

# Load .env from Benchmarking repo root (walk up from this file)
try:
    from dotenv import load_dotenv
    for _parent in Path(__file__).resolve().parents:
        _env = _parent / ".env"
        if _env.exists():
            load_dotenv(_env)
            break
except ImportError:
    pass

# Allow import of agapi when running as standalone script
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "Test" / "agapi"))

from mcp.server.fastmcp import FastMCP
from agapi.agents.client import AGAPIClient
from agapi.agents.config import AgentConfig
import agapi.agents.functions as F

# ── Shared API client (created once at server startup) ────────────────────────
_client = AGAPIClient(
    api_key=os.environ.get("AGAPI_KEY", AgentConfig.DEFAULT_API_KEY),
    api_base=AgentConfig.API_BASE,
    timeout=AgentConfig.DEFAULT_TIMEOUT,
)

mcp = FastMCP("agapi-tools")


# ── Helper: serialise any result dict to a JSON string ────────────────────────
def _j(result) -> str:
    return json.dumps(result, default=str)


# ── JARVIS-DFT database queries ────────────────────────────────────────────────

@mcp.tool()
def query_by_formula(formula: str) -> str:
    """Get all polymorphs of a chemical formula from JARVIS-DFT database."""
    return _j(F.query_by_formula(formula, api_client=_client))


@mcp.tool()
def query_by_jid(jid: str) -> str:
    """Get detailed info for a JARVIS ID including POSCAR structure."""
    return _j(F.query_by_jid(jid, api_client=_client))


@mcp.tool()
def query_by_elements(elements: str) -> str:
    """Get materials containing specific elements (comma-separated, e.g. 'Ga,N')."""
    return _j(F.query_by_elements(elements, api_client=_client))


@mcp.tool()
def query_by_property(
    property_name: str,
    min_val: Optional[float] = None,
    max_val: Optional[float] = None,
    elements: Optional[str] = None,
) -> str:
    """Find materials by property range (e.g. bandgap between 1 and 2 eV)."""
    return _j(F.query_by_property(
        property_name, min_val=min_val, max_val=max_val,
        elements=elements, api_client=_client,
    ))


@mcp.tool()
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
        constraint_property=constraint_property, api_client=_client,
    ))


@mcp.tool()
def list_jarvis_columns() -> str:
    """Return all column names available in the JARVIS-DFT database."""
    return _j(F.list_jarvis_columns(api_client=_client))


# ── ALIGNN ML predictions ──────────────────────────────────────────────────────

@mcp.tool()
def alignn_predict(
    poscar: Optional[str] = None,
    jid: Optional[str] = None,
) -> str:
    """Predict material properties using ALIGNN machine learning models."""
    return _j(F.alignn_predict(poscar=poscar, jid=jid, api_client=_client))


# ── ALIGNN force-field tools ───────────────────────────────────────────────────

@mcp.tool()
def alignn_ff_single_point(poscar: str) -> str:
    """Evaluate energy, forces, and stress for a structure using ALIGNN-FF (no relaxation)."""
    return _j(F.alignn_ff_single_point(poscar, api_client=_client))


@mcp.tool()
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
        relax_cell=relax_cell, api_client=_client,
    ))


@mcp.tool()
def alignn_ff_relax(
    poscar: str,
    fmax: float = 0.05,
    steps: int = 150,
) -> str:
    """Relax structure using ALIGNN force field."""
    return _j(F.alignn_ff_relax(poscar, fmax=fmax, steps=steps, api_client=_client))


@mcp.tool()
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
        steps=steps, interval=interval, api_client=_client,
    ))


# ── Electronic structure ───────────────────────────────────────────────────────

@mcp.tool()
def slakonet_bandstructure(
    poscar: str,
    energy_range_min: float = -8.0,
    energy_range_max: float = 8.0,
) -> str:
    """Calculate electronic band structure using SlakoNet."""
    return _j(F.slakonet_bandstructure(
        poscar, energy_range_min=energy_range_min,
        energy_range_max=energy_range_max, api_client=_client,
    ))


# ── XRD tools ─────────────────────────────────────────────────────────────────

@mcp.tool()
def generate_xrd_pattern(
    poscar: str,
    wavelength: float = 1.54184,
    num_peaks: int = 20,
) -> str:
    """Generate powder XRD pattern description from crystal structure."""
    return _j(F.generate_xrd_pattern(
        poscar, wavelength=wavelength, num_peaks=num_peaks, api_client=_client,
    ))


@mcp.tool()
def diffractgpt_predict(formula: str, peaks: str) -> str:
    """Predict structure from XRD peaks using DiffractGPT."""
    return _j(F.diffractgpt_predict(formula, peaks, api_client=_client))


@mcp.tool()
def xrd_match(formula: str, xrd_pattern: str) -> str:
    """Match XRD pattern to JARVIS-DFT database."""
    return _j(F.xrd_match(formula, xrd_pattern, api_client=_client))


@mcp.tool()
def pxrd_match(
    query: str,
    pattern_data: str,
    wavelength: float = 1.54184,
) -> str:
    """Match an experimental powder XRD pattern against JARVIS-DFT by cosine similarity."""
    return _j(F.pxrd_match(
        query, pattern_data, wavelength=wavelength, api_client=_client,
    ))


@mcp.tool()
def xrd_analyze(
    formula: str,
    xrd_data: str,
    wavelength: float = 1.54184,
    method: str = "pattern_matching",
) -> str:
    """Analyze an experimental XRD pattern using pattern matching and/or DiffractGPT."""
    return _j(F.xrd_analyze(
        formula, xrd_data, wavelength=wavelength, method=method, api_client=_client,
    ))


# ── Structure manipulation ─────────────────────────────────────────────────────

@mcp.tool()
def make_supercell(poscar: str, scaling_matrix: list) -> str:
    """Create a supercell from a POSCAR structure. scaling_matrix is [nx, ny, nz]."""
    return _j(F.make_supercell(poscar, scaling_matrix, api_client=_client))


@mcp.tool()
def substitute_atom(
    poscar: str,
    element_from: str,
    element_to: str,
    num_substitutions: int = 1,
) -> str:
    """Substitute atoms in a structure (e.g., replace Ga with Al)."""
    return _j(F.substitute_atom(
        poscar, element_from, element_to,
        num_substitutions=num_substitutions, api_client=_client,
    ))


@mcp.tool()
def create_vacancy(
    poscar: str,
    element: str,
    num_vacancies: int = 1,
) -> str:
    """Create vacancy defects by removing atoms from a structure."""
    return _j(F.create_vacancy(
        poscar, element, num_vacancies=num_vacancies, api_client=_client,
    ))


@mcp.tool()
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
        separation=separation, max_area=max_area, api_client=_client,
    ))


# ── Microscopy ─────────────────────────────────────────────────────────────────

@mcp.tool()
def microscopygpt_analyze(image_path: str, formula: str) -> str:
    """Analyze a microscopy image (STEM/TEM/SEM) using MicroscopyGPT."""
    return _j(F.microscopygpt_analyze(image_path, formula, api_client=_client))


# ── External databases ─────────────────────────────────────────────────────────

@mcp.tool()
def query_mp(formula: str, limit: int = 10) -> str:
    """Fetch crystal structures from the Materials Project via OPTIMADE."""
    return _j(F.query_mp(formula, limit=limit, api_client=_client))


@mcp.tool()
def query_oqmd(formula: str, limit: int = 10) -> str:
    """Fetch crystal structures from OQMD via OPTIMADE."""
    return _j(F.query_oqmd(formula, limit=limit, api_client=_client))


# ── Literature search ──────────────────────────────────────────────────────────

@mcp.tool()
def search_arxiv(query: str, max_results: int = 10) -> str:
    """Search arXiv preprints for materials science literature."""
    return _j(F.search_arxiv(query, max_results=max_results, api_client=_client))


@mcp.tool()
def search_crossref(query: str, rows: int = 10) -> str:
    """Search published journal articles via the Crossref API."""
    return _j(F.search_crossref(query, rows=rows, api_client=_client))


# ── Protein / biology ──────────────────────────────────────────────────────────

@mcp.tool()
def protein_fold(sequence: str) -> str:
    """Predict 3D protein structure from amino acid sequence using ESMFold."""
    return _j(F.protein_fold(sequence, api_client=_client))


@mcp.tool()
def openfold_predict(
    protein_sequence: str,
    dna1: str,
    dna2: str,
) -> str:
    """Predict a protein-DNA complex 3D structure using NVIDIA OpenFold3."""
    return _j(F.openfold_predict(
        protein_sequence, dna1, dna2, api_client=_client,
    ))


# ── Entry point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    mcp.run()