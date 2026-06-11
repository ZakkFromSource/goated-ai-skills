---
name: improve-codebase-architecture
description: Use when looking for source-grounded architecture improvement opportunities, refactor direction, shallow modules, tightly coupled concepts, hard-to-test areas, deeper modules, clearer seams, or more testable and agent-navigable code structure.
metadata:
  goated-category: engineering
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

## Dependencies

Hard: None.

Soft:
- session-start-progressive-disclosure for unfamiliar target projects
- context-matrix-map when docs/agents/context-matrix.md exists or discovery is broad
- project-context-calibration when root CONTEXT.md or language affects architecture terms
- project-standards-calibration when standards affect refactor shape, tests, or artifact location
- architecture-design-map when a descriptive current-state map is needed before ranking improvements
- grill-with-docs when architecture goal, user intent, or constraints are unclear
- tdd when a selected improvement moves into implementation and test design
- write-a-prd when a chosen direction needs product-level scope or stakeholder decisions
- prd-to-issues when a chosen direction should become implementation slices
- verification-before-completion before complete/evidence-backed/downstream-ready opportunity claims

Fallback: If companion skills or durable docs are unavailable, inspect minimal project evidence, keep confidence lower, and separate facts from assumptions.
## Architecture Language

Use target-project names for concrete modules and flows. Keep these review terms hot-path:

- **Module / interface / implementation**: compare caller/test knowledge with behavior hidden behind the module.
- **Depth, leverage, locality**: judge whether a smaller interface gives more capability and concentrates change and proof.
- **Deep vs shallow module**: reward cohesive hidden behavior; flag pass-through modules that leak caller choreography.
- **Deletion test**: if removing the module makes complexity reappear across callers, it likely earns its place.
- **Port**: project-shaped interface at a real seam; require production/test/local variation before recommending it.
- **False seam / adapter**: flag indirection when behavior does not really vary or callers still know internals.
- **Interface-as-test-surface**: prefer proof through caller-visible behavior; private/mock-heavy tests may expose weak shape.

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
   - Read [Deepening Interface Patterns](references/deepening-interface-patterns.md) when using review vocabulary, classifying dependency/seam shape, moving tests to an interface, comparing alternatives, or applying report tags.

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
   - Use `verification-before-completion` before claiming the ranking is complete, evidence-backed, or ready for downstream work; for lightweight scans, verify only the recommendation claim being made and state skipped areas.

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

Main owns scope, evidence standards, opportunity ranking, architecture judgment, final recommendation, and user communication.

Delegate only bounded exploration: trace callers/tests for one module/package/route/flow/dependency, identify shallow modules/repeated choreography/primitive clusters/hard-to-test areas in one source area, check dependency/seam shape, draft interface alternatives for one strong candidate, or validate evidence vs speculation.

Require `Status`: `DONE`, `DONE_WITH_CONCERNS`, `NEEDS_CONTEXT`, or `BLOCKED`; paths inspected; commands run or skipped; exact source evidence; candidate friction, dependency/seam shape, confidence, assumptions, contradictions, and residual uncertainty. No final user-facing recommendation unless specifically asked.

Status handling: `DONE` integrates opportunity evidence, dependency/seam assessment, or interface alternatives into ranking; `DONE_WITH_CONCERNS` requires review of speculative evidence, false seams, migration risk, weak test surfaces, or overbroad refactor direction before recommending; `NEEDS_CONTEXT` gets the missing source area, caller/test evidence, architecture doc, dependency constraint, or user goal before re-dispatch; `BLOCKED` narrows/splits/defer the candidate, changes model/tooling, or escalates.

If subagents are unavailable, run the same passes sequentially with a narrower context budget.

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

Linked support file, read at the workflow gate above: [Deepening Interface Patterns](references/deepening-interface-patterns.md).
