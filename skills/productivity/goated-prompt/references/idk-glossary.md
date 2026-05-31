# IDK Glossary

Use Information Dense Keywords when they reduce ambiguity. Do not force them into prose where ordinary language is clearer.

## Action Keywords

| Keyword | Use When |
| --- | --- |
| `CREATE` | Generate a new artifact, function, file, type, module, document, test, or plan from scratch. |
| `ADD` | Introduce a new element into an existing structure while preserving what is already there. |
| `UPDATE` | Change an existing artifact's content, behavior, data, or metadata. |
| `REPLACE` | Swap one existing artifact, behavior, or dependency for another. |
| `REFINE` | Improve clarity, quality, performance, wording, or maintainability without changing the core purpose. |
| `REFACTOR` | Restructure internals without changing external behavior. |
| `REMOVE` | Eliminate a specific part while keeping the surrounding structure. |
| `DELETE` | Remove an artifact or entity entirely. Use carefully when the action is irreversible. |
| `MOVE` | Transfer an artifact from one location or scope to another while preserving it. |
| `MIRROR` | Reproduce an existing pattern, structure, style, or behavior in another location. |
| `TEST` | Create or run checks that prove behavior. |
| `VALIDATE` | Check correctness, constraints, compliance, or acceptance criteria. |
| `CONFIGURE` | Set options, environment, flags, settings, or integration parameters. |
| `DOCUMENT` | Create or update explanatory, operator, API, product, or user-facing docs. |
| `ANALYZE` | Inspect source, behavior, data, tradeoffs, risks, logs, or evidence. |
| `DEPLOY` | Release or run a service, app, model, workflow, or artifact in a target environment. |

## Detail Keywords

| Keyword | Use When |
| --- | --- |
| `FILE` | The target is a document, source file, config file, or tracked artifact. |
| `FUNCTION` | The target is a standalone callable unit. |
| `METHOD` | The target is a callable unit owned by a class or object. |
| `CLASS` | The target is an object blueprint with data and behavior. |
| `TYPE` | The target is a data shape, schema, interface, alias, annotation, or domain type. |
| `VAR` | The target is mutable state or a named value. |
| `CONSTANT` | The target is a fixed value or stable setting. |
| `DEFAULT` | The target is fallback behavior or a value used when no explicit input is supplied. |
| `MODULE` | The target is a cohesive source unit or namespace. |
| `PACKAGE` | The target is a grouped set of modules, files, or installable code. |

## Location -> Action -> Detail Pattern

Use this pattern for focused task prompts:

```text
In <location>, <ACTION> the <DETAIL target> so that <observable outcome>.

Include:
- <constraint or edge case>
- <acceptance criterion>
- <verification expectation>
```

Example:

```text
In `src/users/profile.ts`, UPDATE the `normalizeProfile` FUNCTION so it preserves unknown optional fields while trimming known string fields.

Include:
- Do not change the public return TYPE.
- Add or update focused tests for empty strings, missing optional fields, and extra fields.
- Report the test command and result.
```

## MIRROR Pattern

Use `MIRROR` when an existing pattern is the best source of truth:

```text
MIRROR the validation style from `<reference location>` when creating `<new target>`.
Preserve the same error-shape conventions, naming style, and test organization unless the target requires a stated exception.
```

