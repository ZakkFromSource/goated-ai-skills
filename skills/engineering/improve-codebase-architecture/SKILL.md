---
name: improve-codebase-architecture
category: engineering
classification: portable
status: wip
description: Explore source-grounded architecture improvement opportunities, especially shallow modules, tightly coupled concepts, hard-to-test areas, and places where deeper modules would improve testability and AI navigability. Use when a user asks to improve architecture, find refactoring opportunities, consolidate modules, make code more testable, or write architecture RFCs.
triggers:
  - user asks to improve architecture, codebase architecture, module structure, boundaries, seams, layering, or refactor direction
  - user asks for architecture improvement opportunities before committing to a refactor
  - tests, callers, or implementation work reveal shallow modules, repeated choreography, leaky seams, or hard-to-test code
  - a target project needs ranked refactor candidates, deepening directions, or an RFC-style handoff
outputs:
  - review scope, mode, evidence inspected, and commands run or skipped
  - ranked architecture improvement opportunities with source evidence
  - current friction, dependency/seam shape, deepening direction, tradeoffs, confidence, suggested next slice, and RFC trigger per opportunity
  - cross-cutting themes, deferred or rejected candidates, assumptions, skipped areas, and recommended next step
depends_on:
  hard: []
  soft:
    - session-start-progressive-disclosure before reviewing an unfamiliar target project
    - context-matrix-map when docs/agents/context-matrix.md exists or source discovery is broad
    - project-context-calibration when root CONTEXT.md exists or project language affects architecture terms
    - project-standards-calibration when standards influence refactor shape, test expectations, or artifact location
    - architecture-design-map when a descriptive current-state map is needed before ranking improvements
    - grill-with-docs when the architecture goal, user intent, or project constraints are unclear
    - tdd when a selected improvement moves into implementation and test design
    - write-a-prd when a chosen direction needs product-level scope or stakeholder decisions
    - prd-to-issues when a chosen direction should become implementation slices
  fallback: If companion skills or durable project docs are unavailable, inspect the minimum relevant project evidence directly, keep confidence lower, and separate facts from assumptions.
adapters:
  codex: usable
  claude-code: usable
  hermes: usable
  opencode: usable
  generic-agent: usable
---

# Improve Codebase Architecture

## Purpose

Review a target project's existing source and docs to find architecture improvement opportunities before implementation begins. Prefer deeper modules: small, meaningful interfaces that hide real behavior, improve locality, and give callers and tests more leverage.

This skill is review/design-only. It ranks opportunities, explains tradeoffs, and routes the next slice or RFC decision. It does not implement refactors, rewrite code, update tests, or mutate project architecture unless the user separately asks for implementation.

## Inputs

- User request, target-project root, architecture concern, and requested scope.
- Existing `docs/agents/context-matrix.md`, root `CONTEXT.md`, `docs/agents/project-standards.md`, `docs/agents/architecture-map.md`, ADRs, PRDs, issue handoffs, specs, and contributor docs when present.
- Source files, manifests, package/module indexes, route definitions, entrypoints, dependency injection/configuration code, data-access code, service clients, adapters, tests, fixtures, and CI/test commands related to the review scope.
- Existing architecture diagrams, prior refactor notes, implementation pain points, test failures, flaky areas, or user-provided examples of hard-to-change code.

## Architecture Language

