---
name: plan-codebase-architecture
category: engineering
classification: portable
status: wip
description: Plan source-grounded codebase or feature architecture before implementation begins. Use when a clarified project brief, PRD, issue, or grill-with-docs result needs an architecture blueprint with deep modules, clear interfaces, real seams, dependency strategy, test surfaces, slice order, risks, and RFC or ADR triggers.
triggers:
  - user asks to plan codebase architecture, feature architecture, module design, system design, or an architecture blueprint before implementation
  - a new target project needs a project-wide architecture plan after onboarding context and standards are known
  - a feature PRD, issue, or clarified brief affects modules, interfaces, data ownership, dependencies, test strategy, or implementation order
  - future implementation should be steered toward deep modules, clear seams, and behavior-focused test surfaces
outputs:
  - project-wide or feature-specific architecture blueprint
  - planned modules, responsibilities, interfaces, caller knowledge, and hidden complexity
  - dependency categories, ports, adapters, data/state ownership, seams, and cross-module flows
  - test surfaces, first TDD slices, implementation slice order, risks, open questions, and RFC or ADR triggers
depends_on:
  hard: []
  soft:
    - session-start-progressive-disclosure before planning architecture in an unfamiliar target project
    - grill-with-docs before durable blueprint writing when the brief, scope, constraints, or project language is unclear
    - write-a-prd when product scope or acceptance criteria are not clarified enough for architecture planning
    - context-matrix-map when docs/agents/context-matrix.md exists or source discovery is broad
    - project-context-calibration when root CONTEXT.md exists or project language affects architecture terms
    - project-standards-calibration when standards influence module layout, testing, persistence, or artifact locations
    - architecture-design-map when current architecture must be described before planning additions or changes
    - improve-codebase-architecture when existing-code repair or refactor ranking is the real task
    - prd-to-issues when the accepted blueprint should become implementation issue slices
    - tdd when a blueprint slice moves into implementation and behavior proof
  fallback: If companion skills or durable project docs are unavailable, inspect the minimum relevant evidence directly, require an explicit clarified brief from the user, keep confidence lower, and separate blueprint facts from assumptions.
adapters:
  codex: usable
  claude-code: usable
  hermes: usable
  opencode: usable
  generic-agent: usable
---

# Plan Codebase Architecture

## Purpose

Create a source-grounded architecture blueprint before implementation begins. Use this skill to turn clarified product or project intent into planned modules, interfaces, dependency seams, data ownership, test surfaces, and implementation slice order.

This skill is design-only. It prevents avoidable architecture drift by planning for deep modules up front, but it does not implement code, write tests, break issues down, create PRDs, or own RFC/ADR capture. Route those follow-ups to companion skills.

## Inputs

- Clarified brief, PRD, issue, `grill-with-docs` result, or user-confirmed project/setup intent.
- Target-project root path and whether the blueprint is project-wide, feature-specific, or a small inline design.
- Existing root `CONTEXT.md`, `docs/agents/context-matrix.md`, `docs/agents/project-standards.md`, `docs/agents/architecture-map.md`, ADRs, PRDs, issue handoffs, specs, README files, and contributor docs when present.
- Current source evidence for affected areas, including manifests, package/module indexes, routes, schemas, service clients, dependency wiring, persistence code, tests, fixtures, and CI/test commands.
- User constraints, such as compatibility, migration risk, team ownership, deployment topology, deadlines, security posture, or technology choices that cannot be inferred from local evidence.

## Architecture Language

- **Module**: anything with an interface and implementation, such as a function, class, package, feature slice, subsystem, route group, or tier-spanning flow.
- **Interface**: everything callers or tests must know to use a module correctly, including types, methods, invariants, ordering, error modes, configuration, and relevant performance expectations.
- **Deep module**: a module where a small, meaningful interface hides substantial cohesive behavior.
- **Shallow module**: a module whose interface is nearly as complex as its implementation, forcing callers to coordinate details.
- **Seam**: the place where a module's interface lives and where behavior can vary without editing the caller.
- **Port**: an interface introduced at a real seam so production and test adapters can vary dependency behavior while the deep module owns domain logic.
- **Adapter**: a concrete implementation of a port or interface at a seam.
- **Leverage**: more useful behavior per interface fact a caller must learn.
- **Locality**: concentrating change, bugs, knowledge, and verification in one module instead of scattering them across callers.
- **Interface-as-test-surface**: tests should prove observable behavior through the module interface that production callers use.

