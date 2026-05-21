## Parent PRD

`issues/prd-goated-ai-skills-v1-superpowers-absorption.md`

## Type

HITL

## What to build

Decide whether GOATED V1 should ever include runtime bootstrap or adapter automation inspired by Superpowers, or whether those ideas stay post-V1. This issue should produce a human-reviewed recommendation, not implementation.

## Acceptance criteria

- [ ] The analysis compares docs-first installation, portable router guidance, adapter notes, runtime bootstrap scripts, plugin manifests, and hook-based activation.
- [ ] The analysis identifies any conflict with `AGENT.md`, `CONTEXT.md`, and the V1 public core's docs-first distribution model.
- [ ] The analysis explains what would need to change before runtime automation could be public-safe and framework-agnostic.
- [ ] The recommendation is one of: keep out of V1, allow a narrow V1 adapter note only, create a new PRD, or approve a specific implementation issue.
- [ ] No runtime bootstrap code, manifests, hooks, installer scripts, or automatic skill activation behavior are implemented in this issue.
- [ ] Any approved future work is routed to a new issue or PRD with explicit scope and acceptance criteria.

## Blocked by

- `issues/archive/034-add-using-goated-ai-skills-router.md`

## User stories addressed

- As a maintainer, I can make a deliberate decision before GOATED moves beyond docs-first installation.
- As an agent user, I can trust V1 does not silently assume a specific framework runtime.

## Implementation notes

- Use `grill-with-docs` before the decision pass and read the current V1 distribution language before making recommendations.
- Superpowers source inspiration: https://github.com/obra/superpowers/blob/main/skills/using-superpowers/SKILL.md
- Also inspect upstream adapter/product distribution ideas from the repo root when useful: https://github.com/obra/superpowers
- Treat this as a decision record precursor. If a durable decision is approved, route to the repo's ADR or PRD convention rather than burying it in chat.
