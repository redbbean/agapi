---
title: Raman Matching
---

# Raman Matching

Raman spectrum matching against JARVIS ramandb (~5K materials). User provides freq_cm vs raman_activity data + optional formula. Cosine similarity matching to find best-fit materials.

[:material-open-in-new: Open App](https://atomgpt.org/raman){ .md-button .md-button--primary }

---

## Overview

Raman spectrum matching against JARVIS ramandb (~5K materials). User provides freq_cm vs raman_activity data + optional formula. Cosine similarity matching to find best-fit materials.

!!! info "Data Source"
    **ramandb (~5K entries)**

## Endpoints

- `GET /raman`
- `POST /raman/lookup`
- `POST /raman/match`

**Request Models:** `RamanMatchRequest`, `RamanLookupRequest`

!!! note "Authentication"
    All POST endpoints require `Authorization: Bearer YOUR_TOKEN`.

## API Example

```python
import requests

response = requests.post(
    "https://atomgpt.org/raman/lookup",
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
response = agent.query_sync("Show raman matching for Silicon")
print(response)
```

## Reference

- Comp. Mat. Sci. 259, 114063 (2025)
