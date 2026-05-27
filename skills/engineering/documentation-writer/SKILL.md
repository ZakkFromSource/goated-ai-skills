---
name: documentation-writer
category: engineering
classification: portable
status: wip
description: Use when creating or substantially revising source-grounded durable documentation such as manuals, operator guides, runbooks, troubleshooting guides, onboarding guides, product docs, or AI-facing guide docs.
triggers:
  - user asks to write, create, draft, improve, or substantially revise a manual, guide, runbook, troubleshooting guide, onboarding guide, product doc, or user-facing documentation
  - planned documentation needs audience, scope, source evidence, target location, assumptions, and verification before it is ready
  - a project needs a separate AI-facing guide for repeated agent or model use, distinct from human-facing documentation
  - existing docs need a manual-style rewrite rather than a drift-only sync
outputs:
  - created or updated durable documentation grounded in source evidence and audience needs
  - target audience, doc type, scope, source evidence, assumptions, gaps, and unresolved questions
  - target documentation location chosen from project conventions or an explicit fallback
  - AI-facing guide decision, including created path or reason a separate guide is unnecessary
  - verification summary, doc-sync relationship, skipped evidence, and remaining gaps
depends_on:
  hard: []
  soft:
    - session-start-progressive-disclosure before writing docs in an unfamiliar target project
    - grill-with-docs when audience, purpose, scope, terminology, product behavior, or documentation ownership is unclear
    - write-a-prd when product requirements, acceptance criteria, or feature intent are not settled enough to document
    - doc-sync after documentation changes may make other durable docs, catalogs, standards, or operator guidance stale
    - verification-before-completion before claiming docs are ready, source-grounded, checked, synced, or complete
    - handoff when remaining gaps, skipped evidence, or documentation ownership need continuity
  fallback: If companion skills, project docs, source access, or review tools are unavailable, inspect the smallest useful evidence, write narrower docs, label assumptions and gaps, and avoid readiness claims that cannot be verified.
adapters:
  codex: usable
  claude-code: usable
  hermes: usable
  opencode: usable
  generic-agent: usable
---

# Documentation Writer

## Purpose

Create or substantially revise durable documentation that helps humans understand and use a project, product, workflow, or operational process.

Use this skill for planned documentation authoring: manuals, operator guides, runbooks, troubleshooting guides, onboarding guides, durable product docs, and optional AI-facing guide docs. Keep it separate from `doc-sync`: this skill writes planned docs from source evidence and audience needs; `doc-sync` checks whether changed behavior or docs made other durable docs stale.

Human-facing docs come first. AI-facing guides are separate artifacts used only when requested or useful for repeated agent or model work.

## Inputs

- User request, documentation goal, target audience, desired doc type, scope, and freshness expectations.
- Target-project root path and applicable project or agent instructions.
- Existing documentation conventions, docs indexes, README files, manuals, guides, runbooks, product docs, and agent docs.
- Source evidence such as code, tests, commands, product notes, PRDs, issues, ADRs, schemas, config, logs, support notes, screenshots, or user-provided context.
- Known private or sensitive material that must not be copied into durable docs.
- Verification tools or manual checks available for Markdown, links, generated docs, screenshots, commands, or product behavior.

## Workflow

1. Confirm the documentation contract:
   - Identify whether the task is a new doc, substantial revision, AI-facing guide, or drift-only check.
   - Route drift-only work to `doc-sync`; route unsettled product intent to `write-a-prd`; route unclear audience or scope to `grill-with-docs`.
   - State the intended doc type, audience, scope, owner if known, and readiness claim being pursued.
   - Ask only for product intent or preference that cannot be discovered from local evidence.

2. Gather source evidence before writing:
   - Find the target-project documentation conventions before choosing a path.
   - Inspect relevant existing docs, context artifacts, source files, tests, commands, PRDs, issues, ADRs, schemas, config, or user-provided materials.
   - Separate verified facts, stale or conflicting sources, assumptions, skipped evidence, and unresolved product questions.
   - Stop and ask which source wins when source behavior, product intent, and existing docs conflict in a way that changes the documentation claim.

3. Choose the documentation location:
   - Prefer the target project's existing docs convention, naming style, and index structure.
   - If no convention exists, default human-facing durable Markdown to `docs/<topic>-guide.md`.
   - If a separate AI-facing guide is requested or useful and no convention exists, default to `docs/agents/<topic>-ai-guide.md`.
   - Record location assumptions instead of presenting defaults as universal rules.

4. Shape the doc for the audience:
   - Read [Manual Patterns And QA](references/manual-patterns-and-qa.md) when choosing a doc type, AI-facing guide shape, or QA checklist.
   - Keep human docs task-oriented, readable, and audience-specific.
   - Keep AI-facing guides separate from human manuals by default. They should help agents load the right facts quickly, not replace human docs or become the only source of product behavior.
   - Prefer concise sections, examples, commands, warnings, and next reads that match the audience's real task.

