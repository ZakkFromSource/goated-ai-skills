## Parent PRD

`issues/prd-goated-ai-skills-v1-public-core.md`

## Type

AFK

## What to build

Implement `framework-agnostic-skill-porting` under `skills/agent-workflows/`. The skill converts tool-specific or project-specific workflows into the neutral GOATED skill format while separating universal behavior from adapter notes and private or domain-specific assumptions.

## Acceptance criteria

- [x] `skills/agent-workflows/framework-agnostic-skill-porting/SKILL.md` exists and follows the lean schema.
- [x] The workflow inventories source workflow behavior, tool-specific mechanics, assumptions, dependencies, and portability risks.
- [x] The output contract includes a proposed neutral skill shape, adapter notes, classification recommendation, and remaining blockers.
- [x] The guardrails require private or sensitive content to be removed, generalized, or kept out of public main.
- [x] The workflow explains when to use `references/` rather than expanding `SKILL.md`.
- [x] Delegation notes support independent portability and privacy review passes.

## Blocked by

- `issues/archive/002-define-skill-authoring-contract.md`
- `issues/archive/003-session-start-progressive-disclosure.md`

## User stories addressed

- As a maintainer, I can adapt existing workflows into portable public skills.
- As a private-fork user, I can understand what must be sanitized before contributing publicly.
