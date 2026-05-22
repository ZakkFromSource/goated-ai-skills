---
name: commit-message
category: engineering
classification: portable
status: wip
description: Use when the user asks for a commit message, commit summary, git commit text, or closeout message for local changes.
triggers:
  - user asks for a commit message, commit summary, git commit text, or closeout message for local changes
  - implementation, review, doc-sync, or verification work is complete and the next step is committing
  - a target-project change needs a concise subject plus optional body explaining what changed, why, and what was verified
  - an agent needs to summarize staged, unstaged, committed, or supplied patch changes for a human-controlled commit
outputs:
  - single copy-pasteable command block combining `git add -- ... && git commit -m ...` for selected changes, or commit-only command when selected changes are already staged
  - commit message preview with an imperative subject and optional body that accurately summarizes the change
  - commit scope section listing included files and any not-included files with reasons
  - optional commit plan for obvious independent change groups
  - compact notes for verification evidence, skipped checks, scope warnings, unrelated-change notes, and private-detail sanitization
depends_on:
  hard: []
  soft:
    - session-start-progressive-disclosure before drafting from an unfamiliar target project
    - standards-and-spec-review before commit-message when spec fit or project standards remain unresolved
    - code-security-review before commit-message when trust boundaries, auth, user data, persistence, unsafe execution, or security-sensitive config changed
    - doc-sync before commit-message when behavior, interfaces, docs, standards, configuration, or tests may have drifted
    - verification-before-completion before drafting commit wording that claims completion, passing checks, synced docs, or review readiness
    - handoff after commit-message when unfinished work or residual risk should be preserved for a future session
  fallback: If companion skills, git metadata, specs, or verification evidence are unavailable, inspect the smallest relevant local evidence, state lower confidence, and avoid inventing intent or checks.
adapters:
  codex: usable
  claude-code: usable
  hermes: usable
  opencode: usable
  generic-agent: usable
---

# Commit Message

## Purpose

Draft clear copy-pasteable commit commands from the actual change set and its verified context. The message should help future readers understand what changed, why it changed, how it was checked, and what remains uncertain.

This skill is read-only. It prepares a shell-ready `git add -- ... && git commit -m ...` command for the user or a separate publishing workflow; it does not run staging, commit, push, tag, or publish commands.

## Inputs

- User request, issue, PRD, ticket, accepted plan, review summary, doc-sync report, or implementation notes.
- Target-project root path.
- Git status, staged changes, unstaged changes, untracked files, recent commits, branch context, or supplied patch.
- Relevant local diffs, file names, issue acceptance criteria, PRD requirements, ADRs, standards notes, and nearby docs needed to understand intent.
- Verification evidence such as tests, linters, formatters, manual checks, review gates, doc-sync results, skipped checks, or known failures.
- Target shell or shell constraints when message or path quoting is not cross-shell safe.
- Optional platform context such as pull request title, issue ID, CI result, or review thread when available and relevant.

## Workflow

1. Confirm the commit scope:
   - Identify the target-project root and whether the user requested a scope such as staged changes, unstaged changes, all working-tree changes, named paths, commits since a fixed point, or a supplied patch.
   - Use an explicit user scope when one is provided.
   - In git projects, inspect read-only status and summaries before drafting, using equivalents of `git status --short`, staged and unstaged diff stats, name-status output, and relevant hunk reads.
   - When staged changes exist, treat them as the primary scope unless the user explicitly asks for unstaged or all dirty files. Mention other dirty files as caveats or optional later groups.
   - Include untracked files in the scope decision. If they look relevant, inspect them directly because normal diffs may not show their contents.
   - Do not mutate the index, working tree, branches, remotes, tags, or issue state.

2. Resolve messy working trees:
   - When no scope is explicit and the dirty tree has obvious clusters, draft a multi-commit plan instead of one blended message.
   - Treat separate issue or PRD work, separate skill folders, archive moves, and unrelated docs updates as likely cluster boundaries.
   - Pair deleted issue files with matching `issues/archive/...` files in the same group.
   - Keep support docs in a group only when they directly belong to that change.
   - If clusters are not obvious, draft one all-dirty commit and call out the risk that unrelated work may be combined.

