# AtomGPT.org API (AGAPI)


AGAPI provides examples of how to interact with https://atomgpt.org/


A significant amount of time in computational materials design is often spent on software installation, which creates a major barrier for newcomers to the field. AGAPI removes this layer by providing APIs that can be used directly for prediction and analysis, thereby lowering entry barriers and accelerating research.


# Python SDK examples:

agapi/README.md 



# Prompt Examples

## 1. Access to Materials Databases

Prompt: List materials with Ga and As in JARVIS-DFT

Response: <img  alt="database" src="https://github.com/atomgptlab/agapi/blob/main/agapi/images/jarvisdft.png" />

## 2. Graph Neural Network Predictions

Prompt: Predict properties of this POSCAR using ALIGNN
(Upload a POSCAR e.g. [this file](https://github.com/atomgptlab/agapi/blob/main/agapi/images/POSCAR))

Response: <img  alt="database" src="https://github.com/atomgptlab/agapi/blob/main/agapi/images/alignn_prop.png" />


## 3. Graph Neural Network Force-field 

Optimize structure from uploaded POSCAR file using ALIGNN-FF
(Upload a POSCAR e.g. [this file](https://github.com/atomgptlab/agapi/blob/main/agapi/images/POSCAR))

Response: <img  alt="database" src="https://github.com/atomgptlab/agapi/blob/main/agapi/images/alignn_ff.png" />

## 4. X-ray diffraction to atomic structure

Prompt: Convert XRD pattern to POSCAR
(Upload a XRD file e.g. [this file](https://github.com/atomgptlab/agapi/blob/main/agapi/images/Lab6data.dat))

Response: <img  alt="database" src="https://github.com/atomgptlab/agapi/blob/main/agapi/images/xrd_db_match.png" />


## 5. Live arXiv search

Prompt: Find papers on MgB2 in arXiv. State how many results did you find and show top 10 recent papers only.

Response: <img  alt="database" src="https://github.com/atomgptlab/agapi/blob/main/agapi/images/search.png" />


# References:

1. https://doi.org/10.1007/s40192-025-00410-9
2. https://doi.org/10.1016/j.commatsci.2025.114063
3. https://doi.org/10.1021/acs.jpclett.4c01126

Note: AGAPI (ἀγάπη) in Greek means unconditional love.

<img  alt="database" src="https://github.com/atomgptlab/agapi/blob/main/agapi/images/atomgpt_org_poster.jpg" />
