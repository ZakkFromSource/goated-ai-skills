# Instruction Refinement Implementation Plan

## Target And Scope

Apply the maintainer-approved instruction audit informed by the September 2026
OpenAI guidance. Keep the public library framework-agnostic and preserve
standalone skills, user intent, privacy, required checks, and approval limits.
This is a durable plan because the change spans shared policy, several skill
packages, documentation, and an authorized local installation refresh.

The source contract is the approved audit, supported by
[Ticket 009](../../tickets/archive/009-prove-behaviour-without-mandatory-refinement.md),
[Ticket 015](../../tickets/archive/015-sharpen-skill-authoring-discipline.md), and
the [external guidance note](../agents/external-docs/openai-skill-guidance.md).
Historical acceptance records remain historical.

Branch base was verified after fetching `origin`: `update/v2` at `8da4625`
contains all of `main` plus 45 commits. The implementation branch starts at
that V2 tip.

## Implementation

1. In `stack/AGENTS.md` and `using-goated-ai-skills`, clarify instruction
   precedence, reuse of covering authorization, task completion, and when to
   expand verification. Retain explicit approval for actions whose reach is
   not already covered and all host safety controls.
2. In `goated-prompt` and its references, make outcome, context, constraints,
   acceptance, proof, and authorized completion the default prompt contract.
   Reserve detailed task sequences for settled dependencies or real ordering
   constraints. Remove clarification triggers based only on file count or
   public visibility and reconcile optional explanation with its checklist.
3. In `code-refinement` and the `documentation-cleanup` checklist, distinguish
   unresolved risky mutations from safe investigation and separable edits.
   Remove the obsolete `grill-with-docs` skip-report requirement.
4. Tighten `commit-message` discovery. Extract Create and Port details from
   `framework-agnostic-skill-creator` into directly linked branch references,
   retaining common decisions and constraints in the root. Move prototype
   presentation recipes into existing branch references and size experiments
   from the live decision rather than a fixed variant count.
5. Extend the existing skill-evaluation guidance with model-upgrade comparisons
   and positive/negative selection cases. Use isolated decision exercises and
   source inspection as proportionate evidence for prose changes; do not add
   tests that assert the new wording or claim a model benchmark.
6. Update installation guidance and thin instruction integration for one
   explicitly loaded shared policy, discovered through the host rather than a
   machine-specific absolute path. Back up local instructions and overwritten
   installation files, preserve personal preferences, then refresh only public
   source counterparts in both installed layouts. Preserve unrelated extras
   and record newly created paths for recovery.

## Verification

- Before changing skills, capture the current packages and compare unaided and
  existing-skill decisions on fixed, synthetic tasks. Repeat with the revised
  skills using fresh agents and inspect returned evidence. Treat this as a
  limited decision exercise, not production execution or cross-model proof.
- Review changed roots together with their references and consumers for
  contradictory triggers, permission loops, lost invariants, missing links,
  and new dependencies on the source repository.
- Run `uv run python scripts/validate_skills.py`,
  `uv run python -m unittest discover -s tests -v`, and
  `uv run python scripts/compare_v1_v2_context.py`.
- Run `git diff --check`; inspect the final diff, public/private boundary,
  instruction sizes, and source-to-install file contents. Confirm unrelated
  working-tree edits remain unchanged.

## Ownership And Boundaries

The main agent owns all edits, installation, integration, and final claims.
Independent agents may run read-only decision exercises and review bounded
policy or package surfaces. Their reports require source inspection before use.
A local commit and installation refresh from that committed revision are
authorized. No new skill, runtime harness, dependency, push, or publication is
part of this change. Existing acceptance tests remain useful structural checks.

Pause dependent work only for a material unresolved decision, unsafe target,
unexpected user changes in an overwrite target, or an action outside covering
authorization. Continue independent authorized work while resolving it.

## Evidence Status

The scoped source and local instruction changes are implemented. Review caught
and corrected stale refinement proposal reasons and a shared packaging rule
that had moved into only one creator branch. Maintainer feedback also removed
machine-specific instruction paths and added bounded discovery with a
standalone fallback. Local discovery and an explicit policy read were checked;
automatic loading in future sessions and other hosts were not exercised.

All 148 existing tests pass. Package validation passes for 37 skills, 37
registry entries, and 98 fixture scenarios; the shared policy is 1,192 words.
The four existing V1/V2 route-size comparisons meet their 10% reduction target.
These are structural and size checks, not measured model improvements.

Four fixed synthetic decision exercises ran in fresh agents for unaided,
existing-skill, and revised-skill conditions. All preserved the intended
authorization and read-only boundaries. The revised prompt skill selected a
focused task for settled multi-file work; the existing skill selected a spec
route. No baseline failure was manufactured, and these exercises did not run
the proposed code or documentation changes in real target projects.

The authorized installation refresh verified normalized content parity for
87 flat skill files and 221 categorized skill/policy files. Overwritten files
were backed up, new paths recorded, and unrelated additions preserved. Personal
instruction preferences and pre-existing working-tree edits were retained.

Runtime model-selection accuracy, actual context truncation, and performance
gains are not established by this work. Cross-model comparison remains a
separate experiment.
