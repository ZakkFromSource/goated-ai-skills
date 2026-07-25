---
name: design-codebase-architecture
description: Use when a clarified brief, PRD, issue, or grill result needs a source-grounded architecture blueprint before implementation, especially for deep modules, clear interfaces, real seams, dependencies, test surfaces, slice order, risks, or ADR/RFC triggers.
metadata:
  goated-category: engineering
---

# Design Codebase Architecture

## Purpose

Create a source-grounded architecture blueprint before implementation begins. Use this skill to turn clarified product or project intent into planned modules, interfaces, dependency seams, data ownership, test surfaces, and implementation slice order.

This skill is design-only. It prevents avoidable architecture drift by planning for deep modules up front, but it does not implement code, write tests, break issues down, create PRDs, or own RFC/ADR capture. Route those follow-ups to companion skills.

## Inputs

- Clarified brief, PRD, issue, `grill-with-docs` result, or user-confirmed project/setup intent.
- Target-project root path and whether the blueprint is project-wide, feature-specific, or a small inline design.
- Existing root `CONTEXT.md`, `docs/agents/context-matrix.md`, `docs/agents/project-standards.md`, `docs/agents/architecture-map.md`, ADRs, PRDs, issue handoffs, specs, README files, and contributor docs when present.
- Current source evidence for affected areas, including manifests, package/module indexes, routes, schemas, service clients, dependency wiring, persistence code, tests, fixtures, and CI/test commands.
- User constraints, such as compatibility, migration risk, team ownership, deployment topology, deadlines, security posture, or technology choices that cannot be inferred from local evidence.

## Dependencies

Hard: None.

Soft:
- session-start-progressive-disclosure for unfamiliar architecture planning
- grill-with-docs before durable blueprints when brief, scope, constraints, or language is unclear
- write-a-spec when product scope or acceptance criteria are not architecture-ready
- context-matrix-map when docs/agents/context-matrix.md exists or discovery is broad
- project-context-calibration when root CONTEXT.md or language affects architecture terms
- project-standards-calibration when standards affect module layout, testing, persistence, or artifact locations
- architecture-design-map when current architecture must be described before planning additions or changes
- review-codebase-architecture when existing-code repair or refactor ranking is the real task
- spec-to-tickets when the accepted blueprint should become delivery tickets
- tdd when a blueprint slice moves into implementation and behavior proof
- verification-before-completion before complete/evidence-backed/issue-breakdown-ready blueprint claims

Fallback: If companion skills or durable docs are unavailable, inspect minimal evidence, require an explicit clarified brief, keep confidence lower, and separate blueprint facts from assumptions.
## Architecture Language

Use project terms for concrete names. Keep these hot-path terms inline because they shape blueprint quality:

- **Module / interface**: plan behavior ownership plus the caller/test contract, not speculative file trees.
- **Deep vs shallow module**: prefer small meaningful interfaces that hide cohesive behavior over wrappers that leak coordination to callers.
- **Seam / port / adapter**: introduce only for real dependency variation, usually production plus test/local behavior.
- **Leverage / locality**: a good design reduces caller knowledge and concentrates change, bugs, and proof.
- **Interface-as-test-surface**: planned tests prove behavior through the public module interface.

## Workflow

1. Confirm the planning mode and intent gate:
   - Classify the blueprint as project-wide setup, feature-specific planning, or small inline architecture advice.
   - Require a clarified brief, PRD, issue, or `grill-with-docs` result before writing a durable blueprint.
   - If intent is fuzzy, route to `grill-with-docs` or `write-a-spec` before continuing.
   - Keep installed-skill instructions separate from target-project artifacts.

2. Choose output location:
   - For project-wide setup, write `docs/agents/architecture-plan.md` by default.
   - For feature-specific planning, write `docs/architecture/<slug>-architecture-plan.md` by default.
   - Return inline for small exploratory designs, tiny changes, or when the user does not want a durable artifact.
   - Prefer the target project's existing architecture-plan convention if one is clearly present.

3. Gather source and constraint evidence:
   - Use `docs/agents/context-matrix.md` when present to choose relevant docs, source, tests, and commands.
   - Read the clarified brief, relevant PRD/issue, context docs, standards, ADRs, architecture maps, manifests, representative code, tests, and dependency wiring.
   - Trace existing interfaces, callers, routes, data flow, persistence ownership, dependency construction, test surfaces, and deployment or runtime constraints as needed.
   - Record evidence inspected, commands run or skipped, assumptions, stale docs, contradictions, and missing sources.

4. Plan the interface-level architecture:
   - Identify planned modules by responsibility and hidden complexity, not by speculative file tree.
   - Define the caller-facing interface shape: entry points, caller knowledge, invariants, error modes, configuration, and expected results.
   - Assign data/state ownership and describe cross-module flow.
   - Classify dependencies as in-process, local-substitutable, remote-owned, true external, or unknown.
   - Introduce ports/adapters only where there is a real seam or dependency category justifies variation.
   - Read [Architecture Blueprint Patterns](references/architecture-blueprint-patterns.md) when choosing blueprint mode, module/interface shape, dependency or seam strategy, test surfaces, overdesign checks, or artifact shape.
   - Use the smallest useful visualization: prose for a simple design, a table for repeated module/interface comparisons, and a diagram only when flow, hierarchy, or topology is materially clearer visually.

