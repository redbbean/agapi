---
title: Elastic Tensor
---

# Elastic Tensor

Visualize and compare the 6×6 elastic stiffness tensor Cij for any JARVIS-DFT material. Search by JARVIS ID, formula, elements, space group, and modulus ranges. Heatmap, matrix, and comparison views.

[:material-open-in-new: Open App](https://atomgpt.org/elastic_tensor){ .md-button .md-button--primary }

---

## Overview

Visualize and compare the 6×6 elastic stiffness tensor Cij for any JARVIS-DFT material. Search by JARVIS ID, formula, elements, space group, and modulus ranges. Heatmap, matrix, and comparison views.

!!! info "Data Source"
    **dft_3d**

## Endpoints

- `GET /elastic_tensor`
- `POST /elastic_tensor/search`
- `GET /elastic_tensor/data/{jid}`

**Request Models:** `ElasticSearchRequest`

!!! note "Authentication"
    All POST endpoints require `Authorization: Bearer YOUR_TOKEN`.

## API Example

```python
import requests

response = requests.post(
    "https://atomgpt.org/elastic_tensor/search",
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
response = agent.query_sync("Show elastic tensor for Silicon")
print(response)
```

## Reference

- Phys. Rev. B 98, 014107 (2018)
