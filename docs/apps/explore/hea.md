---
title: HEA Explorer
---

# HEA Explorer

High-Entropy Alloy design tool. Compute thermodynamic parameters (ΔS_mix, δ, VEC, Ω), predict phases (FCC/BCC/mixed), Hume-Rothery checks, and screen JARVIS-DFT for matching compositions.

[:material-open-in-new: Open App](https://atomgpt.org/hea){ .md-button .md-button--primary }

---

## Overview

High-Entropy Alloy design tool. Compute thermodynamic parameters (ΔS_mix, δ, VEC, Ω), predict phases (FCC/BCC/mixed), Hume-Rothery checks, and screen JARVIS-DFT for matching compositions.

!!! info "Data Source"
    **dft_3d + built-in element property database**

## Endpoints

- `GET /hea`
- `POST /hea/compute`
- `POST /hea/screen`

**Request Models:** `HEAComputeRequest`, `HEAScreenRequest`

!!! note "Authentication"
    All POST endpoints require `Authorization: Bearer YOUR_TOKEN`.

## API Example

```python
import requests

resp = requests.post(
    "https://atomgpt.org/hea/screen",
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
response = agent.query_sync("Show hea explorer for Silicon")
print(response)
```

## Reference

- Mater. Today 19, 349 (2016)
