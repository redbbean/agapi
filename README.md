# 🌐 AtomGPT.org API (AGAPI)

AGAPI provides a simple way to interact with [AtomGPT.org](https://atomgpt.org/), enabling **Agentic AI materials science research** through intuitive APIs.

A significant amount of time in computational materials design is often spent on software installation and setup — a major barrier for newcomers.  

**AGAPI removes this hurdle** by offering APIs for prediction, analysis, and exploration directly through natural language or Python interfaces, lowering entry barriers and accelerating research.

---

## 📖 Table of Contents

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

1. [Choudhary, K. *et al.*, MRS Bull. 2025.](https://doi.org/10.1007/s40192-025-00410-9)  
2. [Choudhary, K. *et al.*, Comput. Mater. Sci. 2025.](https://doi.org/10.1016/j.commatsci.2025.114063)  
3. [Choudhary, K. *et al.*, J. Phys. Chem. Lett. 2024.](https://doi.org/10.1021/acs.jpclett.4c01126)

---

## ❤️ Note

> “AGAPI (ἀγάπη)” is a Greek word meaning **unconditional love**.

We hope this API fosters **open, collaborative, and accelerated discovery** in materials science.

![Poster](https://github.com/atomgptlab/agapi/blob/main/agapi/images/atomgpt_org_poster.jpg)
