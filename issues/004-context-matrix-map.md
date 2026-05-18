## Parent PRD

`issues/prd-goated-ai-skills-v1-public-core.md`

## Type

AFK

## What to build

Implement `context-matrix-map` under `skills/agent-workflows/`. The skill builds a source-grounded target-project context map that helps future agents choose what to read first, second, and only if needed.

## Acceptance criteria

- [ ] `skills/agent-workflows/context-matrix-map/SKILL.md` exists and follows the lean schema.
- [ ] The workflow discovers docs, code areas, tests, commands, ADRs, and context packs without bulk-reading the project.
- [ ] The default tracked output is `docs/agents/context-matrix.md` inside the target project.
- [ ] The output contract separates first-read, second-read, and only-if-needed sources.
- [ ] The guardrails prevent the context matrix from becoming a broad architecture essay.
- [ ] Delegation notes require evidence such as paths, commands, and explicit assumptions from any subagent scan.

## Blocked by

- `issues/archive/003-session-start-progressive-disclosure.md`

## User stories addressed

- As an agent user, I can give future agents a durable map of important project context.
- As a future agent, I can avoid context flooding while still finding relevant source material.
