# Ticket Slicing Templates

## Contents

- [Wide-Refactor Sequence](#wide-refactor-sequence)
- [Proposed Batch](#proposed-batch)
- [Delivery Ticket](#delivery-ticket)
- [Multi-Ticket Order](#multi-ticket-order)

## Wide-Refactor Sequence

Use this branch only when one mechanical contract change fans across a blast
radius too broad for one safe ticket, replacing the form directly would break
existing callers, and no ordinary vertical slice can land green. Size alone,
many files, or ordinary product work does not qualify.

1. **Expand:** Introduce the new form beside the old without breaking existing
   callers.
2. **Migrate:** Move callers in bounded batches, each blocked by expand. Size
   batches from current evidence such as package or directory ownership,
   caller counts, dependency boundaries, focused test surfaces, and risk.
   Record the basis; do not choose arbitrary equal sizes. Each batch should
   leave the repository green while the old form remains.
3. **Contract:** Remove the old form only after every migration batch. Block
   contract on every migrate ticket and require repository-wide proof that no
   old caller remains plus relevant tests after removal.

Use a shared integration branch only when evidence shows migration batches
cannot remain green independently. Record why, keep every batch blocked by
expand, make every batch block a final integrate-and-verify ticket, and promise
green only at that final gate. Contract remains blocked by every migration
batch and the final integration gate. Never use this exception merely because
coordination is convenient.

## Proposed Batch

```markdown
# Proposed Delivery Tickets

Source spec: `<path>`
Approval: <reused | requested because scope/reach changed | not yet covered>
Slice strategy: <vertical | wide-refactor with qualifying blast-radius evidence>

1. `NNN-short-title.md` — <vertical outcome>
   - Blocked by: <ticket IDs or none>
   - Covers: <spec acceptance criteria>

Order file: `tickets/<spec-slug>-order.md` or `Skipped — single ticket`
```

## Delivery Ticket

```markdown
# Ticket NNN: <Vertical Outcome>

## Parent Spec

`<path>`

## Type

<AFK | HITL — name the required gate>

## What To Build

<Stable outcome and why this slice is coherent.>

## Recommended First Reads

- `<path>` — <why it matters>

## Relevant Source Links

- `<path or durable reference>`

## Acceptance Criteria

- [ ] <Observable condition>

## Expected Proof

- <Command category, test surface, manual review, or artifact evidence>

## Blocked By

- `<ticket path>` or `None`

## Wide-Refactor Phase

<Omit for vertical work. For expand, migrate, or contract, name the phase.
Migrate tickets also name the evidence-backed batch boundary. Contract states
the proof that no old callers remain.>

## User Stories Addressed

- <Story or omit when it adds no useful context>

## Scope Exclusions

- <Explicitly excluded adjacent work>
```

## Multi-Ticket Order

```markdown
# <Spec Name> Delivery Order

Source spec: `<path>`

1. `NNN-first-ticket.md`
   - Blocked by: None
   - Enables: <dependent outcome>
2. `NNN-second-ticket.md`
   - Blocked by: `NNN-first-ticket.md`
   - Enables: <dependent outcome or final delivery>

## Ready Frontier

- `<uncompleted ticket path whose blockers are all complete>`

## Coverage

- `<spec acceptance criterion>` → `<ticket path>`
```

For a wide refactor, order expand first, then evidence-bounded migrate tickets,
then contract blocked by every migrate ticket. The order file is regenerated
from the full approved set, including its computed ready frontier. It is not a
remote tracker sync, a global index, or an implementation plan.
