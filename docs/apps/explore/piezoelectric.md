---
title: Piezoelectric
---

# Piezoelectric

Visualize and compare DFPT piezoelectric stress tensors eij (C/m²) and IR intensities from JARVIS-DFT calculations.

[:material-open-in-new: Open App](https://atomgpt.org/piezoelectric){ .md-button .md-button--primary }

---

## Overview

Visualize and compare DFPT piezoelectric stress tensors eij (C/m²) and IR intensities from JARVIS-DFT calculations.

!!! info "Data Source"
    **dft_3d (DFPT)**

## Endpoints

- `GET /piezoelectric`
- `POST /piezoelectric/search`
- `GET /piezoelectric/data/{jid}`

**Request Models:** `PiezoSearchRequest`

!!! note "Authentication"
    All POST endpoints require `Authorization: Bearer YOUR_TOKEN`.

## API Example

```python
import requests

response = requests.post(
    "https://atomgpt.org/piezoelectric/search",
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
response = agent.query_sync("Show piezoelectric for Silicon")
print(response)
```

## Reference

- NPJ Comp. Mat. 6, 1 (2020)
