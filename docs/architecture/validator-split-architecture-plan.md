# Architecture Plan: Validator Split By Concern

## Purpose

This feature-specific blueprint guides Ticket 013's behavior-preserving split
of `scripts/validate_skills.py`. The command and the 16 validator functions
imported by tests remain compatible while cohesive concern modules take
ownership of validation rules, constants, and focused test surfaces.

Implementation now matches this blueprint on `ticket_013`; local acceptance
proof is complete, with GitHub Actions and maintainer review still pending.

## Source Evidence

- Brief and spec:
  `tickets/013-split-validator-by-concern.md` and
  `docs/specs/2026-07-25-goated-ai-skills-v2.md`.
- Project guidance: `AGENT.md`, `CONTEXT.md`,
  `docs/agents/project-standards.md`, and
  `docs/high-confidence-adoption-acceptance-report.md`.
- Current implementation: `scripts/validate_skills.py`,
  `tests/test_validate_skills.py`, `tests/test_v2_refinement_contracts.py`,
  `stack/fixtures/`, and `.github/workflows/validate.yml`.
- Source trace: the current file contains 56 top-level functions. Concern
  validators depend primarily on `Finding`, repo-relative path/text helpers,
  YAML loading, `is_string_list`, and two small fixture-contract helpers.
  `validate_skills`, reporting, and `main` are concentrated at the end of the
  file.
- Baseline commands run on 2026-07-26:
  `uv run python scripts/validate_skills.py`,
  `uv run python -m unittest discover -s tests -v`, and
  `uv run python scripts/compare_v1_v2_context.py`. They reproduced 37 skills
  and registry entries, 121 passing tests, 1,193 shared-policy words, zero
  human-review notes, three report-only drift notes, and route reductions of
  47.9%, 17.7%, 40.9%, and 10.1%.

## Planned Architecture

All implementation modules live under `scripts/validation/`. The compatibility
module remains `scripts/validate_skills.py`.

| Module | Responsibility | Interface and caller knowledge | Hidden complexity | Evidence or assumption |
| --- | --- | --- | --- | --- |
| `shared.py` | Own `Finding`, path/text traversal, YAML loading, and small type predicates used by multiple concerns. | Concern modules import stable primitives; callers do not coordinate file decoding or finding formatting. | Lenient text reads, stable relative paths, public-file traversal, YAML error conversion, and simple reusable contract checks. | Current dependency trace shows these helpers are shared across otherwise cohesive validators. |
| `skill_packages.py` | Own skill discovery, frontmatter, required sections, Markdown links, forbidden files, canonical references, public-boundary leaks, and report-only schema drift. | Expose cohesive validation functions plus a package-validation entry point used by aggregation. | Recovering from malformed frontmatter while continuing body checks and keeping blocking, review-only, and drift findings distinct. | Ticket groups skill-package, frontmatter, links, canonical references, and public-boundary validation. |
| `registry.py` | Own registry schema, catalog, alias, category, signal, and word-budget summary validation. | `validate_registry(repo)` and `registry_summary(repo)` preserve current results. | JSON Schema failures, cross-checks against installed skills, canonical names, aliases, and budget paths. | Existing registry logic is one contiguous block and imports package parsing helpers. |
| `routing.py` | Own route fixtures, end-to-end fixtures, and diagnosis-minimization contracts. | `validate_route_fixtures(repo)` and `validate_end_to_end_fixtures(repo)`. | Shared routing vocabulary, checkpoint and approval rules, registered-gate resolution, and end-to-end route constraints. | These functions already share routing profile helpers and constants. |
| `onboarding.py` | Own clarification and onboarding fixture validation. | `validate_clarification_fixtures(repo)` and `validate_onboarding_fixtures(repo)`. | Mode rules, evidence reuse, artifact budgets, continuity storage, and resumability contracts. | Ticket names clarification and onboarding as one concern group. |
| `planning.py` | Own specification/ticket, architecture, and implementation-planning validation. | `validate_planning_fixtures(repo)` and `validate_architecture_planning_fixtures(repo)`. | Compact/full spec contracts, ticket dependency frontiers, wide-refactor rules, Markdown sample inspection, and architecture-plan contracts. | Ticket names these planning surfaces together; their constants and helpers are already adjacent. |
| `behavior_proof.py` | Own behavior-proof, review/verification, and output-communication fixtures. | Three existing validator functions remain callable independently. | Stable contract matrices for TDD/refinement/delegation, specialist review gates, and closeout/output defaults. | Ticket assigns these validators to one concern group. |
| `merge_conflicts.py` | Own merge-conflict contracts and fixtures. | `validate_merge_conflict_fixtures(repo)`. | Operation-aware resolution, intent preservation, evidence sufficiency, and lifecycle authorization contracts. | Ticket requires explicit ownership and focused proof. |
| `research.py` | Own knowledge-retrieval and source-grounded-research validation. | Both existing public validator functions. | Read-only retrieval, authority/freshness, conflict handling, source hierarchy, and durable-capture contracts. | Ticket groups these related evidence concerns and requires source-grounded-research compatibility. |
| `operations.py` | Own Setup Scribe and Wayfinding validation. | Both existing public validator functions. | Recipe evidence states, safety boundaries, Wayfinder lifecycle, decision records, and linked Markdown delivery artifacts. | Ticket groups these two operational workflows. |
| `reporting.py` | Own aggregate result data, fixture counts, word-budget status, finding presentation, and exit-code calculation. | Return typed aggregate/report data; render the exact existing CLI lines in the same order. | Blocking versus informational result semantics, count collection, ordering, and output compatibility. | Current `main` duplicates count collection and presentation decisions over roughly 180 lines. |
| `scripts/validate_skills.py` | Remain the command entrypoint, orchestration boundary, and compatibility re-export surface. | Preserve `main()`, `validate_skills(repo)`, and the 16 direct test imports. | Direct-script versus imported-module loading and stable orchestration order. | Explicit Ticket 013 acceptance requirement. |

