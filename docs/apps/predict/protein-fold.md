---
title: Protein Fold
---

# Protein Fold

Protein structure prediction using ESMFold/OpenFold. Paste amino acid sequence, get 3D structure with pLDDT confidence. Web endpoint for interactive folding.

[:material-open-in-new: Open App](https://atomgpt.org/protein_fold){ .md-button .md-button--primary }

---

## Overview

Protein structure prediction using ESMFold/OpenFold. Paste amino acid sequence, get 3D structure with pLDDT confidence. Web endpoint for interactive folding.

!!! info "Data Source"
    **ESMFold / OpenFold models**

## Endpoints

- `GET /protein_fold`
- `GET /protein_fold/query`
- `POST /protein_fold/query`
- `POST /protein_fold/predict`
- `GET /openfold/query`

**Request Models:** `ProteinFoldRequest`

!!! note "Authentication"
    All POST endpoints require `Authorization: Bearer YOUR_TOKEN`.

## API Example

```python
import requests

resp = requests.post(
    "https://atomgpt.org/openfold/query",
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
response = agent.query_sync("Show protein fold for Silicon")
print(response)
```

## Reference

- Science (2023)
