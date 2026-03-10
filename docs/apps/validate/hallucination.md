---
title: Hallucination Detector
---

# Hallucination Detector

Verify LLM outputs against JARVIS data. Cross-check predicted properties and material claims with the DFT database. Streaming check endpoint for real-time verification.

[:material-open-in-new: Open App](https://atomgpt.org/hallucination_detector){ .md-button .md-button--primary }

---

## Overview

Verify LLM outputs against JARVIS data. Cross-check predicted properties and material claims with the DFT database. Streaming check endpoint for real-time verification.

!!! info "Data Source"
    **dft_3d + LLM verification**

## Endpoints

- `GET /hallucination_detector`
- `GET /detector`
- `POST /hallucination/check_stream`

**Request Models:** —

!!! note "Authentication"
    All POST endpoints require `Authorization: Bearer YOUR_TOKEN`.

## API Example

```python
import requests

response = requests.post(
    "https://atomgpt.org/hallucination/check_stream",
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
response = agent.query_sync("Show hallucination detector for Silicon")
print(response)
```

## Reference

- —