## Data And Dependency Flow

- `shared.py` is the dependency root and imports no concern module.
- Concern modules may import `shared.py`; `registry.py` may also import the
  frontmatter/discovery primitives owned by `skill_packages.py`.
- Concern modules do not import `reporting.py` or the CLI.
- `reporting.py` may depend on shared result types but does not discover
  concern implementations dynamically.
- `scripts/validate_skills.py` imports each concern explicitly, invokes them in
  the current order, and re-exports only the documented compatibility surface.
- Findings remain immutable values. Aggregation preserves three separate
  sequences: blocking errors, human-review notes, and report-only drift.
- No plugin system, dependency injection layer, or runtime registry is added;
  all dependencies are in-process and statically imported.

## Test Surfaces And Slices

| Slice | Behavior proof | Public test surface | Notes |
| --- | --- | --- | --- |
| Characterization | Compatibility names import, aggregate groups remain distinct, CLI lines stay ordered, success exits zero, and a failing fixture exits one. | `scripts.validate_skills`, the command, and subprocess exit status. | Add before moving behavior; this is baseline characterization rather than RED for new behavior. |
| Shared foundation | `Finding.format`, YAML error findings, stable path labels, and traversal behavior remain identical after relocation. | `scripts.validation.shared` plus compatibility re-export. | The first extraction is deliberately narrow and must leave all existing tests green. |
| Concern batches | Each extracted module accepts a minimal copied fixture tree and reports the same findings without importing unrelated concerns. | One concern module API per focused test class. | Move constants and helpers with their behavior owner; avoid pass-through wrappers. |
| Aggregation | All concerns execute in the established order and preserve exact result grouping. | `validate_skills(repo)`. | Extract only after concern ownership stabilizes. |
| CLI contraction | Counts, word-budget reporting, informational notes, presentation order, and exit codes remain exact. | `python scripts/validate_skills.py`. | Compatibility re-exports remain until final review proves callers migrated or preserved. |

## Risks, Open Questions, And Decision Triggers

- Import topology is the main migration risk because the file must work both as
  `scripts.validate_skills` and as a directly executed script. Use an explicit
  package-aware import compatibility block and prove both invocation forms.
- Constants must move with their concern owner. A broad `constants.py` would
  recreate coupling and is rejected.
- Shared helpers are limited to behavior used by at least two concern modules
  or foundational result/path/parsing contracts. Single-concern helpers stay
  local.
- Exact output strings and ordering are compatibility behavior; reporting
  cleanup waits until characterization coverage exists.
- No ADR is required because the public command and imports are preserved and
  no product, service, persistence, security, or deployment boundary changes.
  Revisit this only if implementation requires changing the public import
  surface.

## Recommended Next Step

- Run GitHub Actions and maintainer review against the completed module split,
  then archive Ticket 013 if no findings remain.
