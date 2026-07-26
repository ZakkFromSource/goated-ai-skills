"""Shared result, path, text, and fixture primitives for validator concerns."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path

import yaml


HEADING_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)

# Directory names skipped during broad repo scans. This keeps validation focused
# on public source files and avoids virtualenvs, build output, and private notes.
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

# Public text scans are deliberately narrow. They are used for local path leaks
# and docs drift, not for broad secret scanning.
PUBLIC_TEXT_SUFFIXES = {
    ".md",
    ".mdx",
    ".rst",
    ".txt",
    ".py",
    ".toml",
    ".yml",
    ".yaml",
    ".json",
    ".lock",
}
PUBLIC_TEXT_NAMES = {".gitignore"}


@dataclass(frozen=True)
class Finding:
    """One validation message tied to a file and optional line number."""

    path: str
    message: str
    line: int | None = None

    def format(self) -> str:
        """Return the stable path-and-message form used by CLI reporting."""

        location = self.path if self.line is None else f"{self.path}:{self.line}"
        return f"{location}: {self.message}"


def relative(path: Path, repo: Path) -> str:
    """Return a stable repo-relative path for readable output."""

    return path.relative_to(repo).as_posix()


def read_text(path: Path) -> str:
    """Read text files leniently so one odd byte does not crash validation."""

    return path.read_text(encoding="utf-8", errors="replace")


def iter_files(repo: Path) -> list[Path]:
    """Walk the repo without following symlinks or scanning generated folders."""

    paths: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(repo):
        # Editing dirnames in place tells os.walk which child directories to skip.
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
            paths.append(path)
    return sorted(paths, key=lambda item: item.relative_to(repo).as_posix().lower())


def iter_public_text_files(repo: Path) -> list[Path]:
    """Return files that are reasonable to scan as public text surfaces."""

    return [
        path
        for path in iter_files(repo)
        if path.suffix.lower() in PUBLIC_TEXT_SUFFIXES
        or path.name in PUBLIC_TEXT_NAMES
    ]


def load_mapping(
    path: Path,
    label: str,
) -> tuple[dict[str, object] | None, list[Finding]]:
    """Load a YAML or JSON mapping and return readable parse findings."""

    if not path.exists():
        return None, [Finding(label, "missing required file")]

    try:
        loaded = yaml.safe_load(read_text(path))
    except yaml.YAMLError as exc:
        return None, [Finding(label, f"YAML or JSON parse error: {exc}")]

    if not isinstance(loaded, dict):
        return None, [Finding(label, "document must be a mapping")]
    return loaded, []


def is_string_list(value: object, *, allow_empty: bool = True) -> bool:
    """Return whether a fixture value is a list containing only strings."""

    return (
        isinstance(value, list)
        and (allow_empty or bool(value))
        and all(isinstance(entry, str) for entry in value)
    )


def validate_fixture_contract_values(
    actual: dict[str, object],
    required: dict[str, object],
    fixture_label: str,
    contract_name: str,
) -> list[Finding]:
    """Return readable findings for mismatched fixture contract values."""

    return [
        Finding(
            fixture_label,
            f"{contract_name} requires {field}={required_value!r}",
        )
        for field, required_value in required.items()
        if actual.get(field) != required_value
    ]
