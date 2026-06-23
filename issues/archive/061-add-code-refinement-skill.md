## Parent PRD

No separate parent PRD. This issue is based on the user-approved 2026-06-23 grill for absorbing the public Anthropic `code-simplifier` idea into GOATED AI Skills as a GOATED-native skill.

## Type

AFK

## What to build

Implement `code-refinement` under `skills/engineering/`.

The skill should guide agents through a disciplined post-change refinement pass for recently changed code. It should preserve behavior first, improve readability and local reasoning second, then reduce duplication, unnecessary branching, and needless abstraction only when the result is clearer.

The skill must be language/framework-agnostic, scoped to known/current changes by default, and safe around dirty worktrees. It should act as a soft closeout step after non-trivial implementation/TDD work and before standards/spec review, security review when relevant, doc sync, and final verification.

## Grill decisions

| Decision | Outcome |
| --- | --- |
| Skill shape | Standalone engineering skill, not folded into `improve-codebase-architecture` or `tdd`. |
| Name | `code-refinement`. |
| Default scope | Known/current changes only: current diff, task-touched files, or explicit user paths. |
| Proof gate | Require behavior-preservation proof before and after non-trivial refinement edits, with fallback reporting when tests/checks are unavailable. |
| Optimization priority | Preserve behavior, improve readability/local reasoning, reduce duplication/branches, remove needless abstraction, reduce line count last. |
| Public interfaces | Do not change public APIs, file/module boundaries, or dependency structure by default; route those to architecture/TDD workflows. |
| Invocation | Soft closeout step for non-trivial code changes; skip for tiny mechanical edits, generated files, docs-only changes, and already-clean one-line fixes. |
| Delegation | Optional bounded reviewer/subagent can inspect scoped diffs and suggest refinements; main agent owns edits and final judgment. |
| Support file | Add `references/refinement-patterns.md` for patterns and anti-patterns. |
| Test edits | Allow only narrow proof-preserving test cleanup; do not weaken assertions or remove coverage without equivalent replacement. |
| Docs | Mostly report possible drift and route to `doc-sync`; only tiny directly tied doc edits are in scope. |
| Route position | Implementation/TDD -> `code-refinement` -> standards/spec review -> security review when relevant -> doc sync -> verification. |
| Dirty worktree | Explicitly preserve unrelated user-authored changes and identify scope before editing. |
| Framework scope | Keep the core language/framework-agnostic. |
| Examples | If examples are added, prefer Python, HTML, and CSS examples. |
| Edit behavior | Edit by default when scope is explicit and behavior-preservation checks are available or discoverable; propose refinements first when scope/proof is weak or subjective. |

## Recommended first reads

- `AGENT.md`
- `CONTEXT.md`
- `skills/README.md`
- `skills/engineering/README.md`
- `README.md`
- `docs/how-to-use.md`
- `skills/agent-workflows/using-goated-ai-skills/SKILL.md`
- `skills/agent-workflows/framework-agnostic-skill-creator/SKILL.md`
- `skills/agent-workflows/framework-agnostic-skill-creator/references/skill-evaluation.md`
- `skills/engineering/tdd/SKILL.md`
- `skills/engineering/tdd/references/refactor-after-green.md`
- `skills/engineering/improve-codebase-architecture/SKILL.md`
- `skills/engineering/standards-and-spec-review/SKILL.md`
- `skills/engineering/doc-sync/SKILL.md`
- `skills/engineering/verification-before-completion/SKILL.md`

## Relevant source links

