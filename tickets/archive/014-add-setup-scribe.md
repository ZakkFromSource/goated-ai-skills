# Ticket 014: Add Setup Scribe

## Parent Spec

`docs/specs/2026-07-26-setup-scribe.md`

## Type

AFK

## Work State

Completed and archived on 2026-07-26.

## What To Build

Add `setup-scribe` as a public, framework-agnostic productivity skill that
preserves the verified path required to recreate a project's working
environment.

Deliver one coherent vertical slice containing the installed skill package,
its directly linked references, integrated-stack routing and registry metadata,
behavioral fixtures, validation coverage, and synchronized public guidance.
Scribe must work both as a conditional V2 reproducibility gate and as a
self-contained individually installed skill.

The skill must own four modes:

- capture project-relevant setup changes during current work;
- backfill an existing setup using honest evidence labels;
- audit the current setup recipe for drift;
- propose or generate safe, Bash-first replay automation.

Keep the setup recipe project-first, tracked, ordered, secret-safe, and
source-of-truth aware. Do not turn Scribe into passive monitoring, a personal
machine journal, a duplicate configuration system, or an automation executor.

## Recommended First Reads

- `AGENT.md` — source-repository workflow, public boundary, and ticket rules.
- `CONTEXT.md` — V2 vocabulary, installed-skill boundary, artifact model,
  categories, and quality bar.
- `docs/specs/2026-07-26-setup-scribe.md` — complete accepted product contract
  and acceptance criteria.
- `docs/agents/context-matrix.md` — targeted source routing for this repository.
- `docs/agents/project-standards.md` — enforced and review-based standards and
  acceptance commands.
- `skills/agent-workflows/framework-agnostic-skill-creator/SKILL.md` — GOATED
  skill creation, support-file, portability, and evaluation procedure.
- `skills/agent-workflows/framework-agnostic-skill-creator/references/skill-evaluation.md`
  — RED/GREEN pressure-scenario and forward-test expectations.
- `stack/AGENTS.md` — shared approval, evidence, safety, routing, and closeout
  behavior that Scribe must reuse.
- `stack/goated-stack.yaml` and
  `stack/schemas/stack-registry.schema.json` — registry and signal contracts.
- `skills/engineering/doc-sync/SKILL.md`,
  `skills/engineering/documentation-writer/SKILL.md`,
  `skills/productivity/learning-capture/SKILL.md`, and
  `skills/agent-workflows/handoff/SKILL.md` — neighboring ownership boundaries.
- `scripts/validate_skills.py` and `tests/test_validate_skills.py` — current
  structural, registry, fixture, link, and public-boundary validation.
- `tickets/archive/013-split-validator-by-concern.md` — validator refactor scope;
  avoid overlapping validator writes if that ticket is in progress.

## Relevant Source Links

- `docs/specs/2026-07-25-goated-ai-skills-v2.md`
- `skills/README.md`
- `skills/productivity/README.md`
- `README.md`
- `docs/how-to-use.md`
- `docs/install.md`
- `stack/fixtures/`
- `.github/workflows/validate.yml`

## Acceptance Criteria

- [x] `skills/productivity/setup-scribe/SKILL.md` exists, follows the lean
      schema, stays within the source-repo soft line budget, and remains useful
      without root repository files.
- [x] The skill implements capture, backfill, audit, and automate modes with
      clear activation, stop, approval, fallback, and compact closeout behavior.
- [x] Material setup steps distinguish `verified`, `source-backed`, and
      `unverified` evidence without turning reconstruction, static inspection,
      or generated automation into false proof.
- [x] The workflow maintains one tracked, ordered current recipe, uses
      verified-ignored or temporary staging safely, and creates chronological
      history only when requested or established by project convention.
- [x] Recipe guidance is project-first, platform- and scope-aware, secret-safe,
      verification-oriented, and adaptable to an existing project convention.
- [x] The workflow references manifests, lockfiles, environment templates,
      containers, toolchain files, task runners, and other declarative sources
      instead of duplicating their owned facts.
- [x] Audit mode classifies findings as `current`, `stale`, `missing`, `moved`,
      `unverifiable`, or `obsolete` using fresh project evidence.
- [x] Automation prefers existing declarative configuration, then portable
      POSIX-conscious Bash, then narrowly scoped platform-native helpers, with
      BAT and manual fallbacks used only when justified.
- [x] Generated automation checks prerequisites, failure behavior, action
      scope, rerun safety, secrets, preview feasibility, verification, and
      manual gaps; it is neither executed nor called verified without separate
      approval and evidence.
- [x] `references/setup-recipe-template.md`,
      `references/automation-and-safety.md`, and
      `references/pressure-scenarios.md` exist, are directly linked with clear
      read conditions, and contain the detailed guidance removed from
      `SKILL.md`.
- [x] The first version adds no bundled executable helper unless implementation
      evidence reveals a stable project-agnostic operation and the scope change
      is explicitly approved.
- [x] `stack/goated-stack.yaml`, its schema or validator where required, and the
      shared routing policy represent Scribe's conditional reproducibility
      gate, domains, profile eligibility, accepted and emitted signals, and
      standalone boundary without copying the specialist procedure.
- [x] Focused fixtures cover live capture, mixed-evidence backfill, drift
      repair, Bash-first automation with a native helper, secret rejection,
      existing-source ownership, unrelated personal-setting exclusion, and a
      compact no-impact route.
