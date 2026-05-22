## Parent PRD

`issues/prd-goated-ai-skills-v1-superpowers-absorption.md`

## Type

HITL

## What to build

Research whether GOATED should add skill-trigger evaluation harnesses, and if so, what form is worth implementing after V1 or behind a separate approved issue.

## Acceptance criteria

- [x] The research compares static checks, prompt transcript fixtures, live agent harness tests, and hybrid/manual acceptance checklists.
- [x] The research explains nondeterminism, cost, maintenance, privacy, and false-confidence risks for each option.
- [x] The research identifies what could be useful in V1 docs without adding a live harness.
- [x] The research recommends one of: no harness for V1, static/docs-only checks, prompt transcript examples, a prototype, or a future PRD.
- [x] No live harness, CI integration, runtime adapter, or trigger-test framework is implemented in this issue.
- [x] Any future implementation path includes explicit acceptance criteria and public-boundary guardrails.

## Decision

Recommendation accepted: **static/docs-only checks for V1; no live harness; future PRD after real usage evidence**.

GOATED V1 should not add a live agent harness, CI integration, runtime adapter, automatic trigger-test framework, or generated skill activation machinery. V1 already has the useful portable pieces: trigger-focused descriptions, explicit `triggers`, manual RED/GREEN evaluation guidance, pressure scenarios, rationalization capture, and residual-risk reporting in the skill creation workflow.

Future trigger-evaluation work is worth revisiting after GOATED has real usage evidence. The next step should be a **future PRD**, not immediate implementation, once maintainers can point to recurring trigger-selection or skill-compliance failures from actual use.

## Research summary

### Option comparison

| Option | What it would prove | V1 fit | Recommendation |
| --- | --- | --- | --- |
| Static checks | Whether a skill follows GOATED's documented authoring contract: lean schema, trigger-focused `description`, concrete `triggers`, outputs, dependencies, adapters, support-file links, and public-boundary rules. | High if kept as manual review guidance. Automated validators remain future work. | Use in V1 docs and reviews as checklist-style guidance only. |
| Prompt transcript fixtures | Whether representative prompts and expected outcomes are clear enough to discuss trigger behavior, tiny-task escape hatches, user overrides, and rationalization risks. | Medium if examples are public-safe and explicitly non-deterministic. | Allow as illustrative examples or future PRD inputs, not as proof. |
| Live agent harness tests | Whether an actual model run selects or follows a skill under pressure. | Low for V1. It implies framework/runtime assumptions and creates cost, nondeterminism, privacy, maintenance, and false-confidence risks. | Do not implement in V1. Consider only through a future PRD. |
| Hybrid/manual acceptance checklists | Whether maintainers reviewed static shape plus representative RED/GREEN scenarios and documented residual risk. | High. This matches current GOATED skill-evaluation guidance without adding tooling. | Use for V1 skill authoring and closeout review. |

### Risk matrix

| Option | Nondeterminism | Cost | Maintenance | Privacy | False-confidence risk |
| --- | --- | --- | --- | --- | --- |
| Static checks | Low; mostly deterministic document review. | Low. | Medium if converted to tooling; low as checklist guidance. | Low if checks avoid private fixtures. | Medium if schema compliance is mistaken for behavioral proof. |
| Prompt transcript fixtures | Medium; prompts may behave differently across models or sessions. | Low to medium, depending on whether they are only examples or repeatedly replayed. | Medium; fixtures need updates as skills and router guidance evolve. | Medium; realistic transcripts can leak private project details unless sanitized. | High if examples are treated as deterministic tests. |
| Live agent harness tests | High; model choice, temperature, context, tool availability, and framework behavior can change results. | High; repeated model runs and subagents consume time, context, and money. | High; harnesses, fixtures, rubrics, model versions, and adapter behavior all need upkeep. | High; live prompts, transcripts, paths, and logs can capture private work. | High; a passing run can look authoritative while remaining anecdotal. |
| Hybrid/manual acceptance checklists | Medium; human judgment is involved, but evidence can be labeled honestly. | Low to medium. | Medium; checklists need occasional refinement from observed failures. | Low to medium if public-boundary review is explicit. | Medium; mitigated by requiring residual-risk notes and avoiding "proof" language. |

## V1-useful guidance without a live harness

V1 should keep evaluation as documented review behavior:

- Write `description` as discovery-only trigger text, not a workflow summary.
- Keep explicit `triggers` for user requests, task conditions, symptoms, and project situations.
- For router skills, manually review trigger-selection scenarios, tiny-task escape hatches, explicit user overrides, and source-repo versus target-project distinctions.
- For new, substantially changed, or discipline-heavy skills, use the existing RED baseline, pressure scenario, rationalization capture, GREEN verification, and residual-risk language in `framework-agnostic-skill-creator`'s `skill-evaluation` reference.
- Record planned scenarios and residual risk when live evaluation is unavailable instead of claiming behavioral proof.
- Treat prompt transcript examples as illustrative scenario material, not deterministic acceptance tests.

## Future implementation path

Future work should start with a scoped PRD after real usage reveals repeated trigger failures. That PRD should define:

- observed failure patterns that justify tooling;
- whether the target is trigger discovery, skill compliance after trigger, or both;
- public-safe fixture format and forbidden fixture content;
- model and framework scope, including unsupported-framework fallback;
- advisory reporting before any CI gate;
- explicit handling for nondeterminism, model/version drift, and repeated-run interpretation;
- cost budget and maintenance ownership;
- privacy rules for prompts, transcripts, logs, paths, and user data;
- acceptance criteria that distinguish evidence from proof;
- public-boundary guardrails that keep installed skills self-contained and avoid runtime activation assumptions.

The first future milestone should be a PRD-backed fixture-format proposal if usage evidence shows the manual guidance is not enough. Any non-CI prototype should follow that PRD or a separately approved issue.

## Blocked by

- `issues/archive/034-add-using-goated-ai-skills-router.md`
- `issues/archive/035-decide-runtime-bootstrap-and-adapter-automation.md`

## User stories addressed

- As a maintainer, I can decide whether skill-trigger evaluation is worth the complexity before adding tooling.
- As an agent user, I can avoid over-trusting flaky or opaque trigger tests.

## Implementation notes

- Use `grill-with-docs` before research synthesis to compare current GOATED trigger conventions against the proposed harness options.
- Superpowers source inspiration: https://github.com/obra/superpowers/tree/main/skills/writing-skills
- Related source inspiration: https://github.com/obra/superpowers/blob/main/skills/using-superpowers/SKILL.md
- This is a research and decision issue. Keep any experiments under ignored local paths unless the maintainer approves tracked prototype artifacts.

## Verification notes

- `grill-with-docs` was used before synthesis.
- No live harness, CI integration, runtime adapter, automatic activation behavior, generated manifest, or trigger-test framework was implemented.
- This issue produced a research decision only. Future implementation still requires a separate PRD or approved issue.
