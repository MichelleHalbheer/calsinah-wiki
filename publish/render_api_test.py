import json
from pathlib import Path
from bs4 import BeautifulSoup

import requests

RENDER_API_URL = "http://127.0.0.1:27123/render"

TIMELINE = r"""
```aat-vertical
History of Calsinah
dateDisplayFormat: {year}
```
"""

payload = {
    #"filePath": Path(r"C:\Users\MichelleHalbheer\Documents\Calsinah DM\9 Lore\91 History\A Brief History of Calsinah.md").as_posix(),
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


def strip_links_inside_cards(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    for card in soup.select("a.aat-card"):
        for inner_link in card.select("a"):
            if inner_link is card:
                continue

            inner_link.unwrap()

    return str(soup)

html = strip_links_inside_cards(html)

print(html[:5000])

with open(
    "rendered_timeline.html",
    "w",
    encoding="utf-8"
) as f:
    f.write(html)

print("Saved to rendered_timeline.html")
