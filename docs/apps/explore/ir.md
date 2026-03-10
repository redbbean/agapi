---
title: IR Spectra
---

# IR Spectra

Visualize and compare infrared spectra from JARVIS-DFT DFPT calculations. Born effective charges and phonon frequencies parsed from JARVIS XML.

[:material-open-in-new: Open App](https://atomgpt.org/ir){ .md-button .md-button--primary }

---

## Overview

Visualize and compare infrared spectra from JARVIS-DFT DFPT calculations. Born effective charges and phonon frequencies parsed from JARVIS XML.

!!! info "Data Source"
    **dft_3d (DFPT, JARVIS XML)**

## Endpoints

- `GET /ir`
- `POST /ir/search`
- `GET /ir/data/{jid}`

**Request Models:** `IRSearchRequest`

!!! note "Authentication"
    All POST endpoints require `Authorization: Bearer YOUR_TOKEN`.

## API Example

```python
import requests

resp = requests.post(
    "https://atomgpt.org/ir/data/{jid}",
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
response = agent.query_sync("Show ir spectra for Silicon")
print(response)
```

## Reference

- NPJ Comp. Mat. 6, 1 (2020)
