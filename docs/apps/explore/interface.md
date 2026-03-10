---
title: Interface Explorer
---

# Interface Explorer

Browse, search, and visualize heterostructure interface properties from the JARVIS interface database (607 entries). Band alignments and interface energies.

[:material-open-in-new: Open App](https://atomgpt.org/interface_db){ .md-button .md-button--primary }

---

## Overview

Browse, search, and visualize heterostructure interface properties from the JARVIS interface database (607 entries). Band alignments and interface energies.

!!! info "Data Source"
    **interfacedb (607 entries)**

## Endpoints

- `GET /interface_db`
- `POST /interface/search`
- `GET /interface/data/{idx}`

**Request Models:** `InterfaceSearchRequest`

!!! note "Authentication"
    All POST endpoints require `Authorization: Bearer YOUR_TOKEN`.

## API Example

```python
import requests

resp = requests.post(
    "https://atomgpt.org/interface/data/{idx}",
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
response = agent.query_sync("Show interface explorer for Silicon")
print(response)
```

## Reference

- Phys. Rev. Mat. 7, 014009 (2023)
