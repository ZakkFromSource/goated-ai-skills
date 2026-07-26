# Setup Scribe Implementation Plan

## Plan Target

- Ticket: `tickets/archive/014-add-setup-scribe.md`
- Parent spec: `docs/specs/2026-07-26-setup-scribe.md`
- Mode: durable tracked plan because the slice spans a skill package, integrated
  routing, fixture validation, tests, and public documentation.
- Execution route: TDD for fixture and routing behavior, followed by skill
  forward evaluation, security review, standards/spec review, documentation
  sync, and full verification.

## Source Inspected

- Maintainer and product contracts: `AGENT.md`, `CONTEXT.md`,
  `docs/agents/context-matrix.md`, and `docs/agents/project-standards.md`.
- Approved delivery artifacts: the ticket and parent spec above.
- Nearby skill patterns: `skills/productivity/learning-capture/SKILL.md`,
  `skills/engineering/doc-sync/SKILL.md`,
  `skills/engineering/documentation-writer/SKILL.md`, and
  `skills/agent-workflows/handoff/SKILL.md`.
- Integrated surfaces: `stack/AGENTS.md`, `stack/goated-stack.yaml`,
  `stack/schemas/stack-registry.schema.json`, and representative fixtures.
- Proof surfaces: `scripts/validate_skills.py`,
  `tests/test_validate_skills.py`, `.github/workflows/validate.yml`, and the
  commands recorded in `docs/agents/project-standards.md`.
- Public guidance: `README.md`, `skills/README.md`,
  `skills/productivity/README.md`, `docs/install.md`, and
  `docs/how-to-use.md`.

## Slice Shape And Interface Focus

The vertical slice adds one installable `setup-scribe` workflow and proves its
observable contract through focused YAML fixtures consumed by the repository's
public validator interface. The integrated registry and shared policy expose a
conditional `reproducibility-impact` route without moving specialist procedure
into shared instructions.

## Assumptions

- Ticket 013 is ready but not in progress; Ticket 014 may add focused validator
  behavior without performing Ticket 013's refactor.
- No registry schema change is needed because the existing signal and skill
  entry shapes already represent Scribe.
- The generic Codex skill initializer may be used only as a temporary
  scaffold. The source repository's lean schema and prohibition on
  `agents/openai.yaml` govern the tracked package.

## Stop Conditions

- Pause if current source contradicts an accepted Scribe product decision.
- Pause if fixture coverage requires Ticket 013's validator refactor or a new
  dependency rather than a focused extension.
- Pause before destructive, credentialed, external, machine-wide, generated
  automation execution, publication, or any scope beyond Ticket 014.
- Do not claim completion if required checks repeatedly fail or forward
  evaluation cannot produce inspectable evidence.

## Steps

1. Add failing tests in `tests/test_validate_skills.py` for the focused
   `setup-scribe` fixture validator: required scenarios, evidence-state
   integrity, secret rejection, source ownership, automation creation versus
   execution, and compact no-impact routing. Run the focused unittest class and
   confirm failure because the validator interface and fixtures do not exist.
2. Add `stack/fixtures/setup-scribe/` with a concise README and eight scenarios:
   live capture, mixed-evidence backfill, drift audit, Bash plus native-helper
   automation, secret rejection, source-of-truth reuse, personal-setting
   exclusion, and no reproducibility impact. Extend
   `scripts/validate_skills.py` only enough to validate their stable observable
   contract and report their count. Run the focused tests to GREEN.
3. Add `skills/productivity/setup-scribe/SKILL.md` plus
   `references/setup-recipe-template.md`,
   `references/automation-and-safety.md`, and
   `references/pressure-scenarios.md`. Keep the main skill below the soft
   300-line budget, link every reference with a read condition, add no
   executable helper, and preserve standalone behavior.
4. Register `reproducibility-impact` and `setup-scribe` in
   `stack/goated-stack.yaml`. Update `stack/AGENTS.md` with only the
   cross-skill conditional-gate rule while retaining its 800–1,200 word budget.
   Run registry and focused fixture tests after these changes.
5. Synchronize `CONTEXT.md`, `README.md`,
   `skills/productivity/README.md`, `docs/how-to-use.md`,
   `docs/agents/context-matrix.md`, and
   `docs/agents/project-standards.md` where the implemented skill, terminology,
   route, fixture surface, or validation commands changed. Leave
   `docs/install.md` unchanged unless diff review identifies an install fact
   that actually drifted.
6. Forward-test the raw setup task without the skill for RED and with the skill
   for GREEN using independent subagents. Inspect their outputs, revise only
   for observed failure modes, and rerun focused validation after revisions.
7. Review the final diff for secret handling, unsafe execution, permissions,
   machine-wide settings, external-service actions, public safety, accepted
   scope, ownership boundaries, schema conformance, links, and documentation
   drift.
8. Run `uv run python scripts/validate_skills.py`,
   `uv run python -m unittest discover -s tests -v`, and
   `uv run python scripts/compare_v1_v2_context.py`; then perform targeted
   `rg`, whitespace, line-budget, Markdown, diff, and `git status --short`
   checks. Report failures, skips, warnings, and residual risk exactly.

## Acceptance Coverage

Every ticket criterion is covered by the skill and references in Steps 3–4,
the eight behavioral fixtures and TDD in Steps 1–2, synchronized catalog and
operator docs in Step 5, live RED/GREEN evaluation in Step 6, and the
security/spec/docs/verification gates in Steps 7–8.

## Residual Risk

- Live forward evaluation is probabilistic; fixture validation and manual
  source review remain the deterministic contract.
- The repository has no Markdown formatter or linter, so Markdown quality and
  link wording require manual inspection in addition to validator checks.