3. Ground the message in intent:
   - Read the originating issue, PRD, ticket, user request, accepted plan, review notes, or doc-sync report when available.
   - Compare the requested intent with the changed files and diff behavior.
   - Separate primary behavior from supporting edits such as tests, docs, formatting, fixtures, or generated artifacts.
   - Note when the diff includes unrelated changes, partial work, unresolved acceptance criteria, or user changes that should not be summarized as this task.

4. Collect verification evidence:
   - Prefer actual command output, test results, review gates, CI summaries, and manual verification notes over assumptions.
   - Use `verification-before-completion` before including completion, correctness, passing, docs-synced, or review-ready claims in the commit body.
   - Record skipped or unavailable checks explicitly.
   - If no checks were run or provided, say so in the caveats instead of inventing confidence.
   - Treat platform-specific checks, pull request metadata, issue IDs, and CI context as optional aids, not required inputs.

5. Choose the command and message shape:
   - Use the project's existing commit style when it is discoverable from recent history or standards docs.
   - If no style is discoverable, default to a concise imperative subject without a prefix.
   - Keep the subject focused on the user-visible or maintainer-meaningful outcome, usually 72 characters or fewer when practical.
   - Add a body only when it helps: multi-part changes, non-obvious rationale, migration notes, verification details, caveats, or reviewer context.
   - Keep body paragraphs shell-safe and concise because each paragraph becomes an additional `-m` argument.
   - Rewrite unsafe wording before output instead of dropping command output. Prefer removing embedded quotes, backticks, shell metacharacters, and fragile punctuation from the subject/body.
   - For unstaged, untracked, deleted, or all-dirty scopes, prepare a single combined `git add -- ... && git commit -m ...` command that stages exactly the selected paths and commits only if staging succeeds.
   - For staged-only scopes, do not include a `git add -- ...` segment. State exactly: `No git add command needed; selected changes are already staged.`
   - Always prepare a `git commit -m "Subject"` command for each successful draft. Add body paragraphs with additional `-m "Body paragraph"` flags on the same physical command line.
   - When the user asks for a commit message, return the command block first. Do not make the user extract the usable command from notes, previews, or prose.

6. Sanitize public text:
   - Do not include secrets, tokens, private user data, sensitive logs, credentials, or ignored scratch content in commit text.
   - Avoid private client names, personal domains, internal handles, private URLs, or sensitive issue details unless they are already appropriate for the target project's public history.
   - If a change fixes exposure of sensitive material, describe the exposure class without repeating the sensitive value.
   - Prefer portable, project-local wording over hosting-platform jargon unless the project clearly uses that context in commit history.

7. Draft and self-check:
   - Ensure the subject matches the actual diff, not just the original plan.
   - Ensure the body does not claim checks, reviews, security coverage, or doc updates that did not happen.
   - Ensure known caveats are visible, especially skipped verification, unrelated changes, partial scope, generated files not inspected, or lower-confidence intent.
   - Keep verification notes and caveats outside the copy-pasteable command block.
   - Put selected staging and commit operations in one `Git Command` code block.
   - Put each command on its own single physical line; do not use shell-specific line continuations such as PowerShell backticks or Bash backslashes.
   - Use project-relative paths in the `git add -- ...` segment and quote paths that contain spaces or shell-sensitive characters.
   - If a safe combined command would be too long or hard to review, split the selected scope into separate named commit groups or state the blocker rather than hiding files or emitting unclear staging commands.
   - Ensure quote wrapping or escaping is safe for every command shown. When message quote safety is uncertain, rewrite the message into safe wording before omitting command output.
   - Omit command blocks only when a safe command cannot be produced after rewriting and path review; state the blocker plainly and provide the closest safe preview.
   - If the safest output is multiple commit groups, list them in the order the user should run them.

## Output Contract

Return copy-pasteable commands as the primary output. For a single clear unstaged, untracked, deleted, or all-dirty commit, start with one combined command block:

````markdown
## Git Command

```powershell
git add -- "path/or/group" && git commit -m "Subject" -m "Optional body paragraph"
```

## Commit Message Preview

```text
Subject

Optional body paragraph
```

## Commit Scope

Included files:
- `path/or/group`: reason included

Not included:
- None
````

For staged-only scope, state `No git add command needed; selected changes are already staged.` before the `Git Command` block and emit only:

````markdown
## Git Command

