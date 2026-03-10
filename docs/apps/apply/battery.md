---
title: Battery Explorer
---

# Battery Explorer

Battery cathode voltage profile and theoretical capacity predictor. Supports model selection: default_path or wt01_path. Uses ALIGNN-FF for intercalation energy calculations.

[:material-open-in-new: Open App](https://atomgpt.org/battery){ .md-button .md-button--primary }

---

## Overview

Battery cathode voltage profile and theoretical capacity predictor. Supports model selection: default_path or wt01_path. Uses ALIGNN-FF for intercalation energy calculations.

!!! info "Data Source"
    **ALIGNN-FF battery models**

## Endpoints

- `GET /battery`
- `POST /battery/predict`

**Request Models:** `BatteryPredictRequest`

!!! note "Authentication"
    All POST endpoints require `Authorization: Bearer YOUR_TOKEN`.

## API Example

```python
import requests

resp = requests.post(
    "https://atomgpt.org/battery/predict",
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
response = agent.query_sync("Show battery explorer for Silicon")
print(response)
```

## Reference

- Comp. Mat. Sci. 259, 114063 (2025)
