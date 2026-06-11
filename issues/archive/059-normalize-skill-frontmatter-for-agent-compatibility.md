## Parent PRD

No separate parent PRD. This issue continues the user-approved 2026-06-11 GOATED AI Skills compatibility and token-footprint cleanup agenda after `issues/053-optimize-hotspot-skill-token-footprint.md`, `issues/054-optimize-code-security-review-token-footprint.md`, `issues/055-optimize-architecture-vocabulary-token-footprint.md`, `issues/056-optimize-reference-read-gate-token-footprint.md`, `issues/057-optimize-delegation-boilerplate-token-footprint.md`, and `issues/058-optimize-depends-on-frontmatter-token-footprint.md`.

## Type

AFK

## What to build

Normalize implemented `SKILL.md` frontmatter for major Agent Skills consumers while preserving GOATED behavior in standard Markdown body sections.

The target top-level frontmatter shape for every implemented skill is:

```yaml
---
name: <skill-name>
description: <discovery-focused description>
metadata:
  goated-category: <agent-workflows | engineering | productivity>
---
```

Remove custom GOATED-only top-level fields from all 30 implemented `SKILL.md` files:

- `category`
- `classification`
- `status`
- `triggers`
- `outputs`
- `depends_on`
- `adapters`

Migrate only behavior that still matters:

- Keep `goated-category` under standard `metadata` so the public category label travels with copied skills.
- Cut `classification` and `status`; do not preserve them in frontmatter.
- Cut `triggers`; rely on `description` for discovery and body workflow text for workflow constraints.
- Cut `outputs`; preserve unique output behavior in `## Output Contract` only where the body does not already cover it.
- Move the current Issue `058` compressed `depends_on` wording into a body `## Dependencies` section, preserving wording word-for-word except mechanical YAML-to-Markdown formatting.
- Cut `adapters` entirely; do not replace the generic "usable everywhere" map with body text.

Update schema-contract docs and skill-creation guidance so future skills do not recreate the old frontmatter shape.

## Grill decision

The user noticed VS Code Agent warnings for unsupported fields such as `adapters` and asked whether Codex behaves the same way. The docs-grounded answer is:

- Codex requires `name` and `description` in `SKILL.md`, discovers skills from `name`, `description`, and file path, and places Codex-specific UI/dependency metadata in `agents/openai.yaml`.
- The open Agent Skills spec supports top-level `name`, `description`, optional `license`, `compatibility`, `metadata`, and experimental `allowed-tools`.
- VS Code supports a narrower validator-recognized frontmatter set and warns on GOATED-only custom top-level fields.

The selected posture is **standards-first top-level frontmatter**:

- Use only broadly compatible top-level fields needed by the suite now.
- Keep GOATED behavior in Markdown body sections where all consumers can read it after activation.
- Avoid framework-specific invocation controls or metadata files in this slice.
- Treat `metadata` as public and potentially model-visible; do not put private data, routing behavior, guardrails, or dependency semantics there.

## Source grounding

- OpenAI Codex Agent Skills docs: `SKILL.md` must include `name` and `description`; Codex starts with each skill's `name`, `description`, and file path for progressive disclosure; optional Codex app metadata belongs in `agents/openai.yaml`.
  - https://developers.openai.com/codex/skills
- Agent Skills specification: supported frontmatter includes required `name` and `description`, optional `license`, `compatibility`, `metadata`, and experimental `allowed-tools`; `metadata` is arbitrary key-value data for additional properties.
  - https://agentskills.io/specification
- VS Code Agent Skills docs: VS Code frontmatter support centers `name`, `description`, and VS Code-specific optional fields such as `argument-hint`, `user-invocable`, `disable-model-invocation`, and `context`; invalid names can fail to load and unsupported fields produce warnings.
  - https://code.visualstudio.com/docs/agent-customization/agent-skills
- Local repo docs currently require the older GOATED schema and therefore must be updated in this issue.

## Settled decisions

