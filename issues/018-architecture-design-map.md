## Parent PRD

`issues/prd-goated-ai-skills-v1-public-core.md`

## Type

AFK

## What to build

Implement `architecture-design-map` under `skills/engineering/`. The skill produces source-grounded architecture maps for target projects, using Mermaid by default and optional visual formats only when useful and available.

## Acceptance criteria

- [ ] `skills/engineering/architecture-design-map/SKILL.md` exists and follows the lean schema.
- [ ] The workflow gathers source evidence before diagramming.
- [ ] The default output includes a Mermaid diagram, source references, concise explanation, and uncertainty notes.
- [ ] Optional formats such as Excalidraw, ASCII maps, generated images, or plugin-backed diagrams are clearly secondary.
- [ ] The guardrails prohibit decorative or speculative diagrams unsupported by source evidence.
- [ ] The workflow states when to write a durable target-project artifact versus answer inline.

## Blocked by

- `issues/archive/004-context-matrix-map.md`
- `issues/022-project-context-calibration.md`
- `issues/archive/005-project-standards-calibration.md`

## User stories addressed

- As an agent user, I can get an architecture map grounded in the project source.
- As a future agent, I can use the map without mistaking speculation for fact.
