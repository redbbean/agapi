---
title: OPTIMADE Explorer
---

# OPTIMADE Explorer

Query JARVIS-DFT using OPTIMADE-style filters served directly from the dft_3d dataset (no external API calls). Supports elements HAS ANY/ALL/ONLY, formula, nelements, nsites, and numeric property filters.

[:material-open-in-new: Open App](https://atomgpt.org/optimade_explorer){ .md-button .md-button--primary }

---

## Overview

Query JARVIS-DFT using OPTIMADE-style filters served directly from the dft_3d dataset (no external API calls). Supports elements HAS ANY/ALL/ONLY, formula, nelements, nsites, and numeric property filters.

!!! info "Data Source"
    **dft_3d (in-memory OPTIMADE filter engine)**

## Endpoints

- `GET /optimade_explorer`
- `POST /optimade_explorer/query`
- `GET /optimade_explorer/entry/{jid}`

**Request Models:** `OptimadeQueryRequest`

!!! note "Authentication"
    All POST endpoints require `Authorization: Bearer YOUR_TOKEN`.

## API Example

```python
import requests

response = requests.post(
    "https://atomgpt.org/optimade_explorer/query",
    headers={
        "Authorization": "Bearer sk-XYZ",
        "accept": "application/json",
        "Content-Type": "application/json",
    },
    json={"jid": "JVASP-1002"},
)
data = response.json()
print(data)
```

## AGAPI Agent

```python
from agapi.agents import AGAPIAgent
import os

agent = AGAPIAgent(api_key=os.environ.get("AGAPI_KEY"))
response = agent.query_sync("Show optimade explorer for Silicon")
print(response)
```

## Reference

- NPJ Comp. Mat. 6, 173 (2020)
