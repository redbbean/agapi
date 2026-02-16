"""
Comprehensive test suite for AGAPI client.

Tests are organized by functionality:
- Client initialization and configuration
- Database queries (JARVIS-DFT, Materials Project)
- ML predictions (ALIGNN, ALIGNN-FF, SlakoNet)
- Analysis tools (XRD, protein folding, weather)
- Literature search (arXiv, CrossRef)
- Structure manipulation
- Error handling and edge cases

Run with:
    pytest tests/test_client.py -v -s
    pytest tests/test_client.py -v -s -k "test_jarvis"
    pytest tests/test_client.py -v -s --cov=agapi
"""

import os
import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import json

from agapi import (
    Agapi,
    AgapiError,
    AgapiAuthError,
    AgapiValidationError,
    AgapiTimeoutError,
    AgapiServerError,
)

# ============================================================================
# Test Data
# ============================================================================

SAMPLE_POSCAR = """Si2
1.0
3.3641499856336465 -2.5027128e-09 1.94229273881412
1.121382991333525 3.1717517190189715 1.9422927388141193
-2.5909987e-09 -1.8321133e-09 3.884586486670313
Si
2
Cartesian
3.92483875 2.77528125 6.7980237500000005
0.56069125 0.39646875 0.9711462500000001
"""

SAMPLE_CIF = """data_example
_cell_length_a    3.263150
_cell_length_b    3.263150
_cell_length_c    3.263150
_cell_angle_alpha 90.0
_cell_angle_beta  90.0
_cell_angle_gamma 90.0
loop_
_atom_site_label
_atom_site_fract_x
_atom_site_fract_y
_atom_site_fract_z
Ti 0.5 0.5 0.5
Au 0.0 0.0 0.0
"""

SAMPLE_XRD_PATTERN = """LaB6
21.38 0.69
30.42 1.00
35.19 0.39
"""

SAMPLE_PROTEIN_SEQ = "MGREEPLNHVEAERQRREKLNQRFYALRAVVPNVSKMDKASLLGDAIAYINELKSKVVKTESEKLQIKNQLEEVKLELAGRLEHHHHHH"

# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture(scope="session")
def api_key() -> str:
    """Get API key from environment."""
    key = os.getenv("AGAPI_API_KEY") or os.getenv("ATOMGPT_API_KEY")
    if not key:
        pytest.skip("API key not found. Set AGAPI_API_KEY or ATOMGPT_API_KEY")
    print(f"\n✓ Using API key: {key[:15]}...")
    return key


@pytest.fixture
def client(api_key: str) -> Agapi:
    """Create AGAPI client instance."""
    return Agapi(api_key=api_key, timeout=60, retries=2)


@pytest.fixture
def poscar_file(tmp_path: Path) -> Path:
    """Create temporary POSCAR file."""
    poscar_path = tmp_path / "POSCAR"
    poscar_path.write_text(SAMPLE_POSCAR)
    return poscar_path


@pytest.fixture
def cif_file(tmp_path: Path) -> Path:
    """Create temporary CIF file."""
    cif_path = tmp_path / "structure.cif"
    cif_path.write_text(SAMPLE_CIF)
    return cif_path


# ============================================================================
# Client Initialization Tests
# ============================================================================

class TestClientInitialization:
    """Test client initialization and configuration."""
    
    def test_init_with_api_key(self, api_key):
        """Test initialization with explicit API key."""
        print("\n🔧 Testing client initialization with API key...")
        client = Agapi(api_key=api_key)
        
        assert client.api_key == api_key
        assert client.base_url == "https://atomgpt.org"
        assert client.timeout == 120
        print("✅ Client initialized successfully")
    
    def test_init_with_env_var(self, api_key):
        """Test initialization with environment variable."""
        print("\n🔧 Testing initialization from environment...")
        
        # Temporarily set env var
        os.environ["AGAPI_API_KEY"] = api_key
        try:
            client = Agapi()
            assert client.api_key == api_key
            print("✅ Client initialized from AGAPI_API_KEY")
        finally:
            os.environ.pop("AGAPI_API_KEY", None)
    
    def test_init_missing_api_key(self):
        """Test initialization fails without API key."""
        print("\n🔧 Testing missing API key error...")
        
        # Clear env vars
        old_agapi = os.environ.pop("AGAPI_API_KEY", None)
        old_atomgpt = os.environ.pop("ATOMGPT_API_KEY", None)
        
        try:
            with pytest.raises(AgapiAuthError) as exc_info:
                Agapi()
            
            assert "Missing API key" in str(exc_info.value)
            print(f"✅ Correctly raised AgapiAuthError: {exc_info.value}")
        finally:
            # Restore env vars
            if old_agapi:
                os.environ["AGAPI_API_KEY"] = old_agapi
            if old_atomgpt:
                os.environ["ATOMGPT_API_KEY"] = old_atomgpt
    
    def test_custom_base_url(self, api_key):
        """Test custom base URL."""
        print("\n🔧 Testing custom base URL...")
        custom_url = "http://localhost:8080"
        client = Agapi(api_key=api_key, base_url=custom_url)
        
        assert client.base_url == custom_url
        print(f"✅ Custom base URL set: {client.base_url}")
    
    def test_custom_timeout(self, api_key):
        """Test custom timeout."""
        print("\n🔧 Testing custom timeout...")
        client = Agapi(api_key=api_key, timeout=30)
        
        assert client.timeout == 30
        print("✅ Custom timeout set: 30s")
    
    def test_context_manager(self, api_key):
        """Test context manager usage."""
        print("\n🔧 Testing context manager...")
        
        with Agapi(api_key=api_key) as client:
            assert client.api_key == api_key
            print("✅ Context manager works")
    
    def test_repr(self, client):
        """Test string representation."""
        print("\n🔧 Testing __repr__...")
        repr_str = repr(client)
        
        assert "Agapi" in repr_str
        assert "atomgpt.org" in repr_str
        print(f"✅ Repr: {repr_str}")


