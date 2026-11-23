# Hook Friction Round 7 Delivery Order

Source spec: `docs/specs/2026-11-23-hook-friction-round-7.md`

The maintainer chose every decision on 2026-11-23 and asked for three
tickets: closely related changes share a ticket and are phased inside it,
for one agent each.

1. `tickets/122-core-reviews-kept-across-small-follow-ups.md`
   - Status: Ready. Decisions D1, D2, D4, D5, D6 and D7.
   - Blocked by: None.
   - Overlaps: the contract and the scenario files with 123, and the
     closeout note (122 changes how often it is given, 123 its order).
   - Enables: no Review or Verification re-ask for small follow-ups on a
     reviewed branch; briefs without a route line spared Review; notices
     given once.
2. `tickets/123-core-narrower-triggers-and-hold-texts.md`
   - Status: Ready. Decisions D3, D8 and D10.
   - Blocked by: None.
   - Overlaps: as above with 122.
   - Enables: no security hold on a conversation `session`, plain reads
     with backslashes in quotes, no Setup ask for example-env comments,
     and the four hold-text changes.
3. `tickets/124-skill-text-closeout-skills-and-real-data.md`
   - Status: Ready. Decisions D9 and D11.
   - Blocked by: None.
   - Overlaps: none.
   - Enables: routes and briefs without closeout-time skills in
     `requires:`, and the real-data check.

## Waves

- Wave 22: 122, 123 and 124 in parallel.

## Merge Notes

- Merge 122 or 123 first, then the other, keeping both sides' contract
  rows and scenarios.
- Regenerate the adapter's text fixture after the second core merge:
  `uv run --no-project --with pyyaml --with jsonschema python tests/test_skill_usage_mod.py --write`.
- Run the skill-usage mod's tests (`claude plugin test .` in
  `adapters/claude-code/skill-usage`) on the integration.
- After 124 merges, sync the installed router, `handoff` and
  `verification-before-completion` copies; after 122 or 123, sync the
  stack files they change.

## Ready Frontier

- `tickets/122-core-reviews-kept-across-small-follow-ups.md`
- `tickets/123-core-narrower-triggers-and-hold-texts.md`
- `tickets/124-skill-text-closeout-skills-and-real-data.md`

## Coverage

- AC1, AC2 (a review stays met across small follow-ups) → 122
- AC3 (a skills line marks a brief) → 122
- AC4 (the skip notice once) → 122
- AC5 (the closeout note once) → 122
- AC6 (`session` beside an auth word) → 123
- AC7 (hold texts) → 123
- AC8 (skill text) → 124
- AC9 (backslashes in double quotes) → 123
- AC10 (comments in example env files) → 123
- AC11 (contract and scenarios) → 122 and 123
