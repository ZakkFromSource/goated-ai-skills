# Ticket 012: Complete And Accept The V2 Migration

## Parent Spec

`docs/specs/2026-07-25-goated-ai-skills-v2.md`

## Type

HITL

## What To Build

Finish the cross-catalog semantic-anatomy migration, remove remaining shared
boilerplate, run V2 conformance and context-size comparisons, synchronize every
public V2 document, and present the complete release for maintainer acceptance.

## Recommended First Reads

- `docs/specs/2026-07-25-goated-ai-skills-v2.md` — complete spec and acceptance
  criteria
- `tickets/goated-ai-skills-v2-order.md`
- Tickets 001 through 011 and their resulting changes
- `AGENT.md`
- `CONTEXT.md`
- `README.md`
- `docs/install.md`
- `docs/how-to-use.md`
- `skills/README.md`

## Relevant Source Links

- `docs/agents/context-matrix.md`
- `docs/agents/project-standards.md`
- `docs/adr/`
- `scripts/validate_skills.py`
- `skills/`
- V1 baseline recorded by Ticket 001

## Acceptance Criteria

- [ ] Every implemented skill follows the semantic V2 anatomy or records a
      justified exception.
- [ ] Repeated global routing, delegation, privacy, evidence, and closeout
      boilerplate is removed.
- [ ] All aliases, canonical names, registry paths, links, and route signals
      validate.
- [ ] All end-to-end and focused behavioural fixtures required by the spec are
      reviewed or run through the documented comparison method.
- [ ] Representative V2 routes load materially less instruction text than V1
      without losing required behaviour.
- [ ] Root context, standards, README, install guidance, operator guidance,
      category indexes, ADR index, and migration guidance describe V2
      consistently.
- [ ] Historical V1 artifacts remain intact.
- [ ] No Factory runtime, model benchmarking, or dedicated evaluation skill has
      entered V2 scope.
- [ ] All required checks and manual reviews are reported with residual risk.
- [ ] The maintainer explicitly accepts V2 before the release is treated as
      complete.

## Expected Proof

- Complete validator output.
- Link and renamed-reference scans.
- Registry, alias, signal, and word-budget reports.
- Representative V1/V2 instruction-size comparisons.
- Behavioural fixture results or documented host-driven review evidence.
- Manual public-documentation and migration review.
- Git status/diff evidence and explicit maintainer acceptance.

## Blocked By

- `tickets/archive/001-establish-v2-integrated-stack-foundation.md`
- `tickets/archive/002-route-work-through-adaptive-gates.md`
- `tickets/archive/003-onboard-and-resume-projects-proportionally.md`
- `tickets/004-clarify-decisions-proportionally.md`
- `tickets/005-turn-specs-into-delivery-tickets.md`
- `tickets/006-design-architecture-and-plans-proportionally.md`
- `tickets/archive/007-navigate-uncertainty-with-wayfinder.md`
- `tickets/archive/008-retrieve-durable-knowledge-safely.md`
- `tickets/archive/009-prove-behaviour-without-mandatory-refinement.md`
- `tickets/010-review-and-verify-conditionally.md`
- `tickets/011-produce-concise-docs-prompts-and-closeouts.md`

## User Stories Addressed

- Derived: As the maintainer, I can understand, verify, migrate to, and
  deliberately accept the complete GOATED AI Skills V2 stack.

## Implementation Route

- Use `writing-plans` for the remaining catalog and documentation migration.
- Use `standards-and-spec-review`, `doc-sync`, and
  `verification-before-completion` before requesting maintainer acceptance.

## Scope Exclusions

- Do not use this ticket to add deferred skills or Factory features.
- Do not accept V2 merely because structural validation passes.
