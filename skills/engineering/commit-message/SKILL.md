---
name: commit-message
description: Use when the user asks to draft or revise a Git commit message.
metadata:
  goated-category: engineering
---

# Commit Message

## Purpose

Draft clear commit text from the actual change set and verified context. Help
future readers understand what changed, why, how it was checked, and what
remains uncertain.

This skill is read-only. It returns message text by default and never stages,
commits, pushes, tags, or publishes.

## Inputs

- User request and originating intent.
- Target-project root path.
- Git status, staged changes, unstaged changes, untracked files, recent commits, branch context, or supplied patch.
- Relevant diffs and nearby intent or standards evidence.
- Verification evidence such as tests, linters, formatters, manual checks, review gates, doc-sync results, skipped checks, or known failures.
- Shell constraints only when commands are explicitly requested.

## Dependencies

Hard: None.

Soft:
- session-start-progressive-disclosure for unfamiliar target projects
- standards-and-spec-review when spec fit or standards remain unresolved
- code-security-review when trust boundaries, auth, user data, persistence, execution, or security config changed
- doc-sync when behavior, interfaces, docs, standards, configuration, or tests may drift
- verification-before-completion before commit wording claims completion, passing checks, synced docs, or review readiness
- handoff when unfinished work or residual risk needs future continuity

Fallback: If companion skills, git metadata, specs, or verification evidence are unavailable, inspect minimal local evidence, state lower confidence, and avoid invented intent/checks.

## Workflow

1. Confirm the commit scope:
   - Identify the target-project root and whether the user requested a scope such as staged changes, unstaged changes, all working-tree changes, named paths, commits since a fixed point, or a supplied patch.
   - Use an explicit user scope when one is provided.
   - In git projects, inspect read-only status and summaries before drafting, using equivalents of `git status --short`, staged and unstaged diff stats, name-status output, and relevant hunk reads.
   - When staged changes exist, treat them as the primary scope unless the user explicitly asks for unstaged or all dirty files. Mention other dirty files as caveats or optional later groups.
   - Include untracked files in the scope decision. If they look relevant, inspect them directly because normal diffs may not show their contents.
   - Do not mutate the index, working tree, branches, remotes, tags, or issue state.

2. Resolve messy working trees:
   - Split obvious independent clusters instead of blending unrelated work.
   - Keep direct support docs and matching archive moves with their owning
     change. If grouping remains ambiguous, state the risk.

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

5. Choose the message shape:
   - Use the project's existing commit style when it is discoverable from recent history or standards docs.
   - If no style is discoverable, default to a concise imperative subject without a prefix.
   - Keep the subject focused on the user-visible or maintainer-meaningful outcome, usually 72 characters or fewer when practical.
   - Add a body only when it helps: multi-part changes, non-obvious rationale, migration notes, verification details, caveats, or reviewer context.
   - Return message text only by default. Do not add staging, commit, push, or shell-command suggestions unless the user explicitly asks for commands or repository mutation.

6. Sanitize public text:
   - Do not include secrets, tokens, private user data, sensitive logs, credentials, or ignored scratch content in commit text.
   - Avoid private client names, personal domains, internal handles, private URLs, or sensitive issue details unless they are already appropriate for the target project's public history.
   - If a change fixes exposure of sensitive material, describe the exposure class without repeating the sensitive value.
   - Prefer portable, project-local wording over hosting-platform jargon unless the project clearly uses that context in commit history.

7. Draft and self-check:
   - Ensure the subject matches the actual diff, not just the original plan.
   - Ensure the body does not claim checks, reviews, security coverage, or doc updates that did not happen.
   - Ensure known caveats are visible, especially skipped verification, unrelated changes, partial scope, generated files not inspected, or lower-confidence intent.
   - Put the finished message first. Add scope, verification, or caveat notes only when they prevent an inaccurate or wrong-scope commit.
   - When multiple commit groups are genuinely needed, put each finished message before its compact scope note.
   - If the user explicitly requests commands, read [Commit Output Variants](./references/commit-output-variants.md) and keep commands separate from the default message-only result.

## Output Contract

Return the finished commit message first:

````markdown
```text
Subject

Optional body paragraph
```
````

After the message, include only material context:

- selected or excluded scope when the working tree is ambiguous;
- verification caveats when the body would otherwise overclaim;
- uncertainty about grouping or intent.

Omit empty scope, caveat, verification, and `None` sections. In integrated use,
return the message plus any material scope or risk delta to the main agent; do
not produce a competing task closeout.

## Delegation

Main owns scope, wording, caveats, and communication. Delegate only bounded
diff, intent, verification, style, or draft review. Never delegate staging or
committing.

## Guardrails

- Do not run `git add`, `git commit`, push, tag, create branches, amend commits, rewrite history, publish releases, or open pull requests.
- Do not add staging, commit, push, or command suggestions unless the user explicitly asks for them.
- Do not silently collapse unrelated work into one tidy commit. Split obvious clusters or call out the risk.
- Draft from the inspected diff or patch, not the originating issue alone.
- When commands are explicitly requested, do not emit unsafe paths, quoting, or shell-specific continuations.
- Do not claim tests, CI, reviews, doc sync, security review, or standards review passed unless there is evidence.
- Do not hide skipped checks, failures, or unrelated work.
- Do not include private notes, ignored scratch content, credentials, secrets, sensitive personal context, client data, or real user data in commit text.
- Do not require this source repo's root docs after installation. The skill may rely only on its own instructions and target-project evidence.

## References

- [Commit Output Variants](./references/commit-output-variants.md) - read only when the user explicitly requests commands or command-oriented variants.
