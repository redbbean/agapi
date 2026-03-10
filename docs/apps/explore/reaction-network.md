---
title: Reaction Network
---

# Reaction Network

Balance chemical equations (SVD null-space), compute reaction thermodynamics ΔH from JARVIS-DFT formation energies, and build interactive d3.js bipartite reaction network graphs.

[:material-open-in-new: Open App](https://atomgpt.org/reaction_network){ .md-button .md-button--primary }

---

## Overview

Balance chemical equations (SVD null-space), compute reaction thermodynamics ΔH from JARVIS-DFT formation energies, and build interactive d3.js bipartite reaction network graphs.

!!! info "Data Source"
    **dft_3d (formation energies)**

## Endpoints

- `GET /reaction_network`
- `POST /reaction_network/balance`
- `POST /reaction_network/thermodynamics`
- `POST /reaction_network/network`

**Request Models:** `BalanceRequest`, `ThermodynamicsRequest`, `NetworkRequest`

!!! note "Authentication"
    All POST endpoints require `Authorization: Bearer YOUR_TOKEN`.

## API Example

```python
import requests

response = requests.post(
    "https://atomgpt.org/reaction_network/balance",
    headers={
        "Authorization": "Bearer sk-XYZ",
        "accept": "application/json",
        "Content-Type": "application/json",
    },
    json={"equation": "Fe2O3 + C -> Fe + CO2"},
)
data = response.json()
print(data)
```

## AGAPI Agent

```python
from agapi.agents import AGAPIAgent
import os

agent = AGAPIAgent(api_key=os.environ.get("AGAPI_KEY"))
response = agent.query_sync("Show reaction network for Silicon")
print(response)
```

## Reference

- NPJ Comp. Mat. 6, 173 (2020)
