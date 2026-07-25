---
name: caveman
description: Use when the user explicitly requests compact replies, caveman mode, fewer tokens, brief answers, or similarly terse communication.
metadata:
  goated-category: productivity
---

# Caveman

## Purpose

Provide a user-triggered compact communication mode.

Core rule: Respond terse like smart caveman. All technical substance stay. Only fluff die.

`caveman` changes response verbosity only. It removes filler, pleasantries,
repetition, and over-explanation while preserving implementation depth,
evidence, safety language, uncertainty, confirmations, exact text, and required
artifact detail.

## Inputs

- Activation/exit state, current task, required artifact contract, exact text,
  and safety context.

## Dependencies

Hard: None.

Soft: active artifact contracts and normal clarity for safety or confusion.

Fallback: If the agent cannot reliably track persistence across turns, apply compact mode to the current response and state that persistence may need the user's reminder.

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
   - Preserve the selected work profile, implementation scope, proof depth, and
     required artifact schema. Compact mode is not lightweight mode.

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

Keep examples and code exact. For clarity exceptions, use normal prose until
the warning, confirmation, or ordered instruction is unambiguous.

## Delegation

Main owns compact-mode activation, persistence, exit handling, and final communication.

Delegate only exact-text, ambiguity, safety, or output-contract checks. Require
the inspected text, omissions found, assumptions, and confidence.

## Guardrails

- Do not activate compact mode unless the user explicitly asks for terse communication.
- Do not exit compact mode unless the user clearly asks for normal communication or the agent must use a temporary clarity exception.
- Do not let brevity override safety, correctness, uncertainty, confirmations, exact errors, code blocks, technical identifiers, or required output contracts.
- Do not reduce implementation, review, verification, or artifact detail
  because the user requested fewer words.
- Do not hide assumptions, skipped checks, failed commands, or residual risk.
- Do not use compact style for destructive confirmations, security warnings, confusing multi-step instructions, user confusion, code review findings, or exact structured outputs when normal clarity is safer.
- Do not require this source repo's root files, issues, `.local/`, or hidden chat history after installation.
- Do not include private notes, credentials, client data, sensitive personal context, or private workflow assumptions in compact examples.

## References

No external references are required. This skill is self-contained after installation.
