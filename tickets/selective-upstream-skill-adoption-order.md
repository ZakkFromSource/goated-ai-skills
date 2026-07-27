# Selective Upstream Skill Adoption Delivery Order

Source spec:
`docs/specs/2026-07-26-selective-upstream-skill-adoption.md`

This order separates the approved high-confidence delivery batch from two
evidence-gated experiments. It is not authorization to start conditional
implementation tickets before their maintainer gates are satisfied.

## Phase A: High-Confidence Adoption

1. `tickets/archive/015-sharpen-skill-authoring-discipline.md`
   - Status: Completed and archived.
   - Blocked by: None
   - Enables: new skills to use the refined authoring and evaluation contract.
2. `tickets/archive/016-minimize-diagnostic-reproductions.md`
   - Status: Completed and archived.
   - Blocked by: None
   - Enables: independent diagnosis refinement.
3. `tickets/archive/017-slice-wide-refactors-safely.md`
   - Status: Completed and archived.
   - Blocked by: None
   - Enables: independent wide-refactor planning.
4. `tickets/archive/018-add-resolving-merge-conflicts.md`
   - Status: Completed and archived.
   - Blocked by: Ticket 015
   - Enables: intent-preserving Git conflict resolution.
5. `tickets/archive/019-add-source-grounded-research.md`
   - Status: Completed and archived.
   - Blocked by: Ticket 015
   - Enables: reusable external-research evidence and optional support for
     Ticket 021.
6. `tickets/archive/020-accept-high-confidence-adoption-batch.md`
   - Status: Accepted with residual risk and archived.
   - Blocked by: Tickets 015 through 019
   - Enables: maintainer acceptance of the independent adoption release.

Tickets 016 and 017 could run alongside Ticket 015 when their write scopes did
not overlap. Phase A is accepted with residual risk. The maintainer selected
`tickets/archive/013-split-validator-by-concern.md` as the next slice and
requested its baseline be refreshed for the accepted validator growth before
implementation. That slice is now completed and archived.

## Phase B: Invocation Topology

1. `tickets/archive/021-investigate-invocation-topology.md`
   - Status: Completed with maintainer no-go and archived.
   - Blocked by: None
   - Result: no production consumer or invocation metadata accepted.
2. `tickets/archive/022-implement-invocation-topology.md`
   - Status: Not authorized; closed without implementation and archived.
   - Blocked by: Ticket 021's maintainer no-go decision
   - Result: no registry, schema, validator, adapter, or installation changes.

Ticket 021 reused Ticket 019's research workflow. Ticket 019 was not a hard
blocker because the parent spec also contained a standalone research contract.
Phase B concluded on 2026-07-27. Any future caller-aware invocation harness is
a separate product track requiring its own spec and approval.

## Phase C: Active Domain Modeling

1. `tickets/023-evaluate-active-domain-modeling.md`
   - Blocked by: Ticket 015
   - Enables: maintainer go/revise/no-go decision.
2. `tickets/024-add-active-domain-modeling.md`
   - Blocked by: Ticket 023 plus an explicit go decision
   - Enables: the accepted narrow domain-modeling remedy.

## Frontier

The current ready frontier is:

- Ticket 023

Tickets 013 and 015 through 021 are complete. Ticket 022 closed without
implementation after the invocation no-go. Conditional Ticket 024 never joins
the frontier without its recorded maintainer go decision.

## Acceptance-Criteria Coverage

- AC1 -> Ticket 015
- AC2 -> Ticket 016
- AC3 -> Ticket 017
- AC4 -> Ticket 018
- AC5 -> Ticket 019
- AC6 -> archived Ticket 021
- AC7 -> not applicable after Ticket 021's no-go; archived Ticket 022 records
  that no invocation metadata was accepted or implemented
- AC8 -> Ticket 023
- AC9 -> Ticket 024
- AC10 -> Tickets 015 through 020 and conditional Ticket 024
- AC11 -> every implementation ticket, consolidated by Ticket 020

## Deferred Separate Product Tracks

The parent spec records but does not ticket:

- work-management setup, triage, and remote publishing;
- optional architecture hotspot and review ergonomics;
- custom invocation-policy or caller-aware routing harnesses;
- guided learning; and
- installer, marketplace, or adapter-generation CLI work.

Each requires a separate approved spec because it changes external action reach,
product boundaries, or distribution ownership.
