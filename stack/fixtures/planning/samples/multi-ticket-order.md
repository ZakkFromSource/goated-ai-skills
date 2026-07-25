# Workflow Migration Delivery Order

Source spec: `docs/specs/2026-07-25-workflow-migration.md`

1. `tickets/001-establish-compatible-contract.md`
   - Blocked by: None
   - Enables: consumer migration.
2. `tickets/002-migrate-consumers.md`
   - Blocked by: `tickets/001-establish-compatible-contract.md`
   - Enables: completed migration proof.

## Coverage

- Compatible public contract → `tickets/001-establish-compatible-contract.md`
- Migrated consumer behavior → `tickets/002-migrate-consumers.md`
