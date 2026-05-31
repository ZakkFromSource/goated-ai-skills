# Prompt Type Router

Classify before writing. The prompt type decides how much structure the final prompt needs.

## Types

| Type | Use When | Best Shape | Model Class |
| --- | --- | --- | --- |
| Spec/build | The user wants a new app, feature, module, system, or multi-file change. | Objective, milestones, implementation notes, context, ordered tasks. | Reasoning or code-specialized model. |
| Focused task | The user wants one narrow action on an existing artifact. | Location -> Action -> Detail. | Fast capable or code-specialized model. |
| Planning/design | The user wants architecture, design, strategy, tradeoff analysis, or a decision before implementation. | Goal-oriented prose with decision criteria and output format. | Reasoning model. |
| Iterative/refinement | The user has existing output, code, docs, prompt text, or analysis to improve. | TCREI: Task, Context, References, Evaluate, Iterate. | Match the original model class when known, otherwise use a capable general or code model. |
| General | The request is non-code writing, research, explanation, comparison, analysis, or documentation. | Clear task, context, constraints, and output format. | Capable general model, or reasoning model for complex analysis. |

## GOATED Mode Route Notes

When writing a GOATED Prompt, include a route note only when it helps the receiving agent choose the next workflow:

| Need | Route Note |
| --- | --- |
| Unsure which GOATED skill applies | Start with `using-goated-ai-skills`. |
| Unfamiliar project or source area | Start with `session-start-progressive-disclosure`. |
| Scope, success criteria, project docs, standards, or source facts matter | Use `grill-with-docs` before implementation. |
| User needs lightweight ideation without project docs | Use `grill-me`. |
| Fuzzy feature or product idea needs durable requirements | Use `write-a-prd`. |
| Approved issue or scoped task needs exact executable steps | Use `writing-plans`. |
| Behavior change needs proof through tests | Route implementation through `tdd`. |
| Prompt should become an installable GOATED skill | Use `framework-agnostic-skill-creator`. |
| Changed behavior or docs may create documentation drift | Use `doc-sync`. |
| Completion, passing, ready, or synced claim is about to be made | Use `verification-before-completion`. |

Do not claim routing is automatic. The prompt should instruct the receiving agent to use the route when the installed stack and task conditions make it available.

## Clarifying Question Gate

Ask one question before writing only when the answer changes one of these:

- the target artifact or project;
- whether the work is GOATED-aware or generic reusable;
- the prompt type;
- security, privacy, or destructive-action risk;
- acceptance criteria or success state;
- whether the result should be a prompt, PRD, issue, implementation plan, or skill.

If the answer would only polish wording, make a reasonable assumption and write the prompt.

