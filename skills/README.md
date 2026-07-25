# Skills

This folder contains the public skill catalog. The current folders preserve the
completed V1 standalone experience while V2 migration proceeds through scoped
tickets.

Skill folders and `SKILL.md` files are added only when a specific approved implementation issue calls for them.

Implemented skill folders may be installed individually or as part of the
integrated stack described in [`../docs/install.md`](../docs/install.md). A
skill folder remains useful after individual installation without depending on
the shared registry or this repo's root files.

## Categories

- `agent-workflows/` - operating patterns for installed skills, target-project onboarding, context calibration, handoffs, and skill creation and porting.
- `engineering/` - software delivery, review, testing, docs, and architecture workflows.
- `productivity/` - portable productivity workflows.

## Lean Schema

Every implemented `SKILL.md` must use YAML frontmatter with this required shape:

```yaml
---
name: <skill-name>
description: <discovery-focused description>
metadata:
  goated-category: <agent-workflows | engineering | productivity>
---
```

`description` is for skill discovery only. It should say when to load the skill by naming user requests, task conditions, symptoms, or project context. Put workflow steps, proof gates, outputs, review loops, and implementation detail in the body, not in `description`.

Valid `metadata.goated-category` values for public V1 are:

- `agent-workflows`
- `engineering`
- `productivity`

Do not add GOATED-only top-level fields such as `category`, `classification`, `status`, `triggers`, `outputs`, `depends_on`, or `adapters`. Treat `metadata` as public, scalar, and non-behavioral. Keep routing behavior, output behavior, dependency semantics, and guardrails in Markdown body sections.

Use standard optional frontmatter only when the skill has a real need. `compatibility` may describe an actual per-skill environment or framework constraint. Do not add VS Code-only fields, Codex `agents/openai.yaml`, or experimental tool controls unless a future approved issue explicitly calls for that work.

Dependencies should name hard dependencies, soft dependencies, and graceful fallbacks explicitly in a body `## Dependencies` section. Adapter or compatibility notes should appear only when a specific skill has a real framework caveat; do not recreate generic "usable everywhere" maps.

Before committing skill or integrated-registry changes, run the local validator
from the repo root:

```bash
uv run python scripts/validate_skills.py
```

The validator enforces current skill checks plus the integrated registry's JSON
Schema and source cross-references. It reports docs/example schema drift
separately without failing the command when implemented skills pass.

## Body Sections

Prefer:

- `# Skill Name`
- `## Purpose`
- `## Inputs`
- `## Dependencies`
- `## Workflow`
- `## Output Contract`
- `## Delegation`
- `## Guardrails`
- `## References`

Omit sections that add no value. Keep `SKILL.md` under a soft 300-line cap.

Installed skills must retain the task-critical guidance needed when invoked
alone. They can reference files inside their own skill folder, but they must
not require the integrated registry or this source repo's `AGENT.md`,
`README.md`, or `CONTEXT.md` at runtime.

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
