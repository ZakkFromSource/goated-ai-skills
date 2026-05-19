# Deep Modules

Read this reference when a test is hard to write because the public interface is too wide, setup is noisy, behavior leaks across modules, or callers must know too much about the implementation.

Deep-module thinking is part of the GOATED engineering philosophy: prefer modules with small, meaningful interfaces that hide substantial behavior. TDD makes this visible because awkward tests often reveal awkward interfaces.

## Deep Versus Shallow

A deep module has a small interface and a rich implementation behind it:

```text
+-----------------------+
| Small interface       |
| few methods, simple   |
| params, clear result  |
+-----------------------+
|                       |
| Deep implementation   |
| complex behavior      |
| hidden behind the API |
|                       |
+-----------------------+
```

A shallow module has a large interface and little implementation:

```text
+-----------------------------------+
| Large interface                   |
| many methods, complex params,     |
| caller must know many details     |
+-----------------------------------+
| Thin implementation               |
| mostly passes complexity through  |
+-----------------------------------+
```

Shallow modules make tests noisy because every caller has to understand the details the module failed to hide.

## Why TDD Cares

Tests are callers. If a behavior test requires a large pile of setup, internal patching, call-order assertions, or knowledge of private sequencing, that is design evidence.

Ask:

- Can the public interface expose the behavior in fewer calls?
- Can parameters be simplified into a value object or clearer command?
- Can the module return a result instead of forcing callers to inspect side effects?
- Can validation, branching, retries, mapping, or orchestration move behind one interface?
- Can repeated setup become a meaningful domain factory or fixture instead of test-only plumbing?

Do not add abstraction just to make a test easy. Deepen the module only when the new interface hides real complexity and improves both production callers and tests.

## Interface As Test Surface

The public interface is the test surface. A good public interface lets tests ask for behavior directly:

```python
result = planner.schedule(task, due_date)

assert result.status == "scheduled"
assert result.visible_on == due_date
```

A shallow interface forces tests to choreograph internals:

```python
validator.validate(task)
normalizer.normalize(task)
calendar.reserve(task)
notifier.prepare(task)
planner.commit(task)
```

If every caller must perform the choreography, the module may not be deep enough. The behavior might belong behind a smaller interface that owns the sequence.

## Deletion Test

Use the deletion test to judge whether a module earns its place:

- If deleting the module would make its complexity reappear across callers, the module is probably hiding useful behavior.
- If deleting the module would simply remove indirection with no complexity returning, the module may be shallow pass-through.

TDD refactors should prefer the first kind. A module that earns its interface gives tests and callers leverage.

## Deepening During TDD

Deepening usually belongs in the refactor phase, after green. During RED and GREEN, keep attention on the current behavior. Once green, look for interface friction the cycle exposed:

- repeated setup across tests;
- many public methods needed to prove one behavior;
- callers passing primitive clusters that belong together;
- tests patching internals because dependencies are created too deep;
- behavior scattered across modules with no single owner;
- assertions that need private state because no public result exists.

Possible refactors:

- combine shallow modules when they only pass behavior through;
- introduce a value object for repeated primitive clusters;
- move behavior to the module that owns the data;
- return a result object that captures observable outcomes;
- introduce a real seam and adapter for an external dependency;
- replace old implementation-detail tests with public-interface tests once coverage is equivalent.

Keep the test surface stable unless changing the public interface is part of the issue. When the interface must change, update tests to describe the new public contract, not the transitional internals.

If the TDD cycle exposes a broader architecture problem that is larger than the current issue, do not smuggle that refactor into the green phase. Capture the evidence and route follow-up to `improve-codebase-architecture` when that skill exists and is available.

## Deep Module Checklist

Before calling a refactor "deeper", check:

- The public interface got smaller, clearer, or more meaningful.
- The implementation hides complexity that callers previously had to know.
- Tests can prove behavior with less internal knowledge.
- Production callers benefit, not just tests.
- The module has real responsibility, not just a renamed pass-through.
- Existing behavior remains green after each refactor step.
