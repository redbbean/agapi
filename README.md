# 🌐 AtomGPT.org API (AGAPI) - Agentic AI for Materials Science

[![Open in Google Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/knc6/jarvis-tools-notebooks/blob/master/jarvis-tools-notebooks/agapi_example.ipynb)

Empower your materials science research with AtomGPT's Agentic AI API. AGAPI removes complex software setups, allowing you to perform advanced predictions, analyses, and explorations through natural language or Python, accelerating discovery.

---

## ✨ Key Capabilities

AGAPI provides a unified interface to powerful materials science tools:

### 1. **Materials Database Query**
Access JARVIS-DFT, OQMD, and Materials Project databases to find structures, properties, and more.

```python
from agapi.agents.functions import query_by_formula
from agapi.agents.client import AGAPIClient
import os

client = AGAPIClient(api_key=os.environ.get("AGAPI_KEY"))
result = query_by_formula("Si", client)
print(result["materials"][0]["formula"], result["materials"][0]["bandgap"])
# Expected: Si 1.12
```
**Natural Language Example:** `agent.query_sync("What are the bandgaps of Si and GaAs?")`

### 2. **AI Property Prediction (ALIGNN)**
Predict material properties like bandgap, formation energy, and elastic moduli using state-of-the-art Graph Neural Networks.

```python
from agapi.agents.functions import alignn_predict
# ... client setup ...

result = alignn_predict(jid="JVASP-1002", api_client=client)
print(f"Formation Energy: {result.get('formation_energy'):.2f} eV/atom")
# Expected: Formation Energy: -0.11 eV/atom
```
**Natural Language Example:** `agent.query_sync("Predict properties for JVASP-1002 using ALIGNN.")`

### 3. **AI Force Field (ALIGNN-FF)**
Perform structure optimization, molecular dynamics, and single-point energy calculations with near-DFT accuracy.

```python
from agapi.agents.functions import alignn_ff_relax
# ... client setup ...

SI_PRIM = """Si\n1.0\n0 2.734 2.734\n2.734 0 2.734\n2.734 2.734 0\nSi\n2\ndirect\n0 0 0\n0.25 0.25 0.25"""
result = alignn_ff_relax(SI_PRIM, api_client=client)
if result.get("status") == "success":
    print("Structure relaxed successfully.")
# Expected: Structure relaxed successfully.
```
**Natural Language Example:** `agent.query_sync("Optimize this Si primitive cell POSCAR using ALIGNN-FF: [POSCAR string]")`

### 4. **XRD to Atomic Structure**
Predict atomic structures from PXRD patterns, identify phases, and analyze experimental data.

```python
from agapi.agents.functions import pxrd_match
# ... client setup ...

SI_XRD = """28.44 1.00\n47.30 0.55\n56.12 0.30"""
result = pxrd_match("Si", SI_XRD, api_client=client)
if "matched_poscar" in result:
    print("Matched POSCAR found for Si.")
# Expected: Matched POSCAR found for Si.
```
**Natural Language Example:** `agent.query_sync("Analyze this XRD pattern for Silicon: [XRD data]")`

### 5. **Structure Manipulation**
Perform common crystallographic operations like supercell generation, atom substitution, and vacancy creation (local execution).

```python
from agapi.agents.functions import make_supercell
# SI_PRIM defined above

result = make_supercell(SI_PRIM, [2, 1, 1])
print(f"Original atoms: {result['original_atoms']}, Supercell atoms: {result['supercell_atoms']}")
# Expected: Original atoms: 2, Supercell atoms: 4
```
**Natural Language Example:** `agent.query_sync("Create a 2x2x1 supercell for the most stable GaN structure.")`

### 6. **Literature Search**
Search arXiv and Crossref for relevant research papers and publication metadata.

```python
from agapi.agents.functions import search_arxiv
# ... client setup ...

result = search_arxiv("graphene properties", max_results=1, api_client=client)
if result.get("results"):
    print(f"Found paper: {result['results'][0]['title']}")
# Expected: Found paper: ... (A relevant graphene paper title)
```
**Natural Language Example:** `agent.query_sync("Find recent papers on perovskite solar cells on arXiv.")`

---

## 🚀 Quickstart

### 1. Obtain Your API Key
Sign up at [AtomGPT.org](https://atomgpt.org/) and navigate to your `Account -> Settings` to get your `AGAPI_KEY`.

### 2. Install the SDK
```bash
pip install agapi jarvis-tools scipy httpx
```

### 3. Use the Python SDK
Set your API key as an environment variable or pass it directly.

```python
import os
from agapi.agents import AGAPIAgent

# Option 1: Set environment variable (recommended)
# export AGAPI_KEY="sk-your-key-here"

# Option 2: Pass directly (less secure for production)
# api_key = "sk-your-key-here" 
# agent = AGAPIAgent(api_key=api_key)

agent = AGAPIAgent(api_key=os.environ.get("AGAPI_KEY"))

# Natural Language Query
response = agent.query_sync("What is the bandgap of Silicon?")
print(response)

# Tool-specific function call (using the client directly)
from agapi.agents.client import AGAPIClient
from agapi.agents.functions import query_by_jid

client = AGAPIClient(api_key=os.environ.get("AGAPI_KEY"))
result = query_by_jid("JVASP-1002", client)
print(result["formula"])
```

---

## 📚 More Resources

*   **API Documentation:** [AtomGPT.org/docs](https://atomgpt.org/docs)
*   **Colab Notebook:** Experiment instantly with the [AGAPI Example Notebook](https://github.com/knc6/jarvis-tools-notebooks/blob/master/jarvis-tools-notebooks/agapi_example.ipynb).
*   **YouTube Demos:** See AGAPI in action on our [Demo Playlist](https://www.youtube.com/playlist?list=PLjf6vHVv7AoInTVQmfNSMs_12DBXYCcDd).
*   **Full Publication List:** [Google Scholar](https://scholar.google.com/citations?hl=en&user=klhV2BIAAAAJ&view_op=list_works&sortby=pubdate)

---

## ❤️ Note & Disclaimer

> “AGAPI (ἀγάπη)” is a Greek word meaning **unconditional love**.
>
> AtomGPT.org can make mistakes. Please verify important information. We hope this API fosters **open, collaborative, and accelerated discovery** in materials science.

---
```
