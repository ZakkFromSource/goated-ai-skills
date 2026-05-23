# GOATED AI Skills

GOATED AI Skills is a public source library for installable, framework-agnostic AI skills. The intended use is to clone, download, copy, or adapt the skill folders into an existing agentic workflow, then use those skills inside the user's own projects.

This repo is not a project template that users are expected to clone into every codebase. It is the distribution home and maintainer workspace for the skills.

## Current State

This repo currently contains the V1 scaffold, PRDs, archived implementation issue handoffs, and the implemented WIP skill folders completed so far through approved issues. The V1 additions, Superpowers absorption issue set, and final V1 acceptance pass are complete or explicitly deferred.

New skill folders and `SKILL.md` files should be added only when a specific approved implementation issue calls for them.

## Source Repo Boundary

Use this repo as the public distribution home for reusable skill folders. Do not treat its root instructions, docs, or `.local/` notes as runtime requirements for installed skills. Once copied into an agent framework, each skill folder must carry the guidance it needs inside its own folder.

Private planning may live in ignored `.local/`, but public behavior must not depend on it.

## Quick Use Model

GOATED AI Skills has three layers:

1. **Skill Pack Distribution** - users clone, download, copy, or install skill folders from this repo into Codex, Claude Code, Hermes, OpenCode, or another agent framework.
2. **Target Project Onboarding** - installed skills prepare a user's project for serious agent work by mapping sources, calibrating project context and standards, and integrating with the chosen agent instructions.
3. **Target Project Delivery** - installed skills help perform real project work through planning, architecture blueprints, prototyping, PRDs, issues, TDD, review, docs, commit messages, and handoff.

Start with [docs/install.md](docs/install.md) for installation and adaptation guidance. After installation, use [docs/how-to-use.md](docs/how-to-use.md) as the human operator manual for the installed skill stack.

## Design Principles

- Skills are portable by default and explicit when they are not.
- Installed skills must be self-contained and must not require this repo's root `AGENT.md`, `README.md`, or `CONTEXT.md` at runtime.
- `SKILL.md` stays lean; deeper examples, templates, and checklists live in directly linked `references/`.
- Every skill is subagent-aware but single-agent-compatible.
- Public main stays free of private project names, handles, credentials, sensitive personal domains, client context, and private workflow assumptions.
- Private forks or private deployments can add private/domain-specific skills using the same classification system.

## Root Layout

```text
AGENT.md               Maintainer/contributor guidance for this repo.
AGENTS.md              Thin adapter for agents contributing to this repo.
CLAUDE.md              Thin adapter for Claude-style contributors to this repo.
CONTEXT.md             Public context for this skill library.
docs/install.md        Docs-first install and adaptation guidance.
docs/how-to-use.md     Human operator manual for using the installed skill stack.
docs/adr/              Architectural Decision Records.
.out-of-scope/         Public future ideas and deferred upgrades.
.local/                Ignored private notes and scratch work for local source-repo work.
skills/                Public skill categories and implemented skill folders.
issues/                PRDs and future issue handoff docs.
```

## Public Skill Categories

- `skills/agent-workflows/` - installable operating patterns for session starts, target project onboarding, context calibration, standards calibration, instruction integration, handoffs, and skill creation and porting.
- `skills/engineering/` - installable workflows for PRDs, prototyping, implementation plans, TDD, reviews, security checks, doc sync, commits, architecture maps, architecture plans, and refactoring.
- `skills/productivity/` - installable productivity workflows that are public-safe and portable.

Future private or domain-specific categories belong in a private fork or private deployment until intentionally sanitized for public use.

## Classifications And Status

Every implemented skill should declare a classification:

- `portable` - safe for any compatible agent or project.
- `domain-specific` - reusable pattern with a named public domain or project assumption.
- `private` - intended for private forks or private deployments, not public main.

Every implemented skill should declare a status:

- `stable` - recommended for normal use.
- `wip` - experimental or still being sharpened.
- `deprecated` - kept for reference only.

## Target Project Onboarding

After the skill pack is installed into an agent framework, use this workflow inside a target project before durable, cross-file, PRD-level, architectural, or repeated work. Tiny one-off tasks can skip it.

```text
session-start-progressive-disclosure
-> grill-with-docs
-> context-matrix-map
-> project-context-calibration
-> project-standards-calibration
-> agent-instructions-integrator
-> architecture-design-map optional
-> plan-codebase-architecture optional
-> doc-sync
-> handoff optional
```

Durable target-project artifacts should be tracked, such as root `CONTEXT.md`, `docs/agents/context-matrix.md`, `docs/agents/project-standards.md`, and `docs/agents/architecture-plan.md` when a project-wide architecture blueprint is useful. Handoffs default to the OS temp directory under `goated-handoffs/<project-name>/`; other session/private workspace artifacts can use ignored `.local/`.

## Target Project Delivery

Use this workflow inside a target project after the relevant skills are installed and, for serious work, after onboarding.

```text
session-start-progressive-disclosure
-> grill-with-docs when gated mandatory
-> prototype optional
-> write-a-prd
-> plan-codebase-architecture optional
-> prd-to-issues
-> prototype optional per focused issue
-> writing-plans
-> subagent-driven-development optional for larger, riskier, or parallelizable implementation
-> tdd
-> standards-and-spec-review
-> code-security-review
-> doc-sync
-> verification-before-completion
-> commit-message
-> handoff optional
```

`grill-with-docs` is gated mandatory for onboarding, PRDs, architecture changes, cross-file work, unclear requests, and public-facing behavior. Tiny mechanical edits can skip it.

## V1 Acceptance

- Public docs distinguish source repo, installed skills, and target projects.
- Root files explain the distribution model clearly.
- `.local/` is ignored.
- Actual skill implementation proceeds only through specific approved implementation issues.
- Implemented skills follow the lean schema once created.
- New `SKILL.md` files are created only by their approved implementation issues.
- Public main contains no private names, handles, sensitive personal domains, client context, or private workflow assumptions.
