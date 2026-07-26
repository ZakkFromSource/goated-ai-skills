# Selective Upstream Skill Adoption Delivery Order

Source spec:
`docs/specs/2026-07-26-selective-upstream-skill-adoption.md`

This order separates the approved high-confidence delivery batch from two
evidence-gated experiments. It is not authorization to start conditional
implementation tickets before their maintainer gates are satisfied.

## Phase A: High-Confidence Adoption

1. `tickets/015-sharpen-skill-authoring-discipline.md`
   - Blocked by: None
   - Enables: new skills to use the refined authoring and evaluation contract.
2. `tickets/016-minimize-diagnostic-reproductions.md`
   - Blocked by: None
   - Enables: independent diagnosis refinement.
3. `tickets/017-slice-wide-refactors-safely.md`
   - Blocked by: None
   - Enables: independent wide-refactor planning.
4. `tickets/018-add-resolving-merge-conflicts.md`
   - Blocked by: Ticket 015
   - Enables: intent-preserving Git conflict resolution.
5. `tickets/019-add-source-grounded-research.md`
   - Blocked by: Ticket 015
   - Enables: reusable external-research evidence and optional support for
     Ticket 021.
6. `tickets/020-accept-high-confidence-adoption-batch.md`
   - Blocked by: Tickets 015 through 019
   - Enables: maintainer acceptance of the independent adoption release.

Tickets 016 and 017 may run alongside Ticket 015 when their write scopes do not
overlap. Tickets 018 and 019 are logically parallel after Ticket 015, but any
validator edits must be sequenced with each other and with active Ticket 013.

## Phase B: Invocation Topology

1. `tickets/021-investigate-invocation-topology.md`
   - Blocked by: None
   - Enables: maintainer go/revise/no-go decision and first-consumer choice.
2. `tickets/022-implement-invocation-topology.md`
   - Blocked by: Ticket 021 plus an explicit go decision
   - Enables: accepted registry and adapter behavior.

Ticket 021 may reuse Ticket 019 after it is implemented, but Ticket 019 is not a
hard blocker because the parent spec contains a standalone research contract.

## Phase C: Active Domain Modeling

1. `tickets/023-evaluate-active-domain-modeling.md`
   - Blocked by: Ticket 015
   - Enables: maintainer go/revise/no-go decision.
2. `tickets/024-add-active-domain-modeling.md`
   - Blocked by: Ticket 023 plus an explicit go decision
   - Enables: the accepted narrow domain-modeling remedy.

## Frontier

The initial ready frontier is:

- Ticket 015
- Ticket 016
- Ticket 017
- Ticket 021

Ticket 023 joins the frontier when Ticket 015 completes. Tickets 018 and 019
also join after Ticket 015. Conditional Tickets 022 and 024 never join the
frontier without their recorded maintainer go decisions.

## Acceptance-Criteria Coverage

- AC1 -> Ticket 015
- AC2 -> Ticket 016
- AC3 -> Ticket 017
- AC4 -> Ticket 018
- AC5 -> Ticket 019
- AC6 -> Ticket 021
- AC7 -> Ticket 022
- AC8 -> Ticket 023
- AC9 -> Ticket 024
- AC10 -> Tickets 015 through 020, 022, and 024
- AC11 -> every implementation ticket, consolidated by Ticket 020

## Deferred Separate Product Tracks

The parent spec records but does not ticket:

- work-management setup, triage, and remote publishing;
- optional architecture hotspot and review ergonomics;
- guided learning; and
- installer, marketplace, or adapter-generation CLI work.

Each requires a separate approved spec because it changes external action reach,
product boundaries, or distribution ownership.
