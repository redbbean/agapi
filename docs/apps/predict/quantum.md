---
title: Quantum Computation
---

# Quantum Computation

Run Qiskit VQE/VQD on Wannier tight-binding Hamiltonians from JARVIS-DFT using statevector simulator. EfficientSU2 (circuit6) ansatz. Full bandstructure via JARVIS get_bandstruct.

[:material-open-in-new: Open App](https://atomgpt.org/quantum){ .md-button .md-button--primary }

---

## Overview

Run Qiskit VQE/VQD on Wannier tight-binding Hamiltonians from JARVIS-DFT using statevector simulator. EfficientSU2 (circuit6) ansatz. Full bandstructure via JARVIS get_bandstruct.

!!! info "Data Source"
    **JARVIS-WTB + Qiskit**

## Endpoints

- `GET /quantum`
- `GET /quantum/materials`
- `POST /quantum/vqe`
- `POST /quantum/bandstructure`

**Request Models:** `VQERequest`, `BandstructureRequest`

!!! note "Authentication"
    All POST endpoints require `Authorization: Bearer YOUR_TOKEN`.

## API Example

```python
import requests

response = requests.post(
    "https://atomgpt.org/quantum/vqe",
    headers={
        "Authorization": "Bearer sk-XYZ",
        "accept": "application/json",
        "Content-Type": "application/json",
    },
    json={"jid": "JVASP-816", "kpoint": [0.5, 0.0, 0.5], "ham_type": "electron", "reps": 2},
)
data = response.json()
print(data)
```

## AGAPI Agent

```python
from agapi.agents import AGAPIAgent
import os

agent = AGAPIAgent(api_key=os.environ.get("AGAPI_KEY"))
response = agent.query_sync("Show quantum computation for Silicon")
print(response)
```

## Reference

- J. Phys.: Condens. Matter 33, 385501 (2021)
