---
title: Surface Explorer
---

# Surface Explorer

Browse, search, and visualize surface properties from the JARVIS surface database (607 entries). Work functions, surface energies, and cleavage energies.

[:material-open-in-new: Open App](https://atomgpt.org/surface){ .md-button .md-button--primary }

---

## Overview

Browse, search, and visualize surface properties from the JARVIS surface database (607 entries). Work functions, surface energies, and cleavage energies.

!!! info "Data Source"
    **surfacedb (607 entries)**

## Endpoints

- `GET /surface`
- `POST /surface/search`
- `GET /surface/data/{idx}`

**Request Models:** `SurfaceSearchRequest`

!!! note "Authentication"
    All POST endpoints require `Authorization: Bearer YOUR_TOKEN`.

## API Example

```python
import requests

resp = requests.post(
    "https://atomgpt.org/surface/data/{idx}",
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
response = agent.query_sync("Show surface explorer for Silicon")
print(response)
```

## Reference

- Digital Discovery (2024)
