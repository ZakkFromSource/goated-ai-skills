---
name: resolving-merge-conflicts
description: Use when an in-progress Git merge, rebase, cherry-pick, or revert has conflicts that must be resolved from the intent behind both sides.
metadata:
  goated-category: engineering
---

# Resolving Merge Conflicts

## Purpose

Resolve active Git conflicts by preserving the reason behind each change, not
by mechanically choosing ours or theirs.

Use this skill only for an operation already in progress. End with either an
evidence-backed resolution ready for an authorized lifecycle action, an
explicit semantic decision, or a safe stop or abort recommendation.

## Inputs

- User request, current repository, active approval mode, and allowed action
  reach.
- Git status, operation metadata, unmerged paths, index stages, and relevant
  history.
- Commits, pull requests, issues, tests, docs, changelogs, or other primary
  evidence for the intent of both sides.
- Project instructions and commands for checks scoped to the resolved paths.

## Dependencies

Hard:
- an in-progress Git merge, rebase, cherry-pick, or revert with inspectable
  conflict state

Soft:
- local history and connected issue or pull-request sources for intent evidence
- project test, type, lint, format, build, or validation commands
- `diagnose` when a resolved conflict exposes a separate failure whose cause is
  unclear
- `verification-before-completion` when the resolution is complex,
  multi-surface, delegated, high-risk, or explicitly audited

Fallback: When history, remote metadata, checks, or companion skills are
unavailable, use the strongest local evidence, state the gap, and stop before
guessing intent or performing an unauthorized lifecycle action.

## Workflow

1. **Establish the operation and boundary.**
   - Inspect read-only state first, normally with `git status`,
     `git diff --name-only --diff-filter=U`, and `git ls-files -u`.
   - Identify the actual operation from Git's state, such as `MERGE_HEAD`,
     rebase state, `CHERRY_PICK_HEAD`, or `REVERT_HEAD`. Do not rely on the
     user's label alone.
   - Record the current branch or detached state, operation, source commits,
     exact unmerged paths, partially resolved paths, staged changes, unrelated
     dirty changes, and applicable instructions.
   - If no supported operation is active, the operation differs materially
     from the request, the wrong branch or commits are involved, or the state
     is unsafe or unauthorized, stop before editing.

   This phase is complete when the active operation and exact conflict scope are
   identified or the mismatch is reported.

2. **Build two-sided intent evidence.**
   - For each conflict, inspect the base and both index stages where available,
     the surrounding file, and the commits that introduced each side.
   - Label the sides by commit and intent. Git's `ours` and `theirs` labels can
     be misleading during rebases, so do not treat them as product meaning.
   - Trace each side to the strongest available primary evidence: commit and
     patch, linked pull request or issue, test, specification, documentation,
     migration, or user decision.
   - Confirm the evidence is current and authoritative for the relevant intent
     or decision scope. Preserve stale sources as context, not as controlling
     intent.
   - Distinguish facts from inference. A nearby code shape or conflict-marker
     position is not enough evidence of intent.

   This phase is complete when each side has a concise intent statement and
   source reference, or the evidence gap is explicit and resolution has
   stopped.

3. **Classify the semantic relationship.**
   - **Compatible:** both intents can hold together without changing either
     contract. Plan the smallest combined resolution.
   - **Incompatible:** satisfying one intent defeats or changes the other.
     State the tradeoff and obtain the required user or product decision unless
     current, authoritative primary evidence within the relevant decision scope
     already settles it.
   - **Unrelated or under-evidenced:** the conflict contains behavior outside
     the operation's goal or lacks enough evidence. Stop rather than inventing
     a third behavior.
   - Urgency or permission to finish the operation does not replace missing
     intent evidence.
   - Treat delete/modify, rename/rename, generated files, lockfiles, migrations,
     schemas, permissions, and security-sensitive conflicts as semantic work,
     not automatic text selection.

