# Invocation Topology Decision Report

## Decision Summary

- Report date: 2026-07-26.
- Last evidence update: 2026-07-27.
- Scope: Ticket 021 and parent-spec R6/AC6.
- Audience: GOATED maintainer and any future separately scoped harness designer.
- Document type: source-grounded host-capability and product-decision report.
- Investigation recommendation: **REVISE** the four candidate values before
  production use.
- Maintainer decision: **NO-GO**.
- First supported consumer: **none**.
- Decision date: 2026-07-27.
- Production changes made by this ticket: **none**.

Do not add `autonomous`, `router-only`, `manual-only`, and `reference-only` as
one production registry enum.

For historical design reference, the evidence supported one narrow,
orthogonal control: `implicit_invocation: allowed | blocked`. `autonomous` and
`manual-only` could be derived from that control where a host also supports
explicit user invocation. `reference-only` remains a package structure rather
than a registered skill mode, while strict `router-only` would require a
caller-aware consumer. None of these production metadata changes were
accepted.

Before the decision, the evidence identified Codex as the strongest first
consumer candidate because it has a documented native translation through
`agents/openai.yaml`, and the disposable experiment observed its catalog,
implicit-selection, and explicit user-selection behavior. Claude Code was a
strong second candidate. The generic Agent Skills specification does not
standardize invocation policy.

The maintainer declined production adoption after reviewing that evidence.
The benefit did not justify adding registry, adapter, migration, and
host-specific workflow complexity to GOATED's deliberately simple Codex
experience. Invocation access control or caller-aware routing may be explored
later in a separately specified custom harness, but it is not part of the core
GOATED workflow.

## Decision Record

| Field | Value |
| --- | --- |
| Maintainer decision | `NO-GO` |
| First supported consumer | `None` |
| Accepted production semantics | `None` |
| Decision date | `2026-07-27` |
| Ticket 022 authorized | `NO; close without implementation` |
| Governing rationale | `Preserve the simple Codex workflow; move richer invocation control to a separately scoped custom harness if it is ever needed` |

## Scope And Evidence Standard

This report answers:

> Which parts of `autonomous`, `router-only`, `manual-only`, and
> `reference-only` can Codex, Claude Code, and a generic Agent Skills host
> enforce as of 2026-07-26?

The decision use is whether Ticket 022 should add production metadata and
which host-specific surface should consume it first.

The source hierarchy was:

1. current governing host specifications and first-party documentation;
2. current first-party host source or release records;
3. current GOATED source, ADRs, schema, and installation contract;
4. observed disposable-host behavior.

Search snippets, community posts, remembered behavior, and static fixtures are
not evidence for host invocation behavior. Model observations are labeled
probabilistic even when the host configuration is deterministic.

## Current GOATED Boundary

The current registry owns catalog and cross-skill orchestration data, but it is
not an installer or runtime. The install guide says this directly, and the
schema currently rejects undeclared skill fields through
`additionalProperties: false`.
([Install guide](install.md),
[registry](../stack/goated-stack.yaml),
[registry schema](../stack/schemas/stack-registry.schema.json))

[ADR 0001](adr/0001-v1-runtime-bootstrap-and-adapter-automation.md) still
excludes runtime bootstrap, prompt injection, hooks, automatic loading,
generated plugin manifests, installers, and adapter automation.
[ADR 0002](adr/0002-v2-integrated-stack-foundation.md) adds the integrated
policy and registry but explicitly leaves those runtime exclusions in force.

The existing
[`agent-instructions-integrator`](../skills/agent-workflows/agent-instructions-integrator/SKILL.md)
creates thin target-project instruction routing. It does not package installed
skills or translate per-skill host metadata, so it is not the right production
consumer for invocation policy.

## Framework-Neutral Semantics

Catalog visibility is split into model and user visibility because the hosts
can control them independently.

| Candidate | Neutral definition | Model catalog | User catalog | General implicit selection | Explicit user selection | Router reachability | Context cost | Safe fallback |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `autonomous` | An independent skill is advertised to the host model and is eligible for model-driven selection. Eligibility is not a guarantee that the model will select it. | Yes | Yes | Allowed | Allowed | Ordinary skill access | Recurring catalog entry; full body when selected | `manual-only`, with the loss of autonomy reported |
| `manual-only` | An independent skill is absent from model discovery and can load only after an explicit user action. | No | Yes | Blocked | Allowed | Blocked | No default model-catalog entry; full body on explicit use | `reference-only` or omit when implicit selection cannot be blocked |
| `router-only` | An independent target is visible and invokable only to one designated router, not to the general model or user. This requires caller-aware access control. | No | No | Router only | Blocked | Designated router only | Router metadata plus target body only after routing | Degrade to a router-owned reference and report loss of independent skill identity |
| `reference-only` | Supporting content has no independent skill identity and is read only through an owning skill or workflow. | No | No | Blocked | Blocked | Owning skill reads it | Content cost only when the owner reads it | Omit rather than register it as a skill |

