# PRD: GOATED AI Skills Documentation Writer

## Status

Approved and implemented by `issues/archive/049-implement-documentation-writer-manuals-first.md` on 2026-05-27.

## Problem

At PRD creation, GOATED AI Skills already included workflows for PRDs, implementation planning, review, verification, and documentation drift sync, but did not yet have a dedicated skill for intentionally authoring durable user-facing documentation before or alongside product delivery.

Without a planned documentation authoring skill, agents can overuse `doc-sync` for work it was not designed to own. `doc-sync` is the right closeout workflow for checking whether changed behavior made docs stale, but it is not a full manual-writing workflow for creating user manuals, operator guides, onboarding guides, durable product docs, or AI-optimized companion docs from source evidence and audience needs.

`documentation-writer` should fill that gap with a manuals-first workflow that helps agents produce useful durable documentation while preserving GOATED's public-safe, framework-agnostic, self-contained skill model.

## Audience

- Agent users who want source-grounded manuals, operator guides, onboarding guides, and durable product documentation for a target project.
- Maintainers and contributors who need a clear v1 boundary for reviewing or extending `skills/engineering/documentation-writer/`.
- Future agents reviewing or extending the implemented `documentation-writer` skill.
- AI agents and models that benefit from separate AI-optimized companion docs designed for fast context loading and task routing.

## Goals

- Add a `documentation-writer` engineering skill for planned, source-grounded documentation authoring.
- Scope v1 to manuals-first durable documentation: user manuals, operator guides, onboarding guides, durable product docs, and separate AI-optimized companion docs when requested or useful.
- Keep `documentation-writer` distinct from `doc-sync`: author planned docs first, then use `doc-sync` when changed behavior or existing docs may have drifted.
- Require audience, doc type, source evidence, assumptions, gaps, and verification to be explicit before claiming a document is ready.
- Preserve GOATED skill requirements: portable, public-safe, self-contained after installation, lean-schema-compatible, support-file-friendly, subagent-aware, and single-agent-compatible.

## Non-Goals

- This PRD issue did not implement `documentation-writer`; implementation was completed by `issues/archive/049-implement-documentation-writer-manuals-first.md`.
- Do not create additional `documentation-writer` skill folders or alternate implementations without a new approved issue.
- Do not replace `doc-sync` or turn `documentation-writer` into a drift-sync closeout workflow.
- Do not implement documentation webpages, static site generation, hosting, publishing, or deployment in v1.
- Do not list planned future skills as implemented in `README.md`, `docs/how-to-use.md`, or category READMEs before their implementation issue is complete.
- Do not add private project names, credentials, client data, sensitive personal context, raw private transcripts, or private workflow assumptions to public main.
- Do not require installed skills to depend on this source repo's root `AGENT.md`, `CONTEXT.md`, issue files, or chat history at runtime.

## Requirements

| Requirement | Priority | Notes |
| --- | --- | --- |
| Create a manuals-first authoring skill | Must | `documentation-writer` v1 should create or substantially revise user manuals, operator guides, onboarding guides, and durable product documentation. |
| Support AI-optimized companion docs | Must | The skill should support separate companion documents for AI agents and models when requested or useful, rather than mixing model-focused notes into every human manual. |
| Gather source evidence before writing | Must | The workflow should inspect relevant existing docs, source files, product notes, architecture notes, issues, PRDs, support notes, commands, or user-provided context before drafting. |
| Choose documentation location from project conventions | Must | Prefer a target project's existing docs conventions. If no convention exists, choose a simple durable Markdown default and record the assumption. |
| Keep human audience first | Must | Human manuals and guides should remain readable, task-oriented, and audience-specific. AI companion docs should optimize for agent context loading, not replace human documentation. |
| Separate from `doc-sync` | Must | `documentation-writer` authors planned docs. `doc-sync` remains responsible for documentation drift after behavior, interfaces, architecture, standards, config, tests, or docs change. |
| Preserve GOATED skill shape | Must | The skill must follow the lean schema, stay self-contained after installation, and use support files when templates, examples, checklists, or QA rubrics would bloat `SKILL.md`. |
| Include delegation and fallback behavior | Must | The skill should support bounded subagent passes for source summarization, outline review, audience fit, AI-doc usefulness, and documentation QA, while remaining usable by a single agent. |
| Record assumptions and open questions | Must | If audience, product behavior, source truth, doc owner, or target location is unclear, the workflow should ask or record an explicit assumption instead of inventing facts. |
| Verify documentation output | Must | The output contract should include docs created or updated, source evidence used, target audience, scope, verification performed, skipped checks, and remaining gaps. |
| Defer websites and static sites | Must | Webpages, static-site generation, hosting, and publishing belong to a future phase or separate PRD after maintainer approval. |

