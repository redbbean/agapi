---
title: Phonon DOS
---

# Phonon DOS

Visualize and compare phonon density of states from JARVIS-DFT. Vibrational spectra fetched from JARVIS XML pages.

[:material-open-in-new: Open App](https://atomgpt.org/phonon_dos){ .md-button .md-button--primary }

---

## Overview

Visualize and compare phonon density of states from JARVIS-DFT. Vibrational spectra fetched from JARVIS XML pages.

!!! info "Data Source"
    **dft_3d (JARVIS XML)**

## Endpoints

- `GET /phonon_dos`
- `POST /phonon_dos/search`
- `GET /phonon_dos/data/{jid}`

**Request Models:** `PhononDOSSearchRequest`

!!! note "Authentication"
    All POST endpoints require `Authorization: Bearer YOUR_TOKEN`.

## API Example

```python
import requests

response = requests.post(
    "https://atomgpt.org/phonon_dos/search",
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
response = agent.query_sync("Show phonon dos for Silicon")
print(response)
```

## Reference

- Phys. Rev. Mat. 7, 023803 (2023)
