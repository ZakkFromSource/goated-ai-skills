# Split Validator By Concern Implementation Plan

## Plan Target

- Ticket: `tickets/archive/013-split-validator-by-concern.md`.
- Architecture:
  `docs/architecture/validator-split-architecture-plan.md`.
- Mode: durable tracked plan because the refactor is architectural,
  multi-surface, compatibility-sensitive, and expected to span bounded
  extraction batches.
- Execution route: sequential characterization and TDD-compatible extraction.
  Overlapping moves remain sequential because all concerns currently share one
  source file.

## Implementation Status

- Implemented and merged into `update/v2` with focused concern modules,
  compatibility
  re-exports, direct-module tests, and a thin CLI.
- Local acceptance proof, GitHub Actions, maintainer review, and archival are
  complete.

## Source Inspected

- `AGENT.md`, `CONTEXT.md`, `docs/agents/project-standards.md`, and the ticket.
- `docs/specs/2026-07-25-goated-ai-skills-v2.md` and
  `docs/high-confidence-adoption-acceptance-report.md`.
- `scripts/validate_skills.py`, `tests/test_validate_skills.py`,
  `tests/test_v2_refinement_contracts.py`, `stack/fixtures/`,
  `.github/workflows/validate.yml`, and `pyproject.toml`.
- An AST trace of all 56 validator functions, their line ranges, direct
  intra-file calls, imports, and module constants.
- Fresh baseline output from the validator, all 121 unit tests, and the V1/V2
  comparison.

## Slice Shape And Interface Focus

The first slice is a narrow characterization foundation. It adds observable
compatibility proof without changing production behavior. Later slices move
one cohesive concern at a time behind its public module interface while
`scripts.validate_skills` keeps the established compatibility exports and
orchestration order.

## Assumptions

- `scripts/validation/` is the project-local package boundary for validator
  implementation modules.
- The 16 functions currently imported in `tests/test_validate_skills.py` remain
  re-exported from `scripts.validate_skills` for the whole ticket.
- Characterization tests that pass against existing behavior are intentional
  baseline proof, not RED evidence. Each extraction then uses those tests as
  its behavior-preserving GREEN gate.
- No validation behavior, message, fixture schema, output wording, or
  lifecycle status changes in this ticket.

## Stop Conditions

- Pause if a moved concern changes any finding path/message, output order,
  fixture count, informational-note count, or exit status.
- Pause if a proposed shared helper is used by only one concern or forces a
  concern module to import the CLI, reporting, or an unrelated concern.
- Stop and redesign if direct command execution and imported-module execution
  cannot use the same implementation without path mutation or circular
  imports.
- Do not resolve the three Learning Capture drift notes or add validation rules.
- Do not claim completion if focused proof, the full acceptance commands,
  compilation, diff checks, or CI evidence is missing.

## Steps

1. Add `tests/test_validator_compatibility.py` to characterize the 16 direct
   compatibility exports, `Finding` formatting, aggregate result grouping,
   successful CLI output order and counts, zero exit status, and non-zero exit
   status for a deliberately invalid temporary repository. Run this test file
   and retain the passing pre-extraction evidence.
2. Create `scripts/validation/shared.py` and focused tests for the stable
   finding, path, text, traversal, YAML-loading, and reusable fixture-predicate
   interfaces. Move only those primitives, re-export compatibility names where
   required, and run the focused compatibility, registry, and full validator
   tests after the move.
3. Extract `skill_packages.py` and `registry.py` sequentially. Move constants
   with their behavior owners, preserve malformed-frontmatter recovery and
   three-way finding grouping, and prove each module against minimal copied
   repositories before running the existing registry tests.
4. Extract `routing.py`, then `onboarding.py`, then `planning.py`. After each
   move, run only that concern's existing unittest classes first, followed by
   compatibility tests and the repository validator.
5. Extract `behavior_proof.py`, `merge_conflicts.py`, `research.py`, and
   `operations.py` in separate GREEN batches. Add direct module tests proving
   each concern runs with only its own fixture tree and shared prerequisites.
   Keep merge-conflict and source-grounded-research ownership explicit.
6. Extract aggregation and presentation into `reporting.py`. Preserve concern
   invocation order, fixture counts, word-budget status, zero human-review
   notes, the three report-only drift notes, exact output lines, and exit-code
   semantics under the characterization tests.
7. Contract `scripts/validate_skills.py` to argument parsing, explicit
   orchestration, presentation invocation, exit handling, and documented
   compatibility re-exports. Review import direction with an AST scan and
   reject circular imports, dynamic concern discovery, generated duplication,
   and shallow pass-through modules.
8. Review the diff against every Ticket 013 criterion and project standard.
   Synchronize only docs whose architecture, test commands, or contributor
   guidance materially changed; do not archive or mark the ticket complete
   before acceptance and CI evidence.
9. Run the focused 35-test acceptance suite, `uv run python
   scripts/validate_skills.py`, `uv run python -m unittest discover -s tests
   -v`, `uv run python scripts/compare_v1_v2_context.py`, `uv run python -m
   compileall -q scripts tests`, and `git diff --check`. Inspect the final diff,
   module import graph, file sizes, and `git status --short`, then obtain a
   green GitHub Actions run before the final compatibility claim.

## Acceptance Coverage

- Steps 1 and 6 protect public imports, messages, ordering, counts, notes, and
  exit behavior.
- Steps 2-5 establish explicit module ownership and focused tests that do not
  load unrelated concerns.
- Step 7 proves a thin CLI, explicit dependency direction, and absence of
  shallow pass-through modules.
- Steps 8-9 cover spec fit, documentation drift, all local acceptance commands,
  compile and whitespace checks, final review, and CI.

## Resolved Risks

- The validator contains large literal contract matrices. Moving them is
  mechanically risky even when behavior is unchanged; each concern move was
  kept small and independently verified.
- The direct-script/imported-module dual use needs explicit compatibility
  coverage; compatibility and fresh-interpreter isolation tests now protect
  both entry paths.
- GitHub Actions passed after the branch was pushed, satisfying the final
  external verification criterion.

## Completion

- Ticket 013 was accepted and archived after the completed implementation was
  verified and merged into `update/v2`.
