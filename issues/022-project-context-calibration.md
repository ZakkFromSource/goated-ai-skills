## Parent PRD

`issues/prd-goated-ai-skills-v1-public-core.md`

## Type

AFK

## What to build

Implement `project-context-calibration` under `skills/agent-workflows/`. The skill creates or curates a target project's root `CONTEXT.md` so future agents share the same project boundaries, domain language, durable artifact definitions, and reusable architecture vocabulary.

## Acceptance criteria

- [ ] `skills/agent-workflows/project-context-calibration/SKILL.md` exists and follows the lean schema.
- [ ] The workflow uses `docs/agents/context-matrix.md` when present to find source-grounded context before writing or refreshing `CONTEXT.md`.
- [ ] The default tracked output is root `CONTEXT.md` inside the target project.
- [ ] The output contract covers project boundaries, domain language, durable artifact definitions, and reusable architecture vocabulary.
- [ ] The workflow routes future agents to treat `CONTEXT.md` as target-project context, not as this source repo's root `CONTEXT.md`.
- [ ] The guardrails prevent overlap with source mapping, standards enforcement, architecture diagrams, and refactor recommendations.
- [ ] Delegation notes support bounded terminology, docs, architecture-language, and artifact-definition scans with evidence.

## Blocked by

- `issues/archive/004-context-matrix-map.md`

## User stories addressed

- As an agent user, I can make project language and architecture vocabulary durable before repeated work.
- As a future agent, I can read one target-project context file without confusing it with standards, source maps, diagrams, or refactor plans.
