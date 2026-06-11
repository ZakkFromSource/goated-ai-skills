"""Read-only validator for GOATED AI Skills source-repo skill files.

This script is intentionally plain Python. It is meant to be easy for a future
maintainer to inspect and change without learning a test framework, linter, or
custom validation library first.

The validator has three result types:

- blocking errors: fail the command and should be fixed before committing;
- human-review notes: do not fail, but ask a reviewer to look at a standard
  optional field such as `compatibility`;
- report-only drift: do not fail, but point to docs/examples that may still
  mention old schema fields.
"""

from __future__ import annotations

import argparse
import os
import re
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote

import yaml


# Public V1 skill folders live under exactly these category names.
PUBLIC_CATEGORIES = {"agent-workflows", "engineering", "productivity"}

# These body sections preserve behavior that used to live in frontmatter.
REQUIRED_SECTIONS = ("## Dependencies", "## Output Contract")

# The normalized required frontmatter shape is:
# name, description, and metadata.goated-category.
REQUIRED_FRONTMATTER_KEYS = {"name", "description", "metadata"}

# Standard Agent Skills fields are allowed, but this repo does not rely on them.
# If they appear, the script asks for human review instead of failing.
OPTIONAL_REVIEW_KEYS = {"license", "compatibility"}
ALLOWED_FRONTMATTER_KEYS = REQUIRED_FRONTMATTER_KEYS | OPTIONAL_REVIEW_KEYS

# These were useful during early GOATED design, but issue 059 moved this
# behavior into Markdown body sections for wider agent compatibility.
BANNED_TOP_LEVEL_KEYS = {
    "category",
    "classification",
    "status",
    "triggers",
    "outputs",
    "depends_on",
    "adapters",
}

# VS Code supports these fields, but GOATED public skills stay framework-neutral.
VSCODE_ONLY_KEYS = {
    "argument-hint",
    "user-invocable",
    "disable-model-invocation",
    "context",
}

# Experimental invocation controls are intentionally out of scope for V1.
EXPERIMENTAL_KEYS = {"allowed-tools"}

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

# Regex helpers for specific mechanical checks. These intentionally favor clear,
# high-confidence matches over clever parsing.
MARKDOWN_LINK_RE = re.compile(r"!?\[[^\]]+\]\(([^)]+)\)")
HEADING_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
LEGACY_SCHEMA_LINE_RE = re.compile(
    r"^\s{0,4}(category|classification|status|triggers|outputs|depends_on|adapters):\s*",
    re.MULTILINE,
)

# These path-leak regexes catch obvious local user home-directory paths.
# They intentionally allow generic placeholders like C:/Users/.../skills.
WINDOWS_USER_PATH_RE = re.compile(
    r"\b[A-Za-z]:[\\/]+Users[\\/]+(?!\.{2,3}(?:[\\/]|$))"
    r"[A-Za-z0-9._-]+[\\/][^\s)>\"`]*"
)
POSIX_USER_PATH_RE = re.compile(
    r"(?<![\w])/(?:Users|home)/(?!\.{2,3}(?:/|$))[A-Za-z0-9._-]+/[^\s)>\"`]*"
)


@dataclass(frozen=True)
class Finding:
    """One validation message tied to a file and optional line number."""

    path: str
    message: str
    line: int | None = None

    def format(self) -> str:
        location = self.path if self.line is None else f"{self.path}:{self.line}"
        return f"{location}: {self.message}"


def parse_args() -> argparse.Namespace:
    """Parse the repo path so the same script can validate temp fixtures."""

    parser = argparse.ArgumentParser(
        description="Validate GOATED AI Skills schema and source-repo guardrails."
    )
    parser.add_argument(
        "--repo",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Repository root to validate. Defaults to this script's repo.",
    )
    return parser.parse_args()


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
        if path.suffix.lower() in PUBLIC_TEXT_SUFFIXES or path.name in PUBLIC_TEXT_NAMES
    ]


