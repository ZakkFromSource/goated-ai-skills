# Ticket 016: Minimize Diagnostic Reproductions

## Parent Spec

`docs/specs/2026-07-26-selective-upstream-skill-adoption.md`

## Type

AFK

## Work State

Completed and archived on 2026-07-26.

## What To Build

Add an explicit reproduction-minimization gate to `diagnose` after the exact
symptom is confirmed and before hypotheses are ranked.

The minimized loop should retain only load-bearing inputs, dependencies, steps,
timing conditions, and environmental facts while preserving symptom fidelity
and existing safety boundaries.

## Recommended First Reads

- `docs/specs/2026-07-26-selective-upstream-skill-adoption.md` — R2 and AC2.
- `skills/engineering/diagnose/SKILL.md` — current loop and root-cause route.
- `skills/engineering/diagnose/references/pressure-scenarios.md` — current
  shortcuts and completion checks.
- `stack/fixtures/end-to-end/bug-report-to-root-cause-fix.yaml` — integrated
  diagnosis route.

## Relevant Source Links

- `skills/engineering/diagnose/references/root-cause-tracing.md`
- `skills/engineering/diagnose/references/condition-based-waiting.md`
- `scripts/validate_skills.py`
- `tests/test_validate_skills.py`

## Acceptance Criteria

- [x] A confirmed reproduction is minimized before broad hypothesis ranking
      unless safety or fidelity makes minimization inappropriate.
- [x] Every remaining element is described as load-bearing or the residual
      uncertainty is recorded.
- [x] Intermittent, production-only, destructive, and human-in-the-loop cases
      retain safe lower-confidence fallbacks.
- [x] The workflow does not imply that the existing fast, deterministic,
      red-capable loop was previously absent.
- [x] A focused fixture catches premature hypothesis work against a large,
      reducible reproduction.

## Expected Proof

- Focused fixture and validator test for minimization ordering.
- Manual pressure-scenario review for unsafe and intermittent cases.
- Fresh repository acceptance commands required by the parent spec.

## Blocked By

None.

## User Stories Addressed

- As a developer diagnosing a difficult bug, I can isolate the smallest
  load-bearing reproduction before spending time on broad theories.

## Implementation Route

- Use `writing-plans`, then TDD or equivalent fixture-first proof.
- Use `doc-sync` if diagnosis guidance outside the skill changes.
- Use `verification-before-completion` for the final contract claim.

## Scope Exclusions

- Do not rewrite the diagnosis workflow wholesale.
- Do not turn diagnosis into fix implementation.
- Do not weaken production, privacy, or destructive-reproduction controls.

## Implementation Proof

- `diagnose` now minimizes a confirmed reproduction before broad hypothesis
  ranking while preserving the existing fast, red-capable feedback loop.
- The workflow removes or simplifies one element at a time, requires a
  load-bearing reason or residual-uncertainty record for every retained input,
  dependency, step, timing condition, and environmental fact, and preserves
  symptom fidelity.
- Intermittent, production-only, destructive, and human-in-the-loop cases use
  a bounded proxy or retained confirmed loop with an explicit lower-confidence
  result instead of weakening safety.
- The end-to-end bug fixture models a large reducible reproduction, required
  ordering, retained-element accounting, fidelity, and all four safe fallback
  classes.
- Focused RED showed the validator previously accepted hypothesis ranking
  before minimization. GREEN passes the new ordering regression and all four
  end-to-end fixture tests.
- `uv run python scripts/validate_skills.py` passed 35 implemented skills, 35
  registry entries, every fixture family, and zero human-review notes.
- `uv run python -m unittest discover -s tests -v` passed all 98 tests.
- `uv run python scripts/compare_v1_v2_context.py` confirmed all four
  representative routes retain the required 10% reduction.
- Manual pressure-scenario, standalone-package, public-boundary, diff, and
  whitespace review found no ticket-scoped blocker. Three pre-existing
  Learning Capture schema examples remain report-only drift.
