# Spawn Brief

Use this template when work is about to start in a fresh agent or session now:
a subagent, a parallel session, or a session the current task moves into. The
brief is that agent's first message. It is the only context the agent gets
unless it inherits this conversation, so it must stand on its own.

For a scoped implementation task, fill the implementer prompt from
`subagent-driven-development` instead when that skill is installed; it adds
write ownership and review statuses. Use this template for everything else.

## Contents

- [Before Writing](#before-writing)
- [Template](#template)
- [After Sending](#after-sending)

## Before Writing

- Decide the brief is needed. A lookup you could run in a few steps, or a
  question this conversation already answers, needs no new agent.
- If the agent inherits this whole conversation, write only the task, the
  scope, and what done looks like. Do not retell what it can already read.
- Do not restate rules the agent already receives from its own instructions
  or setup, such as project instruction files or a session-start rule. Name a
  rule only when this task needs it applied differently.
- Write in your own words. "Based on the findings above" points at context the
  agent does not have.
- Leave out credentials, private data, and content the agent should not see.
- Name the skills the agent should read before it starts, on a skills line of
  its own or as a list item, outside code blocks, in lowercase, bare or in
  one pair of backticks. Name skills by their installed names, with any
  plugin namespace, such as `goated-skills: tdd, software-design-principles`
  or `goated-skills: goated:tdd`. When no skill applies, write none alone
  with a reason of three words or more, such as
  `goated-skills: none: the agent only lists files`. This file defines the
  line; other brief templates follow it. Picking the skills stays your
  judgement: name those your own route or work needed for this task.
  `doc-sync`, `standards-and-spec-review`, `verification-before-completion`
  and `setup-scribe` are met at the closeout, so leave them off the skills
  line and out of `requires:` even when the task will need them later.
  `code-security-review` may still be listed, since it applies while writing.
- If you already routed the task, end the brief with its route line, such as
  `goated-route: standard | requires: tdd`, on its own line outside code
  blocks. A new session takes it as its route and still loads those skills.
  On a `standard` or `full` route it orients before its first write by
  reading the sources the brief names, at least three files, or by loading
  `session-start-progressive-disclosure`, when installed, if the area is
  unfamiliar.
  A route line anywhere in the brief counts, so quote no other.

## Template

```markdown
## Goal

<One or two sentences: the task and why it exists.>

## Scope

- Work in: <files, directories, or area>
- May change: <write scope, or "read only">
- Must not touch: <areas other agents or the main agent own>
- Shared with: <other agents or sessions that may change the same files, or "none">
- Others may be editing elsewhere: do not revert changes you did not make.

## Done Means

- <Observable result: a passing check, a file that exists, a question answered.>
- Checks: <what the agent runs before reporting; what you run after merging its work>

## Already Settled

- Decisions: <what is decided and must not be reopened>
- Ruled out: <approaches tried or rejected, and why in a phrase>
- Sources: <paths, specs, tickets, commands worth reading first>

## Constraints

- <Commit, push, branch, dependency, or publication rules for this task.>

## Stop And Report When

- You need a decision, source, or permission you were not given.
- The task looks wrong, or is larger than this brief describes.

## Report Back

- Status: DONE | DONE_WITH_CONCERNS | NEEDS_CONTEXT | BLOCKED
- Changed paths and paths inspected
- Commands run and their results
- Assumptions, concerns, and checks skipped

Read each skill below before you start: load it with your skill tool, or
read its SKILL.md file if you have no skill tool.

goated-skills: <skill>, <skill>
<Route line, when you routed the task.>
```

Drop sections and lines that carry nothing for this task, such as Shared
with when no other agent works nearby, but keep the skills line.
Keep the brief short enough that the agent reads all of it before acting.

## After Sending

Treat the report as evidence to inspect, not a finished claim. Check changed
paths or reproduce important results before relying on them. For a session
started from the brief, that inspection of the report and the changed paths is
the starting session's review of the work.
