# 🌐 AtomGPT.org API (AGAPI) - Agentic AI for Materials Science

Empower your materials science research with AtomGPT's Agentic AI API. AGAPI removes complex software setups, commercial API cost allowing you to perform advanced predictions, analyses, and explorations through natural language or Python, accelerating materials discovery and design.

## 🚀 Quickstart

### 1. Obtain Your API Key
Sign up at [AtomGPT.org](https://atomgpt.org/) and navigate to your `Account -> Settings` to get your `AGAPI_KEY`.
```bash
export AGAPI_KEY="sk-your-key-here"
```

### 2. Install the SDK
```bash
pip install agapi
```
### 3. Start with Google Colab Notebook
[![Open in Google Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/knc6/jarvis-tools-notebooks/blob/master/jarvis-tools-notebooks/agapi_example.ipynb)



---

## ✨ Key Capabilities

AGAPI provides a unified interface to powerful materials science tools:

### 1. **Materials Database Query**
Access JARVIS-DFT and other databases to find structures, properties, and more.

```python
import os
from agapi.agents.client import AGAPIClient
from agapi.agents import AGAPIAgent
from jarvis.io.vasp.inputs import Poscar
# API-Client
client = AGAPIClient(api_key=os.environ.get("AGAPI_KEY"))
# AI Agent
agent = AGAPIAgent(api_key=os.environ.get("AGAPI_KEY"))
from agapi.agents.functions import query_by_formula
result = query_by_formula("Si", client)
print(result["materials"][25]["formula"], result["materials"][25]["mbj_bandgap"])
# Expected: Si 1.27
```
**Natural Language Example:** `agent.query_sync("What are the bandgaps of Si and GaAs?", verbose=True)`

### 2. **AI Property Prediction (ALIGNN)**
Predict material properties like bandgap, formation energy, and elastic moduli using state-of-the-art Graph Neural Networks.

```python
from agapi.agents.functions import alignn_predict
result = alignn_predict(jid="JVASP-1002", api_client=client)
print(f"Formation Energy: {result.get('formation_energy')[0]:.2f} eV/atom")
# Expected: Formation Energy: 0.0 eV/atom
```
**Natural Language Example:** `agent.query_sync("Predict properties for JVASP-1002 using ALIGNN.", verbose=True)`

### 3. **AI Force Field (ALIGNN-FF)**
Perform structure optimization, molecular dynamics, and single-point energy calculations with near-DFT accuracy.

```python
from agapi.agents.functions import alignn_ff_relax
SI_PRIM = """Si\n1.0\n0 2.734 2.734\n2.734 0 2.734\n2.734 2.734 0\nSi\n2\ndirect\n0 0 0\n0.25 0.25 0.25"""
result = alignn_ff_relax(SI_PRIM, api_client=client)
if result.get("status") == "success":
    print("Structure relaxed successfully.")
print(Poscar.from_string(result['relaxed_poscar']))
# Expected: Structure relaxed successfully.
```
**Natural Language Example:** `agent.query_sync(f"Optimize this Si primitive cell POSCAR using ALIGNN-FF:\n\n{SI_PRIM}", verbose=True)`

### 4. **XRD to Atomic Structure**
Predict atomic structures from PXRD patterns, identify phases, and analyze experimental data.

```python
from agapi.agents.functions import pxrd_match
SI_XRD = """28.44 1.00\n47.30 0.55\n56.12 0.30"""
result = pxrd_match("Si", SI_XRD, api_client=client)
if "matched_poscar" in result:
    print("Matched POSCAR found for Si.")
    print(Poscar.from_string(result['matched_poscar']))
# Expected: Matched POSCAR found for Si.
```
**Natural Language Example:** `agent.query_sync(f"Analyze this XRD pattern for Silicon:\n\n{SI_XRD}", verbose=True)`

### 5. **Structure Manipulation**
Perform common crystallographic operations like supercell generation, atom substitution, and vacancy creation (local execution).

```python
from agapi.agents.functions import make_supercell
# SI_PRIM defined above
result = make_supercell(SI_PRIM, [2, 1, 1])
print(f"Original atoms: {result['original_atoms']}, Supercell atoms: {result['supercell_atoms']}")
# Expected: Original atoms: 2, Supercell atoms: 4
```
**Natural Language Example:** `agent.query_sync("Create a 2x2x1 supercell for the most stable GaN structure.", verbose=True)`

### 6. **Literature Search**
Search arXiv and Crossref for relevant research papers and publication metadata.

```python
from agapi.agents.functions import search_arxiv
result = search_arxiv("MgB2", max_results=1, api_client=client)
if result.get("results"):
    print(f"Found paper: {result['results'][0]['title']}")
# Expected: Found paper: Lumped-Element Model of THz HEB Mixer Based on Sputtered MgB2 Thin Film
```
**Natural Language Example:** `agent.query_sync("Find recent papers on MgB2 on arXiv", verbose=True)`

---


---

## 📖 References

If you find this work helpful, please consider citing:

1. **AGAPI-Agents: An Open-Access Agentic AI Platform for Accelerated Materials Design on AtomGPT.org**  
   https://doi.org/10.48550/arXiv.2512.11935

2. **ChatGPT Material Explorer: Design and Implementation of a Custom GPT Assistant for Materials Science Applications**  
   https://doi.org/10.1016/j.commatsci.2025.114063

3. **The JARVIS Infrastructure Is All You Need for Materials Design**  
   https://doi.org/10.1016/j.commatsci.2025.114063

*   **Full Publication List:** [Google Scholar](https://scholar.google.com/citations?hl=en&user=YVP36YgAAAAJ&view_op=list_works&authuser=4&sortby=pubdate)
---



## 📚 More Resources

*   **Choudhary Research Group:** [AtomGPTLab](https://choudhary.wse.jhu.edu/)
*   **API Documentation:** [AtomGPT.org/docs](https://atomgpt.org/docs)
*   **Colab Notebook:** Experiment instantly with the [AGAPI Example Notebook](https://github.com/knc6/jarvis-tools-notebooks/blob/master/jarvis-tools-notebooks/agapi_example.ipynb).
*   **YouTube Demos:** See AGAPI in action on our [Demo Playlist](https://www.youtube.com/playlist?list=PLjf6vHVv7AoInTVQmfNSMs_12DBXYCcDd).
---

## ❤️ Note & Disclaimer

> “AGAPI (ἀγάπη)” is a Greek word meaning **unconditional love**.


> AtomGPT.org can make mistakes. Please verify important information. We hope this API fosters **open, collaborative, and accelerated discovery** in materials science.

---

