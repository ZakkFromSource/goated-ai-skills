---
name: diagnose
description: Use when investigating bugs, failing behavior, flaky tests, build failures, integration failures, performance regressions, or unexpected behavior before proposing or implementing fixes.
metadata:
  goated-category: engineering
---

# Diagnose

## Purpose

Find and prove the cause of a bug, flaky failure, build or integration break, production symptom, or performance regression before fixing it.

Diagnosis ends with evidence and a routed next action. It does not own the fix cycle. When the cause and correct public-interface seam are known, route implementation and regression proof to `tdd`. When no correct seam exists, tests require private access, or repeated fixes keep failing, route the architecture problem to `improve-codebase-architecture`.

## Inputs

- User report, issue, failing test, error output, logs, traces, metrics, screenshots, profiles, benchmark results, reproduction steps, or observed symptoms.
- Target-project root, relevant docs, recent changes, configs, dependency versions, environment facts, and affected entrypoints.
- Known safety constraints, including production access, customer or user data, destructive repro risk, secret handling, time limits, and whether instrumentation may be left running.
- Available proof tools: tests, CLI commands, HTTP scripts, browser automation, fixtures, traces, profilers, query plans, log search, feature flags, bisection, or human-in-the-loop checks.

## Dependencies

Hard: None.

Soft:
- session-start-progressive-disclosure for unfamiliar target projects
- grill-with-docs when reported vs expected behavior, scope, risk, or user impact is unclear
- tdd when proven cause and fix/regression proof can use a public-interface seam
- improve-codebase-architecture when no correct seam, false seams, failed fixes, or testability friction appear
- code-security-review when symptoms touch trust boundaries, auth, permissions, secrets, user data, persistence, execution, or unsafe config
- doc-sync when diagnosis changes behavior docs, runbooks, architecture docs, or test guidance
- verification-before-completion before proven-cause, complete, fixed, passing, or implementation-ready claims
- handoff when repro, root cause, uncertainty, or blocked verification needs continuity

Fallback: If companion skills, docs, commands, profilers, production access, or subagents are unavailable, build/request the smallest safe feedback loop, state missing evidence, downgrade claims, and report residual risk.

## Workflow

1. Triage scope and safety:
   - Classify the symptom: functional bug, flaky or timing failure, performance regression, build failure, integration failure, production symptom, or unknown.
   - Identify the blast radius, data sensitivity, environment, urgency, and whether reproduction or instrumentation could be destructive.
   - Do not run destructive repro steps, mutate production, add production instrumentation, or expose secrets without explicit approval and a rollback or cleanup plan.
   - Ask only for non-discoverable facts that materially change diagnosis: expected behavior, missing access, unsafe repro approval, or the user's tolerance for risk.

2. Build the fastest honest feedback loop:
   - Before hypothesis testing, establish or request the smallest loop that can show the symptom with enough fidelity.
   - Prefer a focused failing test, exact command, CLI fixture, HTTP request script, browser path, captured trace replay, benchmark, profiler run, query plan, differential comparison, bisection, or human-in-the-loop loop.
   - If the loop is slow, make it narrower before continuing. If no loop is safe or available, stop before full hypothesis testing, request the missing loop or access, and limit any artifact-only diagnosis to explicitly lower-confidence triage.
   - Capture the loop as evidence: command or steps, inputs, environment, observed result, timing, and whether the result is deterministic or intermittent.

3. Confirm the exact symptom:
   - Reproduce the reported failure or verify the provided artifact. Match the user-visible symptom, error, timing, environment, and frequency.
   - If the local symptom differs from the report, diagnose the mismatch first instead of drifting into a different bug.
   - Record expected behavior separately from actual behavior. Treat ambiguous expected behavior as a product or user decision, not a debugging fact.

4. Observe before fixing:
   - Read errors, stack traces, logs, recent changes, callers, tests, configs, schemas, dependency wiring, and working examples before proposing a fix.
   - Compare expectations to reality at each relevant interface: inputs, state, side effects, timing, outputs, errors, and invariants.
   - Read [Root-Cause Tracing](references/root-cause-tracing.md) when the bad value, event, state, or timing appears downstream from its origin.
   - Do not edit production behavior, weaken tests, broaden retries, or add speculative guards during observation.

5. Rank falsifiable hypotheses:
   - List 3-5 plausible causes, ordered by evidence, impact, and cheapest falsifying probe.
   - For each hypothesis, state the prediction that would be true if it were the cause and the smallest probe that can confirm or falsify it.
   - Keep "obvious fix" ideas as hypotheses until evidence proves them.
   - If pressure, fatigue, authority, or sunk cost is pushing a shortcut, read [Pressure Scenarios](references/pressure-scenarios.md).

6. Probe one hypothesis at a time:
   - Add the narrowest instrumentation, command, log, assertion, trace, breakpoint, metric, profile, query plan, or comparison needed for one prediction.
   - Change one variable at a time. After each probe, record the result, update the ranking, and remove or tag temporary instrumentation for cleanup.
   - For flaky or async symptoms, read [Condition-Based Waiting](references/condition-based-waiting.md) before changing waits, retries, sleeps, polling, or timeouts.
   - For performance symptoms, measure the baseline first, then use profiling, query plans, benchmarks, bisection, allocation or I/O measurement, or differential traces before proposing optimization.

