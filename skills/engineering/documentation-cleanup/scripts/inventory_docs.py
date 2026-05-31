"""Read-only documentation inventory helper for documentation-cleanup.

The script scans likely project documentation files and prints a compact
inventory. It never writes files, follows no symlinks, and ignores common
dependency/build/private folders by default.
"""

from __future__ import annotations

import argparse
import json
import os
import re
from dataclasses import asdict, dataclass
from pathlib import Path


DOC_EXTENSIONS = {".md", ".mdx", ".rst", ".txt"}
ROOT_DOC_NAMES = {
    "README.md",
    "README.mdx",
    "CONTEXT.md",
    "AGENT.md",
    "AGENTS.md",
    "CLAUDE.md",
    "project_skills.md",
    "progress.md",
    "progress_current.md",
    "progress_archive.txt",
}
INCLUDED_DIR_NAMES = {
    "docs",
    "documentation",
    "doc",
    "issues",
    "adr",
    "adrs",
    "decisions",
    ".github",
}
SKIPPED_DIR_NAMES = {
    ".git",
    ".hg",
    ".svn",
    ".venv",
    "venv",
    "env",
    "node_modules",
    "vendor",
    "build",
    "dist",
    "target",
    ".dart_tool",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
    ".local",
    ".scratch",
    "tmp",
    "temp",
    "__pycache__",
}

HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
MARKDOWN_LINK_RE = re.compile(r"!?\[[^\]]+\]\(([^)]+)\)")
LAST_UPDATED_RE = re.compile(
    r"(last updated|updated|date)\s*[:\-]\s*(\d{4}-\d{2}-\d{2})",
    re.IGNORECASE,
)
WINDOWS_ABSOLUTE_RE = re.compile(r"[A-Za-z]:\\[^\s)>\"]+")
POSIX_HOME_RE = re.compile(r"/Users/[^/\s)>\"]+|/home/[^/\s)>\"]+")
SECRET_HINT_RE = re.compile(
    r"(api[_-]?key|secret|token|password|credential|authorization)",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class DocInventoryItem:
    path: str
    role_hints: list[str]
    line_count: int
    heading_count: int
    headings: list[str]
    link_count: int
    last_updated: list[str]
    risk_hints: list[str]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Read-only documentation inventory for GOATED documentation-cleanup."
    )
    parser.add_argument("--repo", required=True, help="Target project root to inspect.")
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit JSON instead of a Markdown table.",
    )
    return parser.parse_args()


def should_scan_path(path: Path, repo: Path) -> bool:
    try:
        relative = path.relative_to(repo)
    except ValueError:
        return False

    if any(part in SKIPPED_DIR_NAMES for part in relative.parts[:-1]):
        return False

    if path.name in ROOT_DOC_NAMES:
        return True

    if path.suffix.lower() not in DOC_EXTENSIONS:
        return False

    first_part = relative.parts[0] if relative.parts else ""
    return first_part in INCLUDED_DIR_NAMES


def iter_doc_paths(repo: Path) -> list[Path]:
    paths: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(repo):
        dirnames[:] = sorted(
            dirname
            for dirname in dirnames
            if dirname not in SKIPPED_DIR_NAMES
            and not (Path(dirpath) / dirname).is_symlink()
        )

        current_dir = Path(dirpath)
        for filename in sorted(filenames):
            path = current_dir / filename
            if path.is_symlink():
                continue
            if should_scan_path(path, repo):
                paths.append(path)
    return sorted(paths, key=lambda item: item.relative_to(repo).as_posix().lower())


def role_hints(relative_path: str, text_lower: str) -> list[str]:
    hints: list[str] = []
    path_lower = relative_path.lower()

    if path_lower.endswith("readme.md") or "onboarding" in text_lower:
        hints.append("human guide")
    if "docs/agents/" in path_lower or path_lower in {"agent.md", "agents.md", "claude.md"}:
        hints.append("ai-facing guide")
    if path_lower.endswith("context.md") or "project boundaries" in text_lower:
        hints.append("context source")
    if "project-standards" in path_lower or "standards" in path_lower:
        hints.append("standards profile")
    if "context-matrix" in path_lower or "context-map" in path_lower:
        hints.append("routing artifact")
    if "/adr/" in path_lower or "/decisions/" in path_lower or "decision record" in text_lower:
        hints.append("adr or decision")
    if "prd" in path_lower or "requirements" in text_lower:
        hints.append("prd or spec")
    if "external-docs" in path_lower or "lookup" in text_lower:
        hints.append("external-doc note")
    if "progress" in path_lower or "current status" in text_lower:
        hints.append("status or progress")
    if "/issues/" in path_lower or path_lower.startswith("issues/"):
        hints.append("issue workbench")
    if "archive" in path_lower:
        hints.append("archive or history")

    return hints or ["unknown"]


def risk_hints(text: str, relative_path: str) -> list[str]:
    hints: list[str] = []
    lower_text = text.lower()

    if WINDOWS_ABSOLUTE_RE.search(text) or POSIX_HOME_RE.search(text):
        hints.append("absolute-local-path")
    if SECRET_HINT_RE.search(text):
        hints.append("secret-word")
    if "last updated" not in lower_text and "updated by" not in lower_text:
        hints.append("no-last-updated-marker")
    if text.count("\n") > 250:
        hints.append("large-doc")
    if "todo" in lower_text or "tbd" in lower_text:
        hints.append("open-placeholder")
    if relative_path.lower().endswith("readme.md") and "current state" in lower_text:
        hints.append("root-current-state-claim")

    return hints


def inspect_doc(path: Path, repo: Path) -> DocInventoryItem:
    relative_path = path.relative_to(repo).as_posix()
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()

    headings = []
    for line in lines:
        match = HEADING_RE.match(line)
        if match:
            headings.append(f"{match.group(1)} {match.group(2)}")

    links = MARKDOWN_LINK_RE.findall(text)
    last_updated = [match.group(2) for match in LAST_UPDATED_RE.finditer(text)]

    return DocInventoryItem(
        path=relative_path,
        role_hints=role_hints(relative_path, text.lower()),
        line_count=len(lines),
        heading_count=len(headings),
        headings=headings[:8],
        link_count=len(links),
        last_updated=last_updated,
        risk_hints=risk_hints(text, relative_path),
    )


def emit_markdown(items: list[DocInventoryItem], repo: Path) -> None:
    print(f"# Documentation Inventory\n\nRepo: `{repo}`\n")
    print("| Path | Roles | Lines | Headings | Links | Last updated | Risk hints |")
    print("| --- | --- | ---: | ---: | ---: | --- | --- |")
    for item in items:
        print(
            "| {path} | {roles} | {lines} | {headings} | {links} | {updated} | {risks} |".format(
                path=item.path,
                roles=", ".join(item.role_hints),
                lines=item.line_count,
                headings=item.heading_count,
                links=item.link_count,
                updated=", ".join(item.last_updated) or "-",
                risks=", ".join(item.risk_hints) or "-",
            )
        )


def main() -> int:
    args = parse_args()
    repo = Path(args.repo).expanduser().resolve()
    if not repo.exists() or not repo.is_dir():
        raise SystemExit(f"Repo path does not exist or is not a directory: {repo}")

    items = [inspect_doc(path, repo) for path in iter_doc_paths(repo)]
    if args.json:
        print(json.dumps([asdict(item) for item in items], indent=2))
    else:
        emit_markdown(items, repo)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
