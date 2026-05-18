## Parent PRD

`issues/prd-goated-ai-skills-v1-public-core.md`

## Type

HITL

## What to build

Run the final V1 acceptance and public-boundary pass after the foundation and skill implementation issues are complete. This issue requires maintainer review before V1 can be treated as complete.

## Acceptance criteria

- [ ] All prior issue handoffs are complete or explicitly deferred with maintainer approval.
- [ ] Public docs consistently distinguish source repo, installed skills, and target projects.
- [ ] Implemented skills follow the lean schema and are self-contained after installation.
- [ ] Implemented skills include clear triggers, outputs, guardrails, and delegation notes where useful.
- [ ] `agent-instructions-integrator`, Target Project Onboarding, and Target Project Delivery are documented consistently.
- [ ] Review skills keep standards/spec review separate from security review.
- [ ] Public main contains no private names, handles, credentials, client context, or sensitive personal workflow assumptions.
- [ ] Maintainer has reviewed any open PRD questions that became blockers during implementation.

## Blocked by

- `issues/archive/001-confirm-scaffold-public-scope.md`
- `issues/archive/002-define-skill-authoring-contract.md`
- `issues/archive/003-session-start-progressive-disclosure.md`
- `issues/004-context-matrix-map.md`
- `issues/005-project-standards-calibration.md`
- `issues/006-agent-instructions-integrator.md`
- `issues/007-handoff.md`
- `issues/008-framework-agnostic-skill-porting.md`
- `issues/009-grill-with-docs.md`
- `issues/010-write-a-prd.md`
- `issues/011-prototype.md`
- `issues/012-prd-to-issues.md`
- `issues/013-tdd.md`
- `issues/014-standards-and-spec-review.md`
- `issues/015-code-security-review.md`
- `issues/016-doc-sync.md`
- `issues/017-commit-message.md`
- `issues/018-architecture-design-map.md`
- `issues/019-improve-codebase-architecture.md`
- `issues/020-grill-me.md`
- `issues/022-project-context-calibration.md`

## User stories addressed

- As a maintainer, I can make a final human judgment that V1 is public-safe and complete.
- As an agent user, I can trust that the public core is coherent before installing or adapting it.
