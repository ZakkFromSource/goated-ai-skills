## Parent PRD

No separate parent PRD. This issue is part of the user-approved 2026-05-26 post-V1 improvement issue set. Use this file as the implementation contract.

## Type

AFK

## What to build

Upgrade `prd-to-issues` so multi-issue breakdowns create or refresh a local recommended order file, such as `issues/<prd-slug>-order.md`, after the user approves the issue breakdown.

Dynamic means updated when `prd-to-issues` runs. It does not mean background automation, generated indexes, remote issue tracker sync, or live project-board state.

## Recommended first reads

- `AGENT.md`
- `CONTEXT.md`
- `docs/how-to-use.md`
- `skills/engineering/prd-to-issues/SKILL.md`
- `issues/v1-superpowers-absorption-order.md`
- `issues/archive/012-prd-to-issues.md`
- `issues/archive/040-upgrade-prd-to-issues-zero-context-handoffs.md`

## Relevant source links

- `skills/engineering/prd-to-issues/SKILL.md` - existing issue breakdown workflow and templates.
- `issues/v1-superpowers-absorption-order.md` - precedent for a local recommended order file.
- `docs/adr/0001-v1-runtime-bootstrap-and-adapter-automation.md` - boundary against automation and adapter/runtime behavior.

## Acceptance criteria

- [ ] `prd-to-issues` outputs include a local recommended order file for multi-issue breakdowns.
- [ ] The order file includes parent PRD or planning artifact path, generation/update date, generated issue paths, dependency order, blockers, AFK/HITL type, and status placeholders.
- [ ] The order file is written only after user approval of the proposed issue breakdown.
- [ ] If an order file for the same PRD already exists, the workflow refreshes it from the approved issue set instead of appending stale duplicates.
- [ ] Single-issue breakdowns may skip the order file and report why.
- [ ] Guardrails explicitly reject remote tracker sync, generated global indexes, background automation, labels, milestones, assignees, or project boards.
- [ ] The after-writing report includes the order file path along with generated issue paths.

## Expected proof

- Manual review of updated `prd-to-issues` workflow, output contract, and guardrails.
- Targeted `rg` for `order file`, `dynamic`, `remote`, `tracker`, `project board`, and stale output wording.
- Scenario checks: multi-issue set creates an order file; single-issue set can skip it; refreshing an existing order file does not preserve stale entries.

## Blocked by

- None - can start immediately.

## User stories addressed

- As an agent user, I can see the recommended order for a generated issue set without reconstructing blockers manually.
- As a future agent, I can pick the next issue using a stable local order artifact.

## Implementation route

- Use `writing-plans` before editing because the issue touches workflow templates and guardrails.
- Use `doc-sync` if public operator docs mention `prd-to-issues` outputs.

## Scope exclusions

- Do not implement remote issue tracker integration.
- Do not add background regeneration or filesystem watchers.
- Do not create global generated indexes for all issue sets.

