---
name: documentation-cleanup
description: Use when auditing, tidying, consolidating, or optimizing a target project's docs tree, docs/agents artifacts, root README or context files, agent routing docs, progress/status docs, or documentation structure.
metadata:
  goated-category: engineering
---

# Documentation Cleanup

## Purpose

Audit and tidy a target project's documentation structure so humans and future agents can find the right source of truth quickly.

Use this skill for periodic documentation hygiene: role classification, duplication reduction, status-summary cleanup, agent-doc optimization, root-router alignment, stale or orphaned doc triage, and gated cleanup edits. Keep it separate from `doc-sync` and `documentation-writer`: `doc-sync` is for drift caused by a specific changed fact, while `documentation-writer` is for planned documentation authoring or substantial guide rewrites.

Default to audit-first. Do not move, delete, archive, or change source-of-truth ownership unless the user explicitly requested implementation mode and the project convention or user approval supports the action.

## Inputs

- User request, target-project root, requested mode, and cleanup goal.
- Existing project instructions, such as `AGENT.md`, `AGENTS.md`, `CLAUDE.md`, framework config, or routing notes.
- Root docs, progress/status files, roadmaps, skill maps, and operator guides.
- In-scope documentation folders, indexes, decisions, feature docs, agent
  guides, and workbench docs.
- Project conventions for archives, immutable decisions, generated docs, private scratch areas, and source-of-truth precedence.
- Optional inventory output from `scripts/inventory_docs.py`.

## Dependencies

Hard: None.

Soft:
- session-start-progressive-disclosure for unfamiliar target projects
- context-matrix-map, project-context-calibration,
  project-standards-calibration, or agent-instructions-integrator when the
  corresponding artifact needs deeper work
- documentation-writer when cleanup reveals a missing or rewritten durable doc
- doc-sync when recent behavior, interface, architecture, test, or workflow changes created drift
- verification-before-completion before cleaned/organized/safe/synced/future-ready docs claims

Fallback: Inspect the smallest useful docs set, report lower confidence, and
avoid destructive cleanup claims.

## Workflow

1. Choose the mode:
   - **Audit mode** is the default for review, planning, brainstorm, and "what should we clean" requests. It reports findings and recommendations without edits.
   - **Plan mode** produces a decision-complete cleanup plan for a future implementation pass, including exact approval-needed actions.
   - **Implementation mode** may edit docs only after audit evidence exists and the action is safe under user intent and project conventions.
   - If the user asks for broad cleanup but intent is ambiguous, start in audit mode and state that assumption.
   - Do not load `documentation-writer` unless the audit identifies a real
     missing or substantially rewritten artifact. Do not load `doc-sync`
     unless a specific changed fact created drift.

2. Confirm the project boundary and local authority order:
   - Identify the target-project root from the request, current directory, or repository metadata.
   - Read local agent instructions and docs indexes before judging layout.
   - Detect authority order from local docs when present. Do not impose GOATED's preferred artifacts on projects that use a different documented convention.
   - Treat missing `docs/agents/` or root `CONTEXT.md` as an optional finding, not an automatic defect.

3. Inventory before judging:
   - Run `python scripts/inventory_docs.py --repo <path>` when Python is available and a deterministic inventory helps.
   - If the script is unavailable, use manual file discovery such as `rg --files` and targeted reads.
   - Include `docs/`, `docs/agents/`, root README/context files, agent instruction adapters, progress/status docs, and issue/workbench docs only when project conventions put them in scope.
   - Skip generated output, dependency folders, binary assets, ignored scratch files, raw transcripts, private notes, and large archives unless the user explicitly includes them.

4. Classify doc roles:
   - Read [Doc Role Taxonomy](references/doc-role-taxonomy.md) when roles are unclear.
   - Assign each in-scope doc a likely role, audience, source-of-truth status, and lifecycle: active, dated evidence, historical, generated, private/scratch, or unknown.
   - Separate human-facing docs from AI-facing guides and routing artifacts.
   - Mark immutable or append-only sources, such as ADRs or archives, before proposing edits.

