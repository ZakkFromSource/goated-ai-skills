# Ticket 016: Minimize Diagnostic Reproductions

## Parent Spec

`docs/specs/2026-07-26-selective-upstream-skill-adoption.md`

## Type

AFK

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

- [ ] A confirmed reproduction is minimized before broad hypothesis ranking
      unless safety or fidelity makes minimization inappropriate.
- [ ] Every remaining element is described as load-bearing or the residual
      uncertainty is recorded.
- [ ] Intermittent, production-only, destructive, and human-in-the-loop cases
      retain safe lower-confidence fallbacks.
- [ ] The workflow does not imply that the existing fast, deterministic,
      red-capable loop was previously absent.
- [ ] A focused fixture catches premature hypothesis work against a large,
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
