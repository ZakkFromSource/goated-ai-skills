# Testing Anti-Patterns

Read this reference when a TDD cycle is under pressure, a test is being skipped, mocks are spreading, or completion would rely on proof weaker than the claim.

The goal is not ritual for its own sake. The goal is trustworthy behavior proof through public interfaces, one vertical RED/GREEN cycle at a time. When tests are hard to write, treat that as design evidence: the module may be shallow, the public interface may leak internals, or a real dependency seam may be missing.

## Quick Rule

Before implementation, prefer one focused failing behavior test through a public interface. After implementation, prove the same behavior goes green and run the relevant surrounding checks.

If that is not feasible, say why, use the smallest honest proof available, and report residual risk. Do not turn weak proof into a strong claim.

## Anti-Pattern: Skipping Feasible Tests

Symptoms:

- "This is too small to test" even though a nearby test pattern exists.
- "The framework is annoying" when the behavior can still be reached through a public interface.
- "Manual testing is enough" for behavior that will need regression protection.

Why it hurts:

- The change has no repeatable proof.
- Future refactors cannot distinguish intended behavior from accident.
- The agent loses the design feedback that TDD would have produced.

Better:

- Add the smallest behavior test that can fail for the missing behavior.
- Use existing fixtures, commands, or public APIs before inventing new infrastructure.
- If test support is genuinely missing, document the gap and add the smallest useful fallback proof.

## Anti-Pattern: Tests After Implementation Called TDD

Symptoms:

- Production code was written first, then tests were added and passed immediately.
- The report claims TDD because tests exist.
- The test mostly describes what the implementation already does.

Why it hurts:

- A test that never failed has not proved it can catch the missing behavior.
- Tests-after are biased toward the current implementation shape.
- The RED signal is missing, so the cycle cannot prove the test is meaningful.

Better:

- Pause and establish proof before continuing.
- If the agent made exploratory changes safely, set them aside or redo the agent's own work from a failing behavior test when appropriate.
- If keeping existing implementation is necessary, be honest: call it tests-after or regression coverage, not TDD, and report the missing RED evidence.

## Anti-Pattern: Changing Tests To Match Broken Behavior

Symptoms:

- A failing test is relaxed until it passes without the required behavior.
- Expected values are changed because the current output is easier to accept.
- Assertions are deleted instead of explaining why they no longer represent the requirement.

Why it hurts:

- The test stops guarding the user-visible contract.
- Broken behavior becomes documented as expected behavior.
- Future agents inherit false confidence.

Better:

- Re-read the issue, PRD, bug report, or public contract.
- Keep the test aligned with intended behavior unless the requirement itself changed.
- If the requirement is ambiguous, ask or report `NEEDS_CONTEXT` instead of normalizing the broken output.

## Anti-Pattern: Over-Mocking Owned Code

Symptoms:

- Internal collaborators are mocked even though the project owns them.
- The test asserts call counts, call order, or method names inside the implementation.
- Refactoring internals breaks tests while user-visible behavior still works.

Why it hurts:

- Tests freeze shallow structure instead of behavior.
- Owned modules cannot be deepened freely.
- The public interface stops being the test surface.

Better:

- Exercise real owned code through the public interface.
- Mock only true external, slow, unsafe, nondeterministic, or costly dependencies.
- If mocking feels necessary for owned code, look for a missing deep module or misplaced real seam.

## Anti-Pattern: Testing Mocks Instead Of Behavior

Symptoms:

- The assertion proves a mock component, fake response, or stub method was used.
- The test would pass even if the real behavior were missing.
- Test names mention the mock instead of the user or caller outcome.

Why it hurts:

- The mock becomes the subject under test.
- The test no longer proves production behavior.
- A broken integration can hide behind a passing mock assertion.

Better:

- Assert on observable behavior: returned result, rendered affordance, emitted command, persisted state through a public interface, or safe recorded external effect.
- Use fakes to support the behavior test, not to replace the behavior being tested.
- If the mock has no behavior-relevant assertion, remove it or move it to the real external seam.

