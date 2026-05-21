# PRD: GOATED AI Skills V1 Public Core

## Status

Draft reference PRD. This file is intended to be reviewed first, then used in a later session with `prd-to-issues`.

This PRD does not mean the V1 skills have been implemented yet. The current repo may contain only scaffold files and category placeholders until implementation issues are created.

## Problem Statement

Agent workflows are often powerful but inconsistent. Skills, prompts, setup conventions, reviews, PRDs, and handoffs tend to live as scattered personal snippets or tool-specific habits. This makes agents harder to reuse across Codex, Claude Code, Hermes, OpenCode, and other tool-calling environments.

GOATED AI Skills should become a public-facing, framework-agnostic source library of installable skill folders. Users should be able to clone, download, copy, install, or adapt the skills into their own agentic workflow, then use those installed skills inside their own projects.

This repo should not read like a project template that users clone into every new codebase. It is the public distribution home and maintainer workspace for the skills.

## Goals

- Create a public source repo for reusable, framework-agnostic AI skills.
- Make installation, copying, and adaptation the public entrypoint.
- Define a lean skill schema that is human-readable, agent-usable, and portable.
- Ensure installed skill folders are self-contained and do not require this repo's root files at runtime.
- Define three layers: Skill Pack Distribution, Target Project Onboarding, and Target Project Delivery.
- Provide a V1 skill set that covers the complete public core workflow once implemented.
- Preserve a generic private-fork/private-deployment path without exposing private details.
- Make all skills subagent-aware while remaining usable by single-agent environments.
- Make progressive disclosure a first-class authoring rule.

## Non-Goals

- Do not implement actual skill folders in the scaffold/PRD phase.
- Do not build private project, client, personal-domain, or sensitive personal skills in public V1.
- Do not require users to clone this repo into every target project.
- Do not make installed skills depend on this repo's root `AGENT.md`, `README.md`, or `CONTEXT.md`.
- Do not implement rich machine-readable manifests in V1.
- Do not generate indexes from metadata in V1.
- Do not build automated validators or adapter repair scripts in V1.
- Do not claim full security audit coverage in V1.
- Do not build installer tooling in V1.
- Do not run compatibility testing across every agent framework in V1.

## Audience

Primary audience:

- Agent users who want to install, copy, adapt, or maintain a public core skill library across different agentic workflows.

Secondary audience:

- Maintainers contributing to this public skill library.
- Future private-fork or private-deployment users who want to add private/domain-specific skills without changing the public-core conventions.
- Future agents that need clear routing for installed skills inside target projects.

## Product Model

GOATED AI Skills has three layers.

### Layer 0: Skill Pack Distribution

This public repo is the source, catalog, and documentation home for GOATED skill folders.

Users should be able to:

- clone or download the repo;
- copy selected skill folders;
- adapt skill folders to a chosen agent framework;
- install the skill pack into a local agent skill directory when supported;
- read docs-first guidance for Codex, Claude Code, Hermes, OpenCode, and generic agent frameworks.

Layer 0 does not mean users clone this repo into every target project.

### Layer 1: Target Project Onboarding

After skills are installed into an agent framework, users can run onboarding inside any project where they want serious agent support.

Target Project Onboarding is gated mandatory for:

- durable/repeated work;
- cross-file changes;
- PRD-level planning;
- architecture changes;
- public-facing behavior;
- work where project standards matter.

Tiny one-off tasks can skip onboarding.

### Layer 2: Target Project Delivery

After the relevant skills are installed, and after onboarding when required, users can use the delivery workflow inside their own project.

Delivery covers:

- intent clarification;
- optional prototypes;
- PRDs;
- architecture blueprints;
- issue breakdown;
- TDD;
- standards/spec review;
- security review;
- doc sync;
- commit message drafting;
- handoff.

## Root Repo Requirements

The public source repo should use this scaffold:

```text
AGENT.md
AGENTS.md
CLAUDE.md
CONTEXT.md
README.md
.gitignore
.out-of-scope/
docs/
  install.md
  adr/
issues/
  prd-goated-ai-skills-v1-public-core.md
skills/
  README.md
  agent-workflows/
    README.md
  engineering/
    README.md
  productivity/
    README.md
.local/        # ignored by git
```

Root file responsibilities:

