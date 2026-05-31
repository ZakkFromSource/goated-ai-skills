## Parent PRD

No separate parent PRD. This issue is based on the user-approved 2026-05-31 implementation plan for adding `goated-prompt`.

## Type

AFK

## What to build

Implement `goated-prompt` under `skills/productivity/`.

The skill should transform raw user requests into high-quality prompts in two harmonized modes:

- **GOATED Prompt mode** rewrites a request so it works cleanly with the existing GOATED AI Skills framework, including likely route, context needs, assumptions, and handoff to companion skills when appropriate.
- **Reusable Prompt mode** rewrites any raw request into a precise, reusable prompt for AI coding assistants or reasoning models.

The skill should preserve the useful ideas from the source prompt and course-note evidence: prompt type classification, context/model/prompt alignment, IDK-style action/detail language, spec prompts for complex builds, TCREI-style refinement, and context calibration. It must generalize or omit private, stale, tool-specific, credential-like, or path-specific source material.

## Recommended first reads

- `AGENT.md`
- `CONTEXT.md`
- `skills/README.md`
- `skills/productivity/README.md`
- `skills/productivity/grill-me/SKILL.md`
- `skills/agent-workflows/framework-agnostic-skill-creator/SKILL.md`
- `skills/agent-workflows/framework-agnostic-skill-creator/references/skill-evaluation.md`
- `skills/agent-workflows/using-goated-ai-skills/SKILL.md`
- `skills/engineering/grill-with-docs/SKILL.md`
- `skills/engineering/writing-plans/SKILL.md`
- `docs/how-to-use.md`
- `README.md`

## Relevant source links

- `skills/README.md` - lean schema, support-file policy, delegation contract, and implementation boundary.
- `CONTEXT.md` - source repo, installed skill, target project, public-safe, support-file, and skill anatomy language.
- `skills/productivity/grill-me/SKILL.md` - nearby productivity skill style and routing to `grill-with-docs`.
- `skills/agent-workflows/framework-agnostic-skill-creator/SKILL.md` - skill creation, support-file, privacy, portability, and evaluation guidance.
- `skills/agent-workflows/framework-agnostic-skill-creator/references/skill-evaluation.md` - scenario and residual-risk expectations for new skills.
- `skills/agent-workflows/using-goated-ai-skills/SKILL.md` - GOATED routing behavior that `goated-prompt` should respect rather than duplicate.
- `skills/engineering/writing-plans/SKILL.md` - implementation-plan boundary that `goated-prompt` should route to instead of replacing.

## Acceptance criteria

- [x] `skills/productivity/goated-prompt/SKILL.md` exists and follows the lean schema.
- [x] The skill supports both GOATED Prompt mode and Reusable Prompt mode.
- [x] The workflow classifies prompt type before writing: spec/build, focused task, planning/design, iterative/refinement, or general.
- [x] The output contract includes detected mode/type, principles applied, recommended model class, optimized prompt in a code block, assumptions, and a short rationale.
- [x] Long templates, IDK glossary details, review checks, and examples live in `references/`, not in `SKILL.md`.
- [x] The skill is self-contained after installation and does not depend on this source repo's root docs or issue files at runtime.
- [x] The skill does not duplicate `writing-plans`, `framework-agnostic-skill-creator`, or `using-goated-ai-skills`; it routes to them when they are the better owner.
- [x] Public-boundary review confirms no private note paths, secrets, clone URLs, credentials, private project names, or raw private course excerpts are included.
- [x] `README.md`, `docs/how-to-use.md`, and `skills/productivity/README.md` list the skill only after implementation is complete.

## Expected proof

- Manual schema review of `skills/productivity/goated-prompt/SKILL.md`.
- Manual review that every support-file link exists and has a read condition.
- Targeted `rg` checks for `goated-prompt`, stale planned wording, private path patterns, credential-like strings, and catalog consistency.
- Manual scenario review for:
  - raw feature idea to spec prompt;
  - small code request to focused Location -> Action -> Detail prompt;
  - architecture/design request to planning prompt;
  - existing rough prompt to iterative refinement prompt;
  - GOATED workflow request to GOATED-aware prompt;
  - missing critical context to one focused question or explicit assumption;
  - private or sensitive source material summarized safely.
- Public-boundary pass.

## Blocked by

- None - the user approved the scope and asked to implement it.

## User stories addressed

- As an agent user, I can turn a rough request into a prompt that is clear enough for a coding assistant or reasoning model to execute.
- As a GOATED user, I can translate a rough request into a GOATED-aware prompt that names the likely skill route without bypassing the existing stack.
- As a maintainer, I can add a reusable prompt-crafting workflow without turning GOATED into a prompt dump or leaking private source notes.

## Implementation route

- Use `framework-agnostic-skill-creator` to create the skill package in GOATED shape.
- Use `doc-sync` after implementation because public catalogs and operator guidance change.
- Use `verification-before-completion` before claiming the skill and docs are implemented.

## Scope exclusions

- Do not add a separate PRD for this skill.
- Do not add scripts, assets, runtime bootstrap, automatic activation, prompt-injection tooling, or live model harnesses.
- Do not recommend specific current model names in the core workflow; use generic model classes.
- Do not copy private course-note paths, credential-like examples, clone URLs, private project names, or raw private source excerpts into tracked files.
- Do not replace `writing-plans`, `framework-agnostic-skill-creator`, `using-goated-ai-skills`, `grill-me`, or `grill-with-docs`.