## Anti-Pattern: Test-Only Production APIs

Symptoms:

- A production class gains methods used only by tests.
- Cleanup, state inspection, reset, or force-set helpers appear in production interfaces.
- Tests require callers to know lifecycle details that real callers should not know.

Why it hurts:

- The production contract grows around test plumbing.
- Real callers see APIs that are unsafe, confusing, or unsupported.
- Test friction is hidden instead of used as design evidence.

Better:

- Put setup and cleanup in test utilities, fixtures, or local adapters.
- Prefer public results over private state inspection.
- If production callers also need the capability, design it as a real public behavior and test it as such.

## Anti-Pattern: Incomplete Fakes Or Mocks

Symptoms:

- A fake returns only the fields the current assertion needs.
- A mock omits side effects the behavior depends on.
- The fake accepts invalid sequences that the real dependency would reject.

Why it hurts:

- Tests pass against a world production will never see.
- Integration failures appear later and are harder to diagnose.
- The fake becomes another untested implementation.

Better:

- Model the parts of the dependency contract the behavior relies on, including required fields, errors, and side effects.
- Keep fake behavior small but faithful.
- If a faithful fake is becoming complex, consider a real local substitute, contract test, or narrower external seam.

## Anti-Pattern: Manual-Only Proof

Symptoms:

- The only evidence is "I tried it" or "it worked locally."
- Manual steps are not repeatable enough for another agent or maintainer.
- A completion claim depends on screenshots, logs, or UI clicks without an automated regression path where one is feasible.

Why it hurts:

- Manual checks decay immediately.
- Future changes cannot rerun the proof cheaply.
- Edge cases and regressions depend on memory.

Better:

- Add automated behavior proof when feasible.
- Use manual checks as supplemental evidence for rendering, integration, or environment-specific behavior.
- When manual-only proof is the best available option, list exact steps, result observed, why automation was not added, and residual risk.

## Anti-Pattern: Completion Claims Without Proof

Symptoms:

- "Done", "fixed", "passing", or "ready" appears without command evidence.
- Only the focused test passed, but the report implies broad verification.
- Skipped checks are omitted.

Why it hurts:

- The claim is stronger than the evidence.
- Reviewers cannot tell what was actually protected.
- The next agent may skip needed verification.

Better:

- Report RED evidence, GREEN evidence, and broader checks separately.
- Say exactly which commands ran and what they proved.
- Route completion, correctness, passing, or review-ready claims through `verification-before-completion` when available.

## Rationalization Checks

| Rationalization | Better response |
| --- | --- |
| "It is too small to test." | Find the smallest public-interface behavior test, or explain why none is feasible. |
| "I will test after." | That may add coverage, but it is not TDD without RED evidence. |
| "The current output is close enough." | Keep assertions tied to required behavior or request clarification. |
| "Mocking this makes the test easier." | Mock only at real external seams; owned code should usually run. |
| "The fake only needs these fields." | Include the dependency contract the behavior relies on. |
| "Manual proof is faster." | Use manual proof only as supplemental or explicitly weaker fallback evidence. |
| "All good." | Name the commands, results, skipped checks, and residual risk. |

## Stop And Recover

Pause when any of these happen:

- implementation exists without RED evidence;
- a feasible test is being skipped;
- a test is changed to accept broken behavior;
- mocks are replacing owned behavior;
- production APIs are being added only for tests;
- proof is too weak for the completion claim.

Recovery path:

1. Restate the observable behavior and public interface.
2. Choose one vertical slice and write or repair the failing test.
3. Run it and capture the expected failure reason.
4. Implement only enough to pass that test.
5. Run focused and relevant surrounding checks.
6. Report any missing RED evidence, fallback proof, or residual risk honestly.

If earlier exploratory implementation exists, do not rewrite unrelated user work. For the agent's own safe exploratory changes, pause, establish proof, and discard or redo only what is appropriate to regain a trustworthy cycle.

