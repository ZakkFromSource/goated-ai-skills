## Parent PRD

`issues/prd-goated-ai-skills-v1-superpowers-absorption.md`

## Type

HITL

## What to build

Decide whether GOATED V1 should ever include runtime bootstrap or adapter automation inspired by Superpowers, or whether those ideas stay post-V1. This issue should produce a human-reviewed recommendation, not implementation.

## Acceptance criteria

- [x] The analysis compares docs-first installation, portable router guidance, adapter notes, runtime bootstrap scripts, plugin manifests, and hook-based activation.
- [x] The analysis identifies any conflict with `AGENT.md`, `CONTEXT.md`, and the V1 public core's docs-first distribution model.
- [x] The analysis explains what would need to change before runtime automation could be public-safe and framework-agnostic.
- [x] The recommendation is one of: keep out of V1, allow a narrow V1 adapter note only, create a new PRD, or approve a specific implementation issue.
- [x] No runtime bootstrap code, manifests, hooks, installer scripts, or automatic skill activation behavior are implemented in this issue.
- [x] Any approved future work is routed to a new issue or PRD with explicit scope and acceptance criteria.

## Decision

Recommendation accepted: **allow a narrow V1 adapter note only**.

GOATED V1 remains docs-first and framework-agnostic. V1 may keep portable router guidance, small `adapters` notes, and thin target-project instruction adapters that point to installed skills. V1 does not include runtime bootstrap, automatic prompt/session-context injection, plugin manifests, marketplace packaging, hook-based activation, installer scripts, automatic framework detection, automatic skill loading, or adapter sync/version/drift automation.

Durable decision record: `docs/adr/0001-v1-runtime-bootstrap-and-adapter-automation.md`.

Deferred future possibilities are recorded in `.out-of-scope/future-automation-and-validation.md`.

## Analysis summary

- **Docs-first installation:** Fits `AGENT.md`, `CONTEXT.md`, `README.md`, and `docs/install.md`. Users manually copy, install, or adapt skill folders into their chosen agent framework.
- **Portable router guidance:** Fits V1. `using-goated-ai-skills` describes task routing and skill selection without changing runtime behavior.
- **Adapter notes:** Fit V1 only when narrow. `adapters` frontmatter and `agent-instructions-integrator` may provide compatibility notes or thin target-project routing, but must not copy full skill bodies or assume one framework's file names are universal.
- **Runtime bootstrap scripts:** Out of V1. They would shift GOATED from docs-first distribution toward runtime behavior injection.
- **Plugin manifests:** Out of V1. Framework-specific manifests and marketplace packaging need separate product ownership, compatibility, and public-safety decisions.
- **Hook-based activation:** Out of V1. Hooks and automatic prompt/session-context injection create silent runtime assumptions that conflict with the V1 public core unless future work explicitly changes that model.

Before runtime automation can become public-safe and framework-agnostic, a future PRD or issue must define supported frameworks, fallback behavior, product-layer ownership, test strategy, user/project instruction precedence, self-contained installed-skill guarantees, and public docs that do not imply universal runtime support.

## Blocked by

- `issues/archive/034-add-using-goated-ai-skills-router.md`

## User stories addressed

- As a maintainer, I can make a deliberate decision before GOATED moves beyond docs-first installation.
- As an agent user, I can trust V1 does not silently assume a specific framework runtime.

## Implementation notes

- `grill-with-docs` was used before the decision pass, and current V1 distribution language was read before making the recommendation.
- Superpowers source inspiration: https://github.com/obra/superpowers/blob/main/skills/using-superpowers/SKILL.md
- Upstream adapter/product distribution ideas from the Superpowers repo root were inspected as source inspiration.
- This issue produced a decision record and deferred future-work notes only. It did not implement runtime bootstrap code, manifests, hooks, installer scripts, or automatic skill activation behavior.
