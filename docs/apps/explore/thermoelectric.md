---
title: Thermoelectric
---

# Thermoelectric

Visualize and compare thermoelectric (BoltzTrap) data from JARVIS-DFT. Seebeck coefficient, electrical conductivity, and power factor parsed from JARVIS XML pages.

[:material-open-in-new: Open App](https://atomgpt.org/thermoelectric){ .md-button .md-button--primary }

---

## Overview

Visualize and compare thermoelectric (BoltzTrap) data from JARVIS-DFT. Seebeck coefficient, electrical conductivity, and power factor parsed from JARVIS XML pages.

!!! info "Data Source"
    **dft_3d (JARVIS XML)**

## Endpoints

- `GET /thermoelectric`
- `POST /thermoelectric/search`
- `GET /thermoelectric/data/{jid}`

**Request Models:** `ThermoelectricSearchRequest`

!!! note "Authentication"
    All POST endpoints require `Authorization: Bearer YOUR_TOKEN`.

## API Example

```python
import requests

response = requests.post(
    "https://atomgpt.org/thermoelectric/search",
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
response = agent.query_sync("Show thermoelectric for Silicon")
print(response)
```

## Reference

- J. Phys. Cond. Matt. 32, 475501 (2020)
