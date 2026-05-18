## Parent PRD

`issues/prd-goated-ai-skills-v1-public-core.md`

## Type

AFK

## What to build

Implement `grill-me` under `skills/productivity/`. The skill interviews the user about a plan, PRD, architecture choice, workflow change, or ambiguous feature design when project docs are not required.

## Acceptance criteria

- [ ] `skills/productivity/grill-me/SKILL.md` exists and follows the lean schema.
- [ ] The workflow asks one decision-shaping question at a time.
- [ ] The skill recommends defaults and explains tradeoffs without pretending to know undiscovered project facts.
- [ ] The output contract includes decisions made, assumptions locked, unresolved questions, and recommended next action.
- [ ] The guardrails state that `grill-with-docs` is preferred when project artifacts matter.
- [ ] The skill remains portable and public-safe.

## Blocked by

- `issues/archive/002-define-skill-authoring-contract.md`
- `issues/archive/003-session-start-progressive-disclosure.md`

## User stories addressed

- As an agent user, I can clarify an idea before turning it into a plan or PRD.
- As a maintainer, I can keep lightweight interrogation separate from docs-grounded grilling.
