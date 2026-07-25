# Ticket 009: Prove Behaviour Without Mandatory Refinement

## Parent Spec

`docs/specs/2026-07-25-goated-ai-skills-v2.md`

## Type

AFK

## What To Build

Deliver a direct diagnosis-to-proof implementation route that chooses the
smallest stable test surface, permits justified equivalent proof, invokes full
refinement only from observed debt, and delegates only independently ownable
work.

## Recommended First Reads

- `docs/specs/2026-07-25-goated-ai-skills-v2.md` — TDD, Code Refinement, and
  Direct Transitions And Narrow Fast Paths
- `skills/engineering/diagnose/SKILL.md`
- `skills/engineering/tdd/SKILL.md`
- `skills/engineering/code-refinement/SKILL.md`
- `skills/engineering/subagent-driven-development/SKILL.md`

## Relevant Source Links

- `skills/engineering/tdd/references/`
- `skills/engineering/code-refinement/references/`
- `stack/goated-stack.yaml`

## Acceptance Criteria

- [ ] A requested bug fix continues from established diagnosis into
      implementation without redundant authorization.
- [ ] Unit, property, component, contract, integration, and end-to-end tests
      are selected by the smallest stable observable boundary.
- [ ] Integration tests are not preferred merely for being broader.
- [ ] Equivalent proof requires a recorded reason when TDD is unsuitable.
- [ ] Refactor-after-green remains inside the TDD cycle.
- [ ] Full `code-refinement` activates only from explicit request or concrete
      refinement debt.
- [ ] Run-or-explicit-skip refinement language is removed.
- [ ] Delegated development requires a concrete task board with non-overlapping
      write scopes and settled shared interfaces.

## Expected Proof

- Root-cause bug-fix fixture.
- Pure-unit, property, component, and contract proof fixtures.
- Justified non-TDD fixture.
- Refinement-debt and no-debt comparison.
- Generated-code cleanup fixture.
- Independent and overlapping delegation fixtures.
- Focused validator and instruction-size output.

## Blocked By

- `tickets/archive/002-route-work-through-adaptive-gates.md`

## User Stories Addressed

- Derived: As a maintainer, I can prove behaviour changes without paying for
  unnecessary integration tests, approval pauses, or refinement passes.

## Implementation Route

- Use `writing-plans` for the diagnosis, proof, refinement, delegation,
  registry, and fixture changes.
- Apply TDD to any validator or executable behaviour introduced by this ticket.

## Scope Exclusions

- Do not weaken readability, regression proof, or completion evidence.
- Do not introduce runtime worker orchestration, worktrees, or Factory task
  boards.