- `skills/README.md` - lean schema, support-file policy, implementation boundary, and delegation contract.
- `CONTEXT.md` - source repo, installed skill, target project, public-safe, support-file, deep-module, and workflow language.
- `skills/engineering/README.md` - engineering catalog and closeout gate guidance.
- `README.md` - public skill catalog and typical delivery route.
- `docs/how-to-use.md` - operator delivery pipeline, skill reference, and practical routing rules.
- `skills/agent-workflows/using-goated-ai-skills/SKILL.md` - router behavior that should learn when to route simplification/refinement requests.
- `skills/agent-workflows/framework-agnostic-skill-creator/SKILL.md` - skill creation, support-file, privacy, portability, and evaluation guidance.
- `skills/agent-workflows/framework-agnostic-skill-creator/references/skill-evaluation.md` - evaluation expectations for new discipline-heavy skills.
- `skills/engineering/tdd/SKILL.md` - companion implementation flow and `Refactor After Green` relationship.
- `skills/engineering/tdd/references/refactor-after-green.md` - existing refactor guidance that `code-refinement` should complement without duplicating.
- `skills/engineering/improve-codebase-architecture/SKILL.md` - architecture review/design boundary that `code-refinement` must not blur.
- `skills/engineering/standards-and-spec-review/SKILL.md` - review gate after refinement.
- `skills/engineering/doc-sync/SKILL.md` - companion route for documentation drift after refinement.
- `skills/engineering/verification-before-completion/SKILL.md` - final evidence gate before completion, correctness, or behavior-preservation claims.
- Anthropic source inspiration: `https://github.com/anthropics/claude-plugins-official/blob/main/plugins/code-simplifier/agents/code-simplifier.md`

## Acceptance criteria

- [x] `skills/engineering/code-refinement/SKILL.md` exists and follows the lean schema.
- [x] `skills/engineering/code-refinement/references/refinement-patterns.md` exists and is directly linked from `SKILL.md` with a clear read condition.
- [x] The skill is portable, self-contained after installation, and does not depend on this source repo's root docs or issue files at runtime.
- [x] The skill's discovery description triggers on post-change refinement, simplifying/refactoring recently changed code, cleanup after implementation, and preserving behavior.
- [x] The skill defines its default scope as current diff, task-touched files, or explicit user paths.
- [x] The workflow requires identifying the refinement scope and dirty-worktree/user-change risk before editing.
- [x] The workflow requires behavior-preservation proof before and after non-trivial refinement edits, or an explicit fallback/residual-risk report when proof is unavailable.
- [x] The skill allows direct edits only when scope is explicit and proof is available or discoverable.
- [x] The skill requires proposing refinements first when scope is broad, proof is weak, user-authored changes are mixed in, public interfaces might be affected, or the cleanup is subjective.
- [x] The skill preserves this priority order: behavior, readability/local reasoning, duplication/branch reduction, needless-abstraction reduction, and line-count reduction last.
- [x] The skill rejects clever compactness, dense one-liners, hidden behavior changes, broad opportunistic cleanup, and unrelated style churn.
- [x] The skill forbids public API, module-boundary, file-ownership, dependency-structure, or architecture changes by default and routes those to companion skills.
- [x] The skill includes narrow rules for proof-preserving test cleanup and forbids weakening or deleting behavior coverage without equivalent replacement.
- [x] The skill reports possible doc drift and routes substantial documentation updates to `doc-sync`.
- [x] The skill defines its delivery-pipeline position after implementation/TDD and before standards/spec review, security review when relevant, doc sync, and final verification.
- [x] The skill includes an optional bounded reviewer/subagent delegation pattern while keeping main-agent ownership of edits and final claims.
- [x] `references/refinement-patterns.md` contains language/framework-agnostic refinement patterns and anti-patterns, with Python/HTML/CSS examples if examples are used.
- [x] The support reference distinguishes clarity-improving simplification from line-count-driven or clever rewrites.
- [x] Public-boundary review confirms no private project names, personal paths, credentials, raw private notes, private workflow assumptions, or tool-specific automation claims are included.
- [x] `README.md`, `docs/how-to-use.md`, `skills/engineering/README.md`, and `skills/agent-workflows/using-goated-ai-skills/SKILL.md` are updated to route and catalog `code-refinement` only after implementation is complete.

## Expected proof

