---
name: grill-with-docs
category: engineering
classification: portable
status: wip
description: Pressure-test important target-project work against available docs, standards, ADRs, and project facts before implementation begins.
triggers:
  - user asks to be grilled, challenged, pressure-tested, or interviewed about a plan, PRD, architecture choice, workflow change, or ambiguous feature
  - target-project onboarding is starting
  - target-project delivery involves PRD-level planning, architecture changes, cross-file work, unclear intent, or public-facing behavior
  - agent detects that success criteria, scope boundaries, project language, or documented decisions are unclear
outputs:
  - clarified goal and success criteria
  - scope boundaries, non-goals, and affected project areas
  - decisions made, assumptions confirmed, and remaining questions
  - source-grounded notes from docs, standards, ADRs, code, tests, or project facts
depends_on:
  hard: []
  soft:
    - session-start-progressive-disclosure before grilling an unfamiliar target project
    - context-matrix-map when docs/agents/context-matrix.md exists or onboarding should discover project sources
    - project-context-calibration when project language, boundaries, or architecture vocabulary need durable capture
    - project-standards-calibration when standards affect the decision
  fallback: If project docs or companion skills are unavailable, inspect the minimum relevant local evidence and state lower confidence before asking questions.
adapters:
  codex: usable
  claude-code: usable
  hermes: usable
  opencode: usable
  generic-agent: usable
---

# Grill With Docs

## Purpose

Clarify important work by challenging the user's intent against the target project's documented language, standards, ADRs, code behavior, tests, and available facts.

Use this skill before costly or ambiguous work so the agent and user reach shared understanding before implementation. The goal is not to interrogate every request; it is to find the decisions that would otherwise become rework.

## Inputs

- User request, plan, PRD draft, architecture idea, issue, or feature description.
- Target-project root path.
- Existing root `CONTEXT.md`, if present.
- Existing `docs/agents/context-matrix.md`, if present.
- Existing `docs/agents/project-standards.md`, if present.
- Relevant README files, contributor docs, feature docs, specs, PRDs, ADRs, issue threads, glossary or context docs, and agent instructions.
- Relevant source files, tests, schemas, commands, or runtime behavior when they can answer factual questions.
- User constraints, preferences, deadlines, risk tolerance, and intended audience when not discoverable from project files.

## Workflow

1. Decide whether the grill is mandatory:
   - Treat this skill as gated mandatory for target-project onboarding, PRDs, architecture changes, cross-file work, unclear requests, public-facing behavior, and work where project standards or domain language matter.
   - Skip it for tiny mechanical edits with obvious scope, such as a typo fix, one-line rename, formatting-only change, or direct command the user already specified.
   - If skipping, say briefly why the request is small enough to proceed without a grill.

2. Gather project facts first:
   - Start from the user's request and target-project root.
   - If a context matrix exists, use it to pick the first project sources to read.
   - Read standards, ADRs, glossary/context docs, relevant specs, issue files, and nearby source or tests only as needed.
   - Prefer discoverable facts over user questions. If code, docs, tests, config, or command definitions can answer something, inspect them before asking.
   - Stop gathering when the remaining uncertainty is a decision, tradeoff, preference, or missing product intent.

3. Identify the decision tree:
   - Restate the likely goal and why the work matters.
   - List the decision branches that materially affect design, scope, behavior, testing, docs, migration, rollout, or user experience.
   - Order questions so upstream decisions are resolved before dependent details.
   - Avoid dumping every possible question at once.

4. Ask one decision-shaping question at a time:
   - Ask only one focused question, then wait for the user's answer before continuing.
   - Include the recommended default and the evidence or reasoning behind it.
   - Ask about choices, priorities, boundaries, tradeoffs, and intent, not facts the agent should discover.
   - When the user uses vague or overloaded terms, propose a precise term and ask them to confirm or correct it.

5. Challenge against docs and project reality:
   - Compare user statements with documented standards, ADRs, glossary/context language, source behavior, tests, and known constraints.
   - Surface contradictions directly and ask which source should win.
   - Use concrete scenarios and edge cases to test boundaries between concepts.
   - Call out when a decision would conflict with existing standards, require a new ADR, or need follow-up documentation.

6. Capture decisions as they settle:
   - Keep a running summary of clarified goal, success criteria, scope, non-goals, decisions, assumptions, and remaining questions.
   - Note which project sources support or contradict each decision.
   - If the project has a documented glossary, standards profile, ADR process, or doc-sync workflow, identify updates that should happen after the decision is confirmed.
   - Do not create new durable docs during the grill unless the user asked for that or the target project's established workflow requires it.

7. Stop at shared understanding:
   - Stop when implementation can begin safely, the next skill should take over, or a blocker needs user or stakeholder input.
   - Recommend the next direct action or skill, such as `write-a-prd`, `context-matrix-map`, `project-context-calibration`, `project-standards-calibration`, `architecture-design-map`, `tdd`, or `doc-sync`.
   - If the user decides to proceed with known ambiguity, name the risk clearly.

## Output Contract

During the grill, keep the conversation one-question-at-a-time. After enough decisions are resolved, return a compact working brief:

```markdown
## Clarified Work

- Goal: <one sentence>
- Success criteria: <observable outcomes>
- Scope: <included areas>
- Non-goals: <excluded areas>
- Affected sources: <docs, code, tests, ADRs, standards, or "not yet verified">

## Decisions

| Decision | Outcome | Evidence or rationale |
| --- | --- | --- |

## Assumptions

- <confirmed or still-active assumption>

## Remaining Questions

- <question, owner, and when it must be answered>

## Next Step

- <recommended direct action or next skill>
```

When the grill is skipped, report:

- why the request qualifies as a tiny mechanical edit;
- any facts already verified;
- the direct next action.

## Delegation

The main agent owns the user interview, decision ordering, recommendations, final synthesis, and when to stop.

When subagents are available, use them only for bounded evidence gathering that can run independently, such as:

- finding relevant docs, ADRs, standards, or context files;
- checking whether code or tests contradict a user statement;
- summarizing one feature area or source family;
- collecting existing project terminology around one domain concept.

Require every subagent result to include:

- paths inspected;
- commands run or deliberately skipped;
- exact source evidence found;
- assumptions and confidence;
- candidate questions or contradictions, not direct user-facing conclusions.

If subagents are unavailable, perform the same evidence gathering sequentially with a narrower context budget.

## Guardrails

- Do not ask the user for discoverable facts before inspecting available project evidence.
- Do not turn tiny mechanical edits into a planning ceremony.
- Do not ask multiple decision questions at once unless the user explicitly asks for a questionnaire.
- Do not treat undocumented guesses as project facts.
- Do not override existing ADRs, standards, glossary terms, or code behavior silently; surface conflicts and ask which source should change.
- Do not create or edit durable docs during the grill unless the user requested it or the target project's established workflow calls for immediate capture.
- Do not include private notes, ignored local scratch files, credentials, client data, or sensitive personal context in tracked outputs.
- Prefer concrete scenarios, observable success criteria, and named tradeoffs over abstract brainstorming.

## References

This skill is self-contained after installation.

Inspired by [Matt Pocock's grill-with-docs skill](https://github.com/mattpocock/skills/tree/main/skills/engineering/grill-with-docs): ask one decision-shaping question at a time, inspect code and docs for discoverable facts, challenge language against project context, and offer ADRs only for decisions that are costly, surprising, and tradeoff-driven.
