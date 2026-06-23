# Refinement Patterns

Read this reference when applying `code-refinement` to a scoped diff, choosing safe cleanup moves, or checking whether a simplification is actually clearer.

## Rule

Clarity beats compactness. A refinement is good when a maintainer can understand and verify the same behavior with less local effort. It is not good merely because the code has fewer lines.

## Good Refinement Moves

### Name The Concept

Rename vague locals, helpers, tests, CSS classes, or markup identifiers when the new name describes the domain concept or behavior being proved.

Prefer:

```python
is_overdue = due_date < today
```

over:

```python
flag = due_date < today
```

Do not rename stable public symbols without routing to a public-interface workflow.

### Collapse Duplicated Branch Work

If branches repeat setup or output shape, keep the decision visible and share only the repeated work.

Prefer:

```python
status_label = "Archived" if item.is_archived else "Active"
return {"id": item.id, "status": status_label}
```

over:

```python
if item.is_archived:
    return {"id": item.id, "status": "Archived"}
return {"id": item.id, "status": "Active"}
```

Do not collapse branches when they represent different business rules, error paths, or side effects that are clearer when kept separate.

### Extract Only When The Name Pays Rent

Extract a helper when the helper name explains a real concept, hides repeated choreography, or gives tests/callers a clearer public behavior surface.

Prefer a helper for repeated parsing or validation:

```python
def normalized_tag(value):
    return value.strip().casefold()
```

Avoid helpers that only restate one line:

```python
def strip_value(value):
    return value.strip()
```

### Inline Shallow Wrappers

Inline local wrappers that mostly forward arguments and force readers to jump around without hiding meaningful behavior.

Keep wrappers that encode domain language, enforce invariants, centralize side effects, or provide a stable public interface.

### Keep Error Handling Explicit

Simplify repeated error handling, but do not hide important failure states behind dense expressions.

Prefer:

```python
try:
    return load_profile(path)
except FileNotFoundError:
    return default_profile()
```

over a clever expression that makes the failure path harder to inspect.

### Preserve Useful Comments

Remove comments that narrate obvious syntax:

```python
# Increment count by one.
count += 1
```

Keep comments that explain why the code is shaped this way:

```python
# Keep this comparison case-sensitive; external IDs are not normalized.
if submitted_id == stored_id:
    ...
```

### Simplify HTML Structure Without Losing Semantics

Remove unnecessary wrapper elements when they do not carry layout, semantics, accessibility, or styling responsibility.

Prefer:

```html
<button class="save-button" type="submit">Save</button>
```

over:

```html
<div class="save-button-wrapper">
  <button class="save-button" type="submit">Save</button>
</div>
```

Only remove the wrapper after checking CSS, scripts, layout hooks, and accessibility relationships.

### Consolidate CSS With Intent

Combine repeated declarations when selectors share a real design role.

Prefer:

```css
.primary-button,
.secondary-button {
  border-radius: 4px;
  padding: 0.5rem 0.75rem;
}
```

over repeating identical declarations in both rules.

Do not merge selectors just because declarations match today if their design meanings are unrelated and likely to diverge.

### Clean Tests Without Weakening Proof

Rename tests, remove duplicated setup, and replace private-state assertions with public-interface assertions when behavior coverage stays equivalent or improves.

Prefer:

```python
def test_marks_past_due_invoice_as_overdue():
    invoice = invoice_due(days_ago=2)

    assert invoice.status(today=TODAY) == "overdue"
```

over a test name or assertion that forces readers to inspect implementation details.

Do not delete a test because it feels redundant until equivalent behavior proof exists elsewhere.

## Anti-Patterns

### Clever Compactness

Reject dense expressions that make readers mentally execute the code to understand it.

Be suspicious of:

- nested ternaries;
- chained boolean expressions with mixed concerns;
- clever comprehensions that hide side effects or error cases;
- single-line functions that compress validation, mutation, and return behavior.

### Line-Count-Driven Rewrites

Fewer lines are not automatically simpler. A longer version is often better when it names intermediate concepts, keeps failure states visible, or matches local style.

### Abstraction Churn

Do not add a helper, class, adapter, hook, mixin, or utility module just because two nearby lines look similar. Add abstraction only when it removes real duplication, clarifies a concept, or hides meaningful behavior.

Do not remove an abstraction if deleting it makes domain rules, side effects, or caller choreography scatter back into multiple places.

### Scope Creep

Do not clean adjacent files because they are nearby. Do not modernize an old area while touching a narrow bug fix. Do not reformat a file unless formatting is part of the scoped proof or project command.

### Proof Erosion

Do not change tests to match the refined implementation. Do not replace behavior assertions with snapshots, call counts, private-state checks, or looser assertions unless the public behavior remains equally protected.

### Generated File Drift

Do not hand-edit generated output unless the project treats that output as source. Find the generator, source template, or documented generation command instead, or report the file as out of scope.

## Quick Check

Before keeping a refinement, answer:

- Does behavior stay the same?
- Is the scope still the current diff, task-touched files, explicit paths, or approved area?
- Can the same proof be rerun after the edit?
- Is the resulting code easier to read locally?
- Did any public interface, module boundary, dependency seam, or docs-relevant name change?
- Would a maintainer understand why this is better without reading a long explanation?