## Relationship To `doc-sync`

`documentation-writer` and `doc-sync` should remain companion skills with different entry points.

| Skill | Primary trigger | Primary output | Not responsible for |
| --- | --- | --- | --- |
| `documentation-writer` | User asks to create or substantially revise planned durable documentation. | Manuals, operator guides, onboarding guides, product docs, and optional separate AI-optimized companion docs grounded in source evidence. | Post-change drift audit across existing docs, broad catalog sync, or claiming all docs remain current after unrelated behavior changes. |
| `doc-sync` | Behavior, interfaces, architecture, standards, configuration, tests, or public docs may have drifted. | Drift report and required updates to keep existing durable docs aligned with changed facts. | Creating a full manual-writing workflow or deciding the audience, structure, and scope of a new planned guide from scratch. |

After `documentation-writer` creates or changes durable docs, agents should route to `doc-sync` only when the work may make other docs stale, such as catalog references, operator guidance, standards docs, README summaries, or public workflow descriptions.

## AI-Optimized Companion Docs

V1 should include AI-optimized companion docs as a supported documentation type, not as mandatory output for every manual.

These companion docs should be separate artifacts by default. They should summarize project or product context in a structure that agents can load quickly, such as purpose, audience, source-of-truth links, key workflows, constraints, glossary, common tasks, known gaps, verification commands, and safe next reads. They should not hide private context, duplicate entire human manuals, or become the only place where important product behavior is documented.

The skill should create an AI companion doc when the user asks for it, when a project has repeated agent work, or when the documentation set would benefit from a model-oriented read path. For small documents, the skill may instead report that a separate AI companion doc is unnecessary and explain why.

## Implementation Notes

- The skill was implemented at `skills/engineering/documentation-writer/SKILL.md` by `issues/archive/049-implement-documentation-writer-manuals-first.md`.
- Use `category: engineering`, `classification: portable`, and `status: wip` unless the implementation issue or maintainer decision changes the convention.
- Keep the `SKILL.md` lean. Put detailed document templates, outline examples, AI companion doc rubrics, and manual QA checklists in directly linked `references/` files if they materially improve the skill.
- Recommended soft dependencies for the skill include `session-start-progressive-disclosure`, `grill-with-docs`, `write-a-prd`, `doc-sync`, and `verification-before-completion`.
- The workflow should start by confirming the documentation purpose, audience, doc type, source evidence, location convention, and freshness expectations.
- The output contract should include created or updated paths, audience, source evidence, assumptions, skipped evidence, verification, relationship to `doc-sync`, and remaining gaps.
- Documentation webpages, static site generation, deployment, publishing, generated navigation, and hosting integrations require a future PRD or explicit maintainer approval.

## Acceptance Criteria

- [x] `skills/engineering/documentation-writer/SKILL.md` is created only by `issues/archive/049-implement-documentation-writer-manuals-first.md` after this PRD is reviewed and approved.
- [x] The implemented skill follows the GOATED lean schema and remains self-contained after installation.
- [x] The implemented skill is scoped to manuals-first durable documentation: user manuals, operator guides, onboarding guides, durable product docs, and optional separate AI-optimized companion docs.
- [x] The workflow gathers source evidence before writing and records assumptions, gaps, and unresolved product questions.
- [x] The workflow chooses documentation locations from target-project conventions before falling back to a simple durable Markdown default.
- [x] The workflow distinguishes planned documentation authoring from `doc-sync` drift handling.
- [x] The output contract covers created or updated docs, source evidence, audience, scope, verification, `doc-sync` relationship, and remaining gaps.
- [x] Delegation supports bounded source summarization, outline review, audience fit review, AI companion doc review, and documentation QA.
- [x] Guardrails prevent private data, credentials, raw private transcripts, unverified product claims, and documentation website or static-site generation in v1.
- [x] `README.md`, `docs/how-to-use.md`, and `skills/engineering/README.md` list `documentation-writer` only after issue 049 implements the skill.

## Testing And Verification

