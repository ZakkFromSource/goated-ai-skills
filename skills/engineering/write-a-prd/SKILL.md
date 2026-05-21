---
name: write-a-prd
category: engineering
classification: portable
status: wip
description: Use when fuzzy intent, a client brief, roadmap item, or feature idea needs a scoped PRD before issue breakdown or implementation.
triggers:
  - user asks for a PRD, product requirements document, product spec, implementation spec, or feature brief
  - user wants to turn unclear intent, a roadmap item, client brief, or feature idea into a concrete plan
  - target-project delivery needs a scoped artifact before issue breakdown or implementation
  - a future agent needs enough product and technical context to split work into vertical-slice issues
outputs:
  - tracked target-project PRD under docs/prds/ by default
  - problem, goals, non-goals, audience, and requirements
  - acceptance criteria, risks, assumptions, and open questions
  - source-grounded implementation and testing notes for later prd-to-issues work
depends_on:
  hard: []
  soft:
    - session-start-progressive-disclosure before writing a PRD for an unfamiliar target project
    - grill-with-docs when docs, standards, ADRs, project artifacts, domain language, or decision tradeoffs matter
    - context-matrix-map when docs/agents/context-matrix.md exists or source discovery is needed
    - project-context-calibration when root CONTEXT.md exists or project language affects requirements
    - project-standards-calibration when project standards affect requirements, testing, or rollout
    - verification-before-completion before claiming the PRD is fully checked or ready for issue breakdown
  fallback: If companion skills or project docs are unavailable, inspect the minimum relevant evidence and mark unverifiable assumptions in the PRD.
adapters:
  codex: usable
  claude-code: usable
  hermes: usable
  opencode: usable
  generic-agent: usable
---

# Write A PRD

## Purpose

Create a scoped product requirements document that turns fuzzy intent into an implementation-ready planning artifact.

Use this skill when the next useful artifact is a PRD that can feed `prd-to-issues`. The PRD should clarify the problem, target audience, goals, requirements, risks, and acceptance criteria without turning into a sprawling backlog or implementation transcript.

## Inputs

- User request, conversation context, client brief, roadmap item, feature idea, issue, or prototype verdict.
- Target-project root path.
- Existing PRD, spec, issue, roadmap, or planning conventions, if present.
- Existing root `CONTEXT.md`, `docs/agents/context-matrix.md`, and `docs/agents/project-standards.md`, if present.
- Relevant docs, ADRs, glossary/context files, standards, source files, tests, schemas, analytics notes, support notes, or product references.
- Clarified work brief from `grill-with-docs`, when available or needed.

## Workflow

1. Confirm the PRD boundary:
   - Identify the target project and the product outcome the PRD should cover.
   - Decide whether this is a new PRD, an update to an existing PRD, or a brief review before writing.
   - Keep the PRD focused on one coherent product or delivery outcome.
   - If the request is too small for a PRD, say so and recommend a direct issue, task, or implementation step instead.

2. Choose the PRD location:
   - Prefer the target project's existing PRD or spec convention when one is discoverable.
   - If no convention exists, write a tracked PRD under `docs/prds/<YYYY-MM-DD>-<short-slug>.md`.
   - Ask before using a different location when multiple conventions exist, the user wants a remote issue tracker, the PRD belongs in a private artifact, or the target project has no tracked docs area.
   - Do not write PRDs under `.local/` unless the user explicitly wants a private draft.

3. Explore available project facts before asking questions:
   - Start from the user request, target-project docs, and any existing planning artifacts.
   - If a context matrix exists, use it to choose relevant docs, code areas, tests, commands, and ADRs.
   - Read standards, glossary/context docs, feature docs, prior PRDs, issues, ADRs, nearby source, and tests only as needed.
   - Prefer discoverable facts over user questions.
   - Stop exploration when remaining uncertainty is product intent, priority, tradeoff, audience, scope, or acceptance criteria.

4. Use `grill-with-docs` when project artifacts matter:
   - Use it for PRD-level planning when docs, standards, ADRs, domain language, public-facing behavior, architecture, cross-file work, or unclear scope affect the outcome.
   - Carry forward its clarified goal, success criteria, scope boundaries, decisions, assumptions, and remaining questions.
   - Do not ask the user to restate facts already found in project artifacts.

5. Shape the PRD:
   - Write from the user's or product audience's perspective first, then include technical notes needed for issue breakdown.
   - Use project terminology from glossary/context docs when available.
   - Separate goals from non-goals and requirements from implementation notes.
   - Include enough technical direction for future agents to split vertical slices, but avoid brittle file-path inventories or code snippets unless they encode a stable decision.
   - Record assumptions and open questions instead of silently filling gaps.

6. Keep scope under control:
   - Treat the PRD as a contract for one focused change, not a backlog for every adjacent idea.
   - Move deferred ideas into an out-of-scope or future considerations section.
   - Do not expand requirements just because nearby improvements were discovered.
   - Prefer concrete acceptance criteria over broad aspirations.

7. Write and verify the artifact:
   - Create the parent directory if needed.
   - If updating an existing PRD, preserve useful existing decisions and mark changed scope clearly.
   - Re-read the PRD after writing.
   - Check that it includes problem, goals, non-goals, audience, requirements, acceptance criteria, risks, and open questions.
   - Check that the PRD can plausibly feed `prd-to-issues` without needing the future agent to reread the whole conversation.
   - Use `verification-before-completion` before claiming the PRD is ready for `prd-to-issues` or fully checked; for drafts or proposal-only PRDs, verify only the readiness claim being made and state open questions.

## Output Contract

Write a Markdown PRD using this shape by default:

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

After writing, report:

- PRD path;
- status and whether it is ready for `prd-to-issues`;
- key scope boundaries;
- remaining open questions or blockers;
- source evidence used;
- files changed.

## Delegation

The main agent owns the PRD scope, final synthesis, product judgment, and user communication.

When subagents are available, use them only for bounded evidence gathering, such as:

- finding existing PRD/spec conventions;
- summarizing relevant docs, ADRs, standards, or prior issues;
- checking source or tests for current behavior;
- identifying risks or acceptance criteria from one feature area.

Require every subagent result to include:

- paths inspected;
- commands run or deliberately skipped;
- source evidence found;
- assumptions and confidence;
- candidate PRD inputs, not final PRD prose.

If subagents are unavailable, perform the same evidence gathering sequentially with a narrower context budget.

## Guardrails

- Do not write a PRD before exploring discoverable project facts.
- Do not ask the user questions that project docs, code, tests, configs, or existing planning artifacts can answer.
- Do not turn the PRD into an unbounded backlog, architecture essay, or implementation issue list.
- Do not include unrelated refactors, nice-to-haves, or speculative future phases as requirements.
- Do not publish private notes, credentials, client data, sensitive personal context, or ignored scratch content into a tracked PRD.
- Do not assume a remote issue tracker, label vocabulary, or PRD location when the target project does not show one.
- Do not claim the PRD is ready for `prd-to-issues` while important acceptance criteria, scope boundaries, or blockers remain unresolved.
- Prefer explicit open questions and non-goals over pretending the plan is more settled than it is.

## References

No external references are required. This skill is self-contained after installation.
