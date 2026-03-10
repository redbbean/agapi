---
title: ALIGNN-FF Dynamics
---

# ALIGNN-FF Dynamics

Universal ML force field. Structure relaxation (BFGS), geometry optimization, NVT/NPT molecular dynamics, and phonon calculations — all via ALIGNN-FF. Supports model selection (default or wt01).

[:material-open-in-new: Open App](https://atomgpt.org/alignn_ff_dynamics){ .md-button .md-button--primary }

---

## Overview

Universal ML force field. Structure relaxation (BFGS), geometry optimization, NVT/NPT molecular dynamics, and phonon calculations — all via ALIGNN-FF. Supports model selection (default or wt01).

!!! info "Data Source"
    **ALIGNN-FF pretrained model**

## Endpoints

- `GET /alignn_ff_dynamics`
- `GET /alignn_ff/query`
- `POST /alignn_ff/query`
- `GET /alignn_ff/relax`
- `POST /alignn_ff/optimize`
- `POST /alignn_ff/md`
- `POST /alignn_ff/phonons`

**Request Models:** `OptimizationRequest`, `MDRequest`, `PhononRequest`

!!! note "Authentication"
    All POST endpoints require `Authorization: Bearer YOUR_TOKEN`.

## API Example

```python
import requests

response = requests.post(
    "https://atomgpt.org/alignn_ff/query",
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
response = agent.query_sync("Show alignn-ff dynamics for Silicon")
print(response)
```

## Reference

- Digital Discovery 2(2), 346 (2023)
