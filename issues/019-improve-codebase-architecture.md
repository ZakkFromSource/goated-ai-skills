## Parent PRD

`issues/prd-goated-ai-skills-v1-public-core.md`

## Type

AFK

## What to build

Implement `improve-codebase-architecture` under `skills/engineering/`. The skill explores architecture improvement opportunities in a target project and produces candidate refactor directions or an RFC-style handoff when needed.

## Acceptance criteria

- [ ] `skills/engineering/improve-codebase-architecture/SKILL.md` exists and follows the lean schema.
- [ ] The workflow looks for shallow modules, tightly coupled concepts, hard-to-test areas, and places where deeper modules would improve clarity.
- [ ] The workflow uses source-grounded evidence and avoids speculative rewrites.
- [ ] The output contract includes opportunities, evidence, tradeoffs, suggested next slice, and when to write an RFC.
- [ ] The guardrails prevent implementing refactors during review-only exploration.
- [ ] Delegation notes support independent exploration of bounded code areas.

## Blocked by

- `issues/018-architecture-design-map.md`

## User stories addressed

- As an agent user, I can identify architecture improvements before committing to a refactor.
- As a maintainer, I can turn architecture observations into workable future slices.
