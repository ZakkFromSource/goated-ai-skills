# Commit Output Variants

Read this reference when the selected scope is already staged, when the dirty tree should be split into independent commit groups, or when the default single-command shape in `SKILL.md` is not enough.

The `SKILL.md` workflow owns scope selection, read-only git behavior, quote safety, verification caveats, and private-detail sanitization. These variants preserve output shape; they do not loosen those gates.

## Staged-Only Scope

When selected changes are already staged, state exactly:

```text
No git add command needed; selected changes are already staged.
```

Then emit only the commit command:

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

## Ambiguous Or Independent Change Groups

When the dirty tree contains obvious independent groups, return a commit plan instead of blending unrelated work:

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

If groups are plausible but not safe enough to command, return candidate groups with caveats and recommend the safest default.

## Notes Shape

After the command, preview, and scope, include compact notes only when they prevent overclaiming or wrong-scope commits:

```markdown
Notes:
- Verification: <commands, checks, review gates, CI, manual verification, or "No verification evidence provided or run">
- Caveats: <skipped checks, unrelated changes, partial scope, assumptions, private-detail sanitization notes, or "None">
```

## Variant Checks

- START with the usable command or plan, not explanatory prose.
- INCLUDE `Commit Scope` for every command group.
- LIST excluded dirty files or say `None`; do not leave the user to infer scope.
- KEEP each command on one physical line without shell-specific line continuations.
- REWRITE unsafe quote characters, shell metacharacters, or private details before output.
