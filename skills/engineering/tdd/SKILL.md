---
name: tdd
description: Use when implementing or fixing target-project behavior, changing public interfaces, adding regression coverage, or doing test-first development.
metadata:
  goated-category: engineering
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

## Dependencies

Hard: None.

Soft:
- session-start-progressive-disclosure for unfamiliar target projects
- grill-with-docs when behavior, public interface, scope, language, or testing priority is unclear
- prd-to-issues when implementing a planned vertical issue slice
- prototype when risky behavior or interfaces need disposable evidence before production tests
- project-standards-calibration when test, fixture, naming, or quality standards affect implementation
- standards-and-spec-review after implementation when available
- code-security-review after implementation when trust boundaries, persistence, auth, or user data are touched
- doc-sync after behavior, public interface, architecture, or testing-doc changes
- verification-before-completion before complete/correct/passing/review-ready implementation claims

Fallback: If companion skills or docs are unavailable, inspect minimal evidence, use discoverable tests/commands, and state lower confidence plus residual risk.

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
   - Read [Testing Anti-Patterns](references/testing-anti-patterns.md) when tempted to skip RED, write tests after, change tests to match current behavior, over-mock, or claim completion from weak proof.

3. RED: write one focused failing test:
   - Write one test for one observable behavior through the chosen public interface.
   - When a behavior test is feasible, do not implement production behavior until RED evidence exists.
   - Run the smallest useful test command and confirm it fails for the expected reason.
   - If it passes before implementation, the test is not proving the missing behavior; tighten the setup or choose a better behavior.
   - If no feasible behavior test exists, use the infrastructure fallback and do not describe fallback proof as RED evidence.
   - Capture red evidence: command, failing test name, and failure reason.

4. GREEN: implement only enough code to pass:
   - Change production code only for the current failing behavior.
   - Keep implementation scoped to the current issue, current public interface, and current test.
   - Do not anticipate future tests, add speculative features, or broaden the change because adjacent cleanup is tempting.
   - Do not change a failing test to match broken behavior; change the test only when RED evidence shows the test is invalid or the requirement changed.
   - Run the focused test until it passes, then run relevant nearby or existing checks that protect the touched area.
   - Capture green evidence in two parts: focused command and passing result first, then broader checks run or skipped.

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
   - Pass the TDD evidence packet to `verification-before-completion` before making completion, correctness, passing, or review-ready claims; for drafts, analysis-only work, or fallback proof, verify only the claim being made and report residual risk.

## Output Contract

During or after TDD work, report:

- Behavior: the observable behavior or regression protected.
- Public interface: the interface, command, route, component, service, adapter, or workflow used as the test surface.
- Test intent: the focused behavior test added or changed, with why it proves the requirement.
- Red evidence: command, failing test name, and expected failure reason before implementation, or an explicit fallback reason when RED is not feasible.
- Green evidence: focused command and passing result, plus separate broader nearby or existing checks run after implementation.
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

Main owns behavior selection, public-interface judgment, scope control, final implementation, and user communication.

Delegate only bounded evidence-producing work: find the nearest public interface/test convention/fixture/command, identify related tests, check proposed tests for internal coupling, implement one owned production slice after the failing test is defined, run disjoint verification, or review spec/standards/security concerns.

Require `Status`: `DONE`, `DONE_WITH_CONCERNS`, `NEEDS_CONTEXT`, or `BLOCKED`; paths inspected or changed; commands run or skipped; behavior and public interface under test; red or green evidence when relevant; assumptions, residual risk, and confidence.

Status handling: `DONE` integrates evidence and continues the TDD cycle; `DONE_WITH_CONCERNS` requires concern review before trusting implementation/test/review, then fix, re-dispatch, or report risk; `NEEDS_CONTEXT` gets missing behavior, public interface, fixture, command, or spec detail before re-dispatch; `BLOCKED` narrows the slice, chooses a safer proof path, changes model/tooling, or escalates before continuing.

If subagents are unavailable, run the same work sequentially with a narrower context budget.

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
- Do not treat tests written after implementation as TDD unless you also prove they would have failed against the missing or broken behavior.
- Do not weaken, delete, or rewrite a behavior test just to make current implementation pass.
- Do not add production methods, flags, or hooks that exist only for tests; use test utilities or a real public interface.
- Do not pretend tests are stronger than they are. If infrastructure is weak, use the smallest honest proof and report residual risk.
- Do not claim work is complete from focused GREEN alone; route the actual claim through `verification-before-completion`.
- Do not create broad test infrastructure, fixture frameworks, package-manager changes, CI changes, or new dependencies unless the current issue explicitly calls for that foundation.
- Do not delete or rewrite existing tests just because they are awkward. Replace obsolete implementation-detail tests only when the new public-interface proof covers the behavior.
- Do not include private notes, credentials, client data, sensitive personal context, ignored scratch content, or real user data in tests or fixtures.
- Do not require this source repo's root files, issue files, `.local` notes, upstream sources, or hidden chat history after installation. The skill may rely only on its own files and target-project evidence.

## References

Linked support files, read at the workflow gates above: [Test Design](references/test-design.md), [Mocking And Seams](references/mocking-and-seams.md), [Deep Modules](references/deep-modules.md), [Refactor After Green](references/refactor-after-green.md), and [Testing Anti-Patterns](references/testing-anti-patterns.md).
