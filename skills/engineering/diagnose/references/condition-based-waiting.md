# Condition-Based Waiting

Read this when diagnosing flakes, async behavior, timing races, readiness, retries, polling, arbitrary sleeps, timeouts, eventual consistency, or intermittent failures.

A fixed sleep is usually a guess. It may hide the failure on one machine while preserving the race everywhere else. Prefer waiting for the condition that proves the system is ready.

## First Diagnose The Flake

Before changing waits:

1. Confirm the failure is intermittent and record the failure rate over repeated runs when safe.
2. Capture the exact missing condition: element visible, file written, event processed, job drained, subscription connected, cache invalidated, lock released, transaction committed, server listening, or metric updated.
3. Identify whether the test or code proceeds before readiness, waits for the wrong signal, swallows a failure, or depends on global state from another test.
4. Add targeted instrumentation around ordering and readiness, not broad delay.
5. Prove the condition is the gate by observing that failures occur when the action runs before the condition is true.

If the failure is not timing-related, do not "fix" it with waiting.

## Replace Time With Signals

Prefer these signals over sleeps:

- a public API response that confirms state;
- a visible UI condition that a user would rely on;
- a queue, job, or event-drain signal;
- a database or repository read through a public interface;
- an explicit lifecycle event such as server ready, connection open, subscription active, transaction committed, or worker idle;
- a bounded polling loop that checks one observable condition and fails with useful diagnostics.

A good wait names the condition. A weak wait names a duration.

## Bounded Polling Shape

Use this generic shape when a native framework helper is unavailable:

```text
deadline = now + timeout
last_observation = none

while now < deadline:
  observation = read_observable_condition()
  if condition_is_met(observation):
    return observation
  remember observation for failure message
  wait a small interval

fail with:
  expected condition
  last observation
  timeout
  relevant environment or command
```

The failure message matters. A timeout that says "waited 10 seconds" is weak. A timeout that says "expected job abc to finish; last state was retrying with error X" is useful.

## Polluter And Order Failures

When a flake depends on test order or prior state:

- run the failing test alone, then with the file, then with neighboring suites;
- randomize or vary order if the framework supports it;
- bisect the preceding tests or setup steps that make the failure appear;
- inspect shared global state, singleton caches, ports, temp directories, database rows, clocks, feature flags, env vars, and mocked dependencies;
- confirm cleanup runs even on failure.

The polluter is proven when adding or removing the suspect setup makes the victim fail or pass predictably.

## Runtime Code Versus Test Code

In test code, waits should express user-visible or public-interface readiness. Do not reach into private internals just to make a test deterministic unless there is no correct public seam and architecture work is being recorded.

In production code, retries, polling, and timeouts need a product reason:

- What condition is transient?
- What maximum delay is acceptable to the user or caller?
- What happens after timeout?
- How is cancellation handled?
- How are failures logged without leaking secrets?
- Is this containing an external dependency, or hiding an owned-code race that should be fixed?

Route production changes through `tdd` once the root cause is proven.

## Anti-Patterns

- Adding `sleep(1000)` because the failure "needs more time."
- Increasing timeouts repeatedly without measuring the actual readiness time.
- Waiting for a proxy signal, such as any network response, when the needed state is different.
- Retrying an assertion that should be deterministic after setup.
- Swallowing errors inside the wait loop.
- Leaving flake instrumentation or debug logs in place after diagnosis.
- Treating a lower failure rate as proof of a fix.

## Evidence Packet

```markdown
## Flake Diagnosis

- Failure rate: <runs, command, failures>
- Missing condition: <readiness signal that was false too early>
- Ordering evidence: <logs, trace, timestamps, repeated runs, polluter bisection>
- Replacement wait: <condition-based wait or routed TDD fix>
- Timeout behavior: <diagnostic failure message and limit>
- Cleanup: <instrumentation removed or retained intentionally>
- Residual risk: <remaining nondeterminism or skipped stress runs>
```