7. Prove root cause and route the next action:
   - Root cause is proven only when evidence explains the exact symptom and the symptom changes predictably when the cause or triggering condition changes.
   - Build a compact evidence packet: repro loop, key observations, hypotheses rejected, confirming probe, cause, affected interface, and residual uncertainty.
   - If a correct public-interface seam exists, route to `tdd` with the desired regression behavior and suggested first failing test.
   - If no correct seam exists, tests would need private internals, setup is pathological, or repeated fixes failed, route to `improve-codebase-architecture` before implementation.
   - If the diagnosis changes docs or runbooks, route to `doc-sync`. If it touches trust boundaries or sensitive data, route to `code-security-review`.

8. Cleanup and verify closeout:
   - Remove debug logs, temporary scripts, local harnesses, probes, flags, breakpoints, test-only hooks, scratch files, and instrumentation that should not remain.
   - If any diagnostic artifact must remain, document why, who owns it, how it is controlled, and when to remove it.
   - Use `verification-before-completion` before claiming the cause is proven, diagnosis is complete, the fix is ready, or the work is safe to hand to implementation.
   - Report residual risk plainly: unreproduced paths, environment differences, skipped probes, unavailable access, weak measurement, flaky evidence, or unverified assumptions.

## Output Contract

Return a diagnosis packet shaped like this:

```markdown
## Diagnosis Scope

- Symptom: <reported and confirmed symptom>
- Safety constraints: <production, data, destructive repro, secret, or access constraints>
- Feedback loop: <command, test, script, benchmark, trace, manual loop, or missing loop>

## Repro Evidence

- Expected: <expected behavior>
- Actual: <actual behavior>
- Frequency and environment: <deterministic/intermittent, versions, inputs, timing>
- Evidence: <logs, command output, profile, trace, screenshot, metrics, or source reads>

## Hypotheses And Probes

| Rank | Hypothesis | Prediction | Probe | Result |
| --- | --- | --- | --- | --- |
| 1 | <cause candidate> | <what would be observed> | <instrumentation or command> | <confirmed/falsified/pending> |

## Root-Cause Result

- Cause: <proven cause, not proven, or still uncertain>
- Proof: <evidence that ties cause to exact symptom>
- Rejected causes: <important falsified hypotheses>
- Performance evidence: <baseline, profile, benchmark, query plan, bisection, or not applicable>
- Cleanup: <removed artifacts or remaining controlled artifacts>
- Routed next action: <tdd, improve-codebase-architecture, verification-before-completion, handoff, or user decision>
- Residual risk: <remaining uncertainty>
```

## Delegation

Main owns symptom framing, hypothesis discipline, root-cause judgment, fix direction, and user communication.

Delegate only bounded diagnosis/review work: reproduce separately, trace one subsystem/caller/data/dependency path, compare working vs failing examples, gather profiles/query plans/benchmarks/bisection evidence, review hypotheses for gaps, or verify cleanup and public-boundary safety.

Require `Status`: `DONE`, `DONE_WITH_CONCERNS`, `NEEDS_CONTEXT`, or `BLOCKED`; paths/commands inspected; evidence gathered; assumptions, skipped checks, residual risk, and confidence. The main agent sanity-checks important delegated evidence before relying on it.

Status handling: `DONE` integrates inspected evidence; `DONE_WITH_CONCERNS` requires concern review before trust; `NEEDS_CONTEXT` gets the missing symptom, path, command, artifact, access, or expected behavior before re-dispatch or local continuation; `BLOCKED` narrows the diagnosis, chooses a safer loop, asks for approval, or hands off residual risk.

If subagents are unavailable, run the same steps sequentially with a narrower context budget.

## Guardrails

- Do not fix before proving the cause. A likely fix is still a hypothesis.
- Do not bundle probes with fixes; evidence becomes muddy when the variable changes with the treatment.
- Do not weaken, delete, or rewrite failing tests just to make the symptom disappear.
- Do not log secrets, tokens, credentials, private user data, raw production payloads, or sensitive identifiers. Redact before sharing or persisting evidence.
- Do not add production instrumentation, enable verbose logs, alter live config, or run destructive repro steps without explicit approval, scope, duration, and rollback.
- Do not use arbitrary sleeps as the default flake fix. Prefer observed readiness conditions, bounded polling, deterministic synchronization, or root-cause proof.
- Do not claim a performance fix path without baseline measurement and relevant profiling, query-plan, benchmark, bisection, or equivalent evidence.
- Do not leave behind debug tags, temporary scripts, local harnesses, scratch artifacts, breakpoints, ad hoc flags, or diagnostic logs without documenting ownership and cleanup.
- Do not force a regression test through the wrong seam. If the only available proof reaches into private internals or brittle implementation details, route architecture follow-up first.
- Do not require this source repo, upstream repos, issue files, hidden chat history, ignored scratch folders, or maintainer-only docs after the skill is installed.

## References

Workflow-gated support files: [Root-Cause Tracing](references/root-cause-tracing.md), [Condition-Based Waiting](references/condition-based-waiting.md), and [Pressure Scenarios](references/pressure-scenarios.md).

- [Defense In Depth](references/defense-in-depth.md) - read after root cause is proven and the likely fix needs layered prevention, containment, detection, or recovery; route implementation through `tdd`.
