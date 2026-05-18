# GOATED AI Skills Maintainer Contract

This file guides agents contributing to this repository. It is not an installable artifact that users are expected to copy into every target project.

GOATED AI Skills is a public source library for installable, self-contained AI skill folders. Preserve the distinction between:

1. this source repo;
2. skill folders installed into an agent framework;
3. target projects where installed skills are used.

Current state: this repo contains the V1 scaffold and PRD. Actual skill folders and `SKILL.md` files are intentionally deferred until the PRD is approved and split into issues.

## Core Posture

Build and maintain a public, framework-agnostic skill library. Do not over-center this repo's root instructions as if they were runtime requirements for installed skills.

Before changing files in this repo:

1. Read this file.
2. Read `CONTEXT.md`.
3. Read the relevant PRD or issue.
4. Load only the docs, ADRs, references, or source files needed for the current task.
5. Keep public/private boundaries explicit.

## Product Model

Layer 0: Skill Pack Distribution

- Users clone, download, copy, or adapt skill folders from this repo into Codex, Claude Code, Hermes, OpenCode, or another agent framework.
- V1 installation is docs-first, not automated.
- Installed skill folders must be self-contained.

Layer 1: Target Project Onboarding

- Installed skills prepare a user's project for serious agent work.
- This is gated mandatory for durable, cross-file, PRD-level, architectural, or repeated work.
- It is skippable for tiny one-off tasks.

Layer 2: Target Project Delivery

- Installed skills help perform real work inside a target project.
- Delivery includes planning, prototyping, PRDs, issues, TDD, review, docs, commit messaging, and handoff.

## Progressive Disclosure

Use context in layers:

1. Root maintainer files for this repo: `AGENT.md`, `CONTEXT.md`, and `README.md`.
2. The relevant PRD or issue under `issues/`.
3. Category README files under `skills/`.
4. Skill bodies and references only after those skills exist and are relevant.

Do not bulk-read the repo when a targeted read will do. Do not create actual skill folders or `SKILL.md` files unless the current task explicitly calls for skill implementation.

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

## Planned Target Project Onboarding

When the V1 skills are implemented and installed into an agent framework, use this workflow inside a target project before serious/repeated work:

```text
session-start-progressive-disclosure
-> grill-with-docs
-> context-matrix-map
-> project-standards-calibration
-> agent-instructions-integrator
-> architecture-design-map optional
-> doc-sync
-> handoff optional
```

Durable target-project artifacts should be tracked under `docs/agents/`. Session/private artifacts should use ignored `.local/`.

## Planned Target Project Delivery

When the V1 skills are implemented and installed into an agent framework, use this workflow inside a target project for delivery work:

```text
session-start-progressive-disclosure
-> grill-with-docs when gated mandatory
-> prototype optional
-> write-a-prd
-> prd-to-issues
-> prototype optional per focused issue
-> tdd
-> standards-and-spec-review
-> code-security-review
-> doc-sync
-> commit-message
-> handoff optional
```

## Public Boundary

Do not add private personal context, private project names, credentials, client data, handles, sensitive personal domains, or private workflow assumptions to public main. Put private planning in `.local/`, which is ignored.

Public docs may mention private forks or private deployments generically, but they must not depend on private content.

## Editing Rules

- Keep this repo's docs public-safe.
- Keep future `SKILL.md` files under a soft 300-line cap.
- Move detailed examples, checklists, templates, and stack-specific notes into directly linked `references/`.
- Make installed skills self-contained; they must not need this repo's root `AGENT.md`, `README.md`, or `CONTEXT.md` at runtime.
- Make dependency behavior explicit: hard dependency, soft dependency, or graceful fallback.
- Keep repo adapter files thin and scoped to contribution in this repo.
