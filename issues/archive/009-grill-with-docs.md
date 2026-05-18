## Parent PRD

`issues/prd-goated-ai-skills-v1-public-core.md`

## Type

AFK

## What to build

Implement `grill-with-docs` under `skills/engineering/`. The skill challenges user intent against available docs, standards, ADRs, and project facts before serious target-project work.

## Acceptance criteria

- [x] `skills/engineering/grill-with-docs/SKILL.md` exists and follows the lean schema.
- [x] The workflow first gathers relevant project facts through progressive disclosure.
- [x] The skill is gated mandatory for onboarding, PRDs, architecture changes, cross-file work, unclear requests, and public-facing behavior.
- [x] The skill can be skipped for tiny mechanical edits and states that skip rule clearly.
- [x] The output contract includes clarified goal, success criteria, scope boundaries, decisions, assumptions, and remaining questions.
- [x] The workflow asks decision-shaping questions without asking for discoverable facts.

## Blocked by

- `issues/archive/003-session-start-progressive-disclosure.md`
- `issues/archive/004-context-matrix-map.md`
- `issues/archive/005-project-standards-calibration.md`

## User stories addressed

- As an agent user, I can pressure-test important work before implementation starts.
- As a maintainer, I can keep planning grounded in project artifacts rather than vibes.
