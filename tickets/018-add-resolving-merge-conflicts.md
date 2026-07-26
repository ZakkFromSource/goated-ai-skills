# Ticket 018: Add Resolving Merge Conflicts

## Parent Spec

`docs/specs/2026-07-26-selective-upstream-skill-adoption.md`

## Type

AFK

## What To Build

Add `resolving-merge-conflicts` as a compact engineering skill for
intent-preserving resolution of in-progress merges, rebases, cherry-picks, and
reverts.

Deliver the self-contained skill, pressure scenarios, registry and routing
metadata, focused fixtures, validation coverage, and synchronized public
guidance as one vertical slice.

## Recommended First Reads

- `AGENT.md` — Git, approval, skill, and public-boundary rules.
- `docs/specs/2026-07-26-selective-upstream-skill-adoption.md` — R4 and AC4.
- `skills/agent-workflows/framework-agnostic-skill-creator/SKILL.md` — creation
  workflow.
- `stack/AGENTS.md` — approvals, destructive actions, proof, and closeout.
- `skills/engineering/receiving-code-review/SKILL.md` and
  `skills/engineering/verification-before-completion/SKILL.md` — neighboring
  review and proof boundaries.

## Relevant Source Links

- `stack/goated-stack.yaml`
- `stack/schemas/stack-registry.schema.json`
- `skills/engineering/README.md`
- `README.md`
- `docs/how-to-use.md`
- `https://github.com/mattpocock/skills/blob/main/skills/engineering/resolving-merge-conflicts/SKILL.md`

## Acceptance Criteria

- [ ] The skill detects the active Git operation and exact conflict scope.
- [ ] It traces both sides to commits, issues, PRs, tests, docs, or other
      primary intent evidence.
- [ ] Compatible intents are preserved without inventing unrelated behavior.
- [ ] Incompatible intents become an explicit semantic tradeoff or user
      decision.
- [ ] Safe abort is allowed for a wrong, unsafe, unauthorized, or
      under-evidenced operation.
- [ ] Loading the skill does not independently authorize stage, commit,
      continue, abort, push, or protected-branch mutation.
- [ ] Project checks are discovered and scoped to the resolution.
- [ ] Standalone and integrated behavior are pressure-tested.

## Expected Proof

- RED/GREEN scenarios for compatible intent, incompatible intent, insufficient
  evidence, wrong operation, and authorized continuation.
- Focused registry, fixture, link, and public-boundary validation.
- Fresh repository acceptance commands required by the parent spec.

## Blocked By

- `tickets/archive/015-sharpen-skill-authoring-discipline.md`

Ticket 013 is not a functional dependency. Sequence overlapping validator
edits if its refactor is in progress.

## User Stories Addressed

- As a developer resolving a conflict, I can preserve the reasons behind both
  changes instead of mechanically choosing ours or theirs.
- As a maintainer, I retain control over semantic decisions and Git lifecycle
  actions.

## Implementation Route

- Use `framework-agnostic-skill-creator`, `writing-plans`, and scenario-first
  TDD or equivalent proof.
- Use `code-security-review` only if unsafe execution, credentials, hooks, or
  protected-branch behavior enters scope.
- Use `standards-and-spec-review`, `doc-sync`, and
  `verification-before-completion` before closeout.

## Scope Exclusions

- Do not require completion at any cost or prohibit safe abort.
- Do not auto-commit, push, publish, or make product decisions.
- Do not add a Git wrapper, hook, installer, or framework-specific runtime.