- [x] Public catalogs and operator guidance list Scribe only after
      implementation and distinguish it from `doc-sync`,
      `documentation-writer`, `learning-capture`, and `handoff`.
- [x] The repository validator, unit suite, V1/V2 context comparison, targeted
      source scans, manual Markdown review, and diff checks pass with fresh
      evidence or report an explicit blocker or residual risk.
- [x] RED/GREEN forward evaluation from raw project evidence demonstrates that
      the skill improves setup capture or reconstruction without leaking the
      intended answer; observed rationalizations are addressed or recorded as
      residual risk.

## Expected Proof

- A RED baseline and GREEN forward test following
  `framework-agnostic-skill-creator/references/skill-evaluation.md`, using raw
  setup artifacts and no leaked expected answer.
- Focused fixture and validator tests proving route selection, signal behavior,
  evidence classification, secret handling, source ownership, and automation
  boundaries.
- Fresh successful output from:
  - `uv run python scripts/validate_skills.py`
  - `uv run python -m unittest discover -s tests -v`
  - `uv run python scripts/compare_v1_v2_context.py`
- Targeted `rg` scans for `setup-scribe`, `reproducibility-impact`, stale
  planned wording, broken ownership boundaries, private paths, secret examples,
  and unsupported automation claims.
- Manual review that every local reference exists, each read condition is
  clear, the installed folder is self-contained, and public output contains no
  private or sensitive material.
- Manual Markdown review because this repository has no configured Markdown
  formatter or linter.
- Fresh `git status --short`, diff inspection, and whitespace checks covering
  the complete ticket scope.

## Blocked By

None.

Ticket 013 is not a functional dependency. If its validator refactor is in
progress, sequence overlapping validator and test edits rather than modifying
the same surfaces concurrently.

## User Stories Addressed

- As a project maintainer, I can recreate a working development environment
  without relying on old chat history or memory.
- As a new contributor, I can follow one ordered setup recipe that points to
  the project's real configuration sources and tells me how to verify success.
- As an agent user, I can recover undocumented setup through honest backfill
  rather than invented historical certainty.
- As a maintainer, I can detect when setup instructions drift from current
  manifests, commands, settings, platforms, or automation.
- As a cross-platform user, I can prefer portable Bash automation while keeping
  unavoidable native operations explicit and narrowly scoped.
- As a security-conscious user, I can preserve setup knowledge without putting
  credentials or unsafe machine changes into tracked automation.

## Implementation Route

- Use `writing-plans` just before implementation to choose exact source,
  fixture, validation, and documentation edits.
- Use `framework-agnostic-skill-creator` to create and evaluate the skill
  package.
- Use TDD or equivalent RED/GREEN proof for new registry, signal, fixture, and
  validator behavior.
- Use `code-security-review` for secret handling, unsafe execution, permission,
  external-service, and machine-wide automation boundaries.
- Use `standards-and-spec-review` to check the completed diff against this
  ticket and its parent spec.
- Use `doc-sync` after behavior, registry, fixtures, and public guidance change.
- Use `verification-before-completion` before any ready, passing, integrated,
  self-contained, safe, or complete claim.

## Scope Exclusions

- Do not implement passive monitoring, shell history collection, GUI
  surveillance, runtime hooks, telemetry, or framework-specific background
  automation.
- Do not create a general personal-computer customization log.
- Do not duplicate package manifests, lockfiles, containers, environment
  templates, toolchain files, task runners, or other declarative configuration.
- Do not replace manuals, runbooks, documentation drift checks, learning notes,
  handoffs, or broad knowledge retrieval.
- Do not store secret values, credentials, licence keys, private certificates,
  client data, private paths, or machine-local personal details in public or
  tracked artifacts.
- Do not execute generated automation as part of capture or generation.
- Do not imply that Bash removes platform-specific command, path, privilege,
  package-manager, or system-API differences.
- Do not add a separate history file, fixed universal docs layout, executable
  helper package, remote issue, installer, or Factory runtime without a
  separately approved scope change.
- Do not implement Ticket 013's validator refactor as part of this ticket.

## Implementation Proof

- `setup-scribe` ships as a 213-line standalone productivity skill with three
  directly linked references and no bundled executable helper.
- Eight portable fixtures and seven focused regression tests cover capture,
  backfill, audit, Bash-first automation, secret rejection, source ownership,
  project-versus-personal settings, and the compact no-impact route.
- RED/GREEN forward evaluation used the same raw mock project evidence without
  leaking the intended answer. The first GREEN run exposed a task-runner
  loophole that preferred new Node replay logic; the skill was tightened and a
  fresh GREEN run correctly proposed Bash-first automation with separate
  execution approval.
- `uv --no-cache run python -m unittest discover -s tests -v` passed all 94
  tests.
- `uv --no-cache run python scripts/validate_skills.py` passed 35 skills, 35
  registry entries, all fixture families, and all eight Setup Scribe scenarios.
  The shared policy is 1,193 words with zero human-review notes.
- `uv --no-cache run python scripts/compare_v1_v2_context.py` confirmed all
  representative V2 routes retain at least the required 10% reduction.
- The generic skill validator, targeted privacy and placeholder scans,
  whitespace checks, Markdown/link review, and `git diff --check` passed.
- Focused security review found no high-evidence issue in secret, execution,
  permission, machine-wide, external-service, or public-boundary handling.
  Standards/spec review findings were corrected and reverified.
- Three pre-existing Learning Capture schema examples remain report-only drift;
  they are unrelated to Ticket 014 and do not block validation.
