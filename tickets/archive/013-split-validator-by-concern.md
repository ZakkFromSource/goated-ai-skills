# Ticket 013: Split The Validator By Concern

## Parent Spec

`docs/specs/2026-07-25-goated-ai-skills-v2.md`

## Type

AFK

## Work State

Completed, accepted, and archived on 2026-07-26.

## What To Build

Refactor the 5,358-line validation subsystem into focused modules while
preserving the public imports used by tests and the command
`uv run python scripts/validate_skills.py`.

Keep `scripts/validate_skills.py` as a thin CLI and compatibility surface.
Separate shared types and helpers from:

- skill-package, frontmatter, link, canonical-reference, and public-boundary
  validation;
- registry validation;
- routing and end-to-end fixture validation;
- clarification and onboarding validation;
- specification/ticket, architecture, and implementation-planning validation;
- behavior-proof, review/verification, and output-communication validation;
- merge-conflict validation;
- knowledge-retrieval and source-grounded-research validation;
- Setup Scribe and Wayfinding validation; and
- result aggregation, word-budget reporting, and CLI presentation.

Use explicit dependency direction. Concern modules may depend on shared types
and parsing helpers; shared modules and the CLI must not depend back on concern
implementations through circular imports.

## Recommended First Reads

- `scripts/validate_skills.py`
- `tests/test_validate_skills.py`
- `tests/test_v2_refinement_contracts.py`
- `.github/workflows/validate.yml`
- `AGENT.md`
- `docs/agents/project-standards.md`
- `docs/high-confidence-adoption-acceptance-report.md`
- `tickets/archive/018-add-resolving-merge-conflicts.md`
- `tickets/archive/019-add-source-grounded-research.md`
- `stack/fixtures/`

## Current Characterization Baseline

Record this baseline again immediately before the first extraction:

- `scripts/validate_skills.py`: 5,358 lines;
- `tests/test_validate_skills.py`: 2,727 lines;
- test compatibility surface: 16 validation functions imported directly from
  `scripts.validate_skills`;
- implemented skills and registry entries: 37 each;
- focused high-confidence acceptance suite: 35 tests;
- full unit suite: 121 tests;
- shared policy: 1,193 words;
- report-only drift: the same three pre-existing Learning Capture `status:`
  examples;
- representative route reductions: 47.9%, 17.7%, 40.9%, and 10.1%.

The exact validator messages, finding paths, fixture counts, report-only notes,
exit codes, import surface, and context-comparison results are compatibility
behavior, not incidental output to simplify during extraction.

## Acceptance Criteria

- [x] The CLI entrypoint contains orchestration and presentation only.
- [x] Validation concerns live in named modules with explicit dependencies.
- [x] Existing imports from `scripts.validate_skills` remain compatible or are
      migrated in one reviewed change.
- [x] No validation rule, fixture requirement, output status, or exit-code
      behavior is lost.
- [x] The accepted merge-conflict and source-grounded-research validators,
      fixture counts, public-boundary checks, and focused tests retain explicit
      module ownership and equivalent behavior.
- [x] Validator output preserves concern ordering, fixture counts,
      word-budget reporting, zero human-review notes, and the three existing
      report-only drift notes unless a separately approved behavior ticket
      changes them.
- [x] Focused module tests can run without loading unrelated validation
      concerns.
- [x] The validator, full unit suite, and V1/V2 comparison pass locally and in
      CI.
- [x] The final diff contains no generated duplication or shallow
      pass-through modules.

## Expected Proof

- Characterization tests passing before the refactor.
- Focused tests for each extracted concern, including merge-conflict,
  source-grounded-research, cross-concern aggregation, and CLI compatibility.
- Fresh output from all three repository acceptance commands.
- Fresh output from the 35-test high-confidence acceptance suite.
- `python -m compileall -q scripts tests` and `git diff --check`.
- Diff review showing a thin CLI and explicit module ownership.
- Green GitHub Actions run on the branch.

## Acceptance Result

- The maintainer confirmed that all GitHub Actions checks passed for
  `ticket_013`, approved its fast-forward merge into `update/v2`, and requested
  archival.
- Fresh local closeout proof passed after the merge: validator, 147-test full
  suite, 35-test high-confidence suite, V1/V2 comparison, and `compileall`.
- The implementation and its compatibility history remain on `update/v2` at
  commit `db501a5`.

## Blocked By

- `tickets/archive/012-complete-and-accept-v2-migration.md`
- `tickets/archive/020-accept-high-confidence-adoption-batch.md`

## Extraction Order

1. Characterize the current import surface, output ordering, exit codes,
   fixture counts, and report-only notes before moving behavior.
2. Expand with shared finding/types, path, YAML-loading, and parsing modules
   while the existing CLI continues to own orchestration.
3. Extract concern modules in bounded batches with focused GREEN proof after
   every batch. Keep dependent or overlapping moves sequential.
4. Extract result aggregation and presentation only after concern ownership is
   stable.
5. Contract `scripts/validate_skills.py` to the documented compatibility
   imports, orchestration, argument parsing, presentation, and exit code.
6. Run focused, repository-wide, context-comparison, compile, diff, and CI
   proof before removing any temporary compatibility re-export.

## Implementation Route

- Use `design-codebase-architecture` to define dependency direction and avoid
  shallow pass-through modules before the extraction plan is approved.
- Use `writing-plans` to define exact module ownership and extraction order.
- Use `tdd` for characterization and compatibility proof.
- Use `code-refinement` for the behavior-preserving module split.
- Use `verification-before-completion` for the final compatibility claim.

## Scope Exclusions

- Do not add new validation behavior while moving existing rules.
- Do not redesign fixture schemas, registry semantics, or CLI output.
- Do not resolve the three report-only Learning Capture examples in this
  refactor.
- Do not combine accepted invocation-topology or domain-modeling experiments
  with the validator split.
- Do not add a general agent-evaluation runtime or Factory-only integration.
