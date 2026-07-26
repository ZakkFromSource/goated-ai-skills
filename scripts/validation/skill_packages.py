"""Validate installable skill packages and their public source boundaries."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote

import yaml

from .shared import (
    Finding,
    HEADING_RE,
    iter_public_text_files,
    read_text,
    relative,
)


# Public V1 skill folders live under exactly these category names.
PUBLIC_CATEGORIES = {"agent-workflows", "engineering", "productivity"}

# These body sections preserve behavior that used to live in frontmatter.
REQUIRED_SECTIONS = ("## Dependencies", "## Output Contract")

# The normalized required frontmatter shape is:
# name, description, and metadata.goated-category.
REQUIRED_FRONTMATTER_KEYS = {"name", "description", "metadata"}

# Standard Agent Skills fields are allowed, but this repo does not rely on them.
# If they appear, the validator asks for human review instead of failing.
OPTIONAL_REVIEW_KEYS = {"license", "compatibility"}
ALLOWED_FRONTMATTER_KEYS = REQUIRED_FRONTMATTER_KEYS | OPTIONAL_REVIEW_KEYS

# These fields were useful during early design but are no longer public schema.
BANNED_TOP_LEVEL_KEYS = {
    "category",
    "classification",
    "status",
    "triggers",
    "outputs",
    "depends_on",
    "adapters",
}

# VS Code supports these fields, but public skills stay framework-neutral.
VSCODE_ONLY_KEYS = {
    "argument-hint",
    "user-invocable",
    "disable-model-invocation",
    "context",
}

# Experimental invocation controls are intentionally out of scope.
EXPERIMENTAL_KEYS = {"allowed-tools"}

MARKDOWN_LINK_RE = re.compile(r"!?\[[^\]]+\]\(([^)]+)\)")
LEGACY_SCHEMA_LINE_RE = re.compile(
    r"^\s{0,4}(category|classification|status|triggers|outputs|depends_on|"
    r"adapters):\s*",
    re.MULTILINE,
)
WINDOWS_USER_PATH_RE = re.compile(
    r"\b[A-Za-z]:[\\/]+Users[\\/]+(?!\.{2,3}(?:[\\/]|$))"
    r"[A-Za-z0-9._-]+[\\/][^\s)>\"`]*"
)
POSIX_USER_PATH_RE = re.compile(
    r"(?<![\w])/(?:Users|home)/(?!\.{2,3}(?:/|$))"
    r"[A-Za-z0-9._-]+/[^\s)>\"`]*"
)


@dataclass(frozen=True)
class SkillPackageValidation:
    """Grouped findings and discovered files from skill-package validation."""

    errors: list[Finding]
    review_notes: list[Finding]
    drift: list[Finding]
    skill_files: tuple[Path, ...]


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
                    "SKILL.md must live at "
                    "skills/<category>/<skill-name>/SKILL.md",
                )
            )
            continue
        if parts[1] not in PUBLIC_CATEGORIES:
            errors.append(
                Finding(
                    relative(path, repo),
                    f"unknown public category {parts[1]!r}; "
                    f"expected one of {sorted(PUBLIC_CATEGORIES)}",
                )
            )
            continue
        valid_files.append(path)

    return valid_files, errors


def split_frontmatter(
    text: str,
    path_label: str,
) -> tuple[dict[str, object] | None, str, list[Finding]]:
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
        return None, body, [
            Finding(path_label, f"frontmatter YAML parse error: {exc}")
        ]

    if not isinstance(loaded, dict):
        return None, body, [
            Finding(path_label, "frontmatter must be a mapping")
        ]

    return loaded, body, []


def validate_frontmatter(
    path: Path,
    repo: Path,
    frontmatter: dict[str, object],
) -> tuple[list[Finding], list[Finding]]:
    """Validate the normalized frontmatter contract for one implemented skill."""

    path_label = relative(path, repo)
    category = path.relative_to(repo).parts[1]
    errors: list[Finding] = []
    notes: list[Finding] = []

    keys = set(frontmatter)
    # Specific disallowed fields get specific messages so maintainers can tell
    # legacy GOATED fields from framework-specific and unknown fields.
    for key in sorted(keys & BANNED_TOP_LEVEL_KEYS):
        errors.append(
            Finding(
                path_label,
                f"banned GOATED legacy frontmatter key: {key}",
            )
        )
    for key in sorted(keys & VSCODE_ONLY_KEYS):
        errors.append(
            Finding(
                path_label,
                f"VS Code-only frontmatter key is not allowed: {key}",
            )
        )
    for key in sorted(keys & EXPERIMENTAL_KEYS):
        errors.append(
            Finding(
                path_label,
                f"experimental frontmatter key is not allowed: {key}",
            )
        )
    special_disallowed_keys = (
        BANNED_TOP_LEVEL_KEYS | VSCODE_ONLY_KEYS | EXPERIMENTAL_KEYS
    )
    for key in sorted(
        keys - ALLOWED_FRONTMATTER_KEYS - special_disallowed_keys
    ):
        errors.append(Finding(path_label, f"unexpected frontmatter key: {key}"))
    for key in sorted(keys & OPTIONAL_REVIEW_KEYS):
        notes.append(
            Finding(
                path_label,
                f"optional frontmatter key requires human review: {key}",
            )
        )

    for key in ("name", "description"):
        value = frontmatter.get(key)
        if not isinstance(value, str) or not value.strip():
            errors.append(
                Finding(
                    path_label,
                    f"frontmatter {key!r} must be a non-empty string",
                )
            )

    metadata = frontmatter.get("metadata")
    if not isinstance(metadata, dict):
        errors.append(
            Finding(path_label, "frontmatter 'metadata' must be a mapping")
        )
        return errors, notes

    metadata_keys = set(metadata)
    for key in sorted(metadata_keys - {"goated-category"}):
        errors.append(
            Finding(path_label, f"metadata contains unexpected key: {key}")
        )

    # Metadata must agree with the folder so copied skills retain their category.
    goated_category = metadata.get("goated-category")
    if not isinstance(goated_category, str) or not goated_category.strip():
        errors.append(
            Finding(
                path_label,
                "metadata.goated-category must be a non-empty string",
            )
        )
    elif goated_category not in PUBLIC_CATEGORIES:
        errors.append(
            Finding(
                path_label,
                f"metadata.goated-category {goated_category!r} "
                f"is not one of {sorted(PUBLIC_CATEGORIES)}",
            )
        )
    elif goated_category != category:
        errors.append(
            Finding(
                path_label,
                f"metadata.goated-category {goated_category!r} "
                f"must match category folder {category!r}",
            )
        )

    return errors, notes


def validate_required_sections(
    path: Path,
    repo: Path,
    body: str,
) -> list[Finding]:
    """Check for required Markdown sections in the skill body."""

    path_label = relative(path, repo)
    headings = {
        f"## {match.group(1).strip()}" for match in HEADING_RE.finditer(body)
    }
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
    """Return whether this target should not be checked on disk."""

    if not target or target.startswith("#"):
        return True
    if re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", target):
        return True
    if target.startswith("//"):
        return True
    return False


def validate_markdown_links(
    path: Path,
    repo: Path,
    text: str,
) -> list[Finding]:
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
            line = text.count("\n", 0, match.start()) + 1
            errors.append(
                Finding(
                    relative(path, repo),
                    f"relative Markdown link target does not exist: {target}",
                    line=line,
                )
            )
    return errors


def validate_forbidden_skill_files(
    skill_file: Path,
    repo: Path,
) -> list[Finding]:
    """Reject Codex-specific metadata files inside public skill folders."""

    return [
        Finding(
            relative(path, repo),
            "Codex openai.yaml files are not allowed in skill folders",
        )
        for path in sorted(skill_file.parent.rglob("openai.yaml"))
    ]


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


def scan_docs_schema_drift(
    repo: Path,
    skill_files: set[Path],
) -> list[Finding]:
    """Report old schema-looking lines in docs without failing the command."""

    drift: list[Finding] = []
    for path in iter_public_text_files(repo):
        # Skill files are validated strictly elsewhere. This pass is only for
        # prose docs, issue files, examples, and other public text.
        if path in skill_files or path.suffix.lower() not in {
            ".md",
            ".mdx",
            ".rst",
            ".txt",
        }:
            continue
        text = read_text(path)
        for match in LEGACY_SCHEMA_LINE_RE.finditer(text):
            line = text.count("\n", 0, match.start()) + 1
            drift.append(
                Finding(
                    relative(path, repo),
                    "possible legacy frontmatter example or drift: "
                    f"{match.group(1)}:",
                    line=line,
                )
            )
    return drift


def validate_canonical_architecture_references(repo: Path) -> list[Finding]:
    """Reject deprecated architecture names from active runtime and user docs."""

    deprecated_names = {
        "plan-codebase-architecture": "design-codebase-architecture",
        "improve-codebase-architecture": "review-codebase-architecture",
    }
    active_paths = [
        repo / "README.md",
        repo / "docs" / "how-to-use.md",
        repo / "docs" / "install.md",
        repo / "stack" / "AGENTS.md",
    ]
    active_paths.extend(sorted((repo / "skills").rglob("*.md")))

    errors: list[Finding] = []
    for path in active_paths:
        if not path.exists():
            continue
        text = read_text(path)
        for deprecated_name, canonical_name in deprecated_names.items():
            for match in re.finditer(re.escape(deprecated_name), text):
                line = text.count("\n", 0, match.start()) + 1
                errors.append(
                    Finding(
                        relative(path, repo),
                        "active reference uses deprecated architecture skill "
                        f"name {deprecated_name!r}; use {canonical_name!r}",
                        line=line,
                    )
                )
    return errors


def validate_skill_packages(repo: Path) -> SkillPackageValidation:
    """Validate all installable skill packages and public source boundaries."""

    skill_files, errors = find_skill_files(repo)
    review_notes: list[Finding] = []

    for path in skill_files:
        text = read_text(path)
        path_label = relative(path, repo)

        # Malformed frontmatter should not stop later body checks. The parser
        # returns any recoverable body so the remaining package checks continue.
        frontmatter, body, frontmatter_errors = split_frontmatter(
            text,
            path_label,
        )
        errors.extend(frontmatter_errors)
        if frontmatter is not None:
            field_errors, field_notes = validate_frontmatter(
                path,
                repo,
                frontmatter,
            )
            errors.extend(field_errors)
            review_notes.extend(field_notes)
        errors.extend(validate_required_sections(path, repo, body))
        errors.extend(validate_markdown_links(path, repo, text))
        errors.extend(validate_forbidden_skill_files(path, repo))

    errors.extend(scan_public_path_leaks(repo))
    errors.extend(validate_canonical_architecture_references(repo))
    drift = scan_docs_schema_drift(repo, set(skill_files))

    return SkillPackageValidation(
        errors=errors,
        review_notes=review_notes,
        drift=drift,
        skill_files=tuple(skill_files),
    )
