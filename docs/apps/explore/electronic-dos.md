---
title: Electronic DOS
---

# Electronic DOS

Visualize and compare the electronic density of states from JARVIS-DFT. Spin-resolved up/down channels fetched from JARVIS XML pages.

[:material-open-in-new: Open App](https://atomgpt.org/electronic_dos){ .md-button .md-button--primary }

---

## Overview

Visualize and compare the electronic density of states from JARVIS-DFT. Spin-resolved up/down channels fetched from JARVIS XML pages.

!!! info "Data Source"
    **dft_3d (JARVIS XML)**

## Endpoints

- `GET /electronic_dos`
- `POST /electronic_dos/search`
- `GET /electronic_dos/data/{jid}`

**Request Models:** `DOSSearchRequest`

!!! note "Authentication"
    All POST endpoints require `Authorization: Bearer YOUR_TOKEN`.

## API Example

```python
import requests

resp = requests.post(
    "https://atomgpt.org/electronic_dos/data/{jid}",
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
response = agent.query_sync("Show electronic dos for Silicon")
print(response)
```

## Reference

- Comp. Mat. Sci. 259, 114063 (2025); JOM 74, 1395 (2022)
