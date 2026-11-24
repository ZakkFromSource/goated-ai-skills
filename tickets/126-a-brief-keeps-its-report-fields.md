# Ticket 126: A Brief Keeps Its Report Fields

## Parent Spec

None. This ticket follows ticket 125
(`tickets/archive/125-every-brief-asks-for-a-report.md`) and comes from a
diagnosis on 2026-11-24, recorded under Background below. The maintainer
asked for both changes the same day.

## Type

AFK. Decisions R1 and R2 (the maintainer, 2026-11-24).

## Background

Ticket 125 made every handoff spawn brief keep a `Report Back` heading, and
the spawn hold holds a brief without one. A delegated ticket session started
after that change still ended without the structured report: no `Status`
line, no Changed paths, no Tests section.

The cause was traced in that session's transcript:

- The brief was written after ticket 125 was merged and the installed copies
  were synced. It had a `## Report Back` heading, so the hold let it through.
- Under the heading the lead wrote one prose line that listed field names
  ("Status, branch and commits, paths changed, checks run … and checks
  skipped"). It dropped the template's nine labelled lines and the four
  status values.
- The template allows this: "Drop sections and lines that carry nothing for
  this task" covers lines inside Report Back, and the hold checks only the
  heading.
- The session followed the vague request and wrote a tidy report with no
  labels.
- The session's own explanation blamed `verification-before-completion`'s
  output block. That block is not the missing format: the missing one is the
  implementer report (`Status: DONE_WITH_CONCERNS`, Task completed, Changed
  paths, Tests, Checks, Concerns, Recommended next step).

Nothing outside the brief asks a started session for the report, so a weak
brief is enough to lose it.

## What To Build

- **R1: the report section keeps its Status line.**
  - Every brief template with a kept report section (`Report Back` in
    `handoff`'s spawn brief, `Required Report Format` in the implementer and
    reviewer prompts) already opens it with a `Status` line naming `DONE`,
    `DONE_WITH_CONCERNS`, `NEEDS_CONTEXT` and `BLOCKED`.
  - The spawn hold treats a brief whose report section lacks a `Status` line
    naming all four values as not written from the template, the same way it
    treats a brief that lacks the heading. Judge the line the way the other
    kept parts are judged (outside code blocks, under that heading).
  - The hold text says what is missing: the report section's `Status` line
    and its four values, and that the section is copied as written.
  - `spawn-brief.md` says to copy Report Back as written; its "drop sections
    and lines" sentence no longer reaches lines inside Report Back.
- **R2: a started session ends with the report.** The shared policy's
  Communication And Closeout section gains one sentence: an agent started
  from a brief ends its final report with that brief's report fields as
  labelled lines, starting with `Status`. State it as the exception to "no
  skill closeouts", since the report is the requested result.
  - Keep `stack/AGENTS.md` within any size limit the validator or tests set.

The rule lives in the shared core's brief templates and spawn check, under
`adapters/core/goated_core/`. The contract's spawn gate, its "Spawn brief"
rule and Hold Messages, and conformance scenarios under
`stack/fixtures/enforcement/` change in the same change. The adapter's text
fixture is regenerated with
`uv run --no-project --with pyyaml --with jsonschema python tests/test_skill_usage_mod.py --write`.

## Recommended First Reads

- `tickets/archive/125-every-brief-asks-for-a-report.md`, whole.
- `skills/agent-workflows/handoff/references/spawn-brief.md`, whole.
- The Required Report Format sections of
  `skills/engineering/subagent-driven-development/references/implementer-prompt.md`
  and `reviewer-prompt.md`.
- `adapters/core/goated_core/contracts.py`: `BriefTemplate`,
  `HANDOFF_TEMPLATE` and `BRIEF_TEMPLATES`.
- The spawn hold in `adapters/core/goated_core/actions.py`, and how a
  brief's headings are found.
- `stack/enforcement-contract.md`: the spawn gate, "Spawn brief", and Hold
  Messages.
- `stack/AGENTS.md`: Communication And Closeout.
- `stack/fixtures/enforcement/handing-on.yaml`.

## Acceptance Criteria

- [x] A handoff brief with a `Report Back` heading but no `Status` line
      naming the four values is held by `spawn`. The hold text names the
      missing line.
- [x] The same brief with the template's `Status` line starts, even when it
      drops other Report Back lines.
- [x] Implementer and reviewer briefs are held the same way when their
      Required Report Format lacks the `Status` line, and start with it.
- [x] A `Status` line inside a code block, or under another heading, does
      not count.
- [x] `spawn-brief.md` says to copy Report Back as written.
- [x] `stack/AGENTS.md` asks a started agent to end with its brief's report
      fields as labelled lines, starting with `Status`.
- [x] The contract states the rule, and conformance scenarios cover holding,
      clearing, and the near misses above.
- [x] Existing briefs in fixtures and tests that lack the `Status` line gain
      it.
- [x] The repo checks in `AGENTS.md` pass, and so does `claude plugin test .`
      in `adapters/claude-code/skill-usage`.

## Expected Proof

- The conformance scenarios through the core and the example translator.
- The Claude Code adapter's spawn tests through its hook, and its generated
  text fixture.
- The skill-usage mod's tests.
- The repo checks in `AGENTS.md`.

## Blocked By

- None.

## Scope Exclusions

- Checking the report itself at the end of a delegated session.
- Requiring Report Back lines other than `Status`.
- Changing the verification skill's activation, the Verification closeout
  item, or how the router lists closeout skills. The diagnosed session
  suggested these. They are separate from the report format; the router rule is ticket
  124's decision.
- Syncing installed copies: the lead does that after merging.
