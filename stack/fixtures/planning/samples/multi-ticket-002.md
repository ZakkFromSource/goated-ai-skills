# Ticket 002: Migrate Contract Consumers

## Parent Spec

`docs/specs/2026-07-25-workflow-migration.md`

## Type

AFK

## What To Build

Move current consumers onto the compatible contract and prove the end-to-end
migration outcome.

## Recommended First Reads

- `docs/specs/2026-07-25-workflow-migration.md` — rollout and acceptance.
- `tickets/001-establish-compatible-contract.md` — prerequisite contract.
- `src/consumers/` — current consumers.

## Relevant Source Links

- `tests/integration/` — end-to-end consumer proof.

## Acceptance Criteria

- [ ] All named consumers use the compatible contract.
- [ ] The end-to-end workflow remains available without legacy-only behavior.

## Expected Proof

- Consumer-focused tests and the end-to-end workflow suite.

## Blocked By

- `tickets/001-establish-compatible-contract.md`

## Scope Exclusions

- Do not remove compatibility support until the spec's rollout gate is met.
- Do not change unrelated consumer behavior.
