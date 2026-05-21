## Parent PRD

`issues/prd-goated-ai-skills-v1-additions.md`

`issues/prd-goated-ai-skills-v1-superpowers-absorption.md`

## Type

AFK

## What to build

Implement `diagnose` under `skills/engineering/`. The skill should guide bug and performance investigation from reproduction through root-cause proof, then route implementation proof to companion skills such as `tdd`.

## Acceptance criteria

- [ ] `skills/engineering/diagnose/SKILL.md` exists and follows the lean schema.
- [ ] The workflow builds or requests a fast enough feedback loop before hypothesis testing.
- [ ] The workflow includes repro confirmation, ranked falsifiable hypotheses, targeted instrumentation, root-cause reporting, cleanup, and residual-risk notes.
- [ ] The workflow absorbs useful Superpowers `systematic-debugging` discipline: observe before fixing, compare expectations to reality, test one hypothesis at a time, and prove root cause.
- [ ] Performance regressions route through measurement, profiling, query plans, or bisection before fixes.
- [ ] Regression proof routes to `tdd` when a correct seam exists and records architecture follow-up when no correct seam exists.
- [ ] The workflow routes closeout through `verification-before-completion` when that skill is available.
- [ ] Guardrails cover secrets/logs, production instrumentation, destructive repros, debug-log cleanup, and temporary artifacts.
- [ ] The skill is self-contained after installation and does not require this source repo's root files.

## Blocked by

- `issues/archive/013-tdd.md`
- `issues/archive/019-improve-codebase-architecture.md`
- `issues/archive/036-add-verification-before-completion-skill.md`
- `issues/041-upgrade-tdd-superpowers-contracts.md`

## User stories addressed

- As an agent user, I can ask for a hard bug or performance regression to be diagnosed before implementation begins.
- As a maintainer, I can keep debugging work disciplined, reproducible, and evidence-backed.

## Implementation notes

- Use `grill-with-docs` before implementation to compare the current GOATED debugging, TDD, and architecture guidance.
- Use the upstream package as inspiration, not a wholesale copy: https://github.com/mattpocock/skills/tree/main/skills/engineering/diagnose
- Use Superpowers `systematic-debugging` as additional source inspiration: https://github.com/obra/superpowers/blob/main/skills/systematic-debugging/SKILL.md
- Related Superpowers TDD and verification sources:
  - https://github.com/obra/superpowers/blob/main/skills/test-driven-development/SKILL.md
  - https://github.com/obra/superpowers/blob/main/skills/verification-before-completion/SKILL.md
- Keep `diagnose` separate from `tdd`: diagnosis finds the cause and establishes proof; TDD owns implementation cycles once behavior is clear.
- Include MIT attribution if substantial upstream wording or template material is reused.