- **Module**: anything with an interface and an implementation, such as a function, class, package, feature slice, subsystem, route group, or tier-spanning flow.
- **Interface**: everything callers or tests must know to use a module correctly, including types, methods, invariants, ordering, error modes, configuration, and relevant performance expectations.
- **Implementation**: the code and internal structure behind a module's interface.
- **Depth**: the leverage provided by a module's interface: how much useful behavior callers can exercise per interface fact they must understand.
- **Deep module**: a module where a small, meaningful interface gives access to substantial cohesive behavior and hides implementation complexity.
- **Shallow module**: a module whose interface is nearly as complex as its implementation, often passing complexity through to callers.
- **Seam**: the place where a module's interface lives and where behavior can vary without editing the caller.
- **Port**: an interface introduced at a real seam so production and test adapters can vary dependency behavior while the deep module owns domain logic.
- **Adapter**: a concrete implementation that satisfies a port or interface at a seam, usually for production, testing, or an external integration.
- **Leverage**: what callers gain from depth: more capability and behavior per interface fact they must learn.
- **Locality**: what maintainers gain from depth: change, bugs, knowledge, and verification concentrate in one module instead of scattering across callers.
- **Deletion test**: if deleting a module makes its complexity reappear across callers, it was hiding useful behavior; if complexity simply disappears, it was likely pass-through.
- **Interface-as-test-surface**: tests should exercise observable behavior through the module's interface. Tests reaching behind the interface are evidence that module shape or seam placement may need attention.

Use the target project's own domain names for concrete modules and flows. Use this vocabulary to explain architecture mechanics when the project has no better local term.

## Workflow

1. Confirm scope and mode:
   - Identify the target-project root from the request, current directory, repository metadata, or manifests.
   - Classify the work as broad architecture scan, focused subsystem review, testability review, dependency/seam review, or RFC-prep review.
   - Keep installed-skill instructions separate from target-project artifacts.
   - Ask only when the target root, review scope, or required output cannot be inferred safely.

2. Gather evidence before judging:
   - Use `docs/agents/context-matrix.md` when present to choose first-read and second-read sources.
   - Read relevant context docs, ADRs, architecture maps, standards, PRDs/issues, manifests, entrypoints, package indexes, imports/callers, representative source, tests, fixtures, and dependency construction code.
   - Trace actual calls, imports, data flow, configuration, routes, job wiring, or test setup instead of relying on folder names alone.
   - Record commands run, commands skipped, missing evidence, stale docs, inferred relationships, and contradictions.

3. Find candidate architecture friction:
   - Look for shallow pass-through modules, thin layers, wrappers that mostly forward calls, and modules that fail the deletion test.
   - Look for tightly coupled concepts, behavior split across callers, repeated caller choreography, primitive clusters, and modules that require many public calls to prove one behavior.
   - Look for hard-to-test areas: noisy setup, internal patching, private-state assertions, call-order tests, dependency construction hidden too deep, or tests coupled to implementation details.
   - Look for false seams: ports/adapters with only one real implementation, interfaces added only for tests, or seams that leak internal ordering and configuration back to callers.
   - Look for dependency shapes that block deepening: in-process logic, local-substitutable dependencies, remote-owned services, and true external services.
   - Read [Deepening Interface Patterns](references/deepening-interface-patterns.md) when classifying dependency/seam shape, comparing interface alternatives, or shaping the report.

4. Rank opportunities:
   - Prefer candidates with strong source evidence, repeated pain across callers/tests, meaningful public-interface leverage, and a small next slice.
   - Separate high-confidence opportunities from speculative ideas, taste preferences, broad rewrites, and candidates blocked by missing evidence.
   - Include rejected or deferred candidates when they looked plausible but failed the evidence, deletion, locality, seam, or test-surface checks.

5. Sketch deepening directions without implementing:
   - Describe what behavior should move behind a smaller interface, what callers/tests would stop needing to know, and which dependencies should remain internal or become ports.
   - For strong candidates, optionally compare interface alternatives: minimal, flexible, caller-optimized, and ports/adapters designs.
   - Recommend an RFC-style handoff when the candidate crosses public interfaces, data ownership, service/package boundaries, deployment topology, security posture, multi-team ownership, migration/deprecation strategy, or multiple viable interface designs.

6. Report and route the next step:
   - Return the ranked review inline unless the user requested a durable artifact.
   - Recommend `architecture-design-map` when a current-state diagram is missing and would reduce uncertainty.
   - Recommend `write-a-prd`, `prd-to-issues`, or an RFC when the chosen direction needs planning before implementation.
   - Recommend `tdd` when the next step is a focused implementation slice with behavior proof through the new or existing interface.

