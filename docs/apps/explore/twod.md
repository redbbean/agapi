---
title: 2D Materials
---

# 2D Materials

Browse, search, and visualize properties of 2D materials from the JARVIS-DFT 2D dataset (~1.1K monolayers). Exfoliation energies, band gaps, magnetic properties.

[:material-open-in-new: Open App](https://atomgpt.org/twod){ .md-button .md-button--primary }

---

## Overview

Browse, search, and visualize properties of 2D materials from the JARVIS-DFT 2D dataset (~1.1K monolayers). Exfoliation energies, band gaps, magnetic properties.

!!! info "Data Source"
    **dft_2d (~1.1K entries)**

## Endpoints

- `GET /twod`
- `POST /twod/search`
- `GET /twod/data/{jid}`

**Request Models:** `TwoDSearchRequest`

!!! note "Authentication"
    All POST endpoints require `Authorization: Bearer YOUR_TOKEN`.

## API Example

```python
import requests

resp = requests.post(
    "https://atomgpt.org/twod/data/{jid}",
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
response = agent.query_sync("Show 2d materials for Silicon")
print(response)
```

## Reference

- Sci. Rep. 7, 5179 (2017)