- `README.md` explains the public skill-library purpose, install model, categories, and planned workflows.
- `docs/install.md` provides docs-first install/adaptation guidance.
- `AGENT.md` guides agents contributing to this source repo only.
- `AGENTS.md` and `CLAUDE.md` are thin contributor adapters for this source repo.
- `CONTEXT.md` defines public-safe language and repo intent.
- `.gitignore` ignores `.local/`.
- `.out-of-scope/` records public future upgrades and deferred ideas.
- `docs/adr/` stores future ADRs.
- `issues/` stores this PRD and future issue handoff files.
- `skills/` contains active public skill category placeholders until skill implementation begins.

## Public/Private Boundary

Public main should contain portable public-core workflows only.

Private or domain-specific workflows may live in private forks or private deployments unless deliberately sanitized for public use. Public docs may mention private forks or private deployments generically, but must not include private names, handles, sensitive context, client details, or workflows that require non-public knowledge.

`.local/` is ignored and can contain private planning notes such as:

- future private taxonomy notes;
- temporary research notes;
- scratch notes while designing public-safe skills.

No content inside `.local/` should be required for public repo behavior.

## Installation Requirements

V1 installation is docs-first.

`README.md` should provide:

- a short explanation of the installable skill-library model;
- the three-layer model;
- a link to `docs/install.md`;
- current scaffold status;
- the planned categories and workflows.

`docs/install.md` should provide:

- generic copy/install/adapt guidance;
- notes for Codex;
- notes for Claude Code;
- notes for Hermes;
- notes for OpenCode;
- target-project artifact defaults;
- clear statement that installer scripts are out of scope for V1.

Installed skills must be self-contained:

- A copied skill folder must include the workflow guidance it needs.
- A copied skill folder can reference files inside its own folder.
- A copied skill folder must not require this repo's root `AGENT.md`, `README.md`, or `CONTEXT.md` at runtime.

## Skill Taxonomy

Use active public category folders only in V1:

- `skills/agent-workflows/`
- `skills/engineering/`
- `skills/productivity/`

Do not create empty public placeholders for future private/domain categories. Future categories can be tracked locally in `.local/` or added later when they contain public-safe skills.

## Skill Schema

Each implemented skill should live in:

```text
skills/<category>/<skill-name>/SKILL.md
```

Each `SKILL.md` should use lean YAML frontmatter:

```yaml
---
name: skill-name
category: agent-workflows|engineering|productivity
classification: portable|domain-specific|private
status: stable|wip|deprecated
description: Clear trigger-focused description of when to use the skill, not a workflow summary.
triggers:
  - user asks for ...
outputs:
  - expected output ...
depends_on:
  - optional dependency ...
adapters:
  codex: usable
  claude-code: usable
  generic-agent: usable
---
```

The `description` field is for skill discovery only. It should describe when to load the skill using user requests, task conditions, symptoms, or project context. Workflow steps, proof gates, outputs, review loops, and implementation detail belong in the body.

GOATED keeps this richer schema even when source inspiration uses smaller frontmatter. `classification`, `status`, `outputs`, `depends_on`, and `adapters` remain required for implemented skills.

Required body sections:

- `# Skill Name`
- `## Purpose`
- `## Inputs`
- `## Workflow`
- `## Output Contract`
- `## Delegation`
- `## Guardrails`
- `## References`

Sections can be omitted only when they add no value.

## Progressive Disclosure Requirements

Each `SKILL.md` should act as the router and operating procedure, not the entire knowledge base.

Rules:

- Treat 300 lines as a soft review threshold.
- Treat `references/`, `scripts/`, and `assets/` as first-class support files when they keep `SKILL.md` lean or make the installed skill more capable.
- Move detailed examples, checklists, prompt templates, stack-specific notes, anti-pattern catalogs, rationalization tables, and long decision guides into directly linked `references/`.
- Use `scripts/` for maintained executable helpers and `assets/` for reusable fixtures, templates, images, or packaged materials.
- Keep support files one level deep from `SKILL.md`.
- Directly link every support file from `SKILL.md`.
- Tell the agent exactly when to read or use each support file.
- Do not duplicate the same guidance in both `SKILL.md` and support files.
- Do not require this source repo's root files once the skill is installed elsewhere.
- For discipline-heavy skills, use stop rules, proof gates, rationalization counters or tables, red flags, or anti-pattern references when generic reminders would be easy to rationalize away.

## Subagent Requirements

Every skill should be subagent-aware and single-agent-compatible.

Global rule:

