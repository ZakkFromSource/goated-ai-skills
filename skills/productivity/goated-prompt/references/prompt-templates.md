# Prompt Templates

Use these as starting shapes. Adapt them to the user request; do not paste placeholders that the receiving agent cannot resolve.

## Spec/Build Prompt

```text
You are working in <project/context>. Ingest this specification and implement the ordered tasks.

High-Level Objective
<One sentence naming what is being built and why.>

Mid-Level Objectives
- <Measurable milestone>
- <Measurable milestone>
- <Measurable milestone>

Implementation Notes
- <Stack, libraries, constraints, standards, or architecture decisions>
- <What to preserve or avoid>
- <How to handle edge cases or uncertainty>

Context
Beginning context:
- <Known files, current behavior, current state, or source evidence>

Ending context:
- <Expected files, behavior, docs, tests, or user-visible state>

Low-Level Tasks
1. <ACTION> <DETAIL target> in <location>.
   Detail: <specific behavior, acceptance criteria, and verification>
2. <ACTION> <DETAIL target> in <location>.
   Detail: <specific behavior, acceptance criteria, and verification>

Verification
- <Commands, manual checks, or evidence expected>
- <What to report when complete>
```

## Focused Task Prompt

```text
In <location>, <ACTION> the <DETAIL target> so that <observable outcome>.

Context:
- <Relevant current behavior or pattern to mirror>

Constraints:
- <What must not change>
- <Privacy, safety, compatibility, or style requirement>

Acceptance criteria:
- <Observable condition>
- <Observable condition>

Verification:
- <Test, command, review, or manual check>

Report:
- <Changed files or artifact>
- <Verification result>
- <Assumptions or skipped checks>
```

## Planning/Design Prompt

```text
Analyze <decision/problem> and recommend a plan.

Goal:
<Desired outcome in user or maintainer terms.>

Context:
- <Known project, audience, constraints, evidence, or uncertainty>

Decision criteria:
- <Criterion>
- <Criterion>
- <Criterion>

Output:
- Recommended direction
- Alternatives considered
- Tradeoffs and risks
- Assumptions and missing evidence
- Next action or GOATED skill route when relevant

Do not implement changes. Do not invent project facts that are not provided.
```

## Iterative/Refinement Prompt

```text
Refine the current output using the TCREI loop.

Task:
<What needs to improve or change.>

Context:
<Current state, original goal, constraints, and known issues.>

References:
- <Existing output, pattern, source, or example to preserve or mirror>

Evaluate:
- <Success criteria>
- <Failure modes to avoid>

Iterate:
- Produce the revised output.
- Explain the material changes briefly.
- List assumptions, unresolved questions, and what to adjust if the next pass misses.
```

## General Prompt

```text
Complete this task: <clear task>.

Context:
- <Relevant background>

Constraints:
- <Audience, tone, length, sources, privacy, or format constraints>

Output format:
- <Sections, bullets, table, code block, or artifact shape>

Quality bar:
- <What a useful answer must include>
- <What to avoid>

If critical context is missing, ask one focused question. Otherwise proceed with explicit assumptions.
```

## GOATED Prompt Wrapper

Use this wrapper when the receiving agent has GOATED AI Skills installed:

```text
Use GOATED AI Skills for this request.

Likely route:
- Start with `<skill>` because <reason>.
- Route to `<next skill>` if <condition>.

Task:
<Optimized prompt body.>

Context to inspect first:
- <Project docs, issue, source area, or "conversation context only">

Success criteria:
- <Observable outcomes>

Report:
- <Expected closeout shape, assumptions, skipped checks, and verification evidence>
```

