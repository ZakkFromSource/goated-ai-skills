---
name: grill-me
category: productivity
classification: portable
status: wip
description: Use when the user wants to be grilled, challenged, interviewed, or walked through a non-docs-grounded idea, topic, plan, choice, or decision.
triggers:
  - user says "grill me" about an idea, topic, question, plan, choice, or brainstorming thread
  - user asks to be challenged, interviewed, pressure-tested, or walked through a decision one question at a time
  - user wants to explore assumptions, tradeoffs, options, implications, or next moves using only conversation context and user-provided notes
  - user needs lightweight alignment before deciding whether to keep brainstorming, make a choice, write a PRD, prototype, implement, or switch to a docs-grounded grill
outputs:
  - clarified topic, central question, and desired outcome
  - assumptions, tradeoffs, options, and tensions surfaced during the interview
  - decisions or provisional conclusions, unresolved questions, and next move
  - recommended defaults for decision-shaping questions without claiming undiscovered project facts
depends_on:
  hard: []
  soft:
    - grill-with-docs when engineering/project context, domain language, docs, standards, ADRs, code behavior, tests, schemas, or source evidence matter
    - write-a-prd when the user wants the clarified topic turned into a scoped PRD
    - prototype when the user wants to resolve a specific unknown through a disposable experiment
  fallback: If companion skills are unavailable, continue the lightweight interview and clearly label unsourced assumptions.
adapters:
  codex: usable
  claude-code: usable
  hermes: usable
  opencode: usable
  generic-agent: usable
---

# Grill Me

## Purpose

Clarify a user-supplied topic by interviewing the user relentlessly but usefully, one question at a time.

Use this skill for general productivity conversations: brainstorming, exploring a question, sharpening an idea, pressure-testing a lightweight plan, or walking through a decision. The grill should expose assumptions, force crisp tradeoffs, and help the user decide the next move without pretending to know project facts.

Use `grill-with-docs` instead when engineering/project context matters, including target-project docs, domain language, standards, ADRs, code behavior, tests, schemas, or other source evidence.

## Inputs

- User's topic, idea, question, brainstorming notes, lightweight plan, workflow thought, or decision.
- Conversation context the user wants treated as in scope.
- Constraints the user states directly, such as audience, deadline, appetite for risk, budget, rollout needs, or preferred tone.
- Any user-provided note or excerpt that does not require broader project discovery.

## Workflow

1. Route the grill:
   - Use `grill-me` when the needed context is the conversation, user-provided notes, and general reasoning.
   - Use `grill-with-docs` when project artifacts or engineering reality matter, including target-project docs, domain language, documented standards, ADRs, code behavior, tests, schemas, or source-grounded implementation facts.
   - If the topic starts general but a question depends on project reality, pause and recommend `grill-with-docs` rather than guessing.
   - If the user explicitly wants to proceed without project discovery, continue but label project-specific claims as assumptions.

2. Establish the first framing:
   - Restate the topic and central question in one sentence.
   - Identify the broad interview shape: desired outcome, audience or beneficiary, assumptions, options, constraints, tradeoffs, success criteria, risks, and next move.
   - Pick the highest-upstream unresolved question first.
   - Do not dump the whole question list unless the user explicitly asks for a questionnaire.

3. Ask one decision-shaping question at a time:
   - Ask exactly one focused question, then wait for the user's answer.
   - Include a recommended default in every question.
   - Explain the key tradeoff behind the recommendation without inventing undiscovered project facts.
   - Prefer choices, boundaries, priorities, scenarios, and definitions over vague "tell me more" prompts.
   - When the user uses a fuzzy term, propose a precise meaning and ask them to confirm or correct it.

4. Pressure-test the topic in dependency order:
   - Resolve upstream questions before dependent details.
   - Use concrete scenarios to test assumptions, edge cases, failure states, audience fit, timing, reversibility, opportunity cost, and success measures.
   - Challenge contradictions in the user's stated goals, constraints, preferences, or answers.
   - For brainstorming, keep narrowing options until the user has a stronger direction or a clear reason to keep exploring.

5. Keep a running brief:
   - Track the clarified topic, central question, decisions or provisional conclusions, assumptions, unresolved questions, and recommended next action as the conversation progresses.
   - Separate confirmed user decisions from agent recommendations.
   - Keep assumptions explicit when they are based only on conversation context.
   - Do not write durable docs, PRDs, issues, prototypes, or implementation files unless the user asks for that next step.

6. Stop at shared understanding:
   - Stop when the topic is resolved enough for the next action, or when a remaining blocker needs another stakeholder, more reflection, or project evidence.
   - Recommend the next direct action or companion skill, such as continuing the brainstorm, making a choice, writing a PRD, prototyping, implementing, or switching to `grill-with-docs`.
   - If the user chooses to proceed with known ambiguity, name the residual risk clearly.

## Output Contract

During the grill, keep the conversation one-question-at-a-time. Each question should use this shape:

```markdown
My recommended default: <one sentence>.
Tradeoff: <why this default is useful, and what it costs>.
Question: <one focused decision question>
```

After enough decisions are resolved, return a compact working brief:

```markdown
## Clarified Topic

- Topic: <one sentence>
- Central question or goal: <one sentence>
- Success criteria: <observable outcomes>
- Constraints: <known constraints or "none stated">
- Non-goals: <excluded areas>

## Key Tradeoffs

| Tradeoff | Recommendation | Cost |
| --- | --- | --- |

## Decisions

| Decision | Outcome | Rationale or tradeoff |
| --- | --- | --- |

## Assumptions

- <assumption confirmed by the user, provisionally accepted, or explicitly still uncertain>

## Unresolved Questions

| Question | Owner | Needed before |
| --- | --- | --- |

## Recommended Next Action

- <direct next step or companion skill>
```

If `grill-with-docs` is the better fit, say why and name the artifacts or project facts that would change the quality of the answer.

## Delegation

The main agent owns the interview, decision ordering, recommendations, final synthesis, and user communication.

When subagents are available, use them only for bounded, non-project-fact work that can run independently, such as:

- generating alternative decision-tree branches from the user's provided topic;
- stress-testing a stated assumption with hypothetical scenarios;
- comparing two user-provided options at a high level;
- summarizing a provided excerpt without broad project discovery.

Require every subagent result to include:

- inputs inspected;
- assumptions made;
- tradeoffs or risks found;
- candidate questions, not direct user-facing conclusions.

If subagents are unavailable, perform the same reasoning sequentially. Do not use subagents to inspect project docs, code, tests, standards, schemas, or ADRs for this skill; route that need to `grill-with-docs`.

## Guardrails

- Ask one decision-shaping question at a time and wait for the user's answer.
- Prefer `grill-with-docs` when project artifacts, engineering constraints, source evidence, standards, ADRs, code behavior, tests, schemas, or target-project terminology matter.
- Do not pretend to know undiscovered project facts.
- Do not ask broad bundles of questions unless the user explicitly asks for a questionnaire.
- Do not turn lightweight alignment into a full PRD, issue breakdown, prototype, or implementation session unless the user asks for that next step.
- Do not treat agent recommendations as user decisions; confirm or label them as recommendations.
- Do not include private notes, credentials, client data, sensitive personal context, or ignored scratch content in any output.
- Prefer concrete scenarios, observable success criteria, and named tradeoffs over abstract brainstorming.

## References

No external references are required. This skill is self-contained after installation.
