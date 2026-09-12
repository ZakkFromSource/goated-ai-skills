# Prompt Review Checklist

Use this checklist before delivering a non-trivial, GOATED-aware, sensitive, or reusable prompt.

## Classification

- The mode is correct: GOATED Prompt, Reusable Prompt, or both.
- The prompt type is correct: spec/build, focused task, planning/design, iterative/refinement, or general.
- The prompt is not overbuilt for a small task or underbuilt for serious work.
- The recommended recipient is a generic model class or GOATED skill route, not a stale model-name claim.

## Context Calibration

- The prompt gives enough context for a competent agent to act.
- Missing critical context becomes one focused question or an explicit assumption.
- Excess context, duplicate context, confusing similarly named entities, and irrelevant history are removed.
- Source checks are named when the receiving agent must inspect project files before making claims.

## Prompt Quality

- The target, action, and success state are unambiguous.
- Focused tasks use Location -> Action -> Detail when useful.
- Builds define outcomes, constraints, acceptance, and verification. Ordered tasks appear only when sequencing is necessary or already agreed.
- Refinement prompts include task, context, references, evaluation criteria, and iteration expectations.
- Planning prompts focus on outcome, criteria, tradeoffs, risks, and next action before implementation tactics.
- Output format is explicit.
- The endpoint and authorization are clear; implementation continues through relevant checks and fixes, while review-only scope and explicit checkpoints remain intact.

## GOATED Fit

- GOATED Prompt mode respects `using-goated-ai-skills` as the router when route selection is uncertain.
- The prompt uses `grill-with-docs` only when unresolved intent or conflicting project evidence materially blocks progress. File count, visibility, and the presence of standards alone do not trigger it.
- It routes scoped implementation planning to `writing-plans` instead of duplicating that workflow.
- It routes prompt-to-skill work to `framework-agnostic-skill-creator`.
- It does not imply automatic skill activation, runtime bootstrap, or framework-specific mechanics.

## Privacy And Safety

- No private paths, credentials, clone URLs, client data, proprietary source excerpts, raw private notes, ignored scratch content, or sensitive personal context are included.
- Destructive, security-sensitive, or externally published prompts include explicit caution and verification expectations.
- Framework-specific command syntax appears only when the user or target environment provides it.
- Assumptions and skipped checks are visible.

## Optional Rationale

- Include explanation only when requested or when a material assumption, route choice, or limitation affects use of the prompt.
- Keep any explanation brief and place it after the finished prompt.
- It does not restate the full prompt or pad with generic praise.
