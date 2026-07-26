# Source-Grounded Research Implementation Plan

## Plan Target

- Ticket: `tickets/019-add-source-grounded-research.md`
- Parent spec:
  `docs/specs/2026-07-26-selective-upstream-skill-adoption.md`, requirement R5
  and acceptance criterion AC5.
- Mode: durable tracked plan because the slice spans a skill package, routing,
  six fixture contracts, validator behavior, tests, and public docs.
- Execution route: scenario-first TDD for the fixture contract, followed by
  question-only forward evaluation, standards/spec review, documentation sync,
  and full verification.

## Source Inspected

- Maintainer and product contracts: `AGENT.md`, `CONTEXT.md`,
  `docs/agents/context-matrix.md`, `docs/agents/project-standards.md`, and
  `stack/AGENTS.md`.
- Approved delivery artifacts: the ticket and parent spec above.
- Authoring and proof workflows:
  `skills/agent-workflows/framework-agnostic-skill-creator/SKILL.md`, its skill
  evaluation reference, `skills/engineering/writing-plans/SKILL.md`, and
  `skills/engineering/tdd/SKILL.md`.
- Neighboring ownership:
  `skills/productivity/knowledge-retrieval/SKILL.md`,
  `skills/productivity/learning-capture/SKILL.md`,
  `skills/engineering/doc-sync/SKILL.md`, and
  `skills/engineering/doc-sync/references/external-docs-lookup-notes.md`.
- Shared evidence and integrated surfaces: `stack/templates/evidence-entry.md`,
  `stack/goated-stack.yaml`, `stack/schemas/stack-registry.schema.json`,
  representative focused fixtures, `scripts/validate_skills.py`, and
  `tests/test_validate_skills.py`.
- Public guidance: `README.md`, `skills/engineering/README.md`, and
  `docs/how-to-use.md`.
- Upstream inspiration:
  `https://github.com/mattpocock/skills/blob/main/skills/engineering/research/SKILL.md`.

## Port Manifest And Decisions

- The upstream source contributes primary-source preference, claim citations,
  and reuse of an existing research-note convention.
- Mandatory background-agent delegation and mandatory Markdown output do not
  fit this ticket. GOATED will make delegation optional, retain an equivalent
  sequential path, and treat read-only inline output as complete.
- The specialist will frame the exact question, decision use, applicable
  scope, and currency need before broad collection; build a question-specific
  source hierarchy; and keep findings, inference, disagreement, missing
  evidence, and unresolved uncertainty distinct.
- Durable capture is a separately selected and authorized branch. It reuses a
  project-owned research convention or the existing external-doc lookup-note
  convention instead of creating duplicate truth.
- No browser, MCP server, crawler, cache, database, refresh daemon, or
  background agent becomes a hard dependency.

## Slice Shape And Interface Focus

The vertical slice adds one installable `source-grounded-research` workflow and
proves its portable contract through six YAML scenarios consumed by a dedicated
validator interface. The registry and router expose external investigation
without moving specialist procedure into shared policy or weakening the local
read-only boundary of `knowledge-retrieval`.

## Assumptions

- The existing registry schema and route signals can represent the skill
  without schema changes.
- `external-research` is the clearest registry workflow role.
- The six required scenarios belong in one dedicated
  `stack/fixtures/source-grounded-research/` group.
- Copyright, restricted-source, credential, and private-data behavior needs
  explicit skill guidance, deterministic fixture expectations, and manual
  review; fixtures alone cannot prove live retrieval safety.

## Stop Conditions

- Pause if implementation requires a new retrieval tool, credential, restricted
  source, schema change, or product choice not settled by R5, AC5, or the
  ticket.
- Pause if fixture coverage requires Ticket 013's unrelated validator refactor
  rather than a narrow compatible extension.
- Stop before durable capture when the destination, convention, sensitivity,
  or write authority is unresolved.
- Do not claim behavioral proof if question-only evaluation cannot produce
  inspectable sources and a claim-scoped evidence delta.
- Do not claim completion if required checks repeatedly fail.

## Steps

1. Add a failing focused test in `tests/test_validate_skills.py` for a new
   `validate_source_grounded_research_fixtures` public seam. Confirm RED because
   the validator and fixtures do not exist.
2. Add `stack/fixtures/source-grounded-research/README.md` and the six required
   scenarios: stale source, conflicting sources, no primary source, read-only
   output, durable capture, and no-delegation fallback. Extend
   `scripts/validate_skills.py` narrowly to validate their stable observable
   contract, require claim-scoped evidence fields and traceable freshness,
   include the group in repository acceptance, and report its fixture count.
   Add one mutation test at a time and run the focused class to GREEN after
   each behavior.
3. Add `skills/engineering/source-grounded-research/SKILL.md` and
   `references/pressure-scenarios.md`. Keep the main skill under the soft
   300-line limit, link the reference with an explicit read condition, preserve
   standalone behavior, and make copyright, privacy, credentials, restricted
   sources, and optional durable capture explicit.
4. Register `source-grounded-research` in `stack/goated-stack.yaml` and add the
   distinct external-research gate to
   `skills/agent-workflows/using-goated-ai-skills/SKILL.md`. Name the new route
   from `knowledge-retrieval` without making either skill depend on the other.
5. Synchronize `README.md`, `skills/engineering/README.md`,
   `docs/how-to-use.md`, `docs/agents/context-matrix.md`, and
   `docs/agents/project-standards.md` for discovery, route boundaries, fixture
   coverage, and acceptance commands. Change `stack/AGENTS.md` only if the
   specialist split reveals a universal shared-policy gap.
6. Run a question-only public research evaluation without leaking the desired
   answer. Inspect the source hierarchy, citations, dates, claim scopes,
   findings versus inference, disagreement or missing-evidence handling,
   copyright restraint, inline output, and evidence delta. Revise only for
   observed failure modes and rerun focused validation.
7. Review the final diff against R5, AC5, every ticket criterion, repository
   standards, public safety, standalone behavior, registry conformance,
   copyright boundaries, and documentation drift.
8. Run `uv run python scripts/validate_skills.py`,
   `uv run python -m unittest discover -s tests -v`,
   `uv run python scripts/compare_v1_v2_context.py`, and `git diff --check`;
   then inspect line budgets, the final diff, and `git status --short`. Report
   failures, warnings, skipped checks, and residual risk exactly.

## Acceptance Coverage

Steps 2-3 cover question framing, source hierarchy, provenance, freshness,
finding classification, optional capture, delegation fallback, and safety.
Steps 4-5 cover registry, routing, local-retrieval separation, and public
guidance. Step 6 supplies behavioral evidence beyond static fixtures.
Steps 7-8 provide standards, spec, documentation, public-boundary, and
repository acceptance proof.

## Residual Risk

- Live forward evaluation is probabilistic; deterministic fixture validation
  and manual source review remain the stable portable contract.
- The repository has no Markdown formatter or linter, so Markdown quality
  requires manual inspection in addition to validator link checks.
