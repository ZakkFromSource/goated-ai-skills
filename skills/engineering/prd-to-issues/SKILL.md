---
name: prd-to-issues
category: engineering
classification: portable
status: wip
description: Use when a scoped PRD, product spec, roadmap item, or approved plan is ready to become dependency-ordered vertical-slice local issue handoffs with acceptance criteria, blockers, and user stories.
triggers:
  - user asks to turn a PRD, product requirements document, product spec, implementation spec, roadmap item, or plan into issues
  - user wants local issue handoffs, implementation tickets, work slices, or agent-ready tasks from a scoped PRD
  - target-project delivery needs independently workable vertical slices before TDD, implementation, review, or handoff
  - a future agent needs a PRD decomposed into blocker-aware AFK and HITL issues
outputs:
  - approval-ready issue breakdown with title, type, blockers, user stories, acceptance focus, and foundation rationale when relevant
  - local Markdown issue handoffs named issues/NNN-short-title.md by default that a fresh agent can use without hidden chat history
  - local recommended order file for approved multi-issue breakdowns, refreshed from the approved issue set when the workflow runs again
  - blocker and foundation issues written before dependent issues
  - concise vertical-slice issue bodies with parent PRD, first reads, source links, blockers, acceptance criteria, expected proof, and user stories
  - implementation routing notes that send future agents to grill-with-docs before implementation and writing-plans for executable steps
  - warnings when the PRD may be too broad or not ready for issue breakdown
depends_on:
  hard: []
  soft:
    - session-start-progressive-disclosure before slicing an unfamiliar target project
    - grill-with-docs when PRD scope, project language, standards, architecture, or approval tradeoffs are unclear
    - write-a-prd when the PRD is missing, stale, ambiguous, or not ready for issue breakdown
    - writing-plans after an issue is approved and a future implementer needs exact executable steps
    - prototype when a risky issue slice depends on a disposable experiment verdict
    - context-matrix-map when docs/agents/context-matrix.md exists or source discovery is needed
    - project-context-calibration when root CONTEXT.md exists or project language affects issue wording
    - project-standards-calibration when project standards affect issue scope, verification, or acceptance
    - verification-before-completion before claiming the generated issue set is complete, checked, or ready for implementation
  fallback: If companion skills or project docs are unavailable, inspect the minimum relevant local evidence, state lower confidence, and pause instead of writing issues from an unready PRD.
adapters:
  codex: usable
  claude-code: usable
  hermes: usable
  opencode: usable
  generic-agent: usable
---

# PRD To Issues

## Purpose

Break a scoped PRD into local Markdown issue handoffs that future agents or engineers can implement one slice at a time.

In this skill, a fresh-agent-ready issue is one that can be started from the issue file and its linked sources without relying on hidden chat history, ignored notes, or unlinked upstream context.

Use this skill after a PRD is ready for breakdown. Each issue should be a balanced vertical tracer bullet: narrow enough to complete with quality, but complete enough that the resulting behavior is independently verifiable. For multi-issue breakdowns, the workflow also creates or refreshes a local recommended order file so future agents can pick up the dependency order without reconstructing blockers manually. Dynamic means refreshed when this workflow runs, not background automation. The workflow is local-only in V1; it creates files inside the target project and does not publish to remote issue trackers.

## Inputs

- Scoped PRD, product spec, implementation spec, roadmap plan, issue, or approved planning artifact.
- Target-project root path.
- Existing local issue convention, such as `issues/NNN-short-title.md`, if present.
- Existing local recommended order file for the same parent PRD or planning artifact, if present.
- Existing root `CONTEXT.md`, `docs/agents/context-matrix.md`, and `docs/agents/project-standards.md`, if present.
- Relevant docs, ADRs, standards, source files, tests, schemas, prototypes, or prior issue handoffs needed to understand current implementation state.
- Clarified work brief from `grill-with-docs`, when available or needed.
- Known scope exclusions, blockers, expected proof, and durable source links that a future implementer should read without access to the current chat session.

## Workflow

1. Confirm the source and target:
   - Identify the PRD or planning artifact being sliced and the target project where local issues should be written.
   - Confirm the PRD describes one coherent product or delivery outcome.
   - Treat the PRD as the upstream contract. Read it, reference it, and surface gaps, but do not edit it during this workflow.
   - Record the parent PRD or planning artifact path that each generated issue will carry forward.

