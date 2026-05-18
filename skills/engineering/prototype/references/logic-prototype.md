# Logic Prototype

Use this reference after choosing the logic/state/data/API branch.

This branch answers questions about behavior that is hard to judge on paper: business rules, state transitions, data shape, API feel, validation, permissions, workflow constraints, or integration boundaries. If the real question is what a screen, page, or interaction should look like, use [UI Prototype](ui-prototype.md) instead.

## Default Shape

Prefer a full-frame terminal interaction when the user needs to drive state by hand and watch it change.

The terminal shell is disposable. The logic behind it should be small, portable, and isolated enough that the validated idea can be lifted into production later if it still fits.

Choose a different artifact only when it answers the question better:

- Use a script when repeatable cases matter more than hand-driving choices.
- Use a fixture harness when the question depends on sample records, scenario matrices, or import/export shapes.
- Use an isolated module when the question is about API shape, data modeling, or pure transformations and does not need an interactive shell.
- Use a local stub or scratch dependency only when the question specifically concerns an integration boundary.

## Process

1. State the branch and question:
   - Record that this is the logic/state/data/API branch.
   - Write the focused question and any branch assumption in the prototype comment, note, README, or harness header.
   - Name the state model, data shape, API surface, or rule family being explored.

2. Match the target project's runtime:
   - Use the target project's existing language, task runner, fixtures, and command style.
   - Do not introduce a new package manager, framework, service, or dependency just to run the prototype.
   - If no runtime is obvious, ask before creating one.

3. Isolate the logic:
   - Keep terminal input, logging, rendering, fixture loading, file access, and network stubs outside the reusable logic.
   - Pick the smallest interface that matches the question: reducer, explicit state machine, pure function set, or a small module/class when ongoing internal state is genuinely part of the model.
   - Use a pure reducer, `(state, action) => state`, when actions are discrete events and state is a single value.
   - Use an explicit state machine when legal actions depend on the current state and invalid transitions are part of the question.
   - Use a small set of pure functions over a plain data type when there is no implicit current state, only transformations.
   - Use a class or module with a clear method surface when the logic genuinely owns ongoing internal state.
   - Keep the interface plain enough that production code could later absorb the idea without inheriting the throwaway shell.

4. Build a full-frame terminal shell when hand-driving state:
   - Initialize one in-memory state object or struct.
   - Render one stable frame with current state first and available actions second.
   - Clear and re-render the whole frame after every action instead of appending an ever-growing transcript.
   - Keep the frame compact enough to read on one screen.
   - Use direct keystrokes or short line commands, whichever is natural for the project runtime.
   - Include a quit action and a reset action when reset helps repeat cases quickly.

5. Keep alternatives equally disposable:
   - Scripts should print the input scenario, output state, and any surprising transition or invariant.
   - Fixture harnesses should use local sample data, stubs, or wipeable scratch files clearly marked as prototype data.
   - Isolated modules should include a tiny driver or note showing how to inspect the explored API or transformation.

6. Provide one entrypoint:
   - Prefer the target project's existing task runner or documented command convention.
   - If the project has no task runner, put the exact command in the prototype note.
   - Make the entrypoint easy to copy, rerun, and delete.

7. Capture the verdict:
   - Record what the prototype proved, disproved, or left unknown.
   - Keep observations tied to the stated question, not every adjacent idea discovered while playing with it.
   - If the user must drive the terminal later, leave a handoff with branch, question, entrypoint, current verdict status, cleanup trigger, and cleanup owner.

8. Clean up or absorb:
   - Delete the terminal shell, script, harness, fixtures, and scratch data when they are no longer needed.
   - Absorb only the validated behavior or API shape into production code.
   - Once behavior is absorbed into production, add the normal tests, docs, and review expected by the target project.

## Guardrails

- Do not use a terminal shell for UI/look/layout questions.
- Do not wire the prototype to real persistence or real mutations unless that boundary is the question.
- Do not let terminal prompts, rendering, logs, fixture setup, or scratch I/O leak into the reusable logic interface.
- Do not add tests for the throwaway shell; do add tests when validated behavior becomes production behavior.
- Do not leave prototype commands, drivers, fixtures, or scratch data behind without an explicit handoff and cleanup trigger.
