# 🌐 AtomGPT.org API (AGAPI)

AGAPI provides a simple way to interact with [AtomGPT.org](https://atomgpt.org/), enabling **Agentic AI materials science research** through intuitive APIs.

A significant amount of time in computational materials design is often spent on software installation and setup — a major barrier for newcomers.  

**AGAPI removes this hurdle** by offering APIs for prediction, analysis, and exploration directly through natural language or Python interfaces, lowering entry barriers and accelerating research.

---

## 📖 Table of Contents

- [URL based query Examples](#urls)
- [🧠 Capabilities & Example Prompts](#-capabilities--example-prompts)
  - [1️⃣ Access Materials Databases](#1️⃣-access-materials-databases)
  - [2️⃣ Graph Neural Network Property Prediction](#2️⃣-graph-neural-network-property-prediction-alignn)
  - [3️⃣ Graph Neural Network Force Field](#3️⃣-graph-neural-network-force-field-alignn-ff)
  - [4️⃣ X-ray Diffraction → Atomic Structure](#4️⃣-x-ray-diffraction--atomic-structure)
  - [5️⃣ Live arXiv Search](#5️⃣-live-arxiv-search)
  - [6️⃣ Web Search](#6️⃣-web-search)
  - [7️⃣ Visualize Atomic Structures](#7️⃣-visualize-atomic-structures)
  - [8️⃣ General Question Answering](#8️⃣-general-question-answering)
  - [9️⃣ Structure Manipulation](#9️⃣-structure-manipulation)
  - [🔟 Voice Chat Interaction](#🔟-voice-chat-interaction)
- [🚀 Quickstart](#-quickstart)
  - [Colab Notebook](#colab-notebook)
  - [Python SDK](#python-sdk)
- [🎥 YouTube Demos](#-youtube-demos)
- [📚 References](#-references)
- [❤️ Note](#️-note)

---



## URL based queries  
*Replace `sk-XYZ` with your API key from atomgpt.org account settings.*  

| #  | URL | Description |
|----|-----|-------------|
| 1 | `https://atomgpt.org/jarvis_dft/query?elements=Si,C&APIKEY=sk-XYZ` | Find all entries that contain the elements Si or C. |
| 2 | `https://atomgpt.org/jarvis_dft/query?formula=Al2O3&APIKEY=sk-XYZ` | Query JARVIS-DFT for Al₂O₃. |
| 3 | `https://atomgpt.org/jarvis_dft/query?APIKEY=sk-XYZ&propranges={n-Seebeck:{min:-200},p-Seebeck:{min:400},avg_elec_mass:{min:0.2,max:0.8}}` | Query by Seebeck coefficient and effective-mass ranges. |
| 4 | `https://atomgpt.org/jarvis_dft/query?APIKEY=sk-XYZ&propranges={mbj_bandgap:{min:2},epsx:{min:10},bulk_modulus_kv:{min:50},ehull:{max:0.2}}` | Select materials by band gap, dielectric response, bulk modulus, and hull energy. |
| 5 | `https://atomgpt.org/mp/query?formula=Al2O3&APIKEY=sk-XYZ` | Query Materials Project for Al₂O₃. |
| 6 | `https://atomgpt.org/oqmd/query?formula=Al2O3&APIKEY=sk-XYZ` | Query OQMD for Al₂O₃. |
| 7 | `https://atomgpt.org/alignn/query?jid=JVASP-1002&APIKEY=sk-XYZ` | Retrieve ALIGNN predictions for JARVIS entry JVASP-1002. |
| 8 | `https://atomgpt.org/alignn/query?poscar=System\n1.0\n3.2631502048902807 0.0 -0.0\n0.0 3.2631502048902807 0.0\n0.0 -0.0 3.2631502048902807\nTi Au\n1 1\ndirect\n0.5 0.5 0.5 Ti\n0.0 0.0 0.0 Au\n&APIKEY=sk-XYZ` | Send a POSCAR (URL-encoded newlines) for GNN predictions. |
| 9 | `https://atomgpt.org/pxrd/query?pattern=MoS2\n10 20\n5 50\n&APIKEY=sk-XYZ` | Generate atomic structure from an X-ray diffraction pattern. Header as chemical formula, then 2 \theta vs intensity values. |
| 10 | `https://atomgpt.org/arxiv?query=MgB2&APIKEY=sk-XYZ` | Search arXiv for papers containing “MgB2”. |
| 11 | `https://atomgpt.org/crossref?query=CrMnFeCoNi&rows=100&APIKEY=sk-XYZ` | Retrieve up to 100 recent publications mentioning the CrMnFeCoNi alloy. |



## 🧠 Capabilities & Example Prompts

AGAPI supports **natural language interaction** for a wide range of materials science tasks.  
Each section below includes a prompt example and expected output.

---

## 1️⃣ Access Materials Databases

**Prompt:**  
> List materials with Ga and As in JARVIS-DFT

**Response:**  
Displays all GaAs-containing entries from the JARVIS-DFT database.

![Database example](https://github.com/atomgptlab/agapi/blob/main/agapi/images/jarvisdft.png)

---

## 2️⃣ Graph Neural Network Property Prediction (ALIGNN)

**Prompt:**  
> Predict properties of this POSCAR using ALIGNN  

(Upload a POSCAR, e.g. [example POSCAR file](https://github.com/atomgptlab/agapi/blob/main/agapi/images/POSCAR))

**Response:**  
Returns AI-predicted material properties (formation energy, bandgap, etc.).

![ALIGNN prediction](https://github.com/atomgptlab/agapi/blob/main/agapi/images/alignn_prop.png)

---

## 3️⃣ Graph Neural Network Force Field (ALIGNN-FF)

**Prompt:**  
> Optimize structure from uploaded POSCAR file using ALIGNN-FF  

(Upload a POSCAR, e.g. [example file](https://github.com/atomgptlab/agapi/blob/main/agapi/images/POSCAR))

**Response:**  
Generates optimized structure and energy data.

![ALIGNN-FF example](https://github.com/atomgptlab/agapi/blob/main/agapi/images/alignn_ff.png)

---

## 4️⃣ X-ray Diffraction → Atomic Structure

**Prompt:**  
> Convert XRD pattern to POSCAR  

(Upload an XRD file, e.g. [example XRD file](https://github.com/atomgptlab/agapi/blob/main/agapi/images/Lab6data.dat))

**Response:**  
Predicts atomic structure that best matches the uploaded diffraction pattern.

![XRD to structure](https://github.com/atomgptlab/agapi/blob/main/agapi/images/xrd_db_match.png)

---

## 5️⃣ Live arXiv Search

**Prompt:**  
> Find papers on MgB₂ in arXiv. State how many results you found and show top 10 recent papers.

**Response:**  
Summarizes and lists the latest publications from arXiv related to MgB₂.

![arXiv search example](https://github.com/atomgptlab/agapi/blob/main/agapi/images/search.png)

---

## 6️⃣ Web Search

**Prompt:**  
> Search for recent advances in 2D ferroelectric materials.

**Response:**  
Fetches and summarizes up-to-date information from web sources on the requested topic.

---

## 7️⃣ Visualize Atomic Structures

**Prompt:**  
> Visualize the crystal structure of Silicon in 3D.

**Response:**  
Generates a 3D interactive visualization of the given structure (CIF or POSCAR).

---

## 8️⃣ General Question Answering

**Prompt:**  
> Explain the difference between DFT and DFTB.

**Response:**  
Provides a concise explanation with context and examples.

---

## 9️⃣ Structure Manipulation

**Prompt:**  
> Replace oxygen atoms with sulfur in this POSCAR.

**Response:**  
Outputs a modified POSCAR file with requested atomic substitutions.

---

## 🔟 Voice Chat Interaction

**Prompt (spoken):**  
> What is the bandgap of silicon?

**Response (spoken):**  
> The bandgap of silicon is approximately 1.1 eV.

Enables **voice-based chat** for hands-free interaction with materials science tools.

**The table below lists available endpoints, the corresponding module, and description.**

| Endpoint | Module / Function | Description |
|-----------|------------------|--------------|
| `/materials/property` | **ALIGNN** | Predicts materials properties such as formation energy, bandgap, and elastic moduli directly from structure files. |
| `/materials/forcefield` | **ALIGNN-FF** | Computes energies, forces, and stresses for structure relaxation and molecular dynamics simulations with near-DFT accuracy. |
| `/materials/xrd` | **XRDStructurePrediction** | Determines atomic structures from uploaded XRD files to identify crystal structures. |
| `/literature/search` | **arXivSearchAgent** | Retrieves and summarizes recent arXiv or web publications on specified research topics. |
| `/visualization/structure` | **StructureViewer** | Generates interactive 3D visualizations of input structures and enables atomic structure editing. |
| `/database/jarvis` | **JarvisAPI** | Provides direct access to JARVIS materials data and pre-computed properties for workflow integration. |
| `/interface/voice` | **VoiceChat** | Enables voice-based chat for hands-free interaction with AGAPI. |
| `/literature/search` | **Crossref** | Accesses publication metadata and citation information through the Crossref API. |
---

## 🚀 Quickstart

### Colab Notebook
Try AGAPI instantly in Google Colab:  
👉 [AGAPI Example Notebook](https://github.com/knc6/jarvis-tools-notebooks/blob/master/jarvis-tools-notebooks/agapi_example.ipynb)

### Python SDK
For detailed SDK usage:  
👉 [agapi/README.md](https://github.com/atomgptlab/agapi/blob/main/agapi/README.md)

---

## 🎥 YouTube Demos

Watch AGAPI in action on YouTube:  
🎬 [AGAPI Demo Playlist](https://www.youtube.com/playlist?list=PLjf6vHVv7AoInTVQmfNSMs_12DBXYCcDd)

---

## 📚 References

1. [Choudhary, K. *et al.*, IMMI. 2025.](https://doi.org/10.1007/s40192-025-00410-9)  
2. [Choudhary, K. *et al.*, Comput. Mater. Sci. 2025.](https://doi.org/10.1016/j.commatsci.2025.114063)  
3. [Choudhary, K. *et al.*, J. Phys. Chem. Lett. 2024.](https://doi.org/10.1021/acs.jpclett.4c01126)

---

## ❤️ Note

> “AGAPI (ἀγάπη)” is a Greek word meaning **unconditional love**.

## DISCLAIMER

AtomGPT.org can make mistakes. Please verify important information.


We hope this API fosters **open, collaborative, and accelerated discovery** in materials science.

![Poster](https://github.com/atomgptlab/agapi/blob/main/agapi/images/atomgpt_org_poster.jpg)
