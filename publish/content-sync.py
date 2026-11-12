import shutil
from pathlib import Path
import yaml
import json

with open("content-sync-config.json", "r") as f:
    config = json.load(f)

vault = Path(__file__).resolve().parent.parent.joinpath(config.get("vault", "Calsinah DM"))
quartz = Path(__file__).resolve().parent.joinpath("content")

include_folders = config.get("include", [])

if quartz.exists():
    shutil.rmtree(quartz)

quartz.mkdir(parents=True)

for folder in include_folders:
    src = vault / folder

    for file in src.rglob("*.md"):

        text = file.read_text(encoding="utf-8")

        if text.startswith("---"):

            try:
                parts = text.split("---", 2)

                if len(parts) >= 3:
                    metadata = yaml.safe_load(parts[1])

                    if metadata and metadata.get("publish") is False:
                        continue

            except Exception:
                pass

        rel = file.relative_to(vault)

        target = quartz / rel

        target.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        shutil.copy2(file, target)