| Decision | Outcome |
| --- | --- |
| Top-level schema | `name`, `description`, and `metadata.goated-category` only |
| `category` | Move to `metadata.goated-category` |
| `classification` | Cut |
| `status` | Cut |
| `triggers` | Cut; rely on `description` and body constraints |
| `outputs` | Cut; preserve unique behavior in `## Output Contract` only when not already covered |
| `depends_on` | Move to body `## Dependencies`, preserving Issue `058` wording word-for-word except mechanical Markdown placement |
| `adapters` | Cut entirely |
| `metadata` visibility | Treat as public, model-visible, and non-behavioral |
| VS Code-only fields | Excluded |
| Codex `agents/openai.yaml` | Excluded |
| `allowed-tools` | Excluded |
| New text style | Use `goated-prompt` and the IDK glossary as style references for compact, direct, action-oriented wording |
| Tooling/schema validator | Excluded for this slice |
| Issue type | AFK |

## Recommended first reads

- `AGENT.md`
- `CONTEXT.md`
- `skills/README.md`
- `docs/agents/context-matrix.md`
- `docs/agents/project-standards.md`
- `docs/how-to-use.md`
- `issues/058-optimize-depends-on-frontmatter-token-footprint.md`
- `skills/productivity/goated-prompt/SKILL.md`
- `skills/productivity/goated-prompt/references/idk-glossary.md`
- `skills/agent-workflows/framework-agnostic-skill-creator/SKILL.md`
- `skills/agent-workflows/framework-agnostic-skill-creator/references/source-package-audit.md`
- `skills/agent-workflows/framework-agnostic-skill-creator/references/skill-evaluation.md`
- `skills/agent-workflows/framework-agnostic-skill-creator/references/proposal-and-report-templates.md`
- Current implemented `SKILL.md` files, opened only as needed for migration and review.
- `skills/engineering/verification-before-completion/SKILL.md`

## Relevant source links

- `AGENT.md` - maintainer contract, public boundary, installed-skill self-containment, and editing rules.
- `CONTEXT.md` - current source-repo definitions for lean schema, skill adapters, installed skills, dependencies, triggers, outputs, and categories.
- `skills/README.md` - current schema contract and body-section guidance that must be updated.
- `docs/agents/project-standards.md` - documented standard that currently records the old required frontmatter fields.
- `docs/how-to-use.md` - human operator guide references to current skill creation inputs and WIP status language.
- `skills/agent-workflows/framework-agnostic-skill-creator/SKILL.md` - workflow that currently instructs future agents to create the old schema.
- `skills/agent-workflows/framework-agnostic-skill-creator/references/source-package-audit.md` - source audit guidance that mentions trigger/output/dependency/adapter extraction.
- `skills/agent-workflows/framework-agnostic-skill-creator/references/skill-evaluation.md` - evaluation checklist that currently checks old frontmatter fields.
- `skills/agent-workflows/framework-agnostic-skill-creator/references/proposal-and-report-templates.md` - templates that currently ask for old schema decisions.
- `docs/adr/0001-v1-runtime-bootstrap-and-adapter-automation.md` - ADR mentions small framework compatibility notes in `adapters` fields and may need a narrow historical/current wording update.
- OpenAI Codex Agent Skills docs - external compatibility source.
- Agent Skills specification - external compatibility source.
- VS Code Agent Skills docs - external compatibility source and warning rationale.

## Acceptance criteria

