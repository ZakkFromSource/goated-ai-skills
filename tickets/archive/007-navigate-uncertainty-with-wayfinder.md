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

- [x] Wayfinder activates only for branching uncertainty that exceeds one
      focused session.
- [x] Session-sized discussion and already-specified large implementation are
      rejected and routed elsewhere.
- [x] Map creation requires approval of destination, location, frontier, action
      reach, and initial write scope.
- [x] Local maps and decision tickets follow the portable V2 artifact contract.
- [x] Grilling, research, prototype, and prerequisite tickets classify HITL or
      AFK independently.
- [x] Fog, frontier, blockers, decisions, and out-of-scope work update without
      duplicating authoritative detail.
- [x] Active, blocked, on-hold, destination-ready, completed, and dropped states
      behave as specified.
- [x] Production execution is prohibited.
- [x] Destination handoff reuses settled decisions and evidence.

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

## Implementation Proof

- `skills/agent-workflows/wayfinder/SKILL.md` and its local artifact-template
  reference implement the standalone and integrated workflow without requiring
  this source repo, a remote tracker, subagents, or runtime concurrency.
- Ten fixtures under `stack/fixtures/wayfinding/` cover selection, both
  rejection routes, local Markdown maps and decision records, fog/frontier and
  blocker updates, independent decision type/mode classification, every
  lifecycle state plus evidence-driven transitions, no-execution pressure, and
  handoffs to spec and architecture destinations.
- Validator mutation tests reject missing chart approval, incorrect rejection
  routes, malformed decision samples, delivery-ticket contamination, unlinked
  frontier records, duplicate or missing lifecycle coverage, production
  execution, unlinked completion, and discovery-discarding handoffs.
- Live RED/GREEN pressure evaluation showed that the skill strengthens a
  baseline refusal into an explicit Wayfinder boundary, a
  `destination-ready` versus `completed` decision, and an evidence-reusing
  destination handoff. Deadline, available code, and a map note could not
  authorize production execution.
- `uv run python -m unittest discover -s tests -v` passed 49 tests before
  lifecycle closeout. `uv run python scripts/validate_skills.py` passed 33
  skills, 33 registry entries, and all fixture families, including ten
  Wayfinding scenarios, with zero blocking errors or human-review notes.
- The shared policy remains 1,183 words, within its 800-1,200 target. Three
  unrelated learning-capture drift findings remain report-only.
- `git diff --check` passed. Focused spec re-review found no remaining findings;
  security review was not applicable because the change adds no auth, user
  data, executable side effect, or external-action path.
