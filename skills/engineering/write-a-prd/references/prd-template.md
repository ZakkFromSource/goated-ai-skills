# PRD Template

Read this reference when writing the default Markdown PRD artifact.

The `SKILL.md` workflow owns readiness judgment, source exploration, scope control, evidence quality, and whether the PRD is ready for `prd-to-issues`. This template preserves the default artifact shape.

```markdown
# PRD: <Feature Or Outcome Name>

## Status

<Draft | Ready for issue breakdown | Blocked>, last updated <YYYY-MM-DD>.

## Problem

<The problem from the user or audience perspective.>

## Audience

- <primary user, maintainer, operator, admin, developer, or stakeholder>

## Goals

- <specific outcome>

## Non-Goals

- <explicitly excluded outcome>

## Requirements

| Requirement | Priority | Notes |
| --- | --- | --- |

## Acceptance Criteria

- [ ] <observable condition that proves the PRD is satisfied>

## Implementation Notes

- <source-grounded architecture, module, data, UI, migration, or integration note>

## Testing And Verification

- <behavior, integration, migration, manual QA, or documentation check>

## Risks And Mitigations

| Risk | Impact | Mitigation |
| --- | --- | --- |

## Open Questions

| Question | Owner | Needed before |
| --- | --- | --- |

## Source Evidence

- <path, command, artifact, or conversation note used as evidence>
```

## Template Checks

- INCLUDE problem, audience, goals, non-goals, requirements, acceptance criteria, implementation notes, testing and verification, risks, open questions, and source evidence.
- KEEP requirements product-focused; do not turn them into issue slices or implementation transcripts.
- MARK unverifiable assumptions and unresolved blockers explicitly.
- PRESERVE source-grounded notes that future `prd-to-issues` work needs, but avoid brittle file inventories or code snippets unless they encode a stable decision.
