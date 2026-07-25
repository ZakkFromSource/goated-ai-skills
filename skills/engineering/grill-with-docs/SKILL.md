---
name: grill-with-docs
description: Use when important target-project work needs docs-grounded clarification, pressure testing, success criteria, or scope decisions before implementation.
metadata:
  goated-category: engineering
---

# Grill With Docs

## Purpose

Clarify important work by challenging the user's intent against the target project's documented language, standards, ADRs, code behavior, tests, and available facts.

Use this skill before costly or ambiguous work so the agent and user reach shared understanding before implementation. The goal is not to interrogate every request; it is to find the decisions that would otherwise become rework.

## Inputs

- User request, plan, PRD draft, architecture idea, issue, or feature description.
- Target-project root path.
- Existing root `CONTEXT.md`, nested context docs, or `CONTEXT-MAP.md`, if present.
- Existing `docs/agents/context-matrix.md`, if present.
- Existing `docs/agents/project-standards.md`, if present.
- Relevant README files, contributor docs, feature docs, specs, PRDs, ADRs, issue threads, glossary or context docs, and agent instructions.
- Relevant source files, tests, schemas, commands, or runtime behavior when they can answer factual questions.
- User constraints, preferences, deadlines, risk tolerance, and intended audience when not discoverable from project files.

## Dependencies

Hard: None.

Soft:
- session-start-progressive-disclosure for unfamiliar target projects
- context-matrix-map when docs/agents/context-matrix.md exists or source discovery is needed
- project-context-calibration when language, boundaries, or architecture vocabulary need durable capture
- project-standards-calibration when standards affect the decision
- doc-sync when settled decisions require documentation follow-up after the grill
- verification-before-completion before complete/checked/implementation-ready grill claims

Fallback: If docs or companion skills are unavailable, inspect minimal evidence and state lower confidence before asking questions.

## Workflow

1. Decide whether the grill is mandatory:
   - Treat this skill as gated mandatory for target-project onboarding, PRDs, architecture changes, cross-file work, unclear requests, public-facing behavior, and work where project standards or domain language matter.
   - Skip it for tiny mechanical edits with obvious scope, such as a typo fix, one-line rename, formatting-only change, or direct command the user already specified.
   - If skipping, say briefly why the request is small enough to proceed without a grill.

2. Gather project facts first:
   - Start from the user's request and target-project root.
   - If a context matrix exists, use it to pick the first project sources to read.
   - Read standards, ADRs, glossary/context docs, relevant specs, issue files, and nearby source or tests only as needed.
   - If project language, glossary/context docs, `CONTEXT.md`, `CONTEXT-MAP.md`, ownership, boundaries, or cross-context meaning affects the grill, read [references/context-docs.md](references/context-docs.md).
   - If a settled decision may be costly to reverse, surprising without context, and tradeoff-driven, read [references/adr-capture.md](references/adr-capture.md) before recommending ADR capture.
   - Prefer discoverable facts over user questions. If code, docs, tests, config, or command definitions can answer something, inspect them before asking.
   - Stop gathering when the remaining uncertainty is a decision, tradeoff, preference, or missing product intent.

3. Select the clarification mode and budget:
   - Honor an explicit user choice; otherwise recommend the least intensive mode that can resolve the material decisions:
     - **focused**: one dependent or high-risk decision at a time;
     - **rapid**: one compact batch of no more than three tightly related questions;
     - **recommend-and-proceed**: state provisional defaults and continue for reversible, low-risk choices;
     - **deep-dive**: follow the material decision tree without a preset question limit for major architecture, fuzzy products, or decision-complete work.
   - Outside deep-dive, derive a soft question budget from workflow intensity: normally one for `lightweight`, up to three for `standard`, and up to five for `full`. Use fewer questions when evidence or safe defaults settle the work.
   - Treat the budget as pressure toward decision value, not permission to ask discoverable facts. If the remaining decision does not fit, summarize progress and ask whether to continue, change mode, defer it, or proceed with named ambiguity.
   - In recommend-and-proceed, never default an irreversible, destructive, security-sensitive, privacy-sensitive, externally binding, or otherwise high-risk decision. Stop for an explicit human choice.

4. Identify the decision tree:
   - Restate the likely goal and why the work matters.
   - List the decision branches that materially affect design, scope, behavior, testing, docs, migration, rollout, or user experience.
   - Include scenario probes when they would clarify lifecycle, ownership, identity, cardinality, partial vs whole operations, failure states, or cross-context effects.
   - Order questions so upstream decisions are resolved before dependent details.
   - Avoid dumping every possible question at once.

5. Ask according to the selected mode:
   - In focused and deep-dive modes, ask one focused question, then wait for the user's answer. Rapid mode may ask its tightly related batch together.
   - Include a recommended default and the evidence or rationale behind it in every decision-shaping question.
   - Ask about choices, priorities, boundaries, tradeoffs, and intent, not facts the agent should discover.
   - When the user uses vague or overloaded terms, propose a precise term and ask them to confirm or correct it.
   - In recommend-and-proceed, record reversible low-risk defaults as provisional rather than confirmed user decisions, then continue within the approved scope.

