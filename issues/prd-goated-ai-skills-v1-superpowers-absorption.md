# PRD: GOATED AI Skills V1 Superpowers Absorption

## Status

Draft reference PRD, rechecked 2026-05-23.

## Problem

GOATED AI Skills V1 already has a public-safe, framework-agnostic stack for onboarding, planning, implementation, review, documentation, and handoff. Analysis of the public Superpowers repository found several behavior-shaping conventions that would make GOATED more reliable for serious agent work:

- skills are tested as behavior, including RED baselines, pressure scenarios, rationalization capture, and GREEN verification;
- delegated implementation has a formal review loop instead of loose "send agents" prompting;
- completion claims require fresh proof from commands, tests, diffs, or inspected artifacts;
- implementation plans are executable enough for a fresh agent to act without the original chat history;
- discipline-heavy skills use explicit stop rules and rationalization guardrails;
- support files such as `references/`, prompt templates, and scripts are treated as normal skill anatomy.

GOATED should absorb the portable parts of these conventions without copying Superpowers wholesale, weakening GOATED's richer schema, or turning V1 into runtime plugin/bootstrap automation before a human decision approves that shift.

## Audience

- Maintainers preparing GOATED AI Skills for V1 acceptance.
- Future agents implementing the Superpowers absorption issue set.
- Agent users who need installable skills that remain self-contained after copying into Codex, Claude Code, Hermes, OpenCode, or generic agent workflows.

## Goals

- Add GOATED-native guidance for behavior-testing skills: RED baseline, pressure scenarios, rationalization capture, and GREEN verification.
- Add a portable `using-goated-ai-skills` router skill inspired by Superpowers' router, without runtime plugin automation.
- Add `verification-before-completion` as a shared engineering closeout skill.
- Add `writing-plans` as the place where approved issues become executable implementation plans just before implementation.
- Add `subagent-driven-development` with implementer/reviewer prompts and explicit delegated-work statuses.
- Upgrade `prd-to-issues` so generated issue handoffs include enough context for agents with no session history.
- Add `receiving-code-review`.
- Upgrade `diagnose`, `tdd`, and `framework-agnostic-skill-creator` with the strongest relevant Superpowers conventions.
- Keep runtime bootstrap/plugin automation out of V1 per ADR 0001, and keep live skill-trigger eval harnesses behind a future PRD after archived issue `043`.

## Non-Goals

- Do not copy Superpowers text, tone, or repo architecture wholesale.
- Do not weaken GOATED's lean schema fields: `depends_on`, `outputs`, `adapters`, `classification`, and `status` stay required.
- Do not implement runtime bootstrap/plugin automation in V1; ADR 0001 allows only narrow adapter notes.
- Do not implement marketplace manifests, version/drift manifests, release-note machinery, worktree lifecycle, finish-branch lifecycle, strong PR gates, or full adapter automation in this V1 scope.
- Do not add standalone V1 skills for Superpowers `brainstorming`, `dispatching-parallel-agents`, `executing-plans`, `requesting-code-review`, `using-git-worktrees`, or `finishing-a-development-branch`.
- Do not make issue handoffs so verbose that they become stale implementation transcripts; detailed executable steps belong in `writing-plans` after source inspection.

## Ranked Findings From 2026-05-21 Analysis

| Rank | Superpowers strength | Value for GOATED | V1 action |
| --- | --- | --- | --- |
| 1 | Skill behavior testing | Gives skills a way to prove they change agent behavior, not just prose | Add `references/skill-evaluation.md` guidance through the skill creator upgrade |
| 2 | Verification-before-completion gate | Prevents stale or unverified success claims | Add `verification-before-completion` and wire it through relevant skills |
| 3 | Subagent-driven development protocol | Turns parallel agents into a reviewable implementation system | Add `subagent-driven-development` with prompt templates and status enums |
| 4 | Executable implementation plans | Makes approved work actionable for fresh agents | Add `writing-plans` and upgrade issue handoffs to route to it |
| 5 | Rationalization-resistant discipline | Reduces loopholes in TDD, review, debugging, and verification | Add rationalization tables and stop rules where discipline matters |
| 6 | Trigger and activation machinery | Helps agents choose skills at the right time | Add a portable router skill; defer runtime bootstrap automation |
| 7 | Support-file pragmatism | Keeps `SKILL.md` lean while allowing templates, checks, and references | Codify support files in the skill authoring contract |
| 8 | Adapter/product distribution polish | Useful for post-V1 adoption | Defer manifests, drift checks, and full adapter automation |

## Requirements

