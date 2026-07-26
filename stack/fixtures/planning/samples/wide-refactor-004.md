# Ticket 004: Contract The Legacy Shared Symbol

## Parent Spec

`docs/specs/2026-07-25-shared-symbol-migration.md`

## Type

AFK

## What To Build

Remove the legacy shared symbol only after every bounded migration batch is
complete and repository-wide evidence proves no old caller remains.

## Recommended First Reads

- `docs/specs/2026-07-25-shared-symbol-migration.md` — removal gate.
- `tickets/002-migrate-core-consumers.md` — completed core migration.
- `tickets/003-migrate-adapter-consumers.md` — completed adapter migration.

## Relevant Source Links

- `src/` — repository-wide legacy-form search surface.
- `tests/` — full compatibility proof after removal.

## Acceptance Criteria

- [ ] No caller of the legacy shared symbol remains.
- [ ] The legacy form is removed without breaking the new contract.

## Expected Proof

- Repository-wide old-caller search with no matches.
- Full relevant test suite after legacy-form removal.

## Blocked By

- `tickets/002-migrate-core-consumers.md`
- `tickets/003-migrate-adapter-consumers.md`

## Scope Exclusions

- Do not remove unrelated compatibility behavior.
- Do not publish or deploy the migration.
