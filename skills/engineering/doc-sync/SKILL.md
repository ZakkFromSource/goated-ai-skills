---
name: doc-sync
category: engineering
classification: portable
status: wip
description: Use when behavior, interfaces, architecture, standards, configuration, tests, or public docs may have documentation drift.
triggers:
  - implementation work changed behavior, public interfaces, architecture, standards, configuration, tests, docs, or user-visible workflows
  - user asks to sync docs, update docs, check documentation drift, or list required documentation updates
  - standards-and-spec-review, code-security-review, TDD, PRD, issue, or architecture work indicates durable docs may be stale
  - planning or review-only work needs required doc updates reported without editing files
outputs:
  - changed-behavior summary grounded in diffs, specs, tests, commands, or source evidence
  - relevant docs discovered and checked before updates are proposed
  - documentation updates made during implementation sessions or recommended during planning and review-only sessions
  - skipped docs with reasons, already-covered docs, and residual drift risk
depends_on:
  hard: []
  soft:
    - session-start-progressive-disclosure before syncing docs in an unfamiliar target project
    - context-matrix-map when docs/agents/context-matrix.md exists or doc discovery is broad
    - project-context-calibration when project language, boundaries, or durable context may have changed
    - project-standards-calibration when standards, commands, conventions, or enforcement levels may have changed
    - standards-and-spec-review before doc sync when spec fit or changed scope is unclear
    - code-security-review before doc sync when security assumptions, trust boundaries, or sensitive behavior changed
    - handoff after doc sync when unfinished work or residual risk should be preserved for a future session
  fallback: If companion skills, git history, or durable docs are unavailable, inspect the smallest relevant local evidence, state lower confidence, and report unverifiable drift risk.
adapters:
  codex: usable
  claude-code: usable
  hermes: usable
  opencode: usable
  generic-agent: usable
---

# Doc Sync

## Purpose

Keep durable project documentation aligned with the behavior and decisions a target-project change actually introduced.

Use this skill after implementation or review work that could make docs stale. In implementation sessions, update the relevant docs in the same session when the needed change is clear. In planning or review-only sessions, report the required doc updates without mutating files.

## Inputs

- User request, issue, PRD, ticket, accepted plan, review finding, or implementation summary.
- Target-project root path.
- Changed files, diffs, commits, staged changes, unstaged changes, generated files, migrations, config changes, or supplied patch.
- Tests, command output, manual verification notes, TDD evidence, standards/spec review, security review, prototype verdicts, or architecture notes.
- Existing durable docs such as `README.md`, `CONTEXT.md`, `docs/agents/context-matrix.md`, `docs/agents/project-standards.md`, ADRs, feature docs, API docs, schema docs, runbooks, changelogs, or design docs.
- Existing local/session artifacts such as `.local/handoffs/`, scratch notes, or temporary plans when they help identify context but should not become source-of-truth docs.

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
   - Summarize the changed behavior, public interfaces, architecture decisions, standards, commands, schemas, migrations, configuration, tests, security assumptions, or user-visible workflows.
   - Separate verified facts from assumptions, proposed future work, and unresolved questions.

3. Discover relevant docs with progressive disclosure:
   - Use `docs/agents/context-matrix.md` when present to choose likely docs first.
   - Check root docs, docs indexes, feature docs, API docs, ADRs, standards profiles, schema docs, runbooks, changelogs, issue handoffs, and nearby package or command docs only as relevant to the changed facts.
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
   - When a settled, hard-to-reverse decision needs durable capture and an ADR convention exists, recommend or update the relevant ADR according to that convention. If no convention exists, report the ADR need instead of inventing one.
   - If source behavior, specs, and docs conflict in a way that changes product intent, stop and ask which source should win.

6. Verify the documentation result:
   - Re-read edited sections and nearby headings.
   - Run doc lint, format, link check, or generated-doc commands only when the project defines them and they are safe for the session.
   - Confirm all required updates are made or explicitly reported.
   - Record skipped checks, unavailable sources, weak evidence, and residual drift risk.

