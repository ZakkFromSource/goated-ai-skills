# Issue Breakdown Templates

Read this reference only after PRD readiness is confirmed and you need artifact shapes for approval, generated issue files, the recommended order file, or the final report.

The `SKILL.md` workflow owns PRD readiness, approval, blocker order, local-only behavior, and fresh-agent-ready standards. These templates preserve output shape; they do not replace workflow judgment.

## Approval Breakdown

Before writing files, present the proposed issue set in dependency order:

```markdown
## Proposed Issue Breakdown

Planned order file: `issues/<parent-slug>-order.md` for multi-issue sets, or "Skipped - single-issue breakdown"

1. <Title>
   - Type: <AFK | HITL>
   - Blocked by: <local planned path/title or "None - can start immediately">
   - User stories addressed: <explicit or derived stories>
   - Recommended first reads: <docs, PRD sections, ADRs, prior issues, or "Parent PRD only">
   - Relevant source links: <paths, anchors, external docs, or "None yet">
   - Acceptance focus: <observable behavior or verification target>
   - Expected proof: <test, review, command, artifact, source read, manual check, or decision evidence>
   - Scope exclusions: <important non-goals, or "None worth calling out">
   - Foundation rationale: <only when relevant; interface, hidden complexity, and unlocked slices>
```

Approval must cover granularity, blocker relationships, user-story coverage, AFK/HITL type, and fresh-agent-ready handoff coverage.

## Issue File

After approval, write each issue in dependency order using the target project's local convention or the default `issues/NNN-short-title.md` convention:

```markdown
## Parent PRD

`<path-to-parent-prd>`

## Type

<AFK | HITL>

## What to build

<Concise description of the vertical slice. Describe the end-to-end behavior, not layer-by-layer implementation.>

## Recommended first reads

- `<parent PRD path or section>`
- `<relevant doc, ADR, prior issue, source file, or "None beyond the parent PRD">`

## Relevant source links

- `<path, URL, ADR, issue, schema, source file, or test that anchors this slice>`

## Acceptance criteria

- [ ] <observable criterion>
- [ ] <observable criterion>

## Expected proof

- <Test, command, source review, artifact review, manual check, or approval evidence expected to prove this issue. Keep this stable; put exact executable steps in `writing-plans`.>

## Blocked by

- `<local issue path>`

Or:

- None - can start immediately

## User stories addressed

- <story from PRD, or "Derived: As a ..., I can ..., so that ...">

## Implementation route

- Use `grill-with-docs` before implementation unless this is a tiny mechanical issue.
- Use `writing-plans` to create exact executable steps after reading this issue and the linked sources.

## Scope exclusions

- <Optional. Include only important exclusions or non-goals that prevent likely scope creep. Omit this section when it adds no value.>

## Implementation notes

- <Optional. Include only source-grounded notes that prevent likely mistakes. Omit this section when it adds no value. Do not turn this section into an implementation transcript.>
```

## Recommended Order File

For approved multi-issue breakdowns, write or refresh the local recommended order file after issue files exist:

```markdown
# <Parent PRD or Planning Artifact Title> Issue Order

Last updated: <YYYY-MM-DD>

Parent PRD or planning artifact: `<path-to-parent-prd-or-planning-artifact>`

This local order file was generated from the approved `prd-to-issues` breakdown. Refresh it from the full approved issue set when `prd-to-issues` runs again; do not append stale entries. It is not a remote tracker sync, generated global index, background automation output, labels/milestones/assignees list, or project-board state.

## Generated Issues

- `<issue path>` - <Title> (<AFK | HITL>; Status: Not started; Blocked by: <issue paths or "None">)

## Recommended Order

1. `<issue path>`
   - Type: <AFK | HITL>
   - Status: Not started
   - Blocked by: <issue paths or "None - can start immediately">
   - Why now: <dependency or blocker-order rationale>
```

For single-issue breakdowns, skip the order file and record the reason in the final report.

## Final Report Checklist

After writing, report:

- issue files created in dependency order;
- order file path for multi-issue breakdowns, or the single-issue skip reason;
- parent PRD path;
- warnings or broad-PRD concerns raised;
- assumptions and derived user stories;
- unresolved blockers or PRD gaps;
- fresh-agent-ready handoff coverage, including any missing first reads, source links, proof expectations, or scope exclusions;
- recommended next implementation slice or skill.
