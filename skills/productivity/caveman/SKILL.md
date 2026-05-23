---
name: caveman
category: productivity
classification: portable
status: wip
description: Use when the user explicitly requests compact replies, caveman mode, fewer tokens, brief answers, or similarly terse communication.
triggers:
  - user says "caveman mode", "use caveman", "talk like caveman", or "compact mode"
  - user asks for "less tokens", "fewer tokens", "be brief", "short answers", or similarly terse responses
  - user asks the agent to keep replies compact across the current conversation
  - user wants concise communication without losing technical accuracy, warnings, uncertainty, exact errors, or required output formats
outputs:
  - compact-mode activation, persistence, or exit decision
  - terse response that preserves all technical substance and required structure
  - normal-clarity exception when brevity would risk safety, correctness, confirmation, or user understanding
  - explicit uncertainty, assumptions, warnings, exact errors, and code blocks when present
depends_on:
  hard: []
  soft:
    - active tool, skill, review, safety, or user-requested output contracts that require exact structure or normal clarity
    - normal clarity for destructive confirmations, security warnings, confusing multi-step instructions, or user confusion
  fallback: If the agent cannot reliably track persistence across turns, apply compact mode to the current response and state that persistence may need the user's reminder.
adapters:
  codex: usable
  claude-code: usable
  hermes: usable
  opencode: usable
  generic-agent: usable
---

# Caveman

## Purpose

Provide a user-triggered compact communication mode.

Core rule: Respond terse like smart caveman. All technical substance stay. Only fluff die.

`caveman` changes prose density, not accuracy. It removes filler, pleasantries, repetition, and over-explanation while preserving technical meaning, safety language, uncertainty, confirmations, exact text, and required output contracts.

## Inputs

- User's compact-mode request, exit request, or current persistence state.
- Current task, active instructions, and any required output contract.
- Exact code, commands, errors, warnings, assumptions, data, identifiers, or technical terms that must not be compressed incorrectly.
- Safety context, especially destructive actions, security risks, irreversible operations, or confusing multi-step instructions.

## Workflow

1. Detect activation and exit:
   - Activate when the user explicitly requests compact communication, including "caveman mode", "use caveman", "talk like caveman", "compact mode", "less tokens", "fewer tokens", "be brief", or "short answers".
   - Once activated, keep compact mode active for the current conversation until the user clearly exits with "stop caveman", "normal mode", "stop being brief", or an equivalent request.
   - If the user exits compact mode, resume normal communication style immediately.

2. Compress prose only:
   - Prefer short sentences, fragments, direct verbs, and arrows for cause or sequence.
   - Remove pleasantries, throat-clearing, repetition, and low-value qualifiers.
   - Keep technical terms exact when a shorter synonym would change meaning.
   - Use common abbreviations only when they are clear in context, such as DB, auth, config, req, res, fn, or impl.

3. Preserve substance:
   - Keep code blocks unchanged.
   - Quote exact errors, logs, commands, filenames, identifiers, user-provided text, and API names exactly.
   - Preserve warnings, assumptions, uncertainty, constraints, confirmations, and caveats.
   - Follow any active tool, skill, review, or user-requested output contract even if it makes the response longer.

4. Use normal clarity when needed:
   - Temporarily leave compact style for destructive confirmations, security warnings, safety-sensitive caveats, user confusion, and multi-step instructions where fragments could be misread.
   - Use normal clarity for required structured formats, code review findings, or exact confirmation prompts.
   - After the clarity-critical portion is complete, resume compact mode if it is still active.

5. Avoid false terseness:
   - Do not omit uncertainty to sound decisive.
   - Do not shorten a warning until it becomes vague.
   - Do not compress separate steps into one sentence if order matters.
   - Do not alter code, SQL, shell commands, or error text to fit the style.

## Output Contract

For ordinary answers in compact mode, prefer this shape:

```markdown
<answer>. <reason if useful>. <next step if useful>.
```

For examples, use compact prose but keep code exact.

Python example:

````markdown
Bug: `items` can be `None`, loop crashes.

```python
for item in items or []:
    print(item)
```
````

PostgreSQL example:

````markdown
Slow query: missing index on filtered column.

```sql
CREATE INDEX idx_orders_customer_id ON orders (customer_id);
```
````

For clarity exceptions, use normal clarity until the risk is clear:

````markdown
Warning: This permanently deletes rows from `orders` and cannot be undone unless a backup or transaction rollback is available.

Confirm the exact table, backup status, and rollback plan before running:

```sql
DELETE FROM orders;
```
````

## Delegation

The main agent owns compact-mode activation, persistence, exit handling, and final communication.

When subagents are available, use them only for bounded checks that do not depend on the compact style itself, such as:

- checking whether a draft preserved exact code, errors, warnings, and required formats;
- reviewing whether a compact response became ambiguous or unsafe;
- verifying whether a required output contract was preserved.

Require delegated checks to return inspected text or paths, any omissions or ambiguity found, assumptions, and confidence. If subagents are unavailable, perform the same review directly before answering.

## Guardrails

- Do not activate compact mode unless the user explicitly asks for terse communication.
- Do not exit compact mode unless the user clearly asks for normal communication or the agent must use a temporary clarity exception.
- Do not let brevity override safety, correctness, uncertainty, confirmations, exact errors, code blocks, technical identifiers, or required output contracts.
- Do not hide assumptions, skipped checks, failed commands, or residual risk.
- Do not use compact style for destructive confirmations, security warnings, confusing multi-step instructions, user confusion, code review findings, or exact structured outputs when normal clarity is safer.
- Do not require this source repo's root files, issues, `.local/`, or hidden chat history after installation.
- Do not include private notes, credentials, client data, sensitive personal context, or private workflow assumptions in compact examples.

## References

No external references are required. This skill is self-contained after installation.