def find_skill_files(repo: Path) -> tuple[list[Path], list[Finding]]:
    """Find implemented skills and reject malformed SKILL.md locations."""

    skills_root = repo / "skills"
    if not skills_root.exists():
        return [], [Finding("skills", "missing skills directory")]

    skill_files = sorted(skills_root.rglob("SKILL.md"))
    errors: list[Finding] = []
    valid_files: list[Path] = []

    for path in skill_files:
        parts = path.relative_to(repo).parts
        # Implemented public skills are always exactly:
        # skills/<category>/<skill-name>/SKILL.md
        if len(parts) != 4 or parts[0] != "skills" or parts[3] != "SKILL.md":
            errors.append(
                Finding(
                    relative(path, repo),
                    "SKILL.md must live at skills/<category>/<skill-name>/SKILL.md",
                )
            )
            continue
        if parts[1] not in PUBLIC_CATEGORIES:
            errors.append(
                Finding(
                    relative(path, repo),
                    f"unknown public category {parts[1]!r}; expected one of {sorted(PUBLIC_CATEGORIES)}",
                )
            )
            continue
        valid_files.append(path)

    return valid_files, errors


def split_frontmatter(text: str, path_label: str) -> tuple[dict[str, object] | None, str, list[Finding]]:
    """Split a Markdown file into YAML frontmatter and Markdown body text."""

    lines = text.splitlines()
    # Some Windows editors write a UTF-8 BOM. lstrip keeps those files valid.
    if not lines or lines[0].lstrip("\ufeff").strip() != "---":
        return None, text, [Finding(path_label, "missing YAML frontmatter")]

    end_index = None
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end_index = index
            break

    if end_index is None:
        return None, text, [Finding(path_label, "unterminated YAML frontmatter")]

    yaml_text = "\n".join(lines[1:end_index])
    body = "\n".join(lines[end_index + 1 :])
    try:
        # safe_load parses normal YAML data without constructing Python objects.
        loaded = yaml.safe_load(yaml_text)
    except yaml.YAMLError as exc:
        return None, body, [Finding(path_label, f"frontmatter YAML parse error: {exc}")]

    if not isinstance(loaded, dict):
        return None, body, [Finding(path_label, "frontmatter must be a mapping")]

    return loaded, body, []


def validate_frontmatter(
    path: Path, repo: Path, frontmatter: dict[str, object]
) -> tuple[list[Finding], list[Finding]]:
    """Validate the normalized frontmatter contract for one implemented skill."""

    path_label = relative(path, repo)
    category = path.relative_to(repo).parts[1]
    errors: list[Finding] = []
    notes: list[Finding] = []

    keys = set(frontmatter)
    # Specific disallowed fields get specific messages. This helps a maintainer
    # understand whether a field is legacy GOATED, framework-specific, or simply
    # unknown.
    for key in sorted(keys & BANNED_TOP_LEVEL_KEYS):
        errors.append(Finding(path_label, f"banned GOATED legacy frontmatter key: {key}"))
    for key in sorted(keys & VSCODE_ONLY_KEYS):
        errors.append(Finding(path_label, f"VS Code-only frontmatter key is not allowed: {key}"))
    for key in sorted(keys & EXPERIMENTAL_KEYS):
        errors.append(Finding(path_label, f"experimental frontmatter key is not allowed: {key}"))
    special_disallowed_keys = BANNED_TOP_LEVEL_KEYS | VSCODE_ONLY_KEYS | EXPERIMENTAL_KEYS
    for key in sorted(keys - ALLOWED_FRONTMATTER_KEYS - special_disallowed_keys):
        errors.append(Finding(path_label, f"unexpected frontmatter key: {key}"))
    for key in sorted(keys & OPTIONAL_REVIEW_KEYS):
        notes.append(Finding(path_label, f"optional frontmatter key requires human review: {key}"))

    # Required scalar fields must exist and be useful for skill discovery.
    for key in ("name", "description"):
        value = frontmatter.get(key)
        if not isinstance(value, str) or not value.strip():
            errors.append(Finding(path_label, f"frontmatter {key!r} must be a non-empty string"))

    # metadata is allowed only for public category bookkeeping.
    metadata = frontmatter.get("metadata")
    if not isinstance(metadata, dict):
        errors.append(Finding(path_label, "frontmatter 'metadata' must be a mapping"))
        return errors, notes

    metadata_keys = set(metadata)
    for key in sorted(metadata_keys - {"goated-category"}):
        errors.append(Finding(path_label, f"metadata contains unexpected key: {key}"))

    # The category in metadata must agree with the folder path so copied skills
    # carry the same category label that the repo uses.
    goated_category = metadata.get("goated-category")
    if not isinstance(goated_category, str) or not goated_category.strip():
        errors.append(Finding(path_label, "metadata.goated-category must be a non-empty string"))
    elif goated_category not in PUBLIC_CATEGORIES:
        errors.append(
            Finding(
                path_label,
                f"metadata.goated-category {goated_category!r} is not one of {sorted(PUBLIC_CATEGORIES)}",
            )
        )
    elif goated_category != category:
        errors.append(
            Finding(
                path_label,
                f"metadata.goated-category {goated_category!r} must match category folder {category!r}",
            )
        )

    return errors, notes