- [ ] All 30 implemented `SKILL.md` files are audited.
- [ ] Every implemented `SKILL.md` keeps top-level `name`.
- [ ] Every implemented `SKILL.md` keeps top-level `description`.
- [ ] Every implemented `SKILL.md` has top-level `metadata.goated-category` with one of `agent-workflows`, `engineering`, or `productivity`.
- [ ] No implemented `SKILL.md` has top-level `category`.
- [ ] No implemented `SKILL.md` has top-level `classification`.
- [ ] No implemented `SKILL.md` has top-level `status`.
- [ ] No implemented `SKILL.md` has top-level `triggers`.
- [ ] No implemented `SKILL.md` has top-level `outputs`.
- [ ] No implemented `SKILL.md` has top-level `depends_on`.
- [ ] No implemented `SKILL.md` has top-level `adapters`.
- [ ] No VS Code-only fields such as `argument-hint`, `user-invocable`, `disable-model-invocation`, or `context` are added.
- [ ] No Codex `agents/openai.yaml` files are added.
- [ ] No `allowed-tools` frontmatter is added.
- [ ] No plugin manifest, generated manifest, installer automation, hook, CI check, formatter, schema validator, token dashboard, eval harness, or background automation is introduced.
- [ ] Current Issue `058` compressed `depends_on` `soft` entries are preserved word-for-word when moved into body `## Dependencies` sections, except mechanical YAML-to-Markdown formatting.
- [ ] Current Issue `058` compressed `depends_on` `fallback` sentences are preserved word-for-word when moved into body `## Dependencies` sections, except mechanical YAML-to-Markdown formatting.
- [ ] `hard: []` dependency state becomes a clear Markdown equivalent such as `Hard: None.` without implying a new hard dependency.
- [ ] `## Dependencies` sections are placed consistently, preferably after `## Inputs` when present or after `## Purpose` when `## Inputs` is absent.
- [ ] No dependency behavior is moved into `metadata`.
- [ ] No dependency behavior is moved into repo-level, category-level, or cross-skill shared references.
- [ ] Unique output behavior from removed `outputs` lists is preserved in `## Output Contract` only where the body does not already cover it.
- [ ] `description` remains discovery-focused and is not expanded into workflow detail to compensate for removed `triggers`.
- [ ] Generic adapter usability text is not recreated in the body.
- [ ] `compatibility` is not added unless a skill has a real per-skill environment or framework constraint discovered during implementation; adding any `compatibility` field must be explicitly justified in the ledger.
- [ ] `metadata` remains small, public-safe, scalar, and non-behavioral.
- [ ] Installed skills remain self-contained after installation and do not depend on this source repo's root docs at runtime.
- [ ] Schema-contract docs are updated so future agents do not recreate the old frontmatter shape.
- [ ] `framework-agnostic-skill-creator` and relevant references are updated to create and evaluate the normalized schema.
- [ ] Old body concepts such as trigger, output, dependency, and adapter remain usable as workflow ideas where appropriate, but no longer imply custom top-level YAML fields.
- [ ] Any new text written for skill bodies, schema docs, skill-creator guidance, issue evidence, or migration notes uses the `goated-prompt` / IDK style: compact, direct, information-dense, action-oriented, and not ornamental.
- [ ] The IDK style constraint does not override the word-for-word preservation requirement for Issue `058` dependency text.
- [ ] The implementation records a migration ledger for all 30 implemented `SKILL.md` files.
- [ ] The final diff is reviewed for behavior preservation, not only warning removal or token reduction.

## Expected proof

- Record a migration ledger for all 30 implemented `SKILL.md` files with:
  - file path;
  - original category and new `metadata.goated-category`;
  - removed frontmatter fields;
  - `## Dependencies` placement;
  - whether `outputs` had unique behavior requiring body preservation;
  - whether `adapters` was removed with no replacement;
  - risk notes.
- Targeted scan proving all implemented `SKILL.md` files have top-level `name`, `description`, and `metadata.goated-category`.
- Targeted scan proving no implemented `SKILL.md` still has top-level `category`, `classification`, `status`, `triggers`, `outputs`, `depends_on`, or `adapters`.
- Targeted scan proving no VS Code-only fields, `allowed-tools`, or Codex `agents/openai.yaml` files were introduced.
- Targeted review comparing moved dependency wording against the pre-migration Issue `058` wording.
- Manual review of every new `## Dependencies` section for Markdown clarity and unchanged dependency semantics.
- Manual review of `## Output Contract` sections where removed `outputs` carried unique behavior.
- Targeted doc-drift scan for old schema instructions in `README.md`, `CONTEXT.md`, `docs/`, and `skills/`.
- Manual style pass confirming newly written text follows the `goated-prompt` / IDK style where new wording was required, while preserved Issue `058` dependency text remains unchanged.
- Manual public-boundary pass for private paths, credentials, client data, private notes, sensitive personal context, secrets, or real user data.
- Manual check that no runtime bootstrap, plugin manifest, generated index, automation, validator, CI, token dashboard, or eval harness was added.
- Use `verification-before-completion` before claiming this issue is implemented, behavior-preserving, or ready for git review.

