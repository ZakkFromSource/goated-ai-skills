## Parent PRD

`issues/prd-goated-ai-skills-v1-public-core.md`

## Type

AFK

## What to build

Implement `prd-to-issues` under `skills/engineering/`. The skill breaks a scoped PRD into independently workable local vertical-slice issue handoffs with acceptance criteria, blockers, and user stories.

## Acceptance criteria

- [x] `skills/engineering/prd-to-issues/SKILL.md` exists and follows the lean schema.
- [x] The workflow explores the current repo or target project enough to understand implementation state before slicing.
- [x] The workflow drafts title, type, blockers, and user stories for approval before writing issue files.
- [x] The default output uses local files named `issues/NNN-short-title.md`.
- [x] The workflow creates blocker and foundation issues before dependent issues.
- [x] The guardrails prohibit changing the parent PRD or creating non-local issue records.

## Blocked by

- `issues/archive/010-write-a-prd.md`

## User stories addressed

- As an agent user, I can turn a PRD into reviewable vertical implementation slices.
- As an implementer, I can pick up one issue without re-reading the whole PRD.
