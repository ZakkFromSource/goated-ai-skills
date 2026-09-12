# Skill Evaluation

## Contents

- [Evaluation Loop](#evaluation-loop)
- [Model Upgrade Calibration](#model-upgrade-calibration)
- [Authoring Discipline Lenses](#authoring-discipline-lenses)
- [Pressure Scenarios](#pressure-scenarios)
- [Rationalization Capture](#rationalization-capture)
- [Scenario Types By Skill Kind](#scenario-types-by-skill-kind)
- [Evidence To Record](#evidence-to-record)
- [Final Review Checklist](#final-review-checklist)
- [Reporting Template](#reporting-template)

Use this reference before trusting a new, substantially changed, or discipline-heavy skill.

The goal is to test whether the skill changes agent behavior, not whether the prose sounds convincing. Treat skill evaluation like TDD for process documentation: create a scenario that reveals the old behavior, revise the skill, then verify the new behavior.

## Evaluation Loop

1. Define the behavior under test:
   - State the decision, workflow, or discipline the skill should change.
   - Identify the user value protected by the skill.
   - State who must invoke it independently and why that reach earns its discovery and context cost.
   - Give each important phase a completion criterion the agent can observe.
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
   - Remove no-op or duplicated prose that does not change behavior.
   - Move branch-only material behind a clear pointer, and sharpen phase completion before splitting a sequence.
   - Re-run or re-plan the scenario after each significant change.

## Model Upgrade Calibration

Use this comparison when changed model behavior motivates an instruction edit.
Compare unaided behavior, the existing instructions, and the candidate on the
same representative requests. Use fresh contexts and record which instructions,
model version, and host capabilities were available. Keep scenarios neutral;
do not tell an evaluator the failure it is expected to demonstrate.

Include positive and negative selection cases:

| Scenario | Observable evidence |
| --- | --- |
| Settled change across several files | A useful prompt or action without a needless clarification gate or full specification. |
| Authorized refinement beside separable user edits | Requested cleanup and relevant proof while preserving the other edit. |
| Mechanical repair in a security-related document | Safe source inspection and the authorized repair without changing policy meaning. |
| Review-only task with a consequential unresolved decision | Evidence and the required decision, without unauthorized mutation. |
| Focused checks pass after a small change | Completion after required coverage; additional checks have a named reason. |
| First implementation fails an acceptance check | Continued authorized diagnosis and repair rather than premature closeout. |
| Request near two skills' selection boundaries | The appropriate skill is selected and the neighboring skill is skipped. |

Inspect task quality, premature stops, unwanted actions, unnecessary questions,
and irrelevant reads or checks. Shorter text alone is not a successful result.
If a baseline already works, report that; the candidate may remove ambiguity
without demonstrating better behavior. Repeat only when variance or a changed
instruction leaves a material question. Check other models actually used before
claiming cross-model compatibility.

An agent's proposed next action is a decision exercise, not proof that the real
workflow executed. Static package checks, decision exercises, and live task runs
must retain distinct evidence labels. Do not add a runtime evaluation platform
or model-specific dependency merely to update a skill.

## Authoring Discipline Lenses

Use these as evaluation questions, not as required GOATED vocabulary:

| Lens | Evaluation question | Preferred response |
| --- | --- | --- |
| Invocation value | Must a user, agent, router, or neighboring skill reach this behavior independently? | Keep a separate skill only when that reach earns the discovery description and context cost. |
| Observable completion | Can the agent distinguish a finished phase from an attempted action or plausible summary? | End important phases with a checkable artifact, decision, state, or evidence condition. |
| No-op guidance | Does this sentence change behavior compared with the agent's likely default? | Delete it when removing it produces no meaningful difference. |
| Ownership | Is the same rule already authoritative in shared policy, a neighboring skill, or another section? | Keep the specialist delta here and point to the owner instead of copying universal behavior. |
| Branch disclosure | Does every run need this detail, or only one mode or branch? | Inline common decisions; put branch-only detail behind a pointer that says when to read it. |
| Sequence pressure | Do visible later steps tempt the agent to declare the current phase complete too early? | Sharpen the current completion criterion first; split only when observed pressure remains. |
| Positive steering | Does a prohibition make the unwanted behavior more salient without naming the replacement? | State the positive target behavior first; retain a prohibition only when it is a necessary guardrail and pair it with the replacement action. |
| Leading concept | Can a familiar compact concept replace repeated explanation without hiding a project-specific rule? | Use it when it improves retrieval or execution; explain unfamiliar meaning locally and do not require the label across GOATED. |

Apply the lenses sentence by sentence and branch by branch. They are useful
only when they change an authoring decision; do not add a vocabulary report to
every evaluation.

Concrete pruning and disclosure scenarios:

- Candidate instruction: "Be clear and thorough." If RED behavior is already
  equally clear and complete, Remove it as a no-op. If a real failure remains,
  replace it with the specific observable action that counters that failure.
- Candidate workflow: "Only the port branch needs a compatibility matrix."
  Keep the shared branch decision in `SKILL.md`, then disclose the matrix
  behind a branch-specific pointer with an explicit read condition.
- Candidate sequence: investigation, decision, implementation, and closeout
  appear together, and the agent repeatedly rushes investigation. First make
  investigation end on named evidence. Split or progressively disclose later
  phases only if the same premature-completion pressure remains.

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

- Independent invocation and context visibility earn their cost.
- `description` is discovery-focused and does not summarize the workflow.
- Body activation conditions cover concrete requests, symptoms, or project conditions.
- Important phases and `## Output Contract` define observable completion artifacts, decisions, states, or evidence.
- No-op guidance and duplicated ownership were removed.
- Branch-only detail is progressively disclosed with an explicit read condition.
- Sequence pressure was tested before splitting, and positive target behavior leads avoidable prohibitions.
- Compact leading concepts are used only when they improve behavior, not as mandatory terminology.
- `## Dependencies` classifies hard dependencies, soft dependencies, and fallback behavior.
- Compatibility notes are specific to real constraints and do not turn one framework into a universal rule.
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
