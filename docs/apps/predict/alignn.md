---
title: ALIGNN Predictor
---

# ALIGNN Predictor

Predict 50+ materials properties with ALIGNN graph neural networks. Query by JARVIS ID or upload POSCAR. Web prediction endpoint returns all available model predictions.

[:material-open-in-new: Open App](https://atomgpt.org/alignn){ .md-button .md-button--primary }

---

## Overview

Predict 50+ materials properties with ALIGNN graph neural networks. Query by JARVIS ID or upload POSCAR. Web prediction endpoint returns all available model predictions.

!!! info "Data Source"
    **ALIGNN pretrained models**

## Endpoints

- `GET /alignn`
- `GET /alignn/query`
- `POST /alignn/query`
- `POST /alignn/web_predict`

**Request Models:** —

!!! note "Authentication"
    All POST endpoints require `Authorization: Bearer YOUR_TOKEN`.

## API Example

```python
import requests

resp = requests.post(
    "https://atomgpt.org/alignn/web_predict",
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
response = agent.query_sync("Show alignn predictor for Silicon")
print(response)
```

## Reference

- NPJ Comp. Mat. 7, 1 (2021)
