---
name: tdd
category: engineering
classification: portable
status: wip
description: Test-driven development with a behavior-first red-green-refactor loop. Use when building or fixing target-project behavior, changing public interfaces, adding regression coverage, or when the user mentions TDD, red-green-refactor, test-first development, integration tests, or behavior-driven tests.
triggers:
  - user asks to implement a focused issue, feature, behavior change, or bug fix with test-first proof
  - user mentions TDD, red-green-refactor, test-first development, integration tests, behavior tests, or regression tests
  - a target-project change needs observable behavior proof through public interfaces
  - a public interface, module seam, adapter, or user-facing workflow is changing and should be protected by tests
outputs:
  - identified observable behavior, public test surface, and first focused failing test
  - red evidence showing the test fails for the expected reason before implementation
  - green evidence showing the implementation passes the focused test and relevant existing checks
  - per-cycle notes showing one test, one minimal implementation, and no speculative scope
  - refactor notes after green, including interface friction, deep-module opportunities, and tests rerun
  - residual risk, test gaps, skipped checks, and weak or missing test infrastructure fallback notes
depends_on:
  hard: []
  soft:
    - session-start-progressive-disclosure before TDD work in an unfamiliar target project
    - grill-with-docs when behavior, public interface, scope, project language, or testing priority is unclear
    - prd-to-issues when implementing a planned vertical issue slice
    - prototype when a risky behavior or interface needs a disposable experiment before production tests
    - project-standards-calibration when test, fixture, naming, or quality standards affect the implementation
    - standards-and-spec-review after implementation when available
    - code-security-review after implementation when trust boundaries, persistence, auth, or user data are touched
    - doc-sync after behavior, public interface, architecture, or testing docs may have changed
  fallback: If companion skills or project docs are unavailable, inspect the smallest relevant local evidence, use existing tests or commands where discoverable, and state lower confidence plus residual risk.
adapters:
  codex: usable
  claude-code: usable
  hermes: usable
  opencode: usable
  generic-agent: usable
---

# Test-Driven Development

## Purpose

Use behavior-first TDD to implement target-project changes with proof. The loop is red, green, refactor: write one focused failing test for observable behavior, make the smallest production change that passes it, then improve design only after the tests are green.

The core principle is simple: tests should verify behavior through public interfaces, not implementation details. Code can change entirely; tests should keep proving the same capability.

Good tests are integration-style. They exercise real code paths through public APIs, command surfaces, UI flows, service interfaces, or other stable project entrypoints. They describe what the system does, not how it happens internally. A good test reads like a specification: the behavior is clear even if the implementation is replaced later.

Bad tests are coupled to implementation. They mock internal collaborators, test private helpers, assert call order, or verify through external backdoors when a public interface could prove the behavior. The warning sign is a test that fails during a harmless refactor while the behavior still works.

## Inputs

- User request, bug report, issue handoff, PRD slice, prototype verdict, or scoped behavior change.
- Target-project root path.
- Existing source files, tests, fixtures, commands, public interfaces, schemas, routes, adapters, or UI flows related to the behavior.
- Existing project docs, including root `CONTEXT.md` when present, glossary/context files, ADRs, standards, and test conventions when they affect naming, interface shape, or expected proof.
- Available test commands, focused test filters, local development constraints, and known weak or missing test infrastructure.

## Workflow

1. Ground the behavior before writing code:
   - Identify the observable behavior that should change or be protected.
   - Identify the public interface that should prove it, such as a module API, CLI command, HTTP endpoint, UI flow, repository method, service boundary, or user-facing workflow.
   - Identify the first focused failing test that can prove one behavior.
   - Use the project's root `CONTEXT.md`, domain language, glossary, existing test names, and ADRs when available.
   - Proceed automatically when the issue or PRD already makes behavior and interface clear. Ask only when behavior, public interface, or test priorities are materially ambiguous.

2. Plan tests as behaviors, not implementation steps:
   - List behavior candidates in priority order.
   - Choose the first tracer bullet: the smallest end-to-end behavior that proves the path works.
   - Prefer critical paths, regression risks, and complex logic over exhaustive edge-case theater.
   - Read [Test Design](references/test-design.md) when test shape, naming, public-interface proof, or good-vs-bad test judgment matters.
   - Read [Mocking And Seams](references/mocking-and-seams.md) before introducing mocks, fakes, ports, dependency injection, or adapter seams.
   - Read [Deep Modules](references/deep-modules.md) when the interface feels wide, setup-heavy, shallow, or awkward to test.

3. RED: write one focused failing test:
   - Write one test for one observable behavior through the chosen public interface.
   - Run the smallest useful test command and confirm it fails for the expected reason.
   - If it passes before implementation, the test is not proving the missing behavior; tighten the setup or choose a better behavior.
   - Capture red evidence: command, failing test name, and failure reason.

4. GREEN: implement only enough code to pass:
   - Change production code only for the current failing behavior.
   - Keep implementation scoped to the current issue, current public interface, and current test.
   - Do not anticipate future tests, add speculative features, or broaden the change because adjacent cleanup is tempting.
   - Run the focused test until it passes, then run relevant nearby or existing checks that protect the touched area.
   - Capture green evidence: command, passing result, and any additional checks run or skipped.

5. Repeat vertically:
   - Add the next behavior only after the current test is green.
   - Let each new test respond to what the previous cycle taught you about behavior, interface shape, fixtures, and design friction.
   - Continue until the issue acceptance criteria or agreed behavior set is covered.

