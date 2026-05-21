## Parent PRD

`issues/prd-goated-ai-skills-v1-superpowers-absorption.md`

## Type

AFK

## What to build

Upgrade the existing `tdd` skill with the strongest portable Superpowers TDD conventions: stronger RED/GREEN evidence, rationalization guardrails, anti-pattern references, and closeout routing through verification.

## Acceptance criteria

- [ ] `skills/engineering/tdd/SKILL.md` is updated without losing GOATED's current lean schema or deep-module testing guidance.
- [ ] The workflow requires clear RED evidence before implementation when a behavior test is feasible.
- [ ] The workflow requires GREEN evidence after implementation and distinguishes passing targeted tests from broader verification.
- [ ] The workflow includes rationalization guardrails for skipping tests, changing tests to match broken behavior, over-mocking, and calling work complete without proof.
- [ ] Long anti-patterns, rationalization tables, or examples live under `skills/engineering/tdd/references/` instead of bloating `SKILL.md`.
- [ ] The workflow routes final proof through `verification-before-completion`.
- [ ] The skill remains self-contained after installation and does not require this source repo's root files.

## Blocked by

- `issues/archive/033-update-skill-authoring-contract-superpowers-conventions.md`
- `issues/036-add-verification-before-completion-skill.md`
- `issues/archive/013-tdd.md`

## User stories addressed

- As an agent user, I can trust TDD work includes real failing-before and passing-after evidence when feasible.
- As a maintainer, I can strengthen discipline without importing Superpowers tone wholesale.

## Implementation notes

- Use `grill-with-docs` before implementation to compare the current GOATED TDD skill and its references.
- Superpowers source inspiration: https://github.com/obra/superpowers/blob/main/skills/test-driven-development/SKILL.md
- Related source inspiration: https://github.com/obra/superpowers/blob/main/skills/verification-before-completion/SKILL.md
- Keep GOATED's architecture-sensitive testing guidance, especially deep modules, seams, and replace-don't-layer behavior.
