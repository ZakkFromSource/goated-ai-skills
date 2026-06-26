# Worked Examples

Use these examples to test whether `learning-capture` stays topic-neutral and writer-focused.

## Example 1: Programming Capture And Nurture

### Situation

During a debugging session, an agent discovers that a UI component starts a stream subscription in one lifecycle method but cancellation is scattered through a separate helper. An existing note already exists:

`knowledge/programming/flutter-riverpod/cancel-subscriptions-on-dispose.md`

That note is `seedling`, has weak wording, and only says "remember to cancel subscriptions."

### Candidate Review

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
- Claim: Async subscriptions are easier to reason about when setup and cleanup are owned by the same lifecycle boundary.
- Recommendation: nurture existing note `cancel-subscriptions-on-dispose.md` rather than create a duplicate
```

### Nurtured Note Direction

- Keep the existing file because the old note is close enough to improve.
- Retitle or alias toward the stronger lesson.
- Change `status` from `seedling` to `budding` only if the updated note includes evidence, use cases, and caveats.
- Add a caveat that some frameworks centralize cleanup in a parent managed scope.

### Final Chat Audit

```markdown
Nurtured
- `knowledge/programming/flutter-riverpod/cancel-subscriptions-on-dispose.md` - strengthened the claim, added lifecycle ownership guidance, and moved status from `seedling` to `budding`

Skipped
- "Create async-cleanup-belongs-with-the-lifecycle-that-starts-it.md" - overlapped the nurtured existing note
```

## Example 2: Non-Programming Extract

### Situation

The user provides notes from a workshop about designing a calmer weekly planning routine. The provided material includes this source claim: people were more likely to complete a weekly review when the review separated capture, prioritization, and scheduling into distinct passes.

### Candidate Review

```markdown
### Candidate: Separate capture from prioritization in weekly planning

- Subject: `productivity`
- Topic: `weekly-planning`
- Tags: `learning-capture`, `subject/productivity`, `topic/weekly-planning`, `type/pattern`
- Status: `budding`
- Confidence: `medium`
- Source type: `workshop`
- Destination: `knowledge/productivity/weekly-planning/`
- Proposed filename: `separate-capture-from-prioritization-in-weekly-planning.md`
- Claim: Weekly planning is easier to complete when capture, prioritization, and scheduling happen as separate passes.
- Recommendation: create
```

### Created Note

```markdown
---
title: Separate capture from prioritization in weekly planning
tags:
  - learning-capture
  - subject/productivity
  - topic/weekly-planning
  - type/pattern
subject: productivity
topic: weekly-planning
status: budding
confidence: medium
source_type: workshop
source: User-provided workshop notes about weekly planning routines.
created: 2026-06-26
updated: 2026-06-26
---

# Separate capture from prioritization in weekly planning

## Lesson

Weekly planning is easier to complete when capture, prioritization, and scheduling happen as separate passes.

## For Humans

Trying to list tasks, judge importance, and place work on the calendar at the same time creates friction. A calmer review lets each pass do one job.

## For Agents

When helping with weekly planning, avoid mixing inbox capture, priority ranking, and calendar placement into one prompt unless the user explicitly wants a fast rough pass.

## Use When

- Designing a weekly review.
- Helping a user process an overloaded task list.
- Turning scattered notes into a plan without losing items.

## Caveats

This is based on user-provided workshop notes, not a controlled study. Treat it as a practical planning pattern rather than a universal productivity law.
```

### Final Chat Audit

```markdown
Created
- `knowledge/productivity/weekly-planning/separate-capture-from-prioritization-in-weekly-planning.md` - status: `budding`
```