## Implementation evidence

Migration snapshot: `.local/issue-059-frontmatter-before.json` captured the pre-edit frontmatter for all 30 implemented skills before rewriting. The snapshot is an ignored local verification artifact, not a runtime dependency.

Frontmatter migration summary:

- Implemented `SKILL.md` files migrated: 30.
- New top-level shape: `name`, `description`, `metadata.goated-category`.
- Removed top-level fields from every implemented skill: `category`, `classification`, `status`, `triggers`, `outputs`, `depends_on`, and `adapters`.
- `metadata.goated-category` values preserved the original public category for every skill.
- `## Dependencies` was inserted after `## Inputs` in every skill.
- `hard: []` became `Hard: None.` in every skill.
- `soft` entries became Markdown bullets with the same text.
- `fallback` sentences became `Fallback:` lines with the same sentence.
- All 30 skills already had body `## Output Contract` sections; no removed `outputs` list carried unique behavior that required new body text.
- Generic `adapters` maps were removed without replacement. No per-skill compatibility exception was found.

### Migration ledger

| File | Category -> metadata | Removed fields | Dependencies placement | Output preservation | Adapters | Risk notes |
| --- | --- | --- | --- | --- | --- | --- |
| `skills/agent-workflows/agent-instructions-integrator/SKILL.md` | `agent-workflows` -> `agent-workflows` | `category`, `classification`, `status`, `triggers`, `outputs`, `depends_on`, `adapters` | after ## Inputs | Body `## Output Contract` already covers removed outputs; no added output text. | Removed with no replacement. | Dependency wording moved verbatim from Issue 058 frontmatter; no compatibility exception. |
| `skills/agent-workflows/context-matrix-map/SKILL.md` | `agent-workflows` -> `agent-workflows` | `category`, `classification`, `status`, `triggers`, `outputs`, `depends_on`, `adapters` | after ## Inputs | Body `## Output Contract` already covers removed outputs; no added output text. | Removed with no replacement. | Dependency wording moved verbatim from Issue 058 frontmatter; no compatibility exception. |
| `skills/agent-workflows/framework-agnostic-skill-creator/SKILL.md` | `agent-workflows` -> `agent-workflows` | `category`, `classification`, `status`, `triggers`, `outputs`, `depends_on`, `adapters` | after ## Inputs | Body `## Output Contract` already covers removed outputs; no added output text. | Removed with no replacement. | Dependency wording moved verbatim from Issue 058 frontmatter; no compatibility exception. |
| `skills/agent-workflows/handoff/SKILL.md` | `agent-workflows` -> `agent-workflows` | `category`, `classification`, `status`, `triggers`, `outputs`, `depends_on`, `adapters` | after ## Inputs | Body `## Output Contract` already covers removed outputs; no added output text. | Removed with no replacement. | Dependency wording moved verbatim from Issue 058 frontmatter; no compatibility exception. |
| `skills/agent-workflows/project-context-calibration/SKILL.md` | `agent-workflows` -> `agent-workflows` | `category`, `classification`, `status`, `triggers`, `outputs`, `depends_on`, `adapters` | after ## Inputs | Body `## Output Contract` already covers removed outputs; no added output text. | Removed with no replacement. | Dependency wording moved verbatim from Issue 058 frontmatter; no compatibility exception. |
| `skills/agent-workflows/project-standards-calibration/SKILL.md` | `agent-workflows` -> `agent-workflows` | `category`, `classification`, `status`, `triggers`, `outputs`, `depends_on`, `adapters` | after ## Inputs | Body `## Output Contract` already covers removed outputs; no added output text. | Removed with no replacement. | Dependency wording moved verbatim from Issue 058 frontmatter; no compatibility exception. |
| `skills/agent-workflows/session-start-progressive-disclosure/SKILL.md` | `agent-workflows` -> `agent-workflows` | `category`, `classification`, `status`, `triggers`, `outputs`, `depends_on`, `adapters` | after ## Inputs | Body `## Output Contract` already covers removed outputs; no added output text. | Removed with no replacement. | Dependency wording moved verbatim from Issue 058 frontmatter; no compatibility exception. |
| `skills/agent-workflows/using-goated-ai-skills/SKILL.md` | `agent-workflows` -> `agent-workflows` | `category`, `classification`, `status`, `triggers`, `outputs`, `depends_on`, `adapters` | after ## Inputs | Body `## Output Contract` already covers removed outputs; no added output text. | Removed with no replacement. | Dependency wording moved verbatim from Issue 058 frontmatter; no compatibility exception. |
| `skills/engineering/architecture-design-map/SKILL.md` | `engineering` -> `engineering` | `category`, `classification`, `status`, `triggers`, `outputs`, `depends_on`, `adapters` | after ## Inputs | Body `## Output Contract` already covers removed outputs; no added output text. | Removed with no replacement. | Dependency wording moved verbatim from Issue 058 frontmatter; no compatibility exception. |
| `skills/engineering/code-security-review/SKILL.md` | `engineering` -> `engineering` | `category`, `classification`, `status`, `triggers`, `outputs`, `depends_on`, `adapters` | after ## Inputs | Body `## Output Contract` already covers removed outputs; no added output text. | Removed with no replacement. | Dependency wording moved verbatim from Issue 058 frontmatter; no compatibility exception. |
| `skills/engineering/commit-message/SKILL.md` | `engineering` -> `engineering` | `category`, `classification`, `status`, `triggers`, `outputs`, `depends_on`, `adapters` | after ## Inputs | Body `## Output Contract` already covers removed outputs; no added output text. | Removed with no replacement. | Dependency wording moved verbatim from Issue 058 frontmatter; no compatibility exception. |
| `skills/engineering/diagnose/SKILL.md` | `engineering` -> `engineering` | `category`, `classification`, `status`, `triggers`, `outputs`, `depends_on`, `adapters` | after ## Inputs | Body `## Output Contract` already covers removed outputs; no added output text. | Removed with no replacement. | Dependency wording moved verbatim from Issue 058 frontmatter; no compatibility exception. |
| `skills/engineering/doc-sync/SKILL.md` | `engineering` -> `engineering` | `category`, `classification`, `status`, `triggers`, `outputs`, `depends_on`, `adapters` | after ## Inputs | Body `## Output Contract` already covers removed outputs; no added output text. | Removed with no replacement. | Dependency wording moved verbatim from Issue 058 frontmatter; no compatibility exception. |
| `skills/engineering/documentation-cleanup/SKILL.md` | `engineering` -> `engineering` | `category`, `classification`, `status`, `triggers`, `outputs`, `depends_on`, `adapters` | after ## Inputs | Body `## Output Contract` already covers removed outputs; no added output text. | Removed with no replacement. | Dependency wording moved verbatim from Issue 058 frontmatter; no compatibility exception. |
| `skills/engineering/documentation-writer/SKILL.md` | `engineering` -> `engineering` | `category`, `classification`, `status`, `triggers`, `outputs`, `depends_on`, `adapters` | after ## Inputs | Body `## Output Contract` already covers removed outputs; no added output text. | Removed with no replacement. | Dependency wording moved verbatim from Issue 058 frontmatter; no compatibility exception. |
| `skills/engineering/grill-with-docs/SKILL.md` | `engineering` -> `engineering` | `category`, `classification`, `status`, `triggers`, `outputs`, `depends_on`, `adapters` | after ## Inputs | Body `## Output Contract` already covers removed outputs; no added output text. | Removed with no replacement. | Dependency wording moved verbatim from Issue 058 frontmatter; no compatibility exception. |
| `skills/engineering/improve-codebase-architecture/SKILL.md` | `engineering` -> `engineering` | `category`, `classification`, `status`, `triggers`, `outputs`, `depends_on`, `adapters` | after ## Inputs | Body `## Output Contract` already covers removed outputs; no added output text. | Removed with no replacement. | Dependency wording moved verbatim from Issue 058 frontmatter; no compatibility exception. |
| `skills/engineering/plan-codebase-architecture/SKILL.md` | `engineering` -> `engineering` | `category`, `classification`, `status`, `triggers`, `outputs`, `depends_on`, `adapters` | after ## Inputs | Body `## Output Contract` already covers removed outputs; no added output text. | Removed with no replacement. | Dependency wording moved verbatim from Issue 058 frontmatter; no compatibility exception. |
| `skills/engineering/prd-to-issues/SKILL.md` | `engineering` -> `engineering` | `category`, `classification`, `status`, `triggers`, `outputs`, `depends_on`, `adapters` | after ## Inputs | Body `## Output Contract` already covers removed outputs; no added output text. | Removed with no replacement. | Dependency wording moved verbatim from Issue 058 frontmatter; no compatibility exception. |
| `skills/engineering/prototype/SKILL.md` | `engineering` -> `engineering` | `category`, `classification`, `status`, `triggers`, `outputs`, `depends_on`, `adapters` | after ## Inputs | Body `## Output Contract` already covers removed outputs; no added output text. | Removed with no replacement. | Dependency wording moved verbatim from Issue 058 frontmatter; no compatibility exception. |
| `skills/engineering/receiving-code-review/SKILL.md` | `engineering` -> `engineering` | `category`, `classification`, `status`, `triggers`, `outputs`, `depends_on`, `adapters` | after ## Inputs | Body `## Output Contract` already covers removed outputs; no added output text. | Removed with no replacement. | Dependency wording moved verbatim from Issue 058 frontmatter; no compatibility exception. |
| `skills/engineering/standards-and-spec-review/SKILL.md` | `engineering` -> `engineering` | `category`, `classification`, `status`, `triggers`, `outputs`, `depends_on`, `adapters` | after ## Inputs | Body `## Output Contract` already covers removed outputs; no added output text. | Removed with no replacement. | Dependency wording moved verbatim from Issue 058 frontmatter; no compatibility exception. |
| `skills/engineering/subagent-driven-development/SKILL.md` | `engineering` -> `engineering` | `category`, `classification`, `status`, `triggers`, `outputs`, `depends_on`, `adapters` | after ## Inputs | Body `## Output Contract` already covers removed outputs; no added output text. | Removed with no replacement. | Dependency wording moved verbatim from Issue 058 frontmatter; no compatibility exception. |
| `skills/engineering/tdd/SKILL.md` | `engineering` -> `engineering` | `category`, `classification`, `status`, `triggers`, `outputs`, `depends_on`, `adapters` | after ## Inputs | Body `## Output Contract` already covers removed outputs; no added output text. | Removed with no replacement. | Dependency wording moved verbatim from Issue 058 frontmatter; no compatibility exception. |
| `skills/engineering/verification-before-completion/SKILL.md` | `engineering` -> `engineering` | `category`, `classification`, `status`, `triggers`, `outputs`, `depends_on`, `adapters` | after ## Inputs | Body `## Output Contract` already covers removed outputs; no added output text. | Removed with no replacement. | Dependency wording moved verbatim from Issue 058 frontmatter; no compatibility exception. |
| `skills/engineering/write-a-prd/SKILL.md` | `engineering` -> `engineering` | `category`, `classification`, `status`, `triggers`, `outputs`, `depends_on`, `adapters` | after ## Inputs | Body `## Output Contract` already covers removed outputs; no added output text. | Removed with no replacement. | Dependency wording moved verbatim from Issue 058 frontmatter; no compatibility exception. |
| `skills/engineering/writing-plans/SKILL.md` | `engineering` -> `engineering` | `category`, `classification`, `status`, `triggers`, `outputs`, `depends_on`, `adapters` | after ## Inputs | Body `## Output Contract` already covers removed outputs; no added output text. | Removed with no replacement. | Dependency wording moved verbatim from Issue 058 frontmatter; no compatibility exception. |
| `skills/productivity/caveman/SKILL.md` | `productivity` -> `productivity` | `category`, `classification`, `status`, `triggers`, `outputs`, `depends_on`, `adapters` | after ## Inputs | Body `## Output Contract` already covers removed outputs; no added output text. | Removed with no replacement. | Dependency wording moved verbatim from Issue 058 frontmatter; no compatibility exception. |
| `skills/productivity/goated-prompt/SKILL.md` | `productivity` -> `productivity` | `category`, `classification`, `status`, `triggers`, `outputs`, `depends_on`, `adapters` | after ## Inputs | Body `## Output Contract` already covers removed outputs; no added output text. | Removed with no replacement. | Dependency wording moved verbatim from Issue 058 frontmatter; no compatibility exception. |
| `skills/productivity/grill-me/SKILL.md` | `productivity` -> `productivity` | `category`, `classification`, `status`, `triggers`, `outputs`, `depends_on`, `adapters` | after ## Inputs | Body `## Output Contract` already covers removed outputs; no added output text. | Removed with no replacement. | Dependency wording moved verbatim from Issue 058 frontmatter; no compatibility exception. |

