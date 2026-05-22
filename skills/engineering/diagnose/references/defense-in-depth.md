# Defense In Depth

Read this after root cause is proven and the likely fix needs layered prevention, containment, detection, or recovery.

This reference does not move `diagnose` into implementation ownership. Use it to shape the evidence packet and the recommended fix strategy, then route actual code changes and regression proof through `tdd`.

## Purpose

A single local fix may remove the observed symptom but still leave the system easy to break again. Defense in depth asks which layers should prevent the same invalid state, unsafe input, incorrect assumption, or expensive path from reaching the symptom point again.

Use this especially when the root cause involves:

- invalid input crossing multiple modules;
- missing authorization, permission, tenant, or ownership checks;
- partial validation at only one entrypoint;
- unsafe defaults, stale config, or version skew;
- retries, duplicate events, or non-idempotent side effects;
- performance work where one layer can cap cost while another removes the underlying waste;
- data corruption, schema drift, migrations, or backward compatibility.

## Layer Choices

Consider layers in this order, then recommend the smallest set that materially reduces recurrence.

**Prevent**

Reject invalid inputs, impossible states, unsafe combinations, unauthorized actions, or unsupported versions at the earliest honest interface.

**Normalize**

Convert equivalent inputs to one canonical shape before the rest of the system branches on them.

**Constrain**

Use types, schemas, database constraints, invariants, feature-flag rules, rate limits, idempotency keys, or bounded queues to make invalid states harder to represent.

**Contain**

Keep failure local with transactions, rollback, compensation, circuit breakers, dependency isolation, per-tenant scoping, cancellation, or bounded resource use.

**Detect**

Add useful errors, metrics, tracing, alerts, audit logs, or debug hooks that expose recurrence without leaking secrets or flooding operators.

**Recover**

Define safe retry, backoff, repair, reconciliation, fallback, or user-visible recovery behavior when prevention cannot be perfect.

## Choosing The Right Layers

Do not recommend every possible layer. Pick the layers that match the proven cause:

- If an entrypoint accepted invalid input, prevention belongs near that public interface.
- If callers repeatedly perform the same fragile choreography, a deeper module may need to own it.
- If a dependency returns transient failures, containment and recovery may matter more than input validation.
- If a race creates duplicate side effects, idempotency and transaction boundaries may matter more than retry count.
- If a query plan regressed, measurement-backed query or index work matters more than generic caching.
- If tests can only prove the fix through internals, record architecture follow-up before forcing a brittle regression test.

## Handoff To TDD

When routing to `tdd`, include:

```markdown
## Defense-In-Depth Recommendation

- Proven root cause: <cause and evidence>
- Primary regression behavior: <observable behavior that should fail before the fix>
- Suggested public test surface: <API, CLI, route, UI flow, service, module interface, or missing seam>
- Required prevention layer: <earliest honest layer>
- Additional layer, if needed: <containment, detection, recovery, or none>
- Security or data sensitivity: <trust boundary, secret, tenant, permission, persistence, or none>
- Architecture concern: <no correct seam, repeated choreography, false seam, or none>
- Residual risk: <what the layered strategy still does not cover>
```

If the suggested public test surface is awkward, wide, private, or fake, route to `improve-codebase-architecture` before implementation.

## Anti-Patterns

- Adding validation only where the crash happened even though bad data entered earlier.
- Adding a broad catch or retry that hides the symptom but preserves the invalid state.
- Adding logging that includes secrets, raw production payloads, or sensitive identifiers.
- Adding a new abstraction solely for tests when no real behavior varies across the seam.
- Treating defense in depth as a mandate for broad rewrite instead of a focused prevention strategy.
- Adding caching for performance before measuring where time or cost is spent.
- Shipping a fix without a regression path when a correct public-interface seam exists.
