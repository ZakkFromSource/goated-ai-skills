# Skills

This folder contains public skill categories for GOATED AI Skills V1.

Skill folders and `SKILL.md` files are added only when a specific approved implementation issue calls for them.

Implemented skill folders are intended to be copied, installed, or adapted into a user's chosen agent framework. A skill folder should remain useful after installation without depending on this repo's root files.

## Categories

- `agent-workflows/` - operating patterns for installed skills, target-project onboarding, context calibration, handoffs, and skill porting.
- `engineering/` - software delivery, review, testing, docs, and architecture workflows.
- `productivity/` - portable productivity workflows.

## Lean Schema

Every implemented `SKILL.md` must use YAML frontmatter with these required fields:

```yaml
name:
category:
classification:
status:
description:
triggers:
outputs:
depends_on:
adapters:
```

`description` is for skill discovery only. It should say when to load the skill by naming user requests, task conditions, symptoms, or project context. Put workflow steps, proof gates, outputs, review loops, and implementation detail in the body, not in `description`.

Valid `category` values for public V1 are:

- `agent-workflows`
- `engineering`
- `productivity`

Use `portable`, `domain-specific`, or `private` for `classification`.

Use `stable`, `wip`, or `deprecated` for `status`.

GOATED keeps these richer schema fields even when source inspiration uses a smaller frontmatter shape. `classification`, `status`, `outputs`, `depends_on`, and `adapters` stay required for implemented skills.

`depends_on` should name hard dependencies, soft dependencies, or graceful fallbacks explicitly. `adapters` should state whether the skill is usable in Codex, Claude Code, Hermes, OpenCode, or a generic agent framework, and should keep framework-specific notes small.

## Body Sections

Prefer:

- `# Skill Name`
- `## Purpose`
- `## Inputs`
- `## Workflow`
- `## Output Contract`
- `## Delegation`
- `## Guardrails`
- `## References`

Omit sections that add no value. Keep `SKILL.md` under a soft 300-line cap.

Installed skills must be self-contained. They can reference files inside their own skill folder, but they must not require this source repo's `AGENT.md`, `README.md`, or `CONTEXT.md` at runtime.

## Progressive Disclosure Contract

`SKILL.md` is the router and operating procedure, not the whole knowledge base. Treat `references/`, `scripts/`, and `assets/` as first-class support files when they keep `SKILL.md` lean or make the installed skill more capable.

Put detailed examples, checklists, stack-specific notes, long decision guides, reusable prompt templates, and anti-pattern catalogs in directly linked `references/`. Use `scripts/` for maintained executable helpers and `assets/` for reusable fixtures, templates, images, or packaged materials.

When a skill has support files:

- keep support files one level down from `SKILL.md`;
- link each support file directly from `SKILL.md`;
- tell the agent when to read or use each support file;
- avoid duplicating the same guidance in both places.

## Discipline Contract

Discipline-heavy skills should include concrete stop rules, proof gates, rationalization counters or tables, red flags, or anti-pattern references when generic reminders would be easy to rationalize away.

## Delegation Contract

Every skill should be subagent-aware and single-agent-compatible.

The main agent owns user intent, orchestration, final judgment, and final communication. Subagents may handle bounded independent work when available, but they must return evidence such as file paths, commands, source docs, diff handles, or explicit assumptions. If subagents are unavailable, the main agent should run the same workflow sequentially with a narrower context budget.

Delegated workflows should define explicit status enums such as `DONE`, `DONE_WITH_CONCERNS`, `NEEDS_CONTEXT`, and `BLOCKED` when a subagent result can change the controller's next action, such as implementation, review, verification, blocking, re-dispatch, or competing design paths. Simple evidence scans can keep lighter requirements: evidence, assumptions, uncertainty, and paths or commands inspected.

Each delegated status must say what the controller does next. Longer implementer, reviewer, or controller prompt templates belong in directly linked `references/` files, with `SKILL.md` explaining when to use them.

## Implementation Boundary

Do not create skill folders or `SKILL.md` files from this category index alone. Create them only when working an approved implementation issue for that specific skill.
