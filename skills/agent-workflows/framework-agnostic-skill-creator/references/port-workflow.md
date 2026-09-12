# Port A Workflow

Read when adapting an existing prompt, command, workflow, instruction set, or
skill. Complete a source manifest before judging portability or the final
package shape. When adjacent resources exist, use the directly linked
Source Package Audit reference from `SKILL.md`.

Inventory the provided package, then read first-party files that carry
behavior: instructions, references, scripts, templates, examples, assets, and
producer or consumer contracts. Record inspected and skipped paths with the
reason and any remaining uncertainty. A port based on one supplied prompt
does not require discovering an unrelated repository.

Extract what the workflow changes: activation, decisions, actions, requested
input, outputs, and stopping conditions. Separate reusable behavior from
incidental persona, phrasing, examples, or local conventions.

Check actual dependencies and compatibility constraints, including framework
commands, tools, plugins, instruction precedence, trackers, document layouts,
scratch paths, build commands, and release mechanics. Retain source-specific
details only when they fit the destination and remain public-safe.

This branch is ready for drafting when the manifest and behavior summary
support a portable shape, required resources are accounted for, and remaining
privacy, permission, license, or compatibility blockers are explicit.
