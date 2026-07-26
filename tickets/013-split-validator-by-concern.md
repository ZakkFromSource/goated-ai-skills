# Ticket 013: Split The Validator By Concern

## Parent Spec

`docs/specs/2026-07-25-goated-ai-skills-v2.md`

## Type

AFK

## Work State

Ready after the post-evaluation semantic consistency pass.

## What To Build

Refactor the roughly 4,400-line validation subsystem into focused modules while
preserving the public imports used by tests and the command
`uv run python scripts/validate_skills.py`.

Keep `scripts/validate_skills.py` as a thin CLI and compatibility surface.
Separate shared types and helpers from registry, routing, clarification,
onboarding, planning, proof, review, output communication, knowledge,
Wayfinder, and public-boundary validation.

## Recommended First Reads

- `scripts/validate_skills.py`
- `tests/test_validate_skills.py`
- `tests/test_v2_refinement_contracts.py`
- `.github/workflows/validate.yml`
- `AGENT.md`
- `docs/agents/project-standards.md`

## Acceptance Criteria

- [ ] The CLI entrypoint contains orchestration and presentation only.
- [ ] Validation concerns live in named modules with explicit dependencies.
- [ ] Existing imports from `scripts.validate_skills` remain compatible or are
      migrated in one reviewed change.
- [ ] No validation rule, fixture requirement, output status, or exit-code
      behavior is lost.
- [ ] Focused module tests can run without loading unrelated validation
      concerns.
- [ ] The validator, full unit suite, and V1/V2 comparison pass locally and in
      CI.
- [ ] The final diff contains no generated duplication or shallow
      pass-through modules.

## Expected Proof

- Characterization tests passing before the refactor.
- Focused tests for each extracted concern.
- Fresh output from all three repository acceptance commands.
- Diff review showing a thin CLI and explicit module ownership.
- Green GitHub Actions run on the branch.

## Blocked By

- `tickets/archive/012-complete-and-accept-v2-migration.md`

## Implementation Route

- Use `writing-plans` to define exact module ownership and extraction order.
- Use `tdd` for characterization and compatibility proof.
- Use `code-refinement` for the behavior-preserving module split.
- Use `verification-before-completion` for the final compatibility claim.

## Scope Exclusions

- Do not add new validation behavior while moving existing rules.
- Do not redesign fixture schemas, registry semantics, or CLI output.
- Do not add a general agent-evaluation runtime or Factory-only integration.
