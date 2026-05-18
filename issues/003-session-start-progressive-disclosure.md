## Parent PRD

`issues/prd-goated-ai-skills-v1-public-core.md`

## Type

AFK

## What to build

Implement `session-start-progressive-disclosure` under `skills/agent-workflows/`. The skill starts a session by reading the minimum necessary context, identifies whether the user is installing skills, onboarding a target project, or delivering work, and states assumptions or missing context without flooding the session.

## Acceptance criteria

- [ ] `skills/agent-workflows/session-start-progressive-disclosure/SKILL.md` exists and follows the lean schema.
- [ ] The workflow tells the agent what to read first, what to defer, and when to stop exploring.
- [ ] The skill distinguishes source repo work, target-project onboarding, and target-project delivery.
- [ ] The output contract includes a concise session orientation with assumptions, missing context, relevant artifacts, and next recommended skill.
- [ ] Delegation notes support bounded repo scans when subagents are available and a narrower sequential fallback when they are not.
- [ ] The skill is self-contained and does not require this repo's root docs after installation.

## Blocked by

- `issues/002-define-skill-authoring-contract.md`

## User stories addressed

- As an agent user, I can start a session without loading unnecessary context.
- As a maintainer, I can route later onboarding and delivery workflows through a shared first step.
