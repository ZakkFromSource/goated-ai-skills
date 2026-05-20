# Deepening Interface Patterns

Read this reference when an architecture improvement candidate needs deeper dependency, seam, testing, interface-design, or report-shaping guidance. Keep `SKILL.md` as the operating procedure; use this file for reusable patterns that would bloat the main workflow.

## Dependency Categories

Classify dependencies before proposing a deepening direction. The dependency shape determines whether behavior can move behind one interface directly or needs a port and adapter.

| Category | Shape | Deepening Guidance | Test Guidance |
| --- | --- | --- | --- |
| In-process | Pure computation, local state, parsing, validation, mapping, orchestration, or in-memory behavior | Usually deepen directly. Move repeated caller choreography behind the module interface. | Test through the new module interface with ordinary data and no adapter ceremony. |
| Local-substitutable | Filesystem, local database, queue, cache, clock, or other dependency with a faithful local stand-in | Deepen when the stand-in can exercise realistic behavior without network or production resources. | Use the local substitute, such as an in-memory filesystem or local database, through the interface. |
| Remote-owned | Networked service, internal API, worker, queue, or database owned by the project or organization | Keep domain logic in the deep module and put transport details behind a port when production and test behavior genuinely vary. | Use production and in-memory/test adapters, contract tests, or integration tests appropriate to the project. |
| True external | Third-party API, payment provider, email/SMS vendor, external auth, or service outside the project's control | Inject a narrow port that represents the project's needed behavior, not the vendor's full API. | Use a fake or mock adapter for most behavior tests and reserve live integration checks for explicit integration coverage. |

If the dependency category is unknown, do not invent a port. Record the uncertainty and recommend the smallest evidence-gathering step.

## Seam Discipline

A real seam is where behavior can vary without editing the caller. Good seams reduce caller knowledge. False seams add indirection while still forcing callers to know ordering, configuration, retry policy, mapping rules, or vendor details.

Use the real seam rule:

- Introduce a port or adapter when there is real variation, usually at least production behavior plus a faithful test or local behavior.
- Keep internal seams private when they help implementation or focused tests but should not become caller-facing concepts.
- Avoid one-adapter architecture. If the only implementation is production and no realistic variation exists, prefer a direct deep module interface until evidence says otherwise.
- Do not move vendor-shaped interfaces into the core module just because a vendor exists. The port should express the project behavior that callers need.

Common false seam signals:

- one interface, one implementation, and no clear future or test variation;
- callers still sequence several modules in the correct order;
- tests mock internal collaborators instead of observable outcomes;
- adapters expose transport, serialization, retry, or vendor vocabulary to domain callers;
- a seam exists only so a private helper can be mocked.

## Replace-Don't-Layer Testing

Deepening should usually move proof upward to the new module interface. Do not keep every old shallow-module unit test just because it existed before.

Use this replacement rule:

- Add or identify behavior tests through the deepened interface.
- Confirm those tests cover the important observable outcomes from old implementation-detail tests.
- Delete or retire obsolete shallow tests only when the new coverage is equivalent or stronger.
- Keep focused lower-level tests when they protect complex pure logic that remains a meaningful internal module.
- Avoid call-order assertions, private-state assertions, and mocks of owned internals when caller-visible behavior can prove the same result.

The goal is not fewer tests by default. The goal is tests that survive refactors because they describe behavior through the interface callers actually use.

## Interface Alternatives

For a strong candidate, design the interface more than once before recommending a direction. Use bounded subagents when available; otherwise run the passes sequentially.

Compare these alternatives when relevant:

- **Minimal interface**: the smallest API that can hide the repeated choreography now.
- **Flexible interface**: an API that supports likely variation without exposing internals or speculative extension points.
- **Caller-optimized interface**: the shape that makes the most common caller simple and hard to misuse.
- **Ports/adapters interface**: a core module interface plus ports for remote-owned or true external dependencies.

Each alternative should capture:

- interface shape and example usage;
- invariants, ordering constraints, errors, and configuration the caller must know;
- implementation complexity hidden behind the interface;
- dependency and adapter strategy;
- migration impact for existing callers and tests;
- tradeoffs in leverage, locality, compatibility, and testability.

Prefer a hybrid only when it is simpler than the individual alternatives and keeps the caller contract clear.

## Report Patterns

Markdown is the default portable report format. Add diagrams only when they clarify the evidence or proposed direction.

Recommendation strength:

- **Strong**: source evidence is clear, repeated friction exists, the next slice is small, and the expected depth/locality gain is high.
- **Worth exploring**: evidence points to real friction, but the next interface or dependency strategy needs more investigation.
- **Speculative**: the idea may be useful, but evidence is weak, scope is broad, or the change depends on product/ownership decisions.

Useful tags:

- Dependency: `in-process`, `local-substitutable`, `remote-owned`, `true-external`, `unknown`.
- Seam: `real seam`, `false seam`, `internal seam`, `external seam`, `one-adapter risk`.
- Test surface: `interface-level`, `implementation-detail`, `setup-heavy`, `mock-heavy`, `missing proof`.
- Next step: `TDD slice`, `architecture map`, `PRD`, `issue breakdown`, `RFC`, `evidence pass`.

Optional diagrams:

- Before/after module maps for caller choreography collapsing behind one interface.
- Flow diagrams for behavior currently split across modules.
- Interface-versus-implementation sketches for shallow versus deep module depth.
- Dependency diagrams showing where ports/adapters are justified.

Keep report prose specific:

- Say what callers/tests must know today.
- Say what a deeper interface would hide.
- Name the dependency category and seam shape.
- Name the smallest reversible next slice.
- State confidence and uncertainty instead of overselling the refactor.

## RFC Triggers

Recommend an RFC-style handoff when the candidate affects:

- public interfaces or published packages;
- data ownership, schema ownership, or persistence contracts;
- service, process, package, repository, or deployment boundaries;
- security posture, auth, secrets, privacy, or trust boundaries;
- multi-team or long-lived ownership;
- migration, deprecation, compatibility, or rollout strategy;
- multiple viable interface designs with meaningful tradeoffs.

For smaller candidates, prefer a focused issue or TDD slice with clear behavior proof.
