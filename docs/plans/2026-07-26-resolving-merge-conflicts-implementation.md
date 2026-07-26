# Resolving Merge Conflicts Implementation Plan

## Plan Target

- Ticket: `tickets/018-add-resolving-merge-conflicts.md`
- Parent spec:
  `docs/specs/2026-07-26-selective-upstream-skill-adoption.md`, requirement R4
  and acceptance criterion AC4.
- Mode: durable tracked plan because the slice spans a skill package, pressure
  scenarios, integrated routing, fixture validation, tests, and public docs.
- Execution route: scenario-first TDD for the fixture contract, followed by
  skill forward evaluation, standards/spec review, documentation sync, and full
  verification.

## Source Inspected

- Maintainer and product contracts: `AGENT.md`, `CONTEXT.md`, and
  `stack/AGENTS.md`.
- Approved delivery artifacts: the ticket and parent spec above.
- Authoring and proof workflows:
  `skills/agent-workflows/framework-agnostic-skill-creator/SKILL.md`, its
  source-package-audit and skill-evaluation references,
  `skills/engineering/writing-plans/SKILL.md`, and
  `skills/engineering/tdd/SKILL.md`.
- Neighboring skill patterns:
  `skills/engineering/receiving-code-review/SKILL.md` and
  `skills/engineering/verification-before-completion/SKILL.md`.
- Integrated and proof surfaces: `stack/goated-stack.yaml`,
  `stack/schemas/stack-registry.schema.json`, representative fixture groups,
  `scripts/validate_skills.py`, and `tests/test_validate_skills.py`.
- Public guidance: `README.md`, `skills/engineering/README.md`, and
  `docs/how-to-use.md`.
- Upstream source package:
  `skills/engineering/resolving-merge-conflicts/SKILL.md` and
  `agents/openai.yaml` in `mattpocock/skills`.

## Port Manifest And Decisions

- The upstream `SKILL.md` contributes the compact sequence of state inspection,
  primary-intent tracing, intent-preserving resolution, and project-check
  discovery.
- The upstream `agents/openai.yaml` contains display metadata only; it does not
  carry workflow behavior and is not part of GOATED's tracked skill shape.
- The upstream requirements to always resolve, never abort, stage everything,
  commit, and continue a rebase conflict with the ticket and shared approval
  policy. The GOATED port replaces them with evidence, semantic-decision, safe
  abort, and lifecycle-authorization gates.
- No other first-party files exist in the upstream package. Generated,
  vendored, binary, and unrelated neighboring repository files were excluded.

## Slice Shape And Interface Focus

The vertical slice adds one installable `resolving-merge-conflicts` workflow
and proves its observable contract through five focused YAML scenarios consumed
by the repository validator. The registry exposes independent routing without
moving Git-resolution procedure into shared policy.

## Assumptions

- The existing registry schema can represent the skill without a schema change.
- A dedicated `merge-conflicts` fixture group is clearer than mixing lifecycle
  authorization scenarios into generic review fixtures.
- Git operation detection remains framework-neutral prose; this ticket does not
  add a Git wrapper, hook, installer, or executable helper.
- The source attribution belongs in the skill's pressure-scenario reference or
  public acknowledgements only where it adds useful provenance.

## Stop Conditions

- Pause if a scenario exposes a product choice not settled by R4, AC4, or the
  ticket.
- Pause if fixture coverage requires the unrelated validator refactor mentioned
  in Ticket 013 rather than a focused extension.
- Stop before staging, committing, continuing, aborting, pushing, protected
  branch mutation, or any destructive Git action; implementation of this
  source-repo ticket authorizes none of those lifecycle actions.
- Do not claim completion if required checks repeatedly fail or forward
  evaluation cannot produce inspectable evidence.

## Steps

1. Add failing tests in `tests/test_validate_skills.py` for a focused
   `validate_merge_conflict_fixtures` interface. Cover compatible intent,
   incompatible intent, insufficient evidence, wrong or unsafe operation, and
   authorized continuation. Run the focused unittest class and confirm RED
   because the validator and fixtures do not exist.
2. Add `stack/fixtures/merge-conflicts/` with a concise README and the five
   scenarios. Extend `scripts/validate_skills.py` only enough to validate their
   stable observable contract, require every scenario, include the validator in
   repository acceptance, and report its fixture count. Run focused tests to
   GREEN after each scenario contract is introduced.
3. Add `skills/engineering/resolving-merge-conflicts/SKILL.md` and
   `references/pressure-scenarios.md`. Keep the main skill under the soft
   300-line limit, link the reference with an explicit read condition, preserve
   standalone behavior, and distinguish analysis or file edits from Git
   lifecycle authorization.
4. Register `resolving-merge-conflicts` in `stack/goated-stack.yaml` with the
   existing metadata shape. Run registry and focused fixture tests.
5. Synchronize `README.md`, `skills/engineering/README.md`, and
   `docs/how-to-use.md` for discovery, purpose, inputs, outputs, lifecycle
   boundaries, and integrated versus standalone behavior.
6. Run independent RED and GREEN pressure evaluation against realistic
   compatible-intent, incompatible-intent, under-evidenced, unsafe-operation,
   and continuation scenarios. Inspect outputs, revise only for observed
   failure modes, and rerun focused validation.
7. Review the final diff against R4, AC4, every ticket criterion, source-repo
   standards, public safety, lifecycle authorization, link integrity,
   standalone behavior, registry conformance, and documentation drift.
8. Run `uv run python scripts/validate_skills.py`,
   `uv run python -m unittest discover -s tests -v`, and
   `uv run python scripts/compare_v1_v2_context.py`; then inspect line budgets,
   whitespace, the final diff, and `git status --short`. Report failures,
   warnings, skipped checks, and residual risk exactly.

## Acceptance Coverage

The skill and reference in Step 3 cover operation detection, evidence tracing,
intent reconciliation, abort, authorization, and scoped checks. Steps 1-2 and
6 pressure-test standalone and integrated outcomes. Steps 4-5 cover registry,
routing metadata, and public guidance. Steps 7-8 provide the parent-spec
acceptance and closeout proof.

## Residual Risk

- Live forward evaluation is probabilistic; deterministic fixture validation
  and manual source review remain the stable contract.
- The repository has no Markdown formatter or linter, so Markdown quality
  requires manual inspection in addition to link validation.
