## Parent PRD

No separate parent PRD. This issue follows the completed compatibility cleanup in `issues/archive/059-normalize-skill-frontmatter-for-agent-compatibility.md`.

## Type

AFK

## What to build

Add read-only local validator tooling that locks in the normalized GOATED skill schema from issue `059`.

The first implementation should add:

- root `pyproject.toml`
- root `uv.lock`
- `scripts/validate_skills.py`

The validator must run through `uv`:

```bash
uv run python scripts/validate_skills.py
```

It should enforce strict mechanical checks for implemented public skills, report docs/example drift without failing, and avoid subjective prose-quality checks.

## Grill decisions

| Decision | Outcome |
| --- | --- |
| Enforcement level | Manual local validator script only; CI is out of scope. |
| Strictness | Strict for mechanical schema and structure rules; subjective writing quality stays review-enforced. |
| Docs/examples | Implemented skill violations fail; docs/example drift is report-only. |
| Runtime/tooling | Use `uv` so validation runs inside a managed environment. |
| Project files | Add root `pyproject.toml` and `uv.lock`. |
| YAML parsing | Use `pyyaml`; do not maintain an ad hoc frontmatter parser. |
| Implemented skill discovery | Blocking validation applies to exactly `skills/<public-category>/<skill-name>/SKILL.md`. |
| Support-file checks | Fail on broken relative Markdown links from `SKILL.md`; do not check orphan support files yet. |
| Public-boundary scan | Include a narrow high-confidence local path leak check. |
| Mutation | Read-only only; no `--fix` mode. |

## Recommended first reads

- `AGENT.md`
- `CONTEXT.md`
- `skills/README.md`
- `docs/agents/context-matrix.md`
- `docs/agents/project-standards.md`
- `issues/archive/059-normalize-skill-frontmatter-for-agent-compatibility.md`
- `skills/agent-workflows/framework-agnostic-skill-creator/SKILL.md`
- `skills/engineering/verification-before-completion/SKILL.md`

## Relevant source links

- `skills/README.md` - current lean schema, body-section, dependency, delegation, and support-file standards.
- `CONTEXT.md` - definitions for lean schema, installed skills, public categories, support files, and public-safe boundaries.
- `docs/agents/project-standards.md` - current standards profile and enforcement levels.
- `docs/agents/context-matrix.md` - source-routing guidance and current lack of root tooling.
- `issues/archive/059-normalize-skill-frontmatter-for-agent-compatibility.md` - migration decisions, accepted exclusions, proof expectations, and follow-up candidate for validator tooling.

## Acceptance criteria

- [ ] Root `pyproject.toml` is added for repo maintenance tooling.
- [ ] Root `uv.lock` is added and checked in.
- [ ] `pyproject.toml` declares only the dependencies needed for this issue, expected to be `pyyaml`.
- [ ] `scripts/validate_skills.py` is added.
- [ ] The validator is read-only and does not modify files.
- [ ] The documented command is `uv run python scripts/validate_skills.py`.
- [ ] The validator discovers implemented skills as exactly `skills/<category>/<skill-name>/SKILL.md`.
- [ ] Valid public categories are exactly `agent-workflows`, `engineering`, and `productivity`.
- [ ] The validator fails if any `SKILL.md` under `skills/` is outside the expected two-level implemented-skill path shape.
- [ ] The validator fails if an implemented skill is missing YAML frontmatter.
- [ ] The validator fails if implemented skill frontmatter cannot be parsed as YAML.
- [ ] The validator fails if implemented skill frontmatter is not a mapping.
- [ ] The validator fails if top-level `name` is missing, empty, or not a string.
- [ ] The validator fails if top-level `description` is missing, empty, or not a string.
- [ ] The validator fails if top-level `metadata` is missing or not a mapping.
- [ ] The validator fails if `metadata.goated-category` is missing, empty, not a string, or not one of the valid public categories.
- [ ] The validator fails if `metadata.goated-category` does not match the category folder.
- [ ] The validator fails if `metadata` contains keys other than `goated-category`.
- [ ] The validator fails on banned GOATED legacy top-level fields: `category`, `classification`, `status`, `triggers`, `outputs`, `depends_on`, and `adapters`.
- [ ] The validator fails on VS Code-only top-level fields such as `argument-hint`, `user-invocable`, `disable-model-invocation`, and `context`.
- [ ] The validator fails on experimental `allowed-tools`.
- [ ] The validator fails on unexpected top-level frontmatter fields outside `name`, `description`, `metadata`, optional `license`, and optional `compatibility`.
- [ ] The validator reports optional `license` or `compatibility` fields as requiring human review.
- [ ] The validator fails if an implemented skill lacks `## Dependencies`.
- [ ] The validator fails if an implemented skill lacks `## Output Contract`.
- [ ] The validator fails if a relative Markdown link from an implemented `SKILL.md` points to a missing file.
- [ ] The validator ignores external URLs for link-existence checks.
- [ ] The validator does not fail on orphaned support files in `references/`, `scripts/`, or `assets/`.
- [ ] The validator fails if any implemented skill folder contains Codex `agents/openai.yaml`.
- [ ] The validator fails if any implemented skill folder contains `openai.yaml`.
- [ ] The validator includes a narrow public-boundary path-leak check for high-confidence absolute local user paths in tracked public surfaces.
- [ ] Generic `%USERPROFILE%` references remain allowed.
- [ ] `.local/` references remain allowed when describing ignored local artifacts and are not treated as runtime dependencies.
- [ ] Docs/example scans for old schema drift are report-only and do not change the exit code when implemented skill checks pass.
- [ ] The validator prints clear file-specific errors for blocking failures.
- [ ] The validator prints a compact pass summary when no blocking failures are found.
- [ ] The validator exits nonzero when blocking failures are found.
- [ ] The validator exits zero when only report-only docs/example drift is found.
- [ ] No GitHub Actions workflow, CI hook, pre-commit hook, background automation, generated manifest, installer automation, token dashboard, eval harness, or formatter/linter framework is added.
- [ ] No committed virtual environment, cache, temporary fixture, or generated local scratch directory is added.
- [ ] Docs are updated only where needed to mention the validator command and tooling expectations.

