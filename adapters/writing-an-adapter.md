# Writing An Adapter

This guide shows how to connect a harness the repo does not cover to the
shared enforcement core in [`core/`](core/), such as a custom API tool loop
or another agent CLI. When you finish, your harness holds a call until the
skill the GOATED stack requires has loaded. It also passes the same
conformance scenarios as the repo's adapters.

You need this repo, Python 3.11 or later, and [uv](https://docs.astral.sh/uv/)
for the repo's checks. Every command below runs from the repo root. Run
`uv sync` once first.

The [worked example](example/) is a complete adapter for a toy tool loop:
`toy_loop.py` (the harness), `goated_example_adapter.py` (the adapter) and
`conformance_translator.py` (its translator for the runner). Each section
below points at the part of it that does the step.

## Contents

- [What An Adapter Does](#what-an-adapter-does)
- [1. Map Tools To Call Kinds](#1-map-tools-to-call-kinds)
- [2. Build The Turns So Far](#2-build-the-turns-so-far)
- [3. Call The Core](#3-call-the-core)
- [4. Show A Hold To The Agent](#4-show-a-hold-to-the-agent)
- [Rules Every Adapter Keeps](#rules-every-adapter-keeps)
- [Document What You Cannot Enforce](#document-what-you-cannot-enforce)
- [Check It With The Conformance Runner](#check-it-with-the-conformance-runner)
- [The Worked Example](#the-worked-example)

## What An Adapter Does

An adapter translates and decides nothing. At each moment the harness lets
it act, it builds one **request** in the
[event model](../stack/schemas/enforcement-event-model.schema.json), asks
the core, and turns the core's **decision** into what the harness does:

```text
harness hook -> request (turns so far + event) -> core -> decision -> block, or show notices
```

The rules live in the core, as the
[enforcement contract](../stack/enforcement-contract.md) states them. An
adapter that decides a hold itself, or drops one the core gave, is wrong
([ADR 0004](../docs/adr/0004-portable-enforcement-core.md)).

## 1. Map Tools To Call Kinds

Give each of your harness's tools the call kind it is, with the fields the
event model's `call` definition lists for that kind:

| Kind | A tool that | Fields |
| --- | --- | --- |
| `file_write` | edits or writes a file | `path`, `edits` (each `removed` and `added`, null when the tool does not say), `whole_file`, `creates` |
| `file_read` | reads a file | `path`, `whole` (false when it asked for part) |
| `shell_command` | runs a command | `command`, `shell` (`posix` or `powershell`), `background` |
| `skill_load` | loads a skill | `skill`, as the harness names it, namespace included |
| `spawn` | hands work to another agent or session | `brief`, `starts_now`, `read_only`, `separate` |
| `commit` | commits through a tool, not a shell | `message` |
| `pull_request` | opens a pull request through a tool | `base`, `head`, `repository` |
| `other` | does anything else | none |

- **Give every call an `id` before you ask about it, and keep it.** The
  `pending_call`, the `finished_call`, and the call's entry in later turns
  must carry the same id, since the core keys facts by it. For example, it
  records the template a reviewer's brief followed under the spawn's id, and
  the `review-intake` gate finds the reviewer by that id. A harness that
  numbers a call only when it logs it raises no error. Those gates simply
  never fire.
- Pass paths as the harness gives them. The core reads a relative path from
  the working folder and a leading `~` from the project's `home`.
- A commit or pull request made by a shell command stays a `shell_command`.
  The core reads the command.
- A tool you leave unmapped is `other`, and no write gate judges it. Map
  every tool that writes, runs a command, or hands work on.
- Fill `line_text` only when your harness may not keep the agent's reply
  text whole. It is the call's own text a route or skip line can be read
  from, such as a description field. `action`, an opaque key, is optional:
  give it when two tools the model shows alike should count as different
  actions.

The example's `TOOL_CALLS` table in `goated_example_adapter.py` does this
step. `call_for` gives an unmapped tool the kind `other`.

## 2. Build The Turns So Far

Each request carries **every turn since the last compaction**, oldest
first. A turn has a `key`, an `opener`, and its `entries`:

- **Openers.** A prompt opens a turn, with its `author`: `person`, `session`
  (another agent session), `host` (the harness itself), or `unknown`. A
  compaction opens a turn of its own, `{"type": "compaction"}`.
- **Entries.** Reply text (`reply_text`), each finished call with its result
  (`call`), a skill a person invoked (`skill_invoked`), a background agent
  finishing (`agent_finished`), the turn's end (`turn_ended`), and a prompt
  that arrives mid-turn (a `prompt` entry, not an opener). A harness whose
  calls can finish in another order than they were made adds a
  `call_finished` entry with the call's `id` where each one finished. The
  result stays on the call's own entry, and a call with no result yet is
  still running.
- **Keys.** A turn's key must stay the same in every request, since the core
  keeps facts per turn. Use something the harness never renumbers, such as
  the opener's message id.
- **A held call** goes in as a `call` entry whose result has `held: true`
  and `ok: false`. That way a retry is judged as a retry.
- **Leave the call being judged out**, for a `pending_call` and a
  `finished_call` alike. It travels as the request's event, and it joins the
  turn's entries in later requests.
- **Add `turn_ended` only when the core allowed the end.** A held end adds
  nothing, and the turn goes on.

When the harness cannot supply part of this, send less and say so; never
guess:

- It cannot tell who wrote a prompt: send `author: unknown`. No override
  counts from it.
- It cannot list the installed skills: send `installed_skills: null`.
- It cannot check the project's context documents: leave out
  `context_docs`. The orientation hold and closeout note then name none.
- It cannot report a spawned agent's own work: send the spawn's result
  without `agent.entries`. The core judges without it and adds a `warning`
  notice where it needed them.
- It drops reply text: fill `line_text` on calls, as in step 1.

The contract's
[What An Adapter May Leave Out](../stack/enforcement-contract.md#what-an-adapter-may-leave-out)
is the full list. The example's `turns_from` builds the turns from the toy
loop's transcript.

## 3. Call The Core

Send one request for each of these events, with a `session` whose `id`
stays the same for the whole session and whose `agent` says whether a main
agent or a subagent acts. Send a `project` with the project's folders, the
working folder, the agent's home, the agent's configuration folders, and the
installed skills:

| Event | When | What the decision means |
| --- | --- | --- |
| `session_start` | the session starts, resumes, restarts after a compaction, or is cleared | notices only |
| `prompt_submitted` | each prompt arrives, after it is in the turns; a mid-turn prompt too, which changes nothing | records a person's overrides for the turn; notices only |
| `pending_call` | before each call runs | `hold`: do not run it |
| `finished_call` | after each call ran | notices only, such as the closeout note |
| `turn_end` | the agent ends its turn | `hold`: the turn may not end yet |

Ask the core one of two ways. Both give the same decision for the same
request.

**By import**, from Python. Put `adapters/core/` on `sys.path`:

```python
from goated_core.request import decide, settings_from_environment

settings = settings_from_environment("/path/to/state")  # None: the default folder
decision = decide(request, settings)  # a dict; never raises
```

**By command**, from any language. Write the request as JSON on standard
input and read the decision as JSON on standard output:

```bash
python adapters/core/goated_judge.py --state-dir /path/to/state < request.json
```

For any request, even one it cannot read, the command prints a decision and
exits 0. It exits 2 only for arguments it does not know. `--registry PATH` (or
`GOATED_CORE_REGISTRY`) names an installed registry, `GOATED_CORE_STATE_DIR`
sets the state folder, and `GOATED_CORE_SKILL_NAMESPACES` lists plugin
namespaces whose `ns:skill` loads count. [`README.md`](README.md#the-shared-core)
says more about both ways in.

**The usage log.** The core appends what each judged event showed to a
local usage log in JSON Lines, as `stack/schemas/usage-log.schema.json`
defines it:

- **What it records:** each hold with its gate, kind and what it asks for;
  each hold's outcome; each skill load with its cause; route and skip
  lines; reference reads; and code changes and turn ends.
- **What each entry carries:** the adapter's name, the session id and a
  project key.
- **What it never writes:** prompt text, hold text, file content, or a
  project path.

Writing the log is best effort, and a failed write never blocks a call.

- **Choose where it goes.** The core keeps no log unless one is named. Name
  one with `--usage-log PATH` for the command, the `log_path` argument of
  `settings_from_environment`, or `GOATED_USAGE_LOG` for either. With the
  Python call you can also set `Settings.usage_log` to
  `UsageLog(path, adapter)` from `goated_core.usage_log`. `off`, as a path
  or in the variable, keeps none, and so does `usage_log=None`. Use the
  per-user file that [`README.md`](README.md#the-usage-log) gives when you
  want your sessions counted with the Claude Code adapter's. Never put the
  log in a project folder.
- **Name your adapter.** Use a short name, such as `my-loop`: set
  `GOATED_CORE_ADAPTER` for the command or `settings_from_environment`, or
  pass it as `UsageLog`'s `adapter`. An adapter that names none is logged
  as `core`.
- **Keep it out of tests.** Tests, and runs of the conformance runner, must
  never write a person's real log, which may come from their environment.
  Pass `off` or a temporary file explicitly rather than relying on the
  environment. The runner's `setup` gives `usage_log: None` for this.

The example's `python_judge` and `command_judge` are one of each. Both
take an explicit `log_path`, write as `toy-loop-example`, and keep no log
when given none, whatever the environment names.

## 4. Show A Hold To The Agent

A decision is `allow` or `hold`, with its `holds` and `notices`.

- **On a hold before a call, do not run the call.** Show the agent one
  message carrying every hold in order. Each hold is its hold line, then its
  text, as the contract's
  [Hold Messages](../stack/enforcement-contract.md#hold-messages) section
  lays it out:

  ```text
  goated-hold: design | justified-skip
  <the hold's text>
  ```

  Measurement tools parse the hold line, so write it exactly.
- **On a hold at the turn's end, keep the agent working.** Give it the
  message as the harness's answer to its stop. If the harness cannot refuse
  a stop, send the message as a request to continue, and document that.
- **Show notices as the core wrote them,** a hold or not. `fail_open` and
  `warning` in particular must reach the person or agent, and
  `skip_carried`, on a call a lasting skip let through, and `reads_owed`, on
  a write a read gate let through before its reads, and
  `route_continued`, at a person's prompt in a routed task, must reach the
  agent. Requests carry the event model's version, now 5; the core refuses
  any other.
- **Add only what your harness alone can say:** where a route or skip line
  goes so the harness keeps it, and which call can carry it. Never reword or
  drop the core's text; it already names no harness.
- **Never retry for the agent.** The agent answers the hold by loading the
  skill, reading the reference, or writing the line. Its next call is judged
  afresh.

The example's `GoatedAdapter._answer` does this, and
`WHERE_LINES_GO` is its harness's own words.

## Rules Every Adapter Keeps

These are [ADR 0003](../docs/adr/0003-opt-in-framework-enforcement-adapters.md)'s
rules, as they apply to your code:

- **Opt-in.** A person installs the adapter on purpose. No skill, the shared
  policy, or the registry may need it, and no skill file may name it.
- **No free bypass.** Send `prompt_submitted` for every prompt, with its
  true author, so only a person's typed override counts. Add no switch,
  setting, or retry that lets a held call through. A hold clears only on
  proof of use, a justified skip where the hold allows one, or a person's
  override.
- **Fail open, visibly.** When the adapter cannot reach the core, cannot
  build the request, or gets an answer it cannot read, it lets the action
  through and tells the agent why, with "allowed without checks". The
  core does the same for a request it cannot read. See the example's
  `_fail_open` and the contract's
  [Failing Open](../stack/enforcement-contract.md#failing-open).
- **Enforce nothing the contract does not state.** Do not add a gate,
  widen one, or hold on your own judgement. A rule you want goes into the
  contract and the core first, with a conformance scenario.
- **In this repo, standard library only.** Adapter code under `adapters/`
  imports only the standard library and `goated_core`. The validator checks
  it.

## Document What You Cannot Enforce

Give your adapter a README that lists, for each part of the contract its
harness cannot support, what is lost:

- no hook before a call runs: no gate holds a call, the closeout at a
  commit included;
- no hook at the turn's end: the closeout comes as a request to continue,
  or not at all;
- no prompt author: no override counts, so a person cannot stand a hold
  down by typing;
- no subagents, or no view of their work: subagent turns are not judged,
  and a parent's closeout misses their changes;
- tools left as `other`: what they change is never judged.

Then say what each gap costs a person using your adapter.

## Check It With The Conformance Runner

The conformance scenarios in
[`stack/fixtures/enforcement/`](../stack/fixtures/enforcement/README.md) are
written in the event model's terms. The runner plays them through your
adapter by way of a **translator** you write. The translator is a Python
file with a `make_translator(setup)` function that returns an object with
one method per kind of step. Each method does to your harness what the step
describes, with your adapter installed, and reads back what the harness did
as a decision.

| Method | The step | Returns |
| --- | --- | --- |
| `prompt(prompt, continues)` | a prompt arrives; `continues` when mid-turn | the decision |
| `reply(text)` | the agent writes reply text | nothing |
| `call(call, result)` | the agent makes `call`; when it runs, it returns `result` | (decision before it ran, decision after it ran or None) |
| `skill_invoked(skill)` | a person invokes a skill | nothing |
| `agent_finished(agent_id)` | a background agent finishes | nothing |
| `compaction()` | the harness compacts the conversation | nothing |
| `turn_end()` | the agent ends its turn | the decision |
| `session_start(source)` | a session starts | the decision |

`setup` gives the scenario's folders and session: `home`, `project` (under
`home`), `outside`, `state_dir`, `usage_log` (always None: give your adapter
no log), `installed_skills` (None when the scenario
does not say), and `agent`, the event model's `session.agent`. It gives no
agent configuration folder, so pick one under `home`. The call's `result` is
`{"ok": true}` when the scenario gives none. Each step is its own method
call: `compaction()` only compacts, since a scenario that restarts the
session after a compaction has a `session_start` step of its own. A
`branch_grows` step needs no method: the runner itself adds that many lines
to the project's checkout, as a new untracked code file. The
docstring of [`scripts/run_conformance.py`](../scripts/run_conformance.py)
defines each part.

Read each decision from what the harness did, not from the core's answer:
whether it blocked, and the `goated-hold:` lines it showed. Then an adapter
that drops a hold fails. Return each hold with the text that follows its
line, because the runner reads a closeout hold's items from its
`- <Label>: ` lines. Your adapter's own words after the last hold are
harmless unless one of their lines starts that way. The example's translator
reads holds this way. It takes notice kinds from its adapter's record of
each decision, and counts a notice only when the agent was shown its text.
For a call, it splits that record into the `pending_call` decision and the
`finished_call` one. Raise on a call your harness cannot make faithfully, so
that it fails rather than quietly passing.

Run every scenario through your translator:

```bash
uv run python scripts/run_conformance.py path/to/your_translator.py
```

The runner is a repo tool, not adapter code, so it lives in `scripts/`: it
reads the YAML scenarios with PyYAML, which `uv sync` installs. Your adapter
and translator still need only the standard library.

`path.py:factory` names a factory other than `make_translator`. `--file
routing` (or `routing.yaml`) runs one scenario file, and you can repeat it
for more. `--only TEXT` runs
the scenarios whose name contains `TEXT`. The runner prints `PASS` or `FAIL`
and each scenario's name. Under a failure it prints each step that went
wrong, with the decision the scenario expected and the one your adapter
gave:

```text
FAIL writes: a substantial code change waits for design principles
    step 4 (call file_write): expected {'decision': 'hold', 'holds': [('design', 'justified-skip')], 'failures': []}, got {'decision': 'allow', 'holds': [], 'failures': []}
0 of 1 scenarios passed
```

It exits 0 when every scenario it ran passed, and 1 when one failed or none
matched. It exits 2 when it cannot load the translator, for any reason, or
when `--file` names a scenario file it does not have; it then lists the
files it has. A scenario your harness cannot support at all
is a gap to document, not one to make pass.

## The Worked Example

[`example/`](example/) holds a toy tool loop with its adapter, written to
copy from:

- `toy_loop.py`: the harness. It has its own tool names and transcript, and
  offers hooks before and after each tool, at each prompt, at the turn's
  end, and at a session's start. No model and no network: the agent is
  whatever drives the loop, and each tool is a function you supply.
- `goated_example_adapter.py`: the adapter. It implements steps 1 to 4
  above, with each part named after its step.
- `conformance_translator.py`: its translator for the runner.

Run it through the runner:

```bash
uv run python scripts/run_conformance.py adapters/example/conformance_translator.py
```

Its tests in `tests/test_adapter_conformance.py` run every scenario through
it, by the Python call and by the command. They check each request it sends
against the event model, show an agent answering a hold in the loop, and
show a translator that maps a tool wrongly failing the scenarios it should:

```bash
uv run python -m unittest discover -s tests -p "test_adapter_conformance.py"
```

To start your own adapter, copy the example's adapter and translator,
replace the toy loop with your harness's hooks, and change `TOOL_CALLS`,
`turns_from` and `tool_use_for` to your harness's tools and transcript.
