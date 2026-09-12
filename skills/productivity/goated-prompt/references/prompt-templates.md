# Prompt Templates

## Contents

- [Spec/Build Prompt](#specbuild-prompt)
- [Focused Task Prompt](#focused-task-prompt)
- [Planning/Design Prompt](#planningdesign-prompt)
- [Iterative/Refinement Prompt](#iterativerefinement-prompt)
- [General Prompt](#general-prompt)
- [GOATED Prompt Wrapper](#goated-prompt-wrapper)

Use only the shape that helps the request. Omit empty fields and unresolved
placeholders. Add implementation steps only when their order is required or
already agreed; otherwise let the receiving agent choose the method.

## Spec/Build Prompt

```text
In <project/context>, implement <observable product outcome and purpose>.

Relevant context:
- <Current behavior, source locations, and decisions already settled>

Constraints:
- <Required compatibility, architecture, privacy, or operational boundaries>

Acceptance:
- <Observable conditions that define the finished result>

Verification:
- <Required checks and evidence for acceptance>

Scope and completion:
- <Authorized actions and any explicit approval or review checkpoint>
- Continue through implementation, relevant verification, and fixes caused by
  this change. Report the result and any unresolved limitations.
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

Completion:
- <Authorized endpoint, including checks and related fixes for implementation;
  preserve review-only scope or a requested checkpoint>

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
Improve <current output> so that <observable improvement>.

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

Route guidance, only if needed:
- Start with `<skill>` because <reason>.
- Route to `<next skill>` if <condition>.

Task:
<Optimized prompt body.>

Relevant context:
- <Evidence pointers with the condition under which each is needed>

Success criteria:
- <Observable outcomes>

Report:
- <Expected closeout shape, assumptions, skipped checks, and verification evidence>
```