Independent audit notes:

- Read-only schema audit confirmed current frontmatter fields are `name`, `description`, and `metadata.goated-category` on all 30 skills.
- Read-only behavior audit found no unique removed `outputs` behavior needing new body text.
- Read-only compatibility audit found no skill-specific environment constraint that justifies adding `compatibility:` now.
- Final schema/docs review found 30 audited skills, zero frontmatter violations, no `agents/openai.yaml`, and no blocking old-schema doc drift.
- Final behavior-preservation review confirmed dependency sections match the pre-edit snapshot exactly, 29 output contracts were unchanged, and the updated `framework-agnostic-skill-creator` output contract preserves behavior while replacing old schema terms.

Targeted verification notes:

- Schema script passed for all 30 implemented skills: top-level fields are `name`, `description`, and `metadata`; `metadata.goated-category` counts are `agent-workflows=8`, `engineering=19`, and `productivity=3`.
- Dependency preservation script passed: every current `## Dependencies` section matches the pre-edit `soft` and `fallback` text captured in `.local/issue-059-frontmatter-before.json`, with `Hard: None.` for prior `hard: []`.
- Forbidden-field scan found no top-level `category`, `classification`, `status`, `triggers`, `outputs`, `depends_on`, `adapters`, `allowed-tools`, `compatibility`, or VS Code-only fields in implemented `SKILL.md` files.
- File scan found no `agents/openai.yaml` or `openai.yaml` files.
- Old-schema drift scan found no remaining docs that require the removed rich frontmatter shape; remaining adapter-map mentions are explicit "do not recreate" guidance.
- Public-boundary scan found no user-specific absolute paths after sanitizing the installed-copy exclusion.
- `git diff --check` reported no whitespace errors; Git emitted line-ending warnings only.