2. Discover local conventions and current state:
   - Inspect the target project before slicing. Read only the docs, standards, ADRs, source areas, tests, and prior issues needed to understand current implementation state.
   - Prefer an existing local issue convention when one is discoverable.
   - If no local issue convention exists, default to tracked files under `issues/`.
   - If multiple plausible local issue conventions exist, ask the user which one should receive the generated issue files.
   - Scan active and archived local issue files before writing to choose the next highest unused `NNN` number.
   - For multi-issue breakdowns, derive the recommended order file path from the parent PRD or planning artifact slug, such as `issues/<parent-slug>-order.md`, colocated with generated issues when the project uses another local issue directory.
   - If a matching order file already exists, plan to refresh it from the approved issue set instead of appending new entries to stale content.
   - Collect recommended first reads, durable source links, expected proof targets, blockers, and important scope exclusions for each planned slice.
   - Treat hidden chat history, ignored notes, and unlinked upstream sources as insufficient context for a future issue handoff.

3. Check PRD readiness:
   - Verify the PRD has enough goal, audience, scope, non-goal, requirement, acceptance, blocker detail, and source evidence to derive stable expected proof for each slice.
   - If the PRD is ambiguous, stale, missing important acceptance criteria, or still has blocking open questions, pause and report the gaps.
   - Recommend `write-a-prd` or a focused `grill-with-docs` follow-up when the PRD needs repair.
   - Do not write assumption-heavy issues just to keep moving.

4. Draft balanced vertical slices:
   - Prefer one narrow, complete, verifiable behavior per issue.
   - Avoid horizontal slices such as "add schema", "add API", "build UI", or "write tests" when they do not prove behavior on their own.
   - Prefer several thin tracer bullets over a few broad milestone issues.
   - Mark slices `AFK` by default. Use `HITL` when a slice requires a human decision, design review, credentials, external access, or another approval gate.
   - Use PRD user stories when present. If they are missing, derive concise stories from the PRD audience and goals, and label them as derived.
   - For each slice, identify the stable source links and proof expectations that belong in the issue, and leave volatile execution detail for `writing-plans`.

5. Allow only narrow foundation issues:
   - Create foundation issues only when they clearly unblock named dependent vertical slices.
   - Keep foundations small and verifiable.
   - Require a compact rationale naming the useful interface being created or clarified, the complexity it hides, and the dependent slices it unlocks.
   - Reject broad setup batches that do not create a meaningful interface or do not lead directly to vertical slices.
   - Write blocker and foundation issues before dependent issues so later issues can reference real local paths.

6. Present the approval breakdown before writing:
   - Draft the full issue set, grouped in dependency order.
   - For each proposed issue, show title, type, blockers, user stories, recommended first reads, relevant source links, acceptance focus, expected proof, scope exclusions when applicable, and any foundation rationale.
   - For multi-issue breakdowns, show the planned recommended order file path and make clear that it will be written or refreshed only after approval.
   - For single-issue breakdowns, state that the order file will be skipped because there is no multi-issue dependency order to preserve.
   - Warn when the breakdown is hard to review, contains messy foundations, starts to look like milestones or subsystems, or produces roughly more than 10-12 issues.
   - Ask the user to approve the breakdown, including granularity, blocker relationships, user story coverage, AFK/HITL types, and fresh-agent-ready handoff coverage.
   - Iterate until the user explicitly approves the breakdown.

7. Write local files after approval:
   - Create local Markdown issue files only after approval.
   - Use `issues/NNN-short-title.md` by default, or the discovered local convention when one exists.
   - Use kebab-case short titles in filenames.
   - Write files in dependency order, blockers first.
   - Reference blockers by local file path.
   - Include the parent PRD, recommended first reads, relevant source links, acceptance criteria, expected proof, blockers, user stories, and implementation route in every issue.
   - Include important scope exclusions only when they prevent likely scope creep or source-repo/runtime confusion.
   - Include selective source-grounded implementation notes only when they prevent likely implementation mistakes.
   - Keep exact files to edit, commands to run, expected failures, implementation order, and detailed code snippets out of issue files unless a compact note is needed to prevent a concrete mistake; route those details to `writing-plans`.
   - For multi-issue breakdowns, write or refresh the local recommended order file after the issue files exist, using only the approved issue set.
   - If refreshing an existing order file for the same parent PRD or planning artifact, replace its generated content instead of appending stale duplicates.
   - For single-issue breakdowns, skip the order file and record the skip reason for the final report.