These definitions are neutral intent. They do not claim that every host can
enforce every row.

## Dated Host Source Matrix

| Host/source | Scope and freshness | Material finding | Confidence |
| --- | --- | --- | --- |
| [Codex: Build skills](https://learn.chatgpt.com/docs/build-skills) | Current official Codex manual source; retrieved 2026-07-26 | Codex documents explicit and implicit invocation, repository/user/admin/system discovery, progressive disclosure, and `policy.allow_implicit_invocation`. | High for the documented contract |
| [Claude Code skills](https://code.claude.com/docs/en/skills#control-who-invokes-a-skill) and [subagent preloading](https://code.claude.com/docs/en/sub-agents#preload-skills-into-subagents) | Rolling official docs retrieved 2026-07-26; current release [v2.1.220](https://github.com/anthropics/claude-code/releases/tag/v2.1.220), published 2026-07-25 | Claude documents separate model and user invocation controls, nested skill activation, and supporting files. | High for the documented contract |
| [Agent Skills specification at commit `38a2ff8`](https://github.com/agentskills/agentskills/blob/38a2ff82958afee88dadf4831509e6f7e9d8ef4e/docs/specification.mdx) | Governing source snapshot committed 2026-07-10; retrieved 2026-07-26 | The portable format standardizes progressive disclosure and skill metadata, not invocation policy or caller topology. | High |
| [Agent Skills client implementation guide at commit `38a2ff8`](https://github.com/agentskills/agentskills/blob/38a2ff82958afee88dadf4831509e6f7e9d8ef4e/docs/client-implementation/adding-skills-support.mdx) | Official implementation guidance last materially updated 2026-03-10; retrieved 2026-07-26 | Discovery, filtering, activation transport, and explicit syntax are client choices. `disable-model-invocation` is an example client feature, not a specification field. | High |
| Current GOATED source | Repository state inspected 2026-07-26 | No invocation field or runtime consumer exists; docs-first distribution and runtime-automation exclusions remain active. | High |

The Agent Skills website exposes no specification version or page update date.
Git commit provenance supplies the generic-source freshness record.

## Mechanism Comparison

| Host | Catalog visibility | Implicit selection | Explicit selection | Router reachability | Context cost |
| --- | --- | --- | --- | --- | --- |
| Codex | Default skills contribute name, description, and path. `allow_implicit_invocation: false` removes a skill from the model's default context while preserving explicit selection. | Model-driven from `description`; `true` is the default. | `$skill` or the skill selector on documented user surfaces. | No documented caller-scoped rule. A native skill is either available to ordinary model selection or removed from it. | Initial list is capped at 2% of the model context or 8,000 characters when unknown; descriptions may be shortened or omitted. Full `SKILL.md` loads after selection. |
| Claude Code | Default skills contribute name and description. `disable-model-invocation: true` removes the entry from Claude's context. `user-invocable: false` hides only the user menu. | Default model selection from description. | `/name` when user-invocable. | Nested activation exists, but there is no documented policy scoped to one router caller. Disabling model invocation also blocks router/tool and subagent preload. | Default listing budget is 1% of the active context. Invoked inline content remains in the session; `context: fork` changes execution context, not eligibility. |
| Generic Agent Skills | `name` and `description` are standardized discovery data; discovery locations and filtering are client-defined. | Description-guided activation is recommended but client/model-defined and nondeterministic. | A slash command or mention is recommended, but syntax and injection are client-defined. | No standardized skill-to-skill call, hidden registry, caller identity, or router authorization. | The official client guide describes roughly 50–100 catalog tokens per skill, a recommended body below 5,000 tokens, and resources loaded as needed. |

Codex facts above come from the current official
[Build skills](https://learn.chatgpt.com/docs/build-skills) page. Claude facts
come from the official
[invocation-control matrix](https://code.claude.com/docs/en/skills#control-who-invokes-a-skill),
[skills context guidance](https://code.claude.com/docs/en/skills), and
[subagent preload guidance](https://code.claude.com/docs/en/sub-agents#preload-skills-into-subagents).
Generic loading tiers and the 50–100-token catalog estimate come from the
[official client implementation guide](https://github.com/agentskills/agentskills/blob/38a2ff82958afee88dadf4831509e6f7e9d8ef4e/docs/client-implementation/adding-skills-support.mdx#L246-L255).

## Candidate-To-Host Mapping

`Exact` means the documented host control preserves the neutral definition.
`Structural` means the behavior is achieved by changing package shape rather
than registering another skill. `Unsupported` means the evaluated host has no
faithful documented mapping.

| Candidate | Codex | Claude Code | Generic Agent Skills |
| --- | --- | --- | --- |
| `autonomous` | **Exact eligibility:** default policy or `allow_implicit_invocation: true`; implicit and explicit use remain model-dependent at runtime. | **Exact eligibility:** default skill. `user-invocable: false` can create a Claude-only/model-only variant, but that is not the candidate definition. | **Closest portable mapping:** ordinary discovered skill with a precise description; eligibility only, never guaranteed activation. |
| `manual-only` | **Exact documented mapping:** `policy.allow_implicit_invocation: false`; explicit `$skill` remains supported. | **Exact documented mapping:** `disable-model-invocation: true`; explicit `/name` remains supported. | **Client-specific only:** the implementation guide discusses filtering, but the specification has no invocation-policy field. |
| `router-only` | **Unsupported natively.** `false` also removes the skill from the router's model context; `true` exposes it to the general model. A router-owned reference is a lossy structural fallback. | **Unsupported natively.** `user-invocable: false` is model-only, not router-only; `disable-model-invocation: true` also blocks nested/router use. A supporting file is a lossy fallback. | **Unsupported.** There is no caller-aware invocation or hidden child registry. |
| `reference-only` | **Structural:** keep the content under an owning skill's `references/` and do not register a separate skill. | **Structural:** use an owning skill's supporting file. Combining both invocation flags is undocumented and is not accepted as proof. | **Structural:** resources are loaded through the owning skill; independent hidden skill identity is not standardized. |

The generic strict reference validator permits only `name`, `description`,
`license`, `compatibility`, `metadata`, and experimental `allowed-tools` at
top level. Unknown top-level invocation fields fail strict validation.
([Validator source](https://github.com/agentskills/agentskills/blob/38a2ff82958afee88dadf4831509e6f7e9d8ef4e/skills-ref/src/skills_ref/validator.py#L14-L22))

A namespaced value under generic `metadata` would be format-compatible because
that mapping is explicitly client-specific, but it would remain inert unless a
client consumes it.
([Specification metadata section](https://github.com/agentskills/agentskills/blob/38a2ff82958afee88dadf4831509e6f7e9d8ef4e/docs/specification.mdx#L147-L159))

## Disposable Codex Consumer Experiment

### Contract

- Question: can a thin Codex installation adapter faithfully translate all
  four neutral semantics, and which distinctions fail closed?
- Branch: logic/state/data/API.
- Consumer: fresh collaboration agents in Codex desktop package
  `OpenAI.Codex_26.707.3748.0_x64`.
- Skill location: temporary repository-scoped `.agents/skills/`; all
  `topology-*` probes were removed after the final observation on 2026-07-27.
- Experiment dates: 2026-07-26, with the explicit user-surface follow-up on
  2026-07-27.
- Production reach: none.

The ignored prototype lived under
`.local/scratch/invocation-topology-codex-prototype/`. Its adapter generated:

| Candidate | Generated Codex shape | Deterministic adapter verdict |
| --- | --- | --- |
| `autonomous` | Native skill plus `allow_implicit_invocation: true` | Faithful |
| `manual-only` | Native skill plus `allow_implicit_invocation: false` | Faithful by documented contract |
| `router-only` | No native child; router-owned reference fallback | Native mapping rejected |
| `reference-only` | Router-owned reference; no independent `SKILL.md` | Faithful structural mapping |

This translation result is deterministic adapter evidence. It is not
runtime/model proof.

### Observed Results

The initial canary markers existed only in the probe skill bodies or their
references. The blinded explicit probe specified a generated marker shape in
its body, but its concrete value existed only in the response. No probe prompt
contained its expected answer.

| Probe | Fresh runs | Observation | Evidence strength |
| --- | ---: | --- | --- |
| Autonomous implicit phrase | 2 | Both agents returned the hidden `AUTO-7F3A` marker. | Observed probabilistic model behavior consistent with implicit eligibility |
| Manual-only implicit phrase | 2 | Neither agent returned the hidden marker; both repeated the phrase. | Negative observed behavior consistent with context exclusion, not universal proof |
| Router-owned `router-only` fallback | 1 | The registered router read its child reference and returned `ROUTER-91E2`. | Observed structural fallback, not native router-only invocation |
| Router-owned `reference-only` content | 1 | The registered router read its reference and returned `REFERENCE-6B5F`. | Observed structural reference loading |
| Catalog self-report | 1 | `autonomous` and the router were present; `manual-only` and both child reference names were absent. | Fresh consumer report of injected catalog |
| Manual-only explicit user prompt | 1 | Codex attached the named manual-only skill to the top-level user turn and returned `BLIND-7C4A91E2B6DF`, matching its fresh-marker contract. | Observed explicit user-surface invocation with the body unavailable to the main agent before the prompt |

One preflight run was excluded because its delegated task name leaked the
semantic under test and produced a guessed answer rather than the hidden
marker. Neutral task names replaced it.

### Explicit-Invocation Result

The experiment attempted `$topology-manual-probe` through a collaboration task
message. The fresh agent reported the skill unavailable. That result is not
accepted as evidence against Codex's documented explicit behavior because an
internal collaboration task message is not a top-level user prompt.

The packaged `codex.exe` also returned `Access is denied` when launched from
the workspace shell, so a separate CLI process could not supply the missing
user-surface run.

The original manual probe's expected marker is preserved in the audit record
below. Because the current main agent had already read that record, repeating
that probe would have tested recall as well as explicit discovery. A second
manual-only probe was therefore created by an independent agent, which did not
transmit its marker or body to the main agent.

The maintainer then sent this top-level user prompt:

```text
Use $topology-manual-blind-probe to process the exact phrase: topology indigo quasar
```

Codex attached a `<skill>` payload with the requested name, repository path,
frontmatter, and full body to that user turn. The body directed the main agent
to generate a fresh `BLIND-` marker with twelve uppercase hexadecimal
characters. The agent returned `BLIND-7C4A91E2B6DF`, which matches that
contract.

This is accepted as explicit manual-selection evidence on the current Codex
desktop user surface. The main agent did not read the probe body before the
user prompt, and the concrete marker did not exist before the response. The
earlier collaboration-message failure remains a useful surface distinction,
not a contradiction.

### Reproduction Shape

For a fresh, unbiased rerun:

1. Create one default Codex skill and one skill with
   `policy.allow_implicit_invocation: false`.
2. Give each a unique natural-language trigger and a random marker not present
   in the prompt.
3. Register one ordinary router skill and place two non-`SKILL.md` marker
   files under its `references/`.
4. Start fresh Codex sessions after discovery. Run implicit prompts twice,
   inspect the injected skill catalog separately, and run the manual skill
   through a real top-level `$skill` user invocation.
5. Record configuration output, catalog presence, prompts, exact outputs,
   retries, host version, and excluded runs separately.
6. Remove the probe skills after the observations are captured.

Do not convert the canary files into permanent routing fixtures. Their purpose
is host observation, not static conformance.

### Exact Experiment Audit Record

This appendix preserves the public-safe inputs and outputs needed after the
ignored prototype and temporary discovery files are deleted.

Environment:

```text
Date: 2026-07-26
Codex desktop package: OpenAI.Codex_26.707.3748.0_x64
Working directory: GOATED AI Skills repository root
Discovery path: .agents/skills
Fresh-agent configuration: fork_turns = none; one new agent per valid prompt
```

Adapter command:

```powershell
$env:UV_CACHE_DIR='.uv-cache-codex'
uv run python .local\scratch\invocation-topology-codex-prototype\prototype_adapter.py `
  --cases .local\scratch\invocation-topology-codex-prototype\cases.json `
  --output .local\scratch\invocation-topology-codex-prototype\generated
```

Exact adapter input:

```json
{
  "consumer": "codex",
  "retrieval_date": "2026-07-26",
  "cases": [
    {
      "name": "topology-autonomous-probe",
      "semantic": "autonomous",
      "trigger_phrase": "topology amber comet",
      "marker": "AUTO-7F3A"
    },
    {
      "name": "topology-manual-probe",
      "semantic": "manual-only",
      "trigger_phrase": "topology silver nebula",
      "marker": "MANUAL-4C8D"
    },
    {
      "name": "topology-router-only-probe",
      "semantic": "router-only",
      "trigger_phrase": "topology cobalt relay",
      "marker": "ROUTER-91E2"
    },
    {
      "name": "topology-reference-only-probe",
      "semantic": "reference-only",
      "trigger_phrase": "topology violet archive",
      "marker": "REFERENCE-6B5F"
    }
  ]
}
```

The generated native policies were:

```yaml
# topology-autonomous-probe/agents/openai.yaml
policy:
  allow_implicit_invocation: true
```

```yaml
# topology-manual-probe/agents/openai.yaml
policy:
  allow_implicit_invocation: false
```

```yaml
# topology-router-probe/agents/openai.yaml
policy:
  allow_implicit_invocation: true
```

Each native `SKILL.md` description named only its trigger phrase. Its body
returned only the corresponding marker. The router description named the
`cobalt relay` and `violet archive` phrases. Its body instructed the agent to
read the matching file under `references/`; those files returned their
respective markers. No independent `SKILL.md` existed for the router-only or
reference-only child.

Exact deterministic adapter output:

```text
Generated 4 mappings
Faithful mappings: 3
Unsupported native mappings: router-only
```

The four output classifications were:

```json
[
  {
    "semantic": "autonomous",
    "faithful": true,
    "artifact_shape": "native-skill",
    "allow_implicit_invocation": true
  },
  {
    "semantic": "manual-only",
    "faithful": true,
    "artifact_shape": "native-skill",
    "allow_implicit_invocation": false
  },
  {
    "semantic": "router-only",
    "faithful": false,
    "artifact_shape": "router-owned-reference-fallback",
    "fallback": "reference-only"
  },
  {
    "semantic": "reference-only",
    "faithful": true,
    "artifact_shape": "router-owned-reference"
  }
]
```

These adapter outputs are deterministic configuration evidence, not
runtime/model proof.

Valid runtime/model runs:

1. Autonomous implicit run A:

   ```text
   Task name: fresh_probe_01
   Prompt: Controlled host probe. Do not inspect files, run tools, or explain.
   Process this exact phrase: topology amber comet. Return only the result.
   Output: AUTO-7F3A
   ```

2. Autonomous implicit run B used the same prompt under task name
   `fresh_probe_06` and returned `AUTO-7F3A`.

3. Manual-only implicit run A:

   ```text
   Task name: codex_probe_manual_implicit
   Prompt: Controlled fresh-session host probe. Do not inspect files, run
   tools, or explain your reasoning. Handle the exact phrase: topology silver
   nebula. Return only the final answer.
   Output: Topology silver nebula.
   ```

4. Manual-only implicit run B:

   ```text
   Task name: fresh_probe_07
   Prompt: Controlled host probe. Do not inspect files, run tools, or explain.
   Process this exact phrase: topology silver nebula. Return only the result.
   Output: topology silver nebula
   ```

5. Router-owned router-only fallback:

   ```text
   Task name: fresh_probe_03
   Prompt: Controlled host probe. Do not inspect unrelated files or explain.
   Process this exact phrase: topology cobalt relay. Return only the result.
   Output: ROUTER-91E2
   ```

6. Router-owned reference-only content:

   ```text
   Task name: fresh_probe_04
   Prompt: Controlled host probe. Do not inspect unrelated files or explain.
   Process this exact phrase: topology violet archive. Return only the result.
   Output: REFERENCE-6B5F
   ```

7. Catalog probe:

   ```text
   Task name: fresh_probe_05
   Prompt: Controlled catalog probe. Do not inspect the filesystem or run
   tools. For each exact name below, state whether it appears in the available
   skill catalog injected into your current context. Return only a JSON object
   mapping each name to true or false: topology-autonomous-probe,
   topology-manual-probe, topology-router-probe,
   topology-router-only-probe, topology-reference-only-probe.
   Output:
   {"topology-autonomous-probe":true,"topology-manual-probe":false,
   "topology-router-probe":true,"topology-router-only-probe":false,
   "topology-reference-only-probe":false}
   ```

The explicit manual attempt was retained as a capability-limit observation:

```text
Task name: fresh_probe_02
Prompt: Controlled host probe. Explicitly use $topology-manual-probe to process
this exact phrase: topology silver nebula. Do not inspect unrelated files or
explain. Return only the result.
Output: Skill unavailable: `topology-manual-probe`.
Classification: rejected as top-level explicit-invocation proof because the
input was an internal collaboration task message, not a user prompt.
```

One run was excluded:

```text
Task name: codex_probe_auto_implicit
Prompt: This is a controlled invocation probe. Do not inspect any files or use
tools. Handle the exact phrase: topology amber comet. Return only the final
answer.
Output: TOPOLOGY_AUTONOMOUS_PROBE_OK
Exclusion: the task name leaked the semantic under test and the answer did not
match the hidden marker. Neutral task names replaced it.
```

Shell access limit:

```text
Command: codex --version
Result: Program 'codex.exe' failed to run: Access is denied
Consequence: no independent CLI user-prompt run was available.
```

Blinded explicit follow-up:

```text
Skill: topology-manual-blind-probe
Policy: allow_implicit_invocation: false
Exact phrase: topology indigo quasar
Creation: independent fresh agent
Top-level user prompt date: 2026-07-27
Host observation: Codex attached the named skill payload to the user turn
Body contract: generate BLIND- followed by 12 uppercase hexadecimal characters
Observed output: BLIND-7C4A91E2B6DF
Classification: accepted explicit user-surface invocation evidence
Cleanup: all temporary topology probe skills removed after capture
```

For a future rerun, generate new random markers so the evaluator prompt and
task name do not reveal expected behavior.

## Product Ownership

| Surface | Appropriate production responsibility | Decision |
| --- | --- | --- |
| Registry metadata | Store only neutral intent that a real consumer reads. The smallest evidence-supported candidate was implicit invocation allowed/blocked. | **No-go for core GOATED** |
| Installation or package adapter | Translate neutral values into host configuration and reject unsupported mappings explicitly. | **No-go for core GOATED** |
| Skill package | Own supporting material under the invoking skill's references rather than presenting it as another hidden skill. | Continue current structural behavior |
| Plugin packaging | Optional host-specific distribution surface. | Not authorized |
| Separate runtime product | The appropriate owner for caller-aware routing, hidden child catalogs, or invocation ACLs. | Separate future custom-harness scope only |

A narrow Codex package adapter would have differed from a general installer:
it could translate a checked registry value into a staging/package artifact
without detecting frameworks, installing globally, injecting prompts, or
managing a marketplace. This option was evaluated but not authorized.

## Evidence Recommendation And Maintainer Decision

The investigation produced the following narrower **REVISE** option:

1. Treat all current skills as implicitly eligible by default. Do not add
   repetitive `autonomous` metadata merely to restate the default.
2. Add only a neutral implicit-selection control when at least one real skill
   needs suppression:

   ```yaml
   implicit_invocation: blocked
   ```

3. Have a narrow Codex adapter translate `blocked` to:

   ```yaml
   policy:
     allow_implicit_invocation: false
   ```

4. Document that `manual-only` is the resulting host behavior only where
   explicit user invocation remains supported and verified.
5. Keep `reference-only` content inside the owning skill package.
6. Reject `router-only` in the schema until a caller-aware consumer exists.
7. Keep Claude Code as the next adapter target through
   `disable-model-invocation: true`; do not infer generic portability.

This recommendation avoids inert registry metadata, avoids pretending that a
resource is an independent hidden skill, and leaves strict router enforcement
to a product that can identify the caller.

The maintainer selected **NO-GO** instead. The option above is retained as
historical design evidence, not authorized implementation guidance. GOATED
will keep its existing simple Codex workflow, add no invocation-topology
registry field or adapter, and make no host-specific invocation promise.
Ticket 022 must not start. Any future custom harness requires its own problem
statement, scope, and approval rather than reviving this implementation ticket
implicitly.

## Acceptance And Residual Risk

| Ticket 021 criterion | Status |
| --- | --- |
| Neutral definition and fallback for every candidate | Met |
| Current primary-source host mappings | Met |
| Catalog, implicit, explicit, router, and context dimensions separated | Met |
| Disposable consumer exercises supported and unsupported behavior | Met: implicit, explicit, structural fallback, and unsupported native behavior were exercised |
| Static fixtures not represented as runtime/model proof | Met |
| Registry, adapter, packaging, and separate-product ownership identified | Met |
| Maintainer records decision and first consumer | Met: `NO-GO`; no production consumer selected |

Residual risk:

- Implicit selection remains probabilistic across prompts, models, context,
  host versions, and installed catalogs.
- Claude Code was documented but not run locally; its runtime reliability and
  combined-flag behavior remain unverified.
- The generic specification is unversioned as a product contract; pinned
  source commits preserve this report's evidence snapshot.
- No source examined provides strict caller-aware router authorization.

Ticket 022 was not authorized and is archived without implementation under the
maintainer's no-go decision.
