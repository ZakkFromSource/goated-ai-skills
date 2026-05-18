## Parent PRD

`issues/prd-goated-ai-skills-v1-public-core.md`

## Type

AFK

## What to build

Implement `write-a-prd` under `skills/engineering/`. The skill turns an unclear request, client brief, roadmap item, or feature idea into a scoped PRD that can later feed `prd-to-issues`.

## Acceptance criteria

- [x] `skills/engineering/write-a-prd/SKILL.md` exists and follows the lean schema.
- [x] The workflow explores available project facts before asking the user questions.
- [x] The workflow uses `grill-with-docs` when docs or project artifacts matter.
- [x] The output contract includes problem, goals, non-goals, audience, requirements, acceptance criteria, risks, and open questions.
- [x] The guardrails keep the PRD scoped rather than turning it into an unbounded backlog.
- [x] The skill states where PRDs should be written by default in a target project and when to ask for a different location.

## Blocked by

- `issues/archive/009-grill-with-docs.md`

## User stories addressed

- As an agent user, I can turn fuzzy intent into a usable implementation spec.
- As a future agent, I can split the PRD into concrete vertical issues.
