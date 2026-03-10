---
title: EFG
---

# EFG

Visualize and compare electric field gradient (EFG) tensors from JARVIS-DFT for NMR/NQR applications. Vzz, asymmetry parameter η, quadrupole coupling constants parsed from JARVIS XML.

[:material-open-in-new: Open App](https://atomgpt.org/efg){ .md-button .md-button--primary }

---

## Overview

Visualize and compare electric field gradient (EFG) tensors from JARVIS-DFT for NMR/NQR applications. Vzz, asymmetry parameter η, quadrupole coupling constants parsed from JARVIS XML.

!!! info "Data Source"
    **dft_3d (JARVIS XML)**

## Endpoints

- `GET /efg`
- `POST /efg/search`
- `GET /efg/data/{jid}`

**Request Models:** `EFGSearchRequest`

!!! note "Authentication"
    All POST endpoints require `Authorization: Bearer YOUR_TOKEN`.

## API Example

```python
import requests

resp = requests.post(
    "https://atomgpt.org/efg/data/{jid}",
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
response = agent.query_sync("Show efg for Silicon")
print(response)
```

## Reference

- Nature Sci. Data 7, 362 (2020)
