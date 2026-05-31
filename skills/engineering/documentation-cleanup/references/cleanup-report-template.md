# Cleanup Report Template

Use this shape for audit, plan, and implementation reports. Keep it compact; include exact paths and enough evidence for the next agent to continue.

```markdown
## Documentation Cleanup

- Mode: <audit | plan | implementation>
- Target project: <path or project label>
- Scope inspected: <docs folders, root routers, progress/status docs, issue workbench, or other>
- Scope skipped: <paths or doc families skipped with reasons>
- Inventory method: <script command, rg/manual scan, subagent scan, or supplied artifact>
- Authority order detected: <source order, or "not found">

## Inventory Summary

| Doc family | Paths | Likely role | Status |
| --- | --- | --- | --- |
| <family> | <paths> | <role> | <active/historical/generated/private/unknown> |

## Findings

| Priority | Path | Finding | Evidence | Recommended action |
| --- | --- | --- | --- | --- |
| <P1/P2/P3> | <path> | <issue> | <line, heading, inventory signal, or source> | <keep/refresh/merge/split/move/archive/delete/defer> |

## Approval Needed

- <move/delete/archive/source-of-truth change requiring user approval, or "None">

## Edits Made

- <path>: <summary, or "None">

## Verification

- <script/check/manual review performed>
- <skipped checks and why>

## Companion Routes

- <doc-sync/documentation-writer/context-matrix-map/project-context-calibration/project-standards-calibration/agent-instructions-integrator/handoff/none>

## Residual Risk

- <unverified source behavior, skipped docs, unresolved ownership, private-boundary concerns, or "Low">
```

## Priority Guidance

- `P1`: likely to mislead implementation, leak sensitive content, break documented navigation, or cause irreversible cleanup if handled casually.
- `P2`: stale or duplicated source-of-truth material that can slow or confuse future work.
- `P3`: polish, readability, or consolidation opportunity with low immediate risk.

## Implementation Closeout Additions

When implementation mode edits files, add:

```markdown
## Changed Files

- <path>: <what changed and why>

## Link And Ownership Checks

- <local links checked, role owners checked, catalog updates, or skipped checks>
```
