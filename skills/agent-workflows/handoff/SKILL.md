---
name: handoff
category: agent-workflows
classification: portable
status: wip
description: Use when a session needs a handoff, continuity note, restart note, resume note, or unfinished context for a future agent.
triggers:
  - user asks for a handoff, continuity note, restart note, or resume note
  - agent is ending an onboarding or delivery session with unfinished context
  - future work needs current state, blockers, verification, and next skills preserved
  - user explicitly wants a temporary, local, or tracked handoff artifact
outputs:
  - temporary handoff under the OS temp directory by default
  - per-project handoff path using goated-handoffs/<project-name>/
  - compact current-state summary
  - important references by path
  - verification status, blockers, and recommended next skills
depends_on:
  hard: []
  soft:
    - session-start-progressive-disclosure when a future agent will need to re-orient
    - context-matrix-map when a target project has docs/agents/context-matrix.md
    - project-context-calibration when project language or boundaries affected the work
    - project-standards-calibration when standards affected the work
  fallback: If companion skills or durable artifacts are unavailable, write a compact note with explicit gaps and lower confidence.
adapters:
  codex: usable
  claude-code: usable
  hermes: usable
  opencode: usable
  generic-agent: usable
---

# Handoff

## Purpose

Create a compact continuity note that lets a future agent or session resume without rereading the whole conversation.

Use this skill at the end of onboarding, delivery, review, planning, or interrupted work. The handoff should point to source artifacts and current evidence; it should not duplicate PRDs, issues, ADRs, diffs, commits, or long transcripts.

## Inputs

- User request or reason for handoff.
- Optional next-session focus from the user.
- Target-project root path.
- Target project name when provided by the user.
- Current task, issue, PRD, ADR, or spec paths.
- Relevant `docs/agents/` artifacts, if present.
- Local git status, changed files, commits, or diff summary when relevant.
- Verification commands run, skipped, failed, or still needed.
- Known blockers, risks, assumptions, and recommended next skills.
- Existing handoff path when updating a prior handoff.

## Workflow

1. Confirm the handoff scope:
   - Identify whether the handoff is for target-project onboarding, target-project delivery, review, planning, or an interrupted session.
   - If the user provides a next-session focus, tailor the handoff around what that future session needs first.
   - Confirm the target-project root.
   - Keep the handoff focused on resuming the current work, not documenting the whole project.

2. Choose storage:
   - Default to the user's OS temp directory under `goated-handoffs/<project-name>/`.
   - Resolve OS temp with a platform API when possible, such as Python `tempfile.gettempdir()`, Node `os.tmpdir()`, or PowerShell `[System.IO.Path]::GetTempPath()`.
   - Define `<project-name>` as a filesystem-safe slug from the user-provided project name when available, otherwise the target-project root folder name.
   - Use `unknown-project` when no project name or target-project root can be identified.
   - Replace whitespace, path separators, and reserved filename characters in `<project-name>` with hyphens; keep the slug readable rather than hash-first.
   - Use a clear default path such as `<os-temp>/goated-handoffs/<project-name>/<YYYY-MM-DD>-<short-topic>.md`.
   - If updating an existing handoff, read it before writing.
   - Write a tracked handoff only when the user explicitly requests one, and keep tracked handoffs public-safe.

3. Gather references instead of copying content:
   - Link or list the relevant PRD, issue, ADR, context matrix, standards profile, code files, tests, docs, commits, or commands.
   - Summarize only the current state needed to resume.
   - Reference diffs, commits, PRs, and commit messages by path, command, hash, or link instead of pasting them.
   - Do not include private scratch content unless it is necessary to resume and safe to store in a temporary handoff.

4. Capture current state:
   - What has been completed.
   - What is in progress.
   - What changed since the start of the session.
   - What assumptions are currently active.
   - What decisions were made and where the evidence lives.

5. Capture verification status:
   - Commands run and their outcomes.
   - Commands not run and why.
   - Manual checks completed.
   - Known failing checks, flaky checks, or unverified areas.

6. Capture blockers and next moves:
   - Blockers, risks, unresolved questions, and missing inputs.
   - Recommended next skills, such as `session-start-progressive-disclosure`, `context-matrix-map`, `project-context-calibration`, `project-standards-calibration`, `doc-sync`, `standards-and-spec-review`, `code-security-review`, or `commit-message`.
   - A short resume plan with the next one to three actions.

7. Finalize and report:
   - Re-read the handoff for concision and source references.
   - Confirm it does not duplicate long artifacts.
   - Report the absolute handoff path and the most important next step.

## Output Contract

Write a Markdown handoff under `<os-temp>/goated-handoffs/<project-name>/` by default:

```markdown
# Handoff: <short topic>

## Scope

- Mode: <onboarding | delivery | review | planning | interrupted session>
- Goal: <one sentence>
- Next-session focus: <user-provided focus or "not specified">
- Target project: <path or name>
- Storage: <temporary OS temp | tracked>
- Handoff path: <absolute path>

## Current State

- Completed: <brief bullets>
- In progress: <brief bullets>
- Not started: <brief bullets>

## Important References

| Reference | Why it matters |
| --- | --- |

## Verification Status

| Check | Result | Notes |
| --- | --- | --- |

## Blockers And Risks

- <blocker, risk, unresolved question, or "None known">

## Recommended Next Skills

- `<skill-name>`: <why>

## Resume Plan

1. <next action>
2. <next action>
3. <next action>

## Last Updated

- Date: <YYYY-MM-DD>
- Updated by: <agent or user label>
```

After writing the handoff, report:

- absolute handoff path;
- whether it is temporary OS temp storage or tracked;
- most important references included;
- verification status;
- recommended next skill or direct next action.

## Delegation

The main agent owns the handoff scope, final summary, privacy judgment, and user communication.

When subagents are available, use them only for bounded evidence gathering, such as:

- summarizing changed files;
- collecting verification commands and outcomes;
- finding relevant issue, PRD, ADR, or docs paths;
- resolving the target-project root, project-name slug, or existing handoff path.

Require every subagent result to include:

- paths inspected;
- commands run;
- evidence sources;
- explicit assumptions and uncertainty;
- concise findings suitable for reference, not pasted handoff prose.

If subagents are unavailable, perform the same gathering sequentially with a narrower context budget.

## Guardrails

- Default to `<os-temp>/goated-handoffs/<project-name>/`, not the current project workspace.
- Always report the absolute handoff path because OS temp locations vary by system and may be cleaned automatically.
- Do not treat temporary handoffs as durable records or secret storage.
- Write tracked handoffs only when the user explicitly requests a tracked artifact.
- Do not duplicate PRDs, issue files, ADRs, diffs, commit messages, long logs, or conversation transcripts.
- Do not treat a handoff as a replacement for root `CONTEXT.md`, `docs/agents/context-matrix.md`, `docs/agents/project-standards.md`, a PRD, an issue, or an ADR.
- Do not include credentials, secrets, client data, sensitive personal context, or unsafe private scratch notes in any handoff.
- Do not claim verification passed unless the check was actually run or already evidenced.
- Keep the note short enough that a future agent can read it first.
- Prefer references and resume actions over narrative history.

## References

This skill is self-contained after installation.
