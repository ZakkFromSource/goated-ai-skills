# Diagram Patterns

Use this reference when choosing how to represent a source-grounded architecture map. Start with the smallest useful representation. Source references and the evidence table remain authoritative regardless of presentation format.

## Map Vocabulary

Use project domain names first. Use generic terms as map labels only when evidence supports them.

| Term | Map Use | Evidence To Cite |
| --- | --- | --- |
| Module | Node for a source unit or flow with caller-facing behavior, from function to subsystem. | Entrypoint, export, class or function, package index, route, or test. |
| Interface | Caller/test facts needed to use a module, such as entrypoint, type, invariant, error, config, or result. | Public API, route schema, type, docs, or tests. |
| Implementation | Internal code behind the node; cite only when it explains a relationship. | Source internals, call chain, wiring, or config. |
| Seam | Point where behavior can vary without changing the caller. | Interface plus multiple adapters, local/test substitute, or explicit dependency wiring. |
| Port | Project-shaped interface at a seam; label only when the project exposes dependency behavior through that interface. | Type, protocol, trait, abstract class, service interface, provider contract, or explicit dependency wiring. |
| Adapter | Concrete implementation at a seam for production, test/local behavior, or external integration. | Client, repository, fake, stub, provider, or service wiring. |

## Map Types

### Module Or Dependency Map

Use when showing major modules, packages, feature slices, adapters, or dependency direction.

```mermaid
flowchart LR
  UI[Planner UI] --> Controller[Planner controller]
  Controller --> Repo[Planner repository]
  Repo --> DB[(Project database)]
  Repo --> Analytics[Analytics adapter]

  classDef external fill:#fff7ed,stroke:#f97316,color:#7c2d12;
  class Analytics external;
```

Evidence to cite:

- package or folder entrypoints;
- import statements;
- route or provider registration;
- repository, adapter, or client wiring;
- tests that exercise the relationship.

### Flow Or Sequence Map

Use when the architecture is best understood as ordered behavior: request handling, async work, jobs, events, workflows, or cross-system calls.

```mermaid
sequenceDiagram
  participant User
  participant App
  participant API
  participant DB

  User->>App: Submit task
  App->>API: POST /tasks
  API->>DB: Insert task
  DB-->>API: Created task
  API-->>App: Task response
```

Evidence to cite:

- route handlers, controllers, jobs, queues, or event listeners;
- API docs, OpenAPI specs, or RPC definitions;
- tests or fixtures for the flow;
- logs or runbooks only when they are project-approved evidence.

### Runtime Topology Map

Use when showing deployed units, processes, storage, queues, third-party integrations, scheduled jobs, or infrastructure.

```mermaid
flowchart TB
  Web[Web app process] --> API[API process]
  API --> DB[(Postgres)]
  API --> Queue[[Job queue]]
  Worker[Worker process] --> Queue
  Worker --> External[Third-party API]

  classDef store fill:#eef2ff,stroke:#4f46e5,color:#312e81;
  classDef external fill:#fff7ed,stroke:#f97316,color:#7c2d12;
  class DB,Queue store;
  class External external;
```

Evidence to cite:

- deployment manifests, Dockerfiles, service configs, CI/CD, hosting docs;
- environment variable docs;
- queue, worker, scheduler, or infrastructure definitions;
- runbooks or architecture docs.

### Layered Map

Use when the architecture is intentionally organized by layers or tiers.

```mermaid
flowchart TB
  Presentation[Presentation layer]
  Application[Application layer]
  Domain[Domain logic]
  Persistence[Persistence adapters]

  Presentation --> Application
  Application --> Domain
  Application --> Persistence
```

Evidence to cite:

- documented layering rules;
- module naming conventions;
- import direction checks;
- representative source files.

Do not infer layering from directory names alone.

## Legends And Markers

Include a legend when the diagram uses visual conventions beyond plain nodes and arrows.

Suggested conventions:

- Solid arrow: verified relationship.
- Dashed arrow: inferred or weakly evidenced relationship.
- Orange node: external system or third-party integration.
- Blue node: datastore, queue, file store, or durable state.
- Thick border or label: seam or adapter point, only when source evidence supports it.
- `?` suffix: uncertain node or relationship.

Example:

```mermaid
flowchart LR
  A[Documented module] --> B[Verified dependency]
  A -. inferred .-> C[Potential dependency?]

  classDef uncertain stroke-dasharray: 5 5,stroke:#64748b,color:#334155;
  class C uncertain;
```

Every marker must be explained near the diagram and reflected in the source-reference table.

## Source Reference Table

Use one row per meaningful diagram claim. Group tiny claims only when they share the same source and confidence.

```markdown
| Diagram item | Evidence | Confidence | Notes |
| --- | --- | --- | --- |
| `Planner UI -> Planner controller` | `lib/features/planner/planner_page.dart`; `planner_controller.dart` | High | Verified by provider usage and controller import. |
| `Worker process -> Third-party API` | `docs/runbooks/jobs.md`; `src/jobs/sync.ts` | Medium | Runtime scheduling not verified in this pass. |
| `Billing adapter` | `src/billing/stripe_client.ts` | Low | Adapter role inferred from name and usage; no docs found. |
```

Confidence levels:

- `High`: verified by direct source evidence or explicit durable docs.
- `Medium`: supported by multiple weak signals or one strong source with a small gap.
- `Low`: plausible but incomplete, stale, inferred, or not fully traced.

## Format Selection

Use a visual format only when it adds value and is available in the current agent environment.

- Prose or bullets: useful for one relationship, a tiny caller set, or a short orientation.
- Table: useful for ownership, repeated mappings, interface comparisons, or evidence confidence.
- ASCII: useful for terminal-only output or tiny maps.
- Mermaid: useful for multi-node flows, hierarchy, dependency direction, sequence, or runtime topology.
- Excalidraw: useful for editable whiteboard-style collaboration.
- Generated image: useful for presentation or visual review, but should be derived from a source-grounded map.
- HTML: useful for rich reports when interaction or layout materially improves comprehension.
- Plugin-backed diagrams: useful when an installed tool can preserve editability or team workflow.

Keep source references or an evidence table as the auditable source of truth for every format.

## Anti-Patterns

- Decorative diagrams with no source references.
- Diagrams that show desired future architecture as if it exists.
- Before/after refactor proposals; route those to architecture improvement workflows.
- Exhaustive file inventories disguised as architecture maps.
- Dense diagrams that need a long essay to be understood.
- Claims based only on common framework habits rather than target-project evidence.
