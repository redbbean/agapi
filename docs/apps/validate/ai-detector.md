---
title: AI Detector
---

# AI Detector

AI-generated text detector. Hybrid approach: statistical analysis (perplexity, burstiness, entropy variance, sentence length) + LLM judge. Scans text and returns confidence scores.

[:material-open-in-new: Open App](https://atomgpt.org/ai_detector){ .md-button .md-button--primary }

---

## Overview

AI-generated text detector. Hybrid approach: statistical analysis (perplexity, burstiness, entropy variance, sentence length) + LLM judge. Scans text and returns confidence scores.

!!! info "Data Source"
    **Statistical analysis + LLM judge**

## Endpoints

- `GET /ai_detector`
- `POST /ai_detector/scan`

**Request Models:** —

!!! note "Authentication"
    All POST endpoints require `Authorization: Bearer YOUR_TOKEN`.

## API Example

```python
import requests

resp = requests.post(
    "https://atomgpt.org/ai_detector/scan",
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
response = agent.query_sync("Show ai detector for Silicon")
print(response)
```

## Reference

- —
