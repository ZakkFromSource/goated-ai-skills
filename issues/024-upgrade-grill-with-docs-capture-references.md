## Parent PRD

`issues/prd-goated-ai-skills-v1-public-core.md`

## Type

AFK

## What to build

Upgrade `grill-with-docs` with self-contained references for context-doc and ADR capture decisions. The skill should keep the grill conversational and evidence-grounded, list candidate durable updates, and route target-project `CONTEXT.md` curation to `project-context-calibration` when that skill is available.

Evidence:

- https://github.com/mattpocock/skills/tree/main/skills/engineering/grill-with-docs

## Acceptance criteria

- [ ] `skills/engineering/grill-with-docs/SKILL.md` links to `references/context-docs.md` and `references/adr-capture.md` with clear read conditions.
- [ ] `skills/engineering/grill-with-docs/references/context-docs.md` explains optional context conventions, including `CONTEXT-MAP.md`, without making them universal requirements.
- [ ] `skills/engineering/grill-with-docs/references/adr-capture.md` explains when to recommend ADR capture and how to prefer the target project's existing convention before any default.
- [ ] Each decision-shaping grill question includes a recommended default and evidence or rationale.
- [ ] The workflow includes scenario probes for lifecycle, ownership, identity, cardinality, partial vs whole operations, failure states, and cross-context effects.
- [ ] The output contract lists candidate durable updates for `CONTEXT.md`, ADRs, standards docs, PRDs, or doc-sync follow-up.
- [ ] The skill does not own unconditional `CONTEXT.md` or ADR writes and avoids duplicating `issues/022-project-context-calibration.md`.

## Blocked by

- `issues/archive/009-grill-with-docs.md`

## User stories addressed

- As an agent user, I can pressure-test work against project facts while seeing which durable docs may need later updates.
- As a future agent, I can route resolved context language to the right follow-up skill instead of silently editing the wrong artifact.

