# Ticket 124: Skill Text, Closeout Skills And Real-Data Checks

## Parent Spec

`docs/specs/2026-11-23-hook-friction-round-7.md` (R7, R12; AC8)

## Type

AFK. Decisions D9 and D11 (the maintainer, 2026-11-23).

## What To Build

Two wording changes in installed skills, with no adapter or core change.

- **Closeout skills out of `requires:` (R7).** The router's output
  contract (`using-goated-ai-skills`) and the spawn-brief template
  (`handoff`'s `references/spawn-brief.md`) say that `doc-sync`,
  `standards-and-spec-review`, `verification-before-completion` and
  `setup-scribe` are met at the closeout. They do not go in a route's
  `requires:` or a brief's skills line just because the task will need
  them later. `code-security-review` may still be listed, since it
  applies while writing. Keep the router within its word budget.
- **A real-data check (R12).** `verification-before-completion` gains one
  line: when a feature depends on runtime data, such as a profile, a
  configuration or a model, exercise it against the owner's active data,
  not only fixtures.

If a changed file is a registered reference, or the router's skill map or
fixtures quote the changed text, update `stack/goated-stack.yaml` and
`stack/fixtures/` in the same change.

## Recommended First Reads

- The parent spec: R7 and R12, and the Problem items on closeout skills
  in routes and on the defect found only on the walk-through.
- `skills/agent-workflows/using-goated-ai-skills/SKILL.md`: Output
  Contract.
- `skills/agent-workflows/handoff/references/spawn-brief.md`: the skills
  line and route line rules.
- `skills/README.md`: frontmatter, required sections and the line cap.

## Acceptance Criteria

- [ ] The router and the spawn-brief template carry the closeout-skills
      sentence, naming the four skills and the `code-security-review`
      exception.
- [ ] `verification-before-completion` carries the real-data line.
- [ ] The validator and the context comparison pass, and the router stays
      within its budget.
- [ ] The repo checks in `AGENTS.md` pass.

## Expected Proof

- The repo checks in `AGENTS.md`, including the context comparison.
- A manual read of each changed paragraph against the spec.

## Blocked By

- None.

## Scope Exclusions

- Any change to the `pipeline` gate (decision D9, wording only).
- Lines about driving a UI in a browser or recounting stated numbers (not
  chosen).
- Syncing installed copies: the lead does that after merging.

## Closeout

Completed, merged and archived on 2026-11-23.

- Merged as `1d7f40b` (`d8e1591`, with review fix `f80f61e`).
- Review fix: the closeout skills may still be listed when the task is
  that skill's own work, such as a review.
- Implementer decisions: four router passages were tightened to stay
  within the word budget, which is now full; a guardrail in
  `verification-before-completion` that repeated its Purpose was removed;
  `spawn-brief.md` gained a Contents section.
- Reviewed by one reviewer agent before merge. Installed copies synced
  after the merge.
