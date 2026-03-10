---
title: Polymer Explorer
---

# Polymer Explorer

Browse, search, and visualize crystalline polymer properties by cross-referencing Polymer Genome database (1073 entries) with JARVIS-DFT. Dielectrics, band gaps, formation energies.

[:material-open-in-new: Open App](https://atomgpt.org/polymer){ .md-button .md-button--primary }

---

## Overview

Browse, search, and visualize crystalline polymer properties by cross-referencing Polymer Genome database (1073 entries) with JARVIS-DFT. Dielectrics, band gaps, formation energies.

!!! info "Data Source"
    **polymer_genome (1073 entries) + dft_3d**

## Endpoints

- `GET /polymer`
- `POST /polymer/search`
- `GET /polymer/data/{jid}`

**Request Models:** `PolymerSearchRequest`

!!! note "Authentication"
    All POST endpoints require `Authorization: Bearer YOUR_TOKEN`.

## API Example

```python
import requests

resp = requests.post(
    "https://atomgpt.org/polymer/data/{jid}",
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
response = agent.query_sync("Show polymer explorer for Silicon")
print(response)
```

## Reference

- Sci. Data 3, 160012 (2016)
