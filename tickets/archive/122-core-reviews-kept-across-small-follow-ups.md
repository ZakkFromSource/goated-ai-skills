# Ticket 122: Reviews Kept Across Small Follow-Ups, And Notices Once

## Parent Spec

`docs/specs/2026-11-23-hook-friction-round-7.md` (R1 to R4; AC1 to AC5,
AC11)

## Type

AFK. Decisions D1, D2, D4, D5, D6 and D7 (the maintainer, 2026-11-23), and
the spec's three lead decisions. D1 reverses part of Ticket 069, under
which only a review in the same turn meets the Review item.

## What To Build

A reviewed large branch stops asking for Review and Verification on every
small follow-up. A session started from a brief is spared Review whether
or not its brief has a route line. Two notices stop repeating. One agent
can do this in three phases; each phase lands green.

- **Phase 1, the review point (R1).**
  - When the Review item is met or declined in a turn, record a review
    point: the branch size, measured as the item already measures it. The
    item can be met by a reviewer agent, by the `standards-and-spec-review`
    load with a change read, or declined by a Review skip line.
  - In a later turn, the Review item is met while the branch has grown by
    fewer than 50 changed lines of non-test code since the point. At 50
    or more it is asked again, and meeting it records a new point.
  - Verification gets its own point, set by a
    `verification-before-completion` load or skip line, under the same
    rule. The rule applies only when branch size is the trigger. A `full`
    route, a subagent's code change and a sensitive file still ask in each
    turn.
  - Both points are saved with the session's facts, survive a compaction,
    and end when a new task's route replaces the current task.
- **Phase 2, a skills line marks a brief (R2).** A session whose first
  prompt is a brief from another session (the event model's `brief` flag)
  with a valid `goated-skills:` line is briefed for the Review item, as
  one with a route line is today. The orientation rule for briefed
  sessions still needs the brief's route line.
- **Phase 3, notices once (R3, R4).**
  - The `skip_carried` notice is given once per task for each gate, skill
    and file kind it names.
  - The turn's closeout note is given once per task while its list of
    items is unchanged. A turn whose list differs gets it again.

The rules live in the shared core at `adapters/core/goated_core/`. The
contract's Closeout Items, Branch Size, Prompts, Turns, And Tasks, and
Notices sections, and conformance scenarios under
`stack/fixtures/enforcement/`, change with the code.

## Recommended First Reads

- The parent spec: R1 to R4, the matching Problem items, and the
  Decisions, including the lead decisions.
- `stack/enforcement-contract.md`: Closeout Items, Branch Size (its last
  paragraphs say a review counts only in its own turn), Notices, and
  Prompts, Turns, And Tasks (briefed sessions).
- `tickets/archive/069-adapter-closeout-review-and-verification.md` and
  `tickets/archive/101-core-read-skips-last-the-task.md` (lasting skips and
  the `skip_carried` notice).
- In `adapters/core/goated_core/`: the Review and Verification items and
  the lasting-skip notice in `actions.py`, the briefed flag in `gates.py`
  and `state.py`, and the closeout note in `judge.py`.

## Acceptance Criteria

- [ ] On a large branch, a turn that meets Review by a load and a change
      read is followed by a turn adding 20 code lines that is not asked
      for Review. A turn that brings the growth since the point to 50
      lines is asked.
- [ ] The same holds with a Review skip line as the point, with a
      compaction between the turns, and for Verification with a load or
      skip as its point.
- [ ] A new task's route ends both points.
- [ ] A `full` route, a subagent's code change or a sensitive file still
      asks for Verification in each turn.
- [ ] A session whose first prompt is a brief with a skills line and no
      route line meets no Review item on a large branch, and is still held
      for orientation as today. A typed first prompt with a skills line is
      not a brief.
- [ ] Three writes that one lasting skip lets through carry one
      `skip_carried` notice; a write let through for another file kind
      carries its own.
- [ ] Two turns with the same closeout list give the note once; a third
      turn that adds an item gives it again.
- [ ] Saved state from before this change loads without error.
- [ ] The contract states each rule, and conformance scenarios cover each
      change for holding, each way it clears, and a near miss.
- [ ] The repo checks in `AGENTS.md` pass.

## Expected Proof

- The conformance scenarios through the core and the example translator.
- The core's closeout, state and notice tests; the Claude Code adapter's
  tests through its hook, including its generated text fixture.
- The skill-usage mod's tests, if notice counts it shows change.
- The repo checks in `AGENTS.md`.

## Blocked By

- None. Ticket 123 changes other parts of the core but also edits the
  contract and the scenario files; whichever merges second resolves the
  overlap.

## Scope Exclusions

- The 400-line threshold for a large branch.
- The declined-holds notice (not changed, by decision).
- Orientation for briefs without a route line.
- Reading a background check's result when it arrives (deferred).
- Hold text other than the new wording these rules need: Ticket 123 owns
  the other text changes.

## Closeout

Completed, merged and archived on 2026-11-23.

- Merged as `e773862` (`2945386`, with review fixes `6114172`).
- Implementer decisions: growth is a difference of branch sizes, so a
  rewrite of lines already changed, or a switch to a branch of about the
  same size, is not caught (stated in the contract); a load from an earlier
  turn counts for Verification only through its point; the closeout note's
  record is per task and a compaction keeps it.
- Review fixes: a turn that changes no code also records the Review point
  when it meets Review; a `branch_grows` scenario step proves the 50-line
  boundary for both items; the closeout note's check compares item labels
  only, in order.
- Accepted gap: with the review skill loaded in an earlier turn, a later
  no-code turn that only prints a diff counts as a review.
- Reviewed by one reviewer agent before merge. Installed copies synced
  after the merge.
