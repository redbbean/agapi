---
title: Direct Air Capture
---

# Direct Air Capture

Direct Air Capture CO₂ Isotherm Predictor using ALIGNN pretrained on hMOF data. Uses alignn.pretrained.get_figshare_model to auto-download the model.

[:material-open-in-new: Open App](https://atomgpt.org/dac){ .md-button .md-button--primary }

---

## Overview

Direct Air Capture CO₂ Isotherm Predictor using ALIGNN pretrained on hMOF data. Uses alignn.pretrained.get_figshare_model to auto-download the model.

!!! info "Data Source"
    **ALIGNN hMOF model**

## Endpoints

- `GET /dac`
- `POST /dac/predict`

**Request Models:** `DACPredictRequest`

!!! note "Authentication"
    All POST endpoints require `Authorization: Bearer YOUR_TOKEN`.

## API Example

```python
import requests

resp = requests.post(
    "https://atomgpt.org/dac/predict",
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
response = agent.query_sync("Show direct air capture for Silicon")
print(response)
```

## Reference

- Comp. Mat. Sci. 259, 114063 (2025)
