---
title: Vacancy Explorer
---

# Vacancy Explorer

Browse, search, and visualize vacancy formation energies from the JARVIS vacancy database (464 entries). Dataset loaded from jarvis.db.figshare.data('vacancydb').

[:material-open-in-new: Open App](https://atomgpt.org/vacancy){ .md-button .md-button--primary }

---

## Overview

Browse, search, and visualize vacancy formation energies from the JARVIS vacancy database (464 entries). Dataset loaded from jarvis.db.figshare.data('vacancydb').

!!! info "Data Source"
    **vacancydb (464 entries)**

## Endpoints

- `GET /vacancy`
- `POST /vacancy/search`
- `GET /vacancy/data/{defect_id}`

**Request Models:** `VacancySearchRequest`

!!! note "Authentication"
    All POST endpoints require `Authorization: Bearer YOUR_TOKEN`.

## API Example

```python
import requests

resp = requests.post(
    "https://atomgpt.org/vacancy/data/{defect_id}",
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
response = agent.query_sync("Show vacancy explorer for Silicon")
print(response)
```

## Reference

- AIP Advances 13(9) (2023)
