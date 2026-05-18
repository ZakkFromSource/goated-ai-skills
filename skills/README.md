# Skills

This folder contains public skill category placeholders for GOATED AI Skills V1.

Actual skill folders and `SKILL.md` files are intentionally deferred until the V1 PRD is approved and split into implementation issues.

When implemented, skill folders are intended to be copied, installed, or adapted into a user's chosen agent framework. A skill folder should remain useful after installation without depending on this repo's root files.

## Categories

- `agent-workflows/` - operating patterns for installed skills, target-project onboarding, handoffs, and skill porting.
- `engineering/` - software delivery, review, testing, docs, and architecture workflows.
- `productivity/` - portable productivity workflows.

## Lean Schema

When skill implementation begins, every `SKILL.md` should use YAML frontmatter with:

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

Use `portable`, `domain-specific`, or `private` for `classification`.

Use `stable`, `wip`, or `deprecated` for `status`.

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
