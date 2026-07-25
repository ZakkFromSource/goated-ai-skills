---
name: doc-sync
description: Use when behavior, interfaces, architecture, standards, configuration, tests, or public docs may have documentation drift.
metadata:
  goated-category: engineering
---

# Doc Sync

## Purpose

Keep durable project documentation aligned with the behavior and decisions a target-project change actually introduced.

Use after work that could make docs stale. In implementation sessions, update
clear required drift; in planning or review-only sessions, report it without
edits.

## Inputs

- Request or originating spec, ticket, plan, review, or implementation summary.
- Target-project root path.
- Changed files, diffs, commits, staged changes, unstaged changes, generated files, migrations, config changes, or supplied patch.
- Fresh proof and review evidence relevant to changed facts.
- External documentation lookups when vendor or package docs materially
  informed the work.
- Relevant durable docs, indexes, ADRs, feature/API/schema docs, runbooks,
  changelogs, and standards.

## Dependencies

Hard: None.

Soft:
- session-start-progressive-disclosure for unfamiliar target projects
- context-matrix-map for broad discovery
- project-context-calibration or project-standards-calibration when those
  durable artifacts changed
- standards-and-spec-review when spec fit or changed scope is unclear
- code-security-review when security assumptions, trust boundaries, or sensitive behavior changed
- verification-before-completion before synced, checks-passed, or no-drift claims
- handoff when unfinished work or residual risk needs continuity

Fallback: Inspect minimal evidence, state lower confidence, and report
unverifiable drift risk.

## Workflow

1. Confirm the session mode:
   - Use **implementation mode** when the user asked for implementation, doc updates, or closeout work where file edits are expected.
   - Use **planning mode** when the user is designing future work, writing a plan, or asking what docs will need updates.
   - Use **review-only mode** when the user asked for a review, audit, or report without edits.
   - If mode is ambiguous, infer from the current task and state the assumption before editing. Ask only when the wrong mode would create unwanted file changes.

2. Discover the changed facts before choosing docs:
   - Identify the target-project root and the change set under review.
   - In git projects, inspect status, changed paths, and relevant diffs from the requested fixed point or current working tree.
   - Read the originating issue, PRD, ticket, user request, accepted plan, tests, and review notes when they define intended behavior.
   - Summarize only durable changed facts and affected public or operator
     expectations.
   - Separate verified facts from assumptions, proposed future work, and unresolved questions.

3. Discover relevant docs with progressive disclosure:
   - Use `docs/agents/context-matrix.md` when present to choose likely docs first.
   - Check only doc families relevant to the changed facts: root/index docs,
     feature/API/schema docs, ADRs, standards, runbooks, changelogs, and nearby
     package or command docs.
   - Search docs for changed names, commands, APIs, routes, flags, schema terms, feature names, standards, and architecture vocabulary.
   - Do not bulk-read generated output, dependency folders, old build artifacts, large logs, or unrelated historical notes.

4. Classify doc obligations:
   - **Required update**: a durable doc now contradicts, omits, or misroutes current behavior, public contracts, standards, architecture, verification, or operating instructions.
   - **Already covered**: a relevant doc already describes the new fact accurately enough.
   - **Recommended follow-up**: a doc change is useful but needs a product decision, architecture decision, broader rewrite, external owner, or separate artifact.
   - **Skipped**: a plausible doc was checked but should not be edited now; record the reason.
   - Treat missing durable docs as residual risk unless the current task explicitly includes creating that artifact.

5. Update or report:
   - In implementation mode, make minimal, source-grounded edits to required durable docs in the same session.
   - In planning or review-only mode, report required and recommended doc updates without editing files.
   - Preserve each doc's purpose and level of detail. Update facts, links, commands, status, acceptance, and reading order; avoid turning doc sync into a rewrite or new planning exercise.
   - When external documentation materially informed implementation, PRDs, architecture, troubleshooting, or docs, create or update a concise attributed lookup note using [External Docs Lookup Notes](references/external-docs-lookup-notes.md). Use `docs/agents/external-docs/<library-or-service>.md` when the target project has no better convention.
   - When a settled, hard-to-reverse decision needs durable capture and an ADR convention exists, recommend or update the relevant ADR according to that convention. If no convention exists, report the ADR need instead of inventing one.
   - If source behavior, specs, and docs conflict in a way that changes product intent, stop and ask which source should win.

6. Verify the documentation result:
   - Re-read edited sections and nearby headings.
   - Run doc lint, format, link check, or generated-doc commands only when the project defines them and they are safe for the session.
   - Confirm required updates are made or reported; preserve material proof
     gaps and residual drift risk.

7. Route the next closeout step:
   - Emit the applicable route signal when scope/spec fit, security, durable
     context, or standards need deeper review.
   - Recommend `commit-message` or `handoff` only after doc obligations are
     handled or intentionally deferred.
   - Use `verification-before-completion` before claiming docs are synced, doc checks passed, no required updates remain, or the change is ready for commit; for planning or review-only reports, verify only the documentation claim being made and state residual risk.

## Output Contract

In integrated use, return a compact delta to the main agent:

```markdown
Documentation impact: <none | required | deferred>
Updates: <paths and concise changed facts, when any>
Evidence: <fresh sources or checks that support the result>
Risk: <material skipped evidence, blocker, or residual drift risk>
```

For no durable impact, return only the result and the evidence needed to trust
it, for example: `Documentation impact: none. Checked the changed public
contracts and their owning docs; no durable fact changed.` Do not emit empty
updates, recommendations, skipped-docs, or `None` sections.

Standalone use returns the same compact local closeout. Include artifact-level
detail only when updates, deferrals, or material risk exist. Do not repeat
paths, checks, or the main task closeout.

## Delegation

Main owns mode, source-of-truth judgment, edits, conflicts, and communication.
Delegate only one changed fact or doc family. Subagents return paths, source
evidence, per-artifact status, assumptions, confidence, risk, and suggested
edits—not broad rewrites.

## Guardrails

- Do not edit docs before discovering the changed facts and the relevant docs.
- Do not treat temporary handoffs, scratch files, chat transcripts, or `.local/` notes as durable source-of-truth docs.
- Do not update a PRD, issue, or handoff to hide a mismatch between intended and implemented behavior. Report the mismatch or route it to the appropriate review skill.
- Do not create new durable artifacts such as ADRs, context files, standards profiles, or docs indexes unless the current task or project convention clearly calls for them.
- Do not bulk rewrite docs, reorganize documentation architecture, or modernize stale areas unrelated to the current change.
- Keep external-doc lookup notes attributed, concise, public-safe, and free of
  invented automation claims.
- Do not include private notes, ignored scratch content, credentials, client data, sensitive personal context, secrets, or real user data in tracked docs.
- Do not claim a doc check passed when the relevant file, command, or generated output was not inspected.
- Do not require this source repo's root docs after installation. The skill may rely only on its own instructions and target-project evidence.

## References

Linked support file, read at the workflow gate above: [External Docs Lookup Notes](references/external-docs-lookup-notes.md).
