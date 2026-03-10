---
title: Force Field DB
---

# Force Field DB

JARVIS Force-Field (FF) database search. Search by elements, JID, formula, crystal system, or force-field type (EAM, Tersoff, ReaxFF, etc.).

[:material-open-in-new: Open App](https://atomgpt.org/ff){ .md-button .md-button--primary }

---

## Overview

JARVIS Force-Field (FF) database search. Search by elements, JID, formula, crystal system, or force-field type (EAM, Tersoff, ReaxFF, etc.).

!!! info "Data Source"
    **JARVIS-FF**

## Endpoints

- `GET /ff`
- `POST /ff/search`

**Request Models:** `FFSearchRequest`

!!! note "Authentication"
    All POST endpoints require `Authorization: Bearer YOUR_TOKEN`.

## API Example

```python
import requests

response = requests.post(
    "https://atomgpt.org/ff/search",
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
response = agent.query_sync("Show force field db for Silicon")
print(response)
```

## Reference

- J. Phys. Cond. Matt. 30, 395901 (2018)
