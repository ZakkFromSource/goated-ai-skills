# Wayfinder Artifact Templates

## Contents

- [Location](#location)
- [Map](#map)
- [Decision Record](#decision-record)
- [Update Rules](#update-rules)

Use these templates when no configured tracker supplies an equivalent durable
map and decision-record model.

## Location

```text
docs/wayfinding/<effort-slug>/
  map.md
  decisions/
    001-<decision-title>.md
```

Use stable links between artifacts. Decision records are not delivery tickets:
they resolve uncertainty before a named planning destination takes over.

## Map

```markdown
# Wayfinder: <Effort>

## Destination

<Named planning artifact or decision that must exist.>

## Completion Condition

<Evidence that proves the destination exists.>

## State

<active | blocked | on-hold | destination-ready | completed | dropped>

## State Detail

- Reason: <required for blocked, on-hold, or dropped>
- Resume or review condition: <when relevant>
- Replacement: <when a dropped effort has one>
- Destination link: <required for completed>

## Standing Notes And Constraints

<Durable scope, approval, and operating constraints. These never authorize
production execution.>

## Decisions So Far

- [<decision title>](decisions/001-title.md) - <one-line gist only>

## Current Frontier

- [<precise open decision>](decisions/002-title.md) - <blocker link if any>

## Not Yet Specified

- <in-scope uncertainty that cannot yet be phrased as a precise question>

## Out Of Scope

- <work beyond the destination and why>
```

## Decision Record

```markdown
# Decision: <Title>

## Type

<grilling | research | prototype | prerequisite>

## Mode

<AFK | HITL>

## Status

<open | blocked | resolved | dropped>

## Blockers

- <stable link or identifier; use `None` when unblocked>

## Question

<One precise question this record resolves.>

## Evidence Or Asset Links

- <source, prototype, command, or evidence-entry link with freshness context>

## Resolution

<Settled answer, or `Unresolved` while open.>
```

## Update Rules

- A fact or decision has one authoritative home. The map keeps a gist and link.
- Fog graduates by being removed from `Not Yet Specified` and represented by
  one or more precise decision records.
- Blockers are updated by link or identifier, not copied descriptions.
- Out-of-scope work does not graduate unless the destination is explicitly
  redrawn with fresh approval.
- Completion requires a real, linked destination artifact. A handoff request or
  draft intention is not completion.
