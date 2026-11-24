# GOATED Enforcement Contract

This file states, in words that name no harness, every rule a GOATED
enforcement adapter enforces. Under
[ADR 0003](../docs/adr/0003-opt-in-framework-enforcement-adapters.md) an
adapter enforces portable contracts and never defines them; under
[ADR 0004](../docs/adr/0004-portable-enforcement-core.md) the rules live in
one shared core behind the
[event model](schemas/enforcement-event-model.schema.json), and this file is
what that core enforces.

Each gate enforces a rule that a skill, the shared policy, or the registry
owns. This file cites that owner and does not restate its procedure. What
this file owns is how a rule is judged from events: what is held, what
clears it, and how a hold is shown.

A rule change updates this file and a conformance scenario under
[`fixtures/enforcement/`](fixtures/enforcement/README.md) in the same change.
A test fails when a gate an adapter can return is missing from the
[Gates](#gates) table.

## Contents

- [Terms](#terms)
- [Lines](#lines)
- [Holds](#holds)
- [Gates](#gates)
- [Closeout Items](#closeout-items)
- [Hold Messages](#hold-messages)
- [Overrides](#overrides)
- [Prompts, Turns, And Tasks](#prompts-turns-and-tasks)
- [Subagents](#subagents)
- [Notices](#notices)
- [Failing Open](#failing-open)
- [What An Adapter May Leave Out](#what-an-adapter-may-leave-out)
- [Calling The Core](#calling-the-core)
- [Detection Detail](#detection-detail)

## Terms

The event model's names are used throughout: call kinds, turns, entries,
prompts and their authors, and the project.

The event model is at version 5. Every change to it bumps the version
(ADR 0004), so a request of version 1, 2, 3, or 4 is refused. Version 5
(Ticket 119) added the `route_continued` notice kind and the project's
`context_docs`, version 4
(Ticket 114) the `reads_owed` notice kind, and version 3 (Ticket
101) the `skip_carried` notice kind (see [Notices](#notices)). Version 2 (Ticket 080) added
what the rules read and version 1 could not carry: a pull request's `base`,
`head`, and `repository`, for its size; an edit's `removed` or `added` text
as null when the call does not show it, such as a whole-file write's or a
notebook cell's; a write's `creates`, for an edit that makes a missing file;
a spawn's `separate`, for an agent whose report never comes back as the
call's result; a call's `action`, an opaque key that keeps calls the model
shows alike apart where repeated actions are counted; a `call_finished`
entry, so a call's lines count where it was made while calls still finish in
order; and a result's `ran`, false for a call that never ran for a reason
other than a hold, which no check counts.

- **Write**: a `file_write` call, or a `shell_command` that writes files.
  **Spawn**: a `spawn` call that starts work now (`starts_now`), or that
  carries a brief a person may start later. **Command**: any
  `shell_command`. Every other call is never held.
- **Code file**: a file with a programming-language extension. Docs and
  configuration are not code. **Test file**: a code file under a `tests`,
  `test`, or `__tests__` folder at any depth inside the project, or a
  top-level `spec` folder, or named `test_*`, `*_test.*`, `*_spec.*`,
  `*.test.*`, or `*.spec.*`. A file whose place in the project is unknown is
  not a test file. **Test data**: a test file, or any file under a
  `fixtures` or `__fixtures__` folder at any depth inside the project. A
  configuration file that is test data is not judged by `design` or
  `design-reads`; a code file under a fixtures folder is still code.
- **Inside the project**: under any of `project.folders` or the nearest
  checkout above one. A file is outside only when that is certain; in doubt,
  it is inside. A **scratch file** is outside the project, inside no
  checkout, outside `project.agent_folders`, and not a folder holding the
  project.
- **Change**: a write to a file inside the project, or by a subagent this
  turn spawned. A shell write whose files cannot be named counts as a change
  to non-test code.
- **Check**: a test runner, linter, type checker, or build command, or a
  script whose name says test, check, lint, verify, validate, or build. Inline
  interpreter code is not a check, nor is a shell call run in the background
  (see [Checks](#checks)).
- **Counts as loaded**: a finished, successful `skill_load` of the skill, or
  a `skill_invoked` entry, since the last compaction. A load counts by its
  bare name, or under a namespace the user configured. Naming a skill in text
  is not a load.
- **Whole read**: a finished, successful `file_read` with `whole` true. A
  read asked for by a hold counts until the next compaction; partial reads
  never add up to a whole one.
- **Whole print**: a finished, successful `shell_command`, not run in the
  background, that prints a file whole to the agent, as
  [Whole Prints](#whole-prints) reads it. Only orientation, in the
  `pipeline` row, counts one as a whole read of that file; every other rule
  that asks for a whole read asks for a `file_read`.
- **File print**: the same, for a command that prints a file whole or in
  part, as [File Prints](#file-prints) reads it. Only orientation's five
  distinct files count one.
- **Change read**: a finished call after the last change a step covers that
  puts the change in front of the agent: a command that prints the diff's
  content, or a read of a file the turn changed. A listing of names or
  counts does not count, nor does a read chained in the held command or made
  in parallel with the held call.

## Lines

The route line, the skip line and the skills line are defined by their
owners: the route line by the `using-goated-ai-skills` router's output
contract, the skip line by the shared policy (`stack/AGENTS.md`), and the
skills line by `handoff`'s `references/spawn-brief.md`. Their grammar is
[`fixtures/markers/README.md`](fixtures/markers/README.md).

Where a line counts:

- in a `reply_text` entry, or in a call's `line_text`, which an adapter fills
  when its harness may not keep reply text whole. A line in a call counts
  from that call on, so it covers the call itself. No other field counts:
  file text, edit text, and commands never carry a line;
- in the session's first prompt, when it starts the session
  (`starts_session`): its last route line is the first turn's route, until a
  prompt a person wrote opens a turn;
- only in its own turn, and only for the agent that wrote it;
- outside fenced blocks, as a whole line. The last route line wins.

A harness may judge the calls of one message one at a time, in order, each
with the calls before it already recorded; Claude Code did so for writes,
and commands that write, in one probe run per shape
(`docs/reference/carrier-probe-2026-11-19.md`), while it judged read-only
calls all at once. There a line in an earlier call's `line_text` counts for
a later write of the same message, since it counts from its call on. This is
no new rule: hold text says a route or skip line may ride on a call earlier
in the same message when the held call is a write, or in an earlier
message, and never promises that it will (round 6, R11).

No line is ever read from a prompt, so a line quoted in a prompt counts for
nothing, and no override is ever read from a call or a reply.

## Holds

There are two kinds of hold:

- **strict**: clears only on proof of use or a person's override;
- **justified-skip**: also clears on a skip line naming its skill with a
  reason of three or more words, in the current turn.

Every hold follows these rules:

- **No free retry.** A hold is decided from the events, so repeating a held
  call unchanged gives the same answer until the proof, line, or override
  appears. A held call is recorded as held, and never counts as a change, a
  check, or a read.
- **Every hold at once.** A call is judged by every gate, and one decision
  carries every hold it meets, in firing order: the routing gates
  (`router-first` and `route-line` together, then `pipeline`), then the
  action gates for the call's kind:
  - a file write: `conflict-resolution`, `security`, `review-intake`,
    `design` or `design-reads`, `reference-reads`, `repeated-failure`;
  - a shell command: `conflict-resolution`, `commit`, the closeout at a
    commit, `pull-request`, `pr-review`, `security`, `review-intake`,
    `scripted-edit`, `design` or `design-reads`, `reference-reads`,
    `repeated-failure`;
  - a `commit` call: `commit`, then the closeout; a `pull_request` call:
    `pull-request`, `pr-review`; a spawn: `spawn`.

  `pipeline` is judged once the router counts as loaded and the turn has a
  route line, so it may follow on the retry. A held commit names every
  unmet ask it has at once: the `commit` hold names each of the
  `commit-message` load, the message's content check, and the change read
  still unmet, and the closeout hold beside it names each unmet item (the
  maintainer's choice V1, 2026-11-19, reversing Ticket 095's "may follow on
  the retry"). The [Gates](#gates) table lists gates by subject, not in this
  order.
- **Loads count until the next compaction**, in this turn or a later one, as
  do the reads a hold asks for. Route and skip lines, overrides, change
  reads, the red-flags read after the last change, and proof by a check
  count only in their turn, but for a lasting skip.
- **A lasting skip.** Some skip lines last until the task ends or the next
  compaction: one that clears a `reference-reads` hold, or a `design-reads`
  or `design` hold while `software-design-principles` counts as loaded,
  when both ask only for reads. The same goes for a skip line that would
  clear the hold a write meets, and one that meets the Reads closeout item,
  for the gate whose reads the landed write owes. It lasts for each reference that hold names
  and the same kind of file: a test file, a configuration file, another
  code file, or another file. The two design gates share one set of lasting
  skips, so a skip from `design-reads` covers the reads of a later turn's
  first code change. A write naming no project file gets no lasting skip.
  A later hold of the same gate that asks only for references a lasting
  skip covers, on a file of the same kind, passes. When no other gate
  holds the call, it carries a `skip_carried` notice naming the skip, once
  per task for each gate, skill, and kind of file (see [Notices](#notices)). A
  hold that asks for another reference holds for that reference alone. A
  new task (a route line that is not `continue`) and a compaction end every
  lasting skip. Only the main agent keeps lasting skips: a subagent's skip
  lines last its turn. Every other skip line lasts its turn too, including
  one that clears a `design` hold asking for the load or one that clears a
  closeout item other than Reads, and so does a person's override.
- **A file edit lands and reads after.** A file edit tool's write that
  `design-reads` or `reference-reads` would hold is not held by that gate,
  at any size: the read follows the edit instead of refusing it, so a
  read gate no longer leaves a batch of edits sent in one message
  half-applied (round 6, decision S,
  [Ticket 118](../tickets/archive/118-core-design-reads-never-refuse-an-edit.md)).
  One edit of a batch can still be held, by an edit that does not show its
  text, `design` waiting for the skill's load, a subagent's edits, or
  another gate. So is one that `design` would hold once `software-design-principles`
  counts as loaded, when it asks only for reads (the maintainer's choice,
  2026-11-19). An edit that does not show the text it adds is held. A
  shell write differs: it lands only when it adds thirty or more lines,
  since resending it costs more than revising it (round 5, R5), and a
  shorter one is held as before. Its lines are counted as the gate counts
  them: the lines of text the command shows it writes into the files the
  gate judges, and lines it writes anywhere else, such as a scratch file,
  do not count. A shell write whose lines cannot be counted (one that
  names no judged file, writes a file it does not name, writes text it
  does not show into a judged file, or changes one without new text, such
  as a copy) counts as fewer and is held. The turn's
  [Reads](#closeout-items) item asks for what a landed write owes. When no
  other gate holds the call, it carries one `reads_owed` notice naming
  each reference it owes that no earlier write of the turn that landed
  already owes: the turn's first such write names them all, a later one
  only those it adds, and one that adds none carries no notice (round 6,
  R1). A write that failed or was refused owes nothing. A reference read
  whole since the last compaction is never owed.
  A `design` hold asking for the skill's load never lets a write land,
  and a subagent's write is held as before: a subagent's turn end is
  never held and it keeps no state, so what its write owed would never be
  collected. A call with no `id` is held too, since the closeout finds a
  landed write by its id.
- **A skip line never clears a strict hold.** To drop a skill a route
  requires, write a corrected route line without it.
- **Scratch writes.** `router-first`, `route-line`, and `pipeline` let a
  write through when every file it writes is a scratch file. A shell command
  passes only when every part of it is a plain read, a folder change, or a
  command that only writes, copies, moves, or removes the files it names.

## Gates

Clear ways: `proof` is the gate's own proof of use, in the Clears column;
`skip-line` is a skip line naming the gate's skill; `override` is a person's
override (see [Overrides](#overrides)); `route-line` is a route line in the
turn, or a corrected one that drops the requirement; `brief-route` is a
route line in the brief that started the session, or, in the task it
started and with no compaction since, a `goated-route: continue` line;
`task-route` is, in a turn a person's prompt opened in a routed task an
earlier turn started (see [Prompts, Turns, And Tasks](#prompts-turns-and-tasks)),
the turn's route being `goated-route: continue`, by its line or by having
none; `lasting-skip` is a skip
line from an earlier turn of the task that cleared the same gate (the two
design gates count as one) for the same references on the same kind of
file (see [Holds](#holds)).

| Gate | Kind | Holds | Clears | Clear ways | Enforces |
| --- | --- | --- | --- | --- | --- |
| `router-first` | strict | A write, spawn, or command while the router does not count as loaded; a command made only of plain reads passes | The router counts as loaded; or, until a person's prompt opens a turn, the session's first prompt is a brief with a route line; or, in the task that brief's turn started and with no compaction since, the turn's route line is `goated-route: continue`, whoever's prompt opened it; or, in a turn a person's prompt opened in a routed task an earlier turn started, compacted or not, the turn's route is `goated-route: continue`, by a line or by having no route line (see [Prompts, Turns, And Tasks](#prompts-turns-and-tasks)) | `proof`, `brief-route`, `task-route`, `override` | The router's "use at the start of each new task before the first edit or command" |
| `route-line` | strict | The first write or spawn after each prompt until the turn has a valid route line, except in a turn a person's or another session's prompt opened in a session with a task, which runs as `continue` (see [Prompts, Turns, And Tasks](#prompts-turns-and-tasks)); also `goated-route: continue` when no task is known | A valid route line in the turn | `route-line`, `override` | The router's output contract |
| `pipeline` | strict | A write or spawn while a `requires:` skill of the task does not count as loaded; in a session routed by its brief on a `standard` or `full` route, also while orientation is unmet and the orientation skill is installed; that hold names the project's context documents that exist (see [Calling The Core](#calling-the-core)). A spawn of a read-only agent passes | Each listed skill counts as loaded; orientation by its skill's load, by whole reads or whole prints of three distinct files, or by reads or prints, whole or in part, of five distinct project files, one file read and printed under two spellings counting once; a search that prints matching lines never counts (see [File Prints](#file-prints)) | `proof`, `route-line`, `override` | The router's route line ("must load before the first write") and the shared policy's corrected route line |
| `commit` | strict | A commit, by a git command (not a dry run) or a `commit` call | `commit-message` counts as loaded, an inline message passes the content check, and a [change read](#change-reads) follows the last change to code that is not a comment-only edit, or, in a turn with no such change, comes anywhere in the turn | `proof`, `override` | `commit-message` ("use before any Git commit") |
| `pull-request` | strict | Opening a pull or merge request, by a `gh` or `glab` command or a `pull_request` call | `pr-description` counts as loaded, and a change read follows the last change to any project file | `proof`, `override` | `pr-description` |
| `pr-review` | justified-skip | Opening a pull or merge request that changes 400 or more lines of non-test code against its base. It is judged together with `pull-request`, so both may hold the same call | `standards-and-spec-review` counts as loaded, and a change read follows the last change | `proof`, `skip-line`, `override` | `standards-and-spec-review`'s rule to review a branch of 400 or more changed lines in code outside test paths (`skills/engineering/standards-and-spec-review/SKILL.md`) |
| `spawn` | strict | A spawn with a brief, except of a read-only agent | `handoff` counts as loaded and its `references/spawn-brief.md` is read whole, or `subagent-driven-development` counts as loaded and its implementer or reviewer prompt is read whole; and the brief passes the content check | `proof`, `override` | `handoff` and `subagent-driven-development` |
| `design` | justified-skip | The turn's first file write adding five or more lines to a non-test code file inside the project, or any such file write while the skill does not count as loaded. A [comment-only edit](#comment-only-edits) adding fewer than twenty lines is small, so it is not such a write. A shell write counts only where it puts new text into a file: a redirect, heredoc, `tee`, `Set-Content`, `Add-Content`, `Out-File`, or `New-Item` with a value. It adds the lines of text the command shows, such as a heredoc's body, and five or more when it shows none, as for a program's output or text holding a variable, command substitution, or subexpression. Writes to two spellings of one file add up. A copy, move, restore, or in-place edit adds no text designed in the command, so it is not judged; a script's files are `scripted-edit`'s; and a write naming no file is not judged, since no file's design can be asked for (the maintainer's choice, [Ticket 098](../tickets/archive/098-adapter-contract-gaps.md)). Once the skill counts as loaded, a file edit that shows its text, or a shell write adding thirty or more counted lines, [lands and reads after](#holds) | `software-design-principles` counts as loaded, and every reference the edit's signals select is read whole or a lasting skip covers it | `proof`, `skip-line`, `lasting-skip`, `override` | `software-design-principles`, workflow steps 2 and 4 |
| `design-reads` | justified-skip | A later file write to a code file, or to a configuration file that is not test data, inside the project, once `software-design-principles` counts as loaded, whose signals select a reference not read whole since the last compaction. A shell write counts as for `design`; its text is not read for signals, so only its path selects (a configuration file, the third code file), and a test file it writes selects nothing. A comment-only edit adding fewer than twenty lines is small, so its comment selects no `readability.md`. A file edit that shows its text, or a shell write adding thirty or more counted lines, [lands and reads after](#holds) | Each selected reference is read whole, or a lasting skip covers it | `proof`, `skip-line`, `lasting-skip`, `override` | `software-design-principles`'s Read now lists |
| `reference-reads` | justified-skip | A write inside the project (or anywhere, for a `gate-fires` signal) that fires a signal the installed registry declares for a reference of a skill that counts as loaded. A named pattern matches as [Registry Reference Signals](#registry-reference-signals) states: `mock-or-patch` takes `patch` only as a call or decorator, `monkeypatch` only as a patch of code, and no word inside a quoted string the line shows for certain or a multi-line string the edit shows opening. A file edit that shows its text, or a shell write adding thirty or more counted lines, [lands and reads after](#holds) | Each named reference is read whole, or a lasting skip covers it | `proof`, `skip-line`, `lasting-skip`, `override` | The registry's `references` signals (`stack/goated-stack.yaml`, `skills/README.md`) |
| `review-intake` | justified-skip | A write to a code file inside the project once a reviewer agent has reported in the turn: an agent started now by a spawn whose brief followed `subagent-driven-development`'s reviewer template, whose result arrived or, started in the background, whose completion did. Any other brief, and a held or failed spawn, trigger nothing | `receiving-code-review` counts as loaded | `proof`, `skip-line`, `override` | `receiving-code-review` |
| `security` | justified-skip | A write to a security-sensitive path inside the project (test code meets no category a word in its name selects; see [Security-Sensitive Paths](#security-sensitive-paths)): dependency manifests and lockfiles, env and key files, files named for secrets, credentials, or tokens, auth and permission code (session code only beside an auth word), migrations and schemas, CI, container, and deployment files | `code-security-review` counts as loaded | `proof`, `skip-line`, `override` | `code-security-review` |
| `scripted-edit` | justified-skip | A shell command whose inline script writes a code file inside the project, or a file it names only at run time. It follows `security` and `review-intake` for the same file | A skip line naming `software-design-principles`; loading the skill does not clear it | `skip-line`, `override` | `software-design-principles`: change code with the file edit tools |
| `conflict-resolution` | justified-skip | A write while a merge conflict is open in the turn: an edit whose removed text has a conflict marker at a line start, a write to a file a read, a file printer, or `git diff` showed with one, or any write after a merge, rebase, cherry-pick, revert, or pull reported a conflict, until it finishes or is aborted | `resolving-merge-conflicts` counts as loaded | `proof`, `skip-line`, `override` | `resolving-merge-conflicts` |
| `repeated-failure` | justified-skip | A write once the same check has failed twice in a row in the turn. A run that only fails to load a missing module, the first run after a test file was written, a run with fewer failures than the one before, and a call that never ran (held, refused, or interrupted) neither add nor reset | `diagnose` counts as loaded | `proof`, `skip-line`, `override` | `diagnose` ("a check that keeps failing") |
| `closeout` | justified-skip | A commit, judged beside the `commit` gate, or the turn's end, in a turn that changed code or a security-sensitive file or setup, or landed a write owing reads, while a [closeout item](#closeout-items) is unmet | Every item is met or skipped | `proof`, `skip-line`, `override` | The shared policy's closeout and the skills each item names |

## Closeout Items

Each item is judged against the turn's last code change, but Reads, which
is judged against the writes that owe it. Code a subagent
changed counts at its spawn; if it ran a check after its own last change,
that change is already proved.

| Label | Needed when | Met by | Skip line names |
| --- | --- | --- | --- |
| `Reads` | A write of the turn [landed](#holds) past `design`, `design-reads`, or `reference-reads` before the references it needed were read. What a write owes ends with its turn, as the other items' evidence does | Each reference is read whole after the write, or a lasting skip or a person's skip covers it; then, for a write to a project file, a read of that file or a printed diff follows the last of those reads, and a read of another changed file does not count. It comes first, since revising the write may change what the other items judge | The skill whose references it asks for; the skip lasts as one clearing that gate would |
| `Proof` | A change not already proved. A [comment-only edit](#comment-only-edits), of any size, is already proved | A check after the last code change, in a later call or later in the same shell command, joined by sequencing operators, not in the background: neither sent there with `&` (`pytest &`, as its own call or inside a longer command) nor a shell call the harness runs in the background (its `background`), even one that writes the change itself; such a run's result is not read | `verification-before-completion` |
| `Unfinished` | The last check after the change failed | `handoff` counts as loaded | `handoff` |
| `Docs` | A non-test code file changed | `doc-sync` counts as loaded, and a change read follows the last code change; or, with no load, a documentation file (`.md`, `.mdx`, `.rst`, `.adoc`, or `.txt`, a dependency manifest aside; a `.txt` file counts only outside a [test path](#code-and-test-files) and when it is no build file such as `CMakeLists.txt`, so a golden output file does not) changed after the last code change and a change read follows the last such doc change (the maintainer's choice X1, 2026-11-19). A doc changed only before the last code change does not meet it | `doc-sync` |
| `Design` | `software-design-principles` loaded in the turn, or counts as loaded and the turn made an edit the `design` gate triggers on; in both, some code change in the turn is not a [comment-only edit](#comment-only-edits) adding fewer than twenty lines | `software-design-principles/references/red-flags.md` read whole after the last code change that is not comment-only, then a change read; later changes adding fewer than five lines in total need only the change read. Of those later changes, a line counts only when it is not blank and its text, indentation aside, is not a line of the text the edit replaces, so unchanged context sent with an edit adds none (round 6, R6); an edit that only moves existing lines therefore adds none, a gap the maintainer accepted. The changes the read scanned still count every line their edits add, context included, to reach five. The item repeats the question `red-flags.md` ends with; no answer is checked | `software-design-principles` |
| `Review` | The turn changed code, the session was not started from a brief with a route line or a skills line, and the branch's work is large: 400 or more changed lines of non-test code against its base | A reviewer agent that finished after the last code change; or `standards-and-spec-review` counts as loaded and a change read follows the last code change; or the task's [review point](#review-points) while the branch has grown by fewer than 50 lines since it | `standards-and-spec-review` |
| `Verification` | The turn changed code or a security-sensitive file, and the route is `full`, a spawned agent changed code, a security-sensitive file changed, or the branch's work is large | `verification-before-completion` counts as loaded. When only the branch's size asks for it: the skill loads in the turn, or the task's [verification point](#review-points) holds while the branch has grown by fewer than 50 lines since it | `verification-before-completion` |
| `Security` | `code-security-review` counts as loaded and a security-sensitive file changed | A change read after the last sensitive change | `code-security-review` |
| `Setup` | The turn installed or added a named package or tool, or wrote an env or settings file inside the project | `setup-scribe` counts as loaded, before or after the change | `setup-scribe` |

A session that cannot check yet because it waits on another session's
result, on the user, or on a check running in the background meets Proof
with the same skip line, giving what it waits for as the reason; the Proof
text names each wait, and asks for the check in the foreground. Comments
do not run, so a comment-only edit after the last check does not make
Proof needed, nor does a turn whose code changes are all comment-only; a
failed check before it still makes Unfinished needed. The same holds for a
subagent's comment-only edit after its own check.
A commit that ends a merge conflict, one made while a git conflict is open
in the turn or after an edit in the turn resolved one, as
[Conflicts](#conflicts) defines it, in a session where `resolving-merge-conflicts`
counts as loaded (a person's skip of it does not count), is not asked for
Docs, Design, Security, Review, or Verification. It still needs its change
read and the items about what the resolution itself did: Reads, Proof,
Unfinished, and Setup (the maintainer's choice X2, 2026-11-19). The same
commit without the load gets the full closeout, and so does the next
commit once that one has ended the conflict, and the turn's end.
The Setup item is not judged against code changes. A bare install that only
restores what a manifest records, or installs a local path, does not count.

### Review Points

**A review point** (round 7, R1, decisions D1, D6 and D7) is the
[branch size](#branch-size) at which a turn met or declined the Review item
by its own evidence: a reviewer agent, `standards-and-spec-review` with a
change read, or a Review skip line. A turn that changed no code, such as one
that only reviews the branch, records the point the same way, any change
read counting, though it is asked for no Review item. **A verification point** is the branch
size when a turn loads `verification-before-completion` or writes its skip
line, in any turn. Meeting an item again records a new point; a turn the
point itself meets records none. In a later turn of the same task, Review
is met while the branch has grown by fewer than 50 changed lines of
non-test code since its point (`REVIEW_POINT_GROWTH`), measured as the
difference of the two sizes; at 50 or more it is asked again. The
verification point counts the same way, but only when the branch's size is
the item's one trigger: a `full` route, a spawned agent's code change, or a
security-sensitive change asks in each turn as before, met by a load that
counts as loaded. With only size as its trigger, an earlier turn's load
counts only through its point. Both points are saved with the session's
facts, survive a compaction, and end when a route line starts a new task or
a clear ends the task. A size that cannot be measured records no point.
Saved state without points loads as a task with none. A known limit, from
the lead decision to measure growth by the size the item already uses:
rewriting lines already changed against the base, or checking out another
branch of about the same size, grows the size little or not at all, so it
does not ask again.

## Hold Messages

A hold's text is shown after its hold line:

```text
goated-hold: <gate> | <kind>
<what the agent must do, in plain words>
```

- The hold line matches
  `^goated-hold: ([a-z]+(?:-[a-z]+)*) \| (strict|justified-skip)$`, alone on
  its line. Measurement tools parse it, so it never changes.
- When a decision carries several holds, one message carries them all in
  firing order: the first as it would be alone, then, after a blank line,
  each further hold with its own hold line and text. When two or more of
  them can be cleared by a route or skip line, each keeps the line it asks
  for and every skill, reference and line it names, but drops its own
  advice on where the line goes; the last hold's text ends, on a line of
  its own, with one clearing section that says where a line goes and lists
  each hold's typed override once. A message with one such hold keeps that
  advice in the hold.
- Each hold's text opens with its clearing action, an imperative such as
  "Load", "Read", or "Write"; conditions and caveats follow (round 6, R11).
  A closeout item opens with its action after its `- <Label>: `, and a
  short form with its action after `Still unmet: <what is missing>.`; the
  hold line and the closeout's opening line stay as they are.
- A hold on a file write (`file_write`) ends, on a line of its own before
  anything the adapter adds, by saying that other calls of the same message
  may have landed, so the file is read before the edit is sent again.
- The text is guidance and may change between releases. It backticks each
  skill it asks for by its bare name, and no other bare word; a file is
  quoted by its path. In the `spawn` hold the two skills are alternatives;
  everywhere else each named skill is a separate requirement.
- The `spawn` hold that asks for `handoff` names every heading its spawn
  brief keeps, `Report Back` among them, and its skills line. The hold for a
  brief that lacks kept headings names, for each template read, each heading
  the brief still needs, as a `## <Heading>` Markdown heading.
- The closeout lists each unmet item on its own line, starting
  `- <Label>: `, with the labels of the [Closeout Items](#closeout-items)
  table. The labels are stable.
- A hold asks for a load only when the skill does not count as loaded. A
  hold that asks only for a change read once its skill has loaded names the
  skill without backticks, or only in its skip line.
- A hold that repeats an ask the turn already showed in full is short: it
  opens `Still unmet:` and keeps every skill, reference, and skip line the
  full text names.
- The core returns the rule text. The adapter adds what only its harness can
  say: where a line can be put so the harness keeps it, and which call can
  carry it.

## Overrides

Overrides come only from a prompt a person wrote (`author: person`), apply
only to the turn that prompt opened, and stop at that turn's end
(`turn_ended`). Matching ignores case and the prompt's `pasted` text. A
phrase negated just before it, such as "don't skip routing", is not an
override.

| Phrase | Effect for the turn |
| --- | --- |
| `skip routing`, `skip the router` | Stands down `router-first`, `route-line`, and `pipeline` |
| `skip <skill>`, `skip the <skill> skill` | Stands down every requirement for that skill, in `pipeline`, an action gate, or a closeout item. `skip using-goated-ai-skills` also stands down `router-first`. `<skill>` must be an installed skill, or a registry skill when none can be found |
| `commit message: <text>`, `commit with the message "<text>"`, or a fenced block right after such a phrase | Stands down the `commit` hold for a commit whose inline message has the same subject line |

A recorded override brings an `override_recorded` notice.

## Prompts, Turns, And Tasks

- A prompt with `author: person` opens a turn and may carry overrides. A
  prompt from another session (`author: session`) opens a turn with no
  override. The turn another session's prompt opens in a session with a
  task, and the turn a person's prompt opens in a session with a routed
  task (see below), runs as `continue` until a route line in it says
  otherwise, so `route-line` does not hold it; its skip lines, checks, and
  change reads still start empty. A route-like line in that turn that
  fails the grammar ends the carried route: `route-line` holds, quoting
  it, until a valid line. A route line that starts a new task replaces the
  carried route, and its skills load through `pipeline`. In a session with
  no task, as the brief that starts a session, or, for a person's prompt,
  in a task that is not routed, either prompt meets `route-line` and
  `router-first` as today, and so does every prompt with `author: host` or
  `unknown` that opens a turn.
- **A person's follow-up** (decision T1 of round 6). A task is **routed**
  when a route line other than bare `continue` or a brief's route line
  started it, or when the turn whose bare `continue` line started it met
  `router-first` by the router's load or a person's override. In a turn a
  person's prompt opened, a route of `continue`, by a line or by having
  none, in a routed task an earlier turn started meets `route-line` and
  `router-first` without a router load (`task-route`), compaction or not.
  A bare `continue` line written without the router starts a task that
  carries no later prompt, so the next one is held as in a session with no
  task. The task's required skills are still asked for again after a
  compaction, by `pipeline`. The prompt gets a `route_continued` notice,
  once, saying that new work needs a new route line; the core judges it
  after folding the turns since the last one it saw, as the next judged
  call does, so a route line written after a turn's last judged call
  counts for both. Another session's message meets
  `router-first` as before: by the router, or, in the brief's task with no
  compaction since, by its own `goated-route: continue` line.
- A prompt the
  harness wrote, or a report from an agent this session spawned, continues
  the current turn as an entry: the turn's lines, overrides, checks, and
  change reads stand.
- A compaction opens a turn of its own and clears loads and reads. The route
  carries over, so `goated-route: continue` keeps the task. A clear
  (`session_start` from `cleared`) clears them too and ends the task, so
  the next prompt is routed afresh.
- **A task** starts at a route line that is not `continue` and runs through
  later `continue` turns. In a session with no task yet, a turn whose only
  route lines are `continue` starts a task that requires no skills.
  `goated-route: direct` exempts the task from `pipeline`. A new task ends
  the last one's lasting skips and [review points](#review-points).
- A session whose first prompt is a brief with a route line is **briefed**
  for good: it meets no Review item. So is one whose brief has a valid
  `goated-skills:` line and no route line (round 7, R2, decision D2), for
  the Review item only: briefed-session orientation still needs the
  brief's route line, so such a session is routed as an unbriefed one is.
  Only the event model's `brief` flag (`starts_session`) makes a brief; a
  typed first prompt with a skills line is not one.
- **The brief's task** is the task its turn started. A person's prompt ends
  the brief's route, and with it briefed-session orientation in `pipeline`,
  but not that task: a person's follow-up continues it as above, and
  brings back no orientation. A route line that starts a new task ends the
  brief's task, so it needs the router.

## Subagents

For a subagent (`session.agent.role` of `subagent`):

- the routing gates do not apply, since the parent's brief carries the route;
- every other gate applies, `reference-reads` and `review-intake` aside,
  judged from the subagent's own turn: only its own loads and reads count;
- no override applies;
- the closeout does not run when it stops, but a commit the `commit` gate
  passes meets the closeout judged from its own turn: its changes, checks,
  loads, reads, and skip lines. It was started from a brief, so it meets no
  Review item. Its changes also count toward the closeout of the parent
  turn that spawned it.

## Notices

A notice never holds.

- `fail_open`: the core could not judge and allowed the event (see
  [Failing Open](#failing-open)).
- `warning`: it judged, but something it reads was missing, such as a
  subagent's turn or the registry.
- `override_recorded`: a person's override for the turn.
- `closeout_note`: after the main agent's first finished file write of a
  turn that changes code inside the project, first the project's own
  context documents that exist (see [Calling The Core](#calling-the-core)),
  and none when none does (round 7, R11), then the closeout items the turn
  will meet, each short, judged as if the turn ended there, Reads
  included. Once per
  turn; none in a turn the closeout already held. It is also given once per
  task while its list of item labels is unchanged (round 7, R4, decision
  D5): a later turn of the task whose list is the same as the last note's
  gets none, and one whose list differs gets the note, naming the new list.
  The check compares the items' labels only, in order, so a turn whose
  items are the same but whose wording differs, such as a Reads item naming
  other references, gets no note.
  A new task's route or a clear ends the record; a compaction does not.
- `session_notice`: at a session start, when the shared policy or the router
  is missing, or project agent files the onboarding skills write are
  missing; and at the next person's prompt after a session's third declined
  or unanswered hold, once per session, naming `retrospective`.
- `skip_carried`: on a pending call of the main agent that no gate holds,
  when a lasting skip let it through `design`, `design-reads`, or
  `reference-reads` (see [Holds](#holds)), one per gate. It names the skip
  line's skill, the references, and the kind of file. It is given once per
  task for each gate, skill, and kind of file it names (round 7, R3,
  decision D4): a later write that the same lasting skip lets through
  carries none, and one that a skip for another kind of file lets through
  carries its own. The record ends with the lasting skips, at a new task
  or a compaction. An adapter shows it to the agent.
- `reads_owed`: on a pending call of the main agent that no gate holds,
  when `design`, `design-reads`, or `reference-reads` let a write
  land before its reads (see [Holds](#holds)), one per call, and only
  when the call owes a reference no earlier write of the turn that landed owes. It
  names each such reference with the gate that selected it and its skip
  line, and says the Reads item will ask for the reads and a change read.
  An adapter shows it to the agent. A known limit, accepted: an edit of
  the same message that has not finished yet counts as already owing, so
  if it then fails, a second edit's notice may leave out references the
  agent saw only on the failed edit's notice; the Reads item still asks
  for them.
- `route_continued`: at a person's prompt in a session with a routed task, which
  then runs as `goated-route: continue` (see
  [Prompts, Turns, And Tasks](#prompts-turns-and-tasks)), once per prompt.
  It says that new work needs a new route line. An adapter shows it to the
  agent.

## Failing Open

The core never blocks because of its own failure. It allows the event, with
a `fail_open` notice that says why, when:

- the request cannot be read, or its `event_model` is not a version it knows;
- the turns it needs cannot be read, or do not show the prompt the event
  belongs to;
- it hits an internal error;
- its state, where it keeps any, is unsafe to trust.

State that cannot be read is reset, and a reset can only re-hold, never pass.
A finished-call event has no action to let through, so its failure adds
nothing.

## What An Adapter May Leave Out

An adapter enforces less than this contract only where its harness lacks a
hook, documents each gap, and never enforces a rule this file does not
state:

- a harness that cannot hold a call before it runs cannot enforce the call
  gates;
- a harness that cannot hold a turn's end delivers the closeout as a request
  to continue, and documents it;
- a harness that cannot tell who wrote a prompt marks it `unknown`, and no
  override counts from it;
- a harness with no subagents sends none.

## Calling The Core

The shared core at [`adapters/core/`](../adapters/core/) enforces this
contract ([`adapters/README.md`](../adapters/README.md#the-shared-core) says
how an adapter calls it). Its JSON command and its Python request call take
the same request and give the same decision.

- **Requests carry the turns.** Each request carries every turn since the
  last compaction. The core keeps, keyed by the request's session id and in
  a folder the caller may set, only the facts that outlast them (ADR 0004),
  and the overrides a person typed.
- **A prompt's overrides are recorded at its `prompt_submitted` event**, for
  the turn that prompt opens, and apply only to that turn's calls and end.
  A harness that sends no such event gets no override, so no free bypass.
- **Hold text is complete.** A decision's hold and notice texts are whole,
  in words that name no harness: where a line can go is said in the model's
  terms (reply text or a call's `line_text`). An adapter adds its own words
  only around them, never inside.
- **The adapter reports the project's context documents.** A request's
  `project.context_docs` lists which of `CONTEXT.md`,
  `docs/agents/context-matrix.md`, and `docs/agents/project-standards.md`
  (`gates.CONTEXT_DOCS`) exist at the project's root; the core reads no
  file for them (round 6's R13). The `pipeline` hold for orientation and
  the `closeout_note` name those listed, and name none when the list is
  absent or empty.

## Detection Detail

The rules above name what is detected. This section gives the exact tables
the shared core judges by, in the core's words; each cites the module under
`adapters/core/goated_core/` that holds it. An adapter's own documentation
says only which of its harness's calls become which call kinds, and what its
transcript records.

Shell commands are read lexically, for a `posix` or a `powershell` shell, as
the `shell_command` call's `shell` says. When the reading cannot tell, it
errs toward holding, toward a change, and toward inside the project, as each
rule below says.

### Code And Test Files

- **Code** is a file with a programming-language extension: `.py`, `.js`,
  `.jsx`, `.ts`, `.tsx`, `.mjs`, `.cjs`, `.go`, `.rs`, `.java`, `.kt`,
  `.kts`, `.swift`, `.c`, `.h`, `.cpp`, `.hpp`, `.cc`, `.cs`, `.rb`, `.php`,
  `.scala`, `.ps1`, `.psm1`, `.sh`, `.bash`, `.lua`, `.dart`, `.vue`,
  `.svelte`, `.sql`, `.ex`, `.exs`, `.clj`, `.fs`, `.zig`, `.r`, `.jl`, and
  `.ipynb` (`CODE_EXTENSIONS` in `actions.py`). Docs and configuration files
  are not code.
- A **test file** is judged by its path inside the project, so a folder
  above the project, such as the `tests` in `D:/tests/myapp/`, makes nothing
  a test. It is one under a `tests/`, `test/`, or `__tests__/` folder at any
  depth, or a top-level `spec/` folder; or one named `test_*`, or `*_test.*`,
  `*_spec.*`, `*.test.*`, or `*.spec.*` with exactly one extension after the
  word. So `tests/helpers/factory.py`, `src/app/test_runner.py`, and
  `src/a.test.ts` are test files, and `src/spec/parser.py` and
  `src/a.test.d.ts` are not.
  A file whose place in the project is unknown, because the project is
  unknown or the path cannot be read for certain, is not a test file
  (`TEST_PATH_RE` and `is_test_path` in `design_reads.py`). The design gates,
  the closeout's Docs item, and branch size share it.
- **Test data** is a test file, or any file under a `fixtures/` or
  `__fixtures__/` folder at any depth inside the project, judged by the same
  path (`FIXTURE_PATH_RE` and `is_test_data_path` in `design_reads.py`). It
  decides only whether the design gates judge a configuration file: a code
  file under a fixtures folder, such as `fixtures/build.py`, is still code,
  and a test file only by the rule above. `security` and the closeout's
  Setup item do not use it.

### Project Folders And Scratch Files

The project's folders are `project.folders`, the session's working folder,
and the nearest folder at or above either that holds a `.git` entry, so a
session that changed folder below its checkout still counts the whole
checkout. A file is outside only when it is under none of them in any way
the path can be read, with symbolic links and junctions resolved too
(`actions.py`):

- A relative path is taken from the working folder; a shell write target is
  taken from a folder change before it only as [Shell Reading](#shell-reading)
  says, and counts as inside when its folder is unknown.
- A leading `~` or `~/` is the home folder, read both as `project.home` and
  as `HOME`. On Windows, 8.3 short names such as `PROGRA~1` are expanded
  where the folders exist.
- On Windows, a one-letter top folder naming a drive that exists is Git
  Bash's name for that drive (`/c/work` is `C:/work`); it may also be a
  folder on any drive the project's folders use, and each reading is
  checked. The same applies to a project folder given in that form. On
  Windows, `/tmp/x` is also read as `x` in the temp folder, where Git Bash
  mounts `/tmp`: under `TMP` and under `TEMP`, each that is set, and both
  must be absolute Windows paths, or `/tmp/x` counts as inside. Any other
  path rooted with no drive, such as `/etc/x`, counts as inside, since Git
  Bash mounts `/` as its install folder and a user may add mounts.
- These count as inside, since the core does not read them: a path holding a
  variable or glob (`$`, `%`, a backtick, `*`, `?`), `~-`, `~+`, or another
  user's `~name`, device paths (`\\?\`, `//?/`, `\\.\`), network paths
  (`\\server\share`), a drive-relative path such as `C:x`, and, on Windows, a
  folder or file name ending in a dot or space.

A shell write whose files the command does not name (`git apply`, `patch`, a
download without an output name, a .NET call) counts as a change to
non-test code, wherever it runs. An inline script's write whose path is
built from the system temp folder is outside, as
[Inline Scripts](#inline-scripts) says (round 6, R12).

A **scratch file** is outside the project by these rules, inside no git
checkout (no folder at or above it holds a `.git` file or folder), outside
`project.agent_folders`, and not a folder that holds the project. When any
of that cannot be checked, the file is not scratch. So a write into another
repository, such as a worktree under the temp folder or a sibling checkout,
or into the harness's own settings, is routed. For the scratch pass of the
routing gates, a shell command passes only when every simple command in it
is a [plain read](#plain-reads), a folder change, a command that only
writes, copies, moves, or removes the files it names (`cp`, `mv`, `rm`,
`rmdir`, `touch`, `truncate`, `tee`, `ln`, `unlink`, `shred`, the cmd forms
`copy`, `move`, `ren`, `del`, `erase`, and `rd`, the PowerShell
`Copy-Item`, `Move-Item`, `Remove-Item`, `Rename-Item`, `Tee-Object`,
`New-Item`, `Set-Content`, `Add-Content`, `Clear-Content`, `Out-File`,
`Export-Csv`, and `Export-Clixml`, and their aliases; not `install` or
`rename`; `FILE_WRITERS` in `shell.py`), or a plain read with its output
redirected into a file, so `cp a /tmp/x && cat f` passes and
`cp a /tmp/x && ./script.sh` is held. A write with any file that is not
scratch, or whose files cannot be named, is held as before, and so are
spawns and commands that write nothing.

The `design`, `design-reads`, `reference-reads` (but for a `gate-fires`
signal), `review-intake`, `scripted-edit`, and `security` gates and the
closeout judge only files inside the project. The `conflict-resolution` and
`repeated-failure` gates hold a write wherever its file is, since a worktree
with a conflict, or the code a failing check runs, may sit outside the
project.

### Security-Sensitive Paths

A path is lowercased, with camelCase humps split by `_`, and a word counts
only when it stands alone between `/`, `.`, `_`, or `-`, so `tokenizer.py`
and `author.py` are not held, while `api_token.py` and `userAuth.ts` are.
The first matching category is named (`SECURITY_CATEGORIES` in
`actions.py`):

| Category | Paths |
| --- | --- |
| dependencies | `package.json`, `package-lock.json`, `pnpm-lock.yaml`, `yarn.lock`, `requirements*.txt` or `.in`, `pyproject.toml`, `poetry.lock`, `uv.lock`, `Pipfile` and its lock, `Cargo.toml` and `Cargo.lock`, `go.mod`, `go.sum`, `Gemfile` and its lock, `composer.json` and its lock, `*.csproj` |
| secrets | `.env` and `.env.*`, `*.pem`, `*.key`, `*.p12`, `*.pfx`, `id_rsa`, `id_ed25519`, `id_ecdsa`, and the words `secret`, `credential`, `token`, `apikey` or `api_key`, singular or plural |
| auth | the words `auth`, `authn`, `authz`, `authenticat…`, `authoriz…`, `oauth`, `oauth2`, `login`, `logout`, `signin`, `jwt`, `password`, `permission`, `rbac`, `acl`, `policy`, and the plurals of `password`, `permission`, `acl`, and `policy` only; `session` or `sessions` only beside another of these words in the path |
| persistence | a `migration/` or `migrations/` folder, `schema.sql`, `schema.prisma`, any `.sql` file |
| deploy-and-ci | `Dockerfile`, `docker-compose`, `.github/workflows/`, `.gitlab-ci`, a `terraform/` folder or `.tf` file, a `k8s/` or `helm/` folder, `serverless.yml` or `.yaml` |

A session is often a program's run, not a login, so `session` is no auth
word of its own (round 7, R5): `src/runtime/session.py` meets no `security`
hold, while `src/auth/session.py` and `src/login_session.py` do, through
the other auth word beside it.

Of docs-like files, only dependency manifests (`requirements.txt`) are
sensitive. Test code, a code file that is also a
[test file](#code-and-test-files), is not sensitive by a word in its name:
it meets neither auth nor secrets, so `tests/test_auth_x.py` meets no
`security` hold while `src/auth.py` does (the maintainer's choice X3,
2026-11-19). It still meets the categories a file's kind or folder selects
(`TEST_CODE_SPARED` in `actions.py`): `migrations/0001_test.sql` is
persistence. A test file that is not code meets every category, as
`tests/.env`, `tests/requirements.txt`, `docker-compose.test.yml`,
`.github/workflows/run_test.yml`, `test/fixtures/server.key`, and
`tests/secrets.json` do, and a folder such as `src/testing/` is no test
path. The Security closeout item and the `reference-reads` gate's
`sensitive-category-count` signal use the same categories.

### Checks

A **check** is a test runner, linter, type checker, or build tool
(`pytest`, `python -m unittest`, `npm test`, `cargo test`, `go vet`, `tsc`,
`make check`, and the like, also through `uv run`, `npx`, and the other
command runners), or a script whose name holds, as a whole word, `test`,
`tests`, `check`, `checks`, `lint`, `typecheck`, `verify`, `validate`,
`build`, or `ci` (`scripts/validate_skills.py`, `npm run typecheck`). The
tables are
`CHECK_TOOLS`, `CHECK_MODULES`, `SUBCOMMAND_CHECKS`, `SCRIPT_RUNNERS`,
`TARGET_RUNNERS`, `COMMAND_RUNNERS`, and `CHECK_WORD_RE` in `shell.py`.
Inline interpreter code (`python -c`, `python -Bc`, `node -pe`, `perl -e`)
is not a check; a shell's inline command line (`bash -c`, `pwsh -Command`)
is read as a command line, so `bash -c 'npm test'` is a check and
`bash -c 'echo tests ok'` is not.

For the Proof item, the check may be a later call, or later in the same
shell command as the write (`cp a.py src/a.py && pytest`): every command
from the write to the check must be joined by `&&`, `;`, or a newline, none
of them an `exit`, `return`, or the like, and neither inside a branch, loop,
function, or group (`if`, `( )`, `{ }`); the check must not run in the
background (`pytest &`), though a pipe or `||` after it is fine
(`pytest 2>&1 | tee log.txt`). A check sent to the background with `&` is
no check, in its own call too (`ShellCommand.is_check` in `shell.py`), so
it neither meets Proof nor counts toward or resets
[repeated failures](#repeated-failures). A shell call whose `background` is
true is no check at all, in a later call or the same one: its launch proves
nothing, and its result is not read. A code file written after the check, or by a
.NET call (`[IO.File]::WriteAllText`) anywhere in the command, is not proved
by it; another file written after it, such as a log, does not matter.

### Repeated Failures

The `repeated-failure` gate holds a write once one check has failed twice
in a row in the turn (`REPEATED_FAILURES` in `actions.py`). A shell command
is held when any of its simple commands writes and is not itself a check,
so `sed -i … && pytest` and `pytest | tee out.txt` are held, while
`pytest > out.txt` is a rerun.

- **The same check** is the same command text run from the same folder,
  whitespace aside. A leading `cd` to a folder joined by `&&` or `;` names
  the folder: `cd pkg_a && pytest -q` and `cd pkg_b && pytest -q` are two
  checks, and `cd <the working folder> && pytest -q` is `pytest -q`. The
  text is compared without any trailing pipes into output filters (`tail`,
  `head`, `grep`, `egrep`, `findstr`, `more`, `less`, `tee`, `Tee-Object`,
  `Select-Object` or `select`, `Select-String` or `sls`, `Out-Host`,
  `Out-String`, in any case) or a `2>&1` or `*>&1` before them
  (`PIPE_TAIL_RE`, `STDERR_MERGE_RE`, `LEADING_CD_RE`); so
  `pytest -q | tail -20` and `pytest -q | tail -40` are one check, and a
  narrowed rerun such as one test file of a failing suite is another. The
  hold shows the check without its `cd`.
- **A failed run.** A piped run fails by what it prints (`N failed`,
  `N errors`, `FAILED (`, `FAIL`, `npm ERR!`, `error TS…`,
  `test result: FAILED`, and the like; `FAILURE_SIGNS_RE`), since the exit
  code is the filter's; any other run fails by its result's `ok`.
- **A missing module.** A run whose only failures are test modules that
  could not load a missing module or name neither adds to the count nor
  resets it, whether or not it looks failed, since in TDD the first red run
  often fails because the module under test does not exist yet. Only each
  runner's own report counts: pytest's `ERROR collecting` section showing
  `ImportError while importing test module` or ending in an `ImportError` or
  `ModuleNotFoundError`; unittest's `_FailedTest` error ending in one of
  those; jest's `Test suite failed to run` with `Cannot find module`
  (`LOAD_ERROR_SIGNS`). A run counts as usual when it also shows a failure in
  a test that ran (`1 failed, 1 error`), when a module that is there fails to
  load (a `SyntaxError` or `NameError`: the edit-and-crash loop the gate
  exists for), or when a test only prints such text. These miss, toward
  holding: output cut before the runner names the cause
  (`pytest -q | tail -3`), ts-jest's `TS2307`, and vitest's
  `Failed to load url`.
- **The first run after a test write.** When the first run of a check after
  a finished write to a test file in the turn, by a file write or a shell
  command, fails, it neither adds nor resets: in TDD that run is meant to
  fail. Only that first run is judged this way: a pass there resets the
  count as any pass does, and a missing-module run there (above) uses up the
  excuse, so the run after it counts as usual. A held or failed write
  excuses nothing, nor does a shell write whose target was written from an
  unknown folder.
- **Fewer failures.** A run whose runner reports fewer failed and errored
  tests than the check's run before it neither adds nor resets: pytest's
  summary line (`3 failed, 1 error in 0.2s`), unittest's
  `FAILED (failures=…, errors=…)`, jest's `Tests:` line, and cargo's
  `test result: FAILED` (`FAILURE_COUNT_SIGNS`). When either run's count
  cannot be read, the run counts: output with no summary, a runner that
  prints no count (`go test`), two runners' summaries in one run, a summary
  counting no failure (`Tests: 0 total`), or a run showing a test module or
  suite that could not load (pytest's `ERROR collecting` or
  `Interrupted: 1 error during collection`, unittest's `_FailedTest`, jest's
  `Test suite failed to run`), whose tests are missing from its count.
- A pass of the check resets its count; other commands between runs do not.
  A call that never ran (`held`, or `ran` false) does not count.

The `reference-reads` gate's `gate-fires` signal for this gate observes the
same condition, its runs counted the same way.

### Conflicts

A merge conflict is open in the turn after any of these (`CONFLICT_MARKER_RE`,
`GIT_CONFLICT_COMMAND_RE`, `GIT_CONFLICT_RESULT_RE`,
`GIT_CONFLICT_END_RE`, and the `GIT_DIFF_*_RE` patterns in `actions.py`, and
`FILE_PRINTERS` in `shell.py`):

- an edit whose removed text has a `<<<<<<<` or `>>>>>>>` marker at a line
  start, followed by a space or the line's end;
- a finished call in the turn that showed a file with such a marker, which
  opens the conflict for writes to that file, by a file write or a shell
  command such as `git checkout --theirs`. Three calls show a file this way:
  - a file read whose text has the marker;
  - a shell command that runs a file printer (`cat`, `head`, `tail`, or
    PowerShell's `Get-Content`, `gc`, or `type`) and whose output has the
    marker. It shows every file the printers name, so `cat a b` opens the
    conflict for both, whichever held the marker;
  - a shell command that runs `git diff`, for each file whose section of the
    output adds the marker after the diff's `+` or `++` prefix
    (`++<<<<<<<` in a combined diff). A section is named by its
    `diff --cc` line or its `+++` line, as the diff names the file, from the
    repository's top folder, with git's quoting of a name undone
    (`"b/caf\303\251.py"` is `café.py`).

  Another command that prints the markers, such as `grep`, `git show`, or
  `git log -p`, shows no file;
- a git merge, rebase, cherry-pick, revert, or pull whose result in the turn
  reported a conflict, which opens it for any write.

A marker line may be preceded by a line number and a tab or `→`, as a file
read's or `cat -n`'s numbered output shows it.

A finished shell command that runs `--abort`, `--quit`, `--continue`, or
`--skip` of a git merge, rebase, cherry-pick, or revert, a finished shell
`git commit`, or a finished `commit` call ends the conflict and drops the
files shown before it, unless that same command reports a new conflict. A
held or failed one ends nothing. Only the turn is
read, not the repository, so a conflict opened in an earlier turn is caught
only by markers the turn shows: an edit whose removed text spans only
`=======` and one side, in a file not shown this turn, is not held, because
`=======` alone is also a heading underline. A conflicting stash pop or
apply is not held. A commit ends a conflict when a git conflict is open in
the turn, or when a finished edit in the turn resolved one, which shows a
conflict opened in an earlier turn (`_resolves_conflict` in `actions.py`,
the lead's narrow rule, 2026-11-19). An edit resolves a conflict only when
all of these hold:

- one edit's removed text holds a whole block in order: a line starting
  `<<<<<<< `, then a `=======` line, then a line starting `>>>>>>> `;
- that edit's added text holds no marker line (`<<<<<<<`, `=======`, or
  `>>>>>>>`);
- the file is not a [doc](#closeout-items), as the Docs item tells one.

So removing a marker example from a doc, or one marker line from code,
ends no conflict, and neither do markers a read or a printer only showed.
Such a commit, with `resolving-merge-conflicts` loaded, is not asked for the Docs, Design,
Security, Review, or Verification items; it still needs its change read and
Reads, Proof, Unfinished, and Setup (see [Closeout Items](#closeout-items)); `git merge --continue` ends the conflict
but is not a commit, so it meets no closeout.

### Commits And Pull Requests

A shell command commits when one of its simple commands is `git commit`,
not `--dry-run`. It opens a pull or merge request when one is `gh pr create`
or `gh pr new`, or `glab mr create` or `glab mr new`, with its options
before the noun, between the noun and the verb (`gh pr -R x create`), or
after the verb. An option's value is never read as the verb: between the
noun and the verb, `--x=v`, an attached short form (`-Rx`, `-R=x`) and
`--help` or `-h` are one word, any other `--x` or `-x` takes the next word
as its value, as `gh`'s parser does, and `--` ends the options with no
verb. So `gh pr -R create list`, `gh pr --state create list` and
`gh pr --draft create` open nothing. Each is recognized per simple
command, so `echo gh pr create` opens nothing. A chained command may open
several, and each is read with its own simple command's options alone: a
later one never takes an earlier one's `--repo`, `--base` or `--head`, so in
`gh pr create -R other/x && gh pr create` the second is aimed at the
working folder's checkout. A `commit` call and a `pull_request` call are
judged the same way.

The step that asks for a [change read](#change-reads) is skipped for a
`commit` or `pull_request` call when the turn changed no project file: it
carries the change in its own input, and outside a git checkout no diff can
run and no changed file exists to read, so the strict hold would have no way
out. The `pull-request` gate and `pr-review` ask for the same change read,
so one read meets both. `pr-review` asks for it whenever
`standards-and-spec-review` has loaded and the pull request measures 400 or
more lines (below), whether or not `pr-description` was skipped.

### Branch Size

`standards-and-spec-review` gives the number: a branch whose work against
its base is 400 or more changed lines, added plus deleted, in code files
outside test paths (`REVIEW_MIN_LINES` in `actions.py`). A file counts when
it is code and its path from the top of the checkout is not a test path;
docs, fixtures, configuration, and tests add nothing. Risk, unclear
acceptance, and uncertain conventions, the policy's other reasons, are left
to the router. Branch size is the only place the core runs commands; git
runs in the session's working folder, with a limit of two seconds for all
its calls (`SIZE_TIMEOUT_SECONDS`).

**A pull request**, for the `pr-review` gate, is measured only when the call
would otherwise be held by it. The core asks git which candidate refs exist
(`git for-each-ref`), then measures the first base and head found:

```text
git diff --numstat -z --no-relative --no-ext-diff --no-textconv <base>...<head> --
```

- `<base>` is the branch the pull request merges into: `--base` or `-B` on
  `gh pr create`, `--target-branch` or `-b` on `glab mr create`, or the
  `pull_request` call's `base`, found as `origin/<base>` or else the local
  branch. Without one, it is the first that exists of `origin/HEAD`,
  `origin/main`, `origin/master`, `main`, and `master`
  (`DEFAULT_BASE_REFS`).
- `<head>` is the branch it merges from: `--head` or `-H` on `gh`,
  `--source-branch` or `-s` on `glab`, or the call's `head`, found as the
  local branch or else `origin/<head>`. Without one, it is the checked-out
  `HEAD`. Only committed work counts, which is what the pull request opens.
- A `pull_request` call that names a `repository`, or a shell
  `gh pr create|new` or `glab mr create|new` that names one with `--repo` or
  `-R` (before the noun, between it and the verb, or after the verb, as
  `-R x`, `--repo=x`, `-R=x` or `-Rx`), is measured only when it matches
  the checkout's `origin` URL (one more git call). Aimed at another
  repository, or from a folder with no `origin`, it is not measured. A
  shell value names its repository by path: a host prefix
  (`github.com/owner/repo`, `gitlab.example.com/group/sub/repo`) or
  a full HTTPS or SSH URL names the same repository as `owner/repo`; a
  first part holding a dot, before two more parts, is read as a host. A
  value that is not an `owner/repo` path names no checkout and is not
  measured. The `GH_REPO`-style environment variables and a default set
  with `gh repo set-default` are not read: a command without the option is
  measured in the working folder's checkout.
- A shell command that opens several pull requests has each measured on
  its own, with its own base, head and repository, in order, and the gate
  holds when any of them measures 400 or more lines. Measuring stops at the
  first that does, so each is measured at most once, two naming the same
  base, head and repository are measured once, and the two-second limit
  covers every measure of the call together. The hold names the pull
  request it measured by its place in the command and its base ("its
  default base" when it names none), adding "from <head>" when it names a
  head; a backtick in a branch name is shown as a single quote, since
  backticks name a skill to load. A command opening one pull request is
  measured and named as before.

Values of the command's other options are never read as options
(`PR_VALUE_OPTIONS` in `shell.py`), so `--description "-bump deps"` names no
base. Every name reaches git inside a full ref name (`refs/…`), so none can
read as a git option.

**A branch**, for the closeout's Review and Verification items, is measured
as it stands, against the base found without a `--base`. That counts the
branch's commits since it left the base, staged and unstaged changes, and
every line of each untracked file git does not ignore; a binary file counts
no lines and a symbolic link one, as in `git diff`, and a link's target is
never read. Where the base branch exists both locally and on `origin`, the
branch is measured from the fork point closer to it, so work merged into a
local `main` and not yet pushed does not count toward the next branch. The
`pr-review` gate keeps measuring from `origin/<base>` first.

```text
git for-each-ref --format=%(refname) %(symref) <candidate base refs>
git rev-parse --show-toplevel --symbolic-full-name HEAD
git merge-base HEAD <base> [<the same branch's other ref>]
git diff --numstat -z --no-relative --no-ext-diff --no-textconv <merge-base> --
git ls-files --others --exclude-standard --full-name -z -- :/
```

The size is asked for only in a turn that changed code (or a sensitive file,
for Verification), and only when nothing else has met the item. Because the
branch is measured, not the commit, a large ticket split across commits is
still caught. A later turn on a large branch that changes code raises the
item again only once the branch has grown by 50 lines or more since the
task's [review point](#review-points), or when the task has none; this
reverses Ticket 069's rule that only a review in the same turn counts. The
size is also asked for to record a point when a turn meets or declines the
item. A commit in a turn that changed no code meets no Review or
Verification item, and a commit made in another folder (`git -C <dir>`, or
after a `cd`) is measured as the working folder's branch, or not at all when
that folder is no checkout.

When the size cannot be measured, nothing counts as large and `pr-review`
does not hold: no base or head is found (a head from another fork,
`owner:branch`, or a branch not yet fetched), on the base branch itself,
with a detached `HEAD`, when git is missing or fails, in a folder that is
not a git checkout or that cannot be read for certain, or past the time
limit. Holding on an unknown size would hold every pull request from a fork
or another clone, and a justified-skip hold that fires without evidence
teaches agents to skip it.

A session whose first prompt was a brief with a route line or a valid skills
line meets no Review item for the whole session, typed prompts and compactions included: the
starting session reviews the work when it inspects the report and the
changed paths (`handoff`'s spawn-brief template). Missing state counts as
not briefed.

### Reviewer Agents

A reviewer agent is a finished spawn that starts work now (`starts_now`)
and is not `separate`, that no gate held, whose brief follows
`subagent-driven-development`'s reviewer prompt (`references/reviewer-prompt.md`, read, with its
`Review Mode`, `Review Inputs`, and `Required Report Format` headings). The
core records which templates each spawn's brief followed, by the call's id,
in its state. It has reported once its result arrived; started in the
background (the result's `agent.background`), once an `agent_finished` entry
names it. A reviewer that finished after the turn's last code change meets
the Review item, and one that reported in the turn opens the `review-intake`
gate. A separate session started with a reviewer brief is not one: its
result says only that the review started. Nor is a spawn that only
proposes the work, whatever its brief: it ran nothing. A brief that follows `handoff`'s
spawn brief or the implementer prompt is not a review, and the Review item's
text says to use the reviewer prompt. Whether the review was any good is not
judged. The `review-intake` gate holds a test file like other code; a docs
or configuration file is not held.

### Shell Reading

The core splits a command into its simple commands (joined by `;`, `&&`,
`||`, `|`, `&`, newlines, parentheses, braces, or `$(`) and reads each one's
real command word past wrappers (for example `sudo -u <user>`, `doas`,
`env`, `timeout <n>`, `nice`, `nohup`, `exec`, `time`, `stdbuf`, and
`xargs`; `WRAPPERS` in `shell.py`), past `cmd /c` or `cmd /k` (read in
`_resolve`), past leading variable assignments, a quoted or full path to
the program (`"git"`, `& "C:\…\git.exe"`), and line
continuations (`\` in `posix`, a backtick in `powershell`). A command
writes, and meets the `route-line` and `pipeline` gates like a file write,
when one of its commands:

- redirects output into a file (`>`, `>>`, `&>`, `>&file`, `2>`), except
  into another stream (`2>&1`) or a target in the shell's `NULL_TARGETS`,
  compared in any case. Null devices are per shell: in either shell
  `/dev/null`, `/dev/stdout`, `/dev/stderr`, and `$null`, and in a
  `powershell` command also `NUL`. In a `posix` command a redirect into
  `nul` writes a file named `nul`, as bash does, as
  [Plain Reads](#plain-reads) also treats it, and a routing hold such a
  command meets ends by naming `/dev/null` as the posix null device;
- runs `tee`, `Tee-Object`, `cp`, `mv`, `rm`, `rmdir`, `touch`, `truncate`,
  `ln`, `unlink`, `shred`, or `patch`, or the cmd forms `copy`, `move`,
  `ren`, `rename`, `del`, `erase`, or `rd`;
- edits in place with `sed -i`, `perl -i`, or `ruby -i`;
- runs `Set-Content`, `Add-Content`, `Out-File`, `Clear-Content`, `New-Item`,
  `Copy-Item`, `Move-Item`, `Remove-Item`, `Rename-Item`, `Export-Csv`, or
  `Export-Clixml`, or one of the stock Windows PowerShell 5.1 aliases (`sc`,
  `ac`, `clc`, `del`, `erase`, `copy`, `move`, `ren`, `rd`, `ri`, `mi`, `cpi`,
  `ni`, `rni`), or a .NET `[IO.File]::Write…` style call (`DOTNET_WRITE_RE`).
  In a `powershell` command, a .NET call's text counts wherever it appears,
  since PowerShell can run text in many ways (`& $p`, `Get-Content x | iex`).
  In a `posix` command, a .NET call's text handed only to text tools, which
  cannot start a program (`cat`, `echo`, `printf`, `grep`, `rg`, `head`,
  `tail`, `sort`, `tee`, `Write-Output`, `Select-Object`, and the like;
  `NO_POWERSHELL`), is data, such as a heredoc fed to `cat`. It is still a
  write when it holds a `$(` or a backtick that may run it, outside a
  quoted-delimiter heredoc (`<<'EOF'`); when it is piped on into any other
  program (`… | pwsh -Command -`); when it is written into a PowerShell
  script file (`.ps1`, `.psm1`, `.psd1`) by a redirect or `tee`, wherever
  that file is, since a later call may run it; and whenever the command names
  `pwsh`, `powershell`, `iex`, or `Invoke-Expression` anywhere, or runs a
  script (`. x.ps1`), which may run text written earlier in it.
  Interpreters (`python -c`, `node -e`) and `git` (an alias or hook) can
  start PowerShell, so text handed to them counts too;
- downloads to a file: `curl -o <file>` (also `-sSLo <file>`) or `curl -O`,
  `wget` unless it writes to standard output, or `Invoke-WebRequest -OutFile`;
- runs `git apply`, `git am`, `git restore`, `git mv`, `git rm`, `git clean`,
  `git checkout -- <path>`, `git checkout <rev> <path>`,
  `git checkout --theirs|--ours <path>`, `git reset --hard`, or
  `git stash pop|apply`;
- runs an [inline script](#inline-scripts) that writes, removes, or renames a
  file.

Text inside quotes, heredoc bodies, PowerShell here-strings, and comments is
ignored, as are comparisons inside a `[[ ]]` test that is the command (after
any `if`, `!`, or other keyword) and arithmetic in `$(( ))`, so
`echo "a > b"`, `[[ $a > $b ]]`, and `ls # a > b` write nothing. Elsewhere
`[[` is a plain word, so `cat [[ a > c ]]` writes `c`. Reads, test runs,
`git status`, and `git checkout <branch>` stay free.

**Folder changes.** A write target is read from the folder its command runs
in, and a `cd` moves that folder only when the core is certain it ran and
where it went. Only a plain `cd` in the command's leading `&&` chain is
followed: the first command, or one joined to everything before it by `&&`
alone. Plain means `cd`, `chdir`, `Set-Location`, or `sl` with exactly one
folder argument and no option other than `--` (or `-Path`/`-LiteralPath`
naming that folder), to an absolute path, a drive path, `~` or a path under
it, or a path starting `./` or `../` from a folder already known. So
`cd /elsewhere && mv a.py b.py` moves `/elsewhere/a.py`, outside the
project, and `cd ./sub && mv a.py b.py` moves `sub/a.py`, inside it.

Anything else makes the folder unknown for the rest of the command, and
nothing later makes it known again. Relative targets written from an unknown
folder count as inside the project, so `cd sub && mv a.py b.py` still
changes the project. That is:

- a `cd` to a bare relative name such as `sub`, which bash may find through
  `CDPATH` instead;
- a `cd` to a variable, a glob, a command substitution, `-`, `~-`, `~+`, or
  `+N`, with an option such as `-P`, with more than one argument, and a bare
  `cd`;
- any `pushd`, `popd`, `Push-Location`, or `Pop-Location`, since the folder
  stack can leave the folder unmoved (`pushd -n`) or rotate it (`pushd +1`);
- a command starting with `!`, since a failed `cd` then lets the `&&` after
  it run;
- a `cd` after `;`, a newline, `||`, `|`, or `&`, or that is followed by `|`,
  `||`, or `&`, since it may have failed, never run, or run apart;
- a `cd` inside `( )`, `{ }`, `$( )`, `case`, `if`, a loop, or a PowerShell
  script block;
- any separator other than `&&` after a followed `cd`, since what runs next
  runs even if that `cd` failed.

PowerShell 5.1 has no `&&`, and `;` is not a safe chain, so there a
`Set-Location` before a write leaves the write's relative targets counted as
inside; in PowerShell 7, `Set-Location <absolute path> && …` is followed.
Only a `cd` in the same command is followed, not one in an earlier call.

#### Shell Writes The Design Gates Judge

`design` and `design-reads` judge a shell command only where it puts new
text into a project code or configuration file
([Ticket 098](../tickets/archive/098-adapter-contract-gaps.md), the maintainer's
decision of 2026-11-18): a redirect of output into the file, `tee` or
`Tee-Object`, `Set-Content`, `Add-Content`, or `Out-File` and their aliases,
or `New-Item` or `ni` with a `-Value`. The text counts by the lines the
command shows: a heredoc's body fed to `cat` or `tee`, the arguments of
`echo`, `printf`, or `Write-Output`, shown text piped on through `cat`, a
quoted PowerShell string piped in, or a `-Value` (or `Set-Content`'s and
`Add-Content`'s positional value). Text it does not show counts as five or
more lines, as the closeout counts a shell write: a program's output
(`python gen.py > src/a.py`), and text the shell fills in, holding a `$` or
a backtick (`echo "$CODE"`, `-Value $code`, `-Value (Get-Content x)`), even
inside single quotes, where it would be literal. Writes to two spellings of
one file in one command add up (`src/a.py`, `./src/a.py`, `src\a.py`).
Unlike the other rules, these gates skip a relative target written from an
unknown folder (`cd sub && echo x > src/a.py`), since it has no place to
judge, and a file an inline script writes (`_shell_text_writes` in
`actions.py`). A
code file written this way counts among the turn's code writes when the
gates find its first substantial change and its third code file. The gates
do not read the text for signals, so only the path selects a reference (a
configuration file, the third code file), and a test file selects none.

Other shell writes stay with the routing, `security`, and closeout rules
only. A copy, move, restore (`git checkout -- <path>`), or in-place edit
(`sed -i`) carries text that was designed elsewhere or a substitution the
command shows whole, so asking for a design load there would hold routine
file work. A file an [inline script](#inline-scripts) writes is the
`scripted-edit` gate's, and a write naming no file (`git apply`, `patch`)
shows no file whose design a hold could ask for.

#### Inline Scripts

When a command gives an interpreter its code inline, the core reads that
code for calls that write, remove, or rename a file (`script_writes.py`). It
reads the interpreters in `script_writes.LANGUAGES`: `python`, `python3`,
`py`, `node`, `perl`, `ruby`, `deno`, and `bun`, with any `python` followed
by a version (`python3.12`, `VERSIONED_PYTHON_RE` in `shell.py`) read as
`python`, each also through `uv run`, `npx`, and the other command runners
a check is read through. The code is given by an inline-code option
(`INLINE_CODE` in `shell.py`: `python -c`, `node -e`/`-p`/`--eval`/`--print`,
`perl -e`/`-E`, `ruby -e`, `bun -e`/`-p`/`--eval`/`--print`; and
`deno eval`), or reaches standard input when no script is
named (`python -`, `python`, `deno run -`, `bun run -`) from:

- a heredoc or `<<<` here-string on the interpreter (`python - <<'EOF'`,
  `python <<< "…"`);
- a pipe from a text producer: `cat` with no file, fed a heredoc
  (`cat <<'EOF' | python -`); `echo`, `printf`, or `Write-Output` with their
  arguments; or a PowerShell string or here-string alone
  (`@'…'@ | python -`). Text piped from a file (`cat notes.txt | python -`)
  or any other program is not read.

Such a script is a shell write: its files are the string literals its write
calls name, placed as any write target is (a `cd` it follows applies), and
it meets the routing gates, the path gates (`security`, `review-intake`,
`scripted-edit`, `reference-reads`, `conflict-resolution`,
`repeated-failure`), and the closeout.

A path given as a name counts as the literal that name is bound to when the
script binds it once, at its top level and before the call, to one string
literal with no run-time part: `p = "notes.md"` in Python (read from its
syntax tree, also as a `Path(p)` receiver), and `const`, `let`, or
`var p = 'notes.md'` in JavaScript, where every other use of `p` must be a
whole argument of a call or the object of a property (`f(p)`, `p.length`).
A name bound or changed anywhere else (a second assignment, `p += …`, a loop
or `with` target, a parameter, an import, an `except` name, `del`), bound
inside a loop, branch, function, or class, bound after the call, or bound to
anything but one literal (an f-string, a template with `${}`, a
concatenation, `input()`, an environment variable, a call, a JavaScript
statement that goes on past its line, such as a next line opening with
`.replace(…)` or `+ '.py'`) is not read. No name at all is read in code that
may bind one unseen: code the shell may expand (see below) holding `$` or a
backtick anywhere, or code using `exec`, `eval`, `globals`, `vars`,
`locals`, `sys.modules`, `__main__`, `__dict__`, `globalThis`, a star
import, or a JavaScript `with`. Perl and Ruby names are never read, since
their strings can change in place (`$p =~ s/a/b/`, `p << "x"`).

Any other write call whose path is not one literal is an unnamed write,
inside the project wherever the command runs, as `git apply` is: a script
reaches project files from any folder (`os.path.join(ROOT, …)`,
`sys.argv`, `os.chdir`). So is a literal holding `$` or a backtick in code
the shell may expand first: code given as an argument, an unquoted heredoc
(`<<EOF`), a `<<<` here-string, or piped text
(`python -c "open('$F', 'w')"` writes whatever `$F` holds). A
quoted-delimiter heredoc (`<<'EOF'`) expands nothing, so there `'$F'` is
the file's name. A name an import gives a listed module or function is
followed: `import shutil as s` then `s.move(…)`, `from os import remove`
then `remove(…)`, `from pathlib import Path as P`, and
`const {writeFileSync: w} = require('fs')` or
`import {rmSync as r} from 'fs'`.

A write call whose path is built from the system temp folder is outside the
project (round 6, R12), so it is neither a named file nor an unnamed write
(`_TempPaths` in `script_writes.py`). Its path's first part, inside any
joins, path constructors, string conversions, or an f-string or template
opening on a placeholder (`os.path.join(…)`, `Path(…)`, `str(…)`,
`f'{…}'`, `path.join(…)`, `` `${…}` ``, `await`), must be one of:

- in Python, a `tempfile` call (`gettempdir`, `gettempdirb`, `mkdtemp`,
  `mkstemp`, `mktemp`, `TemporaryDirectory`, `NamedTemporaryFile`), also
  as a name imported from `tempfile`, or `os.environ[…]`, `os.environ.get(…)`
  or `os.getenv(…)` of `TEMP`, `TMP`, or `TMPDIR`, the last two with no
  default, which may be a project folder; or a name bound exactly
  once, by an assignment or a `with` target and before the call, to such a
  path (`d = tempfile.mkdtemp()`, `with tempfile.TemporaryDirectory() as d`,
  then `p = d + "/x"`);
- in JavaScript, `os.tmpdir()`, `process.env` of `TEMP`, `TMP`, or `TMPDIR`,
  `Deno.makeTempDir` or `makeTempFile` and their `Sync` forms, or
  `Deno.env.get(…)` of those variables; a JavaScript name is not read.

A path holding `..` may climb out of the temp folder, and in code the shell
may have expanded, a `$` or backtick may hide one, so either stays an
unnamed write; so does a path whose first part is anything else, such as
`os.path.join(ROOT, tempfile.gettempdir())`. Perl and Ruby paths are never
read as temp. The temp folder is taken as the system's: a command that
points `TEMP`, `TMP`, or `TMPDIR` into the project first
(`TMPDIR=src python - …`) is not seen, a gap of this lexical reading. A script in which no write call is found
is not a write, so `python -c "print(1)"` and a script that opens files only
to read them pass. Inline code is never a check; `python -m pytest` still
is.

The calls, by language (`WRITE_CALLS` in `script_writes.py`):

| Language | Write calls |
| --- | --- |
| Python | `open`, `io.open`, `codecs.open`, `gzip.open`, `bz2.open`, `lzma.open` with a mode holding `w`, `a`, `x`, or `+` (a mode that is not a literal counts); `os.open` with a writing flag; `os.remove`, `unlink`, `rmdir`, `removedirs`, `truncate`, `rename`, `renames`, `replace`; `shutil.copy`, `copy2`, `copyfile`, `copytree` (the destination), `move`, `rmtree`; a path's `.write_text`, `.write_bytes`, `.unlink`, `.touch`, `.rmdir` (an unnamed file unless called on `Path("…")`), and `Path("…").rename`, `.replace`, and `.open` with a writing mode |
| JavaScript (`node`, `deno`, `bun`) | `fs` and `fs/promises`: `writeFile`, `appendFile`, `createWriteStream`, `unlink`, `rm`, `rmdir`, `truncate`, `rename`, `copyFile` and `cp` (the destination), `open` with a writing flag, and their `Sync` forms, the methods without `Sync` only on a file-system receiver; `Deno.writeTextFile`, `writeFile`, `remove`, `create`, `truncate`, `rename`, `copyFile`, and their `Sync` forms; `Bun.write` |
| Perl | `open` with a `>`, `>>`, or `+` mode, in its three-argument form or in the path of its two-argument form; `unlink`, `rmdir`, `rename`, `rmtree`, `remove_tree`; `File::Copy`'s `copy`/`cp` (the destination) and `move`/`mv` |
| Ruby | `File.write`, `IO.write`, `binwrite`; `File.open` and `File.new` with a `w`, `a`, or `+` mode; `File.delete`, `unlink`, `rename`; `FileUtils.rm` and its forms, `remove…`, `rmdir`, `touch`, `mv`/`move`, and `cp`/`copy`/`install` (the destination) |

The reading is lexical: a call spelled inside a string or comment of the
script still counts, toward holding. In Python, a name other code also
uses counts only where its module, receiver, or mode says it writes:
`.rename`, `.replace`, and `.open` only on a `Path("…")`, and `open` only
with a writing mode, so `text.replace("a", "b")` does not. In JavaScript,
`.open`, `.unlink`, `.rm`, `.rmdir`, `.truncate`, `.rename`, `.copyFile`,
and `.cp` count only on a file-system receiver: `fs`, `fs.promises`,
`fsPromises`, `Deno`, or a name the script binds to a `require` or `import`
of `fs`, `node:fs`, `fs/promises`, or `node:fs/promises`, with or without
a declaration and in a comma chain (`const f = require('node:fs')`,
`f = require('fs')`, `const p = require('path'), f = require('fs')`,
`import * as f from 'fs'`), a destructured name
included (`const {promises: p} = require('fs')`), each perhaps followed by
`.promises`. A receiver the core cannot name, one ending in a call or an
index (`require('fs').rm(…)`, `a[b].rm(…)`), counts too. Any other
receiver is some other object, so `window.open(url, 'width=200')`,
`db.rm(id)`, and `this.cp(a, b)` write nothing; a file-system object
passed into a script function under another name goes unseen. `.open`
writes when its second argument is a literal starting with `w` or `a` or
holding `+`, or is not a literal.

The `scripted-edit` gate judges a code file such a script writes inside the
project, test files included, and a file it names only at run time, which
is held as code would be wherever the command runs. The hold names such a
file as one whose kind cannot be told, not as a code file, in its full and
short forms; a named code file is "the code file" and its name. A path
through a name the script binds once to one literal is judged as that
literal's file. Once cleared, the script runs and its files count as
changed.

#### Plain Reads

Before the router loads, `router-first` passes a shell command made only of
plain reads, as it passes file reads, so an agent can look around before it
routes. Each simple command must be one of:

- `cat`, `head`, `tail`, `ls`, `dir`, `grep`, `rg` (without `--pre` or
  `--hostname-bin`), or `wc`;
- `pwd`, `echo`, `cut`, `tr`, `stat`, `which`, `true`, or `:`, and, as a
  whole `powershell` command, `$null`, which does nothing, as `true` does in
  a `posix` shell;
- `sort` without `-o`, `-T`, `--output`, `--temporary-directory`, or
  `--compress-program`, which write files or run a program;
- `uniq` with at most one file, since it writes its second, and no `*`,
  `?`, or `[` in any argument, quoted or not, since bash may expand one
  into several files (`uniq *.txt` overwrote the second);
- `diff` without `-l` or `--paginate`, which pipe its output through `pr`;
- `file` without `-C` or `--compile` (which write a magic file), `-z`, `-Z`,
  or `--uncompress` (which run decompressors), or `-m` and `--magic-file`;
- `find` without `-exec`, `-execdir`, `-ok`, `-okdir`, `-delete`, `-fprint`,
  `-fprint0`, `-fprintf`, or `-fls`;
- `git status`, `git diff`, `git log`, `git show`, `git rev-parse`,
  `git ls-files`, or `git blame`;
- `git branch` with only listing options (`-a`, `-r`, `-v`, `-vv`,
  `--show-current`, `--contains`, `--merged`, `--sort`, `--format`, and the
  like) and a pattern only after `--list`, so no name to create (`-l`
  meant `--create-reflog` before git 2.23); an option value given as the
  next word holds no `*`, `?`, or `[`, since a glob there expands into
  several words and one left over is a branch to create
  (`git branch --format *`), while `--format=*` passes;
- `git worktree list`, and `git remote` bare, with `-v`, or as `get-url`;
- `Get-Content`, `Get-ChildItem`, or `Select-String`, or their aliases `gc`,
  `gci`, and `sls`.

A git read has no `--output`, `--ext-diff`, `--textconv`, or
`--show-signature`, and no option before the subcommand but `-C <path>`,
`--no-pager`, or `-P`. GNU tools take a long option by any prefix of its
name and run short options together, so `sort --out=x` and `sort -uo x` are
held as `--output` and `-o` are; `git branch` takes prefixes too, so only
its listing options written in full pass (`--edit` would open an editor as
`--edit-description`). `git remote show` is held: it contacts each remote,
which runs ssh or a credential helper.

The command's first part may be a `cd` to one plain path, with no `$`,
wildcard, or option (`cd sub && ls`): it moves the reads after it and writes
nothing. A `cd` later in the command, `pushd`, and `cd -` are held.

The command word must be the bare name, in any case: `./cat`, `/bin/cat`,
or `cat.cmd` may be any program, so it is held. The commands may be joined
by pipes, `&&`, `||`, `;`, or newlines. The call is held when any part of it
is something else: another or unknown command, a wrapper such as `sudo` or
`xargs` or a variable assignment before the command, any output redirect, a
heredoc, a subshell, group, or script block, a process substitution, or a
background `&`. A redirect into a null device is held too, since a null
device in one shell is a real file in another: `nul` in bash, `/dev/null` in
PowerShell. The one exception is a `posix` command's redirect of standard
error, or another stream but standard output, into exactly `/dev/null`
(`ls 2>/dev/null`); `ls 2> errors.txt`, `ls > /dev/null`, and the same in a
`powershell` command are held. Duplicating a descriptor (`2>&1`) and an
input redirect (`< a.py`) are fine.

The call is also held when its text holds anything the lexical reading may
not follow as the shell does, even inside quotes: a `$` (variables,
`$(…)` inside double quotes, `${x:=…}`, arithmetic), a backtick, a backslash
(an escape in bash, where `-del\ete` is `-delete`, but a plain character in
PowerShell), `<<<`, a `>&` not followed by a whole descriptor (`>&2` is
fine, `>&2x` writes the file `2x`), any character but printable ASCII, a
newline, or a tab (curly quotes, which PowerShell reads as quotes; a lone
carriage return or U+2028, which it reads as a line break), a PowerShell
block comment `<#`, a PowerShell here-string, `[[` or `]]` (outside command
position a plain word, so a `>` after it redirects), `//`, which starts a
UNC path read over the network, where Windows may send the user's
credentials, `::` before a slash or backslash, a PowerShell provider path
(`FileSystem::\\host\share`) that can do the same, or PowerShell's
stop-parsing token `--%`, after which the rest of the line goes to a native
program unparsed. A backslash and `//` are fine inside a whole single-quoted
argument, which both shells read literally (`grep -n 'def\s+x' a.py`,
`grep 'http://x' src`), unless two slashes or backslashes, in any mix,
appear anywhere in it but right after a URL scheme such as `https:`: a
program may split a path off anywhere (`'-f//host/p'` is `-f` with
`//host/p`), and the core cannot tell a pattern from a path, so
`grep '// TODO' a.c` and `grep 'a\\b' a.py` are held. Inside a whole
double-quoted argument, a backslash is read as POSIX reads it (round 7,
R8): it escapes only `$`, a backquote, `"`, `\`, or a newline, and before
any other character stays literal, as it always is in PowerShell, so both
shells agree on it and it is fine (`grep -n "^#\|^##" a.md`). One before
those five, or at the argument's end, is held, since bash reads it as an
escape and PowerShell does not (`"a\"; rm b; "` ends the string in
PowerShell). The `$` and backtick rules still hold inside double quotes,
so `grep "\$(rm x)" a`, which bash reads as the literal text `$(rm x)`, is
held, as `grep "$(rm x)" a` is; so are two separators that may start a
network path, under the single-quote rule, and a slash pair, which double
quotes do not exempt. A quote inside a word (`x'\s'`, `-e"a\|b"`) gets no
exemption. So a Windows path with
backslashes, such as `Get-Content src\a.py`, is held;
`Get-Content 'src\a.py'`, a file read, or a forward-slash path passes. When
the analysis cannot tell, the call is held. The lists are
`READ_ONLY_COMMANDS`, `READ_ONLY_REFUSED_ARGS`, `READ_ONLY_REFUSED_OPTIONS`,
the `GIT_READ_*` and `GIT_BRANCH_*` tables, and `NOT_PLAINLY_SPELLED_RE` in
`shell.py`. Once the router loads, commands are judged as before.

#### Whole Prints

A simple command prints each file it names whole (a whole print, toward
orientation only) when it is `cat` (with any options, so `cat -n a` counts),
or in a `powershell` command `Get-Content`, `gc`, `type`, or `cat` (an
alias of `Get-Content` there), with none of `-TotalCount`, `-Head`,
`-First`, `-Tail`, or `-Last` (`PS_RANGE_PARAMS`), each by any prefix of its
name as PowerShell takes it (`-Tot 5`, `-T 5`), and when:

- the command fails whenever it fails: it sits in the command's trailing
  `&&` chain, with only `&&` or a later pipe after it, since after a `;`,
  `||`, or newline another command sets the exit status
  (`cat a || true`, `cat a; echo ok`);

- its output goes neither into a pipe (`cat a | head`) nor into a file or
  null device; a redirect of standard error alone leaves it a print
  (`cat a 2>/dev/null`);
- it runs outside any compound command, group, or substitution, and not as
  a background job (`cat a &`);
- its folder is known: from where the command started, or after a `cd` the
  core can follow (see `_change_directory`), so `cd ./src && cat a.py`
  prints `src/a.py`, while after `cd src; ` or a bare `cd src`, which Bash
  may resolve through `CDPATH`, the file cannot be named and does not count.

`cat a b c` prints three files. A word the shell expands (holding `$`, a
backtick, `%`, `*`, `?`, `[`, `{`, or `(`, or opening with `~`) names no
one file and does not count, so `cat *.py` prints none whole; a value of
`-ErrorAction`, `-WarningAction`, `-OutVariable`, `-ErrorVariable`, or
their aliases names no file. `head`, `tail`, `sed`, `grep`, `less`, and
every other command print none whole, nor does `type` in a `posix` command,
which describes commands. A relative path is taken from the session's
folder, so `cat src/a.py` and a `file_read` of the same file's absolute path
are one file. A failed command, or one still running or run in the
background, prints nothing. The core reads it as `whole_prints` in
`shell.py`.

#### File Prints

A simple command prints each file it names, whole or in part (a file
print, toward orientation's five distinct files only; round 6's R3), on
the same terms as a whole print, when it is a whole print, or:

- `head` or `tail`, in either shell, with any options;
- `sed` with `-n`, `--quiet`, or `--silent`, alone or in a cluster such as
  `-ne`, and no `-i`, naming its files after its script, or after each
  `-e` value when it has one (`sed -n 1,40p a.py`, `sed -n -e 1p a b`).
  `sed` without `-n` prints every line, edited, and does not count, nor
  does a script that may write a file: one with a `w` or `W` command or
  flag followed by a space or its end (`sed -n '1w out' a`,
  `sed -n 's/a/b/w out' a`), or one read from a file (`-f`);
- in a `powershell` command, `Get-Content`, `gc`, `type`, or `cat` with a
  range parameter (`Get-Content a -TotalCount 30`, `gc a -Tail 5`).

Each command part counts its own files, so
`sed -n 1,40p a && sed -n 40,80p b` prints two. A search that prints
matching lines (`grep`, `rg`, `Select-String`, and every command not named
here) prints no file. A file printed or read by the `file_read` call, with
or without a range, counts toward the five only when its path, as written,
reads as under a project folder: no link is resolved and no `~` or Git
Bash mount expanded for it, and only a Windows short name is (see
`actions.reads_as_in_project`). The three whole reads count any file, as
before. The core reads it as
`file_prints` in `shell.py`.

### Package Installs And Setup Files

The Setup item is met by a package install or a setup file write in the
turn, a subagent's included.

A **package install** is a finished `npm`, `pnpm`, or `bun` `add`,
`install`, or `i`, `yarn add`, `pip` or `pip3` `install` (also
`python -m pip`, `python3 -m pip`, or `py -m pip`, with `-m pip` as the
first two arguments), `uv add`,
`uv pip install`, `uv tool install`, `poetry add`, `pipx install`,
`conda install`, `cargo add` or `install`, `go get` or `install`,
`gem install`, or `brew`, `apt`, `apt-get`, `winget`, `choco`, or `scoop`
`install`, or `yarn global add`, that names a package. A bare
`npm install`, `pip install -r requirements.txt`, or `pip install -e .`
restores what a manifest records or installs a local path, so it does not
count; a URL, such as `pip install -e git+https://…`, is a package. Each
manager's options that take a value (`--filter`, `--workspace`,
`--python`, `--file`, `--prefix`, `--registry`, `--index-url`, `--target`,
and the like; `PACKAGE_MANAGERS` in `shell.py`) are skipped with their
value, so `pnpm install --filter web` names no package.

A **global, machine, or per-user install** (`npm`, `pnpm`, or `bun` with
`-g` or `--global`, `npm --location=global`, `pip install --user`,
`yarn global add`, `uv tool install`, `pipx install`, `cargo install`,
`go install`, `gem install`, every `brew`, `apt`, `apt-get`, `winget`,
`choco`, or `scoop` install, and any install run under `sudo`;
`GLOBAL_INSTALLS` and `GLOBAL_OPTIONS` in `shell.py`) counts wherever it
runs. Any other package install counts unless it goes into a folder
certainly outside the project. That folder is the one a folder option names
(`npm --prefix`, `pnpm --dir` or `-C`, `yarn` or `bun --cwd`,
`uv --project` or `--directory`, `poetry -C` or `--directory`, `go -C`;
`FOLDER_OPTIONS` in `shell.py`), else the one it runs in, following a `cd`
as a write target does (see [Shell Reading](#shell-reading)). So
`cd /tmp/x && pip install requests` does not count,
`cd /tmp/x && npm install --prefix <project> lodash` does, and so does one
after a `cd` the core cannot follow (`cd "$TMPDIR" && …`, `cd sub && …`).

A **setup file** is `.env` or `.env.*` (`.env.example` included), or an
editor or agent settings file: a `settings*.json` directly in a folder named
`.claude/` or `.vscode/`, in any case, written by a file
write or a shell command (`SETUP_FILE_RE` in `actions.py`). It counts only
inside the project, so a scratch folder's settings do not, and neither do
settings under the home folder, unless the project holds it.

A file write to `.env.example`, `.env.sample`, or `.env.template`, in any
case, that only adds, removes, or edits comment lines (`#` first, past any
spaces) and blank lines is no setup (round 7, R9; `EXAMPLE_ENV_FILES` in
`actions.py`): each edit's replaced text must hold the same other lines,
trailing space aside, as the text it writes. A setting line added,
removed, or changed there, a commented-out setting turned on, a whole-file
write, an edit that does not show its text, and a shell write still count,
and so does any change to `.env` itself or another `.env.*` file.

Two limits: an install inside `bash -c "…"` or another wrapped command
string is not seen, as with every shell reading here; and an install whose
failure the command hides (`npm install foo || true`) still counts, since
the core sees only the whole command's result.

### Design Reference Signals

`software-design-principles` names, for each moment of a change, which
reference to read. The `design` and `design-reads` gates enforce those reads
where the skill counts as loaded, judged from the edit itself
(`design_reads.py`): no line the agent writes declares them. A file edit
that selects a reference lands, and the reference is owed to the closeout's
Reads item ([Holds](#holds)); which references a signal selects does not
depend on whether the edit lands. They apply to
an edit of a code file, or of a configuration file (`.yaml`, `.yml`,
`.toml`, `.json`, `.env`, `.env.*`, `settings.*`) that is neither a lock
file (`*-lock.json`, `pnpm-lock.yaml`, `npm-shrinkwrap.json`) nor test
data, so `stack/fixtures/x.yaml` and `a/__fixtures__/b.json` select
nothing.

Signals are judged on what the edit adds: the lines of its added text that
its removed text did not hold, indentation aside. A whole-file write over a
file on disk is compared with that file. A definition whose name the removed
text already defined, as in a signature change, is not new. Comments and
docstrings are left out of the code the error and concurrency signals read,
so `# try the cache, then raise` selects neither. Three quotes that close a
multi-line string the edit shows opening (as [Registry Reference
Signals](#registry-reference-signals) states) open no docstring.

A **small edit**, one writing fewer than five lines (every line of the text
it writes, unchanged context and a trailing newline's empty line included;
`DESIGN_MIN_LINES` in `actions.py`), or a [comment-only edit](#comment-only-edits)
writing fewer than twenty (`COMMENT_EDIT_MIN_LINES`), selects no reference by the kind of
file or text it touches: no `decoupling.md` for a configuration file or the
third code file, and no `readability.md` for a comment or docstring. A test
file has its own rule, for `coding.md` only: the edit must create the file
or add twenty or more lines, an added line being one of its added text that
its removed text did not hold (spec R9), and not a case-data line in a file
the edit does not create (round 5, K2; [Registry Reference
Signals](#registry-reference-signals) defines one). The registry states it, as the
`tdd` signal for `test-design.md` (see
[Registry Reference Signals](#registry-reference-signals)), and the core
reads it from there, so both references follow one rule. With no registry,
or none declaring an `edit-of-file-kind` signal for `test` files, any test
edit that is not small selects `coding.md`, failing toward holding. Outside
test files, the signals read from the added code apply at any size: a new
code file or public top-level definition, error handling, and concurrency.
An edit whose added lines cannot be counted, such as one whose text the call
does not show, is not small.

| Reference | Selected when the edit |
| --- | --- |
| `process.md` | creates a code file (a whole-file write, or an edit marked `creates`, to a code file no earlier write in the turn made and that is not on disk), or adds a public top-level definition to a code file: an unindented line starting with the word `def`, `class`, `function`, `export`, `func`, `fn`, `public`, `interface`, `struct`, `enum`, `trait`, `impl`, or `defmodule`; with `async` before `def`, `function`, or `fn`; or with `pub`, or `pub(...)` such as `pub(crate)`, then any of the qualifiers `const`, `async`, `unsafe`, `default`, `inline`, or `extern` (with an ABI string such as `extern "C"` or without), before `fn`, `struct`, `enum`, `trait`, `type`, `const`, `static`, `mod`, `union`, `impl`, `extern`, or `var` (`DEFINITION_START_RE` in `design_reads.py`), whose name, its first word that is not a keyword, a string literal, or the path in a `pub(...)` visibility, does not start with `_` and was not defined in the text the edit replaced. A shell `export NAME=` is not one, nor is `async` alone, `async () => run()`, or `async_helper = 1`, and `pub use x;` and `pub extern crate x;` re-export and define nothing. A configuration file defines nothing, so a YAML key such as `class: foo` is not one |
| `complexity-and-modules.md` | the same as `process.md` |
| `decoupling.md` | is not small, and edits a configuration file or is to the third or later distinct non-test code file the turn edits |
| `readability.md` | the same as `process.md`, or is not small and adds a comment or docstring: a line opening with `#`, `//`, `/*`, `*`, `"""`, `'''`, `-- `, or `<!--`, a line inside a docstring or block comment, or a trailing `#` or `//` comment after two spaces. A comment on an edit adding little code selects nothing (round 5, K1): an edit, comment-only or not, whose written text holds fewer than five code lines and fewer than twenty comment lines, read as a [comment-only edit](#comment-only-edits) is (blank lines are neither; a line with a trailing comment is code; unchanged context the text repeats counts; `written_line_counts` in `design_reads.py`). So three code lines with a two-line comment select no `readability.md`; five code lines with a comment, or three with twenty comment lines, or a comment-only edit writing twenty comment lines, do. The `design` gate keeps its own size rule, so the three-plus-two edit is still substantial there. A file of a language whose comments the core does not read, or text it cannot read for certain, is judged by its size alone |
| `errors.md` | adds code holding `try`, `except`, `catch`, `raise`, `throw`, `finally`, `defer` as words, or `with open` |
| `coding.md` | edits a test file and creates it or adds twenty or more lines, case-data lines in a file it does not create left out, by the registry's rule above; a test file selects nothing else |
| `concurrency.md` | adds code holding `threading`, `Lock`, `RLock`, `Mutex`, `asyncio`, `synchronized`, `Promise.all`, a word starting `Atomic`, or `go func` |
| `differences.md` | never selected: no call shows two rules pulling apart, so the registry declares it advisory |

`red-flags.md` is not among them: the closeout's Design item asks for it. A
reference counts as read after a whole read of a path ending in
`software-design-principles/references/<file>`. A shell command printing
one does not count. A typical change, one new public function with a
docstring and error handling, its caller, and its test, requires five:
`process.md`, `complexity-and-modules.md`, `readability.md`, `errors.md`,
and `coding.md`.

The first substantial non-test code edit of a turn meets `design`, which
asks for what is missing: the load and the reads. A test file never triggers
`design` and is not counted when finding the turn's first such edit: in TDD
the test comes first and the design happens in the code after it. A later
edit, or any test file edit once the skill counts as loaded, meets
`design-reads`, which asks only for reads and names each file and what
selected it. A small edit while the skill does not count as loaded is not
held. The skill's section ids and its Section Index name sections for
navigation; no hold asks for a citation of them.

#### Comment-Only Edits

An edit whose added and removed text is only comments and docstrings does
not move the change point the Design item's red-flags read must follow, so
fixing a comment the red-flags scan found does not reopen the item
(`comment_only` in `design_reads.py`). The rules err toward a change:

- The comment syntax comes from the file's extension. `#` comments: `.py`
  and `.pyi` (with three-quote docstrings), `.rb`, `.sh`, `.bash`, `.zsh`,
  `.pl`, `.r`, `.ps1`, `.psm1`. `//` line comments and `/* */` blocks: `.c`,
  `.h`, `.cc`, `.cpp`, `.cxx`, `.hpp`, `.cs`, `.java`, `.js`, `.jsx`, `.mjs`,
  `.cjs`, `.ts`, `.tsx`, `.go`, `.rs`, `.swift`, `.kt`, `.kts`, `.scala`,
  `.dart`. No edit of any other file is comment-only. So `#define` or
  `#[derive]` in a C-family file, and `a // 2` in Python, are code.
- Each removed text must hold the same code lines, indentation included, as
  the added text replacing it, once comments are left out: a whole line
  opening with the line marker, a `/* */` block with nothing after its
  close, a docstring line opening with three quotes with nothing after its
  close, and a trailing comment after two or more spaces (`x = 1  # note`).
- Text it cannot read for certain counts as a change: a quote before a
  trailing comment, a lone three-quote line (a fragment cannot say whether
  it opens or closes a docstring), code after a block's or docstring's
  close, and any code line holding three quotes or a backtick, which may
  open a string spanning lines. A line opening with `*` outside a block it
  saw is code.
- Each removed text and the added text replacing it must end in the same
  state: a `/* */` block or docstring left open at the end of one and not
  the other comments out, or back in, the code after the edit
  (`/* note */` to `/* note`, `# a` to `"""a`, or the reverse). A docstring
  left open on both sides (`"""Return x.` to `"""Return x, capped.`) is
  still comment-only.
- A directive comment, one that changes what a tool does, is code, kept
  whole: a comment whose text, its markers left out, opens with one of
  `DIRECTIVE_PREFIXES` in `design_reads.py` (`//go:`, `// +build`, `@ts-`,
  `eslint-`, `# type:`, `noqa`, `pragma`, `pylint:`, `#!`,
  `/// <reference`, and a doctest's `>>>`). This holds wherever
  `comment_only` is read, the design gates' small comment edits included.
- A whole-file write, even of a file that is now only a comment, an edit
  whose text is not shown, and a shell write always count as a change.

A comment-only edit writing fewer than twenty lines, counted as for a small
edit, is no design change at all (round 4, R3): it is small for `design` and
`design-reads`, so it is not substantial and its comment selects no
`readability.md`, and the Design item does not count it, so a turn whose
code changes are all such edits meets no Design item. A comment-only edit of
twenty or more lines is still substantial, and it makes the Design item
needed, though it does not move its change point. It selects
`readability.md` only when it writes twenty or more comment lines, by the
count every edit's comment is judged by (round 5, K1; the `readability.md`
row of the design references table).

A comment-only edit of any size is already proved, so it does not make
the Proof item needed (round 5, R7). Docs and every other step still count
it as a change: a docstring is documentation, and durable docs may repeat
it.

### Registry Reference Signals

Every skill's entry in the registry, `stack/goated-stack.yaml`, lists each
file under its `references/` folder with a signal that makes its read
required, or `advisory` with the reason no signal fits; the registry schema
and [`fixtures/reference-reads/README.md`](fixtures/reference-reads/README.md)
own the shape. The `reference-reads` gate enforces those signals for the
skills that count as loaded (`reference_reads.py`); a file edit that fires
one lands owing the reference, as [Holds](#holds) states.

The core reads the installed registry on each write. It judges each write
inside the project: a file write, and each file a shell command names as
written when some command in it writes and is not a check, as the
`repeated-failure` gate counts writes (`pytest > out.txt` is not judged),
and only when the command's folder is known. A write the gate cannot place
in the project, such as `git apply fix.patch`,
`cd $DIR && echo x > tickets/a.md`, or a file outside the project, meets
only the `gate-fires` signals. The edit kinds read the code a write adds, so
they fire only for a code file written by a file write:

| Kind | Fires when the write |
| --- | --- |
| `edit-adds-pattern` | adds code matching the named pattern, in a file of `file_kind` when the signal gives one. Comments and docstrings are left out, as for the [design signals](#design-reference-signals) |
| `edit-of-file-kind` | is of a file of `file_kind` and adds at least `min_added_lines` lines, or, with `new_file: true`, creates the file: a whole-file write, or an edit marked `creates`, to a file no earlier write in the turn made and that is not on disk. In a file the write does not create, and when the write adds no test or function definition line (`def`, `async def`, `func`, `fn`, `function`, or an `it(`, `test(` or `describe(` call, indented or not; `TEST_DEFINITION_RE`), an added **case-data line** does not count (round 5, K2): one whose code, comments left out, holds only string and number literals, `True`, `False`, `None`, `true`, `false`, `null`, `nil`, brackets, commas, colons, a keyword argument written `name=` with no spaces before a literal, and the case wrappers `pytest.param(` and `param(`, with at least one bracket or comma, as a row inside a list or call has. A line of only brackets, commas and spaces, such as `],` or `([`, is never one. So 24 new rows such as `(1, "one", True),` or `pytest.param(2, id="two"),` appended to an existing list count none, while a new test function counts every line, and `expected = 5`, a statement `flag=True`, `(make(1), 1),`, a row with `marks=` such as `pytest.param(1, marks=pytest.mark.slow),`, an f-string row, and a comment line still count (`_is_case_data` in `reference_reads.py`). A known limit: literal arguments of a multi-line call added inside an existing test body, with no new definition line, may still read as case data and go uncounted. The `design-reads` gate judges a test edit for `coding.md` by the registry's one such signal for `test` files (`validate_skills.py` refuses a second), so one rule decides both |
| `write-under-path` | is of a file under the `path` folder of the project, case aside: the file's path below a project folder starts with it. So with `docs/specs/`, `docs/specs.md` does not fire it, and a `tickets/` folder outside the project never does. Each project folder counts: from a session working in the checkout's root, `src/docs/specs/x.md` does not fire it, but from a session working in `src/`, that folder is a project folder too, so it does |
| `gate-fires` | comes while the named gate's condition holds, whether or not that gate holds the write: its own skill may be loaded. The core observes `repeated-failure` only (`OBSERVED_GATES`), whose condition is one check failed twice in a row with no pass since. The schema allows any gate name, so `validate_skills.py` fails on an entry naming another; an installed registry that names one anyway asks for nothing by it |
| `sensitive-category-count` | is to a [security-sensitive](#security-sensitive-paths) file inside the project while the turn's changes to such files, its subagents' included and this write counted, span at least `min_categories` categories |

An edit adds the non-blank lines of its added text that its removed text did
not hold, indentation aside; a whole-file write over a file on disk is
compared with that file. So changing one line among four unchanged ones adds
one line, a new four-line file adds four whatever its trailing newline, and
a line the removed text already held, such as an existing mock, is not
added. A shell write meets only the signals that need no added text.

The named patterns are the registry's `reference_patterns`, as the core
matches them; so `dispatch` holds no patch, and `retrieve` no retry.
`mock-or-patch` skips what each quoted string on the added line holds (`"`,
`'`, or a backtick, a backslash escaping the next character), so
`assert kind == "patch"` and `name = 'MagicMock'` match nothing. Where the
line's strings cannot be read for certain, the whole line is matched: a
quote left open, three quotes in a row, a string holding `${`, `#{`, or
`\(`, one with an `f`, `t`, `$`, or `$@` prefix holding `{`, or, outside a
`.py` or `.pyi` file, one holding `$` before a name (`"$fakeRepo"`). In a
`.rs`, `.c`, `.h`, `.cc`, `.cpp`, `.cxx`, `.hpp`, `.cs`, `.java`, `.go`,
`.kt`, `.kts`, `.scala`, or `.swift` file, `'` opens only a char literal
(`'x'`, `'\n'`), and any other `'`, such as a Rust lifetime (`&'a MockDb`),
leaves the line unread; a file whose place in the project is unknown is read
as no such language (`_without_strings` in `reference_reads.py`). A line
inside a string the edit shows opening on an earlier line is skipped whole:
in a `.py` or `.pyi` file, three quotes right after an `=`, a bracket, a
`,` or `:`, or `return` or `yield` (`CONFIG = """`, `dedent('''`) and not
closed on that line; in a `.js`, `.jsx`, `.mjs`, `.cjs`, `.ts`, or `.tsx`
file, a backtick likewise (a template literal). So `[providers.fake]` and
`fake = true` in TOML inside one match nothing. Three quotes opening a line
start a docstring, already left out, and quotes after other text open
nothing, since they may close a string whose opening the edit does not
show; a line the edit shows without its string's opening is read as above.
The line that closes the string is read as above, and so is a line inside
one that may hold code: `{` in an `f` or `t` string, `${` in a template
literal. After a line holding such code and the closing quote, which may
nest a string, no later line of the edit counts as inside one
(`_read_lines` in `design_reads.py`). A hold
names the matched word and stops at a call's parenthesis
(`"patch.object"`). `sleep-retry-or-timeout` matches inside strings too:

| Pattern | Matches |
| --- | --- |
| `mock-or-patch` | outside quoted strings: a word starting `mock`, `stub`, `spy`, or `fake` (either case), `sinon`, `monkeypatch.setattr`, `monkeypatch.delattr`, or `monkeypatch.context` before `(` (a patch of code, so a `monkeypatch` parameter, `monkeypatch.setenv(`, and `monkeypatch.chdir(` match nothing), a word ending `Mock` (`MagicMock`), `jest.fn`, or `vi.fn`; and `patch` only as a call or decorator: `@patch`, or the word `patch` before `(` or `.<name>(` (`patch(`, `mock.patch(`, `patch.object(`), so `patch = load_diff()` and `apply_patch(diff)` match nothing |
| `sleep-retry-or-timeout` | in any case: a word holding `sleep`, `timeout`, `retry`, `retries`, `retried`, or `retrying` (`asyncio.sleep`, `setTimeout`, `MAX_RETRIES`); `poll`, `polls`, `polled`, `polling`, or `poller` at the end of a word or before an underscore or a capital (`poll_interval`, `pollInterval`); `wait_for` or `waitFor` likewise at a word start (`waitForSelector`, `wait_for_element`); or `setInterval` |

So the first enforced set is: `tdd`'s `mocking-and-seams.md` when a test
edit adds a mock or patch, at any size, and its `test-design.md` at a test
edit creating the file or adding twenty or more lines; `diagnose`'s
`condition-based-waiting.md` when an edit adds a sleep, retry, or timeout,
and its `root-cause-tracing.md` at a write after one check failed twice;
`code-security-review`'s `security-review-checklist.md` at a sensitive write
once the turn's sensitive changes span two categories; `write-a-spec`'s
`spec-template.md` before a write under `docs/specs/`; and
`spec-to-tickets`'s `ticket-slicing-templates.md` before a write under
`tickets/`. The registry's other `write-under-path` entries (`docs/adr/`,
`docs/setup/`, `docs/wayfinding/`, `docs/agents/external-docs/`) are
enforced the same way.

A reference added to the registry later is enforced with no core change, as
long as it names a pattern, file kind, and gate listed here. References
declared `existing-rule` keep their own gates (`design-reads`, `spawn`, and
the closeout), and `spawn-with-brief` asks for nothing yet.

A reference counts as read after a whole read of a path ending in
`<skill>/references/<file>`. A shell command printing one does not count,
nor does a file of the same name under another skill. A skip line naming the
skill, or the override `skip <skill>`, clears that skill's references for
the turn. A skill that does not count as loaded is not asked for its
references. When one write fires references of two skills, the hold names
them all and offers a skip line for each.

### Change Reads

A change read must follow the last change its step covers. For every step
that asks for one, a read before the skill load counts: a diff read, then a
`commit-message` or `standards-and-spec-review` load with no change between,
needs no second read. The Design step alone also orders the change read
after its red-flags read.

| Step | The change read must follow |
| --- | --- |
| Docs | The last code change |
| Design | The red-flags read and the last code change that is not [comment-only](#comment-only-edits); after a red-flags read that follows five or more changed lines, later changes adding fewer than five lines in total need no second red-flags read, only this change read after them, counted as the Design item counts them, so an edit's unchanged context lines add none. A red-flags read before any such change covers no later change, and a change whose added lines are unknown, a shell write or a subagent's, counts as five or more |
| Security | The last change to a security-sensitive file |
| Commit | The last change to code that is not a [comment-only edit](#comment-only-edits), or to a [security-sensitive file](#security-sensitive-paths) of any kind (a CI workflow, a manifest, a key or env file), including those a subagent spawned in the turn made; in a turn with no such change, any change read in the turn counts. So any other change to a file that is not code, or a comment-only edit, made after a change read keeps it (the maintainer's choice V2, 2026-11-19), while a turn whose only change is a doc still needs one. A diff chained before the commit in the same command has not run, so it never counts |
| Pull request, pull-request review | The last change to any project file, code or not, including changes a subagent spawned in the turn made |
| Review | The last code change |

A change read is one of:

- a command that prints the changes' content to the agent: `git diff`,
  `git show`, a patch log (`git log` or `git whatchanged` with `-p`, `-u`,
  `-U<n>`, `--unified`, `--patch`, `--patch-with-stat`, or
  `--patch-with-raw`),
  `git stash show -p`, `git format-patch --stdout`, `gh pr diff`, or
  `glab mr diff`, under any wrapper or through a pipe (`git diff | head`), or
  with standard error redirected (`2>err.txt`). A listing of names or counts
  does not count: `--stat`, `--shortstat`, `--numstat`, `--dirstat`,
  `--compact-summary`, `--summary`, `--name-only`, `--name-status`, `--raw`,
  `--check`, `-s`, or
  `--no-patch`, unless a patch option asks for the patch too. Neither does
  `--quiet`, `--output` or `--output=<file>`, or standard output redirected
  into a file (`> change.patch`, `1>out.txt`) (`GIT_PATCH_FLAGS_RE`,
  `GIT_NO_PATCH_FLAGS`, `GIT_SILENT_FLAGS_RE`, and `FORGE_DIFFS` in
  `shell.py`);
- a file read, whole or partial, of a file the turn changed (any project
  file, code or not). In a turn that changed no file it can name, such as a
  commit of an earlier turn's work, only a printed diff can count, and the
  hold says so.

A command whose result is not `ok` does not count, so a diff with
`--exit-code`, which exits 1 when there are changes, is not a change read.
Only git and the `gh` and `glab` diffs are read: another version control
system's diff is not seen. A skip line, where the item accepts one, a skill
override, and a commit message the person typed still clear each hold
without a change read.

A change read can be met by a token read, such as a diff piped through
`head -1`: the rule puts the change in front of the agent, it does not prove
the agent reviewed it. Some forms are counted although they print nothing to
the agent, because the analysis sees the diff but not where its output ends
up: `> /dev/null`, `| Out-Null`, `| wc -l`, `| cat > file`, and
`x=$(git diff)`.

### Content Checks

Only text in the call is checked, and only for what the skill's contract
states plainly enough to test without judgement (`contracts.py`):

- **Commit message.** When the commit carries the message inline (`-m`,
  `--message`, a short-flag cluster such as `-am`, the heredoc fed to that
  commit's `-F -`, a heredoc in `-m "$(cat <<'EOF' … EOF)"`, or a PowerShell
  here-string), or a `commit` call carries it in `message`, it needs a
  non-empty subject of at most 72 characters, a blank line before any body,
  and no credential-shaped token. A message in a file (`-F <path>`), reused
  from another commit (`-c`, `-C`), or from an editor is not checked.
- **Spawn brief.** The brief needs, as Markdown headings, the sections its
  template keeps even for an agent that inherits the conversation: `Goal`,
  `Scope`, `Done Means`, and `Report Back` for `handoff`'s spawn brief, so
  that every brief asks for a report as the other two do; `Task`,
  `Ownership`, and `Required Report Format` for the implementer prompt;
  `Review Mode`, `Review Inputs`, and `Required Report Format` for the
  reviewer prompt. A brief passes when it matches a template whose skill
  counts as loaded and whose reference was read whole since the last
  compaction. A spawn with an empty brief, or of a `read_only` agent, meets
  no `spawn` check at all: no template load or read, headings, or skills
  line.
- **Skills line in a brief.** Every spawn brief, including one a person may
  start later, also needs a skills line naming the skills the new agent
  should read before it starts: `goated-skills: <skill>, <skill>`, or
  `goated-skills: none: <reason>` with a reason of three words or more. A
  skill is named by its installed name, bare or with a namespace
  (`goated:tdd`). Like a route line, the line counts only on its own line
  outside code blocks, bare or in one pair of backticks; it may also be a
  `- ` or `* ` list item. `handoff`'s `references/spawn-brief.md` defines
  the line, and the implementer and reviewer prompts carry it. A brief is
  held when it has no such line or its line is malformed, and the hold names
  the problem: a missing line, no skill named, none with too short a reason,
  none mixed with names, an empty or malformed name, a capitalised prefix, or
  no space after it. Whether the named skills are the right ones, and whether
  the agent reads them, is not checked.

### Hold Text

The [Hold Messages](#hold-messages) rules, as the core's text meets them
(`wording.py`, and each gate's text in `actions.py` and `gates.py`):

- A hold's skills are backticked by bare name, and the grammar's words
  appear backticked only inside a whole line such as
  `goated-skip: <skill>: <reason>`. Each closeout item names the skill it
  asks for, backticked or as the skill of the skip line it offers, so a
  measurement tool can count the item through that skill; the Review item
  names the reviewer prompt by its path, so it counts through
  `standards-and-spec-review`. The two design items share the `Design`
  label.
- A hold asks for a load only when the skill does not count as loaded.
  Inside a subagent, where only its current turn counts, it asks for the
  load or read in this turn.
- A hold or closeout item that asks only for a change read once its skill
  has loaded names the skill without backticks, or only in its skip line:
  the commit, pull-request, and pr-review holds name no skill (pr-review's
  skip line is not backticked either), and the closeout offers the skill
  only as a skip line. Once `software-design-principles` has loaded, the
  `design` hold (asking for reads) and the `design-reads` hold name it only
  in their skip line, and backtick each reference by its path,
  `software-design-principles/references/<file>`.
- The `reference-reads` hold names each skill only in its skip line, since
  the skill is already loaded, and backticks each reference by its path
  under the skill, `<skill>/references/<file>`.
- A hold that a route or skip line can clear says the line may be put where
  the harness keeps it, and that the person can type the matching override.
  The full advice is given on one such hold per turn and agent; every other
  gives one sentence. A message with several such holds gives it once, in
  its closing clearing section: in full when the turn has not had it, else
  in one sentence (`gates.shown_holds`, `wording.clearing_section`).
- A paragraph several holds or closeout items share appears once in a
  message: the change-read explanation (a later copy says to print the diff
  or read a changed file), the sentence about rerunning steps chained before
  a held command, the sentence that a read made in parallel does not count,
  and the closeout's rule for skip lines.
- A short `Still unmet:` hold names what is still missing and every
  constraint needed to clear it, such as what does not count as a change
  read, the lines that broke the route grammar, or a typed message that
  stands a commit down. An ask is the gate and what is unmet, so a gate's new
  ask, such as a change read after a load, comes in full the first time. The
  closeout judges each item apart: an item the turn has not yet shown comes
  in full under the full opening (`Before finishing this turn, which changed
  code:`); when every item it lists was shown before, it opens
  `Still unmet before finishing this turn:` (or `committing in`) and lists
  them short, keeping a commit's rules about chained steps and checks. The
  next turn starts full again.
- Both Design red-flags texts repeat the question `red-flags.md` ends with;
  no hold reads an answer.
- The `route-line` hold quotes each line of the turn that does not match
  the grammar with why, in the words of the marker fixtures' `why`
  (`markers.malformed_reason`): a whole route line with more text after it
  is "nothing may follow the line", and with only punctuation after it "no
  trailing punctuation".
- A routing hold on a shell command whose every simple command is named as
  a [plain read](#plain-reads) (a read command, `cd`, or `git`) but which is
  none names the first part that made it none, such as the redirect into a
  file, a background job, a refused argument, or a wrapper before the
  command (`shell.ShellCommand.write_part`). A posix redirect into `nul`
  gives its own note instead.
- When a write of the turn landed owing reads, the `commit` hold's change
  read asks for the owed references first and the change after them, since
  the Reads item counts only a read of the file made after them; one read
  in that order meets both.
- The `commit` hold's change read says to make the read in an earlier
  message than the commit, since a read sent in the commit's own message
  has not finished when the commit is judged and cannot count for it
  (round 7, R10). The `pull-request` and `pr-review` holds keep their
  wording.
- The `scripted-edit` hold, and a `design` or `design-reads` hold on a
  shell write, carry a slot for what the harness's file edit tools and
  shell do to a file's line endings (`wording.LINE_ENDINGS`; round 7, R6),
  since agents script edits to keep CRLF. The core's neutral words leave it
  empty; an adapter fills it only with what it has checked of its own
  harness. The Claude Code adapter says that the Edit tool keeps a file's
  line endings, so CRLF is no reason to use a script, and that `sed -i` in
  Git Bash can strip CR from a file (both checked on 2026-11-23). A hold on
  a file edit tool's write carries no slot.
