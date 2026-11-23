# GOATED Adapter For Claude Code

An optional set of Claude Code hooks that holds writes, spawns, and commands
until the GOATED router and the skills its route requires have loaded since
the last compaction. It also holds commits, pull requests, spawns, design changes,
security-sensitive edits, and writes during a merge conflict until the skill
that owns each has loaded, and
holds the end of a code-changing turn until it has fresh proof. It enforces
the portable contracts in
`skills/agent-workflows/using-goated-ai-skills/SKILL.md`, `stack/AGENTS.md`,
`stack/fixtures/markers/README.md`, and the trigger each skill states; it adds
no rules of its own
([ADR 0003](../../docs/adr/0003-opt-in-framework-enforcement-adapters.md)).

Skills work the same without it. Install it only if you want enforcement.

## Requirements

- Claude Code with command hooks. The snippet uses the exec form (`command`
  plus `args`); see [Shell-form alternative](#shell-form-alternative) if your
  version lacks it.
- Python 3.11 or later on `PATH`. CI tests 3.11 and 3.14. The adapter and
  the shared core use only the standard library, so they need no packages.

## Install

1. Copy this `claude-code/` folder and the shared core's `core/` folder
   beside it to a stable place, for example inside your installed GOATED
   distribution as `<goated-root>/adapters/claude-code/` and
   `<goated-root>/adapters/core/`. Copy the whole folders: `goated_hook.py`
   imports the `goated_adapter/` package beside it, which calls the rules in
   the [shared core](../README.md#the-shared-core), `../core/goated_core/`.
   An adapter installed inside a GOATED distribution has both already, so an
   install made before the core existed keeps working once its distribution
   is updated, with no change to its settings. Without the core, every hook
   lets its action through with a warning that names the missing package.
   The [`reference-reads`](#registry-references) gate
   reads the installed registry two folders up,
   `<goated-root>/stack/goated-stack.yaml`; if the adapter lives elsewhere,
   set `GOATED_ADAPTER_REGISTRY` to the registry's path. A missing registry
   at the default path turns that gate off quietly; one that does not parse,
   or a path the variable names with no file there, turns it off with a
   warning.
2. Open [`settings.snippet.json`](settings.snippet.json) and replace every
   `<adapter-dir>` with the folder's absolute path. Forward slashes work on
   Windows too.
3. Use `python` as the command on Windows and `python3` on macOS and Linux, or
   give the full path to an interpreter.
4. Merge the five entries under `hooks` into a Claude Code settings file:
   `~/.claude/settings.json` for every project, or a project's
   `.claude/settings.json` for one project. If the file already has a `hooks`
   object, add these entries next to the existing ones rather than replacing
   it.
5. Start a new Claude Code session.

An install made before the `PostToolUse` entry existed has four entries. It
gets the [early closeout note](#early-closeout-note) only once its settings
gain that entry, with its matcher; without it, nothing else changes.

To check the install, start a session and ask the agent to run any shell
command before it has loaded `using-goated-ai-skills`. The call should be
held with a reason that begins `goated-hold: router-first | strict`. If the
GOATED shared policy is not loaded,
the first session start also shows a one-time notice; the
[install guide](../../docs/install.md#load-the-shared-policy-in-claude-code)
shows how to load it.

### Shell-form alternative

Without exec-form support, use a shell command per entry instead of
`command` plus `args`:

```json
{ "type": "command", "command": "python \"<adapter-dir>/goated_hook.py\"" }
```

This works the same but adds the shell's start-up to every call: about 27 ms
per call with Git Bash on the Windows machine measured below. Give the
`PostToolUse` entry this form too, keeping its matcher.

## Disable

Remove the five adapter entries from the settings file, or move them to a
file Claude Code does not load. Start a new session to be sure the change
applies. Claude Code's `"disableAllHooks": true` also stops the adapter, along
with every other hook you have.

## Remove

1. Remove the five adapter entries from the settings file.
2. Delete the copied `claude-code/` folder, and the `core/` folder if no
   other adapter uses it.
3. Delete the state folder `goated-claude-code-adapter/` (see [State](#state)).

Skills keep working unchanged.

## What It Holds

The [enforcement contract](../../stack/enforcement-contract.md) states every
rule this adapter enforces in harness-neutral words: each gate, its kind
(`strict` or `justified-skip`), what it holds and what clears it, the
closeout items, the hold message format, the overrides, and the fail-open
rules. This section says how those rules meet Claude Code's tools and
transcript. The rules live in the [shared core](../README.md#the-shared-core)
(Ticket 081): the routing rules in
[`goated_core/gates.py`](../core/goated_core/gates.py), the action and
closeout rules in [`goated_core/actions.py`](../core/goated_core/actions.py),
and the session state in [`goated_core/state.py`](../core/goated_core/state.py).
A skip line's reason stays in the transcript, where the skill-usage mod
reads it.

The core knows nothing of Claude Code: it reads the
[event model](../../stack/schemas/enforcement-event-model.schema.json), as
[`goated_core/events.py`](../core/goated_core/events.py) holds it, and
judges calls by kind. This adapter calls it through `goated_core.judge`, one
function per hook event, and turns the decision back into hook output.
Three modules translate. The transcript reader
([`goated_adapter/transcript.py`](goated_adapter/transcript.py)) builds the
model's turns from the transcript and removes the reminder and pasted blocks
from a typed prompt before overrides are read.
[`goated_adapter/translation.py`](goated_adapter/translation.py) maps each tool
and its input to a call (which tools are file writes, shell commands, spawns,
commits, or pull requests; the line field of each; which spawns are read-only,
start a side session, or only show a card; which edits make a missing file;
and each call's action key for the friction count) and fills the slots the
rules leave in hold text
([`goated_core/wording.py`](../core/goated_core/wording.py)) with Claude Code's
words: the Skill and Read tools, the line advice, and the carrier sentence.
A slot is marked by two private-use characters, so text a hold quotes, such
as a malformed route line, is never filled. It also upgrades session state
an earlier adapter saved in Claude Code's words (an override record keyed by
`prompt_id`, a shell saved as `Bash` or `PowerShell`) as the core loads it.
The hook entry point ([`goated_adapter/hooks.py`](goated_adapter/hooks.py))
passes Claude Code's own folders as the agent's folders, where no write is
scratch, and its prompt id as the key the core matches a prompt's overrides
by. Two other modules stay with the adapter: `policy.py` and
`onboarding.py` write the session-start notices, which are about where
Claude Code keeps instruction files and skills. A test fails when a core
module names a Claude Code tool, input, transcript or hook field, a tool in
prose, or Claude Code's own folder, or imports anything but the standard
library and the core.

Route and skip lines are read from the agent's reply text and
from one field
of some built-in tool calls: the `description` of a `Bash`, `PowerShell`,
`Agent`, or `Task` call, and the `args` of a `Skill` call, such as
`Skill(using-goated-ai-skills, args: "goated-route: direct")`. Other tools,
MCP tools included, carry no line, because their `description` is often the
payload, such as an issue or merge-request body. Claude Code can
store reply text as a summary that drops the line (see
[Known Limits](#known-limits)), but it keeps a call's input as written, and
the hook sees the input of the call it judges. A line in a call counts from
that call on, so it covers the call itself, and otherwise follows the same
rules as a line in reply text: the same grammar, outside fenced blocks, the
last route line wins, route lines with no write or spawn between them are one
task, and a line counts only in its own turn and agent. No other field counts,
so file text, edit text, and commands never carry a line, and no typed
[override](#user-overrides) is ever read from a call.

A session started from another session gets that session's brief as its
first prompt. A valid route line on its own line anywhere in that brief,
outside fenced blocks and `<system-reminder>` blocks, is the first turn's
route, as if the new session had written it first; when the brief has
several, the last one wins. It meets `router-first`, as a subagent's parent
brief does, until a prompt you type opens a turn: from then on that turn
continues the brief's task as any typed follow-up does (see below), and a
route line that starts a new task needs the router; continuing brings back
no orientation (Tickets 117 and 119). The route's `requires:` skills must still load
in the new session before its first write (`pipeline`), and a later route
line in the turn corrects it as usual. While the brief's route counts, a
`standard` or `full` route also requires orientation
when Claude Code can find `session-start-progressive-disclosure` (a user,
project, or plugin skill): the router selects orientation on such a route
from a brief, and the spawn-brief template says the new session orients
before its first write by reading the sources its brief names or by loading
that skill. Any of three meets it: the skill loads; Read calls of three
distinct files finish, anywhere, each a [whole read](#whole-reads); or
reads of five distinct project files finish, whole or in part (Ticket 119),
since the session started or the last compaction. Reads count across turns
as loads do, and a failed Read does not count (Ticket 098). A finished shell
command that prints a file whole, a `cat` or a PowerShell `Get-Content` with
no range and no pipe, counts as a whole read of that file here, and only
here (Ticket 110); one that prints part of it, a `head`, `tail`, `sed -n`,
or ranged `Get-Content`, counts toward the five. A search such as `grep`,
`rg`, or `Select-String` never counts. The hold names the project's context
documents that exist, as the [early closeout note](#early-closeout-note)
does. The
route line never names the skill, so leaving it out of a corrected line
does not drop it; only a corrected
`goated-route: direct` line or a `lightweight` route line does. A typed prompt
or a compaction ends the brief's route, and the requirement with it, so a
typed `skip session-start-progressive-disclosure` is never needed. When an API
error makes the app resend the turn as a host-written `Try again` prompt,
that prompt continues the
turn, with its route and overrides. Only the session's first prompt counts,
and only in the shape the
desktop app records a brief: text opening `Background (from the session that
started this one)` or `Task (from the session that started this one)` after
any `<system-reminder>` blocks, with `turnOrigin` `host_synthetic` and no
`origin`. A route line in a typed prompt, a later prompt, or another
session's message never counts, and a brief never carries an override. The
`handoff` skill's spawn-brief template says where the parent puts the line.
A brief with a route line also marks the session as briefed, for good (one with none does not): typed prompts and
compactions do not end that, and a briefed session meets no closeout Review
item (see the closeout table below).

The contract's [Gates](../../stack/enforcement-contract.md#gates) table is
the authority for each gate, and its
[Detection Detail](../../stack/enforcement-contract.md#detection-detail)
gives the tables each rule judges by. This table adds only what is Claude
Code's own: which tools make which calls, and which input fields the rules
read.

| Gate | Kind | Holds | Clears when |
| --- | --- | --- | --- |
| `router-first` | strict | An `Edit`, `Write`, `MultiEdit`, or `NotebookEdit`, a spawn, or a `Bash` or `PowerShell` command; a command made only of [plain reads](#plain-reads) passes, as Read and Grep do, and so does a write whose every file is a [scratch file](../../stack/enforcement-contract.md#project-folders-and-scratch-files) | A `Skill` load of `using-goated-ai-skills`; or the session's first prompt is a brief with a route line (see above), until a typed prompt opens a turn; or, in the brief's task with no compaction since, a `goated-route: continue` line in the turn, whoever's prompt opened it; or, in a routed task an earlier turn started, a typed prompt's turn runs as `goated-route: continue`, by that line or by none, compaction or not (Ticket 119). A task is routed when a route line other than bare `continue`, or a brief, started it, or when its bare `continue` turn loaded the router or carried your `skip routing`; a clear (`/clear`) ends the task |
| `route-line` | strict | The first write or spawn after each typed prompt in a session with no task until the turn has a valid route line, in reply text or a call's line field (see above), and after each prompt from elsewhere except another session's message in a session with a task (see [User Overrides](#user-overrides)). In a session with a routed task, a typed prompt's turn runs as `goated-route: continue`, and the prompt gets a notice that new work needs a new route line (Ticket 119) | A valid route line appears in the turn |
| `pipeline` | strict | Writes and spawns while a `requires:` skill has not loaded, or a brief-routed session's orientation is unmet while Claude Code can find `session-start-progressive-disclosure`; a spawn of a [read-only subagent](#plain-reads) passes | Each listed skill loads by the Skill tool, or orientation by that skill or three [whole reads](#whole-reads) by the Read tool |
| `commit` | strict | A `git commit` in a `Bash` or `PowerShell` command, or an MCP tool that records a commit, named `…__push_files`, `…__create_or_update_file`, `…__delete_file`, `…__git_commit`, `…__create_commit`, `…__commit_changes`, or `…__commit`; the tool's `message` is the commit message | `commit-message` [counts as loaded](#loads), the message passes the [content check](#content-checks), and a [change read](#change-reads) follows the last code change that is not comment-only; the [closeout](#closeout-at-commit) is judged beside it |
| `pull-request` | strict | `gh pr create` or `new`, `glab mr create` or `new` in a shell command, or an MCP tool named `…__create_pull_request` or `…__create_merge_request` | `pr-description` [counts as loaded](#loads), and a [change read](#change-reads) |
| `pr-review` | justified-skip | A pull request the `pull-request` gate holds, once it passes, when it is [large](#large-pull-requests); an MCP tool's `base` or `target_branch`, `head` or `source_branch`, and `owner` and `repo` inputs name what is measured | `standards-and-spec-review` [counts as loaded](#loads), and a [change read](#change-reads) |
| `spawn` | strict | An `Agent` or `Task` call, or a `start_session` or `hand_off_to_session` call that carries a brief (see the Spawns bullet below), except a [read-only subagent](#plain-reads) | The skill loads, its template is [read whole](#whole-reads) by the Read tool, and the `prompt` or brief passes the [content check](#content-checks) |
| `design` | justified-skip | The turn's first substantial non-test code write by `Edit`, `Write`, `MultiEdit`, or `NotebookEdit`, or a [shell write that puts new text into the file](#shell-writes) | `software-design-principles` [counts as loaded](#loads), and each [selected reference](#design-references) is [read whole](#whole-reads) by the Read tool |
| `design-reads` | justified-skip | A later write whose [signals](#design-references) select a reference not yet read | Each reference is [read whole](#whole-reads) by the Read tool |
| `reference-reads` | justified-skip | A write tool's or shell command's write that fires a [registry signal](#registry-references) | Each named reference is [read whole](#whole-reads) by the Read tool |
| `review-intake` | justified-skip | A code write once a [reviewer subagent](#reviewer-subagents) started by `Agent` or `Task` has reported | `receiving-code-review` [counts as loaded](#loads) |
| `security` | justified-skip | A write tool's or shell command's write to a [security-sensitive path](../../stack/enforcement-contract.md#security-sensitive-paths); test code meets no category a word in its name selects | `code-security-review` [counts as loaded](#loads) |
| `scripted-edit` | justified-skip | A shell command whose [inline script](#inline-scripts) writes code; the hold asks for the change to be made with `Edit`, `MultiEdit`, or `Write` | A skip line naming `software-design-principles`, or the typed override |
| `conflict-resolution` | justified-skip | A [conflict](../../stack/enforcement-contract.md#conflicts) opened by an `Edit` or `MultiEdit` whose `old_string` holds a marker, a Read whose numbered lines show one, a `Bash` or `PowerShell` file printer (`cat`, `Get-Content`) or `git diff` whose output shows one, or a git command's result; a finished commit, by a shell `git commit` or a commit tool, ends it | `resolving-merge-conflicts` [counts as loaded](#loads) |
| `repeated-failure` | justified-skip | A write once a check in a `Bash` or `PowerShell` command has [failed twice](../../stack/enforcement-contract.md#repeated-failures); a call held by the adapter or another hook, refused at a permission prompt, or interrupted never ran | `diagnose` [counts as loaded](#loads) |
| `closeout` | justified-skip | A commit, or the `Stop` hook, in a turn that changed code, a security-sensitive file, or setup | Every item below is met or skipped |

The contract's [Closeout Items](../../stack/enforcement-contract.md#closeout-items)
table is the authority for each item; this one adds Claude Code's detail.

| Item | Needed when | Met by | Skip line names |
| --- | --- | --- | --- |
| Proof | A change not already proved | A [check](../../stack/enforcement-contract.md#checks) in a `Bash` or `PowerShell` command after the last code change | `verification-before-completion` |
| Unfinished work | The last check after the change failed | `handoff` counts as loaded | `handoff` |
| Docs | A code file outside the tests changed | `doc-sync` counts as loaded, and a [change read](#change-reads); or a doc changed after the last code change, then a change read, as the contract states | `doc-sync` |
| Design red flags | As the contract states | `software-design-principles/references/red-flags.md` [read whole](#whole-reads) by the Read tool after the last code change that is not [comment-only](#comment-only-edits), then a [change read](#change-reads) | `software-design-principles` |
| Review | The branch is [large](#large-branches) and the session was not started from a brief | A [reviewer subagent](#reviewer-subagents) started by `Agent` or `Task`, or `standards-and-spec-review` and a [change read](#change-reads) | `standards-and-spec-review` |
| Verification | As the contract states | `verification-before-completion` counts as loaded | `verification-before-completion`, the Proof item's skip line, so one line answers both |
| Security | As the contract states | A [change read](#change-reads) | `code-security-review` |
| Setup | A [package install or setup file](../../stack/enforcement-contract.md#package-installs-and-setup-files), such as a `settings*.json` under `.claude/` | `setup-scribe` counts as loaded | `setup-scribe` |

A subagent's installs and writes count toward the parent's closeout; that
subagent's own `setup-scribe` load or skip line meets them, as the parent's
does.

**Project folders.** The project's folders, as the adapter passes them to
the core, are `CLAUDE_PROJECT_DIR` when Claude Code sets it and the hook
input's `cwd`; the core adds the checkout above either. Claude Code's own
folders, such as `~/.claude`, are the agent's folders, where no write is
scratch. The core's
[path rules](../../stack/enforcement-contract.md#project-folders-and-scratch-files)
decide what is outside.

- **Writes** are `Edit`, `Write`, `MultiEdit`, and `NotebookEdit`, and a
  `Bash` or `PowerShell` command that writes files (see
  [Shell writes](#shell-writes)). **Spawns** are `Agent` (or `Task`, its name
  in older Claude Code versions), `mcp__ccd_session__start_session`, and
  `mcp__ccd_session__hand_off_to_session`; they hand work on, so they are held
  like writes. A `start_session` call whose `initiation` is `offer` or
  `own_initiative`, with no `proposal_id` (the field that starts a saved
  proposal), only shows a card: nothing runs until the user starts it, so it
  passes `router-first`, `route-line`, and `pipeline`. An `own_initiative` card carries a brief,
  which runs when the user starts the card, so it still meets the `spawn`
  gate; an `offer` card carries none. Any other `initiation`, or none, a call
  with a `proposal_id`, and `hand_off_to_session` are held as spawns. A
  session tool call with no brief, such as an offer card, is not a spawn for
  the `spawn` gate. **Commands** are `Bash` and `PowerShell`.
  Every other tool, including reads and the Skill tool, is never held.
- <a id="loads"></a>**Loads count until the next compaction.** A
  successful load counts from its call until the next compaction or `/clear`,
  in this turn or a later one, for every hold that asks for a load: the
  `pipeline` gate's required skills, the action gates, and the closeout's
  items. That is the point where the skill's text really leaves the agent's
  context; before it, a reload would only repeat text still there. The
  template reads the `spawn` gate asks for count the same way, and so do
  [design references](#design-references) read. The [state](#state) keeps
  the loaded names and the reads; a resumed session keeps them, and missing
  or reset state counts as not loaded.
- **Proof of use** is a successful Skill-tool load read from the transcript (a
  `Skill` tool call whose result is not an error), or a skill the user invoked
  by typing `/<skill>`. Naming a skill in text is not proof. A load counts by
  its bare name only: `someplugin:tdd` does not satisfy `requires: tdd`. If you
  installed GOATED as a Claude Code plugin, set `GOATED_ADAPTER_SKILL_NAMESPACES`
  to its namespace (comma-separated for several), for example in the settings
  file's `env` block. A **required read** is a `Read` tool call on the
  reference file, under any install folder, whose result is not an error.
- **Compaction** is a `SessionStart` with source `compact`, and `/clear`
  counts the same: the router and every other skill must load again, and the
  reads be made again. The route carries over, as the contract's
  [Prompts, Turns, And Tasks](../../stack/enforcement-contract.md#prompts-turns-and-tasks)
  says.
- The rest, per-turn lines and checks, tasks, no free retry, and every hold
  at once, is the contract's [Holds](../../stack/enforcement-contract.md#holds).
  A held call is recorded as an error, so it never counts as a change or a
  check.

### Large pull requests

The rule and its git commands are the contract's
[Branch Size](../../stack/enforcement-contract.md#branch-size). In Claude
Code, git runs in the hook's working folder, and an MCP pull-request tool's
`base` or `target_branch` input names the base, `head` or `source_branch`
the head, and `owner` and `repo` the repository. The cost is in
[Latency](#latency).

#### Large branches

The closeout's Review and Verification items measure the branch as the
contract's [Branch Size](../../stack/enforcement-contract.md#branch-size)
says, in the hook's working folder, so a commit made elsewhere, with
`git -C <dir>` or after a `cd`, is measured as the hook's folder's branch.

#### Reviewer subagents

A reviewer subagent is a finished `Agent` or `Task` spawn that meets the
contract's [Reviewer Agents](../../stack/enforcement-contract.md#reviewer-agents)
rule. The gate records which templates each spawn's brief followed, by the
call's id, in the session's [state](#state). A spawn started in the
background (its result says `async_launched`) has finished only once its
completion arrives later in the turn: a `<task-notification>` naming the
agent's id with a `completed` status, or the agent's
`<agent-message from="<id>">` hand-back, as a prompt or a queued command. A
side session started with a reviewer brief (`start_session` or
`hand_off_to_session`) is not one: its result arrives at once but says only
that the review started.

### Design references

The signals and the reference each selects are the contract's
[Design Reference Signals](../../stack/enforcement-contract.md#design-reference-signals),
in [`../core/goated_core/design_reads.py`](../core/goated_core/design_reads.py).
In Claude Code, an edit's text is an `Edit`'s `old_string` and `new_string`,
each `MultiEdit` entry's, a `Write`'s `content` (compared with the file on
disk), or a `NotebookEdit`'s new source, whose replaced text the call does
not show. An `Edit` with no `old_string` may make a missing file, so it
counts as creating one. A `MultiEdit` with an `edits` entry that is not an
edit cannot be counted, so it is not small. A `goated-design-reads:` line,
which earlier versions asked for, is ignored like other prose.

A reference counts as read after a finished [whole](#whole-reads) `Read` of a
path ending in `software-design-principles/references/<file>`, in this turn
or an earlier one, until the next compaction: the [state](#state) keeps the
names read, and a compaction's or `/clear`'s `SessionStart` clears them. A
skip line or a typed `skip software-design-principles` clears both gates for
the turn. Tune the signals from the skill-usage mod's counts.

### Registry references

The signals are the contract's
[Registry Reference Signals](../../stack/enforcement-contract.md#registry-reference-signals),
in [`../core/goated_core/reference_reads.py`](../core/goated_core/reference_reads.py).
The adapter reads the installed registry (see [Install](#install)) on each
write, with its own reader for the registry's plain YAML, since it uses only
the standard library. A write tool is `Edit`, `Write`, `MultiEdit`, or
`NotebookEdit`; a reference counts as read after a finished
[whole](#whole-reads) `Read` of a path ending in
`<skill>/references/<file>`, kept in the [state](#state) until the next
compaction.

### Shell writes

A `Bash` command is read as a `posix` shell and a `PowerShell` command as a
`powershell` shell; what each writes, and how a `cd` moves its folder, is
the contract's [Shell Reading](../../stack/enforcement-contract.md#shell-reading),
in [`../core/goated_core/shell.py`](../core/goated_core/shell.py).

#### Shell writes the design gates judge

Which shell writes the `design` and `design-reads` gates judge, and how
their lines are counted, is the contract's
[Shell Writes The Design Gates Judge](../../stack/enforcement-contract.md#shell-writes-the-design-gates-judge).

#### Inline scripts

Which inline scripts are read, and their write calls, are the contract's
[Inline Scripts](../../stack/enforcement-contract.md#inline-scripts), in
[`../core/goated_core/script_writes.py`](../core/goated_core/script_writes.py).

### Plain reads

Before the router loads, `router-first` passes a `Bash` or `PowerShell`
command made only of the contract's
[plain reads](../../stack/enforcement-contract.md#plain-reads), as it passes
Read and Grep. `true` in Bash and `$null` in PowerShell are plain reads, and
a hold names either as the carrier for a line (see
[Hold messages](#hold-messages)).

A spawn of a read-only subagent type, `claude-code-guide` (the
`subagent_type` of an `Agent` or `Task` call, matched exactly), delegates
reads, so it passes `pipeline` and `spawn`: Claude Code ships it with Glob,
Grep, Read, WebFetch, and WebSearch only. It still meets `router-first` and
needs a route line in the turn. `Explore` and `Plan` are held like any other
spawn: they keep Bash and PowerShell, and a subagent's own calls meet no
routing gate (see [Subagents](#subagents)). Any other type, a spawn with no
type, and side sessions are held as before. The exemption trusts the name: a
project or user agent file named `claude-code-guide` replaces the built-in,
with whatever tools it lists, and is exempt too. The list is
`READ_ONLY_SUBAGENTS` in `translation.py`.

### Closeout at commit

Agents commit before they report, so a commit meets the closeout first. A
commit, as the `commit` gate sees one (a git commit in a shell command or an
MCP commit tool), is held while the turn has an unmet closeout item. The
hold's first line is the closeout's,
`goated-hold: closeout | justified-skip`, its items are the closeout's
texts, and each item accepts its usual skip line. It opens
`Before committing in this turn`; for a shell commit it adds that the whole
command was held, so a check chained before the commit in the same command
has not run yet and does not count. An MCP commit tool has no command, so
its hold leaves that out. An unmet `commit` hold comes first, in the same
message, naming each of its own asks still unmet, so one held commit shows
everything it needs.

The `Stop` closeout stays as a backstop. A commit changes no file, so an
item met before the commit stays met at `Stop`; a turn that never commits
meets the closeout only at `Stop`. A subagent's commit meets the closeout
judged from its own turn (see [Subagents](#subagents)).

A turn that changes code by a file edit tool learns its items early, from
the [early closeout note](#early-closeout-note), so it can meet them before
its report instead of reporting again after the `Stop` closeout.

### Whole reads

A hold that asks for a file to be read asks for all of it: a required
[design reference](#design-references), a [registry reference](#registry-references),
a spawn template (`handoff`'s `references/spawn-brief.md`, and
`subagent-driven-development`'s implementer and reviewer prompts), and
`red-flags.md` for the closeout's Design item, wherever its read is judged.
A finished `Read` counts only when its input has no `limit`, `offset`, or
`pages` field, whatever the field's value, since a range the call does not
show is taken as partial (Ticket 092). The hold says to read the whole file.
A whole read in an earlier turn counts until the next compaction, as any
read of these does; partial reads never add up to a whole one. A
[change read](#change-reads) is not judged this way: a `Read` of part of a
changed file still counts as one.

### Change reads

What counts as a change read, and which change each step's read must
follow, is the contract's
[Change Reads](../../stack/enforcement-contract.md#change-reads). In Claude
Code, a `Read` of a changed file counts, whole or not, and so does a diff
printed by a `Bash` or `PowerShell` command. A read chained in the same
command as the commit, or made in parallel with the held call, has not
finished when the call is judged, so it does not count. An MCP tool that
commits or opens a pull request skips the read when the turn changed no
project file.

#### Comment-only edits

Which edits are comment-only is the contract's
[Comment-Only Edits](../../stack/enforcement-contract.md#comment-only-edits).
In Claude Code, an `Edit` or `MultiEdit` can be comment-only; a `Write`, a
`NotebookEdit`, and a shell write always count as a change.

### Content checks

The checks are the contract's
[Content Checks](../../stack/enforcement-contract.md#content-checks), in
[`../core/goated_core/contracts.py`](../core/goated_core/contracts.py). In
Claude Code, a commit message is read from the `Bash` or `PowerShell`
command, or from an MCP commit tool's `message`; a spawn brief is an `Agent`
or `Task` call's `prompt`, or a session tool's brief, an offer card's
included.

### Hold messages

Every hold, whether a denied tool call or a blocked `Stop`, returns a reason
whose first line has the format the contract's
[Hold Messages](../../stack/enforcement-contract.md#hold-messages) owns,
with the pattern the first line matches and the closeout's item labels; the
skill-usage mod parses it. Its [Gates](../../stack/enforcement-contract.md#gates)
table owns the list of gates. The hook's decision belongs to the first hold
of a message; the skill-usage mod reads every hold line and counts each hold
as if shown alone. A test checks every hold text against the registry's
skill names. The core returns the rule text; the adapter fills in what only
Claude Code can say:

- A hold that a route or skip line can clear (`route-line`, `pipeline`,
  `design`, `design-reads`, `reference-reads`, `review-intake`, `scripted-edit`, `security`,
  `conflict-resolution`, `repeated-failure`, `pr-review`) says that a line in reply text may not be
  seen (see [Known Limits](#known-limits)), and to put the line in the held
  call's description, or in the description or Skill `args` of a call made
  earlier in the same message, when the held call is a write, or in an
  earlier message of the turn, and make the call again. It then says
  the user can type the matching override. It names those fields without
  backticks, since the mod would read a backticked bare word as a skill.
  That advice is given in full on only one such hold of a turn, holds on
  calls made in parallel included. Every other one in the turn gives one
  sentence instead: put the line in a shell or agent call's description or a
  Skill call's args, or tell the user they can type the override. The hold
  that gives it in full is the first to claim the turn's marker (see
  [State](#state)), one exclusive file create, so of several hooks running at
  once only one can claim it. When the marker cannot be made or read, each
  such hold gives the full advice. The next turn's first such hold gives it
  in full again. A subagent's turns claim their own marker, so each
  subagent gives the full advice once per turn, apart from its parent.
- A message with two or more such holds gives the advice once, after the
  last hold's own text: each hold keeps its skip or route line, and one
  closing section says to put each line in those fields and names every
  hold's override once. It is full or one sentence by the same claim.
- Such a hold on a call with no field a line can go in, such as an `Edit`
  or `Write`, ends its message by naming a carrier in the session's shell:
  a Bash call with the command true, or, in a session whose last shell call
  was PowerShell, a PowerShell call with the command $null (true is no
  command there), with the line in its description. Both are
  [plain reads](#plain-reads), so they pass every hold, before and after the
  router loads. Before the session's first shell call the carrier is Bash.
- A hold that repeats an ask the turn already showed in full is short, as
  the contract says. Each ask claims its own turn marker, apart from the
  advice's; when a marker cannot be made or read, the full text is given.
- A required read names the Read tool and asks for the whole file, with no
  `limit`, `offset`, or `pages`.

Claude Code records a denied call as a `tool_result` with `is_error: true`
whose content carries this reason, and a blocked `Stop` as the reason shown
to the agent. Claude Code 2.1.325 wraps that reason as `Stop hook blocking
error from command: "<command>": <reason>`, so the hold line follows the
wrapper on the same line. The outcome of a hold is read from what follows in the
transcript: the skill load, read, change read, or skip line that cleared it, or the user
override recorded for the turn.

## User Overrides

Overrides come only from prompts a person typed. The user-prompt hook records
the phrases below, and the gates apply them only to the turn that prompt
opened, after checking the transcript's record of who wrote it, and only until
that turn ends with `Stop` (see Subagents for a report arriving later). Text
an agent writes never counts. Matching ignores case, harness `<system-reminder>`
blocks, and text you pasted, which Claude Code wraps as
`<pasted_content id="…">` … `</pasted_content id="…">`: a phrase inside a
pasted report is not an override, while one you type before or after the block
is. A paste ends only at a close tag with its own id, so a close tag or a
nested paste quoted inside it cannot end it early, and a paste with no close
tag runs to the end of the prompt. A phrase negated
just before it, such as "don't skip routing", "never skip tdd", or "no need to
skip doc-sync", is not an override.

The phrases and their effects are the contract's
[Overrides](../../stack/enforcement-contract.md#overrides) table. In Claude
Code, `<skill>` in `skip <skill>` must be a skill Claude Code can find (user,
project, or plugin skills); when none can be found, a GOATED registry skill
name. So "skip line" or "skip the first two lines" is not an override. The
name may be wrapped in backticks, as in ``skip `tdd` ``, or carry a backtick
on one side only. A commit-message override matches the subject line,
whitespace aside; a commit with another message, or with none inline, is
still held, and the skill name `commit-message` is not such a phrase.

Claude Code also submits prompts nobody typed in this session:

- **Background results**, such as the `<task-notification>` that reports a
  finished background task, a desktop-app side-session event, or the
  host-written `Try again` the app sends after an API error. They carry
  agent output, so they never yield overrides, and they do not start a new
  turn: the typed prompt's route line and overrides still cover what follows.
- **Requests from elsewhere**, such as a subagent's final report, a message
  from another Claude session, a brief from the session that started this
  one, or any prompt whose recorded origin is not a person. They start a new
  turn, which needs its own route line (`goated-route: continue` when it
  continues the current task; a session's first brief may carry it, see
  [What It Holds](#what-it-holds)). The one exception is another session's
  or agent's message: a `peer` prompt whose `<cross-session-message>` or
  `<agent-message>` tag names the sender its `origin.from` names. In a
  session that already has a task, its turn runs as `goated-route: continue`
  until a route line in it says otherwise; its skip lines, checks and change
  reads still start empty. A scheduler's or the desktop app's prompt, or a
  peer prompt in any other shape, is not such a message and needs its route
  line as before. They never carry overrides: not ones they quote,
  and not ones you typed earlier, which covered only the turn your prompt
  opened. The adapter neither records nor announces an override for them.
  The user-prompt hook's input does not say where a prompt came from, so the
  hook recognizes these by their opening text, such as the line `Another
  Claude session sent a message:` that opens both a subagent's report and
  another session's message. The gates check again against the transcript,
  where Claude Code marks such a prompt with `origin.kind` `peer` (and
  `isMeta`), so one whose text the hook misses still applies no override.

A prompt you type that starts with a pasted report or message in that shape
reads as one of those requests, so an override typed after the paste does
not count. Type the override before the pasted text.

Claude Code shows a short notice when the adapter records an override. The
same sentence, `GOATED Claude Code adapter: recorded your override for this
prompt: "<phrase>"`, also goes into the turn's context as the hook's
`additionalContext`. Each phrase is recorded as typed, without backticks; a
commit-message override is recorded as `commit message`, without its text.
A notice reaches a Claude Code mod with no text, so the
[skill-usage mod](skill-usage/README.md) counts overrides from that context.
The phrase set lives in [`goated_core/overrides.py`](../core/goated_core/overrides.py);
change it and this table together.

A skip line that clears a hold asking only for reads lasts the task for
those references on files of the same kind, until a new task or a
compaction. Those holds are `reference-reads`, and `design-reads` or
`design` once `software-design-principles` is loaded (see the contract's
Holds). When such a skip lets a later call through and no gate holds it,
the core's `skip_carried` notice goes to the agent as that call's
`additionalContext`.

A file edit that `design-reads` or `reference-reads` would hold for reads
alone, or `design` once `software-design-principles` is loaded, is applied
instead, at any size; a shell write is, at thirty or more counted lines. The core's
`reads_owed` notice, naming each reference, goes to the agent as that
call's `additionalContext`, and the closeout's Reads item asks for the
reads and a change read after them (see the contract's Closeout Items).

## Subagents

A hook call from inside a subagent carries `agent_id`. There:

- the routing gates do not apply, because the parent's brief carries the route;
- the action gates (`commit`, `pull-request`, `pr-review`, `spawn`, `design`,
  `design-reads`, `scripted-edit`, `security`, `conflict-resolution`,
  `repeated-failure`) apply,
  `reference-reads` and `review-intake` aside, judged from
  the subagent's own transcript, which Claude Code keeps in
  `<session-id>/subagents/agent-<agent_id>.jsonl` beside the main one. A
  subagent must load the skill itself: the parent's loads do not count, and
  only its own current turn's loads, template reads, and design references
  count;
- no override applies, because nobody types a subagent's prompts;
- the closeout gate does not run when the subagent stops; the adapter
  registers no `SubagentStop` hook. A commit, though, meets the closeout judged from the subagent's own turn: its
  changes, checks, loads, reads, and skip lines, as a commit's closeout
  holds the main agent (Ticket 098). The subagent was started from its
  parent's brief, so, as a briefed session, it meets no Review item, and it
  has no route of its own, so a parent's `full` route never brings it the
  Verification item; a sensitive change or a large branch still does. Code a
  subagent changed also counts toward the closeout of the parent turn that
  spawned it. The parent finds the subagent through the `agentId` that
  Claude Code records in the spawn's result.

If the subagent's transcript cannot be found, the call fails open with a
warning; at closeout, its changes are left out, with a warning.

A background subagent's final report can reach the parent in two ways: as a
queued attachment inside the turn, or as a prompt that Claude Code records as
a message from another session (an `isMeta` entry with `turnOrigin: peer`, an
`origin` of kind `peer` whose `from` is the agent's id, and text opening
`Another Claude session sent a message:` then `<agent-message from="<id>">`).
Either way the report continues the turn when the adapter can tie it to a
spawn of this session: the prompt's `origin.from` and its tag name the same
agent, and an earlier spawn result in the main transcript, after the last
compaction and within the read limit, records that agent as its `agentId`.
Then the turn's route line, skip lines, overrides, checks and change reads
all stand, a brief's route does not end, the closeout judges the whole turn,
and the user-prompt hook announces no override and resets nothing.
`review-intake` sees a reviewer's report either way. A report carries no
override of its own. A report that arrives after the turn ended, once the
adapter's `Stop` hook let it end, still continues the turn's route, route and
skip lines, checks and change reads, but the overrides typed in that turn no
longer apply. The user-prompt hook sees no `origin`, so it takes typed text
shaped like such a report for one and records nothing; the gates read the
typed origin from the transcript and open a new turn, to which no override
applies. A prompt the adapter cannot tie to one of its spawns,
such as another session's message, a scheduler's prompt, a report naming an
agent this session never spawned, or a shape the adapter does not know,
opens a new turn as before.

## Session Start Notices

At the first session start the adapter says once, in a notice you see and in
the agent's context, when:

- the GOATED shared policy is not in any instruction file Claude Code loads;
- the `using-goated-ai-skills` skill is not among your user, project, or
  plugin skills. Without it, router-first never clears; type `skip routing` in
  a prompt to proceed, or install the router.

At a session start it also says, once per project, which agent files the
project lacks at its root, naming the onboarding skill that writes each, as
those skills state:

| Missing file | Skill named |
| --- | --- |
| `AGENTS.md`, `CLAUDE.md`, or `.claude/CLAUDE.md` | `agent-instructions-integrator` |
| `docs/agents/context-matrix.md` | `context-matrix-map` |
| `docs/agents/project-standards.md` | `project-standards-calibration` |

The project root is `CLAUDE_PROJECT_DIR` when Claude Code sets it, else the
nearest folder at or above the session's folder holding `.git`, else that
folder. Which skills the notice last named is recorded beside the session
state (see [State](#state)), never inside the project. The notice shows again
only when a file goes missing that it did not name before; a file added back
brings none.

At the next prompt after a session's third declined or unanswered hold, it
says once per session that the `retrospective` skill can turn that friction
into improvements, as that skill states. A hold is declined when a skip
line naming its skill follows it, and unanswered when it is still open at the
next typed prompt. It is answered, and counts as neither, when the same gate
later lets the same action through: an edit of the same file, the same
command, a commit or pull request whatever its message, or a spawn of the
same tool. A closeout hold is answered by any later `Stop` or commit the
closeout lets through. A hold is also answered once every skill it names is
loaded and every reference it names is read. A `scripted-edit` hold names
its skill only in the skip line it offers, since loading that skill does
not clear it; it is answered by a later write tool call that goes through
to a file its script named, or to any file when the script named one only
at run time. One the next typed prompt's
override stands down counts as neither too. A gate counts once per turn,
however often it holds in that turn, and only the main agent's holds count.
Holds still open at a compaction or `/clear` are dropped uncounted, since
reading restarts after the boundary. The notice waits for a prompt you type;
a message from another session or agent does not bring it.

Neither notice blocks a call or a `Stop`.

## Early Closeout Note

The closeout fires at a commit or at `Stop`, and in a turn that changes code
without committing, `Stop` comes after the agent's report. So after the main
agent's first finished code change of a turn by a file edit tool (`Edit`,
`Write`, `MultiEdit`, `NotebookEdit`), the `PostToolUse` hook adds one note
to the agent's context naming the closeout items the turn will meet, each in
its short form, and saying they can be met before the final report. For
example, a non-test code change brings Proof and Docs; a test file alone
brings Proof; `software-design-principles` counted as loaded with a
substantial change adds the Design red-flags item; a `full` route adds
Verification. An item already met or skipped is left out. The note opens by
naming the project's own context documents among `CONTEXT.md`,
`docs/agents/context-matrix.md`, and `docs/agents/project-standards.md` at
the project's root, the ones that exist, and names none when none does
(Ticket 119; first since round 7, R11). The orientation hold names them the
same way.

- The items are the closeout's own, judged as if the turn ended at that
  call, from the hook's payload (`tool_name`, `tool_input`,
  `tool_response`), since the transcript may not show the call yet. The
  transcript and state say only what the payload cannot, such as which
  skills count as loaded. The note leaves out what it cannot tell without
  more work: the Review item and a large branch's Verification, which need
  git to measure the branch, and the work of spawned subagents.
- One note per turn, claimed on the turn marker under its own purpose
  (see [State](#state)), so it never meets the unseen-line advice's claim or
  a hold's. A turn the closeout already held, at a commit or a `Stop`,
  gets none: that hold named its items. A turn that already has its note
  is known from the marker alone, without reading the transcript.
- A docs file, a file outside the project, a call that failed or was held,
  a subagent's edit, and a code change by a shell command bring none; the
  hook's matcher starts it only for the file edit tools, so no other call
  starts a hook process.
- The note holds no call and no `Stop`. The closeout is unchanged and still
  decides. When the note's marker cannot be made or read, or the hook
  fails in any other way, such as a transcript that does not yet show the
  call's prompt, the note is left out with no warning: the edit has
  already run, so unlike [Failing Open](#failing-open) there is no action
  to explain, and the call's `PreToolUse` has already warned of the same
  cause.

The skill-usage mod reads two things in hook context: `goated-hold:` lines,
and the adapter's sentence recording a typed override. The note is neither,
so the mod counts no note.

## Failing Open

The adapter never blocks because of its own failure. It lets the call through
and shows a warning that starts `GOATED Claude Code adapter:` when:

- the hook input is not readable JSON or lacks `session_id` or
  `transcript_path`;
- the transcript, or a subagent's own transcript, cannot be read, or the
  current turn alone is larger than the
  64 MB read limit. Older turns beyond the limit are simply not read, as if
  they had been seen;
- the transcript does not show the prompt the call belongs to (its
  `prompt_id`) within 1.5 seconds. The call itself need not be there: it is
  judged from the hook input (see [Latency](#latency));
- the adapter hits an internal error;
- the shared core, `../core/goated_core/`, cannot be imported, such as when
  the `core/` folder was not copied beside this one;
- on macOS and Linux, its state folder is a link, belongs to another user, or
  is writable by others, because planted state there could make holds pass.

Saved state that cannot be read, or has an unexpected shape, is reset with a
warning; a reset can only re-hold, never pass. A missing state file starts
fresh the same way, without a warning. Fresh state cannot tell whether the
session had a task, so `goated-route: continue` stays held until a full route
line starts one, unless the session has just started (a `SessionStart` with
source `startup`) or the adapter has read its transcript from the first turn.
If saving state fails, for
example while a parallel hook has the file open on Windows, the hold decision
still stands and a warning says the state was not saved.

## State

The shared core keeps the session state
([`goated_core/state.py`](../core/goated_core/state.py)), keyed by Claude
Code's session id, in the folder this adapter names: one small JSON file per
session in a `goated-claude-code-adapter/` folder, the same folder as before
the core existed:

- on macOS and Linux, under `$XDG_STATE_HOME`, or `~/.local/state` when that
  is not set, rather than the shared `/tmp`, so another local user cannot
  pre-create it;
- on Windows, under the per-user temporary folder (`%TEMP%`);
- anywhere you choose with `GOATED_ADAPTER_STATE_DIR`.

It holds the current task's route, whether missing or reset state lost the
task, whether the session's first prompt was a brief, whether the router loaded, which GOATED skills loaded and which design
references, skill references, and spawn-brief templates were read since the
last compaction
(see [Loads](#loads)), digests of the first three distinct files the Read
tool read or a shell command printed whole since then, and of the first five distinct project files either read or printed whole or in part, which orient a session routed by its brief, which brief templates each spawn
of the latest turn followed when the `spawn` gate let it through (see
[Reviewer subagents](#reviewer-subagents)), the last turn seen, the
latest typed overrides, and the friction count behind the retrospective
notice (see [Session Start Notices](#session-start-notices)): the holds still
open, with the action each held, the skills, references, and skip lines it
names, and how much of its turn came before it, the gates that held in the latest turn, how many
holds were declined or left unanswered, and whether the notice was shown. It
holds no prompt or reply
text beyond the short override phrases and a commit message the user typed.
Beside the state files, a `turn-markers/` folder holds empty files for the
session, and for each subagent of it, named for the current turn and a
purpose: the [unseen-line advice](#hold-messages), an ask (a gate and
what it found unmet, or one closeout item) whose full text a hold of that
turn gave, or the [early closeout note](#early-closeout-note). Claims for
different purposes in one turn never meet. A claim in a new turn drops its
owner's markers of other turns, and a `SessionStart` after compaction or
`/clear` deletes the session's and its subagents'. The state also keeps the
shell the session last called (`posix` or `powershell`), which names the
carrier a hold offers for a line. A state file an adapter from before Ticket
080 saved names the tool instead (`Bash`, `PowerShell`) and is read the same,
as is one from before Ticket 081, whose override record is keyed by
`prompt_id` where the core keys it by `prompt`.
An older adapter reading a newer state file takes the shell as a tool name,
so until the session's next shell call its carrier sentence names a
`posix` or `powershell` call, with Bash's command `true` either way. An `onboarding-notices/` folder holds one file per project, named by
a digest of the project's path, listing the skills its onboarding notice last
named.
The action and closeout gates keep no state of their own: they read the
current turn, the loads, design and skill references, and templates read
since the last compaction, and, for the closeout's Review item, the
templates recorded for its spawns. Files are not pruned automatically;
deleting the folder between sessions is safe.

The adapter also writes the core's [usage log](../README.md#the-usage-log),
as `claude-code`, to `GOATED_USAGE_LOG` or the core's per-user default
(`%LOCALAPPDATA%\goated\usage-log.jsonl` on Windows,
`~/.local/state/goated/usage-log.jsonl` elsewhere), never to the project.
`GOATED_USAGE_LOG=off` keeps none. It keys each session by Claude Code's
session id and its project by a salted digest of `CLAUDE_PROJECT_DIR`, or of
the hook's `cwd` when that is unset. A `usage-log/` folder beside the state
files keeps how far the log has read each session's turns. A log that
cannot be written changes no hold and adds one warning per session.

## Latency

Measured on 2026-11-16 on Windows 11 with Python 3.13 and an Intel Core
i9-14900K, spawning `goated_hook.py` in exec form, 30 runs each:

| Case | Median | p90 |
| --- | --- | --- |
| Interpreter start alone (`python -c pass`) | 22 ms | 23 ms |
| `UserPromptSubmit` or `SessionStart` | 56 ms | 59 ms |
| `PreToolUse`, 20 KB transcript | 58 ms | 63 ms |
| `PreToolUse`, real 5.3 MB session transcript | 70 ms | 79 ms |
| `PreToolUse`, 88 MB synthetic transcript, 300-call current turn | 70 ms | 78 ms |

The reader reads only the current turn from the end of the file, so
transcript size barely matters. Most of the cost is interpreter start-up and
the `json` and `re` imports. The action and closeout gates (Ticket 031) added
about 4 ms: on the recorded 20 KB fixture, 30 runs each, the median went from
60 to 64 ms. A commit or pull request whose skill has loaded also reads the
transcript of each subagent the turn spawned, as the closeout does, to find
the changes its change read must follow; other calls never read them. That
case was not measured.

Translating Claude Code's calls and transcript into the event model (Ticket
080) adds 1 to 1.5 ms of work per hook. Measured on 2026-11-18 on the same
machine with the uv-managed Python 3.14, before and after, in two rounds:

| Case | Before | After |
| --- | --- | --- |
| In process (`run_hook`), 300-call turn, 150 runs: `PreToolUse` of an `Edit` | 19.3, 19.9 ms | 20.7, 21.2 ms |
| The same, `PreToolUse` of a `Bash` command | 6.3, 6.8 ms | 7.8, 7.7 ms |
| The same, `Stop` | 11.9, 12.3 ms | 13.5, 13.9 ms |
| Spawned in exec form, 202 KB transcript, 30 runs: `PreToolUse` of an `Edit` | 211, 209 ms | 208, 201 ms |
| The same, `Stop` | 202, 202 ms | 200, 195 ms |

Spawned, the difference is lost in the run-to-run spread. Those medians are
about three times the table above because they were measured with a
different interpreter: the project's virtual environment of the uv-managed
Python 3.14 takes 41 ms to start alone, against 22 ms for the system Python
3.13 the table used, and it imports more slowly too (see the Ticket 095
paragraph below). Compare them with each other, not with the table.

Calling the shared core (Ticket 081) adds no measurable cost. Measured on
2026-11-18 the same way, base then branch, in two rounds, with a 245 KB
transcript whose current turn holds 300 calls:

| Case | Before | After |
| --- | --- | --- |
| In process (`run_hook`), 150 runs: `PreToolUse` of an `Edit` | 20.0, 20.5 ms | 19.2, 18.9 ms |
| The same, `PreToolUse` of a `Bash` command | 9.3, 9.3 ms | 9.7, 9.2 ms |
| The same, `Stop` | 12.8, 12.5 ms | 12.7, 12.6 ms |
| Spawned in exec form, 30 runs: `PreToolUse` of an `Edit` | 200, 191 ms | 198, 188 ms |
| The same, `Stop` | 198, 191 ms | 187, 186 ms |
| The same, `UserPromptSubmit` | 164, 165 ms | 169, 160 ms |

The core's own command, `adapters/core/goated_judge.py`, judging an edit in
a 38 KB request with a 300-call turn, took a median of 174 ms over 30 runs,
against 41 ms for the interpreter alone.

Writing the [usage log](../README.md#the-usage-log) (Ticket 082) adds 2 to 4
ms a hook in process. Measured on 2026-11-18 on the same machine with the
uv-managed Python 3.14, in process through `run_hook`, a 300-call current
turn, 150 runs each after a first that logs the turn, log off then on, in
two rounds:

| Case | Log off | Log on |
| --- | --- | --- |
| `PreToolUse` of an `Edit` | 12.7, 12.6 ms | 15.3, 15.3 ms |
| `PreToolUse` of a `Bash` command | 10.1, 9.9 ms | 12.5, 12.1 ms |
| `Stop` | 10.0, 9.8 ms | 13.5, 13.0 ms |
| `UserPromptSubmit` | 2.0, 1.9 ms | 5.9, 5.4 ms |

The cost is the cursor's and the log's locks, two small file writes, and
reading the cursor. A prompt after a turn the log saw end costs that alone;
after a turn that ended any other way, such as one you interrupted, the
prompt hook also reads the last turn again for the facts no event logged,
about 5 ms more on this turn. The spawned, exec-form cost was not measured.

The `pr-review` gate's size check (see [Large pull requests](#large-pull-requests))
runs only on a pull-request call that no load or skip line has cleared of
`pr-review`, judged together with the `pull-request` gate. Measured on 2026-11-16
on the same machine with git 2.55, in-process through `run_hook`, 30 runs each:

| Case | Median | p90 |
| --- | --- | --- |
| No checkout at the hook's folder | 3 ms | 3 ms |
| `gh pr create --base main`, 450 changed lines (two git calls) | 34 ms | 36 ms |
| `gh pr create --fill`, 450 changed lines (two git calls) | 35 ms | 39 ms |
| The same, 20,000 changed lines | 40 ms | 44 ms |
| An MCP tool naming `owner` and `repo`, 450 changed lines (three git calls) | 62 ms | 75 ms |

So a pull request's hook call costs about 35 ms more, about 60 ms for an MCP
tool that names its repository, and at most two seconds when git hangs.

The closeout's [large-branch](#large-branches) measure (Ticket 069, five git
calls) runs at a commit or `Stop` in a turn that changed code, while the
Review or Verification item is not otherwise met. Measured on 2026-11-17 the
same way, a `Stop` with only that measure left to run:

| Case | Median | p90 |
| --- | --- | --- |
| No checkout at the hook's folder | 4 ms | 5 ms |
| A branch of 450 changed lines | 58 ms | 61 ms |
| A branch of 20,000 changed lines | 58 ms | 63 ms |

Every other call costs nothing more.

Judging every gate (Ticket 095) adds no measurable cost: on 2026-11-17, on
the same machine with the uv-managed Python 3.14, whose start-up is slower,
30 runs each in exec form, a test edit that meets three gates took a median
of 165 ms before and after the change, and a passing `ls` 156 and 158 ms.
Each gate still asks git or reads a subagent's transcript only when its own
hold would otherwise fire.

The [early closeout note](#early-closeout-note) (Ticket 096) adds one hook
process after each file edit tool call, and none after any other call. On
2026-11-17, the same way, with a 16 KB transcript:

| Case | Median | p90 |
| --- | --- | --- |
| `PreToolUse`, an edit, for comparison | 165 ms | 182 ms |
| `PostToolUse`, the turn's first code edit, adding the note | 160 ms | 167 ms |
| `PostToolUse`, a later code edit, the note already given | 161 ms | 165 ms |
| `PostToolUse`, a docs edit | 160 ms | 164 ms |

So an edit costs one more hook run, about as long as its `PreToolUse`; the
note never asks git or reads a subagent's transcript.

The hook never waits for the call it judges, which it takes from its input:
in an interactive session (Claude Code 2.1.325) the assistant message holding
the call is recorded only after `PreToolUse` returns, and in headless runs it
appeared 54 to 114 ms after the hook started. The only wait is for the entry
of the call's prompt, which is normally already there.

## Known Limits

- The [early closeout note](#early-closeout-note) comes only after a file
  edit tool's change. A turn that changes code only by shell commands gets
  no note, meets its items at `Stop`, and may still report twice; the
  closeout judges its changes as before. The note also leaves out the Review
  item, a large branch's Verification, and items a spawned subagent's work
  brings, so the closeout may still ask for one of those. The note comes
  once per turn: a turn a subagent's report reopens (see
  [Subagents](#subagents)) gets no second note.
- The hook may see nothing of the assistant message that makes the call it
  judges. In an interactive session Claude Code records that message only
  after the hook returns, so a route line or skip line in the message's text
  may not count yet. Calls of one message are another matter: a carrier
  probe (`docs/reference/carrier-probe-2026-11-19.md`, one run per shape on
  Claude Code 2.1.325) found that Claude Code judges a message's writes, and
  commands that write, one at a time in message order, each with the calls
  before it already in the transcript, while it judges read-only calls all
  at once. So a line on a call earlier in the same message, such as a Bash
  call's description, may count for a later write in it; the holds say it
  may, never that it will, since the order is the harness's behavior, not a
  documented promise. Read-only calls of one message see none of each
  other. When
  the hook input has no `tool_use_id`, the judged call is taken to be the
  newest recorded call without a result if its name and input match, so its
  line is counted once.
- Claude Code can store the text of an assistant message that also makes a
  tool call as a rewritten summary, in a thinking block, that drops route and
  skip lines, so the adapter never sees a line written there, and a retry
  cannot bring it back. The holds a line can clear therefore point to the
  call fields the adapter also reads (see [What It Holds](#what-it-holds)).
  Edit and Write calls have no `description`, so a line for one of them goes
  in a call made earlier in the same message or in an earlier message of the
  turn, such as a Bash call with the command `true` or the Skill call that
  loads a required skill. If the line is still not seen, the holds
  point the user to the typed override: `skip routing`, or `skip <skill>` for a skip line.
- A brief's route line is recognized only in the shape current desktop-app
  builds record (see [What It Holds](#what-it-holds)). Older builds recorded
  a brief with `turnOrigin` `sdk`; such a brief, one passed to `claude -p`,
  or one in any other shape is a prompt like any other, so its session loads
  the router and writes its own route line. After a compaction
  the brief is gone, but its task stays. A task, which lets a typed
  prompt's turn run as `goated-route: continue`, is known only once the
  hook has read the turn whose route line started it: at a call judged in
  it or at its Stop. A session that types its next prompt before either
  happens is held as if it had no task, so it loads the router and writes
  a route line. Harness
  nudges such as "The user hasn't heard from you in a while" are recorded as
  `attachment` entries and never open a turn.
- A briefed session's orientation counts any three distinct files read whole
  with the Read tool or printed whole by a shell command, whatever they are,
  or five distinct files inside the project read or printed whole or in part;
  the adapter cannot tell whether they are the sources the brief names, nor
  whether Claude Code cut a long print short. Two spellings of one path count
  once when they differ by `./`, `..`, or, on Windows, case or separators;
  a relative printed path is taken from the session's folder, not from one a
  `cd` in an earlier command left the shell in.

- Shell analysis is lexical, not a shell. These forms are not seen, so a
  write in them meets only `router-first` and a commit or pull request in
  them meets no action gate:
  - a command run through another shell or evaluator: `bash -c`, `sh -c`,
    `eval`, `Invoke-Expression`, `Start-Process`, or a heredoc fed to a shell
    (`bash <<'EOF'`); only whether a `bash -c`, `sh -c`, `zsh -c`, or
    `pwsh -Command` line is a check is read;
  - command substitution with backticks, or `$(…)` inside double quotes;
  - a write by a script file run by name (`node build.js`,
    `python tools/gen.py`) or fed from a file (`node < build.js`,
    `cat gen.py | python -`), or by an archive tool (`tar -x`, `unzip`);
  - a write by [inline code](#inline-scripts) through a call its table does
    not list: another program (`subprocess`, `child_process`, `system`), a
    library's own writer (`json.dump` to a path, `pandas` `to_csv`,
    `Pathname#write`), a dynamic call (`getattr`, `eval`), or a name
    renamed other than by an import it reads (`w = fs.writeFileSync`,
    `p = os.remove`, `import fs from 'fs'` then `fs.default.rm`); by an
    interpreter the adapter does not read (`php -r`, `pypy`); or by code
    piped in from a program other than the text producers it reads;
  - a path name rebound in some way the reading's lexical rules miss, or a
    literal path made to mean another file by an `os.chdir` before the
    write, so the file judged is not the one written; a name passed on to
    another (`q = p`), joined (`os.path.join`), or formatted is not
    followed, and stays unnamed;
  - git aliases (`git ci`), and `gh api` calls that create a pull request
    (`gh api repos/<owner>/<repo>/pulls`);
  - MCP tools that commit or open pull requests under names other than those
    listed in [What It Holds](#what-it-holds).

  An agent working around the holds this way is the case the next item
  describes.
- A [plain read](#plain-reads) can still run a program that git config
  names, such as `core.fsmonitor` under `git status`, or `diff.external` and
  a `textconv` driver set for the repository, which a plain `git diff`,
  `git show`, `git log -p`, or `git blame` runs too, or a pager such as
  `core.pager` under `git branch` or `git log`. Refusing the `--ext-diff`
  and `--textconv` options does not stop them. A `cd` before a read moves
  it into another repository, whose config then applies, as `git -C` does.
  A passing read can also hang:
  `tail -f` never ends on its own.
- A shell call's result stands for the whole command, not for each command
  in it. A check in the same command as a write proves that write even when
  the command hid the check's failure (`pytest || true`, `pytest; echo done`,
  `pytest | tail`), and the Unfinished item does not see that failure either.
  A write in a subshell (`(cp a.py src/a.py) && pytest`) is not proved by a
  check after the group.
- Two closeout triggers are mechanical stand-ins for judgement. "Behavior or
  interfaces changed" is read as "a non-test code file changed", so a pure
  refactor still asks for `doc-sync` or a skip line. "Work left unfinished" is
  read as "the last check after the change failed"; unfinished work with no
  failing check is not seen.
- The closeout holds the `Stop` even when Claude Code reports that a `Stop`
  hook already blocked once (`stop_hook_active`), because a hold never passes
  on a retry. Each item accepts a skip line, so the agent can always end the
  turn by writing one. The reply being finished is read from the hook input's
  `last_assistant_message`; on a Claude Code version without that field, a
  skip line written only in the final reply may not be seen until the
  transcript catches up.
- Whether a file is inside the project is read from paths, not from a shell
  or the disk's full layout, so the adapter counts a file as outside only when
  it is certain, and every limit here fails toward holding:
  - Git Bash mounts other than `/tmp` (`/` is the Git install folder, and
    any mount you add) are not read, so on Windows a path rooted with no
    drive letter, other than Git Bash's `/c/` drive form and `/tmp`, counts
    as inside the project. `/tmp` is read through `TMP` and `TEMP` as the
    hook sees them, which assumes Git Bash's default `/tmp` mount; a changed
    `/etc/fstab`, or a shell whose `TMP` differs from the hook's, is not seen.
  - `CDPATH` is not read, so a `cd` to a bare relative name makes the folder
    unknown, and the writes after it count as inside.
  - A `cd` is read as bash's default logical `cd -L`: each `..` drops the
    name before it from the text, so `cd /tmp/../c/proj` is in `/c/proj`.
    (`cd -P`, like any `cd` with an option, leaves the folder unknown.) A file
    path with `..` outside a `cd`, such as `> /tmp/../x`, is read physically,
    as the system opens it.
  - A .NET write in a PowerShell script counts when a shell command writes
    the script (a redirect or `tee`), not when the `Write` or `Edit` tool
    does, nor when a script holding it is copied or renamed into place.
  - .NET write text a `Bash` command writes to a file that is not a script,
    and a later call runs, is not seen: for example a later
    `Get-Content x.txt | iex` in the `PowerShell` tool, or Bash
    `pwsh -Command (Get-Content /tmp/x.txt)`. Only the command that writes
    the text is read, and it names no PowerShell.
  - `~` is read both as your profile folder and as `HOME` when that is set
    (Git Bash may point it elsewhere); a `~/...` path inside the project under
    either reading counts as inside. A shell's `HOME` that differs from the
    one Claude Code passes to hooks is not seen.
- The design gate judges size by lines added in the tool input, not by what
  the change does. Of shell writes, the design gates see only those that put
  new text into a file (see [Shell writes](#shell-writes)): a copy, move,
  restore, or `sed -i` of code is not judged, nor is a write naming no file
  (`git apply`), and `printf`'s `\n` escapes are not counted as lines. A
  write from a folder the command leaves unknown has no place, so after a
  bare relative `cd src && cat > export.py <<EOF` the design gates do not
  judge it (see the `cd` rules under [Shell writes](#shell-writes));
  `cd ./src` is followed, and its write is judged.
  The design-reads signals are word and shape matches on lines, so a `try` in
  a string selects `errors.md`, and a `NotebookEdit` cell counts all its text
  as added. A `Write`'s file on disk, read to tell what it adds, is the one
  design input outside the transcript. The adapter cannot tell a reference
  read and applied from one read alone, and nothing checks that the agent
  connected a reference to its change.
- The design-reads gate holds only while `software-design-principles`
  counts as loaded: in a session that has not loaded it since the last
  compaction, a turn whose edits are all small is held for no reference at
  all. Inside a subagent, only the subagent's current turn counts: a load or
  reference read in an earlier turn of a continued subagent is required
  again, and the parent's never count for it, nor its for the parent.
- An edit whose added lines cannot be counted, such as one whose new text
  is missing, is not small: the `design` gate treats it as substantial, and
  in a later turn it brings the closeout's Design items.
- A compaction boundary in the transcript drops earlier loads and reads even
  when its `SessionStart` reset never landed, for example after a hook that
  failed open or an adapter installed mid-session.
- A load counts until the next compaction however many turns ago it was,
  when the agent may no longer follow the skill closely. The checks tied to
  a change (change reads, the red-flags read, Proof) still count only in
  their turn. A turn is folded into the state by the hooks that run in it;
  Claude Code runs `Stop` at the end of every turn, so a turn of loads alone
  still counts. If the state file is lost, a load from an earlier turn is
  asked for again. The security gate judges by
  path alone. The conflict-resolution gate reads git's English messages
  (`Automatic merge failed`, `could not apply`, `could not revert`), so a git
  set to another language is not seen.
- The red-flags reread rule counts the lines an edit tool call writes, so
  fixes made by shell writes or a subagent always ask for the red-flags read
  again, and five small fixes spread over a turn ask for it as one six-line
  fix would.
- A [whole read](#whole-reads) is judged by the `Read` call's input alone: a
  `Read` with no range counts as whole even when the tool cuts a long file
  short, and partial reads that together cover a file still do not count.
- The `review-intake` gate sees only the turn a reviewer reported in. When
  the review reports, the turn ends to ask the user, and the fixes come in
  the next turn, those fixes are not held. A subagent's own edits are never
  held, since only the main agent records which brief each spawn followed.
- The `reference-reads` gate fails open: with no registry at its path (see
  [Install](#install)), or one it cannot read or parse, it asks for nothing,
  with a warning unless the default registry is simply missing. Its reader
  takes the registry's plain block YAML only. A block scalar (`|`), an
  anchor, a flow mapping, a plain value wrapped onto more lines, a sequence
  not indented under its key, or a key with no value makes the whole
  registry unreadable to it. It takes only `true` and `false` as booleans,
  and reads `True`, `yes`, `on`, `null`, `~`, and `-1` as strings, and a
  quoted value without its escapes. `validate_skills.py`
  fails when this reader and a full YAML parser read the source registry's
  references differently, so such a mismatch is refused and a registry edit
  cannot switch the gate off unnoticed; it also fails when more than one
  reference has an `edit-of-file-kind` signal for `test` files, since the
  design gate reads only one. An installed registry edited by hand is not
  checked. A
  signal value of the wrong type, such as a list for `pattern`, makes the
  registry unreadable too. A signal naming a
  pattern or file kind the adapter does not list asks for nothing. A shell
  write meets only the signals that need no added text (`write-under-path`,
  `gate-fires`, `sensitive-category-count`): the edit kinds read the code a
  write adds, which only a write tool's input shows. A file is created only
  by a write tool's `Write`, or `Edit` with no old text, to a path not on
  disk, so a test file a shell command made earlier in the turn, such as
  `touch tests/test_x.py`, is on disk, and a short `Write` over it asks
  neither gate for `coding.md` or `test-design.md`. It does not run inside a
  [subagent](#subagents). Its patterns match words by their letters, so a word
  that only starts like one, such as `patches` or `spyglass`, or one in a
  string, still selects the reference; the read counts until the next
  compaction, which bounds the cost.
- A restore command, such as `git checkout -- <file>` or `git restore`,
  counts as a change whatever it restores, even content identical to what
  the last check ran on, since the adapter reads commands, not file content.
  So the Proof item asks for a check after it; a rerun of the check, or a
  `goated-skip: verification-before-completion: <reason>` line, answers it.
- The adapter guards against agents skipping skills, not against an agent
  working to defeat it. An agent with shell access could edit the transcript,
  the state file, or the settings that install the hooks. Defending against
  that is out of scope; review what agents change if it matters to you.
- Prompt classification relies on transcript fields and text wrappers seen in
  Claude Code 2.1.3xx (`origin`, `turnOrigin`, `<task-notification>`,
  `Another Claude session sent a message:`, and others). A new kind of
  machine-written prompt with no `origin` and an unknown wrapper would be
  treated as typed. A new wrapper alone, on a prompt the transcript marks with
  a non-person origin, still applies no override, but the user-prompt hook
  would announce one. A subagent's report continues the turn only in the shape
  Subagents describes; a new shape, or a report whose spawn lies before a
  compaction or beyond the read limit, opens a turn, as any machine-written
  prompt does. Until it finds the spawn, the reader goes on reading back for
  it, so a report naming an agent this session never spawned makes each hook
  call of the turns it opens read back to the last compaction or the read
  limit.
- Shared-policy detection looks for the policy's title in the instruction
  files Claude Code reads and in their one-level `@` imports. It does not model
  the setting under which a `CLAUDE.md` stops `AGENTS.md` from loading, it
  stops its parent-folder walk at your home folder, and it opens imports only
  inside the project, your home folder, or the importing file's folder, never
  on a network (UNC) path.
- Hooks for parallel tool calls can race on the state file. Each call
  re-derives its turn from the transcript, so a lost update can cause a repeat
  hold, never a pass. The turn markers that share the full unseen-line advice
  and each ask's full text are claimed atomically, apart from the state
  file, so this race never repeats either.
- The Verification item's sensitive-file trigger uses the `security` gate's
  paths, so any change to one, such as an edit of a lockfile or a `.env`
  value, asks for `verification-before-completion` too; its skip line
  answers it.
- The [large-branch](#large-branches) measure counts every untracked code
  file outside test paths that git does not ignore, so an unignored folder of
  generated or vendored code makes a small branch large; its skip line, or a
  `.gitignore` entry, answers that. A branch large only in tests, fixtures,
  docs, or configuration meets no Review item. Test paths are judged from the
  top of the checkout, so in a project below that top a top-level `spec/`
  folder of the project is not a test path.
- A plain `pip install` or `conda install` is judged by the folder it runs
  in, but it installs into the active environment, which may be the
  project's virtual environment though the command ran elsewhere; such an
  install from a scratch folder raises no Setup item.
- A session started from a brief meets no Review item, trusting the
  starting session to review: a brief sent with no review planned leaves a
  large branch unreviewed. Only a brief the adapter recognizes, with a route
  line (see [What It Holds](#what-it-holds)), marks the session.
- The Proof and Verification items name the same skill, so the skill-usage
  mod counts a `verification-before-completion` load as answering both items
  of a hold that lists both, though only Verification asks for the load.

## Measuring It

The optional [skill-usage mod](skill-usage/README.md) in `skill-usage/` shows
the adapter's holds and their outcomes, your overrides, route and skip lines,
reference reads, and subagent activity in a pane beside the chat. It installs
and uninstalls on its own, displays only, and the adapter works the same
without it.

## Tests

`tests/test_claude_code_adapter.py` (routing gates) and
`tests/test_claude_code_adapter_actions.py` (action, shell-write, and closeout
gates) in the GOATED source repo drive the adapter with hook inputs and transcripts in Claude Code's recorded shape,
including the recorded fixtures in `tests/fixtures/claude_code_adapter/`, and
checks the adapter's marker parser against `stack/fixtures/markers/lines.yaml`.
`tests/test_claude_code_adapter_review.py` covers the closeout's Review and
Verification items against scratch git repositories.
`tests/test_claude_code_adapter_closeout_note.py` covers the early closeout
note.
`tests/test_claude_code_adapter_rule_purity.py` fails when a core module
names Claude Code or imports more than the standard library and the core
(see [What It Holds](#what-it-holds)),
`tests/test_claude_code_adapter_translation_parity.py` pins the behaviour the
translation layer must keep (Ticket 080), and
`tests/test_claude_code_adapter_saved_state.py` pins that state saved before
the core reads as before (Ticket 081).
`tests/test_enforcement_scenarios.py` runs the conformance scenarios through
this adapter's hooks, and `tests/test_enforcement_core.py` runs them through
the core's two ways in.
