# Ticket 015: Sharpen Skill Authoring Discipline

## Parent Spec

`docs/specs/2026-07-26-selective-upstream-skill-adoption.md`

## Type

AFK

## What To Build

Refine `framework-agnostic-skill-creator` and its evaluation reference with a
compact, behavior-focused discipline for invocation value, context load,
observable completion, no-op pruning, duplication, branch disclosure,
sequence pressure, positive steering, and useful leading concepts.

Keep shared policy authoritative for universal behavior. Add guidance only
where it changes skill-authoring judgment or evaluation.

## Recommended First Reads

- `AGENT.md` — source-repo and public-boundary rules.
- `docs/specs/2026-07-26-selective-upstream-skill-adoption.md` — approved
  contract, especially R1.
- `skills/agent-workflows/framework-agnostic-skill-creator/SKILL.md` — current
  workflow.
- `skills/agent-workflows/framework-agnostic-skill-creator/references/skill-evaluation.md`
  — current evaluation loop.
- `stack/AGENTS.md` — shared ownership to avoid duplicating.

## Relevant Source Links

- `scripts/validate_skills.py`
- `tests/test_validate_skills.py`
- `issues/archive/043-research-skill-trigger-eval-harnesses.md`
- `https://github.com/mattpocock/skills/blob/main/skills/productivity/writing-great-skills/SKILL.md`

## Acceptance Criteria

- [ ] The authoring workflow asks whether independent invocation and context
      visibility earn their cost.
- [ ] Important phases require observable completion criteria.
- [ ] Evaluation checks no-op guidance, duplicated ownership, premature
      completion pressure, branch-specific disclosure, and positive steering.
- [ ] New vocabulary remains an evaluation lens rather than mandatory GOATED
      terminology.
- [ ] Existing RED/GREEN pressure evaluation and standalone portability remain
      intact.
- [ ] Focused tests or fixtures cover at least one instruction that should be
      removed as a no-op and one workflow that should be split or progressively
      disclosed.

## Expected Proof

- Focused validator or contract tests for new authoring expectations.
- Manual comparison against shared policy for duplicate ownership.
- RED/GREEN or planned scenario evidence following the existing evaluation
  reference.
- Fresh repository acceptance commands required by the parent spec.

## Blocked By

None.

Ticket 013 is not a functional dependency. Sequence overlapping validator
edits if its refactor is in progress.

## User Stories Addressed

- As a skill maintainer, I can tell whether every instruction and skill boundary
  earns its ongoing context and maintenance cost.

## Implementation Route

- Use `writing-plans` immediately before editing.
- Use `framework-agnostic-skill-creator` in revise mode.
- Use TDD or equivalent fixture proof for enforceable contract changes.
- Use `doc-sync` and `verification-before-completion` before closeout.

## Scope Exclusions

- Do not add a new skill-writing skill.
- Do not add a live model benchmark platform or CI trigger harness.
- Do not duplicate universal policy inside the creator.
