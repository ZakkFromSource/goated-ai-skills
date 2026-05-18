---
name: prd-to-issues
category: engineering
classification: portable
status: wip
description: Break a scoped PRD into approved local vertical-slice issue handoffs with acceptance criteria, blockers, and user stories. Use when a target-project PRD is ready to become dependency-ordered Markdown issue files for AFK or HITL implementation.
triggers:
  - user asks to turn a PRD, product requirements document, product spec, implementation spec, roadmap item, or plan into issues
  - user wants local issue handoffs, implementation tickets, work slices, or agent-ready tasks from a scoped PRD
  - target-project delivery needs independently workable vertical slices before TDD, implementation, review, or handoff
  - a future agent needs a PRD decomposed into blocker-aware AFK and HITL issues
outputs:
  - approval-ready issue breakdown with title, type, blockers, user stories, acceptance focus, and foundation rationale when relevant
  - local Markdown issue handoffs named issues/NNN-short-title.md by default
  - blocker and foundation issues written before dependent issues
  - concise vertical-slice issue bodies with acceptance criteria, blockers, and user stories
  - warnings when the PRD may be too broad or not ready for issue breakdown
depends_on:
  hard: []
  soft:
    - session-start-progressive-disclosure before slicing an unfamiliar target project
    - grill-with-docs when PRD scope, project language, standards, architecture, or approval tradeoffs are unclear
    - write-a-prd when the PRD is missing, stale, ambiguous, or not ready for issue breakdown
    - prototype when a risky issue slice depends on a disposable experiment verdict
    - context-matrix-map when docs/agents/context-matrix.md exists or source discovery is needed
    - project-context-calibration when root CONTEXT.md exists or project language affects issue wording
    - project-standards-calibration when project standards affect issue scope, verification, or acceptance
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

Use this skill after a PRD is ready for breakdown. Each issue should be a balanced vertical tracer bullet: narrow enough to complete with quality, but complete enough that the resulting behavior is independently verifiable. The workflow is local-only in V1; it creates files inside the target project and does not publish to remote issue trackers.

## Inputs

- Scoped PRD, product spec, implementation spec, roadmap plan, issue, or approved planning artifact.
- Target-project root path.
- Existing local issue convention, such as `issues/NNN-short-title.md`, if present.
- Existing root `CONTEXT.md`, `docs/agents/context-matrix.md`, and `docs/agents/project-standards.md`, if present.
- Relevant docs, ADRs, standards, source files, tests, schemas, prototypes, or prior issue handoffs needed to understand current implementation state.
- Clarified work brief from `grill-with-docs`, when available or needed.

## Workflow

1. Confirm the source and target:
   - Identify the PRD or planning artifact being sliced and the target project where local issues should be written.
   - Confirm the PRD describes one coherent product or delivery outcome.
   - Treat the PRD as the upstream contract. Read it, reference it, and surface gaps, but do not edit it during this workflow.

2. Discover local conventions and current state:
   - Inspect the target project before slicing. Read only the docs, standards, ADRs, source areas, tests, and prior issues needed to understand current implementation state.
   - Prefer an existing local issue convention when one is discoverable.
   - If no local issue convention exists, default to tracked files under `issues/`.
   - If multiple plausible local issue conventions exist, ask the user which one should receive the generated issue files.
   - Scan active and archived local issue files before writing to choose the next highest unused `NNN` number.

3. Check PRD readiness:
   - Verify the PRD has enough goal, audience, scope, non-goal, requirement, acceptance, and blocker detail to split work safely.
   - If the PRD is ambiguous, stale, missing important acceptance criteria, or still has blocking open questions, pause and report the gaps.
   - Recommend `write-a-prd` or a focused `grill-with-docs` follow-up when the PRD needs repair.
   - Do not write assumption-heavy issues just to keep moving.

4. Draft balanced vertical slices:
   - Prefer one narrow, complete, verifiable behavior per issue.
   - Avoid horizontal slices such as "add schema", "add API", "build UI", or "write tests" when they do not prove behavior on their own.
   - Prefer several thin tracer bullets over a few broad milestone issues.
   - Mark slices `AFK` by default. Use `HITL` when a slice requires a human decision, design review, credentials, external access, or another approval gate.
   - Use PRD user stories when present. If they are missing, derive concise stories from the PRD audience and goals, and label them as derived.

