# Spec Template

Use the smallest useful shape. Compact mode uses the core sections. Full mode
adds only the justified depth sections; omit empty sections.

```markdown
# <Outcome Or Capability>

## Status

<Draft | Decision Needed | Approved | Ticket Ready>

## Mode

<Compact | Full>

## Problem

<Current problem, affected people, and why it matters.>

## Goals

- <Observable outcome>

## Non-Goals

- <Explicit exclusion>

## Requirements

- <Capability or durable constraint>

## Acceptance Criteria

- [ ] <Observable proof condition>

## Constraints

- <Technical, product, policy, timing, compatibility, or resource constraint>

## Open Questions

- <Decision owner and why the answer matters, or "None">

## Stakeholders

<Full mode only when coordination or ownership affects delivery.>

## Architecture

<Full mode only for accepted system constraints or seams, not an implementation plan.>

## Rollout

<Full mode only when staged enablement, compatibility, or rollback matters.>

## Migration

<Full mode only when existing users, data, interfaces, or artifacts must move.>

## Analytics

<Full mode only when success or safety requires measurement.>

## Risks

- <Risk, consequence, mitigation, and decision owner>

## Sources

- `<path or durable reference>` — <fact or constraint supported>
```

Review rules:

- Preserve stable intent and link evidence instead of copying it.
- Make acceptance criteria independently verifiable.
- Keep implementation order and volatile command details for
  `writing-plans`.
