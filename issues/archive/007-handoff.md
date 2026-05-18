## Parent PRD

`issues/prd-goated-ai-skills-v1-public-core.md`

## Type

AFK

## What to build

Implement `handoff` under `skills/agent-workflows/`. The skill writes compact continuity notes for future agents or sessions, defaulting to ignored target-project local storage while referencing existing artifacts instead of duplicating them.

## Acceptance criteria

- [x] `skills/agent-workflows/handoff/SKILL.md` exists and follows the lean schema.
- [x] The default output path is `.local/handoffs/` inside the target project.
- [x] The workflow captures current state, important references, verification status, blockers, and recommended next skills.
- [x] The guardrails prevent duplicating PRDs, issue files, ADRs, diffs, or commit messages.
- [x] The workflow states that tracked handoffs require explicit user request.
- [x] The skill remains useful for both onboarding and delivery sessions.

## Blocked by

- `issues/archive/003-session-start-progressive-disclosure.md`

## User stories addressed

- As an agent user, I can resume work later without losing context.
- As a future agent, I can pick up from a compact note that points to source artifacts.
