# 🌐 AtomGPT.org API (AGAPI)

AGAPI provides a simple way to interact with [AtomGPT.org](https://atomgpt.org/), enabling **Agentic AI materials science research** through intuitive APIs.

A significant amount of time in computational materials design is often spent on software installation and setup — a major barrier for newcomers.  

**AGAPI removes this hurdle** by offering APIs for prediction, analysis, and exploration directly through natural language or Python interfaces, lowering entry barriers and accelerating research.

---

 [![Open in Google Colab]](https://colab.research.google.com/github/knc6/jarvis-tools-notebooks/blob/master/jarvis-tools-notebooks/agapi_example.ipynb)

  [Open in Google Colab]: https://colab.research.google.com/assets/colab-badge.svg



Official Python client for the [AtomGPT.org](https://atomgpt.org) API - providing access to computational materials science tools, databases, and AI-powered property predictions.

## Features

- 🔍 **Database Access**: Query 80,000+ materials from JARVIS-DFT and Materials Project
- 🤖 **ML Predictions**: ALIGNN property predictions (bandgap, formation energy, elastic moduli)
- ⚡ **Force Fields**: ALIGNN-FF structure relaxation
- 📊 **Electronic Structure**: SlakoNet tight-binding band structure calculations
- 🔬 **XRD Analysis**: Pattern matching and structure prediction with DiffractGPT
- 🧬 **Protein Folding**: ESMFold structure prediction from sequences
- ⚛️ **Structure Tools**: Supercells, vacancies, substitutions, interface generation
- 🌐 **Literature Search**: arXiv and CrossRef API integration
- 🤖 **AI Agent**: Natural language interface for materials discovery

## Installation

```bash
pip install agapi
```

Or install from source:

```bash
git clone https://github.com/usnistgov/atomgpt.git
cd atomgpt/agapi
pip install -e .
```

## Quick Start

### Get Your API Key

1. Visit [AtomGPT.org](https://atomgpt.org)
2. Sign up for a free account
3. Get your API key from settings

### Basic Usage

```python
from agapi import Agapi

# Initialize client
client = Agapi(api_key="sk-your-api-key-here")

# Or use environment variable
import os
os.environ["AGAPI_API_KEY"] = "sk-your-api-key-here"
client = Agapi()

# Query materials database
results = client.jarvis_dft_query(formula="GaN", limit=5)
print(f"Found {results['total']} GaN structures")

# Predict properties with ALIGNN
predictions = client.alignn_predict(jid="JVASP-1002")
print(f"Bandgap: {predictions['jv_mbj_bandgap_alignn'][0]:.3f} eV")

# Check API health
health = client.health_check()
print(f"API Status: {health['status']}")
```

## Core Features

### 1. Database Queries

#### JARVIS-DFT Database

```python
# Query by formula
materials = client.jarvis_dft_query(formula="SiC", limit=10)
print(f"Found {materials['total']} SiC polymorphs")

for mat in materials['results']:
    print(f"{mat['jid']}: {mat['spg_symbol']}, Eg={mat['mbj_bandgap']} eV")

# Query by elements
materials = client.jarvis_dft_query(elements=["Ga", "N"], limit=20)

# Query by properties
materials = client.jarvis_dft_query(
    propranges={
        "mbj_bandgap": {"min": 2.0, "max": 3.0},
        "ehull": {"max": 0.1}
    }
)

# Get specific material by JID
material = client.jarvis_dft_query(jid="JVASP-1002")
poscar = material['results'][0]['POSCAR']
```

#### Materials Project (via OPTIMADE)

```python
results = client.materials_project_query(
    formula="MoS2",
    page_limit=10
)

print(f"Found {len(results['results'])} MoS2 entries")
for entry in results['results']:
    print(f"MP-ID: {entry['id'][0]}")
    print(f"Formation energy: {entry['formation_energy_peratom_r2scan']:.3f} eV/atom")
```

#### Available Columns

```python
# Get all queryable properties
columns = client.jarvis_dft_columns()
print(f"Available properties: {len(columns)}")
print(columns[:10])  # First 10: jid, formula, spg_number, bandgap, etc.
```

### 2. Machine Learning Predictions

#### ALIGNN Property Predictions

```python
# Predict from JARVIS ID
predictions = client.alignn_predict(jid="JVASP-1002")

# Predict from POSCAR string
poscar_string = """Si
1.0
3.840198 0.0 0.0
0.0 3.840198 0.0
0.0 0.0 3.840198
Si
2
direct
0.00 0.00 0.00
0.25 0.25 0.25"""

predictions = client.alignn_predict(poscar=poscar_string)

# Access predictions
print(f"Formation energy: {predictions['jv_formation_energy_peratom_alignn'][0]:.4f} eV/atom")
print(f"Bandgap (MBJ): {predictions['jv_mbj_bandgap_alignn'][0]:.3f} eV")
print(f"Bandgap (OptB88vdW): {predictions['jv_optb88vdw_bandgap_alignn'][0]:.3f} eV")
print(f"Bulk modulus: {predictions['jv_bulk_modulus_kv_alignn'][0]:.1f} GPa")
print(f"Shear modulus: {predictions['jv_shear_modulus_gv_alignn'][0]:.1f} GPa")
```

#### ALIGNN Force Field Relaxation

```python
# Relax structure
relaxed_poscar = client.alignn_ff_relax(
    poscar=poscar_string,
    fmax=0.05,  # Force convergence (eV/Å)
    steps=200   # Max optimization steps
)

print("Relaxed structure:")
print(relaxed_poscar)

# Save to file
with open("relaxed.vasp", "w") as f:
    f.write(relaxed_poscar)
```

#### ALIGNN-FF Energy & Forces

```python
# Calculate energy and forces
result = client.alignn_ff_energy(poscar=poscar_string)

print(f"Energy: {result['energy_eV']:.4f} eV")
print(f"Forces (first atom): {result['forces_eV_per_A'][0]}")
print(f"Stress tensor: {result['stress']}")
```

### 3. Electronic Structure

#### SlakoNet Band Structure

```python
# Calculate band structure
img_bytes = client.slakonet_bandstructure(
    jid="JVASP-1002",
    energy_range_min=-8.0,
    energy_range_max=8.0
)

# Save band structure plot
with open("bandstructure.png", "wb") as f:
    f.write(img_bytes)

print("Band structure saved to bandstructure.png")
```

### 4. XRD Analysis

#### Pattern Matching

```python
xrd_pattern = """LaB6
21.38 0.69
30.42 1.00
35.19 0.39
49.02 0.49
67.64 0.28"""

# Match to database
result = client.xrd_analyze(
    formula="LaB6",
    pattern=xrd_pattern,
    wavelength=1.54184,  # Cu K-alpha
    method="pattern_matching"
)

print("Matched structure:")
print(result[:200])  # First 200 chars of POSCAR
```

#### DiffractGPT (XRD → Structure)

```python
# Predict structure from XRD peaks
predicted_structure = client.diffractgpt_predict(
    formula="LaB6",
    peaks="30.42(1.0),49.02(0.49),67.64(0.28)",
    max_new_tokens=1024
)

print("Predicted POSCAR:")
print(predicted_structure)
```

### 5. Structure Manipulation

#### Create Supercells

```python
# Load structure and create 2x2x2 supercell
result = client.jarvis_atoms_query(
    jid="JVASP-1002",
    supercell="2x2x2"
)

print(f"Original atoms: {result['operations'][0]}")
print(f"Supercell atoms: {result['final_structure']['num_atoms']}")
print(f"Formula: {result['final_structure']['formula']}")
```

#### Create Vacancies

```python
# Create vacancy defect
result = client.jarvis_atoms_query(
    jid="JVASP-1002",
    supercell="2x2x2",  # First make supercell
    vacancy_atom="0"     # Remove first atom
)

print(f"Created vacancy at site 0")
print(f"New atom count: {result['final_structure']['num_atoms']}")
```

#### Atom Substitution

```python
# Substitute Si → Ge
result = client.jarvis_atoms_query(
    jid="JVASP-1002",
    substitution_atom="0_Si_Ge"  # site_from_to
)

print(f"Substituted Si with Ge")
print(f"New formula: {result['final_structure']['formula']}")
```

#### Get Primitive Cell

```python
result = client.jarvis_atoms_query(
    jid="JVASP-1002",
    get_primitive=True
)

print(f"Primitive cell: {result['final_structure']['num_atoms']} atoms")
```

#### Multiple Output Formats

```python
# POSCAR format (default)
poscar = client.jarvis_atoms_query(jid="JVASP-1002", output_format="poscar")

# CIF format
cif = client.jarvis_atoms_query(jid="JVASP-1002", output_format="cif")

# XYZ format
xyz = client.jarvis_atoms_query(jid="JVASP-1002", output_format="xyz")

# JSON format
json_data = client.jarvis_atoms_query(jid="JVASP-1002", output_format="json")
```

### 6. Protein Structure Prediction

```python
# Predict protein structure with ESMFold
sequence = "MKTAYIAKQRQISFVKSHFSRQLEEMKKELEDAVDVDGDGTVNYEEFVQMMTAK"

pdb_structure = client.protein_fold(sequence=sequence)

# Save PDB file
with open("protein.pdb", "w") as f:
    f.write(pdb_structure)

print(f"Predicted structure for {len(sequence)} amino acid protein")
```

### 7. Literature Search

#### arXiv Search

```python
papers = client.arxiv_search(
    query="GaN superconductor",
    max_results=5
)

print(f"Found {papers['count']} papers")
for paper in papers['results']:
    print(f"\n{paper['title']}")
    print(f"Authors: {', '.join(paper['authors'][:3])}")
    print(f"Published: {paper['published']}")
    print(f"arXiv: {paper['arxiv_id']}")
```

#### CrossRef Search

```python
pubs = client.crossref_search(
    query="metal organic frameworks",
    rows=10
)

print(f"Found {pubs['total_results']} publications")
for pub in pubs['results'][:5]:
    print(f"\n{pub['title']}")
    print(f"DOI: {pub['doi']}")
    print(f"Publisher: {pub['publisher']}")
```

### 8. Weather Data

```python
weather = client.weather(
    location="San Francisco",
    units="imperial"  # or "metric"
)

print(f"Location: {weather['location']}, {weather['country']}")
print(f"Temperature: {weather['temperature']}°F")
print(f"Weather: {weather['weather']}")
print(f"Humidity: {weather['humidity']}%")
```

## AI Agent Interface

Use natural language to interact with all AGAPI features:

```python
from agapi.agents import AGAPIAgent

# Initialize agent
agent = AGAPIAgent(api_key="sk-your-api-key")

# Simple queries
response = agent.query_sync("Find all SiC materials")
print(response)

# Complex workflows
response = agent.query_sync("""
Create a 2x2x2 supercell of GaN (JVASP-1067), 
create a Ga vacancy, 
relax it with ALIGNN-FF, 
and predict the bandgap with ALIGNN
""")
print(response)

# Render as HTML in Jupyter
agent.query_sync(
    "Find semiconductors with bandgap 2-3 eV",
    render_html=True
)

# Get raw data
result = agent.query_sync(
    "Predict properties of JVASP-1002",
    return_dict=True
)
print(result['predictions'])
```

### Agent Examples

```python
# Database queries
agent.query_sync("Find all materials containing Ga and N")
agent.query_sync("What's the most stable polymorph of SiC?")
agent.query_sync("Find 2D materials with high electron mobility")

# Property predictions
agent.query_sync("Predict bandgap of JVASP-1002")
agent.query_sync("Calculate band structure for wurtzite GaN")
agent.query_sync("What are the elastic moduli of diamond?")

# Structure modifications
agent.query_sync("Create GaN with one Ga vacancy in 2x2x2 supercell and relax")
agent.query_sync("Make Al-doped GaN (10% substitution) and predict bandgap")

# Materials discovery
agent.query_sync("Find materials similar to GaN with larger bandgap")
agent.query_sync("Compare MBJ vs OptB88vdW bandgaps for III-V semiconductors")

# XRD analysis
agent.query_sync("Generate XRD pattern for LaB6")
agent.query_sync("Predict structure from these XRD peaks: 30.42(1.0), 49.02(0.49)")

# Protein folding
agent.query_sync("Predict structure of protein with sequence MKTAYIAK...")
```

## Complete Workflow Example

```python
from agapi import Agapi

client = Agapi(api_key="sk-your-api-key")

# 1. Find materials
print("Step 1: Finding GaN polymorphs...")
materials = client.jarvis_dft_query(formula="GaN", limit=5)
print(f"Found {materials['total']} structures")

# 2. Get most stable structure
best_jid = materials['results'][0]['jid']
print(f"\nStep 2: Using {best_jid}")

# 3. Get structure
material = client.jarvis_atoms_query(jid=best_jid)
poscar = material['final_structure']['poscar']

# 4. Create supercell with vacancy
print("\nStep 3: Creating 2x2x2 supercell with Ga vacancy...")
defect_structure = client.jarvis_atoms_query(
    jid=best_jid,
    supercell="2x2x2",
    vacancy_atom="0"  # Remove first Ga
)

# 5. Relax structure
print("\nStep 4: Relaxing defect structure...")
relaxed = client.alignn_ff_relax(
    poscar=defect_structure['final_structure']['poscar'],
    fmax=0.05,
    steps=200
)

# 6. Predict properties
print("\nStep 5: Predicting properties of relaxed structure...")
predictions = client.alignn_predict(poscar=relaxed)

print("\n=== Results ===")
print(f"Original: {materials['results'][0]['formula']}")
print(f"Bandgap (pristine): {materials['results'][0]['mbj_bandgap']:.3f} eV")
print(f"Bandgap (defect): {predictions['jv_mbj_bandgap_alignn'][0]:.3f} eV")
print(f"Formation energy: {predictions['jv_formation_energy_peratom_alignn'][0]:.4f} eV/atom")

# 7. Calculate band structure
print("\nStep 6: Calculating band structure...")
band_img = client.slakonet_bandstructure(poscar=relaxed)
with open("defect_bandstructure.png", "wb") as f:
    f.write(band_img)
print("Band structure saved!")
```

## Error Handling

```python
from agapi import Agapi, AgapiError, AgapiAuthError, AgapiValidationError

client = Agapi(api_key="sk-your-api-key")

try:
    # Invalid query
    result = client.jarvis_dft_query(formula="InvalidFormula123")
    
except AgapiAuthError as e:
    print(f"Authentication failed: {e}")
    print("Check your API key at https://atomgpt.org")
    
except AgapiValidationError as e:
    print(f"Invalid request: {e}")
    
except AgapiError as e:
    print(f"API error: {e}")
    
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Advanced Features

### Context Manager

```python
with Agapi(api_key="sk-your-api-key") as client:
    materials = client.jarvis_dft_query(formula="GaN")
    predictions = client.alignn_predict(jid="JVASP-1002")
    # Session automatically closed
```

### Custom Configuration

```python
client = Agapi(
    api_key="sk-your-api-key",
    base_url="https://atomgpt.org",  # Custom API endpoint
    timeout=120,  # Request timeout in seconds
    retries=3     # Number of retry attempts
)
```

### Batch Processing

```python
# Process multiple structures
jids = ["JVASP-1002", "JVASP-816", "JVASP-1067"]

results = []
for jid in jids:
    try:
        pred = client.alignn_predict(jid=jid)
        results.append({
            'jid': jid,
            'bandgap': pred['jv_mbj_bandgap_alignn'][0],
            'formation_energy': pred['jv_formation_energy_peratom_alignn'][0]
        })
    except Exception as e:
        print(f"Failed for {jid}: {e}")

# Analysis
import pandas as pd
df = pd.DataFrame(results)
print(df)
```

## API Reference

### Client Initialization

```python
Agapi(
    api_key: str = None,          # API key (or set AGAPI_API_KEY env var)
    base_url: str = "https://atomgpt.org",
    timeout: int = 120,            # Request timeout in seconds
    retries: int = 3,              # Number of retry attempts
    verbose: bool = False          # Enable debug logging
)
```

### Database Methods

- `jarvis_dft_query(formula, jid, elements, propranges, limit, offset, fields)` - Query JARVIS-DFT
- `jarvis_dft_columns()` - Get available property columns
- `materials_project_query(formula, page_limit, page_offset, fields)` - Query Materials Project

### ML Prediction Methods

- `alignn_predict(jid, poscar, file_path)` - Property predictions
- `alignn_ff_energy(poscar, file_path)` - Energy & forces
- `alignn_ff_relax(poscar, file_path, fmax, steps)` - Structure relaxation
- `slakonet_bandstructure(jid, poscar, file_path, energy_range_min, energy_range_max)` - Band structure

### Analysis Methods

- `xrd_analyze(formula, pattern, wavelength, method)` - XRD pattern matching
- `diffractgpt_predict(formula, peaks, max_new_tokens)` - Structure from XRD
- `protein_fold(sequence)` - Protein structure prediction
- `weather(location, units)` - Weather data

### Structure Manipulation Methods

- `jarvis_atoms_query(jid, poscar, cif, supercell, get_primitive, get_conventional, vacancy_atom, substitution_atom, neighbors_cutoff, surface_index, properties, output_format)` - Universal structure tool

### Literature Search Methods

- `arxiv_search(query, max_results)` - Search arXiv
- `crossref_search(query, rows)` - Search CrossRef

### Utility Methods

- `health_check()` - Check API status
- `__repr__()` - String representation
- `__enter__()` / `__exit__()` - Context manager support

## Testing

```bash
# Run all tests
pytest agapi/tests/

# Run specific test file
pytest agapi/tests/test_agapi_client.py -v

# Run with coverage
pytest agapi/tests/ --cov=agapi --cov-report=html

# Skip slow tests
pytest agapi/tests/ -m "not slow"
```

## Environment Variables

```bash
# API Configuration
export AGAPI_API_KEY="sk-your-api-key-here"
export AGAPI_BASE_URL="https://atomgpt.org"  # Optional, default shown

# Agent Configuration (for AI agent)
export ATOMGPT_API_KEY="sk-your-api-key-here"  # Alternative name
```

## Requirements

- Python 3.8+
- requests >= 2.28.0
- openai >= 1.0.0 (for AI agent)
- nest-asyncio (for Jupyter support)

## Troubleshooting

### API Key Issues

```python
# Check if API key is set
import os
print(os.environ.get('AGAPI_API_KEY'))

# Test authentication
client = Agapi(api_key="sk-your-key")
health = client.health_check()
print(health)  # Should show "healthy"
```

### Timeout Errors

```python
# Increase timeout for slow operations
client = Agapi(api_key="sk-your-key", timeout=300)  # 5 minutes
```

### Network Issues

```python
# Enable verbose logging
import logging
logging.basicConfig(level=logging.DEBUG)

client = Agapi(api_key="sk-your-key", verbose=True)
```

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Citation

If you use AGAPI in your research, please cite:

```bibtex
@article{atomgpt2024,
  title={AtomGPT: Atomistic Generative Pretrained Transformer for Forward and Inverse Materials Design},
  author={Choudhary, Kamal and DeCost, Brian and Tavazza, Francesca},
  journal={arXiv preprint arXiv:2401.xxxxx},
  year={2024}
}
```

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Links

- 🌐 **Website**: [https://atomgpt.org](https://atomgpt.org)
- 📚 **Documentation**: [https://atomgpt.org/docs](https://atomgpt.org/docs)
- 💬 **Discord**: [Join our community](https://discord.gg/atomgpt)
- 🐛 **Issues**: [GitHub Issues](https://github.com/usnistgov/atomgpt/issues)
- 📧 **Contact**: kamal.choudhary@nist.gov

## Acknowledgments

- Built by the [JARVIS-Tools](https://jarvis-tools.readthedocs.io/) team at NIST
- Powered by [ALIGNN](https://github.com/usnistgov/alignn) and [DGL](https://www.dgl.ai/)
- Database: [JARVIS-DFT](https://jarvis.nist.gov/)

---

**Note**: This is research software. While we strive for accuracy, predictions should be validated experimentally for critical applications.