4. **Resolve only the evidenced scope.**
   - Edit one coherent conflict at a time. Preserve every compatible intent and
     established invariant with the smallest understandable change.
   - Remove conflict markers and inspect the full resolved unit, not only the
     marked lines. Search the affected path set for remaining markers.
   - Preserve unrelated dirty and staged changes. Do not rewrite adjacent code,
     regenerate broad outputs, or change public behavior unless the evidence
     and request require it.
   - Do not stage yet. A clean working-tree conflict file is evidence for
     review, not permission to change the index.

   This phase is complete when every edited conflict is marker-free, maps back
   to recorded intent evidence, and has no unresolved semantic decision.

5. **Discover and run scoped proof.**
   - Derive checks from project instructions, manifests, nearby tests, CI, and
     the changed file types. Prefer the smallest checks that exercise both
     preserved intents, then broaden in proportion to risk.
   - Inspect diffs and unmerged status again. Separate failures caused by the
     resolution from pre-existing or unrelated failures.
   - Do not weaken tests or checks merely to make the operation continue.

   This phase is complete when scoped checks pass, or failures and proof gaps
   are reported without a readiness claim.

6. **Choose the next lifecycle action.**
   - Loading this skill authorizes no stage, commit, continue, skip, abort,
     push, force operation, or protected-branch mutation.
   - Check whether current user consent covers the exact action, paths,
     operation, and repetition scope. Request fresh authorization when it does
     not.
   - After an authorized continue, inspect state again: a rebase or
     cherry-pick sequence may expose a new commit, conflict set, or semantic
     decision. Reuse only evidence and consent that still apply.
   - Safe abort is a valid outcome when the operation is wrong, unsafe,
     unauthorized, or too under-evidenced to continue. Explain consequences
     and obtain authorization before executing it.
   - Commit and push remain separate actions. Never infer them from permission
     to resolve, stage, continue, or abort.

Read [Pressure Scenarios](references/pressure-scenarios.md) when evaluating or
revising this skill, or when time, authority, sunk-cost, or completion pressure
encourages a shortcut.

## Output Contract

Return a compact resolution record containing:

- detected operation, source commits, current branch state, and exact conflict
  scope;
- intent and primary evidence for both sides of each conflict when the evidence
  phase was reached, or the earlier stop and why it prevented tracing;
- compatible resolutions made, incompatible decisions required, and evidence
  gaps;
- files edited, remaining unmerged paths, scoped checks and results when those
  phases were reached, or `not attempted` with the stopping reason;
- lifecycle actions already authorized or performed, if any; and
- exactly one next state: `ready-for-authorized-action`, `decision-required`,
  `evidence-required`, `abort-recommended`, or `blocked`.

Do not report `ready-for-authorized-action` while conflicts, semantic
decisions, failed required checks, or authorization uncertainty remain.

## Delegation

Main owns operation detection, scope, consent, semantic decisions, integration,
Git lifecycle actions, and user communication.

Delegate only non-overlapping intent tracing, conflict inspection, or scoped
check discovery. Return paths, commits, evidence, intent, assumptions,
uncertainty, commands, and findings. The main agent reviews every result before
editing or acting. Without delegation, perform the same passes sequentially.

## Guardrails

- Do not use whole-file ours/theirs selection as a substitute for intent
  analysis.
- Do not equate Git stage labels with feature ownership, especially in a
  rebase.
- Do not guess from conflict markers, timestamps, branch names, or whichever
  side currently passes one test.
- Do not invent compromise behavior when intents are incompatible.
- Do not discard unrelated working-tree or index changes.
- Do not run destructive cleanup, reset, checkout, restore, skip, abort,
  continue, commit, push, force, hook, or installer actions without applicable
  authority and exact targets.
- Do not claim success from marker removal alone.
- Do not require the GOATED source repository, its root files, registry,
  fixtures, or private session state after installation.

## References

- [Pressure Scenarios](references/pressure-scenarios.md) - read for skill
  evaluation or when pressure makes semantic or lifecycle shortcuts likely.
- Public inspiration:
  [mattpocock/skills resolving-merge-conflicts](https://github.com/mattpocock/skills/tree/main/skills/engineering/resolving-merge-conflicts).
  This port preserves intent tracing and scoped checks while replacing
  always-resolve and automatic-lifecycle behavior with evidence, safe-stop, and
  authorization gates.
