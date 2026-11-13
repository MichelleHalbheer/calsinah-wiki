import re
import shutil
from pathlib import Path
import yaml
import json
from tqdm import tqdm

with open(Path(__file__).parents[0].joinpath("content-sync-config.json"), "r") as f:
    config = json.load(f)

vault = Path(__file__).resolve().parents[2].joinpath(config.get("vault", "Calsinah DM"))
quartz = Path(__file__).resolve().parents[1].joinpath("content")

include_folders = config.get("include", [])

if quartz.exists():
    shutil.rmtree(quartz)

quartz.mkdir(parents=True)

for folder in tqdm(include_folders):
    src = vault.joinpath(folder)

    for file in tqdm(src.rglob("*.md"), leave=False):

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

        # Remove DM-only sections
        starts = len(re.findall(r':::dm\s*$', text, re.MULTILINE | re.IGNORECASE))
        ends = len(re.findall(r'^:::\s*$', text, re.MULTILINE | re.IGNORECASE))

        if starts > 0:
            if starts != ends:
                raise ValueError("Unmatched :::dm markers!")

            text_redacted = re.sub(
                r'\n?:::dm\s*\n.*?\n:::\s*(?:\n|$)',
                '\n',
                text,
                flags=re.DOTALL | re.IGNORECASE
            )
        else:
            text_redacted = text

        rel = file.relative_to(vault)

        target = quartz.joinpath(rel)

        target.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        target.write_text(text_redacted, encoding="utf-8")