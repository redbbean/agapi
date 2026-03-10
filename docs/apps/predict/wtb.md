---
title: Wannier TB Bands
---

# Wannier TB Bands

Wannier tight-binding Hamiltonian bandstructure and DOS. Selects material by JID from JARVIS-WTB database, downloads wannier90_hr.dat, computes band structure and DOS.

[:material-open-in-new: Open App](https://atomgpt.org/wtb){ .md-button .md-button--primary }

---

## Overview

Wannier tight-binding Hamiltonian bandstructure and DOS. Selects material by JID from JARVIS-WTB database, downloads wannier90_hr.dat, computes band structure and DOS.

!!! info "Data Source"
    **JARVIS-WTB (wannier90_hr.dat files)**

## Endpoints

- `GET /wtb`
- `GET /wtb/options`
- `POST /wtb/predict`

**Request Models:** `WtbPredictRequest`

!!! note "Authentication"
    All POST endpoints require `Authorization: Bearer YOUR_TOKEN`.

## API Example

```python
import requests

response = requests.post(
    "https://atomgpt.org/wtb/predict",
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
response = agent.query_sync("Show wannier tb bands for Silicon")
print(response)
```

## Reference

- Sci. Data 8, 106 (2021)