## Blocked by

- None - the docs-grounded grill resolved the schema decisions, migration policy, exclusions, and proof expectations.

## User stories addressed

- As a GOATED skill maintainer, I can keep skill frontmatter compatible with major Agent Skills consumers without losing behavior.
- As a VS Code user, I can open GOATED `SKILL.md` files without warnings for GOATED-only top-level attributes.
- As a Codex user, I can rely on concise `name` and `description` discovery while the full workflow remains available after activation.
- As a future skill author, I can follow repo docs that teach the normalized schema instead of recreating old custom frontmatter.
- As a reviewer, I can verify the migration with a ledger, targeted scans, and wording-preservation checks.

## Implementation route

- Start by reading this issue, the recommended first reads, and current `git status --short`.
- Treat existing unrelated dirty files as out of scope unless they are directly required by this issue.
- Snapshot current frontmatter for all implemented `SKILL.md` files before editing so dependency wording can be compared after migration.
- Migrate frontmatter manually or with tightly reviewed small batches; do not use blind broad rewrites.
- Preserve the Issue `058` dependency wording exactly when moving it to Markdown:
  - YAML `soft` entries should become Markdown bullets with the same text.
  - YAML `fallback` should become a Markdown `Fallback:` line with the same sentence.
  - YAML `hard: []` may become `Hard: None.`