| Requirement | Priority | Notes |
| --- | --- | --- |
| Update `diagnose` issue | Must | Absorb Superpowers `systematic-debugging` as source inspiration while keeping diagnosis separate from TDD implementation. |
| Update `framework-agnostic-skill-creator` issue | Must | Fold in Superpowers `writing-skills` and Matt Pocock `write-a-skill`; require a skill-evaluation reference. |
| Codify Superpowers conventions | Must | Trigger-only descriptions, delegated status enums, prompt templates, rationalization tables, proof gates, and support-file pragmatism. |
| Add `using-goated-ai-skills` router | Must | Portable router skill with project/user-instruction respect and tiny-task escape hatches; no runtime bootstrap automation. |
| Decide runtime bootstrap and adapter automation | Done | Resolved by `issues/archive/035-decide-runtime-bootstrap-and-adapter-automation.md` and ADR 0001: V1 allows narrow adapter notes only. |
| Add `verification-before-completion` | Must | Shared closeout gate requiring fresh command or artifact evidence before success claims. |
| Wire verification across the stack | Must | Relevant engineering skills should soft-depend on verification before completion. |
| Add `writing-plans` | Must | Expand approved issues into executable implementation plans at the moment of implementation. |
| Add `subagent-driven-development` | Must | Fresh implementer per task, spec review, quality review, final review, and status enums. |
| Upgrade `prd-to-issues` | Must | Handoffs must carry enough context for agents with no access to the original session. |
| Upgrade `tdd` | Must | Add stronger red/green proof, rationalization guardrails, and anti-pattern references. |
| Add `receiving-code-review` | Must | Verify feedback before obeying it, clarify unclear items, and push back technically when needed. |
| Research skill-trigger eval harnesses | Done | Resolved by `issues/archive/043-research-skill-trigger-eval-harnesses.md`: V1 keeps docs-only/static guidance and manual scenario examples; future harness work requires a future PRD after usage evidence. |
| Update V1 recheck issues | Must | `032` and `021` should include the new PRD and issue blockers. |

## Source Fit Matrix

| Upstream source | V1 fit | GOATED destination | Decision |
| --- | --- | --- | --- |
| Superpowers repo root: https://github.com/obra/superpowers | High as source evidence | This PRD and linked implementation issues | Use as public inspiration, not runtime dependency. |
| `brainstorming`: https://github.com/obra/superpowers/tree/main/skills/brainstorming | Partial | Existing `grill-with-docs`, `write-a-prd`, and future `writing-plans` | Absorb useful questioning and option-generation habits; do not add standalone V1 skill. |
| `dispatching-parallel-agents`: https://github.com/obra/superpowers/tree/main/skills/dispatching-parallel-agents | Medium | `subagent-driven-development` | Absorb delegation patterns into a fuller implementation/review protocol; no standalone V1 skill. |
| `executing-plans`: https://github.com/obra/superpowers/blob/main/skills/executing-plans/SKILL.md | Medium | `writing-plans` and `subagent-driven-development` | Absorb "follow the plan, checkpoint, verify" behavior without creating a separate executor skill. |
| `finishing-a-development-branch`: https://github.com/obra/superpowers/blob/main/skills/finishing-a-development-branch/SKILL.md | Low for V1 | Post-V1 delivery lifecycle | Defer; useful only after GOATED decides branch lifecycle policy. |
| `using-git-worktrees`: https://github.com/obra/superpowers/blob/main/skills/using-git-worktrees/SKILL.md | Low for V1 | Post-V1 workflow or adapter docs | Defer; worktree lifecycle is explicitly out of V1 scope. |
| `receiving-code-review`: https://github.com/obra/superpowers/blob/main/skills/receiving-code-review/SKILL.md | High | New `receiving-code-review` skill | Absorb as a GOATED-native review feedback skill. |
| `requesting-code-review`: https://github.com/obra/superpowers/blob/main/skills/requesting-code-review/SKILL.md | Partial | `subagent-driven-development` prompt templates and existing review skills | Absorb reviewer-prompt ideas; do not add standalone V1 skill. |
| `subagent-driven-development`: https://github.com/obra/superpowers/blob/main/skills/subagent-driven-development/SKILL.md | Very high | New `subagent-driven-development` skill | Add V1 skill with GOATED guardrails and single-agent fallback. |
| `systematic-debugging`: https://github.com/obra/superpowers/blob/main/skills/systematic-debugging/SKILL.md | High | `diagnose` | Absorb debugging discipline into `diagnose`; keep diagnosis separate from TDD fixes. |
| `test-driven-development`: https://github.com/obra/superpowers/blob/main/skills/test-driven-development/SKILL.md | High | Existing `tdd` upgrade | Absorb red/green proof, rationalization guardrails, and anti-pattern references. |
| `verification-before-completion`: https://github.com/obra/superpowers/blob/main/skills/verification-before-completion/SKILL.md | Very high | New `verification-before-completion` skill | Add V1 skill and wire it through relevant engineering skills. |
| `writing-plans`: https://github.com/obra/superpowers/blob/main/skills/writing-plans/SKILL.md | High | New `writing-plans` skill | Add V1 skill as the executable-plan contract for approved issues. |
| `writing-skills`: https://github.com/obra/superpowers/tree/main/skills/writing-skills | High | `framework-agnostic-skill-creator` and `references/skill-evaluation.md` | Absorb skill-writing and skill-testing practices. |
| Matt Pocock `write-a-skill`: https://github.com/mattpocock/skills/tree/main/skills/productivity/write-a-skill | High | `framework-agnostic-skill-creator` | Combine with Superpowers writing guidance in GOATED style. |
| `using-superpowers`: https://github.com/obra/superpowers/blob/main/skills/using-superpowers/SKILL.md | High concept, constrained runtime fit | New `using-goated-ai-skills` router plus HITL runtime decision issue | Add portable router; defer bootstrap/plugin automation. |
| Adapter manifests, release notes, version/drift checks, PR gates | Useful post-V1 | Future PRD or `.out-of-scope/` | Defer unless maintainer changes scope. |

