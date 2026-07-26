# High-Confidence Adoption Batch Acceptance Report

Date: 2026-07-26

Status: Accepted with residual risk by the maintainer on 2026-07-26.

## Scope

This report supports
[Ticket 020](../tickets/archive/020-accept-high-confidence-adoption-batch.md) and the
high-confidence phase of the
[selective upstream skill-adoption spec](specs/2026-07-26-selective-upstream-skill-adoption.md).
It reviews the committed range from parent-spec commit `aaac926` through
`bb3615d`, covering the implementations and recorded proof for archived
Tickets 015 through 019.

The invocation-topology and active-domain-modeling experiments remain outside
this acceptance decision. Neither experiment is represented as a shipped
capability or production registry contract.

## Acceptance-Criteria Evidence

| Criterion | Fresh evidence | Result |
| --- | --- | --- |
| AC1: skill-authoring discipline | `framework-agnostic-skill-creator` prices independent invocation and context visibility, requires observable phase completion, and links to evaluation checks for no-op pruning, singular ownership, branch disclosure, sequence pressure, positive steering, and useful leading concepts. Focused `SkillAuthoringDisciplineTests` pass. | Satisfied |
| AC2: minimized diagnosis reproduction | `diagnose` minimizes a confirmed reproduction before broad hypothesis ranking, accounts for retained load-bearing elements, preserves symptom fidelity, and retains bounded lower-confidence fallbacks for intermittent, production-only, destructive, and human-in-the-loop cases. The end-to-end bug fixture and focused ordering test pass. | Satisfied |
| AC3: wide-refactor slicing | `spec-to-tickets` keeps vertical slices as the default and uses expand, evidence-bounded migrate batches, and contract only for qualifying wide mechanical refactors. Planning fixtures and focused tests cover blockers, blast-radius evidence, contract fan-in, the integration-branch exception, and the ready frontier. | Satisfied |
| AC4: merge-conflict specialist | `resolving-merge-conflicts` is a 197-line, 1,297-word standalone package registered with the specialist role `conflict-resolution`. Five fixtures cover compatible intent, incompatible intent, insufficient evidence, a wrong or unsafe operation, and authorized continuation without granting lifecycle authority. Public docs and focused tests pass. | Satisfied |
| AC5: external-research specialist | `source-grounded-research` is a 196-line, 1,314-word standalone package registered with the specialist role `external-research`. Six fixtures cover stale sources, conflicting sources, missing primary sources, read-only output, optional durable capture, and no-delegation fallback. Router, local-retrieval boundaries, public docs, and focused tests pass. | Satisfied |
| AC10: repository and manual proof | Repository validation, the full unit suite, V1/V2 context comparison, diff checks, standalone-package inspection, changed-Markdown link review, public-boundary scans, and experiment-boundary review pass. Exact command results and limitations are recorded below. | Satisfied |
| AC11: Ticket 013 isolation | The batch adds behavior-specific validation to the current public validator surface but does not implement Ticket 013's module split. No Ticket 013 artifact or validator module extraction appears in the reviewed range. | Satisfied |

Archived Tickets 015 through 019 retain their focused RED/GREEN or forward
evaluation records. This acceptance pass freshly confirms the integrated GREEN
state; it does not claim that historical RED runs or Ticket 019's public
forward evaluation were reproduced from the current tree.

## Automated Proof

Commands:

```text
uv run python -m unittest tests.test_v2_refinement_contracts.SkillAuthoringDisciplineTests tests.test_validate_skills.PlanningFixtureValidationTests tests.test_validate_skills.MergeConflictFixtureValidationTests tests.test_validate_skills.SourceGroundedResearchFixtureValidationTests tests.test_validate_skills.EndToEndFixtureValidationTests -v
uv run python scripts/validate_skills.py
uv run python -m unittest discover -s tests -v
uv run python scripts/compare_v1_v2_context.py
uv run python -m compileall -q scripts tests
git diff --check aaac926..HEAD
git diff --check
```

Fresh results before the maintainer decision and again after the decision,
lifecycle updates, and Ticket 013 refresh:

