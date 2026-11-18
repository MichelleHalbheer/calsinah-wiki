import json

import requests

RENDER_API_URL = "http://127.0.0.1:27123/render"

TIMELINE = r"""
---
publish: true
type: history
related_events: []
related_eras: []
tags:
  - history
date-created: 2026-11-16T14:54
date-updated: 2026-11-18T11:45
---
# A Brief History of Calsinah
## Overview


```aat-vertical
History of Calsinah
dateDisplayFormat: {year}
```
## Origins
## Development
## Major Turning Points
## Legacy
## Related Events
## Notes
"""

payload = {
    "content": TIMELINE,
    "format": "html"
}

response = requests.post(
    RENDER_API_URL,
    json=payload,
    timeout=120
)

response.raise_for_status()

html = json.loads(response.text)["html"]

print(html[:5000])

with open(
    "rendered_timeline.html",
    "w",
    encoding="utf-8"
) as f:
    f.write(html)

print("Saved to rendered_timeline.html")
