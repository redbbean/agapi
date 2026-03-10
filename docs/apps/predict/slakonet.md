---
title: SlakoNet Bands
---

# SlakoNet Bands

Deep learning tight-binding band structures from neural network Slater-Koster parameters. Query by JARVIS ID or upload POSCAR. Web analyze endpoint returns band structure + DOS.

[:material-open-in-new: Open App](https://atomgpt.org/slakonet){ .md-button .md-button--primary }

---

## Overview

Deep learning tight-binding band structures from neural network Slater-Koster parameters. Query by JARVIS ID or upload POSCAR. Web analyze endpoint returns band structure + DOS.

!!! info "Data Source"
    **SlakoNet pretrained model**

## Endpoints

- `GET /slakonet`
- `GET /slakonet/bandstructure`
- `POST /slakonet/bandstructure`
- `POST /slakonet/web_analyze`

**Request Models:** —

!!! note "Authentication"
    All POST endpoints require `Authorization: Bearer YOUR_TOKEN`.

## API Example

```python
import requests

resp = requests.post(
    "https://atomgpt.org/slakonet/web_analyze",
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
response = agent.query_sync("Show slakonet bands for Silicon")
print(response)
```

## Reference

- J. Phys. Chem. Lett. 16, 11109 (2025)
