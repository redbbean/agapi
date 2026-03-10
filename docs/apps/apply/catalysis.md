---
title: Catalysis
---

# Catalysis

Predict adsorption energy of a molecule on a substrate using ALIGNN-FF. Input: substrate POSCAR + catalyst (substrate+adsorbate) POSCAR + adsorbate indices. Computes E_ads = E_cat - E_sub - E_mol.

[:material-open-in-new: Open App](https://atomgpt.org/catalysis){ .md-button .md-button--primary }

---

## Overview

Predict adsorption energy of a molecule on a substrate using ALIGNN-FF. Input: substrate POSCAR + catalyst (substrate+adsorbate) POSCAR + adsorbate indices. Computes E_ads = E_cat - E_sub - E_mol.

!!! info "Data Source"
    **ALIGNN-FF**

## Endpoints

- `GET /catalysis`
- `POST /catalysis/predict`

**Request Models:** `CatalysisPredictRequest`

!!! note "Authentication"
    All POST endpoints require `Authorization: Bearer YOUR_TOKEN`.

## API Example

```python
import requests

response = requests.post(
    "https://atomgpt.org/catalysis/predict",
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
response = agent.query_sync("Show catalysis for Silicon")
print(response)
```

## Reference

- Comp. Mat. Sci. 259, 114063 (2025)