## Expected proof

- Run `uv run python scripts/validate_skills.py` and record the result.
- Show the validator reports all current implemented skills as passing blocking checks.
- Show the validator reports docs/example drift separately from blocking failures, even if the current report has no drift.
- Verify the command exits `0` on the current repo state.
- Verify at least one blocking failure path is exercised with a temporary untracked fixture, temporary copied repo root, or tightly scoped manual test, and do not commit that fixture.
- Run `git status --short` before closeout and confirm only intended tracked files are changed.
- Run `git diff --check`.
- Manually inspect the script for read-only behavior and no private path leaks.
- Use `verification-before-completion` before claiming the issue is implemented, passing, or ready for review.

## Blocked by

- None - can start immediately.

## User stories addressed

- As a GOATED skill maintainer, I can run one local command to catch schema drift before committing skill changes.
- As a future skill author, I get clear errors when a skill recreates old rich frontmatter.
- As a reviewer, I can separate blocking implemented-skill violations from report-only docs/example drift.
- As a public repo maintainer, I can catch obvious local path leaks before they reach public docs.

## Implementation route

- Start by reading this issue, the recommended first reads, and current `git status --short`.
- Use `uv` to create the root Python tooling surface and lock dependency versions.
- Keep the validator implementation small, readable, and standard-library-first except for `pyyaml`.
- Prefer `pathlib`, explicit path predicates, and clear error objects over shell-dependent logic.
- Parse frontmatter with `yaml.safe_load`.
- Treat implemented-skill checks as blocking errors.
- Treat docs/example old-schema scans as report-only warnings or informational findings.
- Keep exact validation messages stable enough for humans to act on; no machine-readable output format is required in this slice.
- Keep implementation and verification public-safe.

## Scope exclusions

- Do not add CI.
- Do not add GitHub Actions workflows.
- Do not add pre-commit hooks.
- Do not add an auto-fix mode.
- Do not mutate skill files.
- Do not validate installed copies under user-home agent directories.
- Do not scan ignored `.local/` content.
- Do not add broad secret scanning.
- Do not enforce prose quality, description quality, line counts, token counts, or style tone.
- Do not fail on docs/example drift in this first issue.
- Do not check orphaned support files.
- Do not add a generated global skill manifest.
- Do not add installer automation.
- Do not add runtime bootstrap or adapter automation.
- Do not add Codex `agents/openai.yaml`.
- Do not add VS Code-specific fields.
- Do not add `allowed-tools`.

## Implementation notes

- The purpose is to make the issue `059` schema rules executable without making this repo depend on CI yet.
- Keep the command local and boring. The first win is reliable drift detection, not a full tooling platform.
- A future issue can add CI after this script proves stable.
- A future issue can add richer support-file hygiene if broken or orphaned references become a real maintenance problem.
- A future issue can add stricter docs drift enforcement if report-only findings prove low-noise.

## Implementation evidence

- Added root `pyproject.toml`, root `uv.lock`, and `scripts/validate_skills.py`.
- Added `pyyaml` as the only project dependency.
- Added `.gitignore` entries for `.venv/`, Python bytecode, and local Python cache directories.
- Updated `skills/README.md`, `README.md`, `docs/agents/context-matrix.md`, and `docs/agents/project-standards.md` with the validator command and tooling expectations.
- `uv run python scripts\validate_skills.py` passed on the current repo: 30 implemented skills checked, 0 human-review notes, 0 report-only docs/example schema drift.
- `uv run python -m py_compile scripts\validate_skills.py` passed.
- Temporary bad-skill fixture with legacy `category` frontmatter exited `1` as expected and reported blocking schema errors.
- Temporary docs-drift fixture exited `0` as expected and reported report-only schema drift separately.
- Temporary local-path fixture exited `1` as expected and reported a high-confidence public-boundary path leak.
- Temporary broken relative-link fixture exited `1` as expected and reported the missing `SKILL.md` link target.
- `git diff --check` passed with line-ending warnings only.
- Out-of-scope automation scan found no new CI, pre-commit hook, token dashboard, generated manifest, installer automation, or formatter/linter framework.
