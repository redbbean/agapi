---
title: XRD / DiffractGPT
---

# XRD / DiffractGPT

XRD analysis suite: simulate powder XRD patterns from crystal structures, match experimental data to JARVIS-DFT, Rietveld-style refinement, AI-powered peak identification via DiffractGPT, POSCAR to XYZ conversion.

[:material-open-in-new: Open App](https://atomgpt.org/xrd){ .md-button .md-button--primary }

---

## Overview

XRD analysis suite: simulate powder XRD patterns from crystal structures, match experimental data to JARVIS-DFT, Rietveld-style refinement, AI-powered peak identification via DiffractGPT, POSCAR to XYZ conversion.

!!! info "Data Source"
    **dft_3d + DiffractGPT model**

## Endpoints

- `GET /xrd`
- `POST /xrd/query`
- `GET /pxrd/query`
- `GET /xrd/analyze`
- `POST /xrd/analyze`
- `POST /xrd/analyze_with_refinement`
- `GET /diffractgpt/query`
- `POST /xrd/poscar_to_xyz`
- `POST /xrd/generate`

**Request Models:** `XRDAnalysisRequest`, `XRDRefinementRequest`, `XRDGenerateRequest`

!!! note "Authentication"
    All POST endpoints require `Authorization: Bearer YOUR_TOKEN`.

## API Example

```python
import requests

resp = requests.post(
    "https://atomgpt.org/xrd/generate",
    headers={"Authorization": "Bearer YOUR_TOKEN"},
    json={"jid": "JVASP-1002"}
)
print(resp.json())
```

## AGAPI Agent

```python
from agapi.agents import AGAPIAgent
import os

agent = AGAPIAgent(api_key=os.environ.get("AGAPI_KEY"))
response = agent.query_sync("Show xrd / diffractgpt for Silicon")
print(response)
```

## Reference

- J. Phys. Chem. Lett. 16, 2110 (2025)