## Output Contract

Return a compact review shaped like this:

```markdown
## Review Scope

- Mode: <broad scan, focused subsystem, testability, dependency/seam, or RFC-prep>
- Target root: <path or inferred project>
- Evidence inspected: <files, docs, commands, tests, assumptions>
- Commands run or skipped: <commands and reasons>

## Ranked Opportunities

1. <opportunity title> - <Strong, Worth exploring, or Speculative>
   - Source evidence: <paths, callers, tests, commands, docs>
   - Current friction: <what callers/tests/maintainers must know today>
   - Dependency/seam shape: <in-process, local-substitutable, remote-owned, true external, false seam, or unknown>
   - Deepening direction: <what behavior/interface should change at a high level>
   - Tradeoffs: <costs, migration risk, compatibility, test impact>
   - Confidence: <high, medium, or low with reason>
   - Suggested next slice: <small review, prototype, TDD slice, PRD/issue, or RFC>
   - RFC trigger: <none or reason>

## Cross-Cutting Themes

- <repeated architecture pattern, dependency issue, or test-surface issue>

## Deferred Or Rejected Candidates

- <candidate and why it was not recommended now>

## Assumptions And Skipped Areas

- <missing evidence, skipped commands, stale docs, or unresolved scope>

## Recommended Next Step

- <one recommended route>
```

For an RFC-style handoff, include the chosen problem, source evidence, public interfaces affected, viable interface designs, migration/deprecation concerns, test strategy, open decisions, and the smallest reversible next slice.

## Delegation

The main agent owns scope, evidence standards, opportunity ranking, architecture judgment, final recommendation, and user communication.

When subagents are available, use them for bounded independent exploration, such as:

- tracing callers/tests for one module family, package, route group, feature flow, or dependency;
- identifying shallow modules, repeated choreography, primitive clusters, or hard-to-test areas in one bounded source area;
- checking dependency/seam shape for a named integration;
- drafting competing interface alternatives for one strong candidate;
- validating whether a candidate is evidence-backed or speculative.

Require every subagent result to include:

- paths inspected;
- commands run or deliberately skipped;
- exact source evidence found;
- candidate friction, dependency/seam shape, and confidence;
- assumptions, contradictions, and residual uncertainty;
- no final user-facing architecture recommendation unless specifically asked.

If subagents are unavailable, perform the same passes sequentially with a narrower context budget.

## Guardrails

- Do not implement refactors, edit production code, rewrite tests, run formatters, apply migrations, or mutate architecture as part of this review-only skill.
- Do not judge architecture before gathering relevant source evidence.
- Do not rank speculative rewrites, personal taste, folder-layout impressions, or ecosystem best practices as findings without target-project evidence.
- Do not claim a module is shallow only because it is small; judge by interface complexity, caller knowledge, deletion test, and hidden behavior.
- Do not introduce ports, adapters, dependency injection, or seams unless behavior genuinely varies across the seam or dependency category justifies it.
- Do not preserve old implementation-detail tests by default in a proposed direction; replace them only when equivalent interface-level behavior coverage exists.
- Do not hide uncertainty. Mark inferred, stale, missing, weak, or conflicting evidence clearly.
- Do not create durable target-project artifacts, ADRs, PRDs, or issue files unless the user separately asks for those outputs.
- Do not include private notes, ignored local scratch files, credentials, client data, sensitive personal context, secrets, or real user data in reports.
- Do not require the original skill-library repository or any maintainer-only root files after installation. The skill may rely only on its own installed files and target-project evidence.

## References

Read [Deepening Interface Patterns](references/deepening-interface-patterns.md) when classifying dependency categories, applying seam discipline, deciding how tests should move to an interface, comparing interface alternatives, or using report tags and diagrams.
