# Skills

This folder contains public skill categories for GOATED AI Skills V1.

Skill folders and `SKILL.md` files are added only when a specific approved implementation issue calls for them.

When implemented, skill folders are intended to be copied, installed, or adapted into a user's chosen agent framework. A skill folder should remain useful after installation without depending on this repo's root files.

## Categories

- `agent-workflows/` - operating patterns for installed skills, target-project onboarding, handoffs, and skill porting.
- `engineering/` - software delivery, review, testing, docs, and architecture workflows.
- `productivity/` - portable productivity workflows.

## Lean Schema

When skill implementation begins, every `SKILL.md` must use YAML frontmatter with these required fields:

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

Valid `category` values for public V1 are:

- `agent-workflows`
- `engineering`
- `productivity`

Use `portable`, `domain-specific`, or `private` for `classification`.

Use `stable`, `wip`, or `deprecated` for `status`.

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

`SKILL.md` is the router and operating procedure, not the whole knowledge base. Put detailed examples, templates, checklists, stack-specific notes, and long decision guides in directly linked `references/` files inside the skill folder.

When a skill has references:

- keep references one level down from `SKILL.md`;
- link each reference directly from `SKILL.md`;
- tell the agent when to read each reference;
- avoid duplicating the same guidance in both places.

## Delegation Contract

Every skill should be subagent-aware and single-agent-compatible.

The main agent owns user intent, orchestration, final judgment, and final communication. Subagents may handle bounded independent work when available, but they must return evidence such as file paths, commands, source docs, diff handles, or explicit assumptions. If subagents are unavailable, the main agent should run the same workflow sequentially with a narrower context budget.

## Implementation Boundary

Do not create skill folders or `SKILL.md` files from this category index alone. Create them only when working an approved implementation issue for that specific skill.
