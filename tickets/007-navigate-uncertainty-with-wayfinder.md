# Ticket 007: Navigate Multi-Session Uncertainty With Wayfinder

## Parent Spec

`docs/specs/2026-07-25-goated-ai-skills-v2.md`

## Type

AFK

## What To Build

Add a GOATED-native Wayfinder workflow that charts only the visible decision
frontier, persists local decision maps when needed, and hands resolved evidence
to a named planning destination without entering production execution.

## Recommended First Reads

- `docs/specs/2026-07-25-goated-ai-skills-v2.md` — Wayfinder
- `skills/engineering/grill-with-docs/SKILL.md`
- `skills/productivity/grill-me/SKILL.md`
- `skills/engineering/prototype/SKILL.md`
- Canonical V2 spec and architecture skills created by Tickets 005 and 006

## Relevant Source Links

- `docs/wayfinding/` — planned target-project fallback convention
- `stack/goated-stack.yaml`
- `README.md` — existing project-level inspiration attribution

## Acceptance Criteria

- [ ] Wayfinder activates only for branching uncertainty that exceeds one
      focused session.
- [ ] Session-sized discussion and already-specified large implementation are
      rejected and routed elsewhere.
- [ ] Map creation requires approval of destination, location, frontier, action
      reach, and initial write scope.
- [ ] Local maps and decision tickets follow the portable V2 artifact contract.
- [ ] Grilling, research, prototype, and prerequisite tickets classify HITL or
      AFK independently.
- [ ] Fog, frontier, blockers, decisions, and out-of-scope work update without
      duplicating authoritative detail.
- [ ] Active, blocked, on-hold, destination-ready, completed, and dropped states
      behave as specified.
- [ ] Production execution is prohibited.
- [ ] Destination handoff reuses settled decisions and evidence.

## Expected Proof

- Wayfinder selection and rejection fixtures.
- Local-Markdown fallback fixture.
- Fog-graduation and blocker-update fixture.
- Every lifecycle-state transition fixture.
- No-execution pressure scenario.
- Handoff-to-spec and handoff-to-architecture scenarios.
- Validator and word-budget output.

## Blocked By

- `tickets/004-clarify-decisions-proportionally.md`
- `tickets/005-turn-specs-into-delivery-tickets.md`
- `tickets/006-design-architecture-and-plans-proportionally.md`

## User Stories Addressed

- Derived: As a user, I can resolve a large branching idea across sessions
  without pretending that its entire route is already knowable.

## Implementation Route

- Use `framework-agnostic-skill-creator` in create mode.
- Use `writing-plans` for the skill, local templates, registry entry, docs, and
  fixtures.

## Scope Exclusions

- Do not copy the supplied source skill or its tracker-specific commands.
- Do not require a remote issue tracker, subagents, fixed context size, or
  runtime concurrency enforcement.
- Do not let Notes override the no-execution boundary.
