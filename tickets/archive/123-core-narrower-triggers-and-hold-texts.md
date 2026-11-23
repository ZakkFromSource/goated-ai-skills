# Ticket 123: Narrower Triggers And Hold Texts

## Parent Spec

`docs/specs/2026-11-23-hook-friction-round-7.md` (R5, R6, R8 to R11; AC6,
AC7, AC9 to AC11)

## Type

AFK. Decisions D3, D8 and D10 (the maintainer, 2026-11-23).

## What To Build

Three triggers stop matching cases that hold nothing worth holding, and
four hold texts say what agents were missing. One agent can do this in two
phases; each phase lands green.

- **Phase 1, triggers.**
  - **`session` only beside an auth word (R5).** A file name matches the
    auth category through `session` or `sessions` only when its path also
    has another word of that category, such as `auth/session.py` or
    `login_session.py`. Other auth words are unchanged.
  - **Backslashes in double quotes (R8).** Inside double quotes, the shell
    reader reads a backslash as POSIX does: it escapes only `$`, a
    backquote, `"`, `\` or a newline, and otherwise stays literal. So
    `grep -n "^#\|^##" file` is a plain read, and an escaped `$(...)`
    inside double quotes still runs no command.
  - **Comments in example env files (R9).** A change that only adds,
    removes or edits comment lines in `.env.example`, `.env.sample` or
    `.env.template` does not meet the Setup item. `.env` itself, and any
    non-comment change, still does.
- **Phase 2, hold texts.**
  - **Line endings (R6).** The `scripted-edit` hold, and a design hold on a
    shell write, say that the Edit tool keeps a file's line endings, so
    CRLF is no reason to use a script, and that `sed -i` in Git Bash can
    strip CR. This is Claude Code adapter wording; it was checked on
    2026-11-23 (Edit kept CRLF on changed and new lines; Git Bash's
    `sed -i` turned every CRLF into LF). The core stays free of harness
    detail.
  - **The commit's change read (R10).** A commit held for its change read
    says to print the diff in an earlier message, since a read sent in the
    commit's own message cannot count for it.
  - **Context documents first (R11).** Where the closeout note names the
    project's context documents, that line comes first.

The rules live in the shared core at `adapters/core/goated_core/`. The
contract's Security-Sensitive Paths, Shell Reading, Package Installs And
Setup Files, Change Reads and Hold Text sections, and conformance
scenarios under `stack/fixtures/enforcement/`, change with the code. The
adapter's text fixture is regenerated (see the order file's merge notes).

## Recommended First Reads

- The parent spec: R5, R6 and R8 to R11, and the matching Problem items.
- `stack/enforcement-contract.md`: the sections named above, and Hold
  Messages.
- `tickets/archive/120-core-commit-time-holds-in-one-pass.md` (the test-code
  exemption from the auth and secrets categories) and
  `tickets/archive/121-hold-text-small-fixes-and-log-detail.md` (hold text
  that opens with its action; the context-documents pointer).
- In `adapters/core/goated_core/`: `SECURITY_CATEGORIES`, `SETUP_FILE_RE`
  and the Setup item in `actions.py`; the double-quote reader in
  `shell.py`; the commit hold's change-read text; the closeout note in
  `judge.py`. The adapter's wording lives under
  `adapters/claude-code/`.

## Acceptance Criteria

- [ ] An edit to `src/runtime/session.py` meets no security hold; edits to
      `src/auth/session.py` and `src/login_session.py` do.
- [ ] `grep -n "^#\|^##" file` is a plain read for `router-first`; a
      command with `"\$(rm x)"` is read as a literal, and one with
      `"$(rm x)"` is still not a plain read.
- [ ] A comment-only change to `.env.example` meets no Setup item; adding
      a non-comment line to it, or a comment to `.env`, does.
- [ ] The adapter's text fixture shows the line-ending sentence in the
      `scripted-edit` hold and in a design hold on a shell write, the
      earlier-message wording in the commit hold, and the context
      documents first in the closeout note.
- [ ] The contract states each rule, and conformance scenarios cover each
      changed trigger for holding, clearing and a near miss.
- [ ] The repo checks in `AGENTS.md` pass.

## Expected Proof

- The conformance scenarios through the core and the example translator.
- The core's shell, security, setup and hold-text tests; the Claude Code
  adapter's tests through its hook, including its generated text fixture.
- The skill-usage mod's tests (`claude plugin test .` in
  `adapters/claude-code/skill-usage`), since its texts come from the same
  fixture.
- The repo checks in `AGENTS.md`.

## Blocked By

- None. Ticket 122 changes the closeout note's frequency, and this ticket
  changes its order; whichever merges second resolves the overlap, and
  both edit the contract and scenario files.

## Scope Exclusions

- Judging security by the diff rather than the path (a larger change, not
  chosen).
- Script writes that land and owe their design reads (not chosen).
- A CRLF check of any kind.
- Other shell quoting forms, such as `$'...'`, unless a test shows the
  same bug there.

## Closeout

Completed, merged and archived on 2026-11-23.

- Merged as `04b8fe4` (`f455890`). The closeout-note overlap with ticket
  122 kept 122's once-per-task check with this ticket's order, so the
  context documents open the note.
- Implementer decisions: `session` is no longer an auth word, which
  behaves as "only beside another auth word" since that word matches on
  its own; the line-ending sentence is a wording slot the core leaves
  empty and the Claude Code adapter fills; the pull-request holds' wording
  is unchanged.
- Accepted gaps: session code named only with words such as `sso`, `saml`,
  `mfa`, `csrf` or `cookie` meets no security hold; an edit to a fragment
  after `#` inside a setting line of an example env file reads as
  comment-only.
- Reviewed by one reviewer agent before merge. Installed copies synced
  after the merge.
