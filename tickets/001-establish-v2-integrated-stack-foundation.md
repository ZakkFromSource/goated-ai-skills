# Ticket 001: Establish The V2 Integrated-Stack Foundation

## Parent Spec

`docs/specs/2026-07-25-goated-ai-skills-v2.md`

## Type

AFK

## What To Build

Create the smallest installable V2 foundation: preserve a V1 reference point,
record the superseding architecture decision, add the shared integrated-stack
policy and registry contracts, and extend validation without breaking the
current individual-skill experience.

## Recommended First Reads

- `AGENT.md`
- `docs/specs/2026-07-25-goated-ai-skills-v2.md` — Installation Model,
  Integrated Stack Layout, Shared Core Policy, Registry, and Requirements
- `docs/adr/0001-v1-runtime-bootstrap-and-adapter-automation.md`
- `scripts/validate_skills.py`
- `skills/README.md`

## Relevant Source Links

- `stack/` — planned V2 integrated-stack root
- `docs/adr/README.md`
- `docs/install.md`
- `skills/agent-workflows/agent-instructions-integrator/SKILL.md`

## Acceptance Criteria

- [ ] A lightweight V1 baseline or release reference is recorded before
      breaking V2 migration changes.
- [ ] A V2 ADR explicitly supersedes the conflicting installation and
      self-containment decisions in ADR 0001.
- [ ] `stack/AGENTS.md` defines shared V2 behaviour without copying specialist
      procedures.
- [ ] `stack/goated-stack.yaml` represents the current integrated catalog using
      a versioned portable contract.
- [ ] `stack/schemas/stack-registry.schema.json` validates the registry.
- [ ] Human-readable work-envelope and evidence-entry templates exist without
      introducing separate JSON Schemas.
- [ ] Validation covers registry structure and cross-references while all
      current skill checks continue to pass.
- [ ] Individual skill installation remains documented and usable.

## Expected Proof

- Existing skill validator output.
- New registry-schema and cross-reference validation output.
- Manual review of the shared policy against the V2 responsibility boundary.
- Integrated-stack and individual-skill installation walkthroughs.
- Git evidence for the preserved V1 reference point.

## Blocked By

- None — can start immediately.

## User Stories Addressed

- Derived: As the maintainer, I can install one shared GOATED policy and
  validated catalog without breaking users who copy one skill.

## Implementation Route

- Use `writing-plans` to choose the exact baseline, ADR, registry, schema,
  validation, and documentation edits.
- Use `verification-before-completion` before claiming the foundation is
  installable or backward-compatible.

## Scope Exclusions

- Do not migrate every skill in this ticket.
- Do not add installer automation, runtime hooks, Factory code, model metadata,
  or formal work-envelope/evidence JSON Schemas.
- Do not create duplicate folders for future aliases.

## Foundation Rationale

The shared policy and registry form the small interface that hides integrated
stack routing and validation details for every dependent V2 workflow.
