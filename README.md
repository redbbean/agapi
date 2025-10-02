# AtomGPT.org API (AGAPI)

AGAPI provides a simple way to interact with [AtomGPT.org](https://atomgpt.org/), enabling **AI-powered materials science research** through easy-to-use APIs.  

A significant amount of time in computational materials design is often spent on **software installation and setup**, which can be a major barrier for newcomers.  
AGAPI removes this hurdle by offering APIs that can be accessed directly for **prediction, analysis, and exploration**, thereby lowering entry barriers and accelerating research.

---

## 🚀 Quickstart

### Colab Notebook  
Try AGAPI instantly in Google Colab:  
👉 [AGAPI Example Notebook](https://github.com/knc6/jarvis-tools-notebooks/blob/master/jarvis-tools-notebooks/agapi_example.ipynb)

### Python SDK  
See more detailed usage in the SDK guide:  
👉 [agapi/README.md](https://github.com/atomgptlab/agapi/blob/main/agapi/README.md)

---

## 🎥 YouTube Demos
Watch AGAPI in action:  
[YouTube Playlist](https://www.youtube.com/playlist?list=PLjf6vHVv7AoInTVQmfNSMs_12DBXYCcDd)

---

## 💡 Example Prompts & Responses

AGAPI supports natural language prompts for a wide range of materials science tasks.  

### 1. Access Materials Databases
**Prompt:**  
`List materials with Ga and As in JARVIS-DFT`

**Response:**  
<img alt="database" src="https://github.com/atomgptlab/agapi/blob/main/agapi/images/jarvisdft.png" />

---

### 2. Graph Neural Network Property Prediction  
**Prompt:**  
`Predict properties of this POSCAR using ALIGNN`  
(Upload a POSCAR, e.g. [this file](https://github.com/atomgptlab/agapi/blob/main/agapi/images/POSCAR))

**Response:**  
<img alt="alignn prediction" src="https://github.com/atomgptlab/agapi/blob/main/agapi/images/alignn_prop.png" />

---

### 3. Graph Neural Network Force-Field (ALIGNN-FF)  
**Prompt:**  
`Optimize structure from uploaded POSCAR file using ALIGNN-FF`  
(Upload a POSCAR, e.g. [this file](https://github.com/atomgptlab/agapi/blob/main/agapi/images/POSCAR))

**Response:**  
<img alt="alignn ff" src="https://github.com/atomgptlab/agapi/blob/main/agapi/images/alignn_ff.png" />

---

### 4. X-ray Diffraction → Atomic Structure  
**Prompt:**  
`Convert XRD pattern to POSCAR`  
(Upload an XRD file, e.g. [this file](https://github.com/atomgptlab/agapi/blob/main/agapi/images/Lab6data.dat))

**Response:**  
<img alt="xrd structure" src="https://github.com/atomgptlab/agapi/blob/main/agapi/images/xrd_db_match.png" />

---

### 5. Live arXiv Search  
**Prompt:**  
`Find papers on MgB2 in arXiv. State how many results you found and show top 10 recent papers.`

**Response:**  
<img alt="search results" src="https://github.com/atomgptlab/agapi/blob/main/agapi/images/search.png" />

---

## 📚 References
1. [10.1007/s40192-025-00410-9](https://doi.org/10.1007/s40192-025-00410-9)  
2. [10.1016/j.commatsci.2025.114063](https://doi.org/10.1016/j.commatsci.2025.114063)  
3. [10.1021/acs.jpclett.4c01126](https://doi.org/10.1021/acs.jpclett.4c01126)

---

## ❤️ Note
**AGAPI (ἀγάπη)** is a Greek word meaning *unconditional love*.  
We hope this API helps foster open, collaborative, and accelerated discovery in materials science.

<img alt="poster" src="https://github.com/atomgptlab/agapi/blob/main/agapi/images/atomgpt_org_poster.jpg" />
