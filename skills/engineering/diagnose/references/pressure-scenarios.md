# Pressure Scenarios

Read this when urgency, fatigue, authority, repeated failed fixes, or "quick fix" pressure could weaken diagnosis discipline.

Pressure does not make evidence optional. It makes evidence more valuable because it protects the user from confident wrong fixes.

## Common Pressure Traps

| Pressure | Tempting rationalization | Better response |
| --- | --- | --- |
| Production is broken | "We do not have time to reproduce it." | Build the safest available feedback loop: log artifact, read-only query, trace, feature flag check, rollback comparison, or approved minimal repro. State confidence honestly. |
| A senior person named the cause | "They probably know, so I can skip proof." | Treat it as hypothesis rank 1. Confirm with the smallest probe before changing behavior. |
| The fix looks obvious | "This one-line guard will solve it." | State the prediction, prove the current failure path hits it, then route implementation through `tdd` if a seam exists. |
| A previous fix failed | "Try the next likely fix." | Stop. Rebuild the hypothesis list, identify what the failed fix falsified, and trace backward from the still-confirmed symptom. |
| The test is flaky | "Just increase the timeout." | Identify the readiness condition, polluter, race, or global state leak. Read condition-based waiting. |
| The profile looks noisy | "Optimize the code that looks ugly." | Measure baseline and compare costs. Optimize only where the measured bottleneck explains the symptom. |
| The setup is hard to test | "Use private internals for now." | Record the missing public seam and route architecture follow-up when no honest regression surface exists. |
| The user wants speed | "A probably-correct answer is enough." | Offer the fastest honest diagnosis path and make any lower-confidence claim explicit. |

## Stop And Reset Signals

Pause the fix impulse when any of these appear:

- more than one attempted fix has failed;
- the local repro does not match the user report;
- evidence is mostly "I think" or "it feels like";
- instrumentation and code changes are mixed in the same step;
- a timeout was increased without knowing the readiness condition;
- performance work starts before a baseline measurement;
- a test must reach private internals to prove behavior;
- debug logs or temporary scripts are accumulating;
- the same explanation survives every falsifying probe by changing shape.

When a stop signal appears, write the current state in plain language:

```markdown
## Diagnosis Reset

- Confirmed symptom:
- What we know:
- What we do not know:
- Fixes or probes already tried:
- What each result falsified:
- Current top 3 hypotheses:
- Next cheapest safe probe:
- Cleanup needed:
```

## Pressure-Resistant Diagnosis Checklist

Before routing to implementation, confirm:

- The feedback loop shows the exact symptom or a clearly bounded proxy.
- Expected and actual behavior are both stated.
- At least three plausible hypotheses were considered unless evidence made the cause singular.
- The winning hypothesis made a prediction before the confirming probe.
- Important rejected hypotheses are recorded.
- Temporary instrumentation has a cleanup plan.
- Performance claims have measurement.
- Flaky behavior uses a condition, not a guessed delay.
- The next action is routed to `tdd`, `improve-codebase-architecture`, `verification-before-completion`, `handoff`, or a user decision.

## Evaluation Scenarios

Use these scenarios to pressure-test whether an agent is following the skill:

1. A failing production report includes a stack trace and a manager says the null check is obvious. The agent should prove the null entered at that path and avoid fixing before evidence.
2. A browser test fails one in ten runs. The agent should measure failure rate, find the readiness condition or polluter, and reject arbitrary sleep as proof.
3. A page became slow after a deploy. The agent should gather a baseline, compare before and after, inspect profiles or query plans, and avoid cosmetic optimization.
4. A bug is reproducible only through awkward internal setup. The agent should record no correct public seam and route architecture follow-up instead of writing a brittle regression test.

These scenarios are for review and training. They are not runtime dependencies.
