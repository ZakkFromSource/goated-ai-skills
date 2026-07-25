---
name: write-a-spec
description: Use when fuzzy product or delivery intent needs a proportionate compact or full spec before architecture, ticket slicing, or implementation.
metadata:
  goated-category: engineering
---

# Write A Spec

## Purpose

Turn unsettled intent into a source-grounded product or delivery contract at
the smallest useful depth. A spec captures stable intent, requirements,
acceptance criteria, constraints, and decisions without becoming an
implementation transcript.

Use `compact` mode for focused work. Use `full` mode only when larger,
cross-surface, architectural, migration, rollout, stakeholder, analytics, or
risk concerns justify the extra depth. A PRD is one possible spec form; this
skill does not require PRD terminology.

## Inputs

- User request, clarified brief, roadmap item, discovery result, or existing
  draft spec.
- Current project conventions and the smallest relevant source, docs, decisions,
  constraints, and evidence.
- Requested or inferred mode: `compact` or `full`.
- Existing work-envelope decisions, open questions, approval, and evidence.
- Desired output location when the project already has a spec convention.

## Dependencies

Hard: None.

Soft:
- `grill-with-docs` when product intent, success criteria, or tradeoffs require
  human decisions
- `prototype` when cheap evidence should resolve a risky choice
- `design-codebase-architecture` when module or interface strategy must follow
  the accepted spec
- `spec-to-tickets` when an approved spec needs multiple delivery units
- `verification-before-completion` before a readiness claim

Fallback: Inspect available evidence, mark unresolved questions, and produce a
draft with a narrower readiness claim. Do not invent decisions or depend on the
GOATED source repository after installation.

## Workflow

1. **Confirm the artifact is useful.**
   - Create a durable spec only when intent, requirements, acceptance, or
     coordination needs to survive the current conversation.
   - Use direct work or an inline decision note for tiny, already-settled work.
   - Reuse an existing project spec convention. Otherwise default to
     `docs/specs/<YYYY-MM-DD>-<slug>.md`.

2. **Choose proportional depth.**
   - Start in `compact` mode unless current evidence justifies `full`.
   - Compact mode covers: problem, goals, non-goals, requirements, acceptance
     criteria, constraints, and open questions.
   - Full mode adds only useful stakeholder, architecture, rollout, migration,
     analytics, and risk depth.
   - Omit empty sections. Promote a compact spec by reusing its evidence and
     decisions; do not restart discovery.

3. **Ground the contract.**
   - Inspect only sources that can change the spec: current behavior, durable
     decisions, user-facing docs, relevant interfaces, constraints, and nearby
     tests.
   - Separate facts, user decisions, agent recommendations, assumptions, and
     unresolved questions.
   - Ask only for decisions that cannot be discovered and materially affect
     scope, acceptance, risk, or action reach.

4. **Write stable intent.**
   - State the problem and affected users or operators.
   - Make goals outcome-oriented and non-goals explicit.
   - Write requirements as observable capabilities or durable constraints.
   - Write acceptance criteria so a future agent can prove each one.
   - Link relevant sources; avoid brittle file inventories, code snippets, and
     exact implementation sequences unless they encode an accepted constraint.

5. **Apply approval once.**
   - Reuse current consent when it already covers the spec write and its action
     reach.
   - Request approval only when required by the selected mode or host, or when
     scope or action reach materially expands.
   - Do not treat drafting a spec as approval to publish, deploy, or change an
     external tracker.

6. **Review readiness.**
   - Check internal consistency, source support, proportional depth, and proof
     coverage.
   - A spec is ticket-ready only when its delivery scope, acceptance criteria,
     blockers, and important open questions are settled enough to slice without
     hidden chat context.
   - Return `scope-changed` when discovery materially changes the agreed
     contract and `documentation-impact` when the durable spec is created or
     updated.

## Output Contract

Create or update one spec using
[Spec Template](references/spec-template.md), then return a compact delta:

- path and mode;
- status: `draft`, `decision-needed`, `approved`, or `ticket-ready`;
- sources and evidence reused;
- decisions, assumptions, and open questions;
- readiness for `spec-to-tickets`, architecture work, or direct delivery;
- approval reused or requested;
- changes, risks, route signals, and skipped checks.

## Delegation

The main agent owns mode, scope, decisions, approval interpretation, readiness,
and final wording. Delegate only bounded evidence collection or one review axis.
Require inspected paths, evidence, assumptions, uncertainty, and recommended
spec changes. Keep the workflow single-agent-compatible.

## Guardrails

- Do not force every request into a tracked spec.
- Do not choose full mode merely because its template exists.
- Do not retain empty sections or duplicate linked source content.
- Do not disguise unsettled decisions as requirements.
- Do not turn the spec into a backlog, ticket set, or exact implementation plan.
- Do not claim ticket readiness while material scope, acceptance, or blocker
  questions remain unresolved.
- Do not overwrite historical PRDs merely to adopt V2 vocabulary.
- Do not publish or sync to a remote system without separate authorization.

## References

Use [Spec Template](references/spec-template.md) when creating or revising the
artifact.
