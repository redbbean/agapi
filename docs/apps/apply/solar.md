---
title: Solar Cell Screening
---

# Solar Cell Screening

Predict theoretical solar cell performance: SLME (spectroscopic limited maximum efficiency) and Shockley-Queisser limit. Uses jarvis.analysis.solarefficiency.solar.SolarEfficiency directly. Input by JID or upload absorption data.

[:material-open-in-new: Open App](https://atomgpt.org/solar){ .md-button .md-button--primary }

---

## Overview

Predict theoretical solar cell performance: SLME (spectroscopic limited maximum efficiency) and Shockley-Queisser limit. Uses jarvis.analysis.solarefficiency.solar.SolarEfficiency directly. Input by JID or upload absorption data.

!!! info "Data Source"
    **dft_3d + jarvis.analysis.solarefficiency**

## Endpoints

- `GET /solar`
- `POST /solar/predict-jid`
- `POST /solar/predict-data`

**Request Models:** `SolarJidRequest`, `SolarDataRequest`

!!! note "Authentication"
    All POST endpoints require `Authorization: Bearer YOUR_TOKEN`.

## API Example

```python
import requests

resp = requests.post(
    "https://atomgpt.org/solar/predict-data",
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
response = agent.query_sync("Show solar cell screening for Silicon")
print(response)
```

## Reference

- Comp. Mat. Sci. 259, 114063 (2025)
