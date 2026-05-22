# Root-Cause Tracing

Read this when the visible symptom appears downstream from the bad value, event, state, caller, or timing condition that actually caused it.

The goal is to trace the first moment reality diverged from expectation. Do not stop at the function that crashed, the log that looked suspicious, or the layer where the symptom became visible.

## Trace Direction

Start at the confirmed symptom and move backward:

1. Name the final bad observation: wrong output, exception, missing record, bad render, timeout, slow query, duplicate event, or corrupted state.
2. Identify the immediate input, state, dependency response, or timing condition that made that observation possible.
3. Ask where that input or state came from.
4. Repeat until you find the first boundary where expected and actual behavior diverge.
5. Confirm the trigger by changing the input, state, order, config, version, or dependency response and watching the symptom change predictably.

If you cannot make the symptom change predictably, you have a lead, not root-cause proof.

## Boundary Questions

At each boundary, compare expectation to reality:

- What did the caller promise or assume?
- What did the callee actually receive?
- What invariant should have been true here?
- Was the value already bad before this boundary, or did it become bad inside it?
- Did timing, ordering, retries, cache state, or async readiness affect the boundary?
- Did configuration, feature flags, environment, version skew, permissions, or schema shape differ from the expected path?
- Is a working example crossing the same boundary differently?

Prefer evidence that narrows the search space. A good probe says "the value is already wrong before this call" or "the value becomes wrong inside this parser." A weak probe adds noise without deciding direction.

## Instrumentation Rules

- Instrument the nearest boundary that can split the search space.
- Log or assert one meaningful fact at a time: input shape, state transition, dependency response, ordering, duration, query plan, cache key, or selected branch.
- Use unique temporary tags so cleanup can find every diagnostic line.
- Redact secrets and sensitive data before recording or sharing values.
- Remove instrumentation once it has served its purpose, unless it becomes an intentional production diagnostic with ownership and controls.

When a probe falsifies a hypothesis, update the trace map instead of defending the old story.

## Common Trace Patterns

**Bad value appears late**

Trace the value backward through transformations, serializers, validators, adapters, queues, caches, persistence, and user input until you find the first incorrect representation.

**Missing or duplicated side effect**

Trace idempotency keys, retries, transaction boundaries, queue acknowledgements, event handlers, subscriptions, and error swallowing. Confirm whether the side effect was never requested, requested twice, requested but rolled back, or requested and hidden by stale reads.

**Wrong branch or config**

Trace feature flags, environment variables, dependency injection, build-time constants, per-tenant settings, permissions, and version skew. Confirm the selected branch at runtime instead of relying on file names or defaults.

**Works in one path but not another**

Compare the smallest working and failing examples. Diff inputs, ordering, environment, config, versions, auth, data shape, dependency responses, and runtime path.

**Failure after recent change**

Use recent changes as suspects, not proof. Bisect, revert in a disposable branch or harness when safe, or compare behavior before and after the change. Do not treat correlation as cause until the symptom moves with the change.

**Performance regression**

Trace cost backward from the slow observation: wall time, CPU, allocation, network, disk, database, lock contention, fanout, retry count, query plan, cache misses, or payload size. A performance cause must explain the measured cost, not merely look inefficient.

## Evidence Packet

Capture the trace in a form another agent can continue:

```markdown
## Root-Cause Trace

- Final symptom: <bad observation>
- First known bad point: <path, function, call, query, event, or boundary>
- Last known good point: <upstream point where expectation still held>
- Divergence: <what changed from expected to actual>
- Trigger: <input, state, timing, config, dependency, or change that causes it>
- Confirming probe: <command, instrumentation, comparison, profile, or query plan>
- Falsified leads: <important rejected hypotheses>
- Residual uncertainty: <what remains unproved>
```

## Stop Rules

Stop and reroute when:

- the trace requires private internals for any possible regression proof;
- instrumentation would expose sensitive production data;
- the failure cannot be reproduced and the available artifact is too weak for a root-cause claim;
- two or more plausible causes remain and no safe probe can distinguish them;
- the same area has received repeated failed fixes without a clear public-interface seam.

Use `tdd` when the cause and regression behavior are known. Use `improve-codebase-architecture` when the system shape prevents honest proof.
