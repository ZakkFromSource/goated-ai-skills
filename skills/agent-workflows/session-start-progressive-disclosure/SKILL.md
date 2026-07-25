---
name: session-start-progressive-disclosure
description: Use when work begins with an unfamiliar project, cross-area scope, stale evidence, or uncertain project boundary and needs focused orientation before planning or implementation.
metadata:
  goated-category: agent-workflows
---

# Session Start Progressive Disclosure

## Purpose

Collect the smallest fresh evidence needed to orient unfamiliar, cross-area,
stale, or boundary-uncertain work.

Do not activate this full skill for a fresh, obvious tiny task. The shared
router owns proportional orientation and can initialize a lightweight envelope
silently.

## Inputs

- User request, current directory, and applicable instructions.
- Existing work envelope, scope, decisions, and evidence entries.
- Explicit ticket, spec, artifact, source path, or command.
- Existing project context, source maps, and standards when relevant.

## Dependencies

Hard: None.

Soft:
- `context-matrix-map` when repeated source retrieval has a demonstrated gap
- `project-context-calibration` when shared terminology or boundaries are absent
- `project-standards-calibration` when conventions materially affect the task

Fallback: Inspect only the user-named artifact, nearest instructions, and
current source needed for the next safe action. Record lower confidence when an
expected source is unavailable.

## Workflow

1. **Classify the surface.**
   - Distinguish source-repo maintenance, skill installation or adaptation,
     target-project onboarding, target-project delivery, prompt crafting, and
     unknown work.
   - Preserve the boundary between a skill source repository, installed skill
     folders, and the target project.

2. **Reuse the envelope and evidence.**
   - Read the current goal, scope, profile, checkpoint, proof strategy, and next
     action when an envelope exists.
   - Reuse evidence whose locator, applicable scope, freshness, and confidence
     support this task. Do not reread it merely because a new skill started.
   - Emit `evidence-stale` when a source changed, contradicts an entry, or is too
     shallow for the intended claim.

3. **Read one layer at a time.**
   - Start with the request and explicit file, ticket, spec, or artifact.
   - Read applicable local agent instructions.
   - For source maintenance, read maintainer guidance, public context, and the
     relevant ticket or spec.
   - For installation or adaptation, read install guidance and only the
     affected skill or adapter files.
   - For onboarding, inspect existing project instructions, context, standards,
     source maps, README, and build metadata only as needed.
   - For delivery, inspect the originating requirement, relevant standards, and
     the smallest current source and test surface.

4. **Stop discovery when the next action is safe.**
   - Stop when the next local action and proof path are clear, remaining
     uncertainty is a user decision, or further reading would be broad
     collection rather than targeted evidence.
   - Hand off to clarification, context calibration, standards calibration,
     architecture, planning, or direct work only when the discovered need
     justifies it.

5. **Update state without rebuilding the route.**
   - Return the task-surface result, sources inspected, new or refreshed
     evidence, assumptions, uncertainty, and any `scope-changed` or
     `evidence-stale` signal.
   - Let the main router apply signals at a defined checkpoint. Do not select a
     long downstream pipeline.
   - Keep routine orientation internal. Surface a report only for a conflict,
     blocker, missing decision, material scope or risk change, or when the user
     explicitly asks for orientation.

## Output Contract

Return an internal work-envelope delta containing:

- task surface and boundary;
- inspected sources and fresh evidence references;
- assumptions, missing context, and confidence;
- route signals, if any;
- recommended next action.

When a visible report is justified, keep it compact:

```markdown
**Session Orientation**
- Surface: <classification>
- Read: <sources>
- Material finding: <decision, blocker, scope change, or missing context>
- Next: <focused action>
```

Standalone invocation uses the same focused discovery and returns this compact
local result without requiring shared policy, registry, or source-repo files.

## Delegation

The main agent owns classification, boundary judgment, evidence acceptance, and
communication. Delegate only bounded source discovery with paths, commands,
findings, freshness, assumptions, and uncertainty. Review returned evidence
before adding it to the envelope.

Remain single-agent-compatible when delegation is unavailable.

## Guardrails

- Do not load private or ignored notes unless the user names them or the active
  task requires them.
- Do not bulk-read source trees, documentation, or skill references just in
  case.
- Do not infer that a target project adopted GOATED artifacts merely because
  the installed stack supports them.
- Do not treat one instruction filename or framework convention as universal.
- Do not turn orientation into architecture review, standards audit, security
  review, planning, or handoff.
- Do not narrate routine routing or duplicate a task closeout.

## References

No external reference is required. This skill is self-contained after
installation.
