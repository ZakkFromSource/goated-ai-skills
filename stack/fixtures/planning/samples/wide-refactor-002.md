# Ticket 002: Migrate Core Consumers

## Parent Spec

`docs/specs/2026-07-25-shared-symbol-migration.md`

## Type

AFK

## What To Build

Move the core package consumers to the expanded shared symbol contract as one
bounded batch aligned with package ownership and focused package tests.

## Recommended First Reads

- `docs/specs/2026-07-25-shared-symbol-migration.md` — approved migration boundaries.
- `tickets/001-expand-shared-symbol-contract.md` — compatible prerequisite.
- `src/core/` — core-package callers in this batch.

## Relevant Source Links

- `tests/core/` — focused proof boundary for this batch.

## Acceptance Criteria

- [ ] Core-package callers use the new shared symbol.
- [ ] The repository remains green with adapter callers still on the legacy form.

## Expected Proof

- Focused core-package tests and the nearby compatibility suite.

## Blocked By

- `tickets/001-expand-shared-symbol-contract.md`

## Scope Exclusions

- Do not migrate adapter callers.
- Do not remove the legacy shared symbol.
