## Parent PRD

`issues/prd-goated-ai-skills-v1-additions.md`

`issues/prd-goated-ai-skills-v1-superpowers-absorption.md`

## Type

HITL

## What to build

Run documentation synchronization and a final acceptance recheck after the V1 additions and Superpowers absorption issues are implemented or explicitly deferred. This issue prepares the repo to return to `issues/021-v1-acceptance-public-boundary-pass.md`.

## Acceptance criteria

- [ ] `README.md`, `CONTEXT.md`, category READMEs, `docs/agents/context-matrix.md`, and relevant PRDs/issues are consistent with the final V1 additions.
- [ ] Active docs refer to `framework-agnostic-skill-creator` as the current workflow name.
- [ ] The new or edited skills follow the lean schema and are self-contained after installation.
- [ ] The `triage` deferral is reflected in `.out-of-scope/` and not represented as an implemented V1 skill.
- [ ] `issues/prd-goated-ai-skills-v1-superpowers-absorption.md`, `issues/v1-superpowers-absorption-order.md`, and issues `033` through `043` are consistent with the final implemented or deferred scope.
- [ ] Superpowers absorption docs preserve the V1 docs-first distribution model unless a HITL decision explicitly changed it.
- [ ] Public docs contain no private names, handles, credentials, client context, sensitive personal domains, or private workflow assumptions.
- [ ] `issues/021-v1-acceptance-public-boundary-pass.md` can be resumed with this additions issue set resolved or explicitly deferred.

## Blocked by

- `issues/027-add-diagnose-skill.md`
- `issues/028-fold-zoom-out-into-architecture-design-map.md`
- `issues/029-expand-framework-agnostic-skill-creator.md`
- `issues/030-defer-triage-workflow.md`
- `issues/031-add-caveman-skill.md`
- `issues/033-update-skill-authoring-contract-superpowers-conventions.md`
- `issues/034-add-using-goated-ai-skills-router.md`
- `issues/035-decide-runtime-bootstrap-and-adapter-automation.md`
- `issues/036-add-verification-before-completion-skill.md`
- `issues/037-wire-verification-through-goated-stack.md`
- `issues/038-add-writing-plans-skill.md`
- `issues/039-add-subagent-driven-development-skill.md`
- `issues/040-upgrade-prd-to-issues-zero-context-handoffs.md`
- `issues/041-upgrade-tdd-superpowers-contracts.md`
- `issues/042-add-receiving-code-review-skill.md`
- `issues/043-research-skill-trigger-eval-harnesses.md`

## User stories addressed

- As a maintainer, I can verify the additions did not create documentation drift before final V1 acceptance.
- As an agent user, I can trust the V1 public core remains coherent and public-safe.

## Implementation notes

- This is a review and synchronization issue, not a place to add new scope.
- Re-read `issues/prd-goated-ai-skills-v1-superpowers-absorption.md` and `issues/v1-superpowers-absorption-order.md` during this pass.
- Route any new ideas discovered during this pass to `.out-of-scope/` or a future PRD unless the maintainer explicitly changes V1 scope.
