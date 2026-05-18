## Parent PRD

`issues/prd-goated-ai-skills-v1-public-core.md`

## Type

AFK

## What to build

Implement `agent-instructions-integrator` under `skills/agent-workflows/`. The skill creates or updates the target project's agent instruction artifact or configuration so it routes agents to installed GOATED skills and durable target-project artifacts without assuming one universal instruction filename.

## Acceptance criteria

- [ ] `skills/agent-workflows/agent-instructions-integrator/SKILL.md` exists and follows the lean schema.
- [ ] The workflow detects or accepts the chosen agent framework before editing instructions.
- [ ] The workflow supports Codex, Claude Code, Hermes, OpenCode, and generic agent-framework routing at a docs-first level.
- [ ] The output contract includes the selected instruction artifact, installed skill routing, target-project artifact routing, and any unresolved framework assumptions.
- [ ] The guardrails prohibit pasting the full GOATED workflow into every target project.
- [ ] The skill does not assume `AGENT.md` is universal.

## Blocked by

- `issues/archive/003-session-start-progressive-disclosure.md`
- `issues/004-context-matrix-map.md`
- `issues/005-project-standards-calibration.md`

## User stories addressed

- As an agent user, I can integrate GOATED skills into the agent framework I already use.
- As a maintainer, I can keep framework-specific notes as adapters rather than rewriting the workflow.