- The main agent owns intent, orchestration, final judgment, and user communication.
- Subagents may handle bounded independent work when available.
- Subagents must return evidence: file paths, commands, source docs, diff handles, or explicit assumptions.
- The main agent must sanity-check and integrate subagent output.
- If subagents are unavailable, the main agent runs the same workflow sequentially with a narrower context budget.
- Delegated workflows should define explicit status enums such as `DONE`, `DONE_WITH_CONCERNS`, `NEEDS_CONTEXT`, and `BLOCKED` when a subagent result can change the controller's next action, such as implementation, review, verification, blocking, re-dispatch, or competing design paths. Simple evidence scans can use lighter evidence, assumption, uncertainty, and inspected-path requirements.
- Longer implementer, reviewer, or controller prompt templates should live in directly linked `references/` files, with `SKILL.md` explaining when to use them.

Good subagent use cases:

- independent repo scans;
- standards/spec review axes;
- security review passes;
- competing architecture/interface designs;
- verification passes;
- summarizing bounded source material.

## Target Project Artifact Defaults

Installed skills should use split artifact defaults inside target projects:

Tracked durable project artifacts:

```text
CONTEXT.md
docs/agents/context-matrix.md
docs/agents/project-standards.md
docs/agents/architecture-plan.md
docs/architecture/<slug>-architecture-plan.md
```

Session/private artifacts:

```text
<os-temp>/goated-handoffs/<project-name>/
.local/scratch/
```

Durable project facts should be tracked. Temporary handoffs should live outside the workspace in OS temp unless the user explicitly requests a tracked handoff. Other session-private workspace artifacts should be ignored.

## V1 Skill Set

### Agent Workflows

`session-start-progressive-disclosure`

- Starts a session by reading only the minimum necessary context.
- Identifies whether the user is installing skills, onboarding a target project, or delivering work.
- States assumptions and missing context.
- Prevents broad context flooding.

`context-matrix-map`

- Builds a source-grounded map of a target project's docs, code areas, tests, commands, ADRs, and context packs.
- Writes `docs/agents/context-matrix.md` by default inside the target project.
- Supports progressive disclosure by telling future agents what to read first, second, and only-if-needed.
- Does not become an architecture essay.

`project-context-calibration`

- Creates or curates root `CONTEXT.md` inside the target project.
- Captures project boundaries, domain language, durable artifact definitions, and reusable architecture vocabulary.
- Uses `docs/agents/context-matrix.md` when present to find source-grounded context.
- Does not become a source map, standards profile, architecture diagram, or refactor recommendation.

`project-standards-calibration`

- Scans a target project for documented and inferred standards.
- Grills the user only on preferences that cannot be inferred safely.
- Writes `docs/agents/project-standards.md` by default inside the target project.
- Separates documented standards, inferred conventions, user-confirmed preferences, unresolved questions, and enforcement level.

`agent-instructions-integrator`

- Detects or accepts the user's chosen agent framework.
- Creates or updates the target project's agent instruction artifact or configuration.
- Routes the agent to installed GOATED skills and target-project artifacts.
- Does not assume `AGENT.md` is universal.
- Does not paste the full GOATED workflow into every target project.

`handoff`

- Writes compact continuity notes for future agents or sessions.
- Defaults to the OS temp directory under `goated-handoffs/<project-name>/`.
- References existing artifacts instead of duplicating PRDs, issues, ADRs, diffs, or commits.

`framework-agnostic-skill-porting`

- Converts tool-specific or project-specific skills into the repo's neutral skill format.
- Separates universal workflow from tool-specific adapters.
- Identifies hidden assumptions, portability limits, and private/domain-specific content.

### Engineering

`grill-with-docs`

- Challenges user intent against available docs, standards, ADRs, and project facts.
- Runs during Target Project Onboarding and Target Project Delivery.
- Is gated mandatory for onboarding, PRDs, architecture changes, cross-file work, unclear requests, and public-facing behavior.
- Can be skipped for tiny mechanical edits.

`write-a-prd`

- Turns an unclear request, client brief, roadmap item, or feature idea into a scoped PRD.
- Explores available project facts before asking questions.
- Produces a PRD that can later feed `prd-to-issues`.

`prototype`

- Creates target-project-local throwaway artifacts to answer one question.
- Can run before PRD creation or inside focused issue exploration.
- Must capture the verdict and then delete or absorb the prototype.

`prd-to-issues`

- Breaks a scoped PRD into vertical-slice issue handoffs.
- Produces independently workable issues with acceptance criteria and blockers.
- Does not create remote issues unless a later implementation explicitly adds that behavior.

`tdd`

- Uses behavior-first red/green/refactor.
- Tests observable behavior through public interfaces.
- Avoids bulk horizontal test writing.
- Prefers one tracer bullet at a time.

`standards-and-spec-review`

