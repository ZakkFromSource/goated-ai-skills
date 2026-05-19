## Parent PRD

`issues/prd-goated-ai-skills-v1-public-core.md`

## Type

AFK

## What to build

Implement `standards-and-spec-review` under `skills/engineering/`. The skill reviews changes since a fixed point along two separate axes: project standards compliance and spec/issue fit.

## Acceptance criteria

- [x] `skills/engineering/standards-and-spec-review/SKILL.md` exists and follows the lean schema.
- [x] The workflow asks the user or discovers the fixed point for the review.
- [x] The workflow uses `docs/agents/project-standards.md` when present and states lower confidence when it is missing.
- [x] The output contract separates standards findings from spec findings.
- [x] Findings include evidence from files, commands, docs, or explicit assumptions.
- [x] The guardrails prevent mixing security audit claims into this review.

## Blocked by

- `issues/archive/005-project-standards-calibration.md`
- `issues/archive/012-prd-to-issues.md`
- `issues/archive/013-tdd.md`

## User stories addressed

- As an agent user, I can tell whether a change follows project conventions and the requested spec.
- As a reviewer, I can see standards concerns separately from missed requirements.
