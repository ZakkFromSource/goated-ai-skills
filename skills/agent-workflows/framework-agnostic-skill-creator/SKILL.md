---
name: framework-agnostic-skill-creator
description: Use when creating a new GOATED skill from clarified intent or porting, adapting, sanitizing, or publishing an existing skill, command, prompt, workflow, or agent instruction for portable GOATED use.
metadata:
  goated-category: agent-workflows
---

# Framework-Agnostic Skill Creator

## Purpose

Create self-contained GOATED skill folders that can travel across agent frameworks.

Modes:

- **Create** a new or revised skill from clarified reusable behavior.
- **Port** an existing prompt, command, workflow, instruction set, or skill.

Both preserve GOATED's schema, public boundary, dependency behavior,
compatibility caveats, delegation contract, and standalone behavior.

## Inputs

- User request and destination: skill, revision, review, private adaptation, or public contribution.
- Clarified intent, success criteria, audience, workflow scope, non-goals, and examples of user requests that should trigger the skill.
- Source workflow artifacts and adjacent support files when porting.
- Target GOATED category, installation context, portability needs, maturity expectations, and real compatibility constraints, if already decided.
- Public/private boundary requirements.
- Framework docs, repository standards, or licenses that materially affect reuse.

## Dependencies

Hard: None.

Soft:
- grill-with-docs when unresolved intent or conflicting source evidence materially blocks the skill change
- session-start-progressive-disclosure for unfamiliar target projects or source packages
- agent-instructions-integrator when target-project framework routing is needed
- handoff when skill creation or porting is interrupted or resumable

Fallback: If companion skills, source-framework docs, or live subagents are unavailable, inspect available artifacts, mark unverified assumptions, and state residual risk.

## Workflow

1. Select the mode and boundary:
   - Use create mode when the main input is clarified intent or reusable behavior rather than an existing source package.
   - Use port mode when the main input is existing source material; if both apply, audit the source first, then design the created GOATED skill.
   - Identify the intended output: implemented skill folder, patch to an existing skill, proposal, compatibility note, private fork artifact, or portability review.
   - Keep source repo guidance, installed skill behavior, and target-project artifacts distinct.
   - Resolve discoverable facts first. Use `grill-with-docs` only for a material unresolved decision; public visibility or cross-workflow scope alone does not require clarification.

2. Confirm the common contract:
   - State the behavior the skill should change, the audience, success criteria, scope, non-goals, and examples of triggering user requests.
   - Before creating or splitting a skill, ask whether independent invocation by a user, agent, router, or neighboring skill earns its discovery and context cost. Otherwise keep the behavior with its owner or a linked reference.
   - Give each important phase an observable completion condition. Put final artifacts or decisions in `## Output Contract`; an attempt or plausible summary is not completion.

3. Read the selected mode's procedure:
   - For new or revised behavior, read [Create Or Revise](references/create-or-revise.md).
   - For an existing source workflow, read [Port A Workflow](references/port-workflow.md). If the source includes adjacent support files, also read [Source Package Audit](references/source-package-audit.md) before judging the port.
   - Read both modes only when the task needs both. End discovery when the selected contract and source evidence support the next action.

4. Draft the GOATED skill:
   - Use the normalized schema: top-level `name`, top-level `description`, and `metadata.goated-category`.
   - Choose `agent-workflows`, `engineering`, or `productivity`. Classify hard and soft dependencies, fallback behavior, and real compatibility constraints in the body.
   - Use the shortest description that preserves reliable selection. Compare neighboring descriptions; exclude likely misroutes without listing the entire workflow or every capability.
   - Make the body a framework-neutral operating procedure with `Purpose`, `Inputs`, `Dependencies`, `Workflow`, `Output Contract`, `Delegation`, `Guardrails`, and `References` when useful.
   - State outcomes, decisions, and non-obvious invariants. Reserve fixed sequences for operations where deviation causes a concrete problem; distinguish requirements from suggestions.
   - Keep support files one level below `SKILL.md` and link them directly with explicit read or run conditions. Keep branch-only detail behind those links and simple skills self-contained.
   - Avoid decorative files, standalone README files, install guides, and changelogs inside the skill package.
   - Keep `SKILL.md` under the soft 300-line review threshold whenever possible.
   - Attribute public inspiration when useful, but do not bulk-copy external material or private source text.
   - If the user requested review only, return the proposed shape and blockers without editing files.