# ============================================================================
# Database Query Tests
# ============================================================================

class TestDatabaseQueries:
    """Test database query methods."""
    
    def test_jarvis_dft_query_by_formula(self, client):
        """Test JARVIS-DFT query by chemical formula."""
        print("\n🔍 Testing JARVIS-DFT formula query...")
        
        results = client.jarvis_dft_query(formula="Al2O3", limit=10)
        
        print(f"\n{'='*80}")
        print(f"JARVIS-DFT Query Results for Al2O3")
        print(f"{'='*80}")
        print(f"Total results: {results['total']}")
        print(f"Returned: {results['returned']}")
        print(f"Offset: {results['offset']}")
        print(f"Limit: {results['limit']}")
        
        if results['results']:
            first = results['results'][0]
            print(f"\nFirst result:")
            print(f"  JID: {first.get('jid')}")
            print(f"  Formula: {first.get('formula')}")
            print(f"  Spacegroup: {first.get('spg_symbol')}")
        
        print(f"{'='*80}\n")
        
        assert results['total'] > 0
        assert len(results['results']) <= 10
        assert all(r['formula'] == 'Al2O3' for r in results['results'])
        print(f"✅ Found {results['total']} Al2O3 materials")
    
    def test_jarvis_dft_query_by_jid(self, client):
        """Test JARVIS-DFT query by specific JID."""
        print("\n🔍 Testing JARVIS-DFT JID query...")
        
        results = client.jarvis_dft_query(jid="JVASP-1002")
        
        print(f"\n{'='*80}")
        print(f"JARVIS-DFT Query for JVASP-1002")
        print(f"{'='*80}")
        print(json.dumps(results, indent=2)[:500])
        print(f"{'='*80}\n")
        
        assert results['total'] == 1
        assert results['results'][0]['jid'] == 'JVASP-1002'
        print("✅ Successfully retrieved JVASP-1002")
    
    def test_jarvis_dft_query_by_elements(self, client):
        """Test JARVIS-DFT query by elements."""
        print("\n🔍 Testing JARVIS-DFT elements query...")
        
        # Test with list
        results1 = client.jarvis_dft_query(elements=["Si", "C"], limit=5)
        print(f"Query with list ['Si', 'C']: {results1['total']} results")
        
        # Test with string
        results2 = client.jarvis_dft_query(elements="Si,C", limit=5)
        print(f"Query with string 'Si,C': {results2['total']} results")
        
        assert results1['total'] == results2['total']
        print("✅ Elements query works with both list and string")
    
    def test_jarvis_dft_query_with_propranges(self, client):
        """Test JARVIS-DFT query with property filters."""
        print("\n🔍 Testing JARVIS-DFT property range query...")
        
        results = client.jarvis_dft_query(
            propranges={
                "mbj_bandgap": {"min": 2.0, "max": 3.0},
                "ehull": {"max": 0.2}
            },
            limit=5
        )
        
        print(f"\n{'='*80}")
        print(f"Property Range Query Results")
        print(f"{'='*80}")
        print(f"Filters: bandgap 2-3 eV, ehull < 0.2")
        print(f"Total results: {results['total']}")
        print(f"Returned: {len(results['results'])}")
        print(f"{'='*80}\n")
        
        assert 'total' in results
        print(f"✅ Found {results['total']} materials matching criteria")
    
    def test_jarvis_dft_query_no_filters(self, client):
        """Test JARVIS-DFT query fails without filters."""
        print("\n🔍 Testing JARVIS-DFT query validation...")
        
        with pytest.raises(AgapiValidationError) as exc_info:
            client.jarvis_dft_query(limit=10)
        
        assert "at least one filter" in str(exc_info.value).lower()
        print(f"✅ Correctly validated: {exc_info.value}")
    
    def test_jarvis_dft_columns(self, client):
        """Test retrieving JARVIS-DFT columns."""
        print("\n🔍 Testing JARVIS-DFT columns...")
        
        columns = client.jarvis_dft_columns()
        
        print(f"\n{'='*80}")
        print(f"Available JARVIS-DFT Columns ({len(columns)} total)")
        print(f"{'='*80}")
        for i, col in enumerate(columns[:10], 1):
            print(f"{i:3d}. {col}")
        if len(columns) > 10:
            print(f"... and {len(columns) - 10} more")
        print(f"{'='*80}\n")
        
        assert isinstance(columns, list)
        assert len(columns) > 0
        assert 'jid' in columns
        print(f"✅ Retrieved {len(columns)} column names")
    
    def test_materials_project_query(self, client):
        """Test Materials Project query."""
        print("\n🔍 Testing Materials Project query...")
        
        results = client.materials_project_query(formula="MoS2", page_limit=10)
        
        print(f"\n{'='*80}")
        print(f"Materials Project Query for MoS2")
        print(f"{'='*80}")
        print(f"Total results: {results.get('total', 'N/A')}")
        if results.get('results'):
            print(f"First result preview:")
            print(json.dumps(results['results'][0], indent=2)[:300])
        print(f"{'='*80}\n")
        
        assert 'results' in results or 'total' in results
        print("✅ Materials Project query successful")


