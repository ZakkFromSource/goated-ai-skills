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
- Complex builds include objective, milestones, implementation notes, context, ordered tasks, and verification.
- Refinement prompts include task, context, references, evaluation criteria, and iteration expectations.
- Planning prompts focus on outcome, criteria, tradeoffs, risks, and next action before implementation tactics.
- Output format is explicit.

## GOATED Fit

- GOATED Prompt mode respects `using-goated-ai-skills` as the router when route selection is uncertain.
- The prompt routes serious, docs-grounded, cross-file, public-facing, architectural, or standards-sensitive work to `grill-with-docs`.
- It routes scoped implementation planning to `writing-plans` instead of duplicating that workflow.
- It routes prompt-to-skill work to `framework-agnostic-skill-creator`.
- It does not imply automatic skill activation, runtime bootstrap, or framework-specific mechanics.

## Privacy And Safety

- No private paths, credentials, clone URLs, client data, proprietary source excerpts, raw private notes, ignored scratch content, or sensitive personal context are included.
- Destructive, security-sensitive, or externally published prompts include explicit caution and verification expectations.
- Framework-specific command syntax appears only when the user or target environment provides it.
- Assumptions and skipped checks are visible.

## Final Rationale

- The explanation is brief: 2-4 sentences.
- It names classification, key context decisions, and why the chosen structure fits.
- It does not restate the full prompt or pad with generic praise.