- Reviews changes since a fixed point along two independent axes:
  - standards: does the change follow the target project's documented standards?
  - spec: does the change match the originating issue, PRD, or spec?
- Has a soft dependency on `docs/agents/project-standards.md` inside the target project.
- If the standards profile is missing, falls back to discovered standards and states lower confidence.
- Keeps standards findings and spec findings separate.

`code-security-review`

- Performs a static review gate for high-evidence bugs, trust-boundary issues, data leaks, auth problems, injection paths, unsafe config, and exploitable patterns.
- Does not claim full audit coverage.
- Reports only findings with strong evidence.

`doc-sync`

- Identifies documentation drift after behavior, interface, architecture, standards, or test changes.
- Updates docs during implementation sessions.
- Reports required doc updates during planning/review-only sessions.
- Is subagent-friendly but not subagent-required.

`commit-message`

- Drafts a concise, information-rich commit message from local diffs and verified checks.
- Is generic git-first, with optional GitHub/PR context when available.
- Does not stage, commit, or push unless a separate future workflow explicitly handles that.

`architecture-design-map`

- Produces source-grounded architecture maps for a target project.
- Uses Mermaid by default.
- Can use Excalidraw, ASCII, generated images, or plugin-backed diagrams when available and appropriate.
- Must not create decorative or speculative diagrams unsupported by source evidence.

`plan-codebase-architecture`

- Plans source-grounded project-wide or feature-specific architecture before implementation begins.
- Requires a clarified brief, PRD, issue, or `grill-with-docs` result before writing a durable blueprint.
- Produces interface-level architecture blueprints with planned modules, seams, dependencies, test surfaces, slice order, risks, and RFC or ADR triggers.
- Routes PRD creation, issue breakdown, RFC/ADR capture, implementation, existing-code repair, and current-state maps to companion skills.

`improve-codebase-architecture`

- Explores architectural improvement opportunities in a target project.
- Looks for shallow modules, tightly coupled concepts, hard-to-test areas, and places where deeper modules would improve clarity.
- Produces candidate refactor directions and, when needed, an RFC-style handoff.

### Productivity

`grill-me`

- Interviews the user about a plan, PRD, architecture choice, workflow change, or ambiguous feature design.
- Asks one decision-shaping question at a time.
- Recommends defaults and explains tradeoffs.
- Can operate without project docs; `grill-with-docs` is preferred when project artifacts matter.

## Target Project Onboarding

Purpose: prepare a target project for serious agent work after the GOATED skills have been installed into the user's agent framework.

Default flow:

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

Expected outputs:

- tracked `docs/agents/context-matrix.md`;
- tracked root `CONTEXT.md`;
- tracked `docs/agents/project-standards.md`;
- target-agent instruction routing via the relevant instruction artifact or config;
- optional architecture map;
- optional project-wide architecture plan;
- synchronized docs;
- optional temporary handoff under OS temp `goated-handoffs/<project-name>/`.

## Target Project Delivery

Purpose: move one target-project change from intent to verified handoff.

Default flow:

```text
session-start-progressive-disclosure
-> grill-with-docs when gated mandatory
-> prototype optional
-> write-a-prd
-> plan-codebase-architecture optional
-> prd-to-issues
-> prototype optional per focused issue
-> tdd
-> standards-and-spec-review
-> code-security-review
-> doc-sync
-> commit-message
-> handoff optional
```

Expected outputs:

- clarified intent;
- optional prototype verdict;
- scoped PRD;
- optional feature-specific architecture plan;
- vertical-slice issues;
- behavior-focused tests;
- implemented change;
- standards/spec review;
- security review;
- synchronized docs;
- commit message;
- optional temporary handoff.

## Review Gate Design

`standards-and-spec-review` and `code-security-review` must remain separate.

Standards/spec review asks:

- Did the change follow documented standards?
- Did the change implement the spec?
- Did it miss requirements?
- Did it add unrequested scope?

Security review asks:

- Did the change introduce exploitable risk?
- Did it cross trust boundaries unsafely?
- Did it leak data/secrets?
- Did it weaken auth, persistence, validation, or execution safety?

Keeping these separate prevents one axis from masking another.

## Project Context File Design

`project-context-calibration` should write one durable output inside the target project:

```text
CONTEXT.md
```

The file should include:

- project boundaries;
- domain language;
- durable artifact definitions;
- reusable architecture vocabulary;
- explicit gaps or assumptions.

It should not replace `docs/agents/context-matrix.md`, `docs/agents/project-standards.md`, architecture diagrams, architecture plans, ADRs, PRDs, or refactor plans.