5. Draft from evidence:
   - Write durable Markdown in the project's style unless another existing convention clearly applies.
   - Link or name source evidence enough for a future maintainer to verify major claims.
   - Mark assumptions, gaps, outdated areas, missing screenshots, unverified commands, or product questions explicitly.
   - Do not paste raw transcripts, private notes, credentials, real user data, or sensitive context into tracked docs.

6. Verify the documentation:
   - Re-read edited docs and nearby headings for flow, accuracy, audience fit, stale wording, broken local links, and unsupported claims.
   - Run doc lint, link check, render, command, or product verification only when the project defines a safe check or the user asks for it.
   - For AI-facing guides, verify that the file is separate, concise, source-linked, and named as a guide rather than a context source of truth.
   - Record skipped checks and residual risk rather than claiming readiness from uninspected evidence.

7. Route follow-up:
   - Use `doc-sync` after documentation changes when catalogs, README summaries, standards, operator docs, public workflow descriptions, or other durable docs may now be stale.
   - Use `verification-before-completion` before claiming the documentation is ready, complete, source-grounded, or synced.
   - Use `handoff` when gaps, owner questions, or deferred verification need continuity.

## Output Contract

Return a compact report shaped like this:

```markdown
## Documentation Writer

- Mode: <new doc | substantial revision | AI-facing guide | recommendation-only>
- Audience: <human audience and/or AI agent/model audience>
- Doc type and scope: <manual, operator guide, runbook, onboarding guide, product doc, AI guide, or other>
- Created or updated docs: <paths, or "none">
- Location decision: <project convention used or fallback assumption>
- Source evidence used: <docs, source files, tests, commands, PRDs, issues, user context, or assumptions>
- Skipped evidence: <sources/checks skipped and why, or "None">
- Assumptions and gaps: <assumptions, conflicts, unresolved questions, or "None">
- AI-facing guide decision: <created path, deferred, not needed, or not requested>
- Verification: <manual review, commands, link checks, rendered artifacts, source checks, or skipped checks>
- Doc-sync relationship: <not needed | routed to doc-sync | required follow-up and why>
- Remaining gaps: <owner, source, verification, or product gaps, or "None">
```

When no doc should be written, say so and explain the route, such as `doc-sync`, `write-a-prd`, `grill-with-docs`, or a user decision.

## Delegation

The main agent owns audience judgment, source-of-truth decisions, final documentation wording, target location, verification claims, and user communication.

When subagents are available, use them for bounded independent passes, such as:

- source summarization for one doc, code area, PRD, issue, or command family;
- documentation convention discovery for one target project or docs folder;
- outline review against the requested audience and doc type;
- audience-fit review for human manuals, operator guides, onboarding docs, or product docs;
- AI-facing guide usefulness review, including whether a separate guide is warranted;
- documentation QA for unsupported claims, private-data risk, broken links, stale wording, or static-site scope creep.

Require every delegated result to include:

- `Status`: `DONE`, `DONE_WITH_CONCERNS`, `NEEDS_CONTEXT`, or `BLOCKED`;
- paths, docs, source files, commands, artifacts, or links inspected;
- exact evidence found and skipped evidence with reasons;
- assumptions, confidence, concerns, and residual risk;
- suggested findings or edits, not unsupervised final publication.

Handle delegated status this way: `DONE` means integrate evidence after checking important claims; `DONE_WITH_CONCERNS` means inspect concerns before writing or reporting; `NEEDS_CONTEXT` means provide the missing source, doc type, scope, audience, command, artifact, or product decision and re-dispatch or continue locally; `BLOCKED` means narrow the doc scope, choose recommendation-only output, or ask the user for the missing decision.

If subagents are unavailable, perform the same checks sequentially with a narrower context budget.

## Guardrails

- Do not write planned documentation before gathering source evidence.
- Do not use `documentation-writer` for drift-only checks; route those to `doc-sync`.
- Do not turn human manuals into agent scratchpads. Keep AI-facing guidance separate by default.
- Do not name AI-facing guides as context sources when the project already uses context docs for durable language, source maps, or routing.
- Do not create documentation webpages, static sites, publishing workflows, hosting guidance, generated navigation, or deployment steps unless a separate approved scope explicitly asks for them.
- Do not invent product behavior, support promises, commands, SLAs, architecture, permissions, or troubleshooting steps.
- Do not hide mismatches between source behavior and intended behavior by documenting the mismatch away; surface the conflict and route to the right planning or implementation workflow.
- Do not paste credentials, secrets, private notes, raw transcripts, client data, sensitive personal context, real user data, or ignored scratch content into durable docs.
- Do not claim docs are complete, current, source-grounded, synced, or ready when relevant sources or checks were skipped.
- Do not require this source repo's root files, issue files, `.local/` notes, or chat history after installation. The skill may rely only on its own files and target-project evidence.

## References

- [Manual Patterns And QA](references/manual-patterns-and-qa.md) - read when selecting doc type patterns, deciding whether to create an AI-facing guide, or checking manual quality before closeout.
