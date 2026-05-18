## Parent PRD

`issues/prd-goated-ai-skills-v1-public-core.md`

## Type

AFK

## What to build

Implement `doc-sync` under `skills/engineering/`. The skill identifies and handles documentation drift after behavior, interface, architecture, standards, or test changes.

## Acceptance criteria

- [ ] `skills/engineering/doc-sync/SKILL.md` exists and follows the lean schema.
- [ ] The workflow discovers changed behavior and relevant docs before proposing updates.
- [ ] The workflow updates docs during implementation sessions and reports required doc updates during planning or review-only sessions.
- [ ] The output contract includes docs checked, updates made or recommended, skipped docs with reason, and residual drift risk.
- [ ] Delegation notes support bounded documentation review passes.
- [ ] The guardrails keep source-of-truth docs and temporary handoffs distinct.

## Blocked by

- `issues/004-context-matrix-map.md`
- `issues/005-project-standards-calibration.md`
- `issues/014-standards-and-spec-review.md`

## User stories addressed

- As an agent user, I can keep docs aligned with behavior and project standards.
- As a future agent, I can trust durable docs more than stale session notes.