5. Allow only narrow foundation issues:
   - Create foundation issues only when they clearly unblock named dependent vertical slices.
   - Keep foundations small and verifiable.
   - Require a compact rationale naming the useful interface being created or clarified, the complexity it hides, and the dependent slices it unlocks.
   - Reject broad setup batches that do not create a meaningful interface or do not lead directly to vertical slices.
   - Write blocker and foundation issues before dependent issues so later issues can reference real local paths.

6. Present the approval breakdown before writing:
   - Draft the full issue set, grouped in dependency order.
   - For each proposed issue, show title, type, blockers, user stories, acceptance focus, and any foundation rationale.
   - Warn when the breakdown is hard to review, contains messy foundations, starts to look like milestones or subsystems, or produces roughly more than 10-12 issues.
   - Ask the user to approve the breakdown, including granularity, blocker relationships, user story coverage, and AFK/HITL labels.
   - Iterate until the user explicitly approves the breakdown.

7. Write local issue files after approval:
   - Create local Markdown issue files only after approval.
   - Use `issues/NNN-short-title.md` by default, or the discovered local convention when one exists.
   - Use kebab-case short titles in filenames.
   - Write files in dependency order, blockers first.
   - Reference blockers by local file path.
   - Include selective source-grounded implementation notes only when they prevent likely implementation mistakes.

8. Finalize and report:
   - Re-read generated issue files for numbering, blockers, acceptance criteria, user stories, and local-only behavior.
   - Report created issue paths, blocker order, warnings, assumptions, and any PRD gaps that remain.
   - Recommend the next skill, usually `prototype` for a risky focused issue or `tdd` for the first implementation slice.

## Output Contract

Before writing files, present an approval breakdown shaped like this:

```markdown
## Proposed Issue Breakdown

1. <Title>
   - Type: <AFK | HITL>
   - Blocked by: <local planned path/title or "None - can start immediately">
   - User stories addressed: <explicit or derived stories>
   - Acceptance focus: <observable behavior or verification target>
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

## Acceptance criteria

- [ ] <observable criterion>
- [ ] <observable criterion>

## Blocked by

- `<local issue path>`

Or:

- None - can start immediately

## User stories addressed

- <story from PRD, or "Derived: As a ..., I can ..., so that ...">

## Implementation notes

- <Optional. Include only source-grounded notes that prevent likely mistakes. Omit this section when it adds no value.>
```

After writing, report:

- issue files created in dependency order;
- parent PRD path;
- warnings or broad-PRD concerns raised;
- assumptions and derived user stories;
- unresolved blockers or PRD gaps;
- recommended next implementation slice or skill.

## Delegation

The main agent owns PRD readiness judgment, slicing strategy, approval, final issue content, and user communication.

When subagents are available, use them only for bounded evidence gathering that can return paths and source evidence, such as:

- finding existing issue conventions and next issue numbers;
- summarizing the PRD requirements, goals, non-goals, and user stories;
- inspecting one relevant source or test area for current implementation state;
- checking whether proposed slices are vertical, foundation-heavy, or overbroad;
- reviewing generated issue files for local-only behavior, blocker order, and acceptance criteria.

Require every subagent result to include:

- paths inspected;
- commands run or deliberately skipped;
- source evidence found;
- assumptions and confidence;
- candidate concerns or corrections, not final user-facing conclusions.

If subagents are unavailable, perform the same work sequentially with a narrower context budget.

## Guardrails

- Do not write issue files before the user approves the proposed breakdown.
- Do not modify, close, rename, or append generated issue lists to the parent PRD.
- Do not create remote issue tracker records, labels, projects, milestones, cards, or tickets in V1. A remote issue tracker variant belongs in a future companion skill or upgrade.
- Do not assume a remote issue tracker, label vocabulary, assignee model, milestone model, or project board exists.
- Do not slice from an unready PRD; pause and report readiness gaps instead.
- Do not create horizontal layer-only issues unless they are narrow foundation issues with a meaningful interface, hidden complexity, named dependents, and concrete verification.
- Do not create broad foundation, setup, scaffold, or architecture issues that delay all user-verifiable behavior.
- Do not include long file inventories, stale code paths, or step-by-step implementation plans unless a source-grounded note prevents a likely mistake.
- Do not publish private notes, credentials, client data, sensitive personal context, ignored scratch content, or real user data into tracked issue files.
- Do not treat the issue count as a hard rule; use roughly 10-12 issues as a review signal, alongside dependency and granularity judgment.
- Prefer explicit warnings and approval iteration over quietly encoding uncertainty in durable issue files.

## References

No external references are required. This skill is self-contained after installation.
