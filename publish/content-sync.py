
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

def current_directive(stack):
    if not stack:
        return None

    return stack[-1]

def redact_dm_sections(text, path):
    output = []
    redacted = 0
    directive_stack = []

    for line_number, line in enumerate(text.splitlines(keepends=True), 1):

        directive_match = re.match(
            r"^\s*:::\s*([a-zA-Z0-9_-]+)\s*$",
            line
        )

        if directive_match:
            directive_stack.append(directive_match.group(1).lower())
            if current_directive(directive_stack) == "dm":
                redacted += 1
                continue

        if re.match(r"^\s*:::\s*$", line):
            if directive_stack:
                inside_dm = current_directive(directive_stack) == "dm"
                directive_stack.pop()
                if inside_dm:
                    continue
            else:
                raise ValueError(
                    f"Unexpected ::: in {path}, line {line_number}"
                )

        if "dm" in directive_stack:
            continue

        output.append(line)

    if directive_stack:
        raise ValueError(
            f"Unclosed directive(s) in {path}: {directive_stack}"
        )

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
# Processing Attachments
# --------------------------------------------------

def find_attachments(text: str, config: dict) -> set[str]:
    attachments = set()

    matches = re.findall(
        r"!?\[\[([^\]]+)\]\]",
        text
    )

    for match in matches:
        name = match.split("|", 1)[0].strip()

        suffix = Path(name).suffix.lower()

        if suffix and suffix in config["attachment_extensions"]:
            attachments.add(name)

    return attachments

def resolve_attachment(note_path, attachment_name):
    note_dir = note_path.parent

    candidates = [
        note_dir.joinpath(attachment_name),
        note_dir.joinpath("Attachments", attachment_name),
    ]

    matches = [p for p in candidates if p.exists()]

    if not matches:
        raise FileNotFoundError(
            f"Attachment not found: {attachment_name}\nReferenced in note: {note_path}"
        )

    if len(matches) > 1:
        raise ValueError(
            f"Ambiguous attachment: {attachment_name}\nReferenced in note: {note_path}"
        )

    return matches[0]


# --------------------------------------------------
# Sync content
# --------------------------------------------------

def sync_content(vault, staging, include_folders, config):
    copied = 0
    excluded = 0
    redacted_total = 0
    seen_files = set()
    referenced_attachments = []

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

            target_relative = relative

            root_folders = config.get("root_folders", [])
            if root_folders:
                for root in root_folders:
                    try:
                        target_relative = relative.relative_to(root)
                        break
                    except ValueError:
                        continue


            if target_relative in seen_files:
                raise ValueError(f"Duplicate file: {target_relative}")

            seen_files.add(target_relative)

            attachments = find_attachments(filtered, config)
            resolved_attachments = [resolve_attachment(file, att) for att in attachments]
            referenced_attachments.extend(resolved_attachments)

            target = staging.joinpath(target_relative)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(filtered, encoding="utf-8")

            copied += 1
            redacted_total += redacted

    deduplicated_attachments = set(referenced_attachments)

    for asset in deduplicated_attachments:
        try:
            source = Path(asset)
        except Exception as e:
            raise ValueError(f"Attachment error for '{asset}': {e}")

        relative = source.relative_to(vault)
        target = staging.joinpath(relative)
        target.parent.mkdir(parents=True, exist_ok=True)

        if not target.exists():
            shutil.copy2(source, target)

    num_attachments = len(deduplicated_attachments)
    
    return copied, excluded, redacted_total, num_attachments


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
    npx = shutil.which("npx") or shutil.which("npx.cmd")
    npm = shutil.which("npm") or shutil.which("npm.cmd")

    if npx is None:
        raise RuntimeError(
            "Could not locate npx on PATH"
        )

    if npm is None:
        raise RuntimeError(
            "Could not locate npm on PATH"
        )
    
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

    parser.add_argument(
        "--full-check",
        action="store_true",
        help="Run full TypeScript and formatting checks (slower)."
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

        copied, excluded, redacted, num_attachments = sync_content(
            vault,
            staging,
            include_folders,
            config
        )

        print(f"\n  Files copied: {copied}")
        print(f"  Notes excluded: {excluded}")
        print(f"  DM sections removed: {redacted}")
        print(f"  Attachments: {num_attachments}")

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
                [npx, "prettier", ".", "--write"],
                "Formatting repository with Prettier",
                repo_root
            )

            # Check and build
            if args.full_check:
                run_command(
                    [npm, "run", "check"],
                    "Checking TypeScript and formatting",
                    repo_root
                )

                run_command(
                    [npx, "quartz", "build"],
                    "Building Quartz",
                    repo_root
                )

            if args.push:
                run_command(
                    [npx, "quartz", "sync"],
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
        raise e