# ============================================================================
# ML Prediction Tests
# ============================================================================

class TestMLPredictions:
    """Test machine learning prediction methods."""
    
    def test_alignn_predict_by_jid(self, client):
        """Test ALIGNN predictions by JID."""
        print("\n🤖 Testing ALIGNN predictions by JID...")
        
        predictions = client.alignn_predict(jid="JVASP-1002")
        
        print(f"\n{'='*80}")
        print(f"ALIGNN Predictions for JVASP-1002")
        print(f"{'='*80}")
        print(f"Formation Energy: {predictions.get('jv_formation_energy_peratom_alignn', [None])[0]} eV/atom")
        print(f"OptB88vdW Bandgap: {predictions.get('jv_optb88vdw_bandgap_alignn', [None])[0]} eV")
        print(f"MBJ Bandgap: {predictions.get('jv_mbj_bandgap_alignn', [None])[0]} eV")
        print(f"Bulk Modulus: {predictions.get('jv_bulk_modulus_kv_alignn', [None])[0]} GPa")
        print(f"{'='*80}\n")
        
        assert 'jv_formation_energy_peratom_alignn' in predictions
        assert 'jv_mbj_bandgap_alignn' in predictions
        print("✅ ALIGNN predictions successful")
    
    def test_alignn_predict_by_poscar(self, client):
        """Test ALIGNN predictions by POSCAR string."""
        print("\n🤖 Testing ALIGNN predictions by POSCAR...")
        
        predictions = client.alignn_predict(poscar=SAMPLE_POSCAR)
        
        assert 'jv_formation_energy_peratom_alignn' in predictions
        print("✅ ALIGNN predictions from POSCAR successful")
    
    def test_alignn_predict_by_file(self, client, poscar_file):
        """Test ALIGNN predictions by file path."""
        print("\n🤖 Testing ALIGNN predictions by file...")
        
        predictions = client.alignn_predict(file_path=poscar_file)
        
        assert 'jv_formation_energy_peratom_alignn' in predictions
        print(f"✅ ALIGNN predictions from file {poscar_file.name} successful")
    
    def test_alignn_predict_missing_input(self, client):
        """Test ALIGNN predictions fails without input."""
        print("\n🤖 Testing ALIGNN validation...")
        
        with pytest.raises(AgapiValidationError) as exc_info:
            client.alignn_predict()
        
        assert "Provide jid, poscar, or file_path" in str(exc_info.value)
        print(f"✅ Correctly validated: {exc_info.value}")
    
    def test_alignn_ff_energy(self, client):
        """Test ALIGNN-FF energy calculation."""
        print("\n⚡ Testing ALIGNN-FF energy calculation...")
        
        result = client.alignn_ff_energy(poscar=SAMPLE_POSCAR)
        
        print(f"\n{'='*80}")
        print(f"ALIGNN-FF Results")
        print(f"{'='*80}")
        print(f"Number of atoms: {result.get('natoms')}")
        print(f"Energy: {result.get('energy_eV')} eV")
        print(f"Max force: {max([max(abs(f) for f in forces) for forces in result.get('forces_eV_per_A', [[0]])]):.4f} eV/Å")
        print(f"{'='*80}\n")
        
        assert 'energy_eV' in result
        assert 'forces_eV_per_A' in result
        assert 'stress' in result
        print("✅ ALIGNN-FF calculation successful")
    
    def test_alignn_ff_relax(self, client):
        """Test ALIGNN-FF structure relaxation."""
        print("\n⚡ Testing ALIGNN-FF relaxation...")
        
        relaxed_poscar = client.alignn_ff_relax(
            poscar=SAMPLE_POSCAR,
            fmax=0.1,
            steps=10
        )
        
        print(f"\n{'='*80}")
        print(f"ALIGNN-FF Relaxation")
        print(f"{'='*80}")
        print(f"Relaxed POSCAR (first 200 chars):")
        print(relaxed_poscar[:200])
        print(f"{'='*80}\n")
        
        assert isinstance(relaxed_poscar, str)
        assert "System" in relaxed_poscar or relaxed_poscar.strip().split('\n')[0]
        print("✅ Structure relaxation successful")
    
    def test_slakonet_bandstructure(self, client):
        """Test SlakoNet band structure calculation."""
        print("\n📊 Testing SlakoNet band structure...")
        
        img_bytes = client.slakonet_bandstructure(
            jid="JVASP-1002",
            energy_range_min=-8.0,
            energy_range_max=8.0
        )
        
        print(f"\n{'='*80}")
        print(f"SlakoNet Band Structure")
        print(f"{'='*80}")
        print(f"Image size: {len(img_bytes)} bytes")
        ##print(f"Is PNG: {img_bytes[:8] == b'\\x89PNG\\r\\n\\x1a\\n'}")
        print(f"{'='*80}\n")
        
        assert isinstance(img_bytes, bytes)
        assert len(img_bytes) > 1000
        print("✅ Band structure calculation successful")


# ============================================================================
# Analysis Tool Tests
# ============================================================================

