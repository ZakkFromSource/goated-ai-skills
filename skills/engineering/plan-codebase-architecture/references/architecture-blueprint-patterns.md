# Architecture Blueprint Patterns

Read this reference when a project-wide or feature-specific architecture plan needs more detailed blueprint patterns than `SKILL.md` should carry.

## Contents

- Blueprint modes
- Module and interface planning
- Dependency and seam planning
- Test-surface planning
- Anti-overdesign checks
- Artifact patterns

## Blueprint Modes

Use the smallest durable architecture artifact that can steer implementation.

| Mode | Use When | Default Output |
| --- | --- | --- |
| Project-wide setup | A new or newly onboarded project needs a shared architecture direction before repeated work starts. | `docs/agents/architecture-plan.md` |
| Feature-specific | A clarified feature, PRD, or issue changes modules, interfaces, data ownership, dependencies, or test strategy. | `docs/architecture/<slug>-architecture-plan.md` |
| Inline advice | The change is small, exploratory, or not worth a tracked artifact. | Inline response |

Project-wide blueprints should define stable architecture direction without pretending every future feature is known. Feature blueprints should focus on the feature's behavior and the interfaces needed to build it safely.

## Module And Interface Planning

Plan modules around behavior ownership and caller leverage.

For each planned module, capture:

- responsibility: the behavior or concept the module owns;
- interface: the entry points and facts callers must know;
- hidden complexity: orchestration, mapping, validation, retries, persistence, dependency details, or state transitions the module absorbs;
- invariants: ordering, lifecycle, identity, cardinality, permissions, and error modes;
- locality gain: what changes, bugs, or decisions become concentrated;
- evidence: source, brief, PRD, issue, ADR, standard, or assumption supporting the shape.

Prefer interface sketches and usage examples over file inventories. Name likely paths only when the target project has a clear convention or the current source already anchors the location.

Useful interface alternatives:

- **Minimal**: the fewest entry points that can hide real behavior now.
- **Caller-optimized**: the shape that makes the most common caller simple and hard to misuse.
- **Flexible**: supports known variation without exposing internals.
- **Ports/adapters**: keeps core behavior stable while dependency behavior varies at a real seam.

## Dependency And Seam Planning

Classify dependencies before choosing seams.

| Category | Planning Guidance |
| --- | --- |
| In-process | Keep behavior inside the deep module unless splitting improves locality or test clarity. |
| Local-substitutable | Use a local stand-in when it can prove behavior realistically. Avoid mocks if the substitute is faithful and cheap. |
| Remote-owned | Put transport behind a port when the project owns the dependency but needs local test behavior or multiple runtime adapters. |
| True external | Create a narrow project-shaped port around the behavior needed from the external service. Do not expose the vendor API to domain callers. |
| Unknown | Do not invent the seam. Mark the uncertainty and plan an evidence pass. |

Use the real seam rule:

- Add ports or adapters when behavior genuinely varies, usually production plus test/local behavior.
- Keep internal seams private when they help implementation but should not shape the caller contract.
- Avoid one-adapter indirection unless a near-term second adapter, test substitute, or compatibility requirement is explicit.
- Keep domain logic in the deep module and keep transport, vendor, persistence, or deployment detail behind the seam.

## Test-Surface Planning

Plan tests before implementation so the architecture has an observable behavior surface.

For each first slice, define:

- behavior proof: the user-visible or caller-visible behavior to verify;
- public test surface: module API, route, command, service interface, UI flow, repository, or adapter seam;
- dependency strategy: real dependency, local substitute, fake adapter, mock at true external edge, or integration check;
- fixture/setup expectations: the minimum setup needed to prove behavior;
- residual risk: behavior not covered by the first slice.

Good architecture makes the first TDD slice obvious. If a test would need private-state assertions, call-order assertions, or heavy internal patching, revise the interface or seam before implementation starts.

## Anti-Overdesign Checks

Before accepting a blueprint, ask:

- Does each module hide real behavior, or is it a thin name for a future file?
- Does the interface reduce caller knowledge, or does it move complexity into a different folder?
- Is each port backed by a real seam, dependency category, or test strategy?
- Are file paths grounded in current project conventions?
- Can the first implementation slice prove behavior through a public interface?
- Are unknown product, data, security, or ownership decisions marked as open questions?
- Would `improve-codebase-architecture` immediately flag this design as shallow, speculative, or hard to test?

If the answer is weak, simplify the blueprint or route to the needed evidence-gathering workflow.

## Artifact Patterns

Use concise Markdown and source references. Include diagrams only when they make module or dependency flow easier to trust.

Recommended durable sections:

- purpose and mode;
- source evidence;
- planned modules and interfaces;
- data/state ownership and dependency flow;
- test surfaces and first implementation slices;
- risks, open questions, and RFC/ADR triggers;
- recommended next workflow.

Useful tags:

- Blueprint mode: `project-wide`, `feature-specific`, `inline`.
- Dependency: `in-process`, `local-substitutable`, `remote-owned`, `true-external`, `unknown`.
- Seam: `real seam`, `internal seam`, `external seam`, `one-adapter risk`, `no seam needed`.
- Test surface: `module API`, `route`, `command`, `UI flow`, `repository`, `adapter`, `integration`.
- Next step: `prd-to-issues`, `tdd`, `write-a-prd`, `architecture-design-map`, `improve-codebase-architecture`, `ADR`, `RFC`.

RFC or ADR triggers:

- public interface, package, or API contract changes;
- data ownership, schema ownership, or persistence contract decisions;
- service, process, package, repository, or deployment boundaries;
- security posture, auth, secrets, privacy, or trust boundaries;
- multi-team or long-lived ownership;
- migration, deprecation, compatibility, or rollout strategy;
- multiple viable interface designs with meaningful tradeoffs.

Keep the blueprint honest: settled decisions should be actionable, assumptions should be labeled, and open questions should name when they must be answered.
