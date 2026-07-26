# Ticket 003: Migrate Adapter Consumers

## Parent Spec

`docs/specs/2026-07-25-shared-symbol-migration.md`

## Type

AFK

## What To Build

Move adapter-directory consumers to the expanded shared symbol contract as one
bounded batch aligned with adapter ownership and contract suites.

## Recommended First Reads

- `docs/specs/2026-07-25-shared-symbol-migration.md` — approved migration boundaries.
- `tickets/001-expand-shared-symbol-contract.md` — compatible prerequisite.
- `src/adapters/` — adapter callers in this batch.

## Relevant Source Links

- `tests/adapters/` — focused proof boundary for this batch.

## Acceptance Criteria

- [ ] Adapter callers use the new shared symbol.
- [ ] The repository remains green with no required contract removal.

## Expected Proof

- Focused adapter tests and the nearby compatibility suite.

## Blocked By

- `tickets/001-expand-shared-symbol-contract.md`

## Scope Exclusions

- Do not revisit migrated core callers.
- Do not remove the legacy shared symbol.
