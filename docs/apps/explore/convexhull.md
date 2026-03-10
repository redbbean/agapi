---
title: Convex Hull
---

# Convex Hull

Convex hull phase diagram from JARVIS-DFT formation energies. Supports 2-element (2D plot), 3-element (ternary), and 4+-element (3D) systems.

[:material-open-in-new: Open App](https://atomgpt.org/convexhull){ .md-button .md-button--primary }

---

## Overview

Convex hull phase diagram from JARVIS-DFT formation energies. Supports 2-element (2D plot), 3-element (ternary), and 4+-element (3D) systems.

!!! info "Data Source"
    **dft_3d (formation energies)**

## Endpoints

- `GET /convexhull`
- `POST /convexhull/compute`

**Request Models:** `ConvexHullRequest`

!!! note "Authentication"
    All POST endpoints require `Authorization: Bearer YOUR_TOKEN`.

## API Example

```python
import requests

response = requests.post(
    "https://atomgpt.org/convexhull/compute",
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
response = agent.query_sync("Show convex hull for Silicon")
print(response)
```

## Reference

- NPJ Comp. Mat. 6, 173 (2020)