- Place `## Dependencies` after `## Inputs` when present; if no `## Inputs` section exists, place it after `## Purpose`.
- Compare removed `outputs` with existing `## Output Contract`; add only missing behavior-bearing bullets.
- Update schema docs and skill-creator guidance after the skill migration so the docs reflect the actual new shape.
- Write any new body, doc, ledger, or migration wording in the `goated-prompt` / IDK style: prefer compact action verbs, information-dense phrasing, and direct constraints over explanatory padding.
- Do not apply IDK restyling to Issue `058` dependency text that must be preserved word-for-word.
- Use subagents when available for bounded post-edit review:
  - one reviewer checks schema/field compatibility and doc drift;
  - one reviewer checks dependency wording preservation and output behavior preservation.
- Use `verification-before-completion` before closeout.

## Scope exclusions

- Do not add generated manifests, plugin packaging, installer automation, hooks, CI, formatters, schema validators, token dashboards, eval harnesses, or background jobs.
- Do not add Codex `agents/openai.yaml`.
- Do not add VS Code-only frontmatter fields.
- Do not add `allowed-tools`.
- Do not broadly rewrite body workflows.
- Do not compress or rephrase body sections beyond the required migration.
- Do not reword Issue `058` dependency text except for mechanical Markdown placement.
- Do not change skill names or folder paths.
- Do not change public category structure.
- Do not move completed issues to archive.
- Do not edit installed copies under user-home skill directories such as `%USERPROFILE%\.codex\skills`.
- Do not touch unrelated dirty docs or issue files from the existing working tree.
- Do not remove support files, references, scripts, or assets merely to reduce tokens.
- Do not make installed skills depend on this source repo's root `AGENT.md`, `README.md`, `CONTEXT.md`, issue files, `.local/` notes, or hidden chat history.

