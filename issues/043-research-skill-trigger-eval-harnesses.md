## Parent PRD

`issues/prd-goated-ai-skills-v1-superpowers-absorption.md`

## Type

HITL

## What to build

Research whether GOATED should add skill-trigger evaluation harnesses, and if so, what form is worth implementing after V1 or behind a separate approved issue.

## Acceptance criteria

- [ ] The research compares static checks, prompt transcript fixtures, live agent harness tests, and hybrid/manual acceptance checklists.
- [ ] The research explains nondeterminism, cost, maintenance, privacy, and false-confidence risks for each option.
- [ ] The research identifies what could be useful in V1 docs without adding a live harness.
- [ ] The research recommends one of: no harness for V1, static/docs-only checks, prompt transcript examples, a prototype, or a future PRD.
- [ ] No live harness, CI integration, runtime adapter, or trigger-test framework is implemented in this issue.
- [ ] Any future implementation path includes explicit acceptance criteria and public-boundary guardrails.

## Blocked by

- `issues/archive/034-add-using-goated-ai-skills-router.md`
- `issues/archive/035-decide-runtime-bootstrap-and-adapter-automation.md`

## User stories addressed

- As a maintainer, I can decide whether skill-trigger evaluation is worth the complexity before adding tooling.
- As an agent user, I can avoid over-trusting flaky or opaque trigger tests.

## Implementation notes

- Use `grill-with-docs` before research synthesis to compare current GOATED trigger conventions against the proposed harness options.
- Superpowers source inspiration: https://github.com/obra/superpowers/tree/main/skills/writing-skills
- Related source inspiration: https://github.com/obra/superpowers/blob/main/skills/using-superpowers/SKILL.md
- This is a research and decision issue. Keep any experiments under ignored local paths unless the maintainer approves tracked prototype artifacts.
