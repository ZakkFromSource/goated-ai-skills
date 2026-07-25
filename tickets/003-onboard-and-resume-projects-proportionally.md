# Ticket 003: Onboard And Resume Projects Proportionally

## Parent Spec

`docs/specs/2026-07-25-goated-ai-skills-v2.md`

## Type

AFK

## What To Build

Deliver lightweight, standard, and full onboarding from one shared discovery
pass, with incremental artifact refresh, silent session orientation, thin
framework routing, and reliable ignored local continuity.

## Recommended First Reads

- `docs/specs/2026-07-25-goated-ai-skills-v2.md` — Onboarding Profiles,
  Continuity, and High-Frequency Skill Changes
- `skills/agent-workflows/session-start-progressive-disclosure/SKILL.md`
- `skills/agent-workflows/context-matrix-map/SKILL.md`
- `skills/agent-workflows/project-context-calibration/SKILL.md`
- `skills/agent-workflows/project-standards-calibration/SKILL.md`
- `skills/agent-workflows/agent-instructions-integrator/SKILL.md`
- `skills/agent-workflows/handoff/SKILL.md`

## Relevant Source Links

- `docs/agents/context-matrix.md`
- `docs/agents/project-standards.md`
- `.gitignore`

## Acceptance Criteria

- [ ] Onboarding intensity selects an artifact budget rather than a mandatory
      document checklist.
- [ ] One evidence bundle feeds all selected onboarding artifacts.
- [ ] Existing context, source maps, and standards are refreshed incrementally.
- [ ] Inferred standards record provenance and freshness.
- [ ] Small projects can stop after a thin policy/routing integration.
- [ ] Session orientation normally operates silently and reuses fresh state.
- [ ] Resumable envelopes and handoffs default to ignored
      `.local/goated/` paths after ignore verification.
- [ ] OS temp remains a fallback when project-local state is inappropriate.
- [ ] Handoffs link to durable artifacts instead of copying them.

## Expected Proof

- Lightweight small-project fixture.
- Standard incremental-refresh fixture.
- Full architecture- or governance-heavy fixture.
- Resume-from-handoff fixture.
- Ignore-path and OS-temp fallback checks.
- Focused validation and manual artifact review.

## Blocked By

- `tickets/archive/002-route-work-through-adaptive-gates.md`

## User Stories Addressed

- Derived: As a project owner, I receive only the onboarding artifacts my
  project needs and can resume work without reconstructing the session.

## Implementation Route

- Use `writing-plans` to migrate the onboarding skills as one observable route.
- Preserve project instruction precedence and existing local conventions.

## Scope Exclusions

- Do not make `CONTEXT.md`, a context matrix, or a standards profile universal.
- Do not add a database, background refresh service, or framework installer.