- validator: 37 implemented skills and 37 registry entries passed;
- merge-conflict and source-grounded-research fixture families passed;
- human-review notes: zero;
- focused acceptance suite: 35 tests passed;
- unit suite: 121 tests passed;
- all four representative V2 routes retained at least a 10% route-specific
  reduction from V1;
- shared policy: 1,193 words, within its 800–1,200-word target;
- Python compilation completed without errors;
- committed-range and working-tree whitespace checks passed.

The validator continues to report three pre-existing Learning Capture
`status:` examples as report-only schema drift. They are historical or
note-schema examples, not implemented-skill frontmatter, and this batch does
not change them.

## Context-Cost Review

The catalog grows from 35 to 37 entries, an increase of 5.7%. Only
`source-grounded-research` adds a router gate; `resolving-merge-conflicts`
remains an independent operation-specific branch. Neither new specialist
enters the four representative routes or reconstructs the controller pipeline,
although both add catalog-selection surface whose trigger ambiguity is not
measured by the route-size comparison.

| Scenario | V1 route words | Current V2 route words | Reduction | Change from `aaac926` |
| --- | ---: | ---: | ---: | ---: |
| Bug report to root-cause fix | 12,691 | 6,614 | 47.9% | +191 words, +2.97% |
| Existing codebase to proportional onboarding | 7,387 | 6,077 | 17.7% | -8 words, -0.13% |
| Feature brief to verified change | 15,611 | 9,233 | 40.9% | -8 words, -0.09% |
| Product idea to vertical slice | 6,845 | 6,151 | 10.1% | +61 words, +1.00% |

Every route still clears the required route-specific reduction. The
product-planning route tightened from approximately 11.0% to 10.1%, so further
text or route growth can erase the margin quickly. The comparison continues to
report the 1,193-word shared policy separately rather than hiding persistent
integrated context cost.

## Standards, Security, Documentation, And Boundary Review

Standards/spec review found no behavioral acceptance failure. One stale
context-matrix lifecycle row was corrected so Tickets 015 through 019 are
archived; after the maintainer decision, Ticket 020 was archived and Tickets
021 through 024 remain planned.

No new batch-level security review was triggered. The reviewed changes add
portable guidance and deterministic validation; they do not introduce a new
credential, private-data, persistence, deployment, dependency, or executable
trust path. The merge-conflict and external-research packages explicitly
preserve lifecycle authorization, restricted-source, credential, privacy, and
copyright boundaries. Ticket 018's focused lifecycle/security review remains
part of its implementation proof.

Manual review covered:

- root context and public catalog docs;
- operator and installation guidance;
- category indexes, registry roles, router ownership, and local-retrieval
  boundaries;
- both new standalone packages and their local references;
- changed Markdown links and fenced blocks;
- added-line public-boundary indicators and local absolute paths;
- the full committed diff and whitespace state.

No public artifact presents invocation topology or active domain modeling as
implemented. No private project data, personal machine path, credential value,
client data, or ignored local note was found.

## Residual Risks

- The narrowest representative context reduction is 10.1%.
- Catalog-trigger ambiguity from the two new discovery entries is not measured
  by the route-size comparison.
- Deterministic fixtures and contract tests are not live multi-host model
  evaluation or destructive live Git-conflict execution.
- Historical RED runs and Ticket 019's public forward evaluation are retained
  as implementation records rather than reproduced by this acceptance pass.
- Three pre-existing Learning Capture examples remain report-only schema
  drift.
- The repository has no configured Markdown linter or external-URL
  reachability checker; local links, Markdown structure, and public boundaries
  were reviewed manually and through repository validation.
- Ticket 013's validator split remains pending. This batch extends the current
  compatibility surface without taking ownership of that refactor.

## Maintainer Decision

The maintainer accepted the high-confidence adoption batch with the residual
risks recorded above on 2026-07-26.

The maintainer also selected
[Ticket 013](../tickets/013-split-validator-by-concern.md) as the next slice and
requested that its baseline and extraction contract be refreshed for the
accepted validator growth before implementation begins.
