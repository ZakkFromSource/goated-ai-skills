# Evidence Entry

Add compact references to the work envelope instead of copying source content.
Include each field when it helps another skill judge whether the evidence is
relevant and fresh.

```yaml
- identifier: # path, URL, command, commit, artifact ID, or other stable locator
  relevance:
  applicable_scope:
  finding:
  provenance:
  freshness: # commit, modification time, retrieval date, or equivalent
  confidence:
  uncertainty:
  validity: # current | invalidated
  invalidated_by: # changed path, command, checkpoint, or contradictory evidence
```

Reuse a current entry unless required evidence is missing, its source changed,
it is stale or too shallow for the intended claim, or contradictory evidence
appears. Project changes invalidate only affected entries at the
post-implementation checkpoint; retain the locator and invalidation reason
rather than silently deleting the history. Prefer current source and
executable evidence over summaries for exact or high-risk claims.
