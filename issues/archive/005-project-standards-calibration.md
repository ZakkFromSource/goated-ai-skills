## Parent PRD

`issues/prd-goated-ai-skills-v1-public-core.md`

## Type

AFK

## What to build

Implement `project-standards-calibration` under `skills/agent-workflows/`. The skill scans a target project for documented and inferred standards, asks only about preferences that cannot be inferred safely, and writes a durable standards profile.

## Acceptance criteria

- [x] `skills/agent-workflows/project-standards-calibration/SKILL.md` exists and follows the lean schema.
- [x] The workflow inspects documented standards and local conventions before asking the user questions.
- [x] The default tracked output is `docs/agents/project-standards.md` inside the target project.
- [x] The output contract separates documented standards, inferred conventions, user-confirmed preferences, unresolved questions, and enforcement levels.
- [x] Enforcement levels include tooling-enforced, review-enforced, and preference-only.
- [x] The guardrails prevent the skill from asking about discoverable facts.

## Blocked by

- `issues/archive/003-session-start-progressive-disclosure.md`
- `issues/archive/004-context-matrix-map.md`

## User stories addressed

- As an agent user, I can make project standards durable for repeated work.
- As a future agent, I can distinguish hard rules from preferences.
