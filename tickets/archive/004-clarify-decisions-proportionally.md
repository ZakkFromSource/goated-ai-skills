# Ticket 004: Clarify Decisions Proportionally

## Parent Spec

`docs/specs/2026-07-25-goated-ai-skills-v2.md`

## Type

AFK

## What To Build

Let users choose focused, rapid, recommend-and-proceed, or unlimited deep-dive
clarification while keeping discoverable facts out of the interview and using
prototypes only when they raise decision fidelity.

## Recommended First Reads

- `docs/specs/2026-07-25-goated-ai-skills-v2.md` — Grilling and Product
  Principles
- `skills/engineering/grill-with-docs/SKILL.md`
- `skills/productivity/grill-me/SKILL.md`
- `skills/engineering/prototype/SKILL.md`
- `stack/templates/work-envelope.md`

## Relevant Source Links

- `skills/engineering/grill-with-docs/references/`
- `skills/engineering/prototype/references/`

## Acceptance Criteria

- [x] Both grill skills support `focused`, `rapid`,
      `recommend-and-proceed`, and `deep-dive`.
- [x] Rapid mode asks no more than three tightly related questions.
- [x] Deep-dive mode has no arbitrary question limit and periodically
      summarizes settled, provisional, deferred, and conflicting decisions.
- [x] Recommend-and-proceed cannot silently default irreversible or high-risk
      decisions.
- [x] Workflow intensity supplies a soft question budget outside deep-dive.
- [x] Docs-grounded grilling reuses evidence before asking discoverable facts.
- [x] Prototype routing produces decision evidence rather than production work.
- [x] The clarified result updates the shared envelope without a duplicate full
      closeout.

## Expected Proof

- Lightweight no-question or one-question fixture.
- Three-question rapid fixture.
- Irreversible-decision focused fixture.
- Large architecture deep-dive fixture.
- Prototype-needed and prototype-not-needed fixtures.
- Validator and word-budget output.

## Blocked By

- `tickets/archive/002-route-work-through-adaptive-gates.md`

## User Stories Addressed

- Derived: As a user, I can choose a fast interview or a comprehensive
  architectural brainstorm without losing decision quality.

## Implementation Route

- Use `writing-plans` to update the two grill skills, prototype routing, shared
  decision delta, and fixtures together.

## Scope Exclusions

- Do not turn every discussion into a durable spec or Wayfinder map.
- Do not allow an agent to answer the human side of a HITL decision.

## Implementation Proof

- `uv run python -m unittest discover -s tests -v` passed 26 tests, including
  six clarification-fixture validator behaviors.
- `uv run python scripts/validate_skills.py` passed 32 implemented skills, 32
  registry entries, 7 adaptive-routing fixtures, 4 onboarding fixtures, and 6
  clarification fixtures with zero blocking errors or human-review notes.
- The shared policy is 1,183 words, within its 800-1,200 soft target. Existing
  skill decomposition warnings and three unrelated learning-capture drift notes
  remain report-only.
- `uv run python -m compileall -q scripts tests` and `git diff --check` passed.
- Manual standards/spec review found no findings. Documentation sync updated the
  context matrix and project standards for the Ticket 004 fixture contract.
