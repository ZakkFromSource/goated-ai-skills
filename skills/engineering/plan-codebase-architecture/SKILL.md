---
name: plan-codebase-architecture
category: engineering
classification: portable
status: wip
description: Use when a clarified brief, PRD, issue, or grill result needs a source-grounded architecture blueprint before implementation, especially for deep modules, clear interfaces, real seams, dependencies, test surfaces, slice order, risks, or ADR/RFC triggers.
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
    - verification-before-completion before claiming a durable blueprint is complete, evidence-backed, or ready for issue breakdown
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
   - Read [Architecture Blueprint Patterns](references/architecture-blueprint-patterns.md) when choosing blueprint mode, module/interface shape, dependency or seam strategy, test surfaces, overdesign checks, or artifact shape.

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

- <prd-to-issues, tdd, write-a-prd, architecture-design-map, improve-codebase-architecture, ADR/RFC capture, or none>
```

For inline output, include the same core pieces without forcing a durable file path.

## Delegation

Main owns planning mode, intent gate, architecture judgment, output location, final blueprint, and user communication.

Delegate only bounded evidence or competing-blueprint passes: summarize PRD/issue/standards/ADR/context/map evidence, trace callers/modules/data/dependency wiring/test surfaces for one area, draft one constrained alternative interface/module plan, or check the blueprint for overdesign, missing evidence, false seams, and weak test surfaces.

Require `Status`: `DONE`, `DONE_WITH_CONCERNS`, `NEEDS_CONTEXT`, or `BLOCKED`; paths inspected; commands run or skipped; exact source evidence; assumptions, contradictions, confidence, residual uncertainty; and candidate blueprint inputs rather than implementation or final artifact edits.

Status handling: `DONE` integrates evidence, risks, or alternative inputs into architecture judgment; `DONE_WITH_CONCERNS` requires review of overdesign, false seams, weak test surfaces, unsupported assumptions, or implementation-order risk before choosing; `NEEDS_CONTEXT` gets the missing PRD, issue, ADR, source path, dependency constraint, test evidence, or user decision before re-dispatch; `BLOCKED` narrows scope, splits design passes, defers unresolved decisions, changes model/tooling, or escalates.

If subagents are unavailable, run the same passes sequentially with a narrower context budget.

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

Linked support file, read at the workflow gate above: [Architecture Blueprint Patterns](references/architecture-blueprint-patterns.md).