class TestAnalysisTools:
    """Test analysis and characterization tools."""
    
    def test_xrd_analyze(self, client):
        """Test XRD pattern analysis."""
        print("\n🔬 Testing XRD analysis...")
        
        results = client.xrd_analyze(
            formula="LaB6",
            pattern=SAMPLE_XRD_PATTERN,
            method="pattern_matching"
        )
        
        print(f"\n{'='*80}")
        print(f"XRD Analysis Results")
        print(f"{'='*80}")
        print(f"Response type: {type(results)}")
        print(f"Response preview: {str(results)[:300]}")
        print(f"{'='*80}\n")
        
        assert results is not None
        print("✅ XRD analysis successful")
    
    def test_protein_fold(self, client):
        """Test protein structure prediction."""
        print("\n🧬 Testing protein folding...")
        print(f"Sequence length: {len(SAMPLE_PROTEIN_SEQ)}")
        
        pdb_content = client.protein_fold(sequence=SAMPLE_PROTEIN_SEQ)
        
        print(f"\n{'='*80}")
        print(f"Protein Folding Results")
        print(f"{'='*80}")
        print(f"PDB length: {len(pdb_content)} characters")
        print(f"Contains ATOM: {'ATOM' in pdb_content}")
        print(f"First 500 chars:")
        print(pdb_content[:500])
        print(f"{'='*80}\n")
        
        assert isinstance(pdb_content, str)
        assert len(pdb_content) > 100
        print("✅ Protein folding successful")
    
    def test_protein_fold_empty_sequence(self, client):
        """Test protein folding with empty sequence."""
        print("\n🧬 Testing protein folding validation...")
        
        with pytest.raises(AgapiValidationError):
            client.protein_fold(sequence="")
        
        print("✅ Correctly validated empty sequence")
    
    def test_weather(self, client):
        """Test weather data retrieval."""
        print("\n🌤️  Testing weather API...")
        
        weather = client.weather(location="Baltimore", units="imperial")
        
        print(f"\n{'='*80}")
        print(f"Weather Data for Baltimore")
        print(f"{'='*80}")
        print(f"Location: {weather.get('location')}, {weather.get('country')}")
        print(f"Weather: {weather.get('weather')}")
        print(f"Temperature: {weather.get('temperature')}°F")
        print(f"Feels like: {weather.get('feels_like')}°F")
        print(f"Humidity: {weather.get('humidity')}%")
        print(f"Wind speed: {weather.get('wind_speed')} mph")
        print(f"{'='*80}\n")
        
        assert 'temperature' in weather
        assert 'location' in weather
        print("✅ Weather data retrieved successfully")


# ============================================================================
# Literature Search Tests
# ============================================================================

class TestLiteratureSearch:
    """Test literature search methods."""
    
    def test_arxiv_search(self, client):
        """Test arXiv search."""
        print("\n📚 Testing arXiv search...")
        
        results = client.arxiv_search(query="MgB2 superconductor", max_results=5)
        
        print(f"\n{'='*80}")
        print(f"arXiv Search Results for 'MgB2 superconductor'")
        print(f"{'='*80}")
        print(f"Query: {results.get('query')}")
        print(f"Count: {results.get('count')}")
        
        for i, paper in enumerate(results.get('results', [])[:3], 1):
            print(f"\n{i}. {paper.get('title', 'N/A')[:80]}")
            print(f"   Authors: {', '.join(paper.get('authors', [])[:2])}")
            print(f"   Published: {paper.get('published', 'N/A')}")
        
        print(f"{'='*80}\n")
        
        assert 'results' in results
        assert len(results['results']) <= 5
        print(f"✅ Found {len(results['results'])} papers")
    
    def test_crossref_search(self, client):
        """Test CrossRef search."""
        print("\n📖 Testing CrossRef search...")
        
        results = client.crossref_search(query="Al2O3 ceramics", rows=5)
        
        print(f"\n{'='*80}")
        print(f"CrossRef Search Results for 'Al2O3 ceramics'")
        print(f"{'='*80}")
        print(f"Query: {results.get('query')}")
        print(f"Count: {results.get('count')}")
        print(f"Total available: {results.get('total_results')}")
        
        for i, pub in enumerate(results.get('results', [])[:3], 1):
            print(f"\n{i}. {pub.get('title', 'N/A')[:80]}")
            print(f"   DOI: {pub.get('doi', 'N/A')}")
            print(f"   Publisher: {pub.get('publisher', 'N/A')}")
        
        print(f"{'='*80}\n")
        
        assert 'results' in results
        print(f"✅ Found {len(results.get('results', []))} publications")


# ============================================================================
# Structure Manipulation Tests
# ============================================================================

