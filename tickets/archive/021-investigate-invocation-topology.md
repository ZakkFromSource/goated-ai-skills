# Ticket 021: Investigate Invocation Topology

## Parent Spec

`docs/specs/2026-07-26-selective-upstream-skill-adoption.md`

## Type

HITL — the maintainer must choose the supported contract and first consumer.

## Work State

Completed with a maintainer **NO-GO** decision and archived on 2026-07-27.

## What To Build

Produce a source-grounded invocation-topology decision report and disposable
adapter experiment for the candidate semantics `autonomous`, `router-only`,
`manual-only`, and `reference-only`.

The report must distinguish neutral GOATED meaning from Codex, Claude, and
generic Agent Skills mechanisms; identify unsupported mappings; and test one
real consumer before recommending production metadata.

## Recommended First Reads

- `docs/specs/2026-07-26-selective-upstream-skill-adoption.md` — R6 and AC6.
- `docs/adr/0001-v1-runtime-bootstrap-and-adapter-automation.md`
- `docs/adr/0002-v2-integrated-stack-foundation.md`
- `docs/install.md`
- `stack/goated-stack.yaml` and its schema.
- `issues/archive/035-decide-runtime-bootstrap-and-adapter-automation.md`
- `issues/archive/043-research-skill-trigger-eval-harnesses.md`

## Relevant Source Links

- Current official documentation for every evaluated host.
- `scripts/validate_skills.py`
- `skills/agent-workflows/using-goated-ai-skills/SKILL.md`
- `skills/agent-workflows/agent-instructions-integrator/SKILL.md`

## Acceptance Criteria

- [x] Each candidate semantic has a framework-neutral definition and expected
      fallback.
- [x] Host mappings cite current primary documentation or current source.
- [x] The report separates catalog visibility, implicit selection, explicit
      selection, router reachability, and context cost.
- [x] One disposable consumer experiment exercises supported and unsupported
      behavior.
- [x] Static fixtures are not represented as runtime/model proof.
- [x] The report identifies whether production work belongs in registry
      metadata, installation adapters, plugin packaging, or a separate product.
- [x] The maintainer records go, revise, or no-go and selects the first
      supported consumer if applicable.

## Expected Proof

- Dated source matrix with claim-level citations.
- Reproducible experiment inputs and observed results where host access permits.
- Explicit unverified assumptions and unavailable-host residual risk.
- Maintainer decision.

## Blocked By

None.

## User Stories Addressed

- As a GOATED maintainer, I can decide whether invocation metadata will change
  real host behavior before paying permanent schema and catalog cost.

## Implementation Route

- Use `source-grounded-research` if Ticket 019 is already accepted; otherwise
  follow the equivalent research contract in the parent spec.
- Use `prototype` for the disposable consumer experiment.
- Use `grill-with-docs` only for unresolved maintainer tradeoffs.
- Use `verification-before-completion` for the evidence report.

## Scope Exclusions

- Do not change the production registry, schema, validator, or installed skill
  packages.
- Do not commit runtime bootstrap, marketplace, or installer tooling.
- Do not promise cross-framework enforcement where a host lacks support.

## Acceptance Evidence

- [`docs/invocation-topology-decision-report.md`](../../docs/invocation-topology-decision-report.md)
  records the dated host evidence, neutral semantics, reproducible disposable
  adapter experiment, observed implicit and explicit Codex behavior, product
  ownership analysis, and maintainer decision.
- All temporary repository-scoped probe skills were removed after their
  observations were copied into the report.

## Decision Result

The maintainer selected **NO-GO** on 2026-07-27. Invocation-topology metadata
and a host adapter would add more complexity than their benefit justifies in
GOATED's intentionally simple Codex workflow. No production consumer or
semantics were accepted, and Ticket 022 is not authorized.

Caller-aware invocation behavior may be reconsidered only as a separately
specified custom harness rather than as an implicit continuation of this
ticket.
