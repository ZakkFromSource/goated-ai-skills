# Ticket 010: Review And Verify Conditionally

## Parent Spec

`docs/specs/2026-07-25-goated-ai-skills-v2.md`

## Type

AFK

## What To Build

Make standards, spec, security, review-feedback, and full verification
procedures load only when the change surface or uncertainty warrants them while
preserving universal evidence-backed completion discipline.

## Recommended First Reads

- `docs/specs/2026-07-25-goated-ai-skills-v2.md` — Delivery Gate Matrix and
  Verification, Reviews, And Documentation
- `skills/engineering/receiving-code-review/SKILL.md`
- `skills/engineering/standards-and-spec-review/SKILL.md`
- `skills/engineering/code-security-review/SKILL.md`
- `skills/engineering/verification-before-completion/SKILL.md`
- `stack/AGENTS.md`

## Relevant Source Links

- `skills/engineering/code-security-review/references/`
- `skills/engineering/verification-before-completion/references/`
- `stack/goated-stack.yaml`

## Acceptance Criteria

- [ ] Narrow work can verify directly from the shared policy.
- [ ] Full verification loads only for complex, high-risk, delegated,
      multi-surface, or explicitly audited work.
- [ ] Standards/spec review scales with diff size, risk, acceptance ambiguity,
      and convention uncertainty.
- [ ] Security review has explicit trust-boundary and sensitive-surface
      activation conditions.
- [ ] Receiving review preserves accepted, rejected, unclear, and
      user-decision classifications without repetitive response templates.
- [ ] Review skills reuse envelope evidence and emit findings or route deltas
      rather than duplicate closeouts.
- [ ] Evidence freshness and claim scope remain non-negotiable.

## Expected Proof

- Tiny-diff verification fixture.
- Spec-sensitive and standards-sensitive fixtures.
- Trust-boundary and non-security fixtures.
- Delegated combined-change verification fixture.
- Review-feedback classification fixture.
- Instruction-size comparison and validator output.

## Blocked By

- `tickets/002-route-work-through-adaptive-gates.md`
- `tickets/009-prove-behaviour-without-mandatory-refinement.md`

## User Stories Addressed

- Derived: As a maintainer, I receive specialist review where it matters
  without losing evidence-backed completion on smaller work.

## Implementation Route

- Use `writing-plans` to migrate the review and verification route as one
  observable closeout slice.

## Scope Exclusions

- Do not make security, standards, or full verification universal prompt
  payloads.
- Do not weaken proof freshness or permit unsupported completion claims.