- Manually review `skills/engineering/documentation-writer/SKILL.md` against the lean schema after issue 049 creates it.
- Check that the skill can author at least one human-facing manual or guide and can decide whether a separate AI-optimized companion doc is warranted.
- Run targeted searches for `documentation-writer`, `doc-sync`, `manual`, `operator guide`, `onboarding guide`, `AI-optimized`, `webpage`, `static site`, and stale planned-or-implemented wording.
- Confirm no documentation webpage, static-site generation, deployment, publishing, or hosting workflow is introduced in v1.
- Confirm public catalog docs mention the skill only after implementation is complete.
- Use manual Markdown review as the expected proof for this Markdown-only PRD and docs-only implementation, unless later tooling is added.

## Risks And Mitigations

| Risk | Impact | Mitigation |
| --- | --- | --- |
| The skill becomes a clone of `doc-sync` | Agents blur planned authoring and drift cleanup | Keep trigger, output, and non-goal boundaries explicit in the PRD and `SKILL.md`. |
| Manuals become too agent-centric | Human readers get awkward or overly mechanical docs | Keep human manuals audience-first and put AI-oriented context in separate companion docs by default. |
| AI companion docs become private scratchpads | Public docs could leak private context or stale assumptions | Require public-safe review, source evidence, and explicit gaps; forbid private notes, credentials, and raw private transcripts. |
| Static-site scope creeps into v1 | The first release expands into tooling, hosting, and deployment decisions | Treat webpages and static sites as non-goals unless a future PRD approves them. |
| The `SKILL.md` becomes too large | Agents load too much context before acting | Move templates, examples, and QA checklists into linked `references/` files. |
| Agents overclaim documentation readiness | Users trust docs that were not checked against source evidence | Require verification evidence, skipped checks, and remaining gaps in the output contract. |

## Resolved Implementation Questions

| Question | Owner | Resolution |
| --- | --- | --- |
| What default filename convention should AI-optimized companion docs use when no project convention exists? | Maintainer | Resolved for issue 049: use `docs/agents/<topic>-ai-guide.md`, avoiding `context` naming because context docs already carry durable project language and source-routing meaning. |
| Should v1 include reusable templates for manuals, operator guides, onboarding guides, product docs, and AI companion docs under `references/`? | Maintainer or issue 049 implementer | Resolved for issue 049: include one compact support reference for patterns and QA instead of heavy templates. |
| Should runbooks and troubleshooting guides be named explicitly as operator-guide variants? | Maintainer or issue 049 implementer | Resolved for issue 049: name them as operator-guide variants. |

## Follow-Up Issue

The implementation issue is `issues/archive/049-implement-documentation-writer-manuals-first.md`.

Issue 049 was unblocked on 2026-05-27 after this PRD received maintainer approval and is archived after implementation. Issue 048 created the draft PRD and is archived at `issues/archive/048-draft-documentation-writer-prd.md`; that archive state is not a remaining blocker.

## Source Evidence

- `AGENT.md` - source-repo maintainer contract, public boundary, self-contained installed skill rule, and subagent-aware expectations.
- `CONTEXT.md` - GOATED domain language for source repo, installed skills, target projects, durable artifacts, public-safe boundaries, and skill anatomy.
- `README.md` - public distribution model, docs-first installation model, three-layer model, and implemented skill catalog behavior.
- `skills/README.md` - lean schema, support-file policy, delegation contract, and implementation boundary.
- `skills/engineering/README.md` - engineering category scope and current implemented skill inventory.
- `skills/engineering/doc-sync/SKILL.md` - existing documentation drift workflow that `documentation-writer` must not duplicate.
- `skills/engineering/write-a-prd/SKILL.md` - PRD output shape and source-grounded planning behavior.
- `docs/how-to-use.md` - human operator manual for installed GOATED AI Skills and current delivery pipeline.
- `issues/archive/016-doc-sync.md` - original `doc-sync` implementation contract.
- `issues/archive/048-draft-documentation-writer-prd.md` - implementation contract for this PRD draft.
- `issues/archive/049-implement-documentation-writer-manuals-first.md` - implementation issue.
- GitHub, "Tools and techniques for effective code documentation," July 29, 2024 - supports the distinction between high-level documentation such as user manuals, audience-first documentation strategy, docs-as-code/version-control practices, and static hosting as a tool choice rather than v1 scope.
- Write the Docs, "How to write software documentation" - supports audience-specific documentation, starting simple, avoiding FAQ sprawl, and giving users enough information without overloading them.