5. Audit cleanup risks:
   - Read [Cleanup Audit Checklist](references/cleanup-audit-checklist.md) for common findings.
   - Look for duplicated process rules, stale "current state" blocks, conflicting status flags, bloated evidence lists, ambiguous implemented-vs-planned language, broken or risky local links, orphan docs, misplaced AI-facing guidance, obsolete issue handoffs, and private/local leakage.
   - Verify high-impact claims against the documented source of truth, or route to `doc-sync`, `project-context-calibration`, `project-standards-calibration`, or `documentation-writer` when a deeper companion workflow owns the fix.

6. Recommend or edit:
   - Use action labels: **keep**, **refresh**, **merge**, **split**, **move**, **archive**, **delete**, or **defer**.
   - In audit or plan mode, report recommended actions without editing files.
   - In implementation mode, make only bounded, evidence-backed edits that preserve project meaning and links.
   - Require explicit approval for deletes, broad moves, archive operations, irreversible source-of-truth changes, or edits to immutable historical records unless the project convention clearly authorizes them.
   - Preserve private or sensitive content boundaries; sanitize public artifacts instead of copying private examples.

7. Verify and route follow-up:
   - Re-read edited sections and nearby headings.
   - Run markdown lint, link checks, script checks, or docs build commands only when the project defines them or the user asks.
   - Use `doc-sync` if cleanup changed docs that may make other durable docs stale.
   - Use `verification-before-completion` before claiming cleanup is done, docs are organized, or no required cleanup remains.
   - Use `handoff` when cleanup is incomplete or approval-needed actions should carry forward.

## Output Contract

The cleanup audit, plan, or applied cleanup result is the primary artifact. Use
the shape in [Cleanup Report Template](references/cleanup-report-template.md)
when its structure helps the decision. Preserve:

- Mode: audit, plan, or implementation.
- Scope inspected and skipped.
- Inventory summary and role classifications.
- Findings grouped by risk or doc family.
- Recommended actions with approval-needed actions separated.
- Edits made, if any.
- Verification performed and skipped.
- Companion-skill routes and residual risk.

In integrated use, return only material findings, changes, approval needs,
evidence, residual risk, and route signals to the main agent. Omit empty
categories, repeated inventories, and a competing task closeout.

When no cleanup is needed, say that clearly with the evidence needed to support
the decision. Standalone use returns the same compact local closeout.

## Delegation

Main owns source-of-truth judgment, edits, approvals, and communication.
Delegate only bounded inventories or reviews. Subagents return paths, evidence,
findings, assumptions, confidence, and recommendations; they do not decide
deletion, broad moves, or publication.

## Guardrails

- Do not treat this skill as a targeted post-change `doc-sync`; route changed-behavior drift to `doc-sync`.
- Do not use this skill to author a new manual or substantial guide from scratch; route planned authoring to `documentation-writer`.
- Do not impose `docs/agents/`, `CONTEXT.md`, ADRs, or GOATED conventions on projects that document another convention.
- Do not edit before inventorying and classifying the relevant docs.
- Do not move, delete, archive, or rewrite source-of-truth ownership without explicit approval or clear project convention evidence.
- Do not edit immutable ADRs, historical archives, legal/compliance docs, or generated docs except under an explicit project rule or user request.
- Do not include private project names, personal paths, credentials, client data, sensitive personal context, raw transcripts, model payloads, or ignored scratch content in public artifacts.
- Do not claim links, docs, or status are clean when relevant checks were skipped.
- Do not require this source repo's root files, issue files, `.local/` notes, or chat history after installation.

## References

Linked support files, read or use at the workflow/output gates above: [Doc Role Taxonomy](references/doc-role-taxonomy.md), [Cleanup Audit Checklist](references/cleanup-audit-checklist.md), and [Cleanup Report Template](references/cleanup-report-template.md).