7. Route the next closeout step:
   - Recommend `standards-and-spec-review` when the changed scope or spec fit remains unclear.
   - Recommend `code-security-review` when docs describe security-relevant behavior or trust boundaries that were not reviewed.
   - Recommend `project-context-calibration` or `project-standards-calibration` when durable context or standards need deeper curation.
   - Recommend `commit-message` or `handoff` only after doc sync obligations are handled or intentionally deferred.

## Output Contract

Return a compact report shaped like this:

```markdown
## Doc Sync

- Mode: <implementation | planning | review-only>
- Changed facts checked: <behavior, interface, architecture, standards, config, tests, docs, or "none found">
- Evidence inspected: <diffs, docs, commands, specs, tests, or assumptions>

## Docs Checked

| Doc | Why checked | Result |
| --- | --- | --- |
| <path> | <changed fact or search reason> | <required update, already covered, recommended follow-up, skipped> |

## Updates Made

- <path>: <summary of edit>

## Recommended Updates

- <path or artifact>: <needed update, owner or blocker, and why>

## Skipped Docs

- <path>: <reason skipped or not applicable>

## Residual Drift Risk

- <unverified docs, missing artifacts, skipped commands, assumptions, or "Low">
```

When there are no required updates, say so explicitly and still list the docs checked and residual risk.

## Delegation

The main agent owns session mode, source-of-truth judgment, final doc edits, conflict decisions, and user communication.

When subagents are available, use them only for bounded documentation review passes, such as:

- summarizing changed behavior from a named diff or source area;
- finding likely docs for one changed term, feature, interface, command, or schema;
- checking one doc family, such as API docs, ADRs, standards, runbooks, or feature docs;
- verifying that edited docs match the final behavior and do not introduce new drift;
- collecting residual-risk notes for docs that could not be inspected.

Require every subagent result to include:

- `Status`: `DONE`, `DONE_WITH_CONCERNS`, `NEEDS_CONTEXT`, or `BLOCKED`;
- paths inspected;
- commands run or deliberately skipped;
- exact source evidence found;
- doc status for each checked artifact: required update, already covered, recommended follow-up, or skipped;
- assumptions, confidence, and residual drift risk;
- suggested edits or findings, not unsupervised broad rewrites.

Handle delegated status this way: `DONE` means integrate doc status, suggested edits, and residual drift risk into the final doc-sync decision; `DONE_WITH_CONCERNS` means inspect concerns about source-of-truth conflicts, stale docs, incomplete coverage, or risky suggested wording before editing or reporting; `NEEDS_CONTEXT` means provide the missing diff, changed behavior, schema, command output, doc family, or source artifact and re-dispatch; `BLOCKED` means narrow the doc family, defer broad edits, choose a safer recommendation-only path, or escalate to the user.

If subagents are unavailable, perform the same checks sequentially with a narrower context budget.

## Guardrails

- Do not edit docs before discovering the changed facts and the relevant docs.
- Do not treat temporary handoffs, scratch files, chat transcripts, or `.local/` notes as durable source-of-truth docs.
- Do not update a PRD, issue, or handoff to hide a mismatch between intended and implemented behavior. Report the mismatch or route it to the appropriate review skill.
- Do not create new durable artifacts such as ADRs, context files, standards profiles, or docs indexes unless the current task or project convention clearly calls for them.
- Do not bulk rewrite docs, reorganize documentation architecture, or modernize stale areas unrelated to the current change.
- Do not include private notes, ignored scratch content, credentials, client data, sensitive personal context, secrets, or real user data in tracked docs.
- Do not claim a doc check passed when the relevant file, command, or generated output was not inspected.
- Do not require this source repo's root docs after installation. The skill may rely only on its own instructions and target-project evidence.
- Prefer explicit skipped-doc reasons and residual risk over guessing.

## References

No external references are required. This skill is self-contained after installation.