Use project terms from target-project evidence for concrete names. Use this vocabulary to explain architecture mechanics when the project has no better local language.

## Workflow

1. Confirm the planning mode and intent gate:
   - Classify the blueprint as project-wide setup, feature-specific planning, or small inline architecture advice.
   - Require a clarified brief, PRD, issue, or `grill-with-docs` result before writing a durable blueprint.
   - If intent is fuzzy, route to `grill-with-docs` or `write-a-prd` before continuing.
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
   - Read [Architecture Blueprint Patterns](references/architecture-blueprint-patterns.md) when choosing blueprint mode, dependency strategy, test surfaces, or artifact shape.

5. Check against overdesign and underdesign:
   - Reject architecture that creates interfaces only because future variation might happen.
   - Reject file/folder inventories that are not grounded by current project evidence or accepted conventions.
   - Check that each planned module hides real behavior, improves locality, or gives callers/tests leverage.
   - Check that tests can prove behavior through intended public interfaces.
   - Mark open questions that block durable design instead of filling them with guesses.

6. Plan implementation slices without owning implementation:
   - Order the first slices by behavior and risk: smallest useful vertical path first, then dependent modules, integrations, and migration steps.
   - Name test surfaces and first TDD slices, but leave test writing and implementation to `tdd`.
   - Route issue breakdown to `prd-to-issues` after the blueprint is accepted.
   - Route current-state diagrams to `architecture-design-map` and existing-code repair opportunities to `improve-codebase-architecture`.
   - Route PRD, RFC, or ADR capture to companion workflows when the decision exceeds the blueprint.

7. Write or return the blueprint:
   - Include source evidence for important module, interface, dependency, data, and test-surface claims.
   - Separate settled decisions, assumptions, open questions, and deferred alternatives.
   - Include RFC or ADR triggers when the architecture crosses public interfaces, data ownership, service/package boundaries, deployment topology, security posture, migration strategy, or multiple viable interface designs.
   - Recommend the single next workflow or action.

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

- <prd-to-issues, tdd, write-a-prd, architecture-design-map, improve-codebase-architecture, ADR/RFC capture, or none>
```

For inline output, include the same core pieces without forcing a durable file path.

## Delegation

The main agent owns the planning mode, intent gate, architecture judgment, output location, final blueprint, and user communication.

When subagents are available, use them for bounded evidence gathering or competing blueprint passes, such as:

- summarizing relevant PRD, issue, standards, ADR, context, or architecture-map evidence;
- tracing current callers, source modules, data flow, dependency wiring, or test surfaces for one affected area;
- drafting one alternative module/interface plan under a specific constraint, such as minimal interface, caller-optimized interface, or ports/adapters;
- checking the blueprint for overdesign, missing evidence, false seams, or weak test surfaces.

Require every subagent result to include:

- paths inspected;
- commands run or deliberately skipped;
- exact source evidence found;
- assumptions, contradictions, confidence, and residual uncertainty;
- candidate blueprint inputs, not unsupervised implementation or final artifact edits.

If subagents are unavailable, perform the same passes sequentially with a narrower context budget.

## Guardrails

- Do not write a durable blueprint from fuzzy intent. Require a clarified brief, PRD, issue, or `grill-with-docs` result.
- Do not implement production code, write tests, generate migrations, run formatters, break issues down, or mutate architecture as part of this skill.
- Do not turn the blueprint into a speculative file tree. Mention paths only when grounded by project evidence or accepted conventions.
- Do not create interfaces, ports, adapters, or dependency injection just in case. Require a real seam, dependency category, test strategy, or caller-leverage reason.
- Do not duplicate `write-a-prd`, `prd-to-issues`, `tdd`, `architecture-design-map`, or `improve-codebase-architecture`; route to them when their job starts.
- Do not hide uncertainty. Mark inferred, stale, missing, weak, or conflicting evidence clearly.
- Do not include private notes, ignored local scratch files, credentials, client data, sensitive personal context, secrets, or real user data in tracked blueprints.
- Do not require this source repo's root docs after installation. The skill may rely only on its own installed files and target-project evidence.

## References

Read [Architecture Blueprint Patterns](references/architecture-blueprint-patterns.md) when selecting blueprint mode, planning modules and interfaces, classifying dependencies, applying seam discipline, planning test surfaces, checking overdesign, or shaping durable artifacts.
