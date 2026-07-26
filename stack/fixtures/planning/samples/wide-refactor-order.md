# Shared Symbol Migration Delivery Order

Source spec: `docs/specs/2026-07-25-shared-symbol-migration.md`

1. `tickets/001-expand-shared-symbol-contract.md`
   - Phase: Expand
   - Blocked by: None
   - Enables: bounded consumer migration batches.
2. `tickets/002-migrate-core-consumers.md`
   - Phase: Migrate
   - Blocked by: `tickets/001-expand-shared-symbol-contract.md`
   - Batch basis: package ownership and focused package test boundaries.
3. `tickets/003-migrate-adapter-consumers.md`
   - Phase: Migrate
   - Blocked by: `tickets/001-expand-shared-symbol-contract.md`
   - Batch basis: adapter directory ownership and adapter contract suites.
4. `tickets/004-contract-legacy-shared-symbol.md`
   - Phase: Contract
   - Blocked by: `tickets/002-migrate-core-consumers.md`, `tickets/003-migrate-adapter-consumers.md`
   - Enables: migration completion after old-caller absence is proved.

## Ready Frontier

- `tickets/001-expand-shared-symbol-contract.md`

## Coverage

- Compatible expansion → `tickets/001-expand-shared-symbol-contract.md`
- Bounded migration → `tickets/002-migrate-core-consumers.md`, `tickets/003-migrate-adapter-consumers.md`
- Proven legacy removal → `tickets/004-contract-legacy-shared-symbol.md`
