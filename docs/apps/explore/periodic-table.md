---
title: Periodic Table
---

# Periodic Table

Interactive periodic table with JARVIS property overlays. Backend provides per-element property statistics aggregated from JARVIS-DFT 3D (76K materials). Fully client-side visualization.

[:material-open-in-new: Open App](https://atomgpt.org/periodic_table){ .md-button .md-button--primary }

---

## Overview

Interactive periodic table with JARVIS property overlays. Backend provides per-element property statistics aggregated from JARVIS-DFT 3D (76K materials). Fully client-side visualization.

!!! info "Data Source"
    **dft_3d (aggregated per-element stats)**

## Endpoints

- `GET /periodic_table`
- `GET /periodic_table/stats`

**Request Models:** —

!!! note "Authentication"
    All POST endpoints require `Authorization: Bearer YOUR_TOKEN`.

## API Example

```python
import requests

response = requests.get(
    "https://atomgpt.org/periodic_table/stats",
    headers={
        "Authorization": "Bearer sk-XYZ",
        "accept": "application/json",
    },
)
data = response.json()
print(data)
```

## AGAPI Agent

```python
from agapi.agents import AGAPIAgent
import os

agent = AGAPIAgent(api_key=os.environ.get("AGAPI_KEY"))
response = agent.query_sync("Show periodic table for Silicon")
print(response)
```

## Reference

- Comp. Mat. Sci. 259, 114063 (2025)
