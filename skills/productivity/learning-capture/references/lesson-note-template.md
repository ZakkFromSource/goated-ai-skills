# Lesson Note Template

## Contents

- [Candidate Card](#candidate-card)
- [Optional Config](#optional-config)
- [Lesson Note](#lesson-note)
- [Final Chat Audit](#final-chat-audit)

Use this reference when formatting candidate review cards, optional config files, lesson notes, or final chat audit summaries.

## Candidate Card

Show candidate cards before writing or updating notes.

```markdown
### Candidate: Async cleanup belongs with the lifecycle that starts it

- Subject: `programming`
- Topic: `flutter-riverpod`
- Tags: `learning-capture`, `subject/programming`, `topic/flutter-riverpod`, `type/pattern`
- Status: `budding`
- Confidence: `medium`
- Source type: `software`
- Destination: `knowledge/programming/flutter-riverpod/`
- Proposed filename: `async-cleanup-belongs-with-the-lifecycle-that-starts-it.md`
- Claim: Async subscriptions are easiest to reason about when cancellation is owned by the same lifecycle that starts the work.
- Recommendation: create
```

## Optional Config

Prefer `learning-capture.config.md` when a project or vault wants repeatable defaults. `.learning-capture.yml` can be supported as a plain YAML fallback.

```markdown
---
knowledge_root: knowledge
default_subject: programming
default_status: budding
source_type_taxonomy: references/source-type-taxonomy.md
tag_taxonomy:
  required:
    - learning-capture
  prefixes:
    - subject/
    - topic/
    - type/
---

# Learning Capture Config

Short human notes about where learning-capture notes belong in this project or vault.
```

## Lesson Note

Use one file per atomic lesson. Use readable kebab-case filenames without date prefixes.

```markdown
---
title: Async cleanup belongs with the lifecycle that starts it
tags:
  - learning-capture
  - subject/programming
  - topic/flutter-riverpod
  - type/pattern
subject: programming
topic: flutter-riverpod
status: budding
confidence: medium
source_type: software
source: Observed while reviewing a widget lifecycle issue in the current project.
created: 2026-06-26
updated: 2026-06-26
---

# Async cleanup belongs with the lifecycle that starts it

## Lesson

Async subscriptions are easiest to reason about when cancellation is owned by the same lifecycle that starts the work.

## For Humans

When setup and cleanup live together, it is easier to see what starts, what stops, and what can still run after a widget, component, or request is gone.

## For Agents

When editing lifecycle-sensitive code, look for the operation that starts async work and verify the matching cleanup path before adding new listeners, timers, streams, or callbacks.

## Use When

- Reviewing lifecycle-sensitive UI, provider, request, or subscription code.
- Debugging callbacks that fire after their owner is disposed.
- Deciding where cancellation or teardown belongs.

## Caveats

Some frameworks centralize cleanup through a parent owner or managed scope. Verify the local framework pattern before moving teardown code.

## Example

A widget that starts a stream subscription in an initialization path should either cancel it in the matching disposal path or delegate both setup and cleanup to the same lifecycle-aware owner.
```

## Final Chat Audit

Keep the final audit in chat only. Do not create a persistent capture log.

```markdown
Created
- `knowledge/programming/flutter-riverpod/async-cleanup-belongs-with-the-lifecycle-that-starts-it.md` - status: `budding`

Updated
- `knowledge/writing/headlines/specificity-beats-cleverness.md` - added caveat from new examples

Nurtured
- `knowledge/business/offers/clear-risk-reversal-builds-trust.md` - moved from `seedling` to `budding`

Skipped
- "Temporary install failure" - transient task state, not durable learning
- "Client API key handling detail" - sensitive detail omitted

Blocked
- "Async cancellation policy" - destination unclear
```
