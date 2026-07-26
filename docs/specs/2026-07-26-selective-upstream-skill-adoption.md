# Selective Upstream Skill Adoption

## Status

Approved and ticket ready.

## Mode

Full.

## Problem

GOATED V2 already provides a stronger integrated control plane than the
`mattpocock/skills` stack, but the comparison identified several focused
engineering doctrines and workflow gaps that could improve GOATED without
importing a competing orchestration pipeline.

The useful changes fall into two groups:

1. high-confidence additions that can be delivered independently; and
2. invocation and domain-modeling ideas that need evidence before GOATED
   changes its registry, adapters, or skill inventory.

Without a durable contract, these ideas could become an unsliced collection of
new skills, speculative metadata, overlapping workflow ownership, or a hidden
expansion beyond the docs-first V2 distribution boundary.

## Goals

- Add the smallest high-value engineering capabilities missing from GOATED.
- Sharpen existing skills only where current behavior has a demonstrated gap.
- Preserve one controller, specialist deltas, proportional routing, and
  standalone skill fallbacks.
- Test invocation topology against a real host consumer before adding registry
  metadata.
- Test active domain-modeling overlap before approving another public skill.
- Keep every implementation slice independently reviewable and freshly
  verifiable.

## Non-Goals

- Do not merge Matt Pocock's stack wholesale into GOATED.
- Do not add an `implement` super-skill or another competing router.
- Do not require grilling, extensive user stories, automatic commits,
  mandatory HTML reports, or background-agent research.
- Do not copy `never --abort` merge-conflict behavior.
- Do not add generic code-smell doctrine that outranks project evidence.
- Do not add work-management, remote issue mutation, guided learning, or
  installer/CLI tooling in this delivery batch.
- Do not require individual skill-level attribution for adapted design ideas;
  the repository-level inspiration notice remains sufficient for this work.

## Requirements

### R1: Skill-authoring determinism and load discipline

The skill-creation workflow must evaluate whether guidance changes behavior,
earns its invocation and context cost, has observable phase completion, avoids
no-op or duplicated instructions, discloses branch-specific detail
progressively, and does not encourage premature completion.

### R2: Diagnosis reproduction minimization

`diagnose` must explicitly minimize a confirmed reproduction until each
remaining input, dependency, step, and environmental condition is load-bearing.
This refinement must preserve the existing safety, fidelity, intermittent-bug,
and lower-confidence fallback rules.

### R3: Wide-refactor ticket slicing

`spec-to-tickets` must recognize broad mechanical migrations that cannot land
as ordinary vertical slices and support an expand, migrate, contract sequence.
Migration batches must be sized by blast radius, name their blockers, preserve
green intermediate states where possible, and use an integration-branch
exception only when independently green batches are impossible.

### R4: Intent-preserving merge-conflict resolution

GOATED must add a compact, framework-agnostic
`resolving-merge-conflicts` engineering skill. It must trace both sides to
primary intent, preserve compatible intents, surface incompatible semantic
decisions, run scoped checks, and allow safe abort when continuing would be
wrong, unsafe, or unauthorized.

Loading the skill must not by itself authorize staging, committing, continuing
a Git operation, or making an unresolved product decision.

### R5: Source-grounded external research

GOATED must add a `source-grounded-research` skill distinct from read-only
local `knowledge-retrieval` and from `doc-sync`'s external-doc capture
convention.

The skill must frame the research question and currency requirement, choose a
source hierarchy, prefer primary sources, distinguish findings from inference,
record claim-scoped provenance and freshness, support conflicting or missing
evidence, return a reusable evidence delta, remain single-agent-compatible, and
make durable note creation optional.

### R6: Evidence-gated invocation topology

GOATED must define candidate invocation semantics such as `autonomous`,
`router-only`, `manual-only`, and `reference-only`, but must not add them to the
production registry until:

- supported hosts and fallbacks are documented;
- at least one real adapter or installation consumer exists;
- implicit and explicit invocation behavior is exercised against that
  consumer; and
- the maintainer accepts the portability and context-load tradeoff.

Static registry fixtures must not be described as proof of model behavior.

### R7: Evidence-gated active domain modeling

GOATED must evaluate whether terminology decisions made during delivery are
currently lost or detached from context and ADR updates. A new
`domain-modeling` skill may be implemented only if pressure scenarios show a
recurring gap that is not adequately owned by `project-context-calibration`,
`grill-with-docs`, `write-a-spec`, and the architecture skills.

If approved, the skill must make narrow terminology or ADR deltas without
performing broad onboarding or forcing `CONTEXT.md` to be glossary-only.

### R8: Existing boundaries remain intact

Every new or changed skill must:

- remain self-contained when installed individually;
- integrate through the GOATED router without reconstructing the pipeline;
- respect approval modes, action reach, sensitivity, and evidence reuse;
- remain single-agent-compatible;
- keep remote mutation and Git lifecycle actions separately authorized; and
- use source-repo registry, fixture, validation, and public documentation
  updates only when the implemented behavior requires them.

## Acceptance Criteria

- [ ] AC1: The skill creator and its evaluation reference contain
      behavior-changing load, determinism, completion, pruning, and
      progressive-disclosure checks without duplicating shared policy.
- [ ] AC2: Diagnosis fixtures prove exact-symptom reproduction is minimized
      before hypothesis ranking while unsafe or intermittent cases retain
      honest fallbacks.
- [ ] AC3: Ticket-slicing fixtures distinguish ordinary vertical work from
      expand-migrate-contract refactors and report the ready frontier.
- [ ] AC4: `resolving-merge-conflicts` is implemented, registered, documented,
      self-contained, and pressure-tested for compatible intent, incompatible
      intent, unsafe continuation, and lifecycle authorization.