5. Check against overdesign and underdesign:
   - Reject architecture that creates interfaces only because future variation might happen.
   - Reject file/folder inventories that are not grounded by current project evidence or accepted conventions.
   - Check that each planned module hides real behavior, improves locality, or gives callers/tests leverage.
   - Check that tests can prove behavior through intended public interfaces.
   - Mark open questions that block durable design instead of filling them with guesses.

6. Plan implementation slices without owning implementation:
   - Order the first slices by behavior and risk: smallest useful vertical path first, then dependent modules, integrations, and migration steps.
   - Name test surfaces and first TDD slices, but leave test writing and implementation to `tdd`.
   - Route ticket slicing to `spec-to-tickets` after the blueprint is accepted.
   - Route current-state diagrams to `architecture-design-map` and existing-code repair opportunities to `review-codebase-architecture`.
   - Route PRD, RFC, or ADR capture to companion workflows when the decision exceeds the blueprint.

7. Write or return the blueprint:
   - Include source evidence for important module, interface, dependency, data, and test-surface claims.
   - Separate settled decisions, assumptions, open questions, and deferred alternatives.
   - Include RFC or ADR triggers when the architecture crosses public interfaces, data ownership, service/package boundaries, deployment topology, security posture, migration strategy, or multiple viable interface designs.
   - Recommend the single next workflow or action.
   - Emit that recommendation as one next-step signal without reconstructing later implementation, review, documentation, and completion gates.
   - Use `verification-before-completion` before claiming a durable blueprint is complete, evidence-backed, or ready for downstream slicing; for small inline advice or exploratory designs, verify only the claim being made and state uncertainty.

## Output Contract

For durable project-wide or feature-specific blueprints, write Markdown shaped like this:

```markdown
# Architecture Plan: <Project Or Feature>

## Purpose

<What this blueprint is for and what implementation work it should guide.>

## Source Evidence

- Brief or spec: <path, conversation note, PRD, issue, or grill-with-docs result>
- Project evidence: <docs, source, tests, commands, ADRs, standards>
- Commands run or skipped: <commands and reasons>

## Planned Architecture

| Module | Responsibility | Interface and caller knowledge | Hidden complexity | Evidence or assumption |
| --- | --- | --- | --- | --- |

## Data And Dependency Flow

- Data/state ownership: <owners and constraints>
- Cross-module flow: <short flow or Mermaid diagram when useful>
- Dependency strategy: <in-process, local-substitutable, remote-owned, true external, ports/adapters, or unknown>

## Test Surfaces And Slices

| Slice | Behavior proof | Public test surface | Notes |
| --- | --- | --- | --- |

## Risks, Open Questions, And Decision Triggers

- Risks: <architecture, migration, compatibility, security, performance, ownership>
- Open questions: <question, owner, needed before>
- RFC/ADR triggers: <none or reason>

## Recommended Next Step

- <spec-to-tickets, writing-plans, tdd, write-a-spec, architecture-design-map, review-codebase-architecture, ADR/RFC capture, or none>
```

For inline output, include the same core pieces without forcing a durable file path.

## Delegation

Main owns mode, intent gate, architecture judgment, location, blueprint, and
communication. Delegate only bounded evidence traces, one constrained
alternative, or checks for overdesign, false seams, missing evidence, and weak
test surfaces.

Return inspected paths and commands, exact evidence, assumptions,
contradictions, confidence, residual uncertainty, status, and blueprint inputs,
not implementation or final edits. Resolve concerns or missing context before
choosing; narrow or stop on `BLOCKED`. Without delegation, run sequentially.

## Guardrails

- Do not write a durable blueprint from fuzzy intent. Require a clarified brief, PRD, issue, or `grill-with-docs` result.
- Do not implement production code, write tests, generate migrations, run formatters, break issues down, or mutate architecture as part of this skill.
- Do not turn the blueprint into a speculative file tree. Mention paths only when grounded by project evidence or accepted conventions.
- Do not create interfaces, ports, adapters, or dependency injection just in case. Require a real seam, dependency category, test strategy, or caller-leverage reason.
- Do not duplicate `write-a-spec`, `spec-to-tickets`, `writing-plans`, `tdd`, `architecture-design-map`, or `review-codebase-architecture`; emit one appropriate next-step signal when their job starts.
- Do not default to Mermaid or require a diagram when prose or a table is the smaller useful design artifact.
- Do not hide uncertainty. Mark inferred, stale, missing, weak, or conflicting evidence clearly.
- Do not include private notes, ignored local scratch files, credentials, client data, sensitive personal context, secrets, or real user data in tracked blueprints.
- Do not require this source repo's root docs after installation. The skill may rely only on its own installed files and target-project evidence.

## References

Linked support file, read at the workflow gate above: [Architecture Blueprint Patterns](references/architecture-blueprint-patterns.md).
