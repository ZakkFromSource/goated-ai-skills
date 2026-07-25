# Ticket Slicing Templates

## Proposed Batch

```markdown
# Proposed Delivery Tickets

Source spec: `<path>`
Approval: <reused | requested because scope/reach changed | not yet covered>

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

## Coverage

- `<spec acceptance criterion>` → `<ticket path>`
```

The order file is regenerated from the full approved set. It is not a remote
tracker sync, a global index, or an implementation plan.