def validate_required_sections(path: Path, repo: Path, body: str) -> list[Finding]:
    """Check for required Markdown sections in the skill body."""

    path_label = relative(path, repo)
    headings = {f"## {match.group(1).strip()}" for match in HEADING_RE.finditer(body)}
    return [
        Finding(path_label, f"missing required body section: {section}")
        for section in REQUIRED_SECTIONS
        if section not in headings
    ]


def normalize_markdown_target(raw_target: str) -> str:
    """Extract the path part from a Markdown link target."""

    target = raw_target.strip()
    # Markdown allows links like [x](<path with spaces.md>).
    if target.startswith("<"):
        end = target.find(">")
        if end != -1:
            target = target[1:end]
    else:
        # For ordinary links, anything after whitespace is a title.
        target = target.split()[0] if target.split() else ""
    return unquote(target.strip())


def is_external_or_anchor(target: str) -> bool:
    """Return True for targets this script should not check on disk."""

    if not target or target.startswith("#"):
        return True
    if re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", target):
        return True
    if target.startswith("//"):
        return True
    return False


def validate_markdown_links(path: Path, repo: Path, text: str) -> list[Finding]:
    """Fail on broken relative links from SKILL.md files."""

    errors: list[Finding] = []
    for match in MARKDOWN_LINK_RE.finditer(text):
        target = normalize_markdown_target(match.group(1))
        if is_external_or_anchor(target):
            continue
        target_without_fragment = target.split("#", 1)[0].split("?", 1)[0]
        if not target_without_fragment:
            continue
        if Path(target_without_fragment).is_absolute():
            continue
        resolved = (path.parent / target_without_fragment).resolve()
        if not resolved.exists():
            # Count newlines before the match to produce a 1-based line number.
            line = text.count("\n", 0, match.start()) + 1
            errors.append(
                Finding(
                    relative(path, repo),
                    f"relative Markdown link target does not exist: {target}",
                    line=line,
                )
            )
    return errors


def validate_forbidden_skill_files(skill_file: Path, repo: Path) -> list[Finding]:
    """Reject Codex-specific metadata files inside public skill folders."""

    skill_root = skill_file.parent
    errors: list[Finding] = []
    for path in sorted(skill_root.rglob("openai.yaml")):
        errors.append(Finding(relative(path, repo), "Codex openai.yaml files are not allowed in skill folders"))
    return errors


