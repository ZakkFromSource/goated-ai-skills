# Ticket 125: Every Brief Asks For A Report

## Parent Spec

None. This ticket comes from a diagnosis on 2026-11-24, recorded under
Background below. The maintainer chose both decisions the same day.

## Type

AFK. Decisions R1 and R2 (the maintainer, 2026-11-24).

## Background

Delegated ticket sessions in a target project stopped ending with a
structured report: Status, Task completed, Changed paths, Tests, Checks,
Concerns and Recommended next step. They now end in plain prose.

The cause was traced in the session transcripts:

- Until 2026-11-23, the lead session wrote each ticket brief from
  `subagent-driven-development`'s `references/implementer-prompt.md`. That
  template ends with a Required Report Format, and its sessions reported in
  that shape.
- From 2026-11-23, a new lead session loaded `handoff` and wrote its briefs
  from `references/spawn-brief.md`.
  - 19 of its 20 ticket briefs left out the template's Report Back section,
    which the template lets a brief drop ("Drop sections and lines that
    carry nothing for this task").
  - The sessions started from those briefs had no report format, so each
    ended in prose.
  - The one brief that kept Report Back was written after a hold had made the
    lead read the template again.
- The spawn hold enforces a report section for the implementer and reviewer
  templates, whose kept headings include Required Report Format. The
  handoff template's kept headings are only Goal, Scope and Done Means.
- Nothing in round 7 caused this. The briefs without a report predate the
  ticket 124 merge, and ticket 124 did not change Report Back.

## What To Build

- **R1: a spawn brief always asks for a report.**
  - Report Back becomes a section that `spawn-brief.md` always keeps, like
    the skills line. The template's "drop sections" sentence says so.
  - The spawn hold treats a brief from the handoff template that lacks a
    Report Back heading as not written from the template, the same way it
    already treats an implementer brief that lacks Required Report Format.
  - The hold text that names the template's headings names Report Back too.
- **R2: the report asks for the implementer prompt's fields.** Report Back
  in `spawn-brief.md` asks for the same fields as the implementer prompt's
  Required Report Format:
  - `Status` (`DONE`, `DONE_WITH_CONCERNS`, `NEEDS_CONTEXT` or `BLOCKED`);
  - task completed or attempted;
  - changed paths and paths inspected;
  - commands run and their results;
  - tests added or updated, and test results or behaviour proof;
  - assumptions and concerns;
  - skipped checks or unavailable evidence;
  - self-review notes;
  - the recommended next step.

  Keep the wording short enough that the template stays readable, and keep
  `handoff` within the validator's word budget.

The rule lives in the shared core's brief templates, under
`adapters/core/goated_core/`. The contract's spawn gate and Hold Messages
sections, and conformance scenarios under `stack/fixtures/enforcement/`,
change in the same change. The adapter's text fixture is regenerated with
`uv run --no-project --with pyyaml --with jsonschema python tests/test_skill_usage_mod.py --write`.

## Recommended First Reads

- `skills/agent-workflows/handoff/references/spawn-brief.md`, whole.
- `skills/agent-workflows/subagent-driven-development/references/implementer-prompt.md`:
  its Required Report Format.
- `adapters/core/goated_core/contracts.py`: `BriefTemplate` and
  `BRIEF_TEMPLATES`.
- The spawn hold in `adapters/core/goated_core/actions.py`, where it names
  the template's headings, and how a brief's headings are checked.
- `stack/enforcement-contract.md`: the spawn gate, its "Spawn brief"
  rule, and Hold Messages.
- `tickets/archive/071-spawn-briefs-name-skills.md` and
  `tickets/archive/107-core-a-reviewer-starts-work.md`, for how brief
  templates and their kept headings were set.

## Acceptance Criteria

- [ ] `spawn-brief.md` keeps Report Back always and asks for the fields in
      R2. Its "drop sections" sentence names Report Back beside the skills
      line.
- [ ] A spawn whose brief has Goal, Scope, Done Means and a skills line but
      no Report Back heading is held by `spawn`. The hold text names Report
      Back among the headings to add.
- [ ] The same brief with a Report Back heading starts. Implementer and
      reviewer briefs are judged as before.
- [ ] The contract states the rule, and conformance scenarios cover holding,
      clearing, and a near miss (a Report Back heading inside a code block,
      or under another level, judged the way the other kept headings are).
- [ ] The adapter's text fixture shows the new heading list.
- [ ] The repo checks in `AGENTS.md` pass, and so does `claude plugin test .`
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

- Steering ticket work to the implementer prompt in the router. Its word
  budget is full, and R1 gives every template a report anyway.
- Checking the report itself at the end of a delegated session.
- Changing the implementer or reviewer templates.
- Syncing installed copies: the lead does that after merging.
