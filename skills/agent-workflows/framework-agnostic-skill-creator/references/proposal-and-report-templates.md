# Proposal And Report Templates

Read this reference when producing a skill creator proposal, portability review, or edit report.

The `SKILL.md` workflow owns mode choice, source package audit routing, privacy judgment, portability judgment, support-file bias, and evaluation requirements. These templates preserve report shape; they do not replace those decisions.

## Skill Creator Proposal

Use this shape when producing a review or proposal:

```markdown
# Skill Creator Proposal: <skill-name>

## Mode And Intent

- Mode: <create from clarified intent | port from source material>
- Goal: <one sentence>
- Success criteria: <observable outcomes>
- Scope and non-goals: <brief summary>

## Source Package Manifest

Use for port mode. For create mode, write `Not applicable`.

### Files/Links Inspected

| Source | Type | Why inspected | Behavior evidence found |
| --- | --- | --- | --- |

### Skipped Files / Why

| Source | Why skipped | Residual risk |
| --- | --- | --- |

## Neutral Skill Shape

- Name: <candidate-name>
- Metadata category: <agent-workflows | engineering | productivity>
- Discovery description: <candidate description>
- Activation conditions: <brief list>
- Key workflow steps: <brief list>
- Output contract: <brief list>
- Dependencies: <hard, soft, fallback summary>
- Compatibility caveats: <real caveats or "None">

## Support Files

- References: <files and read conditions>
- Scripts: <files and run conditions>
- Assets: <files and use conditions>

## Evaluation

- RED baseline or planned scenarios: <summary>
- Rationalizations or expected failure modes: <summary>
- GREEN verification or residual risk: <summary>

## Compatibility

| Constraint or mechanic | Neutral handling | Remaining risk |
| --- | --- | --- |

## Privacy And Portability

- Public-safe content: <summary>
- Removed or generalized content: <summary>
- Portability judgment: <public-safe portable | domain-specific | private-only>

## Remaining Blockers

- <blocker or "None">
```

## Edit Report

When editing a skill folder, report:

- files changed;
- selected mode and category decision;
- source package manifest summary when porting;
- discovery, output, dependency, support-file, and compatibility decisions;
- evaluation plan or checks performed;
- privacy or portability blockers;
- verification checks performed.

## Template Checks

- INCLUDE source package manifest details for port mode before judging portability.
- MARK create-mode source manifest as `Not applicable` instead of deleting the section when the proposal needs symmetrical review.
- LIST skipped source files or links with residual risk.
- DOCUMENT support files with read or run conditions.
- VALIDATE public-safe wording and self-contained installed behavior before publishing.