- [ ] AC5: `source-grounded-research` is implemented, registered, documented,
      self-contained, and tested for read-only output, optional durable
      capture, stale or conflicting sources, and single-agent fallback.
- [ ] AC6: A maintainer-reviewed invocation-topology report identifies real
      host mappings, a consumer, unsupported behavior, and a go/no-go decision
      before production registry changes.
- [ ] AC7: Any accepted invocation metadata is schema-validated, consumed by at
      least one adapter, documented with graceful fallbacks, and verified
      without overstating static fixtures as runtime proof.
- [ ] AC8: A maintainer-reviewed domain-modeling evaluation records current
      ownership, pressure-scenario evidence, overlap risks, and a go/no-go
      decision before a new skill is added.
- [ ] AC9: Any accepted `domain-modeling` skill owns only active terminology and
      consequential decision capture, with narrow writes and no broad
      onboarding scan.
- [ ] AC10: Repository validation, focused tests, V1/V2 context comparison,
      public-boundary scans, Markdown/link review, and diff checks pass for
      every completed implementation slice.
- [ ] AC11: Ticket 013's validator refactor is not mixed into these behavior
      changes; overlapping validator work is sequenced explicitly.

## Constraints

- `AGENT.md` permits new skill folders only for an approved implementation
  ticket. The tickets derived from this approved spec provide that contract.
- Ticket 013 was completed separately as the behavior-preserving validator
  refactor. Adoption tickets could depend on validator behavior but did not
  silently implement its module split.
- The current V2 distribution remains docs-first. Runtime bootstrap,
  marketplace packaging, generated adapters, and installer automation require
  a separate approved scope.
- New `SKILL.md` files remain under the soft 300-line threshold where possible,
  with detailed scenarios and templates in directly linked support files.
- Public artifacts must not contain private project data, credentials, user
  records, or ignored local notes.

## Stakeholders

- GOATED maintainer: owns scope, invocation and domain-model go/no-go decisions,
  and final acceptance.
- Skill users: need portable standalone behavior and predictable integrated
  routing.
- Future adapter maintainers: need neutral semantics that map honestly to host
  capabilities.

## Architecture

The delivery preserves the existing control-plane shape:

```text
using-goated-ai-skills
  -> selects proportionate specialist gate
  -> specialist returns evidence, artifact, finding, or route delta
  -> controller re-evaluates at defined checkpoints
  -> one verified closeout
```

New skills are specialists, not orchestrators. Invocation metadata remains a
catalog-and-adapter contract only after a consumer proves it can enforce or
faithfully degrade the declared semantics.

## Rollout

### Phase A: High-confidence adoption

Deliver R1 through R5 as independently reviewable slices, then perform one
cross-slice acceptance pass. These changes do not wait for invocation or
domain-modeling experiments.

### Phase B: Invocation experiment

Research host behavior and prototype one consumer. Production registry,
schema, validator, and adapter changes require a separate maintainer go
decision after the evidence is reviewed.

### Phase C: Domain-modeling experiment

Evaluate current workflows under pressure. Creating the public skill requires
a separate maintainer go decision after the overlap evidence is reviewed.

## Risks

- Invocation metadata could become inert documentation. Mitigation: require a
  real consumer before production schema changes.
- A domain-modeling primitive could duplicate onboarding or clarification.
  Mitigation: require RED/GREEN overlap evidence and a maintainer gate.
- New specialist descriptions could increase catalog context and trigger
  ambiguity. Mitigation: apply the new authoring load checks and include
  routing scenarios.
- Multiple tickets could touch validator surfaces while Ticket 013 was active.
  This risk was managed by sequencing overlapping writes and rebasing plans on
  the validator's public compatibility surface.
- Research guidance can produce copyright, freshness, or source-authority
  errors. Mitigation: prefer links and summaries, record provenance and dates,
  and preserve uncertainty.

## Open Questions

- Which host should be the first invocation-topology consumer? Owner: GOATED
  maintainer during the invocation investigation ticket.
- Does current delivery work demonstrate enough terminology-loss failure to
  justify `domain-modeling`? Owner: GOATED maintainer after the evaluation
  report.

## Sources

- `AGENT.md` — source-repo, new-skill, public-boundary, and progressive
  disclosure rules.
- `CONTEXT.md` — GOATED product model and source/installed/target boundaries.
- `docs/specs/2026-07-25-goated-ai-skills-v2.md` — accepted V2 control-plane,
  registry, fixture, and distribution contracts.
- `docs/adr/0002-v2-integrated-stack-foundation.md` — current integrated and
  individual installation decision.
- `stack/AGENTS.md` and `stack/goated-stack.yaml` — shared controller behavior
  and current registry metadata.
- `skills/agent-workflows/framework-agnostic-skill-creator/` — current skill
  authoring and evaluation contract.
- `skills/engineering/diagnose/SKILL.md` — current diagnosis feedback-loop
  behavior.
- `skills/engineering/spec-to-tickets/SKILL.md` — current vertical slicing and
  local-only ticket contract.
- `skills/productivity/knowledge-retrieval/SKILL.md` and
  `skills/engineering/doc-sync/references/external-docs-lookup-notes.md` —
  current local retrieval and external-doc capture boundaries.
- `issues/archive/030-defer-triage-workflow.md`,
  `issues/archive/035-decide-runtime-bootstrap-and-adapter-automation.md`, and
  `issues/archive/043-research-skill-trigger-eval-harnesses.md` — accepted
  deferrals and evaluation constraints.
- `https://github.com/mattpocock/skills` — current upstream inspiration source.
- User-provided comparison report from 2026-07-26 — candidate concepts and
  initial recommendations reviewed against current GOATED source.
