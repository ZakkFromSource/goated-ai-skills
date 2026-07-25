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

- [ ] Both grill skills support `focused`, `rapid`,
      `recommend-and-proceed`, and `deep-dive`.
- [ ] Rapid mode asks no more than three tightly related questions.
- [ ] Deep-dive mode has no arbitrary question limit and periodically
      summarizes settled, provisional, deferred, and conflicting decisions.
- [ ] Recommend-and-proceed cannot silently default irreversible or high-risk
      decisions.
- [ ] Workflow intensity supplies a soft question budget outside deep-dive.
- [ ] Docs-grounded grilling reuses evidence before asking discoverable facts.
- [ ] Prototype routing produces decision evidence rather than production work.
- [ ] The clarified result updates the shared envelope without a duplicate full
      closeout.

## Expected Proof

- Lightweight no-question or one-question fixture.
- Three-question rapid fixture.
- Irreversible-decision focused fixture.
- Large architecture deep-dive fixture.
- Prototype-needed and prototype-not-needed fixtures.
- Validator and word-budget output.

## Blocked By

- `tickets/002-route-work-through-adaptive-gates.md`

## User Stories Addressed

- Derived: As a user, I can choose a fast interview or a comprehensive
  architectural brainstorm without losing decision quality.

## Implementation Route

- Use `writing-plans` to update the two grill skills, prototype routing, shared
  decision delta, and fixtures together.

## Scope Exclusions

- Do not turn every discussion into a durable spec or Wayfinder map.
- Do not allow an agent to answer the human side of a HITL decision.