6. Challenge against docs and project reality:
   - Compare user statements with documented standards, ADRs, glossary/context language, source behavior, tests, and known constraints.
   - Surface contradictions directly and ask which source should win.
   - Use concrete scenarios and edge cases to test boundaries between concepts.
   - Call out when a decision would conflict with existing standards, may qualify for ADR capture, or need follow-up documentation.

7. Capture decisions as they settle:
   - Keep a running summary of clarified goal, success criteria, scope, non-goals, assumptions, and decisions separated into `settled`, `provisional`, `deferred`, and `conflicting`.
   - In deep-dive mode, summarize those four decision states after each coherent decision cluster, when the tree changes materially, or before context becomes hard to retain.
   - Note which project sources support or contradict each decision.
   - List candidate durable updates for `CONTEXT.md`, ADRs, standards docs, PRDs, or doc-sync follow-up.
   - Route target-project `CONTEXT.md` curation to `project-context-calibration` when that skill is available.
   - Route standards or enforcement updates to `project-standards-calibration` when that skill is available.
   - Recommend ADR capture only after checking the target project's existing ADR convention; if none exists, suggest a default only when the user asks to create one.
   - Do not create new durable docs during the grill unless the user asked for that or the target project's established workflow requires it.

8. Route prototypes only for decision evidence:
   - Route to `prototype` only when running, clicking, toggling, or inspecting a disposable experiment would distinguish live options more reliably than further discussion or existing evidence.
   - State one decision question and the evidence needed from the prototype. Do not frame the prototype as production implementation or use it to postpone a required human decision.
   - Skip prototyping when fresh docs, source, tests, or direct discussion already settle the choice.

9. Stop at shared understanding:
   - Stop when implementation can begin safely, the next skill should take over, or a blocker needs user or stakeholder input.
   - Recommend the next direct action or skill, such as `context-matrix-map`, `project-context-calibration`, `project-standards-calibration`, `prototype`, `write-a-spec`, `spec-to-tickets`, `writing-plans`, `design-codebase-architecture`, `architecture-design-map`, `tdd`, or `doc-sync`.
   - Use `verification-before-completion` before claiming the brief is complete, checked, or ready for implementation.
   - If the user decides to proceed with known ambiguity, name the risk clearly.

## Output Contract

During the grill, follow the selected mode and label provisional recommendations. In integrated use, update the shared envelope with the mode, question budget, settled/provisional/deferred/conflicting decisions, remaining questions, evidence, prototype verdict or route signal, and next action. Do not emit a second full task closeout. Standalone use returns this compact working brief:

```markdown
## Clarified Work

- Goal: <one sentence>
- Success criteria: <observable outcomes>
- Scope: <included areas>
- Non-goals: <excluded areas>
- Affected sources: <docs, code, tests, ADRs, standards, or "not yet verified">

## Decisions

| Decision | State | Outcome | Evidence or rationale |
| --- | --- | --- | --- |

## Assumptions

- <confirmed or still-active assumption>

## Remaining Questions

- <question, owner, and when it must be answered>

## Candidate Durable Updates

- Include only candidates such as `CONTEXT.md`, ADRs, standards docs, PRDs, or doc-sync follow-up; if none, say `None`.

| Artifact or workflow | Candidate update | Evidence or rationale | Recommended owner or next skill |
| --- | --- | --- | --- |

## Next Step

- <recommended direct action or next skill>
```

When the grill is skipped, report:

- why the request qualifies as a tiny mechanical edit;
- any facts already verified;
- the direct next action.

## Delegation

Main owns the interview, decision order, recommendations, synthesis, and stop
point. Delegate only bounded source discovery, contradiction checks, one
feature summary, or terminology collection. Return exact paths, commands,
evidence, assumptions, confidence, and candidate questions or contradictions,
not user-facing conclusions. Without delegation, gather evidence sequentially.

## Guardrails

- Do not ask the user for discoverable facts before inspecting available project evidence.
- Do not turn tiny mechanical edits into a planning ceremony.
- Do not ask multiple decision questions at once outside rapid mode or an explicit questionnaire.
- Do not exceed three tightly related questions in rapid mode or impose an arbitrary limit in deep-dive mode.
- Do not silently default irreversible or high-risk decisions in recommend-and-proceed mode.
- Do not treat undocumented guesses as project facts.
- Do not override existing ADRs, standards, glossary terms, or code behavior silently; surface conflicts and ask which source should change.
- Do not create or edit durable docs during the grill unless the user requested it or the target project's established workflow calls for immediate capture.
- Do not treat root `CONTEXT.md`, nested context docs, `CONTEXT-MAP.md`, or ADR directories as universal requirements.
- Do not duplicate `project-context-calibration`; this skill identifies candidate context updates and routes curation when that companion skill is available.
- Do not include private notes, ignored local scratch files, credentials, client data, or sensitive personal context in tracked outputs.
- Prefer concrete scenarios, observable success criteria, and named tradeoffs over abstract brainstorming.

## References

This skill is self-contained after installation.

Linked support files, read at the workflow gates above: [references/context-docs.md](references/context-docs.md) and [references/adr-capture.md](references/adr-capture.md).