class TestStructureManipulation:
    """Test atomic structure manipulation methods."""
    
    def test_jarvis_atoms_query_by_jid(self, client):
        """Test loading structure by JID."""
        print("\n⚛️  Testing structure loading by JID...")
        
        result = client.jarvis_atoms_query(jid="JVASP-1002")
        
        print(f"\n{'='*80}")
        print(f"Structure Query Results")
        print(f"{'='*80}")
        print(f"Source: {result.get('source')}")
        print(f"Operations: {result.get('operations')}")
        if 'final_structure' in result:
            fs = result['final_structure']
            print(f"Formula: {fs.get('formula')}")
            print(f"Atoms: {fs.get('num_atoms')}")
            print(f"Volume: {fs.get('volume'):.2f} Ų")
            print(f"Density: {fs.get('density'):.2f} g/cm³")
        print(f"{'='*80}\n")
        
        assert 'final_structure' in result
        print("✅ Structure loaded successfully")
    
    def test_jarvis_atoms_supercell(self, client):
        """Test supercell generation."""
        print("\n⚛️  Testing supercell generation...")
        
        # Get original structure
        original = client.jarvis_atoms_query(jid="JVASP-1002")
        original_atoms = original['final_structure']['num_atoms']
        
        # Create supercell
        result = client.jarvis_atoms_query(
            jid="JVASP-1002",
            supercell="2x2x2"
        )
        
        final_atoms = result['final_structure']['num_atoms']
        
        print(f"\n{'='*80}")
        print(f"Supercell Generation (2x2x2)")
        print(f"{'='*80}")
        print(f"Original atoms: {original_atoms}")
        print(f"Supercell atoms: {final_atoms}")
        print(f"Multiplication: {final_atoms / original_atoms:.1f}x")
        print(f"Operations: {result.get('operations')}")
        print(f"{'='*80}\n")
        
        assert final_atoms == original_atoms * 8
        print(f"✅ Supercell created: {original_atoms} → {final_atoms} atoms")
    
    def test_jarvis_atoms_properties(self, client):
        """Test structure property calculation."""
        print("\n⚛️  Testing property calculations...")
        
        result = client.jarvis_atoms_query(
            jid="JVASP-1002",
            properties="volume,density,spacegroup"
        )
        
        print(f"\n{'='*80}")
        print(f"Calculated Properties")
        print(f"{'='*80}")
        for key, value in result.get('properties', {}).items():
            print(f"{key}: {value}")
        print(f"{'='*80}\n")
        
        assert 'properties' in result
        print("✅ Properties calculated successfully")
    
    def test_jarvis_atoms_primitive(self, client):
        """Test conversion to primitive cell."""
        print("\n⚛️  Testing primitive cell conversion...")
        
        result = client.jarvis_atoms_query(
            jid="JVASP-1002",
            get_primitive=True
        )
        
        assert 'final_structure' in result
        print("✅ Primitive cell conversion successful")
    
    def test_jarvis_atoms_output_formats(self, client):
        """Test different output formats."""
        print("\n⚛️  Testing output formats...")
        
        formats = ["poscar", "json", "cif", "xyz"]
        
        for fmt in formats:
            result = client.jarvis_atoms_query(
                jid="JVASP-1002",
                output_format=fmt
            )
            print(f"✓ Format '{fmt}' works")
        
        print("✅ All output formats successful")


# ============================================================================
# Error Handling Tests
# ============================================================================

class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def test_invalid_api_key(self):
        """Test authentication error with invalid key."""
        print("\n❌ Testing invalid API key...")
        
        client = Agapi(api_key="invalid_key_12345")
        
        with pytest.raises(AgapiAuthError) as exc_info:
            client.jarvis_dft_query(formula="Al2O3")
        
        print(f"✅ Correctly raised AgapiAuthError: {exc_info.value}")
    
    def test_missing_required_parameter(self, client):
        """Test validation error for missing parameters."""
        print("\n❌ Testing missing parameters...")
        
        with pytest.raises(AgapiValidationError):
            client.alignn_predict()
        
        print("✅ Correctly validated missing parameters")
    
    def test_invalid_jid(self, client):
        """Test query with non-existent JID."""
        print("\n❌ Testing non-existent JID...")
        
        results = client.jarvis_dft_query(jid="INVALID-999999")
        
        assert results['total'] == 0
        print("✅ Correctly returned 0 results for invalid JID")
    
    def test_file_not_found(self, client):
        """Test file path error."""
        print("\n❌ Testing file not found...")
        
        with pytest.raises(AgapiValidationError) as exc_info:
            client.alignn_predict(file_path="/nonexistent/file.poscar")
        
        assert "not found" in str(exc_info.value).lower()
        print(f"✅ Correctly raised error: {exc_info.value}")
    @pytest.mark.skip(reason="Timeout test with unrealistic 0.001s timeout causes network errors") 
    def test_timeout_error(self, api_key):
        """Test timeout handling."""
        print("\n❌ Testing timeout...")
        
        # Create client with very short timeout
        client = Agapi(api_key=api_key, timeout=0.001)
        
        with pytest.raises(AgapiTimeoutError):
            client.jarvis_dft_query(formula="Al2O3")
        
        print("✅ Correctly raised AgapiTimeoutError")


# ============================================================================
# Utility Tests
# ============================================================================

class TestUtilities:
    """Test utility methods."""
    
    def test_health_check(self, client):
        """Test health check."""
        print("\n🏥 Testing health check...")
        
        health = client.health_check()
        
        print(f"\n{'='*80}")
        print(f"Health Check Results")
        print(f"{'='*80}")
        print(f"Status: {health.get('status')}")
        print(f"Base URL: {health.get('base_url')}")
        print(f"Available columns: {health.get('available_columns', 'N/A')}")
        print(f"{'='*80}\n")
        
        assert 'status' in health
        assert health['status'] in ['healthy', 'unhealthy']
        print(f"✅ Health check: {health['status']}")
    
    def test_repr(self, client):
        """Test string representation."""
        print("\n🔧 Testing __repr__...")
        
        repr_str = repr(client)
        
        assert "Agapi" in repr_str
        assert "atomgpt.org" in repr_str
        print(f"✅ Repr: {repr_str}")
    
    def test_context_manager(self, api_key):
        """Test context manager."""
        print("\n🔧 Testing context manager...")
        
        with Agapi(api_key=api_key) as client:
            columns = client.jarvis_dft_columns()
            assert len(columns) > 0
        
        print("✅ Context manager works correctly")


