---
title: SuperconGPT
---

# SuperconGPT

3 tabs: (1) Inverse design — generate crystal structures for target Tc using AtomGPT, (2) Database search for known superconductors, (3) Predict Tc for any structure with ALIGNN.

[:material-open-in-new: Open App](https://atomgpt.org/supercon){ .md-button .md-button--primary }

---

## Overview

3 tabs: (1) Inverse design — generate crystal structures for target Tc using AtomGPT, (2) Database search for known superconductors, (3) Predict Tc for any structure with ALIGNN.

!!! info "Data Source"
    **dft_3d + AtomGPT + ALIGNN supercon model**

## Endpoints

- `GET /supercon`
- `POST /supercon/generate`
- `GET /supercon/generate`
- `GET /supercon/search`
- `POST /supercon/predict_tc`

**Request Models:** `SuperconGenerateRequest`, `SuperconPredictRequest`

!!! note "Authentication"
    All POST endpoints require `Authorization: Bearer YOUR_TOKEN`.

## API Example

```python
import requests

response = requests.post(
    "https://atomgpt.org/supercon/generate",
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
response = agent.query_sync("Show supercongpt for Silicon")
print(response)
```

## Reference

- NPJ Comp. Mat. 8, 244 (2023); J. Phys. Chem. Lett. 15, 6909 (2024)
