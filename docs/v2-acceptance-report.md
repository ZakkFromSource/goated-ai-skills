# GOATED AI Skills V2 Acceptance Report

Date: 2026-07-25

Status: Accepted by the maintainer on 2026-07-25.

## Scope

This report closes
[Ticket 012](../tickets/archive/012-complete-and-accept-v2-migration.md). It covers the
34-skill catalog, shared policy, registry and aliases, route signals, focused
and end-to-end fixtures, V1/V2 instruction-size comparison, public
documentation, and historical-boundary checks.

After reviewing the four residual risks individually, the maintainer explicitly
accepted V2 as it currently stands.

## Automated Proof

Commands:

```text
uv run python scripts/validate_skills.py
uv run python -m unittest discover -s tests -v
uv run python scripts/compare_v1_v2_context.py
```

Fresh acceptance results:

- validator: 34 implemented skills and 34 registry entries passed;
- fixture validation: 74 focused scenarios plus four end-to-end scenarios;
- unit tests: 79 passed;
- shared policy: 1,190 words, within the 800–1,200 target;
- registry schema, canonical paths, aliases, route signals, category/path
  consistency, links, public-boundary scans, and canonical architecture
  references passed;
- report-only legacy example drift: three `status:` examples, all in historical
  issue or learning-note content rather than implemented-skill frontmatter.

These commands were run immediately before the maintainer's decision and again
after the acceptance-status and ticket-archive edits.

## Representative Instruction Comparison

Method:

- V1 skill text is read from the preserved `v1-baseline` Git tag.
- V2 route membership comes from the four end-to-end fixtures.
- Counts use the validator's whitespace-word convention.
- Route-specific skill text is the acceptance comparison. The persistent
  1,190-word shared policy is reported separately so its cost is visible.
- A route is materially smaller when route-specific text is at least 10% below
  its V1 equivalent.

| Scenario | V1 route words | V2 route words | Reduction | V2 + shared policy |
| --- | ---: | ---: | ---: | ---: |
| Bug report to root-cause fix | 12,691 | 6,372 | 49.8% | 7,562 |
| Existing codebase to proportional onboarding | 7,387 | 6,068 | 17.9% | 7,258 |
| Feature brief to verified change | 15,611 | 9,190 | 41.1% | 10,380 |
| Product idea to vertical slice | 6,845 | 6,025 | 12.0% | 7,215 |

All four route-specific comparisons meet the target. The product-planning
scenario is the narrowest margin, and adding persistent shared policy makes its
total integrated instruction volume larger than V1. That transparent
distinction is residual context-cost risk, not hidden from acceptance.

## Catalog And Boilerplate Review

Every implemented skill uses discovery-only frontmatter plus semantic body
sections for dependencies, specialist procedure, outputs, delegation when
useful, guardrails, and local references. No semantic-anatomy exception is
required.

The catalog compression pass removed repeated multi-paragraph controller
status handling from specialist skills. The shared policy owns universal
orchestration, privacy, evidence, approval, and consolidated-closeout behavior;
skills retain only task-specific delegation boundaries and compact standalone
safety.

Thirteen discipline-heavy skills remain above the review-only 1,500-word
decomposition threshold. They retain task-specific workflows, output schemas,
and guardrails needed for standalone use. This is a visible soft-budget review
item, not a validator failure. Representative route comparisons are the release
acceptance measure.

## Behavioral Review

The four end-to-end fixtures cover:

1. feature brief to planned, implemented, reviewed, and verified change;
2. bug report to diagnosis, root-cause fix, regression proof, and review;
3. product idea to scoped spec, architecture, and vertical slice;
4. existing codebase to proportional onboarding.

Focused fixtures cover tiny-task bypass, conflicting route conditions,
checkpoint escalation, restricted data, external-changing actions, approval
reuse, evidence invalidation, conditional refinement, individual-skill
fallback, Wayfinder selection/rejection and state transitions, knowledge
retrieval, proportional planning, review, verification, and concise closeout.

The fixtures and tests validate deterministic structure and prohibited
behavior. They have been manually compared with the V2 spec and relevant skill
contracts. No live multi-host model run or general model benchmark was
performed; those remain outside V2 scope.

## Documentation And Boundary Review

Reviewed surfaces:

- `AGENT.md`, `CONTEXT.md`, root `README.md`;
- `docs/install.md`, `docs/how-to-use.md`, this migration guide;
- `skills/README.md` and all category indexes;
- `docs/agents/context-matrix.md` and
  `docs/agents/project-standards.md`;
- ADR 0002 and the ADR index;
- V2 spec, ticket order, Tickets 001–012, registry, schema, templates, and
  fixtures.

Historical V1 specs, archived issues, and the `v1-baseline` tag remain intact.
No Factory runtime, installer automation, dedicated evaluation skill, or model
benchmarking platform entered V2 scope.

## Accepted Residual Risk

- Host frameworks may load persistent policy and specialist text differently;
  the comparison method is portable and reproducible but not a host tokenizer
  benchmark.
- Thirteen skills remain above the review-only decomposition threshold.
- Behavioral fixtures are deterministic contracts plus manual review, not live
  multi-model evaluations.
- The report-only legacy `status:` examples remain intentional historical or
  note-schema content.

The maintainer accepted these results and residual risks on 2026-07-25. Future
Factory work may add runtime routing, harness behavior, agent orchestration,
host-aware context management, and live evaluation without expanding the
portable V2 core retroactively.

## Post-Acceptance Comparative-Evaluation Refinement

A follow-up V1/V2 comparative evaluation confirmed that V2 fixed the majority
of the original audit findings and identified a small consistency pass. The
resulting refinement:

- made clarification activation need-based rather than category-mandatory;
- made work-envelope population lazy beyond goal, scope, action reach, and
  next action;
- aligned TDD and delegated-development results with the integrated delta and
  consolidated-closeout model;
- allowed existing envelope consent to satisfy Wayfinder's five-part chart
  approval when coverage is already sufficient;
- normalized active architecture, handoff, TDD, and operator prose to specs or
  legacy PRDs and tickets or remote issues;
- added contents navigation to the 15 long references that lacked it (the
  evaluation counted 16, but one already had a contents section);
- added SHA-pinned GitHub Actions validation with full history for the
  `v1-baseline` comparison; and
- captured the larger validator module split as
  `tickets/013-split-validator-by-concern.md`.

The post-refinement suite contains 87 passing tests. The validator still
accepts all 34 skills and 78 fixtures, the shared policy remains within its
800-1,200-word target, and all representative V2 routes retain at least a 10%
route-specific reduction from V1.
