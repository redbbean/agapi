---
title: Spillage
---

# Spillage

Visualize and compare SOC spillage data from JARVIS-DFT for identifying topological insulators and semimetals. Data parsed from JARVIS XML.

[:material-open-in-new: Open App](https://atomgpt.org/spillage){ .md-button .md-button--primary }

---

## Overview

Visualize and compare SOC spillage data from JARVIS-DFT for identifying topological insulators and semimetals. Data parsed from JARVIS XML.

!!! info "Data Source"
    **dft_3d (JARVIS XML)**

## Endpoints

- `GET /spillage`
- `POST /spillage/search`
- `GET /spillage/data/{jid}`

**Request Models:** `SpillageSearchRequest`

!!! note "Authentication"
    All POST endpoints require `Authorization: Bearer YOUR_TOKEN`.

## API Example

```python
import requests

response = requests.post(
    "https://atomgpt.org/spillage/search",
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
response = agent.query_sync("Show spillage for Silicon")
print(response)
```

## Reference

- Sci. Rep. 9, 8534 (2019)
