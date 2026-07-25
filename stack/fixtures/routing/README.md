# Adaptive Routing Fixtures

These versioned YAML fixtures describe portable V2 routing expectations. They
are public-safe contract examples for deterministic validation, manual review,
and optional host-driven comparison. They are not replayable model transcripts
and a passing structural check does not prove that every host agent will follow
the route.

Each fixture records the request and minimal context, all work-profile
dimensions, sensitivity and action reach, initial gates, checkpoint deltas,
route signals, approval behavior, evidence reuse or invalidation, proof
strategy, closeout ownership, and prohibited behavior. Gate names resolve to a
registered skill name or one of the shared gates implemented by the integrated
policy: `proportional-orientation`, `direct-work`, `direct-proof`, and
`consolidated-closeout`.

The fixture format is checked directly by `scripts/validate_skills.py`. It
deliberately has no JSON Schema while V2 fixture serialization is still
maturing; the registry remains the only formally schema-validated V2 contract.

Manual or host-driven review should confirm:

- the router does not narrate routine routing or silently activate a long
  pipeline;
- tiny work stays near-zero ceremony;
- only a defined checkpoint or material signal changes the route;
- skill results become envelope deltas and the main agent gives one closeout;
- static expectations remain realistic in both integrated and standalone use.

Release conformance also requires explicit conflicting-trigger resolution and
individual-skill fallback scenarios. These keep central routing from becoming
parallel pipelines and prove that a copied skill retains task-critical safety
without the shared policy or registry.

## Ticket 002 Baseline Observation

Whitespace-delimited counts recorded on 2026-07-25 compare the preserved
`v1-baseline` tag with the routed V2 slice:

| Path | V1 words | V2 words | Delta |
| --- | ---: | ---: | ---: |
| Standalone router | 1,541 | 1,151 | -390 (-25.3%) |
| Router plus full session orientation | 2,307 | 1,884 | -423 (-18.3%) |

The integrated shared policy is 932 words and is resident stack policy rather
than a task-by-task specialist load. Shared policy plus the V2 router is 2,083
words; this total should not be presented as a direct standalone-router
compression result.

Reproduce the source counts with PowerShell by loading each current file with
`Get-Content -Raw`, loading each baseline file with `git show
v1-baseline:<path>`, splitting on `\s+`, and counting non-empty tokens.
