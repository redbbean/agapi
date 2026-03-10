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

resp = requests.post(
    "https://atomgpt.org/quantum/bandstructure",
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
response = agent.query_sync("Show quantum computation for Silicon")
print(response)
```

## Reference

- J. Phys.: Condens. Matter 33, 385501 (2021)