```powershell
git commit -m "Subject" -m "Optional body paragraph"
```

## Commit Message Preview

```text
Subject

Optional body paragraph
```

## Commit Scope

Included files:
- `path/or/group`: already staged and selected for this commit

Not included:
- None
````

Always include `Commit Scope` after the preview. Use `Included files` for paths selected for the command. Use `Not included` with `None` when there are no excluded dirty files, or list each excluded path with a reason such as unrelated dirty work, untracked scratch file, outside requested scope, already staged outside requested scope, or not inspected enough to safely include.

After the command block, preview, and scope, include compact notes only when they help the user avoid overclaiming or committing the wrong scope:

```markdown
Notes:
- Verification: <commands, checks, review gates, CI, manual verification, or "No verification evidence provided or run">
- Caveats: <skipped checks, unrelated changes, partial scope, assumptions, private-detail sanitization notes, or "None">
```

When the scope is ambiguous or contains unrelated change sets, return separate candidate command groups and name the scope each one covers before recommending a default. Keep every combined command directly copy-pasteable.

For obvious independent change groups, return a commit plan shaped like this:

````markdown
## Commit Plan

1. <Group name>
   - Rationale: <why these files belong together>
   - Git Command:
     ```powershell
     git add -- "path/or/group" && git commit -m "Subject" -m "Optional body paragraph"
     ```
   - Commit Message Preview:
     ```text
     Subject

     Optional body paragraph
     ```
   - Commit Scope:
     Included files:
     - `path/or/group`: reason included

     Not included:
     - <excluded dirty files with reasons, or "None">
   - Verification: <commands, checks, review gates, CI, manual verification, or "No verification evidence provided or run">
   - Caveats: <skipped checks, unrelated dirty files not included, uncertain grouping, shell-safety limits, or "None">
````

## Delegation

The main agent owns scope selection, final message wording, caveat judgment, and user communication.

When subagents are available, use them only for bounded evidence gathering, such as:

- summarizing changed files and diff intent for one source area;
- extracting acceptance criteria or rationale from a named issue, PRD, ticket, or review report;
- collecting verification evidence from command output, CI, review notes, or logs;
- checking recent commit history for local message style;
- reviewing the drafted message for mismatch, overclaiming, private details, or missing caveats.

Require every subagent result to include:

- paths inspected;
- commands run or deliberately skipped;
- evidence found with source paths, diff handles, or verification output;
- assumptions, confidence, and residual risk;
- candidate wording or concerns, not unsupervised staging or committing.

If subagents are unavailable, perform the same checks sequentially with a narrower context budget.

## Guardrails

- Do not run `git add`, `git commit`, push, tag, create branches, amend commits, rewrite history, publish releases, or open pull requests.
- Do not answer a commit-message request with only notes, only a summary, only a message preview, or only prose when safe command blocks can be produced.
- Do not silently collapse unrelated work into one tidy commit. Split obvious clusters or call out the risk.
- Do not run mutating commands such as formatters, generators, migrations, autofixers, or cleanup scripts while drafting a message unless the user separately asks for implementation work.
- Do not draft from the originating issue alone; inspect the local diff or supplied patch before writing the final message.
- Do not omit the combined `Git Command` or staged-only commit command merely because the prose preview is available.
- Do not emit `git add -- ... && git commit -m ...` or staged-only `git commit -m ...` commands unless paths and message quotes are safe for the displayed command; rewrite unsafe message wording first.
- Do not use shell-specific line continuation characters in generated commit commands unless the user explicitly requests a specific shell format.
- Do not emit a `git commit -m '...'` or `git commit -m "..."` command containing unescaped matching quote characters that would break shell parsing.
- Do not claim tests, CI, reviews, doc sync, security review, or standards review passed unless there is evidence.
- Do not hide skipped checks or known failures in a vague positive message.
- Do not combine unrelated work into one tidy story without warning the user.
- Do not include private notes, ignored scratch content, credentials, secrets, sensitive personal context, client data, or real user data in commit text.
- Do not require GitHub, GitLab, Bitbucket, Jira, Linear, or any hosting platform. Use platform metadata only when available and helpful.
- Do not require this source repo's root docs after installation. The skill may rely only on its own instructions and target-project evidence.

## References

No external references are required. This skill is self-contained after installation.
