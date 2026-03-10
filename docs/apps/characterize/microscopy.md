---
title: MicroscopyGPT
---

# MicroscopyGPT

Microscopy Suite with 3 tabs: (1) STEM Analyzer — proxy to MicroscopyGPT service (port 7000) for atom column detection and classification, (2) STEM Generator — simulate STEM images from crystal structures, (3) STM Image generator.

[:material-open-in-new: Open App](https://atomgpt.org/microscopy){ .md-button .md-button--primary }

---

## Overview

Microscopy Suite with 3 tabs: (1) STEM Analyzer — proxy to MicroscopyGPT service (port 7000) for atom column detection and classification, (2) STEM Generator — simulate STEM images from crystal structures, (3) STM Image generator.

!!! info "Data Source"
    **MicroscopyGPT model + jarvis.io.stm**

## Endpoints

- `GET /microscopy`
- `GET /microscopy/health`
- `POST /microscopy/predict`
- `POST /microscopy/segment`
- `POST /microscopy/stem_generate`
- `POST /microscopy/stm_image`

**Request Models:** —

!!! note "Authentication"
    All POST endpoints require `Authorization: Bearer YOUR_TOKEN`.

## API Example

```python
import requests

response = requests.post(
    "https://atomgpt.org/microscopy/predict",
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
response = agent.query_sync("Show microscopygpt for Silicon")
print(response)
```

## Reference

- J. Chem. Inf. Model 63, 1708 (2023); J. Phys. Chem. Lett. 16, 7028 (2025)
