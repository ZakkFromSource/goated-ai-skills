---
name: wayfinder
description: Use when branching uncertainty spans multiple focused sessions, later decisions depend on earlier evidence, and the complete route to a named planning destination cannot yet be specified responsibly.
metadata:
  goated-category: agent-workflows
---

# Wayfinder

## Purpose

Navigate large, branching uncertainty by maintaining only the visible decision
frontier until a named planning destination is ready.

Wayfinder produces decisions and reusable evidence across focused sessions. It
does not implement the destination. Research, disposable prototypes, and
bounded prerequisites may support decisions, but production implementation,
migration execution, publication, and deployment stay outside the map.

## Inputs

- A large uncertain effort or an existing Wayfinder map.
- A named destination workflow and completion condition, such as an approved
  spec or an architecture blueprint.
- Relevant project evidence, constraints, prior decisions, and approvals.
- A configured tracker when the project already uses one, or permission to use
  the local Markdown fallback.
- The current action reach and any human, credential, access, or review gates.

## Dependencies

Hard: None.

Soft:
- `using-goated-ai-skills` to select Wayfinder proportionately
- `grill-with-docs` for decisions grounded in project docs or source
- `grill-me` for conversation-grounded decisions
- `prototype` when a disposable artifact can distinguish live options
- `write-a-spec` or `design-codebase-architecture` as common destinations
- `handoff` when continuity must survive outside the map

Fallback: Without companion skills or a configured tracker, use focused
reasoning and the local Markdown contract in
[Wayfinder Artifact Templates](references/artifact-templates.md). Mark missing
evidence and human gates instead of inventing answers.

## Workflow

1. **Apply the activation gate.**
   - Select Wayfinder only when uncertainty branches, later decisions depend on
     earlier answers, the effort exceeds one focused session, and the complete
     route cannot yet be specified responsibly.
   - Reject session-sized discussion and route it to a focused grill or direct
     decision.
   - Reject large implementation whose decisions are already settled and route
     it to the named planning or delivery workflow.
   - Size alone never selects Wayfinder.

2. **Propose the chart before writing it.**
   - Name the destination and what would make it exist.
   - Propose the tracker or local location, currently visible frontier, action
     reach, and initial write scope.
   - Obtain approval covering all five dimensions before creating the map or
     decision records. Existing envelope consent satisfies this gate when it
     already covers all five chart dimensions.
   - Reuse approval while its scope and reach still cover the work. Get fresh
     approval before an expanded location, scope, or action reach.

3. **Create or load the low-resolution map.**
   - With no configured tracker, use
     `docs/wayfinding/<effort-slug>/map.md` and numbered decision records under
     `decisions/`.
   - Read the map first, then open only the decision and evidence needed for the
     current focus.
   - Keep destination, standing constraints, decision pointers, current
     frontier, not-yet-specified fog, and out-of-scope work distinct.
   - Use the templates reference whenever creating or materially reshaping
     local artifacts.

4. **Chart only the visible frontier.**
   - Create a decision record only when its question is precise now. Inability
     to answer it yet is not fog.
   - Keep suspected but still-imprecise questions in `Not Yet Specified`.
   - Keep work beyond the destination in `Out Of Scope`; it never graduates
     merely because it becomes clearer.
   - Record blockers as links or stable identifiers. Do not copy the
     authoritative detail into the map.

5. **Classify each decision independently.**
   - Choose one type: `grilling`, `research`, `prototype`, or `prerequisite`.
   - Choose `HITL` when resolution requires a human decision, live reaction,
     credential, access grant, external approval, or other human-only input.
     Otherwise choose `AFK`.
   - Do not infer mode from type. Research can be HITL; a prototype can be AFK;
     a prerequisite can use either mode.
   - A prerequisite is allowed only when it is necessary to make a decision
     possible, remains bounded to that need, and has approval for its reach.

6. **Resolve one primary decision focus per invocation.**
   - Choose one frontier decision, respecting blockers and an explicit user
     choice.
   - Use grilling, research, a disposable prototype, or a bounded prerequisite
     only to answer that question.
   - Record evidence as links with enough provenance and freshness to reuse.
     Store the resolution in the decision record; add only a one-line gist and
     link to the map.
   - Supporting evidence work may be delegated when available, but local
     claims or ordering remain advisory unless the configured tracker or
     runtime actually enforces them.

7. **Advance the map without duplicating authority.**
   - Graduate fog only when it has become a precise question.
   - Add or clear blockers from the evidence that changed them.
   - Update invalidated frontier items and out-of-scope findings.
   - Keep authoritative decisions in one decision record and authoritative
     evidence in its source or evidence entry.

8. **Set the lifecycle state from evidence.**
   - `active`: at least one decision focus can advance.
   - `blocked`: progress depends on a named blocker; record reason and resume
     condition.
   - `on-hold`: intentionally paused; record reason and review condition.
   - `destination-ready`: the decisions and evidence are sufficient for the
     named destination workflow, but its artifact does not yet exist.
   - `completed`: the named destination exists and the map links it.
   - `dropped`: the effort will not continue; record the reason and replacement
     when one exists.
   - Do not invent a universal transition graph. Apply the state whose evidence
     is true and preserve the information needed to review or resume it.

9. **Hand off without restarting discovery.**
   - Pass the destination workflow links to settled decisions, current
     evidence, standing constraints, and remaining uncertainty.
   - Let that workflow create its own artifact. Wayfinder never performs the
     production work described by the artifact.
   - Mark the map `destination-ready` before creation, then `completed` only
     after the destination exists and is linked.

## Output Contract

Each invocation returns or persists a compact delta:

- selected, rejected, or loaded route and why;
- approved destination, location, frontier, action reach, and write scope;
- one primary decision focus with type, mode, blockers, evidence, and
  resolution state;
- fog, frontier, blocker, decision-pointer, and out-of-scope changes;
- map lifecycle state plus required resume, review, destination, or drop data;
- destination handoff status and reusable evidence links;
- production-execution boundary confirmation and residual uncertainty.

In integrated use, update the shared envelope and artifacts without emitting a
second full task closeout. Standalone use returns the same delta and the local
artifact paths.

## Delegation

The main agent owns destination interpretation, approvals, frontier judgment,
state changes, final decisions, and user communication.

Delegate only bounded evidence gathering, one disposable prototype, one
source-family scan, or an independent map consistency review. Require inspected
sources, commands or actions run, evidence links, assumptions, uncertainty,
status, and recommendation. A delegate must not resolve a HITL decision for the
human, expand action reach, mutate the destination, or execute production work.

If delegation is unavailable, perform the same bounded work sequentially. Do
not require subagents or pretend local concurrency claims are enforced.

## Guardrails

- Never select Wayfinder because work is merely large.
- Never create chart artifacts before the five-part proposal is approved.
- Never pre-slice fog into speculative decision tickets.
- Never let a map note, user urgency, available code access, or an almost-ready
  implementation override the no-production-execution boundary.
- Never disguise destination delivery as a prerequisite.
- Never treat `destination-ready` as `completed`.
- Never let an agent answer the human side of a HITL decision.
- Never duplicate full decisions, evidence, specs, or architecture detail into
  the map.
- Never require a remote tracker, subagents, fixed context size, branch model,
  or runtime concurrency enforcement.
- Never require this source repo, its root docs, its tickets, or the upstream
  inspiration after installation.

## References

Read [Wayfinder Artifact Templates](references/artifact-templates.md) when
creating, converting, or materially updating a local map or decision record.
