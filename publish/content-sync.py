
import re
import json
import yaml
import shutil
import argparse
import subprocess
import sys
import tempfile

from pathlib import Path
from tqdm import tqdm


# --------------------------------------------------
# Configuration
# --------------------------------------------------

def load_config(config_file):
    with config_file.open("r", encoding="utf-8") as f:
        return json.load(f)


def get_paths(script_dir, config):
    repo_root = script_dir.parent

    vault = repo_root.parent.joinpath(
        config.get("vault", "Calsinah DM")
    )

    content = repo_root.joinpath("content")

    return repo_root, vault, content


# --------------------------------------------------
# Frontmatter processing
# --------------------------------------------------

def should_publish(text, path):
    if not text.startswith("---"):
        return False

    match = re.match(
        r"\A---[ \t]*\r?\n(.*?)\r?\n---[ \t]*(?:\r?\n|\Z)",
        text,
        re.DOTALL
    )

    if not match:
        raise ValueError(f"Malformed frontmatter: {path}")

    try:
        metadata = yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML in {path}: {e}")

    if not isinstance(metadata, dict):
        raise ValueError(f"Frontmatter must be a YAML mapping: {path}")

    publish = metadata.get("publish")
    if not isinstance(publish, bool):
        raise ValueError(
            f"'publish' must be true or false in {path}"
        )

    return publish


# --------------------------------------------------
# DM section filtering
# --------------------------------------------------

def redact_dm_sections(text, path):
    output = []
    inside_dm = False
    redacted = 0

    for line_number, line in enumerate(text.splitlines(keepends=True), 1):
        stripped = line.strip()

        is_start = re.fullmatch(r":::dm", stripped, re.IGNORECASE)
        is_end = stripped == ":::"

        if is_start:
            if inside_dm:
                raise ValueError(
                    f"Nested DM section in {path}, line {line_number}"
                )

            inside_dm = True
            redacted += 1
            continue

        if is_end:
            if not inside_dm:
                raise ValueError(
                    f"Unexpected ::: in {path}, line {line_number}"
                )

            inside_dm = False

            while output and not output[-1].strip():
                output.pop()

            if output:
                output.append("\n")

            continue

        if inside_dm:
            continue

        if stripped.lower().startswith(":::dm"):
            raise ValueError(
                f"Malformed DM marker in {path}, line {line_number}"
            )

        output.append(line)

    if inside_dm:
        raise ValueError(f"Unclosed DM section in {path}")

    result = "".join(output)
    result = re.sub(r"\n[ \t]*\n(?:[ \t]*\n)+", "\n\n", result)
    result = result.lstrip("\r\n")

    return result, redacted


# --------------------------------------------------
# Content validation
# --------------------------------------------------

def validate_content(directory, blocked_phrases):
    print("\nValidating generated content...")

    files = list(directory.rglob("*.md"))

    for file in files:
        text = file.read_text(encoding="utf-8")

        if re.search(
            r"^\s*:::dm\s*$",
            text,
            re.MULTILINE | re.IGNORECASE
        ):
            raise ValueError(
                f"DM marker remains in published file: {file}"
            )

        for phrase in blocked_phrases:
            if phrase.casefold() in text.casefold():
                raise ValueError(
                    f"Blocked phrase '{phrase}' found in {file}"
                )

    print(f"  {len(files)} Markdown files validated.")
    print("  No residual DM markers found.")
    print("  No blocked phrases found.")


# --------------------------------------------------
# Sync content
# --------------------------------------------------

def sync_content(vault, staging, include_folders):
    copied = 0
    excluded = 0
    redacted_total = 0
    seen_files = set()

    print("\nReading Obsidian vault...")

    for folder in tqdm(include_folders, desc="Folders"):
        source = vault.joinpath(folder)

        if not source.is_dir():
            raise FileNotFoundError(
                f"Configured vault folder not found: {source}"
            )

        for file in tqdm(
            sorted(source.rglob("*.md")),
            desc=folder,
            leave=False
        ):
            text = file.read_text(encoding="utf-8")

            if not should_publish(text, file):
                excluded += 1
                continue

            filtered, redacted = redact_dm_sections(text, file)
            relative = file.relative_to(vault)

            if relative in seen_files:
                raise ValueError(f"Duplicate file: {relative}")

            seen_files.add(relative)

            target = staging.joinpath(relative)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(filtered, encoding="utf-8")

            copied += 1
            redacted_total += redacted

    return copied, excluded, redacted_total


# --------------------------------------------------
# External commands
# --------------------------------------------------

def run_command(command, description, repo_root):
    print(f"\n{description}...")

    subprocess.run(
        command,
        cwd=repo_root,
        check=True
    )


# --------------------------------------------------
# Main publishing process
# --------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Calsinah Wiki Publisher"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Filter and validate without changing Quartz content."
    )

    parser.add_argument(
        "--no-push",
        action="store_true",
        help="Build locally without pushing to GitHub."
    )

    parser.add_argument(
        "--push",
        action="store_true",
        help="Commit and push generated content to GitHub."
    )

    args = parser.parse_args()

    if args.push and args.no_push:
        parser.error("--push and --no-push cannot be used together.")

    script_dir = Path(__file__).resolve().parent
    config_file = script_dir.joinpath("content-sync-config.json")

    config = load_config(config_file)

    repo_root, vault, content = get_paths(script_dir, config)

    include_folders = config.get("include", [])
    blocked_phrases = config.get("blocked_phrases", [])

    if not vault.is_dir():
        raise FileNotFoundError(f"Vault not found: {vault}")

    if not include_folders:
        raise ValueError("No folders configured for publishing.")

    print("\n========================================")
    print("       CALSINAH WIKI PUBLISHER")
    print("========================================")

    with tempfile.TemporaryDirectory(
        prefix=".publish-staging-",
        dir=repo_root
    ) as temp_dir:

        staging = Path(temp_dir).joinpath("content")
        staging.mkdir()

        copied, excluded, redacted = sync_content(
            vault,
            staging,
            include_folders
        )

        print(f"\n  Files copied: {copied}")
        print(f"  Notes excluded: {excluded}")
        print(f"  DM sections removed: {redacted}")

        validate_content(staging, blocked_phrases)

        if args.dry_run:
            print("\nDRY RUN: No files changed or published.")
            return

        # Replace Quartz content
        print("\nUpdating Quartz content...")

        backup = Path(temp_dir).joinpath("content-backup")

        if content.exists():
            content.rename(backup)

        try:
            try:
                staging.rename(content)
            except Exception:
                if backup.exists():
                    backup.rename(content)
                raise

            # Format repository
            run_command(
                ["npx", "prettier", ".", "--write"],
                "Formatting repository with Prettier",
                repo_root
            )

            # Check and build
            run_command(
                ["npm", "run", "check"],
                "Checking TypeScript and formatting",
                repo_root
            )

            run_command(
                ["npx", "quartz", "build"],
                "Building Quartz",
                repo_root
            )

            if args.push:
                run_command(
                    ["npx", "quartz", "sync"],
                    "Syncing Quartz to Git",
                    repo_root
                )
            else:
                print("\nLocal build successful.")
                print("No Git push requested.")
        except Exception as e:
            print(f"\nError during publishing: {e}")
            print("Restoring original content...")

            if content.exists():
                shutil.rmtree(content)

            if backup.exists():
                backup.rename(content)

            raise e
        finally:
            if backup.exists():
                shutil.rmtree(backup)

    print("\n========================================")
    print("       PUBLISH SUCCESSFUL")
    print("========================================")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\nPUBLISH FAILED: {e}")
        sys.exit(1)
