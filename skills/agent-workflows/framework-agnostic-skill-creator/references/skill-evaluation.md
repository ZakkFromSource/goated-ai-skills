# Skill Evaluation

Use this reference before trusting a new, substantially changed, or discipline-heavy skill.

The goal is to test whether the skill changes agent behavior, not whether the prose sounds convincing. Treat skill evaluation like TDD for process documentation: create a scenario that reveals the old behavior, revise the skill, then verify the new behavior.

## Evaluation Loop

1. Define the behavior under test:
   - State the decision, workflow, or discipline the skill should change.
   - Identify the user value protected by the skill.
   - Choose realistic scenarios that would trigger the skill.
   - For discipline-heavy skills, include pressures that make the agent want to skip the rule.

2. RED baseline:
   - Run or design the scenario without the skill.
   - Capture what the agent does naturally.
   - Record exact rationalizations, missed steps, wrong assumptions, premature claims, or support files it ignores.
   - If live baseline testing is not available, write the expected baseline risk and mark it as unverified.

3. GREEN verification:
   - Run the same or equivalent scenario with the skill available.
   - Check that the agent loads the skill, follows the intended workflow, uses required references or scripts, and produces the expected output.
   - Confirm the agent does the hard part under pressure, not only an academic summary of the rule.
   - If the skill still fails, revise the skill before claiming it works.

4. REFACTOR and re-test:
   - Add explicit counters for rationalizations observed during RED or GREEN.
   - Add stop rules, proof gates, red flags, anti-pattern references, or support-file links only where they address real failure modes.
   - Remove unnecessary prose that does not change behavior.
   - Re-run or re-plan the scenario after each significant change.

## Pressure Scenarios

Use pressure scenarios when the skill asks agents to resist shortcuts, verify claims, stop before acting, delete or redo work, challenge user assumptions, or follow a strict order.

Good pressure scenarios are concrete and force a choice:

- **Time pressure:** production incident, deadline, deploy window, or user asking for a quick fix.
- **Sunk cost:** work is already done and would need to be redone.
- **Authority pressure:** user, maintainer, manager, or senior reviewer suggests skipping the process.
- **Exhaustion pressure:** late in the session, context is long, or the work feels nearly finished.
- **Social pressure:** following the skill may look slow, pedantic, or overly cautious.
- **Pragmatic pressure:** the shortcut looks faster and appears to satisfy the immediate request.

For discipline-heavy skills, combine at least three pressures. For reference or technique skills, use representative tasks that test retrieval, application, and missing-information behavior instead of artificial pressure.

## Rationalization Capture

Capture the exact excuse the agent uses when it skips, weakens, or reinterprets the skill. Common forms include:

| Rationalization | Counter to add when observed |
| --- | --- |
| "This is too small to need the process." | State the tiny-task exception precisely, or say the process still applies. |
| "I can do the important part later." | Add a before-proceeding gate and require evidence before completion claims. |
| "I followed the spirit of the rule." | Name the required action and say alternative shortcuts do not count. |
| "The source is obvious from the entrypoint." | Require source package audit when adjacent support files exist. |
| "The description already explains enough." | Move workflow out of `description` and require reading the body or reference. |
| "Testing the skill is overkill." | Require at least a planned scenario and residual-risk note when live testing is unavailable. |

Do not add a broad scolding section when a specific counter would do. The best counters name the exact shortcut and the required replacement behavior.

## Scenario Types By Skill Kind

| Skill kind | Best evaluation |
| --- | --- |
| Discipline or proof-gate skill | RED/GREEN pressure scenarios, rationalization table, red flags, proof checks |
| Technique skill | Application scenario with a realistic artifact or code area |
| Pattern or mental-model skill | Recognition scenario, counter-example, and application scenario |
| Reference skill | Retrieval task, application task, and gap check for common requests |
| Router skill | Trigger-selection scenarios, tiny-task escape hatch, explicit user override |
| Porting or creation skill | Source package audit scenario, clarified-intent scenario, schema and public-boundary review |

## Evidence To Record

When evaluation runs, record:

- scenario prompt or task shape;
- whether it was run without the skill, with the skill, or only planned;
- paths, files, or support files available to the agent;
- choices the agent made;
- rationalizations or failures observed;
- changes made to the skill because of the result;
- final GREEN evidence or residual risk.

Avoid leaking the intended answer into an evaluation prompt. Pass the skill and the realistic task, not a diagnosis of what you expect the evaluator to find.

## Final Review Checklist

Before publishing or closing a skill change, verify:

- `description` is trigger-focused and does not summarize the workflow.
- `triggers` cover concrete requests, symptoms, or project conditions.
- `outputs` define observable completion artifacts or decisions.
- Dependencies are classified as hard, soft, or fallback.
- Adapter notes are small and do not turn one framework into a universal rule.
- Support files are directly linked from `SKILL.md` with clear read or run conditions.
- Scripts are included only when maintained deterministic behavior is better than generated prose.
- Long examples, templates, checklists, rationalization tables, and anti-patterns live in `references/`.
- The skill folder is self-contained after installation and does not require the source repo root files.
- Public output contains no private names, credentials, client data, sensitive personal context, or private workflow assumptions.
- Evaluation was run or explicitly recorded as a plan with residual risk.

## Reporting Template

```markdown
## Skill Evaluation

- Skill: <name>
- Change under test: <new or changed behavior>
- Scenario type: <pressure | application | retrieval | router | audit>
- RED baseline: <run evidence or unverified baseline risk>
- Rationalizations captured: <none or list>
- GREEN verification: <run evidence or residual risk>
- Changes made from evaluation: <summary>
- Remaining risk: <none or list>
```