## Acceptance Criteria

- [x] `issues/prd-goated-ai-skills-v1-superpowers-absorption.md` exists and includes prior findings, upstream links, and a source-fit matrix.
- [x] `issues/v1-superpowers-absorption-order.md` exists and gives a dependency-aware issue tackling order.
- [x] Issues `033` through `043` exist, follow the local issue template, and include enough context for agents with no session history.
- [x] Existing issues `027`, `029`, `032`, and `021` are updated to account for this PRD and blocker graph.
- [x] Every implementation issue routes future agents to `grill-with-docs` before implementation unless the issue is only a tiny mechanical edit.
- [x] New skill issues preserve GOATED's lean schema and self-contained installed behavior.
- [x] Runtime bootstrap/plugin automation and skill-trigger eval harnesses are HITL decision or research work, not automatic V1 implementation.
- [x] Public docs and issue text contain no private names, handles, credentials, client context, sensitive personal domains, or source-repo/runtime confusion.

## Implementation Notes

- Future agents should treat this PRD as the source of scope, but they must still read the specific issue being implemented and inspect the current source files before editing.
- Superpowers is MIT-licensed. Rewrite in GOATED-native language; if substantial upstream wording, templates, or structure are reused, record the reuse for project-level attribution before publication rather than making installed skill folders depend on upstream links.
- Support files are encouraged when they keep `SKILL.md` focused: prompt templates, long checklists, scenario examples, adapter notes, and evaluation references belong under `references/` inside the relevant skill folder.
- Issues should provide source links and acceptance criteria, but detailed file-by-file steps should be produced by `writing-plans` after source inspection.
- All new installed skills must remain useful after copying out of this source repo. They must not require this root `AGENT.md`, `CONTEXT.md`, issue files, or `.local/` research artifacts at runtime.

## Testing And Verification

- Manually validate every new and updated issue follows the existing local issue template.
- Check all new skill plans require GOATED's lean schema and self-contained installed behavior.
- Verify every upstream source link is present in this PRD or in relevant issue notes.
- Run targeted searches for stale or ambiguous names: `framework-agnostic-skill-porting`, `using-superpowers`, `writing-plans`, `verification-before-completion`, and new issue paths.
- Run a public-boundary review for private names, credentials, client context, sensitive personal domains, and source-repo/runtime confusion.
- Re-read `issues/archive/032-v1-additions-doc-sync-and-acceptance-recheck.md` and `issues/archive/021-v1-acceptance-public-boundary-pass.md` after blocker updates.

## Risks And Mitigations

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Runtime scope creep | V1 stops being docs-first and portable | Keep runtime automation out of V1 per ADR 0001; future automation requires a new scoped PRD or issue. |
| Superpowers tone or assumptions overwrite GOATED style | Skills become less framework-agnostic or too dogmatic | Rewrite conventions in GOATED language and preserve user/project instruction precedence. |
| Issue handoffs become bulky plans | Future agents follow stale steps | Put exact executable steps in `writing-plans` after current source inspection. |
| Trigger eval harnesses produce flaky confidence | Agents over-trust nondeterministic tests | Keep harnesses in research issue `043` before implementation. |
| Schema drift | New skills lose GOATED metadata richness | Make lean schema preservation explicit in every relevant issue. |

## Resolved Decisions

| Decision | Outcome | Source |
| --- | --- | --- |
| Should V1 ever include runtime bootstrap/plugin automation that changes agent behavior beyond docs-first installation? | No. V1 allows narrow adapter notes only; runtime automation requires future scoped work. | `docs/adr/0001-v1-runtime-bootstrap-and-adapter-automation.md` and `issues/archive/035-decide-runtime-bootstrap-and-adapter-automation.md` |
| Which skill-trigger eval harness style, if any, is worth adding to GOATED? | No live harness for V1. Keep docs-only/static guidance and manual scenario examples now; revisit future trigger-evaluation tooling through a future PRD after real usage reveals recurring failures. | `issues/archive/043-research-skill-trigger-eval-harnesses.md` |

## Open Questions

| Question | Owner | Needed before |
| --- | --- | --- |
| None currently. | Not applicable | Not applicable |

## Source Evidence

- User-approved implementation plan in this session.
- `AGENT.md`
- `CONTEXT.md`
- `docs/adr/0001-v1-runtime-bootstrap-and-adapter-automation.md`
- `issues/archive/035-decide-runtime-bootstrap-and-adapter-automation.md`
- `issues/prd-goated-ai-skills-v1-public-core.md`
- `issues/prd-goated-ai-skills-v1-additions.md`
- Superpowers repo: https://github.com/obra/superpowers
- Superpowers skill links listed in the Source Fit Matrix.
- Matt Pocock `write-a-skill`: https://github.com/mattpocock/skills/tree/main/skills/productivity/write-a-skill
