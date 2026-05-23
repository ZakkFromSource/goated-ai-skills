# PRD: GOATED AI Skills V1 Additions

## Status

Draft reference PRD, rechecked 2026-05-23.

## Problem

The current V1 skill stack covers onboarding, planning, TDD, reviews, docs, architecture maps, architecture planning, refactoring, commit messages, handoffs, and lightweight grilling. Review of public inspiration skills surfaced a few useful additions before final V1 acceptance:

- GOATED lacks a dedicated bug and performance diagnosis workflow before TDD begins.
- `architecture-design-map` can better handle quick "zoom out" requests without durable-map ceremony.
- `framework-agnostic-skill-creator` should cover both new skill creation and existing workflow porting.
- `triage` is useful but belongs outside V1 because it depends on issue tracker state and remote mutation.
- A compact communication mode can be a portable productivity skill when it preserves accuracy and safety.

## Audience

- Maintainers preparing GOATED AI Skills for V1 acceptance.
- Future agents implementing focused local issue handoffs.
- Agent users who install the V1 public core into their own workflows.

## Goals

- Add a GOATED-native `diagnose` engineering skill.
- Fold `zoom-out` behavior into `architecture-design-map` as a quick inline mode.
- Expand `framework-agnostic-skill-creator` as the active skill creation and porting workflow.
- Record `triage` as deferred/out of scope for V1.
- Add a public `caveman` productivity skill with GOATED guardrails.

## Non-Goals

- Do not implement remote issue tracker workflows in V1.
- Do not add a standalone `zoom-out` skill.
- Do not add a standalone `write-a-skill` skill.
- Do not copy upstream source text wholesale without attribution and license handling.
- Do not change the V1 public categories.

## Requirements

| Requirement | Priority | Notes |
| --- | --- | --- |
| Add `diagnose` | Must | Fresh GOATED-native engineering skill inspired by the upstream diagnosis loop. |
| Fold in `zoom-out` | Must | Add quick inline module/caller orientation to `architecture-design-map`. |
| Expand skill creator workflow | Must | Rename current porting workflow and add create/port modes. |
| Defer `triage` | Must | Capture as future issue-tracker workflow, not V1 implementation. |
| Add `caveman` | Must | Keep the public skill name, add GOATED schema and safety guardrails. |
| Preserve public boundary | Must | No private names, credentials, client context, or sensitive workflow assumptions. |
| Preserve self-contained skill design | Must | Installed skills must not depend on this source repo's root files at runtime. |

## Acceptance Criteria

- [x] `diagnose` is implemented under `skills/engineering/` and follows the lean schema.
- [x] `architecture-design-map` includes a quick zoom-out mode without becoming a refactor or planning skill.
- [x] `framework-agnostic-skill-creator` replaces the current porting skill as the active public workflow name.
- [x] `triage` is recorded as deferred/out of scope for V1.
- [x] `caveman` is implemented under `skills/productivity/` and follows the lean schema.
- [x] Public docs and issue blockers reflect the additions before final V1 acceptance.

## Implementation Notes

- `diagnose` should own repro loops, ranked hypotheses, targeted instrumentation, root-cause proof, regression routing, cleanup, and residual-risk reporting. It should route implementation proof to `tdd` instead of merging with it.
- `zoom-out` should become a quick inline mode in `architecture-design-map` for requests like "zoom out," "go up a layer," or "explain this unfamiliar code area." It should return a concise module/caller map with evidence and uncertainty.
- `framework-agnostic-skill-creator` should support two modes: create from clarified intent and port from source material. Port mode should keep the existing source package audit discipline.
- `triage` should be deferred because it relies on issue tracker labels, comments, closing issues, and other remote mutation that V1 intentionally avoids.
- `caveman` should be concise but not careless. It must preserve uncertainty, warnings, exact error text, destructive confirmations, code blocks, and active skill output contracts.

## Testing And Verification

- Validate every new or renamed `SKILL.md` against the lean schema.
- Confirm renamed links and active references resolve.
- Check that new and edited skills are self-contained after installation.
- Run a public-boundary pass for private names, credentials, client context, sensitive assumptions, and source repo/runtime confusion.
- Re-check this PRD, generated issue handoffs, `issues/archive/021-v1-acceptance-public-boundary-pass.md`, and affected docs before V1 acceptance.

## Risks And Mitigations

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Scope creep before V1 acceptance | Delays final acceptance and weakens the public core | Keep the additions split into small issues and defer tracker workflows. |
| External-source copying | License or attribution drift | Rewrite in GOATED-native wording and record project-level MIT attribution before publication if substantial wording is reused. |
| Skill rename drift | Active docs may point to the former porting-only workflow name | Include a dedicated issue for rename/docs cleanup. |
| Brevity mode hides important context | Unsafe or misleading output | Make `caveman` guardrails explicit and require normal clarity for warnings and confirmations. |

## Open Questions

| Question | Owner | Needed before |
| --- | --- | --- |
| None currently. | Not applicable | Not applicable. |

## Source Evidence

- User-approved plan in this session.
- `issues/prd-goated-ai-skills-v1-public-core.md`
- `issues/archive/021-v1-acceptance-public-boundary-pass.md`
- `skills/agent-workflows/framework-agnostic-skill-creator/SKILL.md`
- `skills/engineering/architecture-design-map/SKILL.md`
- Upstream diagnose: https://github.com/mattpocock/skills/tree/main/skills/engineering/diagnose
- Upstream zoom-out: https://github.com/mattpocock/skills/blob/main/skills/engineering/zoom-out/SKILL.md
- Upstream write-a-skill: https://github.com/mattpocock/skills/tree/main/skills/productivity/write-a-skill
- Upstream triage: https://github.com/mattpocock/skills/tree/main/skills/engineering/triage
- Upstream caveman: https://github.com/mattpocock/skills/blob/main/skills/productivity/caveman/SKILL.md