## Implementation notes

- Treat `metadata.goated-category` as public bookkeeping only, not a hidden instruction channel.
- `classification` and `status` can remain source concepts in docs only if needed historically, but they should no longer be per-skill top-level frontmatter fields.
- `trigger`, `output`, and `dependency` remain useful workflow concepts; this issue changes where they live, not whether skills may describe them.
- `adapters` was repeated boilerplate across all implemented skills and should be removed without replacement unless a future skill has a real compatibility caveat.
- If a real per-skill compatibility caveat appears during implementation, prefer a standard `compatibility:` field and record the exception in the migration ledger.
- Use `goated-prompt` and the IDK glossary as style inspiration for any newly written text. Favor focused verbs such as MOVE, REMOVE, UPDATE, PRESERVE, VALIDATE, and DOCUMENT when they reduce ambiguity. Do not force uppercase keywords into prose where ordinary wording is clearer.
- The purpose is compatibility and schema normalization first. Token savings are welcome but not the target and should not justify behavior loss.

## Follow-up candidates

Carried forward from Issue `058`:

- Trim `verification-before-completion` repetition only where a skill repeats the same closeout gate multiple times.
- Treat TDD guardrail compression as a separate behavior-sensitive pass because the horizontal-slice warning is intentionally behavior-shaping.
- Consider a tiny before/after eval suite for representative skill outputs before applying the optimization style broadly.

Additional follow-ups after Issue `059`:

- Add a lightweight schema validation script or CI check after the normalized schema settles.
- Consider whether any heavy skill should opt into VS Code `context: fork` in a separate behavior-design issue.
- Consider Codex `agents/openai.yaml` only for future plugin or marketplace packaging work, not for local source-library normalization.
- Revisit suite-wide body token optimization only after schema migration is complete and verified.
