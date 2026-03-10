---
title: PDB Explorer
---

# PDB Explorer

Search 200K+ protein structures from RCSB PDB. 3D Mol* viewer (RCSB embed iframe), sequence display with position markers, unit cell and crystallographic data, polymer entities. Uses RCSB REST API (no key needed).

[:material-open-in-new: Open App](https://atomgpt.org/pdb_explorer){ .md-button .md-button--primary }

---

## Overview

Search 200K+ protein structures from RCSB PDB. 3D Mol* viewer (RCSB embed iframe), sequence display with position markers, unit cell and crystallographic data, polymer entities. Uses RCSB REST API (no key needed).

!!! info "Data Source"
    **RCSB PDB REST API**

## Endpoints

- `GET /pdb_explorer`
- `POST /pdb_explorer/search`
- `GET /pdb_explorer/entry/{pdb_id}`

**Request Models:** `PDBSearchRequest`

!!! note "Authentication"
    All POST endpoints require `Authorization: Bearer YOUR_TOKEN`.

## API Example

```python
import requests

resp = requests.post(
    "https://atomgpt.org/pdb_explorer/entry/{pdb_id}",
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
response = agent.query_sync("Show pdb explorer for Silicon")
print(response)
```

## Reference

- Nucleic Acids Res. 28, 235 (2000)