5. Evaluate the skill:
   - For a new, substantially changed, or discipline-heavy skill, read [Skill Evaluation](./references/skill-evaluation.md).
   - Design pressure scenarios or representative usage scenarios before trusting the skill.
   - When live subagents are available and safe, run a RED baseline without the skill, capture failures or rationalizations, then run GREEN verification with the skill.
   - When live evaluation is unavailable, write the evaluation plan and residual risk instead of claiming behavioral proof.
   - Apply the reference's behavior, ownership, disclosure, and sequence-pressure lenses.
   - Add rationalization counters, stop rules, red flags, proof gates, or anti-pattern references when testing or review shows agents can dodge the intended behavior.

6. Validate the artifact:
   - Check the normalized schema, category metadata, discovery description, body activation conditions, output contract, dependencies, compatibility caveats, and self-contained runtime behavior.
   - Check that every local reference or script linked from `SKILL.md` exists and has a clear read or run condition.
   - Check that no root source-repo files are required after installation.
   - Check that private or sensitive content was removed, generalized, or kept in a private artifact.
   - Check that copied or adapted names, commands, instruction-file precedence, issue tracker conventions, and docs layouts fit the destination workflow and are not presented as universal GOATED requirements by accident.

## Output Contract

Use [Proposal And Report Templates](./references/proposal-and-report-templates.md) when producing a skill creator proposal, portability review, or edit report.

For proposals or reviews, include mode and intent, port manifest when relevant,
skill shape, support-file plan, evaluation, compatibility, privacy,
portability, and blockers.

For edits, report changed files, mode, category, relevant port manifest,
authoring decisions, evaluation, blockers, and verification.

## Delegation

Main owns the skill goal, public/private boundary, category, final artifact, and
communication. Delegate only bounded source inventory, behavior extraction,
scenario drafting, safe forward-testing, mechanics, privacy, schema, or
portability review; never delegate publication.

Return inspected and skipped sources, behavior, mechanics, evaluation evidence,
assumptions, risk, confidence, unresolved questions, status, and recommendation.
Resolve concerns or missing context before editing; narrow or stop on
`BLOCKED`. Without delegation, run the same passes sequentially and record live
evaluation gaps.

## Guardrails

- Do not publish credentials, secrets, client data, private project names, sensitive personal context, or private workflow assumptions in public main.
- Do not put workflow steps, proof gates, or implementation detail in `description`; keep `description` focused on triggers.
- Do not inspect only the obvious entrypoint when a provided source package includes first-party support files that may define real behavior.
- Do not assume one framework's instruction filename, command syntax, file mention behavior, plugin system, issue tracker, or docs layout is universal.
- Do not claim behavioral proof from skill evaluation unless scenarios actually ran; describe unrun checks as a plan or residual risk.
- Do not turn authoring review labels into mandatory GOATED terminology; use them only when they sharpen a concrete skill decision.
- Do not bulk-copy external source material; summarize behavior, respect licensing, and attribute public inspiration when relevant.
- Do not expand `SKILL.md` with long examples, templates, or generic compatibility matrices when a directly linked `references/` file would keep the skill lean.
- Do not require this source repo's root `AGENT.md`, `README.md`, `CONTEXT.md`, issues, `.local/`, or handoffs at installed runtime.
- Prefer explicit blockers over quiet assumptions when portability, privacy, or evaluation confidence is uncertain.

## References

Linked support files, read or use at the workflow/output gates above: [Create Or Revise](references/create-or-revise.md), [Port A Workflow](references/port-workflow.md), [Source Package Audit](references/source-package-audit.md), [Skill Evaluation](references/skill-evaluation.md), and [Proposal And Report Templates](references/proposal-and-report-templates.md).
