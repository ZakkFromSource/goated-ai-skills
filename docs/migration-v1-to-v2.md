# Migrate From V1 To V2

V2 keeps the V1 skill-folder distribution model and adds a recommended
integrated installation. The preserved V1 release remains available at the
`v1-baseline` Git tag.

## Choose An Installation Mode

For the recommended integrated mode:

1. Keep one distribution root containing sibling `skills/` and `stack/`
   directories.
2. Copy the selected canonical skill folders and the complete `stack/`
   directory.
3. Merge `stack/AGENTS.md` into the instruction artifact your framework
   actually applies. Preserve stronger user, organization, and project rules.
4. Keep `stack/goated-stack.yaml`, its schema, fixtures, and templates at their
   package-relative paths.

For individual mode, copy one complete canonical skill folder. Its
`SKILL.md` and local references retain a compact standalone fallback without
the shared policy or registry.

## Rename Canonical Skills

Update active instructions and links to the V2 canonical names:

| V1 name | V2 canonical name |
| --- | --- |
| `write-a-prd` | `write-a-spec` |
| `prd-to-issues` | `spec-to-tickets` |
| `plan-codebase-architecture` | `design-codebase-architecture` |
| `improve-codebase-architecture` | `review-codebase-architecture` |

Integrated installs may continue accepting the V1 names as registry aliases.
Do not create duplicate alias folders. Individual installs should copy and
invoke the canonical folder.

## Adopt V2 State And Artifact Paths

- Treat the work envelope as compact logical state, not a mandatory tracked
  file.
- For resumable local state, prefer
  `.local/goated/work-envelopes/<effort-slug>.md` and
  `.local/goated/handoffs/<effort-slug>.md` only after verifying `.local/` is
  ignored.
- Use OS temporary storage when ignored project-local storage is unavailable
  or inappropriate.
- Store durable specs under `docs/specs/`, delivery tickets under `tickets/`,
  feature architecture plans under `docs/architecture/`, and Wayfinder maps
  under `docs/wayfinding/` when the target project has no stronger convention.

## Replace Fixed Pipelines With Adaptive Gates

Route through `using-goated-ai-skills`, then select only justified gates for the
current profile and risk. Re-evaluate after clarification or diagnosis, after
planning, after implementation, and before completion.

V2 removes these mandatory assumptions:

- full onboarding for every non-trivial task;
- code refinement after every implementation;
- every specialist review for every change;
- repeated discovery and separate closeouts from each skill;
- fresh authorization pauses when the existing request already covers the
  next project write and action reach has not changed.

Correctness, safety, scope control, and fresh evidence remain universal.
Security, standards/spec review, documentation sync, and full verification load
when their risk or uncertainty conditions apply.

## Validate The Migrated Stack

From this source checkout, run:

```text
uv run python scripts/validate_skills.py
uv run python -m unittest discover -s tests -v
uv run python scripts/compare_v1_v2_context.py
```

Review the four release-level fixtures under `stack/fixtures/end-to-end/` as
host-driven behavior contracts. They are deterministic conformance fixtures,
not a dedicated evaluation skill or model benchmark.

See [Install And Adapt GOATED AI Skills](install.md) for full installation
mechanics and [V2 Acceptance Report](v2-acceptance-report.md) for the release
proof and residual risk.