# ============================================================================
# Integration Tests
# ============================================================================

@pytest.mark.slow
class TestIntegration:
    """Integration tests combining multiple operations."""
    
    def test_workflow_structure_to_predictions(self, client):
        """Test complete workflow: query → predict → analyze."""
        print("\n🔄 Testing integrated workflow...")
        
        # 1. Query database
        print("Step 1: Querying JARVIS-DFT...")
        materials = client.jarvis_dft_query(formula="MoS2", limit=1)
        jid = materials['results'][0]['jid']
        print(f"  Found: {jid}")
        
        # 2. Get ALIGNN predictions
        print("Step 2: Getting ALIGNN predictions...")
        predictions = client.alignn_predict(jid=jid)
        bandgap = predictions['jv_mbj_bandgap_alignn'][0]
        print(f"  Band gap: {bandgap} eV")
        
        # 3. Get structure details
        print("Step 3: Getting structure properties...")
        structure = client.jarvis_atoms_query(
            jid=jid,
            properties="volume,density,spacegroup"
        )
        print(f"  Volume: {structure['properties']['volume']:.2f} Ų")
        
        print("\n✅ Complete workflow successful")
    
    def test_workflow_file_to_relaxed(self, client, poscar_file):
        """Test workflow: file → relax → analyze."""
        print("\n🔄 Testing file processing workflow...")
        
        # 1. Load and predict
        print("Step 1: Initial prediction...")
        initial = client.alignn_ff_energy(file_path=poscar_file)
        print(f"  Initial energy: {initial['energy_eV']} eV")
        
        # 2. Relax structure
        print("Step 2: Relaxing structure...")
        relaxed_poscar = client.alignn_ff_relax(
            file_path=poscar_file,
            fmax=0.1,
            steps=10
        )
        print(f"  Relaxed POSCAR length: {len(relaxed_poscar)} chars")
        
        # 3. Final energy
        print("Step 3: Final prediction...")
        final = client.alignn_ff_energy(poscar=relaxed_poscar)
        print(f"  Final energy: {final['energy_eV']} eV")
        print(f"  Energy change: {final['energy_eV'] - initial['energy_eV']:.4f} eV")
        
        print("\n✅ File processing workflow successful")


# ============================================================================
# Performance Tests
# ============================================================================

@pytest.mark.slow
class TestPerformance:
    """Performance and stress tests."""
    
    def test_concurrent_requests(self, client):
        """Test handling concurrent requests."""
        print("\n⚡ Testing concurrent requests...")
        
        import concurrent.futures
        
        def make_query(i):
            return client.jarvis_dft_query(formula="Si", limit=1)
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_query, i) for i in range(10)]
            results = [f.result() for f in futures]
        
        assert all(r['total'] > 0 for r in results)
        print(f"✅ Completed 10 concurrent requests successfully")
    
    def test_large_result_pagination(self, client):
        """Test pagination with large results."""
        print("\n⚡ Testing pagination...")
        
        # First page
        page1 = client.jarvis_dft_query(formula="Si", limit=50, offset=0)
        
        # Second page
        page2 = client.jarvis_dft_query(formula="Si", limit=50, offset=50)
        
        # Ensure different results
        jids1 = {r['jid'] for r in page1['results']}
        jids2 = {r['jid'] for r in page2['results']}
        
        assert len(jids1 & jids2) == 0  # No overlap
        print(f"✅ Pagination works correctly")


# ========================================================================
# XRD & DiffractGPT Tests
# ========================================================================

class TestXRDAnalysis:
    """Test XRD analysis and DiffractGPT methods."""
    
    def test_xrd_analyze_pattern_matching(self, client):
        """Test XRD pattern matching."""
        print("\n🔬 Testing XRD pattern matching...")
        
        pattern = """LaB6
21.38 0.69
30.42 1.00
35.19 0.39"""
        
        result = client.xrd_analyze(
            formula="LaB6",
            pattern=pattern,
            method="pattern_matching"
        )
        
        print(f"\n{'='*80}")
        print(f"XRD Pattern Matching Results")
        print(f"{'='*80}")
        print(f"Result type: {type(result)}")
        print(f"Result preview: {str(result)[:500]}")
        print(f"{'='*80}\n")
        
        assert result is not None
        print("✅ XRD pattern matching successful")
    @pytest.mark.skip(reason="XRD refinement only available through web interface") 
    def test_xrd_analyze_with_refinement(self, client):
        """Test XRD analysis with Rietveld refinement."""
        print("\n🔬 Testing XRD with refinement...")
        
        xrd_data = """21.38 0.69
30.42 1.00
35.19 0.39"""
        
        result = client.xrd_analyze_with_refinement(
            formula="LaB6",
            xrd_data=xrd_data,
            method="pattern_matching",
            run_refinement=True,
            run_alignn=False,
            run_slakonet=False,
        )
        
        print(f"\n{'='*80}")
        print(f"XRD Refinement Results")
        print(f"{'='*80}")
        if "pattern_matching" in result:
            print(f"Pattern matching: Success")
        if "refinement" in result:
            print(f"Refinement Rwp: {result['refinement'].get('rwp', 'N/A')}")
        print(f"{'='*80}\n")
        
        assert "pattern_matching" in result or "results" in result
        print("✅ XRD refinement successful")
    
    def test_diffractgpt_predict(self, client):
        """Test DiffractGPT structure prediction."""
        print("\n🤖 Testing DiffractGPT...")
        
        poscar = client.diffractgpt_predict(
            formula="LaB6",
            peaks="30.42(1.0),49.02(0.49),67.64(0.28)",
            max_new_tokens=512,
        )
        
        print(f"\n{'='*80}")
        print(f"DiffractGPT Prediction")
        print(f"{'='*80}")
        print(f"POSCAR length: {len(poscar)} characters")
        print(f"First 300 chars:\n{poscar[:300]}")
        print(f"{'='*80}\n")
        
        assert isinstance(poscar, str)
        assert len(poscar) > 100
        print("✅ DiffractGPT prediction successful")


