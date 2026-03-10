---
title: Dielectric Function
---

# Dielectric Function

Look up and interactively plot the MBJ dielectric function ε(ω) for any JARVIS-DFT material. Supports search by JARVIS ID, chemical formula, space group, and MBJ band gap range.

[:material-open-in-new: Open App](https://atomgpt.org/dielectric_function){ .md-button .md-button--primary }

---

## Overview

Look up and interactively plot the MBJ dielectric function ε(ω) for any JARVIS-DFT material. Supports search by JARVIS ID, chemical formula, space group, and MBJ band gap range.

!!! info "Data Source"
    **dft_3d**

## Endpoints

- `GET /dielectric_function`
- `POST /dielectric_function/search`
- `GET /dielectric_function/data/{jid}`

**Request Models:** `DielectricSearchRequest`

!!! note "Authentication"
    All POST endpoints require `Authorization: Bearer YOUR_TOKEN`.

## API Example

```python
import requests

resp = requests.post(
    "https://atomgpt.org/dielectric_function/data/{jid}",
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
response = agent.query_sync("Show dielectric function for Silicon")
print(response)
```

## Reference

- Nature Sci. Data 5, 180082 (2018)