def scan_public_path_leaks(repo: Path) -> list[Finding]:
    """Find obvious local user paths in public text files."""

    errors: list[Finding] = []
    for path in iter_public_text_files(repo):
        text = read_text(path)
        for regex in (WINDOWS_USER_PATH_RE, POSIX_USER_PATH_RE):
            for match in regex.finditer(text):
                line = text.count("\n", 0, match.start()) + 1
                errors.append(
                    Finding(
                        relative(path, repo),
                        f"high-confidence local user path leak: {match.group(0)}",
                        line=line,
                    )
                )
    return errors


def scan_docs_schema_drift(repo: Path, skill_files: set[Path]) -> list[Finding]:
    """Report old schema-looking lines in docs without failing the command."""

    drift: list[Finding] = []
    for path in iter_public_text_files(repo):
        # Skill files are validated strictly elsewhere. This pass is only for
        # prose docs, issue files, examples, and other public text.
        if path in skill_files or path.suffix.lower() not in {".md", ".mdx", ".rst", ".txt"}:
            continue
        text = read_text(path)
        for match in LEGACY_SCHEMA_LINE_RE.finditer(text):
            line = text.count("\n", 0, match.start()) + 1
            drift.append(
                Finding(
                    relative(path, repo),
                    f"possible legacy frontmatter example or drift: {match.group(1)}:",
                    line=line,
                )
            )
    return drift


def validate_skills(repo: Path) -> tuple[list[Finding], list[Finding], list[Finding], int]:
    """Run all validation phases and return grouped findings."""

    skill_files, errors = find_skill_files(repo)
    review_notes: list[Finding] = []

    for path in skill_files:
        text = read_text(path)
        path_label = relative(path, repo)

        # A malformed frontmatter block should not stop later body checks. The
        # script returns the body text it can recover, then continues.
        frontmatter, body, frontmatter_errors = split_frontmatter(text, path_label)
        errors.extend(frontmatter_errors)
        if frontmatter is not None:
            frontmatter_errors, frontmatter_notes = validate_frontmatter(path, repo, frontmatter)
            errors.extend(frontmatter_errors)
            review_notes.extend(frontmatter_notes)
        errors.extend(validate_required_sections(path, repo, body))
        errors.extend(validate_markdown_links(path, repo, text))
        errors.extend(validate_forbidden_skill_files(path, repo))

    # Public-boundary checks scan the whole public text surface, not just skills.
    errors.extend(scan_public_path_leaks(repo))

    # Docs drift is informational in issue 060, so it is returned separately.
    drift = scan_docs_schema_drift(repo, set(skill_files))
    return errors, review_notes, drift, len(skill_files)


def print_findings(title: str, findings: list[Finding], limit: int = 30) -> None:
    """Print a readable finding group with a cap for noisy failures."""

    print(f"\n{title}: {len(findings)}")
    for finding in findings[:limit]:
        print(f"- {finding.format()}")
    remaining = len(findings) - limit
    if remaining > 0:
        print(f"- ... {remaining} more")


def main() -> int:
    """Program entrypoint used by `uv run python scripts/validate_skills.py`."""

    args = parse_args()
    repo = args.repo.expanduser().resolve()
    if not repo.exists() or not repo.is_dir():
        raise SystemExit(f"Repo path does not exist or is not a directory: {repo}")

    errors, review_notes, drift, skill_count = validate_skills(repo)

    # Only blocking errors affect the exit code. Human-review notes and docs
    # drift are visible, but they do not fail the command by design.
    if errors:
        print(f"GOATED skill validation failed for {skill_count} implemented skills.")
        print_findings("Blocking errors", errors)
    else:
        print(f"GOATED skill validation passed for {skill_count} implemented skills.")

    if review_notes:
        print_findings("Human-review notes", review_notes)
    else:
        print("\nHuman-review notes: 0")

    if drift:
        print_findings("Report-only docs/example schema drift", drift)
    else:
        print("\nReport-only docs/example schema drift: 0")

    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