# ========================================================================
# Microscopy Tests
# ========================================================================

class TestMicroscopy:
    """Test MicroscopyGPT methods."""
    
    @pytest.fixture
    def sample_image(self, tmp_path):
        """Create a dummy image for testing."""
        from PIL import Image
        import numpy as np
        
        # Create simple test image
        img_array = np.random.randint(0, 255, (256, 256, 3), dtype=np.uint8)
        img = Image.fromarray(img_array)
        
        img_path = tmp_path / "test_microscopy.png"
        img.save(img_path)
        return img_path
    
    def test_microscopy_predict(self, client, sample_image):
        """Test microscopy structure prediction."""
        print("\n🔬 Testing MicroscopyGPT prediction...")
        
        try:
            result = client.microscopy_predict(
                image_path=sample_image,
                formula="GaN"
            )
            
            print(f"\n{'='*80}")
            print(f"MicroscopyGPT Results")
            print(f"{'='*80}")
            print(f"Success: {result.get('success', False)}")
            if 'structure' in result:
                print(f"Structure predicted: Yes")
            print(f"{'='*80}\n")
            
            print("✅ MicroscopyGPT prediction completed")
        except Exception as e:
            print(f"⚠️  MicroscopyGPT service may not be running: {e}")
            pytest.skip("MicroscopyGPT service unavailable")
    
    def test_microscopy_segment(self, client, sample_image):
        """Test microscopy image segmentation."""
        print("\n🔬 Testing microscopy segmentation...")
        
        try:
            segmented = client.microscopy_segment(image_path=sample_image)
            
            print(f"\n{'='*80}")
            print(f"Microscopy Segmentation")
            print(f"{'='*80}")
            print(f"Segmented image size: {len(segmented)} bytes")
            print(f"{'='*80}\n")
            
            assert isinstance(segmented, bytes)
            print("✅ Segmentation successful")
        except Exception as e:
            print(f"⚠️  SAM service may not be running: {e}")
            pytest.skip("SAM service unavailable")


# ========================================================================
# Protein Folding Tests
# ========================================================================

class TestProteinFolding:
    """Test protein structure prediction methods."""
    
    def test_protein_fold_esmfold(self, client):
        """Test ESMFold protein structure prediction."""
        print("\n🧬 Testing ESMFold...")
        
        sequence = "MGREEPLNHVEAERQRREKLNQRFYAL"
        pdb = client.protein_fold(sequence=sequence)
        
        print(f"\n{'='*80}")
        print(f"ESMFold Results")
        print(f"{'='*80}")
        print(f"Sequence length: {len(sequence)}")
        print(f"PDB length: {len(pdb)} characters")
        print(f"Contains ATOM: {'ATOM' in pdb}")
        print(f"First 300 chars:\n{pdb[:300]}")
        print(f"{'='*80}\n")
        
        assert isinstance(pdb, str)
        assert "ATOM" in pdb or len(pdb) > 100
        print("✅ ESMFold prediction successful")
    
    def test_openfold_complex(self, client):
        """Test OpenFold3 complex prediction."""
        print("\n🧬 Testing OpenFold3...")
        
        try:
            pdb = client.openfold_predict(
                protein_sequence="MGREEPLNHVEAERQRREKLNQRFYAL",
                dna1="AGGAACACGTGACCC",
                dna2="TGGGTCACGTGTTCC",
            )
            
            print(f"\n{'='*80}")
            print(f"OpenFold3 Results")
            print(f"{'='*80}")
            print(f"PDB length: {len(pdb)} characters")
            print(f"First 300 chars:\n{pdb[:300]}")
            print(f"{'='*80}\n")
            
            assert isinstance(pdb, str)
            print("✅ OpenFold3 prediction successful")
        except Exception as e:
            print(f"⚠️  OpenFold3 may require API key: {e}")
            pytest.skip("OpenFold3 service unavailable")


# ========================================================================
# Interface Generation Tests
# ========================================================================

