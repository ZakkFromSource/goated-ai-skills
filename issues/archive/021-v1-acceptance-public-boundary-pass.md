## Parent PRD

`issues/prd-goated-ai-skills-v1-public-core.md`

`issues/prd-goated-ai-skills-v1-additions.md`

`issues/prd-goated-ai-skills-v1-superpowers-absorption.md`

## Type

HITL

## What to build

Run the final V1 acceptance and public-boundary pass after the foundation and skill implementation issues are complete. This issue requires maintainer review before V1 can be treated as complete.

## Acceptance criteria

- [x] All prior issue handoffs are complete or explicitly deferred with maintainer approval.
- [x] Public docs consistently distinguish source repo, installed skills, and target projects.
- [x] Implemented skills follow the lean schema and are self-contained after installation.
- [x] Implemented skills include clear triggers, outputs, guardrails, and delegation notes where useful.
- [x] `agent-instructions-integrator`, Target Project Onboarding, and Target Project Delivery are documented consistently.
- [x] Review skills keep standards/spec review separate from security review.
- [x] Superpowers absorption work is complete or explicitly deferred, and any runtime automation or trigger-harness decisions have maintainer approval.
- [x] Public main contains no private names, handles, credentials, client context, or sensitive personal workflow assumptions.
- [x] Maintainer has reviewed any open PRD questions that became blockers during implementation.

## Blocked by

- `issues/archive/001-confirm-scaffold-public-scope.md`
- `issues/archive/002-define-skill-authoring-contract.md`
- `issues/archive/003-session-start-progressive-disclosure.md`
- `issues/archive/004-context-matrix-map.md`
- `issues/archive/005-project-standards-calibration.md`
- `issues/archive/006-agent-instructions-integrator.md`
- `issues/archive/007-handoff.md`
- `issues/archive/008-framework-agnostic-skill-porting.md`
- `issues/archive/009-grill-with-docs.md`
- `issues/archive/010-write-a-prd.md`
- `issues/archive/011-prototype.md`
- `issues/archive/012-prd-to-issues.md`
- `issues/archive/013-tdd.md`
- `issues/archive/014-standards-and-spec-review.md`
- `issues/archive/015-code-security-review.md`
- `issues/archive/016-doc-sync.md`
- `issues/archive/017-commit-message.md`
- `issues/archive/018-architecture-design-map.md`
- `issues/archive/019-improve-codebase-architecture.md`
- `issues/archive/020-grill-me.md`
- `issues/archive/022-project-context-calibration.md`
- `issues/archive/027-add-diagnose-skill.md`
- `issues/archive/028-fold-zoom-out-into-architecture-design-map.md`
- `issues/archive/029-expand-framework-agnostic-skill-creator.md`
- `issues/archive/030-defer-triage-workflow.md`
- `issues/archive/031-add-caveman-skill.md`
- `issues/archive/032-v1-additions-doc-sync-and-acceptance-recheck.md`
- `issues/archive/033-update-skill-authoring-contract-superpowers-conventions.md`
- `issues/archive/034-add-using-goated-ai-skills-router.md`
- `issues/archive/035-decide-runtime-bootstrap-and-adapter-automation.md`
- `issues/archive/036-add-verification-before-completion-skill.md`
- `issues/archive/037-wire-verification-through-goated-stack.md`
- `issues/archive/038-add-writing-plans-skill.md`
- `issues/archive/039-add-subagent-driven-development-skill.md`
- `issues/archive/040-upgrade-prd-to-issues-zero-context-handoffs.md`
- `issues/archive/041-upgrade-tdd-superpowers-contracts.md`
- `issues/archive/042-add-receiving-code-review-skill.md`
- `issues/archive/043-research-skill-trigger-eval-harnesses.md`

## User stories addressed

- As a maintainer, I can make a final human judgment that V1 is public-safe and complete.
- As an agent user, I can trust that the public core is coherent before installing or adapting it.

## Agent acceptance pass notes

- Date: 2026-05-23.
- Read `AGENT.md`, `CONTEXT.md`, `README.md`, `docs/install.md`, `docs/agents/context-matrix.md`, `docs/agents/project-standards.md`, ADR 0001, the three parent PRDs, and this issue.
- Delegated scans checked blocker completion/defer status, implemented skill schema and self-containment, docs consistency, and public-boundary leakage. No blocking findings remained after this pass.
- Corrected one stale public-core PRD flow: Target Project Delivery now includes `writing-plans`, optional `subagent-driven-development`, and `verification-before-completion`, matching `README.md` and the Superpowers absorption PRD.
- Before lifecycle approval, verified only `021`, the three PRDs, and `v1-superpowers-absorption-order.md` remained at top-level `issues/`; direct blockers existed under `issues/archive/` with checked acceptance criteria or accepted defer/decision notes.
- Verified 27 implemented `SKILL.md` files include required lean schema fields and preferred body sections; linked `references/` files resolve; all are under the 300-line soft threshold.
- Public-boundary scans over tracked files found no actionable secrets, credentials, private names, handles, client context, sensitive personal domains, private workflow assumptions, or tracked ignored scratch paths.
- Review-skill separation is documented in `standards-and-spec-review` and `code-security-review`; runtime bootstrap and live trigger-harness work remain out of V1 by accepted issue decisions and ADR 0001.
- No executable test, lint, build, format, or link-check tooling was found for this Markdown-only repository pass; verification used targeted repository searches, delegated evidence, and manual Markdown review.
- Lifecycle note: archived on 2026-05-23 after maintainer approval to treat the final V1 acceptance pass as complete.
