# GOATED AI Skills Maintainer Contract

This file guides agents contributing to this repository. It is not an installable artifact that users are expected to copy into every target project, and it is distinct from `stack/AGENTS.md`, the installable shared policy.

GOATED AI Skills is a public source library for installable, self-contained AI skill folders. Preserve the distinction between:

1. this source repo;
2. skill folders installed into an agent framework;
3. target projects where installed skills are used.

Current state: this repo preserves the completed V1 public-core skill set at
the `v1-baseline` Git tag and ships the maintainer-accepted V2 integrated
stack. Post-V2 work proceeds through approved specs and tickets; check the
order files under `tickets/` for the current frontier instead of assuming it.
Add new skill folders and `SKILL.md` files only when a specific approved
implementation ticket calls for them.

## Core Posture

Build and maintain a public, framework-agnostic skill library. Do not over-center this repo's root instructions as if they were runtime requirements for installed skills.

Before changing files in this repo:

1. Read this file.
2. Read `CONTEXT.md`.
3. Read the relevant spec or ticket.
4. Load only the docs, ADRs, references, or source files needed for the current task.
5. Keep public/private boundaries explicit.

## Product Model

Layer 0: Skill Pack Distribution

- Users clone, download, copy, or adapt skill folders from this repo into Codex, Claude Code, Hermes, OpenCode, or another agent framework.
- V2 recommends a docs-first integrated install using `stack/AGENTS.md` and
  `stack/goated-stack.yaml`; runtime automation remains out of scope.
- Individually installed skill folders must retain a compact standalone
  fallback and must not depend on source-repo root files.

Layer 1: Target Project Onboarding

- Installed skills prepare a user's project for serious agent work.
- Use docs-grounded clarification when unresolved intent, scope, success
  criteria, tradeoffs, or project-language conflicts materially block safe
  progress.
- Do not activate clarification solely because work is cross-file,
  public-facing, part of onboarding, or described by a spec or legacy PRD.

Layer 2: Target Project Delivery

- Installed skills help perform real work inside a target project.
- Delivery includes specs, Wayfinder decision maps, architecture plans,
  tickets, prototypes, implementation plans, TDD, diagnosis, review, security
  checks, docs, commit messages, and handoffs.

## Progressive Disclosure

Use context in layers:

1. Root maintainer files for this repo: `AGENTS.md`, `CONTEXT.md`, and `README.md`.
2. The relevant spec under `docs/specs/` or ticket under `tickets/`.
3. `docs/agents/context-matrix.md` and `docs/agents/project-standards.md` for non-trivial work.
4. `skills/README.md` and the category README files under `skills/`.
5. Skill bodies and references only when that skill is relevant.

Do not bulk-read the repo when a targeted read will do.

## Where Work Lives

- `docs/specs/`: active product and delivery specs.
- `tickets/`: active delivery tickets and per-spec order files; completed tickets move to `tickets/archive/`.
- `docs/adr/`: architectural decision records, indexed in `docs/adr/README.md`. Supersede accepted ADRs instead of rewriting them.
- `docs/plans/`: dated implementation plans.
- `docs/agents/`: context routing and the standards profile for this repo.
- `stack/`: V2 shared policy, registry, schema, templates, and fixtures.
- `issues/`: historical V1 PRDs and archived issue handoffs. Do not add new work there or rewrite archived records.

## GOATED Skill Routing

Use `skills/agent-workflows/using-goated-ai-skills/SKILL.md` as the portable router when the GOATED skill path is uncertain or needs revision. It selects a proportionate route across source-repo maintenance, skill installation/adaptation, target-project onboarding, target-project delivery, durable-knowledge retrieval, research, prompt work, and tiny direct tasks, while respecting explicit user overrides and user and project instructions. A clear specialist request may go directly to that skill.

When documenting or configuring installed skill usage, point agents and thin target-project adapters to the installed `using-goated-ai-skills` router instead of duplicating full onboarding or delivery workflows here.

## Subagent Policy

Workflows in this repo should be subagent-aware and single-agent-compatible.

Use subagents when available for bounded, independent work:

- repo scans;
- standards/spec review axes;
- security review passes;
- competing architecture/interface designs;
- verification passes;
- source summarization that can return evidence.

The main agent owns user intent, orchestration, final judgment, and final communication. Subagents must return evidence such as file paths, commands, source docs, diff handles, or explicit assumptions. The main agent must sanity-check and integrate their output.

If subagents are unavailable, run the same workflow sequentially with a narrower context budget.

## Target Project Workflows

When the relevant skills are installed into an agent framework, apply the
shared integrated policy when installed and preserve standalone fallback
behavior. Use the installed `using-goated-ai-skills` router for onboarding and
delivery work when the route is uncertain; it classifies the request, applies
user and project instruction precedence, and points to the next relevant
installed skill instead of requiring agents to memorize the full stack.

Track only durable target-project artifacts selected by the onboarding artifact
budget. Resumable envelopes and handoffs default to verified-ignored
`.local/goated/work-envelopes/` and `.local/goated/handoffs/`; use OS temp
`goated-handoffs/<project-name>/` when project-local state is inappropriate or
unsafe.

## Public Boundary

Do not add private personal context, private project names, credentials, client data, handles, sensitive personal domains, or private workflow assumptions to public main. Put private planning in `.local/`, which is ignored.

Public docs may mention private forks or private deployments generically, but they must not depend on private content.

## Editing Rules

- Keep this repo's docs public-safe.
- Keep `SKILL.md` files under a soft 300-line cap.
- Move detailed examples, checklists, templates, and stack-specific notes into directly linked `references/`.
- Keep individual skill fallbacks usable; installed skills must not need this
  repo's root `AGENTS.md`, `README.md`, or `CONTEXT.md` at runtime.
- Make dependency behavior explicit: hard dependency, soft dependency, or graceful fallback.
- Follow the frontmatter schema and required sections in `skills/README.md`.
- When adding or renaming a skill, update `stack/goated-stack.yaml`, the
  relevant `stack/fixtures/`, and the catalog lists in `README.md` and the
  category READMEs in the same change.
- Keep this file the single root instruction file. Add a tool-specific root
  file only when a tool cannot read `AGENTS.md`, and make it import this file
  instead of copying it.

## Validation

Run these before claiming skill, registry, fixture, or validator changes pass:

```
uv run python scripts/validate_skills.py
uv run python -m unittest discover -s tests -v
uv run python scripts/compare_v1_v2_context.py
```

CI runs the same commands on push and pull request. There is no linter or formatter; docs-only changes rely on manual markdown review.
