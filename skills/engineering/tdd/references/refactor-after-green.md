# Refactor After Green

Read this reference after the focused behavior test is green and before non-trivial cleanup, interface reshaping, or module deepening.

## Rule

Never refactor while red. Get to green first.

When a test is red, there are two live questions: "is the behavior implemented?" and "is the design good?" Refactoring while both are unanswered makes failures harder to interpret. Green tests give you a stable floor for improving design.

## What To Look For

After a TDD cycle, look for:

- duplication that hides one concept in several places;
- long methods that mix policy, mapping, orchestration, and side effects;
- shallow modules that mostly pass complexity through;
- feature envy, where logic sits far from the data or concept it uses;
- primitive obsession, where repeated strings, dicts, booleans, or tuples should become a clearer value;
- setup friction in tests that points at a leaky or awkward interface;
- existing code the new behavior reveals as problematic.

Keep tests on the public interface while refactoring. Private helpers can appear or disappear freely if behavior still passes.

## Refactor Moves

Use the smallest move that improves the design:

- extract duplication into a named helper or value only when the name clarifies intent;
- move behavior to the module that owns the concept;
- combine shallow pass-through modules when the split creates more interface than value;
- deepen a module by hiding orchestration or validation behind a smaller public method;
- introduce a real seam for external dependencies;
- return explicit result objects instead of forcing callers to inspect side effects;
- delete obsolete implementation-detail tests after equivalent public-interface coverage exists.

Do not make broad architecture changes just because the tests are green. Refactor in small steps and rerun tests after each meaningful step.

## Interface Friction

Test friction is evidence, not a command. Use judgment.

Friction worth addressing:

- many tests repeat the same awkward setup;
- the public interface requires internal sequencing knowledge;
- callers must pass unrelated primitive clusters together;
- tests need private state to observe outcomes;
- external dependencies are constructed inside logic that should be testable;
- behavior has no obvious owner.

Friction to tolerate for now:

- one isolated ugly setup in legacy code;
- a broad interface that is outside the issue scope;
- a test harness gap that would require new infrastructure;
- a refactor that would change public behavior or create migration work the issue did not ask for.

When deferring friction, name the residual risk in the final output.

## Refactor Evidence

After refactoring, report:

- what changed and why it was safe after green;
- which tests were rerun after each meaningful step;
- whether the public interface changed;
- whether module depth, locality, or test clarity improved;
- what cleanup was deferred because it was outside scope.