## Project Standards Profile Design

`project-standards-calibration` should write one durable output inside the target project:

```text
docs/agents/project-standards.md
```

The file should include:

- documented standards;
- inferred conventions;
- user-confirmed preferences;
- unresolved questions;
- enforcement levels.

Enforcement levels:

- tooling-enforced;
- review-enforced;
- preference-only.

The skill should not ask users about discoverable facts. It should inspect the target project first and ask only about preferences or ambiguous tradeoffs.

## Handoff Storage Policy

`handoff` should write to this OS temp path by default:

```text
<os-temp>/goated-handoffs/<project-name>/
```

Handoffs should:

- summarize current state;
- reference existing artifacts by path;
- avoid duplicating PRDs, issues, ADRs, diffs, or commit messages;
- include recommended next skills;
- stay out of the project workspace unless the user explicitly requests a tracked handoff.

## Prototype Policy

Prototypes are target-project-local and throwaway.

Rules:

- Define the question before building.
- Locate the prototype close to the relevant code or route.
- Mark it clearly as a prototype.
- Avoid persistence by default.
- Skip production polish.
- Surface the relevant state.
- Capture the verdict.
- Delete or absorb before final handoff.

## Architecture Diagram Policy

`architecture-design-map` is Mermaid-first.

Default output should be:

- Mermaid diagram;
- source references;
- concise explanation;
- uncertainty notes.

Optional outputs:

- Excalidraw;
- ASCII map;
- generated image;
- plugin-backed diagram.

Optional formats should be used only when available and useful.

## Architecture Planning Policy

`plan-codebase-architecture` is blueprint-first.

Default durable outputs should be:

- project-wide setup: `docs/agents/architecture-plan.md`;
- feature-specific planning: `docs/architecture/<slug>-architecture-plan.md`;
- inline response for small or exploratory architecture questions.

Architecture plans should require clarified intent and stay at the interface, dependency, data ownership, test-surface, and slice-order level. They should not become speculative file trees, PRDs, issue lists, implementation diffs, current-state diagrams, or refactor reviews.

## Implementation Issue Strategy

When this PRD is later passed to `prd-to-issues`, split implementation into vertical slices.

Recommended issue sequence:

1. Source repo scaffold and public distribution docs.
2. Skill schema and category conventions.
3. Layer 0 install/adaptation guidance.
4. Target Project Onboarding skills.
5. Target Project Delivery planning and implementation skills.
6. Target Project Delivery review and closeout skills.
7. Documentation, ADRs, and final acceptance pass.

Each issue should be independently reviewable and should avoid creating all skills in one undifferentiated batch.

## Acceptance Criteria

The V1 implementation is complete when:

- public docs distinguish source repo, installed skills, and target projects;
- README explains docs-first install/copy/adapt usage;
- `docs/install.md` covers generic guidance plus Codex, Claude Code, Hermes, and OpenCode notes;
- source repo `AGENT.md` is clearly maintainer/contributor guidance only;
- `.local/` is ignored;
- active public category folders exist;
- no actual `SKILL.md` files exist during the scaffold/PRD phase;
- actual implemented skills follow the lean schema once created;
- every implemented skill is self-contained after installation;
- every implemented skill has clear triggers, outputs, guardrails, and delegation notes where useful;
- every `SKILL.md` respects the soft 300-line cap or justifies why it exceeds it;
- `agent-instructions-integrator` replaces narrow single-file instruction framing everywhere;
- Target Project Onboarding and Target Project Delivery are documented consistently;
- `project-context-calibration` clearly defines target-project root `CONTEXT.md`;
- `project-standards-calibration` clearly defines `docs/agents/project-standards.md`;
- `context-matrix-map` clearly defines `docs/agents/context-matrix.md`;
- `plan-codebase-architecture` clearly defines project-wide and feature-specific architecture plan defaults;
- `standards-and-spec-review` clearly defines its soft dependency behavior;
- `code-security-review` does not claim full audit coverage;
- `handoff` defaults to OS temp under `goated-handoffs/<project-name>/`;
- public main contains no private names, handles, sensitive personal domains, client context, or private workflow assumptions.

## Open Questions

These should be resolved only if they become blockers during implementation:

- Whether category README files should list planned skills before the actual skill folders exist.
- Whether future generated indexes should be public docs, local-only artifacts, or both.
- Whether future framework-specific install notes beyond Codex, Claude Code, Hermes, and OpenCode should be added in V1 or deferred.
- Whether future installer automation should live in this repo or in framework-specific adapter packages.