- Manual schema review of `skills/engineering/code-refinement/SKILL.md`.
- Manual review that every support-file link exists and has a read condition.
- Run `uv run python scripts/validate_skills.py` and confirm implemented skills pass blocking checks.
- Run `git diff --check`.
- Targeted `rg` checks for `code-refinement`, `code-simplifier`, stale planned wording, private path patterns, catalog consistency, and delivery-route placement.
- Manual scenario review for:
  - post-TDD refinement after focused tests are green;
  - generated or agent-written code with awkward duplication;
  - broad user request to "clean this up" where the skill should propose first;
  - dirty worktree with unrelated user-authored changes;
  - tempting public-interface or module-boundary cleanup that should route to architecture/TDD instead;
  - tests that can be renamed or deduplicated without weakening behavior proof;
  - docs drift that should route to `doc-sync`;
  - Python, HTML, or CSS examples in the support reference if examples are added.
- Public-boundary pass.
- Use `verification-before-completion` before claiming the skill and docs are implemented, passing, synced, or ready.

## Blocked by

- None - the user approved the grill decisions and asked to create this issue.

## User stories addressed

- As an agent user, I can ask for recently changed code to be cleaned up without accidental behavior changes or broad unrelated refactors.
- As an agent user, I get a safer closeout pass after implementation that improves clarity before review gates.
- As a maintainer, I can keep local code refinement separate from architecture opportunity review and behavior-changing TDD work.
- As a reviewer, I can expect refinement edits to preserve proof, respect scope, and report residual risk instead of hiding subjective churn.

## Implementation route

- Use `writing-plans` to create a just-in-time implementation plan from this issue before editing the skill package.
- Use `framework-agnostic-skill-creator` when drafting the new skill package to preserve GOATED schema, support-file, portability, delegation, and evaluation conventions.
- Use `doc-sync` after implementation because public catalogs, operator guidance, and router behavior change.
- Use `verification-before-completion` before claiming the skill, support reference, docs, and validator checks are complete.

## Implementation evidence

- Added `skills/engineering/code-refinement/SKILL.md` with lean frontmatter, scoped post-change refinement workflow, proof gate, proposal fallback, delegation, output contract, companion routes, and guardrails.
- Added `skills/engineering/code-refinement/references/refinement-patterns.md` with language/framework-agnostic refinement patterns, anti-patterns, and Python/HTML/CSS examples.
- Updated `README.md`, `docs/how-to-use.md`, `skills/engineering/README.md`, and `skills/agent-workflows/using-goated-ai-skills/SKILL.md` to catalog and route `code-refinement`.
- Updated relevant installed-skill routing and soft dependency sections so `code-refinement` appears in planning, TDD, delegated development, review feedback, standards/spec review, architecture-improvement review, verification, and the main GOATED router where scoped behavior-preserving cleanup fits.
- `uv run python scripts/validate_skills.py` passed: 31 implemented skills checked, 0 human-review notes, 0 report-only docs/example schema drift.
- `git diff --check` passed with line-ending warnings only.
- Targeted `rg` checks found expected `code-refinement` routing/catalog references and no copied `code-simplifier`, Claude-only metadata, model-specific tool fields, or high-confidence private local path leaks in the changed public surfaces.
- Manual scenario review passed for post-TDD green refinement, agent-written duplicated code cleanup, broad "clean this up" proposal mode, dirty-worktree mixed-change caution, public-interface/module-boundary routing, proof-preserving test cleanup, doc drift routing, and Python/HTML/CSS support-reference examples.
- Security review skipped: this issue adds markdown skill/docs only, with no scripts, runtime behavior, dependencies, auth, persistence, execution, user data, or unsafe configuration changes.

## Scope exclusions

- Do not fold this behavior into `improve-codebase-architecture`.
- Do not make `code-refinement` a broad architecture scan, generic code review, standards review, security review, or doc-sync replacement.
- Do not add runtime bootstrap, automatic activation, hooks, generated manifests, installer automation, model-specific tool controls, or Claude-only metadata.
- Do not copy the Anthropic source text wholesale; use it as attributed public inspiration and write a GOATED-native workflow.
- Do not make TypeScript/React-specific heuristics part of the core skill.
- Do not require every project to use TDD, `docs/agents/`, ADRs, root `CONTEXT.md`, or GOATED artifact conventions.
- Do not encourage line-count reduction, clever one-liners, dense chaining, or abstraction deletion when readability or behavior proof worsens.
- Do not permit public interface, module ownership, dependency seam, file-structure, or broad test-architecture changes by default.
