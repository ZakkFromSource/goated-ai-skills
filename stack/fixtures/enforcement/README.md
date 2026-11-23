# Enforcement Conformance Scenarios

Each file here holds scenarios for the
[enforcement contract](../../enforcement-contract.md), written in the terms
of the [event model](../../schemas/enforcement-event-model.schema.json)
(`$defs/scenario_file`). A scenario is a sequence of steps: prompts, replies,
calls with their results, skills a person invokes, background agents that
finish, compactions, turn ends, and session starts. A
judged step carries the decision it must get: `allow` or `hold`, the holds by
gate and kind in firing order, for a closeout hold exactly the labels of
the items it lists, and, when given, exactly the notices it carries. A
`fail_open` or `warning` notice the step does not name fails it, so an
adapter that could not judge never passes. Hold text is guidance and is
never compared.

Rules for every scenario:

- **Name no harness.** Calls have kinds, never a harness's tool names, and
  no text names a harness or its hooks. A test checks this.
- **Every call is judged.** A call step with no `expect` must be allowed, so
  a scenario's history passes the gates as a real session's would.
- **Say what it covers, and show it.** `covers` lists a gate holding, a
  way it clears (a clear way the contract's Gates table names), or a near
  miss. A scenario that covers a clear way shows the same
  call held without the clearing step and allowed with it; an override
  comes in a later turn, since it covers only the turn its prompt opens. A
  near miss never holds by its gate. Tests fail when a gate lacks a
  scenario that holds, one for each clear way, or a near miss, and when
  any of the nine closeout labels is pinned by no scenario.
- **Placeholders.** `{outside}` is a folder outside the project and any
  checkout, as a scratch file's or an installed skill's folder is.
- **Setup** describes the project, not the harness: skills installed, a
  branch of a given size, or a subagent as the agent that acts. A
  `branch_grows: <lines>` step grows that branch later, by a new untracked
  code file the runner writes; the adapter sees no event for it.

The repo proves every scenario against the Claude Code adapter through
`tests/claude_code_scenarios.py`, which translates each step into that
adapter's hook input and its output back into a decision. It raises on a
step it cannot run faithfully, such as a line on a call Claude Code gives
no field for, rather than dropping part of it. It also proves them against
the shared core (`adapters/core/`) through both its ways in, the Python call
and the JSON command, with `tests/core_scenarios.py`, which acts as a
minimal adapter: it sends one request per judged step and records a held
call as held. The two ways in must give the same decision at every step.
An adapter for another harness runs the same files through its own
translation, with the conformance runner `scripts/run_conformance.py`, as
[Writing An Adapter](../../../adapters/writing-an-adapter.md) describes.

| File | Gates |
| --- | --- |
| [`routing.yaml`](routing.yaml) | `router-first`, `route-line`, `pipeline` (with a briefed session's orientation), a joint hold |
| [`handing-on.yaml`](handing-on.yaml) | `commit`, `pull-request`, `pr-review` (with `pull-request` in one hold), `spawn` |
| [`writes.yaml`](writes.yaml) | `design` and `design-reads` (by file edit tools and shell writes), `reference-reads`, `review-intake`, `security`, `scripted-edit`, `conflict-resolution`, `repeated-failure`, and a joint message of three holds lines can clear |
| [`closeout.yaml`](closeout.yaml) | `closeout`, at a commit (a subagent's too) and at the turn's end, every item label, and the closeout note |