6. Refactor after green:
   - Read [Refactor After Green](references/refactor-after-green.md) before non-trivial cleanup.
   - Improve names, duplication, structure, locality, and interface shape only while tests are passing.
   - Prefer deeper modules when a smaller interface can hide real complexity and reduce caller/test burden.
   - Run tests after each meaningful refactor step.
   - Never refactor while red. Get to green first.

7. Close the loop:
   - Summarize test intent, red evidence, green evidence, refactor notes, and residual risk.
   - Note weak or missing test infrastructure honestly.
   - Recommend follow-up only when it is directly connected to untested behavior, missing infrastructure, or acceptance risk.

## Output Contract

During or after TDD work, report:

- Behavior: the observable behavior or regression protected.
- Public interface: the interface, command, route, component, service, adapter, or workflow used as the test surface.
- Test intent: the focused behavior test added or changed, with why it proves the requirement.
- Red evidence: command, failing test name, and expected failure reason before implementation.
- Green evidence: command, passing test/check result, and relevant existing checks run after implementation.
- Cycle notes: confirmation that work proceeded one vertical slice at a time, or an explicit reason when it could not.
- Refactor notes: cleanup performed after green, interface friction found, deep-module opportunities addressed or deferred, and tests rerun.
- Files changed: production code, tests, fixtures, docs, or config touched.
- Residual risk: skipped checks, weak or missing test infrastructure, uncovered behavior, flaky tests, environment limits, or follow-up needed.

If test infrastructure is weak or missing, report:

```markdown
## TDD Infrastructure Fallback

- Desired behavior proof: <observable behavior and public interface>
- Existing test support found: <tests, commands, fixtures, or "none">
- Smallest useful proof added or used: <test, characterization, harness, manual check, or "none">
- Why a stronger test was not added now: <tooling gap, missing harness, unsafe setup, time/risk, or scope>
- Residual risk: <what remains unproved>
- Recommended next step: <focused test infrastructure follow-up or none>
```

## Delegation

The main agent owns behavior selection, public-interface judgment, scope control, final implementation, and user communication.

When subagents are available, use them only for bounded work that can return evidence, such as:

- finding the nearest public interface, test convention, fixture pattern, or command;
- identifying existing tests that describe related behavior;
- checking whether a proposed test is coupled to internals;
- implementing a clearly owned production slice after the failing test is already defined;
- running verification on a disjoint platform or test command;
- reviewing the final change for spec coverage, standards, or security concerns.

Require every subagent result to include:

- paths inspected or changed;
- commands run or deliberately skipped;
- behavior and public interface under test;
- red or green evidence when relevant;
- assumptions, residual risk, and confidence.

If subagents are unavailable, perform the same work sequentially with a narrower context budget.

## Guardrails

### Guardrail: Horizontal Slices

DO NOT write all tests first, then all implementation.

This is horizontal slicing: treating RED as "write all tests" and GREEN as "write all code." It produces crap tests:

- Tests written in bulk test imagined behavior, not actual behavior.
- You end up testing the shape of things, such as data structures and function signatures, rather than user-facing behavior.
- Tests become insensitive to real changes: they pass when behavior breaks and fail when behavior is fine.
- You outrun your headlights, committing to test structure before understanding the implementation.

Correct approach: vertical slices via tracer bullets.

```text
WRONG (horizontal):
RED:   test1, test2, test3, test4, test5
GREEN: impl1, impl2, impl3, impl4, impl5

RIGHT (vertical):
RED to GREEN: test1 to impl1
RED to GREEN: test2 to impl2
RED to GREEN: test3 to impl3
...
```

One test, one implementation, repeat. Each test responds to what you learned from the previous cycle. Because you just wrote the code, you know exactly what behavior matters and how to verify it.

### Other Guardrails

- Do not test private helpers, internal collaborators, call counts, ordering, or implementation structure when a public interface can prove behavior.
- Do not verify behavior through a storage query, external backdoor, log scrape, or internal state read when a caller-facing interface can prove it.
- Do not mock owned code by default. Mock true external edges, time, randomness, filesystem, network calls, or dependencies that cannot safely run locally.
- Do not introduce ports, adapters, or dependency injection unless there is a real seam where behavior varies across production and test.
- Do not broaden scope beyond the current issue, current failing test, and public interface under change.
- Do not refactor while red.
- Do not pretend tests are stronger than they are. If infrastructure is weak, use the smallest honest proof and report residual risk.
- Do not create broad test infrastructure, fixture frameworks, package-manager changes, CI changes, or new dependencies unless the current issue explicitly calls for that foundation.
- Do not delete or rewrite existing tests just because they are awkward. Replace obsolete implementation-detail tests only when the new public-interface proof covers the behavior.
- Do not include private notes, credentials, client data, sensitive personal context, ignored scratch content, or real user data in tests or fixtures.

## References

- [Test Design](references/test-design.md) - read when choosing test scope, naming behavior tests, or avoiding implementation-detail tests.
- [Mocking And Seams](references/mocking-and-seams.md) - read before mocking dependencies, adding test doubles, or designing injection points.
- [Deep Modules](references/deep-modules.md) - read when public interfaces feel shallow, wide, leaky, or hard to test.
- [Refactor After Green](references/refactor-after-green.md) - read after tests pass and before non-trivial cleanup or module deepening.
