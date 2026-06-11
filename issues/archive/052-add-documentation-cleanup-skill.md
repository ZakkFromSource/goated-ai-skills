## Parent PRD

No separate parent PRD. This issue is based on the user-approved 2026-05-31 plan for adding `documentation-cleanup` as a post-V1 improvement skill.

## Type

AFK

## What to build

Implement `documentation-cleanup` under `skills/engineering/`.

The skill should audit, tidy, consolidate, and optimize target-project documentation trees, especially `docs/`, `docs/agents/`, and root routing docs such as `README.md`, `CONTEXT.md`, `AGENT.md` / `AGENTS.md`, `CLAUDE.md`, project skill maps, and obvious progress/status docs when project conventions put them in scope.

The default behavior must be audit-first: inventory docs, classify roles, report findings, and propose a cleanup plan before editing. File moves, deletes, archives, and source-of-truth changes require explicit approval or strong project convention evidence.

## Recommended first reads

- `AGENT.md`
- `CONTEXT.md`
- `skills/README.md`
- `skills/engineering/README.md`
- `skills/agent-workflows/framework-agnostic-skill-creator/SKILL.md`
- `skills/agent-workflows/framework-agnostic-skill-creator/references/skill-evaluation.md`
- `skills/engineering/doc-sync/SKILL.md`
- `skills/engineering/documentation-writer/SKILL.md`
- `skills/agent-workflows/context-matrix-map/SKILL.md`
- `skills/agent-workflows/project-context-calibration/SKILL.md`
- `skills/agent-workflows/project-standards-calibration/SKILL.md`
- `skills/agent-workflows/agent-instructions-integrator/SKILL.md`
- `docs/how-to-use.md`
- `README.md`

## Relevant source links

- `skills/README.md` - lean schema, support-file policy, implementation boundary, and delegation contract.
- `CONTEXT.md` - source repo, installed skill, target project, docs/agents, public-safe, and durable artifact language.
- `skills/engineering/doc-sync/SKILL.md` - companion boundary for changed-behavior documentation drift.
- `skills/engineering/documentation-writer/SKILL.md` - companion boundary for planned durable docs and substantial guide authoring.
- `skills/agent-workflows/context-matrix-map/SKILL.md` - companion for future-agent source maps.
- `skills/agent-workflows/project-context-calibration/SKILL.md` - companion for project language and root context cleanup.
- `skills/agent-workflows/project-standards-calibration/SKILL.md` - companion for standards profiles and command expectations.
- `skills/agent-workflows/agent-instructions-integrator/SKILL.md` - companion for thin adapter and installed-skill routing repairs.
- `skills/agent-workflows/framework-agnostic-skill-creator/references/skill-evaluation.md` - evaluation expectations for a discipline-heavy skill.

## Acceptance criteria

- [x] `skills/engineering/documentation-cleanup/SKILL.md` exists and follows the lean schema.
- [x] The skill is portable, self-contained after installation, and does not depend on this source repo's root docs at runtime.
- [x] Audit, plan, and implementation modes are defined.
- [x] Audit mode is the default for review, planning, brainstorm, and ambiguous cleanup requests.
- [x] The skill covers `docs/`, `docs/agents/`, root README/context files, agent instruction adapters, progress/status docs, and issue/workbench docs only when project conventions put them in scope.
- [x] The skill classifies docs by role before recommending cleanup.
- [x] Output includes inventory, doc roles, findings, proposed actions, approval-needed items, edits made, verification, skipped checks, companion routes, and residual risk.
- [x] Moves, deletes, archives, immutable-record edits, and source-of-truth changes are gated by explicit approval or strong project convention evidence.
- [x] An optional read-only stdlib helper exists at `skills/engineering/documentation-cleanup/scripts/inventory_docs.py` with interface `python scripts/inventory_docs.py --repo <path> [--json]`.
- [x] The helper reports doc paths, role hints, line counts, headings, link counts, last-updated markers, and privacy/path risk hints without writing files.
- [x] The skill explains fallback manual inventory with `rg --files` and targeted reads when Python or the helper is unavailable.
- [x] Long taxonomy, checklist, and report-template guidance lives in directly linked `references/` files.
- [x] Public-boundary review confirms no private project names, personal paths, credentials, raw private notes, private workflow assumptions, or tool-specific automation claims are included.
- [x] `README.md`, `docs/how-to-use.md`, and `skills/engineering/README.md` list the skill only after implementation is complete.

## Expected proof

- Manual schema review of `skills/engineering/documentation-cleanup/SKILL.md`.
- Manual review that every support-file and script link exists and has a read/run condition.
- Run `python skills/engineering/documentation-cleanup/scripts/inventory_docs.py --repo . --json` and confirm it exits successfully without writing files.
- Targeted `rg` checks for `documentation-cleanup`, private path patterns, stale automation wording, deletion/archival guardrails, and catalog consistency.
- Manual scenario review for:
  - a GOATED-style repo with `docs/agents/context-matrix.md` and `project-standards.md`;
  - a project with `docs/agents/architecture-map.md`, external-doc lookup notes, and large duplicated progress evidence;
  - a project with no `docs/agents/` but rich root agent instructions and `docs/context-map.md`.
- Public-boundary pass.

## Blocked by

- None - the user approved the scope and asked to implement it.

## User stories addressed

- As an agent user, I can ask for a docs hygiene audit and receive a role-aware cleanup plan before edits happen.
- As an agent user, I can safely tidy `docs/` and agent docs without accidental deletes, broad moves, or source-of-truth rewrites.
- As a maintainer, I can keep documentation cleanup separate from changed-behavior `doc-sync` and planned `documentation-writer` authoring.

## Implementation route

- Use `framework-agnostic-skill-creator` to create the skill package in GOATED shape.
- Use `doc-sync` after implementation because public catalogs and operator guidance change.
- Use `verification-before-completion` before claiming the skill, script, and docs are implemented.

## Scope exclusions

- Do not add runtime bootstrap, background optimization, installer automation, hooks, generated persistent indexes, or automatic file deletion.
- Do not claim every project must use `docs/agents/`, root `CONTEXT.md`, ADRs, or GOATED artifact conventions.
- Do not make the inventory helper rewrite docs, follow symlinks, inspect dependency folders, or crawl private scratch folders by default.
- Do not perform full code/docs drift verification inside this skill unless routed to companion skills.
- Do not replace `doc-sync`, `documentation-writer`, `context-matrix-map`, `project-context-calibration`, `project-standards-calibration`, or `agent-instructions-integrator`.
