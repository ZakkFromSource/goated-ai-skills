## Parent PRD

`issues/prd-goated-ai-skills-v1-public-core.md`

## Type

AFK

## What to build

Implement `grill-with-docs` under `skills/engineering/`. The skill challenges user intent against available docs, standards, ADRs, and project facts before serious target-project work.

## Acceptance criteria

- [ ] `skills/engineering/grill-with-docs/SKILL.md` exists and follows the lean schema.
- [ ] The workflow first gathers relevant project facts through progressive disclosure.
- [ ] The skill is gated mandatory for onboarding, PRDs, architecture changes, cross-file work, unclear requests, and public-facing behavior.
- [ ] The skill can be skipped for tiny mechanical edits and states that skip rule clearly.
- [ ] The output contract includes clarified goal, success criteria, scope boundaries, decisions, assumptions, and remaining questions.
- [ ] The workflow asks decision-shaping questions without asking for discoverable facts.

## Blocked by

- `issues/003-session-start-progressive-disclosure.md`
- `issues/004-context-matrix-map.md`
- `issues/005-project-standards-calibration.md`

## User stories addressed

- As an agent user, I can pressure-test important work before implementation starts.
- As a maintainer, I can keep planning grounded in project artifacts rather than vibes.
