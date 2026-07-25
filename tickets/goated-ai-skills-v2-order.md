# GOATED AI Skills V2 Ticket Order

Last updated: 2026-07-25

Parent spec: `docs/specs/2026-07-25-goated-ai-skills-v2.md`

This index records the approved local V2 ticket set and its dependency order.
It is not a remote tracker, generated global backlog, background automation
output, or authorization to implement every ticket without its own scoped
plan.

## Generated Tickets

- `tickets/archive/001-establish-v2-integrated-stack-foundation.md` — Establish
  The V2 Integrated-Stack Foundation (AFK; Work state: Completed; Blocked by:
  None)
- `tickets/archive/002-route-work-through-adaptive-gates.md` — Route Work
  Through Adaptive Gates (AFK; Work state: Completed; Blocked by: Ticket 001)
- `tickets/archive/003-onboard-and-resume-projects-proportionally.md` — Onboard
  And Resume Projects Proportionally (AFK; Work state: Completed; Blocked by:
  Ticket 002)
- `tickets/archive/004-clarify-decisions-proportionally.md` — Clarify Decisions
  Proportionally (AFK; Work state: Completed; Blocked by: Ticket 002)
- `tickets/archive/005-turn-specs-into-delivery-tickets.md` — Turn Specs Into
  Durable Delivery Tickets (AFK; Work state: Completed; Blocked by: Tickets 002
  and 004)
- `tickets/archive/006-design-architecture-and-plans-proportionally.md` — Design
  Architecture And Plans Proportionally (AFK; Work state: Completed; Blocked
  by: Ticket 002)
- `tickets/archive/007-navigate-uncertainty-with-wayfinder.md` — Navigate
  Multi-Session Uncertainty With Wayfinder (AFK; Work state: Completed; Blocked by: Tickets
  004, 005, and 006)
- `tickets/008-retrieve-durable-knowledge-safely.md` — Retrieve Durable
  Knowledge Safely (AFK; Work state: Not started; Blocked by: Ticket 002)
- `tickets/009-prove-behaviour-without-mandatory-refinement.md` — Prove
  Behaviour Without Mandatory Refinement (AFK; Work state: Not started; Blocked
  by: Ticket 002)
- `tickets/010-review-and-verify-conditionally.md` — Review And Verify
  Conditionally (AFK; Work state: Not started; Blocked by: Tickets 002 and 009)
- `tickets/011-produce-concise-docs-prompts-and-closeouts.md` — Produce Concise
  Docs, Prompts, And Closeouts (AFK; Work state: Not started; Blocked by:
  Tickets 002, 005, and 010)
- `tickets/012-complete-and-accept-v2-migration.md` — Complete And Accept The V2
  Migration (HITL; Work state: Not started; Blocked by: Tickets 001 through
  011)

## Recommended Order

1. `tickets/archive/001-establish-v2-integrated-stack-foundation.md`
   - Why now: establishes the shared policy, registry, validation, and V1
     baseline used by every V2 slice.
2. `tickets/archive/002-route-work-through-adaptive-gates.md`
   - Why now: establishes the central route and shared state used by all
     workflow migrations.
3. `tickets/archive/003-onboard-and-resume-projects-proportionally.md`
   - Why now: completes the first end-to-end consumer of the shared route.
4. `tickets/archive/004-clarify-decisions-proportionally.md`
   - Why now: provides the decision workflow needed before specs and Wayfinder.
5. `tickets/archive/005-turn-specs-into-delivery-tickets.md`
   - Why now: establishes the canonical durable planning vocabulary and path.
6. `tickets/archive/006-design-architecture-and-plans-proportionally.md`
   - Why now: completes the architecture and executable-planning route needed
     by Wayfinder destinations.
7. `tickets/archive/007-navigate-uncertainty-with-wayfinder.md`
   - Why now: composes the settled grill, spec, and architecture capabilities.
8. `tickets/008-retrieve-durable-knowledge-safely.md`
   - Why now: adds a separate evidence consumer after the evidence contract is
     stable.
9. `tickets/009-prove-behaviour-without-mandatory-refinement.md`
   - Why now: migrates the implementation proof route on top of central gates.
10. `tickets/010-review-and-verify-conditionally.md`
    - Why now: consumes implementation evidence and makes specialist closeout
      conditional.
11. `tickets/011-produce-concise-docs-prompts-and-closeouts.md`
    - Why now: completes user-facing artifacts after routing and review
      behaviour are stable.
12. `tickets/012-complete-and-accept-v2-migration.md`
    - Why now: performs full migration, conformance, documentation, and human
      acceptance only after all observable slices exist.

Tickets 003, 004, 006, 008, and 009 share only Ticket 002 as a blocker and may
be reordered when a future plan can prove their write scopes do not overlap.
