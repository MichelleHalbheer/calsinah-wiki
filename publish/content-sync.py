
import re
import json
import yaml
import shutil
import argparse
import subprocess
import tempfile
import hashlib

from pathlib import Path
from tqdm import tqdm
import requests


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
# Render fenced code blocks
# --------------------------------------------------

def block_hash(block: str) -> str:
    return hashlib.sha256(
        block.encode("utf-8")
    ).hexdigest()

def render_via_api(
        payload: dict,
        api_url: str
    ) -> str:

    response = requests.post(
        api_url,
        json=payload,
        timeout=120
    )

    response.raise_for_status()

    html = json.loads(response.text)["html"]

    return html

def render_block_cached(
        block: str,
        block_type: str,
        api_url: str,
        cache: bool,
        cache_dir: Path,
        note_path: Path
    ) -> str:

    if cache:
        digest = block_hash(note_path.resolve().as_posix() + block)

        cache_file = cache_dir.joinpath(f"{digest}.html")

        if cache_file.exists():
            return cache_file.read_text(
                encoding="utf-8"
            )

    if block_type == "dataviewjs":
        payload = {
            "query": block,
            "format": "html"
        }
    elif block_type == "dataview":
        payload = {
            "code": block,
            "format": "html"
        }
    else:
        payload = {
                "content": block,
                "format": "html"
            }

    rendered_html = render_via_api(
        payload,
        api_url
    )

    if cache:
        cache_file.write_text(
            rendered_html,
            encoding="utf-8"
        )

    return rendered_html

def build_render_regex(
        block_types: list[str]
    ) -> re.Pattern:

    escaped = [
        re.escape(x)
        for x in block_types
    ]

    block_pattern = "|".join(escaped)

    return re.compile(
        rf"```({block_pattern})[^\n]*\n(.*?)\n```",
        re.DOTALL
    )

def copy_stylesheet(source: Path):
    if not source.exists():
        raise FileNotFoundError(
            f"Stylesheet not found: {source}"
        )

    content = source.read_text(encoding="utf-8")

    return content

def include_stylesheets(
        used_plugins: set[str],
        vault_path: Path = None,
        repo_root: Path = None
    ) -> str:

    for plugin in used_plugins:
        plugin_path = vault_path.joinpath(".obsidian", "plugins", plugin)
        css_path = plugin_path.joinpath("styles.css")

        quartz_styles_path = repo_root.joinpath("quartz", "styles")
        obsidian_plugins_scss = quartz_styles_path.joinpath(f"obsidian-styles.scss")

        if not obsidian_plugins_scss.exists():
            obsidian_plugins_scss.touch()
            obsidian_plugins_scss.write_text(
                f'@use "sass:map";',
                encoding="utf-8"
            )

        if css_path.exists():
            content = copy_stylesheet(css_path)

            obsidian_plugin_content = obsidian_plugins_scss.read_text(encoding="utf-8")

            obsidian_plugins_scss.write_text(
                obsidian_plugin_content + "\n\n"
                +f"/* ===== {plugin} ===== */\n\n" + content,
                encoding="utf-8"
            )

        custom_scss = quartz_styles_path.joinpath("custom.scss")

        if custom_scss.exists():
            custom_scss_content = custom_scss.read_text(encoding="utf-8")

            import_line = f'@use "./obsidian-styles.scss" as *;'

            if import_line not in custom_scss_content:
                custom_scss.write_text(
                    import_line + "\n" + custom_scss_content.rstrip(),
                    encoding="utf-8"
                )

def render_dynamic_blocks(
        text: str,
        config: dict,
        repo_root: Path,
        note_path: Path = None
    ) -> str:

    regex = build_render_regex(
        list(config["rendered_blocks"].keys())
    )

    api_url = config["render_api_url"]

    parts = []

    last_end = 0

    used_plugins = set()

    for match in regex.finditer(text):

        start, end = match.span()

        parts.append(
            text[last_end:start]
        )

        original_block = match.group(0)

        block_type = match.group(1).strip()

        block_info = config["rendered_blocks"].get(block_type)
        used_plugin = {block_info.get("plugin")}
        used_plugins.update(used_plugin)
        cache = block_info.get("cache", False)

        cache_dir = repo_root.joinpath(config["render-cache-dir"])

        if not cache_dir.exists():
            cache_dir.mkdir(parents=True, exist_ok=True)

        try:
            rendered_html = render_block_cached(
                original_block,
                block_type,
                api_url,
                cache=cache,
                cache_dir=cache_dir,
                note_path=note_path
            )

            replacement = (
                "<!-- ORIGINAL BLOCK\n"
                + original_block
                + "\n-->\n\n"
                + rendered_html
            )

            parts.append(
                replacement
            )

        except Exception as e:

            print(
                f"Failed rendering block: {e}"
            )

            parts.append(
                original_block
            )

        last_end = end

    parts.append(
        text[last_end:]
    )

    return "".join(parts), used_plugins

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

def resolve_attachment(note_path, attachment_name, vault):
    matches = list(
        vault.rglob(attachment_name)
    )

    if matches:
        return matches[0]

    if not matches:
        return None

    if len(matches) > 1:
        raise ValueError(
            f"Ambiguous attachment: {attachment_name}\nReferenced in note: {note_path}"
        )

    return matches[0]


# --------------------------------------------------
# Sync content
# --------------------------------------------------

def sync_content(vault, repo_root,staging, include_folders, config):
    copied = 0
    excluded = 0
    redacted_total = 0
    seen_files = set()
    referenced_attachments = []
    used_plugins = set()

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

            filtered, note_used_plugins = render_dynamic_blocks(filtered, config, repo_root, note_path=file)

            if note_used_plugins:
                used_plugins.update(note_used_plugins)

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
            resolved_attachments = [resolve_attachment(file, att, vault) for att in attachments]
            resolved_attachments = [att for att in resolved_attachments if att is not None]
            referenced_attachments.extend(resolved_attachments)

            target = staging.joinpath(target_relative)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(filtered, encoding="utf-8")

            copied += 1
            redacted_total += redacted

    include_stylesheets(used_plugins, vault, repo_root)

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
            repo_root,
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