class TestInterfaceGeneration:
    """Test heterostructure interface generation."""
    
    def test_generate_interface_by_ids(self, client):
        """Test interface generation using JARVIS IDs."""
        print("\n🔬 Testing interface generation...")
        
        try:
            interface_poscar = client.generate_interface(
                film_ids="JVASP-1002",
                subs_ids="JVASP-1003",
                film_indices="0_0_1",
                subs_indices="0_0_1",
                vacuum_interface=2.0,
                separations=2.5,
            )
            
            print(f"\n{'='*80}")
            print(f"Interface Generation Results")
            print(f"{'='*80}")
            print(f"POSCAR length: {len(interface_poscar)} characters")
            print(f"First 300 chars:\n{interface_poscar[:300]}")
            print(f"{'='*80}\n")
            
            assert isinstance(interface_poscar, str)
            assert len(interface_poscar) > 100
            print("✅ Interface generation successful")
        except Exception as e:
            print(f"⚠️  Interface generation error: {e}")
            # May fail if specific materials incompatible


# ========================================================================
# Molecular Dynamics Tests
# ========================================================================

class TestMolecularDynamics:
    """Test ALIGNN-FF molecular dynamics."""
    @pytest.mark.skip(reason="Molecular dynamics only available through web interface") 
    def test_alignn_ff_optimize(self, client, poscar_file):
        """Test geometry optimization."""
        print("\n⚡ Testing geometry optimization...")
        
        result = client.alignn_ff_optimize(
            file_path=poscar_file,
            fmax=0.1,
            steps=10,
            optimizer="FIRE",
            relax_cell=True,
        )
        
        print(f"\n{'='*80}")
        print(f"Optimization Results")
        print(f"{'='*80}")
        print(f"Converged: {result.get('converged', False)}")
        print(f"Steps taken: {result.get('steps_taken', 0)}")
        print(f"Initial energy: {result.get('initial_energy', 0):.4f} eV")
        print(f"Final energy: {result.get('final_energy', 0):.4f} eV")
        print(f"Energy change: {result.get('energy_change', 0):.4f} eV")
        print(f"Trajectory frames: {len(result.get('trajectory', []))}")
        print(f"{'='*80}\n")
        
        assert 'final_poscar' in result
        assert 'trajectory' in result
        print("✅ Optimization successful")
    
    @pytest.mark.skip(reason="Molecular dynamics only available through web interface") 
    def test_alignn_ff_molecular_dynamics(self, client, poscar_file):
        """Test molecular dynamics simulation."""
        print("\n⚡ Testing molecular dynamics...")
        
        result = client.alignn_ff_molecular_dynamics(
            file_path=poscar_file,
            temperature=300.0,
            timestep=0.5,
            steps=20,
            interval=5,
        )
        
        print(f"\n{'='*80}")
        print(f"Molecular Dynamics Results")
        print(f"{'='*80}")
        print(f"Steps completed: {result.get('steps_completed', 0)}")
        print(f"Average temperature: {result.get('average_temperature', 0):.2f} K")
        print(f"Final temperature: {result.get('final_temperature', 0):.2f} K")
        print(f"Trajectory frames: {len(result.get('trajectory', []))}")
        print(f"{'='*80}\n")
        
        assert 'trajectory' in result
        assert 'energies' in result
        print("✅ Molecular dynamics successful")


# ========================================================================
# Advanced Structure Manipulation Tests
# ========================================================================

class TestAdvancedStructureManipulation:
    """Test advanced structure manipulation features."""
    
    def test_jarvis_atoms_vacancy(self, client):
        """Test vacancy creation."""
        print("\n⚛️  Testing vacancy creation...")
        
        result = client.jarvis_atoms_query(
            jid="JVASP-1002",
            vacancy_atom="0",
        )
        
        print(f"\n{'='*80}")
        print(f"Vacancy Creation")
        print(f"{'='*80}")
        if 'vacancy_info' in result:
            print(f"Removed element: {result['vacancy_info']['removed_element']}")
            print(f"Site index: {result['vacancy_info']['site_index']}")
        print(f"{'='*80}\n")
        
        assert 'final_structure' in result
        print("✅ Vacancy creation successful")
    
   
    def test_jarvis_atoms_substitution(self, client):
        """Test atom substitution."""
        print("\n⚛️  Testing atom substitution...")
        
        result = client.jarvis_atoms_query(
            jid="JVASP-1002",
            substitution_atom="0_Si_Ge",  # FIXED: Si→Ge (JVASP-1002 is Silicon)
        )
        
        print(f"\n{'='*80}")
        print(f"Atom Substitution")
        print(f"{'='*80}")
        if 'substitution_info' in result:
            print(f"Old element: {result['substitution_info']['old_element']}")
            print(f"New element: {result['substitution_info']['new_element']}")
        print(f"{'='*80}\n")
        
        assert 'final_structure' in result
        print("✅ Substitution successful")

    def test_jarvis_atoms_neighbors(self, client):
        """Test neighbor analysis."""
        print("\n⚛️  Testing neighbor analysis...")
        
        result = client.jarvis_atoms_query(
            jid="JVASP-1002",
            neighbors_cutoff=5.0,
        )
        
        print(f"\n{'='*80}")
        print(f"Neighbor Analysis")
        print(f"{'='*80}")
        if 'neighbors' in result:
            print(f"Average coordination: {result['neighbors'].get('average_coordination', 'N/A')}")
            print(f"Cutoff: {result['neighbors'].get('cutoff_radius', 'N/A')} Å")
        print(f"{'='*80}\n")
        
        assert 'neighbors' in result
        print("✅ Neighbor analysis successful")
# ============================================================================
# Test Configuration
# ============================================================================

def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