8. Finalize and report:
   - Re-read generated issue files for numbering, blockers, acceptance criteria, user stories, fresh-agent-ready source links, expected proof, implementation route, and local-only behavior.
   - For multi-issue breakdowns, re-read the order file for parent path, update date, generated issue paths, dependency order, blockers, AFK/HITL type, `Not started` status placeholders, and stale-entry replacement.
   - Check that generated issues do not depend on hidden chat history, ignored `.local/` notes, or unlinked upstream sources.
   - Check that generated issues and order files are not bloated implementation transcripts, stale command inventories, or full code snippets.
   - Report created issue paths, the order file path or single-issue skip reason, blocker order, warnings, assumptions, and any PRD gaps that remain.
   - Recommend the next skill, usually `grill-with-docs` before implementation unless the issue is tiny and mechanical, then `writing-plans` for exact executable steps, `prototype` for a risky focused issue, or `tdd` for the first implementation slice.
   - Use `verification-before-completion` before claiming the issue set is complete, checked, or ready for implementation; for proposal-only breakdowns, verify only the claim being made and state remaining approval or PRD gaps.

## Output Contract

Before writing files, present an approval breakdown shaped like this:

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

After approval, write each issue using this default template:

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

For approved multi-issue breakdowns, write or refresh the local recommended order file after the issue files exist:

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

After writing, report:

- issue files created in dependency order;
- order file path for multi-issue breakdowns, or the single-issue skip reason;
- parent PRD path;
- warnings or broad-PRD concerns raised;
- assumptions and derived user stories;
- unresolved blockers or PRD gaps;
- fresh-agent-ready handoff coverage, including any missing first reads, source links, proof expectations, or scope exclusions;
- recommended next implementation slice or skill.

## Delegation

The main agent owns PRD readiness judgment, slicing strategy, approval, final issue content, and user communication.

When subagents are available, use them only for bounded evidence gathering that can return paths and source evidence, such as:

- finding existing issue conventions and next issue numbers;
- finding or checking an existing recommended order file for the same parent PRD or planning artifact;
- summarizing the PRD requirements, goals, non-goals, and user stories;
- inspecting one relevant source or test area for current implementation state;
- checking whether proposed slices are vertical, foundation-heavy, or overbroad;
- reviewing generated issue and order files for local-only behavior, blocker order, acceptance criteria, source links, expected proof, stale-entry replacement, and hidden-session independence.

Require every subagent result to include:

- paths inspected;
- commands run or deliberately skipped;
- source evidence found;
- assumptions and confidence;
- candidate concerns or corrections, not final user-facing conclusions.

If subagents are unavailable, perform the same work sequentially with a narrower context budget.

## Guardrails

- Do not write issue files before the user approves the proposed breakdown.
- Do not write or refresh a recommended order file before the user approves the proposed breakdown.
- Do not modify, close, rename, or append generated issue lists to the parent PRD.
- Do not append refreshed order-file entries to stale generated content; replace the order file from the approved issue set.
- Do not create remote issue tracker records, tracker sync, labels, projects, milestones, assignees, cards, or tickets in V1. A remote issue tracker variant belongs in a future companion skill or upgrade.
- Do not assume a remote issue tracker, label vocabulary, assignee model, milestone model, or project board exists.
- Do not create generated global issue indexes, background regeneration jobs, filesystem watchers, live project-board state, or other automation around order files.
- Do not slice from an unready PRD; pause and report readiness gaps instead.
- Do not create horizontal layer-only issues unless they are narrow foundation issues with a meaningful interface, hidden complexity, named dependents, and concrete verification.
- Do not create broad foundation, setup, scaffold, or architecture issues that delay all user-verifiable behavior.
- Do not rely on hidden chat history, ignored `.local/` notes, or unlinked upstream sources as required context for a generated issue.
- Do not include long file inventories, stale code paths, stale command inventories, full code snippets, or step-by-step implementation plans unless a compact source-grounded note prevents a likely mistake.
- Do not bury durable source context inside optional implementation notes when it belongs in recommended first reads or relevant source links.
- Do not publish private notes, credentials, client data, sensitive personal context, ignored scratch content, or real user data into tracked issue files.
- Do not treat the issue count as a hard rule; use roughly 10-12 issues as a review signal, alongside dependency and granularity judgment.
- Prefer explicit warnings and approval iteration over quietly encoding uncertainty in durable issue files.

## References

No external references are required. This skill is self-contained after installation.
