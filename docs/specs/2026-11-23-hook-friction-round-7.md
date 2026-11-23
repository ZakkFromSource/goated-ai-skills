# Hook Friction Round 7

## Status

Delivered, 2026-11-23: Tickets 122 to 124 are merged and archived. The maintainer chose an option for every
decision in a brainstorm on 2026-11-23 ([Decisions](#decisions)). Three
details were settled by the lead while writing this spec, and each is
marked as such. Builds on [the round 6 spec](2026-11-19-hook-friction-round-6.md):
every rule change is made once, in the shared core at
`adapters/core/goated_core/`, and stated in
[the enforcement contract](../../stack/enforcement-contract.md). Tickets
122 to 124 ([order](../../tickets/hook-friction-round-7-order.md)).

## Mode

Compact.

## Problem

Two ticket sessions in another project reported on the holds after round
6 had shipped. One used a free-form report, the other a blank template
with the same headings. Their ratings, from 1 (poor) to 5 (excellent):

| Dimension | First session | Second session |
| --- | --- | --- |
| Efficiency | 3 | 2 |
| Effectiveness | 3 | 3 |
| Effect on output quality | 4 | 3 |
| Distraction (5 means never) | 3 | 2 |
| Clarity of hold messages | 3 | 4 |
| Fit of the skills loaded | 3 | 3 |

Both kept the commit-time checks and the red-flags question, which found
two real defects in the first session. Both said the cost came from how
often the asks repeat, not from their wording.

The usage log from round 6's merge to 2026-11-23 covers 22 sessions over
87 hours. Twenty of the sessions are in one project, so the log shows how
often each problem happens, not whether it is specific to that project.

| Measure | Value |
| --- | --- |
| Holds | 163 |
| Skip lines | 176 |
| Commit holds answered | 29 of 29 |
| Closeout holds declined with skip lines | 14 of 25 outcomes |
| Security holds declined | 6 of 8 |
| Sessions asked the Review item twice or more | 6 (15 asks) |
| Route lines naming a closeout-time skill in `requires:` | 6 |
| Skip lines for `software-design-principles` | 79 |
| Of those, on a shell call that writes files from a script | 77 |

Each complaint below was checked against main at `c0bf7d3` by reading the
code, the log and the two transcripts.

- **Review and Verification return on every later turn of a large
  branch.** Once a branch has 400 or more changed lines of non-test code
  against its base, each turn that changes code asks for the Review and
  Verification items again, unless something in that turn meets them. In
  the second session the review was done once. Five later commits of 1 to
  20 lines of CSS, each after a passing quick check, were asked again
  while the owner walked through the work. Every ask was declined.
- **A brief without a route line doesn't count as a brief.** A session
  whose first prompt is a brief with a route line meets no Review item,
  since the session that started it reviews the work. The spawn-brief
  template requires a skills line but leaves the route line optional. The
  second session's brief had a skills line and no route line, so the
  session counted as unbriefed, and that caused the Review asks above.
- **The same notices repeat.** The "an earlier skip line let this write
  through" notice appeared 15 times in six minutes in the first session.
  The turn's "closeout will ask for…" note repeats on every short turn of
  a walk-through.
- **`session` is read as an auth word.** A one-line import into
  `runtime/session.py` was held for a security review. In a chat app, a
  session is a conversation. The log has 5 such holds across 3 sessions,
  all declined.
- **A backslash in double quotes makes a read into a write.** A read-only
  `grep "a\|b"` was held by `router-first`. Both reports and the lead's
  own session hit it.
- **Agents script their edits to protect line endings.** 77 of the 79
  design skip lines rode on shell scripts that write files. The first
  session scripted its edits because it feared the Edit tool would change
  CRLF line endings. The Edit tool keeps them; Git Bash's `sed -i` strips
  them (both checked on 2026-11-23), and it did so in the second session.
- **Closeout-time skills listed in a route hold the first write.** The
  router says a route's `requires:` skills load before the first write.
  Briefs and route lines list `doc-sync` and other closeout skills there,
  so the `pipeline` gate held the first code edit until `doc-sync` loaded,
  hours before any docs work.
- **Small asks with no finding.** The Setup item fired on a commented line
  added to `.env.example`. The commit hold doesn't say that a diff read
  in the commit's own message cannot count. The pointer to the project's
  context documents (round 6, R13) sits on the last line of a long note,
  and the first session's agent missed it.
- **The biggest defect came from neither hook nor check.** In the first
  session, the chat offered four gestures that the avatar's profile left
  out. The owner found this on the walk-through. No check had exercised
  the feature against the owner's real profile.

## Goals

- A small follow-up on a reviewed large branch isn't asked for Review or
  Verification again.
- A session started from a brief is spared the Review item, whether or
  not its brief carries a route line.
- Each notice says something new.
- The security, read-only and Setup triggers stop matching the cases
  above.
- Agents use the Edit tool rather than scripts to keep line endings.
- Routes and briefs stop listing closeout-time skills as skills to load
  first.
- Verification asks for a check against real data where a feature
  depends on it.

## Non-Goals

- Kept from the feedback: the red-flags question, the separate change read
  before a commit, the scripted-edit hold, and the single message per
  held commit.
- No change to the 400-line threshold that makes a branch large.
- The declined-holds notice and its retrospective suggestion stay in
  briefed sessions (not chosen).
- Script writes do not land and owe their design reads as Edit writes do
  (not chosen; the wording in R6 comes first).
- The `pipeline` gate is unchanged (R7 is wording only).
- A check for CRLF loss: that belongs to the project, such as
  `.gitattributes` or a test.
- Lines in `verification-before-completion` about driving a UI in a
  browser or recounting numbers the docs state (not chosen).
- The visual and interface design reference: still its own spec (round 6,
  Y3).

## Requirements

- **R1, a review stays met across small follow-ups** (decisions D1, D6
  and D7).
  - The **review point** is set when the Review item is met or declined
    in a turn: by a reviewer agent, by the `standards-and-spec-review`
    load with a change read, or by a Review skip line (lead decision).
  - After that point, the Review item is met in a later turn while the
    branch, measured as today, has grown by fewer than 50 changed lines of
    non-test code since then.
  - Verification has its own point, set when its item is met or declined
    (a `verification-before-completion` load or skip line), under the same
    50-line rule. This rule applies only when the trigger is branch size.
    The other triggers (a `full` route, a subagent's code, a sensitive
    file) are unchanged.
  - Both points are saved with the session's facts, survive a compaction,
    and end when a new task's route replaces the current task.
  - Once the branch grows by 50 lines or more, the item is asked again,
    and meeting it sets a new point.
- **R2, a skills line marks a brief** (decision D2). A session whose first
  prompt is a brief from another session, with a valid `goated-skills:`
  line, is briefed for the Review item, as one with a route line is today.
  The orientation rule for briefed sessions still needs the brief's route
  line (lead decision).
- **R3, the skip notice once** (decision D4). The `skip_carried` notice is
  given once per task for each gate, skill and file kind it names. Later
  writes that the same lasting skip lets through carry no notice.
- **R4, the closeout note once** (decision D5). The turn's closeout note is
  given once per task while its list of items is unchanged. A later turn
  whose list differs gets the note again, showing the new list.
- **R5, `session` only beside an auth word** (decision D3). A file name
  matches the auth category through `session` or `sessions` only when its
  path also has another word of the auth category, such as
  `auth/session.py` or `login_session.py`. Other auth words are
  unchanged.
- **R6, hold text on line endings** (decision D8). The `scripted-edit`
  hold, and a design hold on a shell write, say that the Edit tool keeps
  a file's line endings, so CRLF is no reason to use a script, and that
  `sed -i` in Git Bash can strip CR from a file.
- **R7, closeout skills out of `requires:`** (decision D9). The router's
  output contract and the spawn-brief template say that `doc-sync`,
  `standards-and-spec-review`, `verification-before-completion` and
  `setup-scribe` are met at the closeout, and do not go in a route's
  `requires:` or a brief's skills line just because the task will need
  them later. `code-security-review` may still be listed, since it applies
  while writing.
- **R8, backslashes in double quotes** (decision D10). Inside double
  quotes, the shell reader reads a backslash as POSIX does. It escapes only
  `$`, a backquote, `"`, `\` or a newline, and otherwise stays literal, so
  `grep "a\|b" file` is still a plain read.
- **R9, comments in example env files** (decision D10). A change that only
  adds, removes or edits comment lines in `.env.example`, `.env.sample` or
  `.env.template` does not meet the Setup item.
- **R10, the commit hold's change read** (decision D10). When a commit is
  held for its change read, the hold says to print the diff in an earlier
  message, since a read sent in the same message as the commit cannot
  count for it.
- **R11, the context documents first** (decision D10). Where the closeout
  note names the project's context documents (round 6, R13), that line
  comes first in the note.
- **R12, a real-data check** (decision D11). `verification-before-completion`
  gains one line: when a feature depends on runtime data, such as a
  profile, a configuration or a model, exercise it against the owner's
  active data, not only fixtures.

## Acceptance Criteria

- **AC1** (R1). On a large branch, a turn that meets the Review item by a
  load and a change read is followed by a turn adding 20 code lines: the
  later turn is not asked for Review. A further turn that brings the
  growth since the point to 50 lines is asked. The same holds with a
  Review skip line as the point, after a compaction between the turns,
  and for Verification with a load or skip as its point.
- **AC2** (R1). A `full` route, a subagent's code change or a sensitive
  file still asks for Verification in each turn, as today.
- **AC3** (R2). A session whose first prompt is a brief with a skills line
  and no route line meets no Review item on a large branch. It is still
  held for orientation as an unbriefed session is today. A typed first
  prompt with a skills line is not a brief.
- **AC4** (R3). Three writes that the same lasting skip lets through
  carry one `skip_carried` notice. A write let through by a skip for
  another file kind carries its own.
- **AC5** (R4). Two turns whose closeout lists are the same give the note
  once. A third turn that adds an item gives it again.
- **AC6** (R5). An edit to `src/runtime/session.py` meets no security
  hold. Edits to `src/auth/session.py` and `src/login_session.py` do.
- **AC7** (R6, R10, R11). The adapter's text fixture shows the
  line-ending sentence in the `scripted-edit` hold and in a design hold on
  a shell write, the earlier-message wording in the commit hold, and the
  context documents first in the closeout note.
- **AC8** (R7, R12). The router, the spawn-brief template and
  `verification-before-completion` carry the new text, and the validator
  and the context comparison pass.
- **AC9** (R8). `grep -n "^#\|^##" file` is a plain read; a command with
  a backslash-escaped `$(...)` inside double quotes is still not.
- **AC10** (R9). A comment-only change to `.env.example` meets no Setup
  item; adding a non-comment line, or a comment in `.env`, does.
- **AC11.** Every changed gate and closeout item has conformance scenarios
  for holding, each way it clears, and a near miss, and the contract
  states the new rule.

## Proof Surface

The conformance scenarios under `stack/fixtures/enforcement/`, run through
the example translator, and the core's unit tests. Hold texts are proved
through the adapter's generated text fixture. The skill text is proved by
the repo checks in `AGENTS.md`.

## Constraints

- A rule change, its contract text and a conformance scenario land in one
  change, as the maintainer contract requires.
- No new notice kind is planned. If a result shape or notice kind changes,
  bump the event model's whole-number version.
- The core stays pure: no harness detail enters it. R6's line-ending
  sentence is adapter wording for Claude Code; other adapters may word it
  for their own tools.
- R7 and R12 change installed skill files, so installed copies need
  syncing after they merge.
- The log never records a path, prompt text or file content.

## Decisions

The maintainer chose these on 2026-11-23; the lead decided three details
while writing this spec.

- **D1, keep a review across small follow-ups,** rather than measuring
  again from the review's commit, or keeping today's rule. This reverses
  part of Ticket 069, under which only a review in the same turn counts.
- **D2, a skills line marks a brief,** rather than requiring a route line
  in every brief, or keeping today's rule. Trade-off: a quick ad-hoc brief
  also skips Review.
- **D3, `session` only beside an auth word,** rather than dropping it, or
  keeping it.
- **D4 and D5, the skip notice and the closeout note once.** The declined-
  holds notice was not changed.
- **D6, under 50 lines,** rather than 100, or the large-branch threshold of
  400.
- **D7, the review point survives a compaction,** as the task's route does
  (round 6, R2).
- **D8, hold text only,** rather than also letting visible script writes
  land and owe their reads.
- **D9, wording only,** rather than changing the `pipeline` gate.
- **D10, all four small fixes.**
- **D11, the real-data line only.**
- **D12, three tickets:** core reviews and notices; core triggers and hold
  text; skill text.
- **Lead decisions:** a Review or Verification skip line also sets the
  point, since the 50-line rule bounds what it covers. R2 covers the Review
  item only, not orientation. R1 measures growth with the branch size the
  item already uses.

## Deferred

- From round 6, still open: reading a background check's result when it
  arrives (round 5's O2). The log has 19 Verification skip lines that
  wait on a background check.
- Data from more than one project. The next feedback round should include
  sessions from other projects, an orchestrator, and a docs or research
  task.

## Open Questions

None.

## Sources

- Two session reports and the lead's log pass, kept privately by the
  maintainer; the figures above are taken from them.
- [The enforcement contract](../../stack/enforcement-contract.md): "A
  Branch", Reviewer Agents, Notices, Security-Sensitive Paths, and the
  skills line in a brief.
- [The spawn-brief template](../../skills/agent-workflows/handoff/references/spawn-brief.md).
- [Ticket 069](../../tickets/archive/069-adapter-closeout-review-and-verification.md).
