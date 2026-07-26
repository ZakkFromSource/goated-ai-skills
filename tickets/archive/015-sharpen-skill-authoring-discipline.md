# Ticket 015: Sharpen Skill Authoring Discipline

## Parent Spec

`docs/specs/2026-07-26-selective-upstream-skill-adoption.md`

## Type

AFK

## Work State

Completed and archived on 2026-07-26.

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

- [x] The authoring workflow asks whether independent invocation and context
      visibility earn their cost.
- [x] Important phases require observable completion criteria.
- [x] Evaluation checks no-op guidance, duplicated ownership, premature
      completion pressure, branch-specific disclosure, and positive steering.
- [x] New vocabulary remains an evaluation lens rather than mandatory GOATED
      terminology.
- [x] Existing RED/GREEN pressure evaluation and standalone portability remain
      intact.
- [x] Focused tests or fixtures cover at least one instruction that should be
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

## Implementation Proof

- The creator now prices independent invocation and context visibility, requires
  observable phase completion, and remains a 1,451-word standalone skill below
  the validator's 1,500-word decomposition threshold.
- The evaluation reference adds compact authoring lenses for no-op pruning,
  singular ownership, branch disclosure, sequence pressure, positive steering,
  and useful leading concepts. It explicitly treats those labels as optional
  evaluation language.
- Focused contract RED failed three tests against the previous authoring
  contract. GREEN passes those same tests for invocation/completion, removal of
  `"Be clear and thorough."` as a no-op, and branch-specific disclosure of a
  port-only compatibility matrix.
- Manual ownership comparison kept universal scope, approval, evidence,
  routing, and closeout behavior authoritative in `stack/AGENTS.md`; the
  creator only tests for duplication and points to the owner.
- `uv run python scripts/validate_skills.py` passed 35 implemented skills, 35
  registry entries, every fixture family, and zero human-review notes.
- `uv run python -m unittest discover -s tests -v` passed all 97 tests.
- `uv run python scripts/compare_v1_v2_context.py` confirmed all four
  representative routes retain the required 10% reduction.
- Manual Markdown, link, public-boundary, standalone-package, diff, and
  whitespace review found no ticket-scoped blocker. Three pre-existing Learning
  Capture schema examples remain report-only drift.
