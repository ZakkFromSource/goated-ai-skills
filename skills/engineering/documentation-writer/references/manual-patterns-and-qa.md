# Manual Patterns And QA

Read this reference when choosing a durable documentation shape, deciding whether a separate AI-facing guide is warranted, or checking a draft before closeout.

These are patterns, not mandatory templates. Preserve the target project's existing documentation conventions when they are discoverable.

## Documentation Type Patterns

### User Manual Or Product Guide

Use when the reader wants to understand and use a product, feature, workflow, or tool.

Useful sections:

- purpose and audience;
- prerequisites, permissions, or setup;
- key concepts and terms;
- core tasks in the order readers perform them;
- examples, expected results, and screenshots when available;
- limitations, caveats, and known gaps;
- troubleshooting or next reads.

Keep the writing task-oriented. Explain what the reader can do, what they need before starting, and how they know it worked.

### Operator Guide, Runbook, Or Troubleshooting Guide

Use when the reader owns operation, recovery, maintenance, support, or incident response.

Useful sections:

- when to use the guide and when not to use it;
- required access, environment, safety limits, and rollback expectations;
- normal operating procedure;
- failure symptoms and safe diagnosis steps;
- recovery or mitigation steps with verification after each meaningful action;
- escalation path, owner, and follow-up records;
- residual risks or cases that require human judgment.

Do not invent operational commands. If a command, dashboard, log, or rollback step is not verified, label it as an assumption or gap.

### Onboarding Guide

Use when a new human contributor, operator, teammate, or user needs a first successful path.

Useful sections:

- who the guide is for;
- fastest safe setup or orientation path;
- project or product map at the level the reader needs;
- first tasks and expected proof they succeeded;
- conventions, vocabulary, and common mistakes;
- where to go next.

Avoid overwhelming first-time readers with every architecture detail or historical decision. Link deeper docs instead.

### Durable Product Doc

Use when documenting stable product behavior, product rules, concepts, user flows, or feature intent.

Useful sections:

- audience and problem solved;
- product concepts, states, roles, permissions, or workflows;
- source-of-truth links such as PRDs, issues, specs, code paths, tests, or screenshots;
- current behavior and intentionally unsupported behavior;
- edge cases, constraints, and known gaps;
- verification notes or examples.

Do not use product docs to replace unsettled PRDs. If behavior or intent is not decided, route to `write-a-prd` or record the question.

### AI-Facing Guide

Use when repeated agent or model work would benefit from a separate guide written for fast context loading and task routing.

Create an AI-facing guide when:

- the user requests one;
- repeated agent work is expected for the documented area;
- the human manual is too narrative or broad for fast agent routing;
- agents need source-of-truth links, constraints, commands, glossary, or safe next reads.

If no project convention exists, default to `docs/agents/<topic>-ai-guide.md`. Do not default to a `context` filename when the project already uses context docs for durable vocabulary, source maps, or routing.

Useful sections:

- purpose and when an agent should load the guide;
- audience and task surfaces covered;
- source-of-truth links and freshness notes;
- key workflows, states, constraints, and glossary terms;
- common agent tasks and safe first reads;
- verification commands or manual checks;
- known gaps, owner questions, and doc-sync risks.

Keep AI-facing guides separate from human-facing manuals by default. They should not duplicate the whole manual, hide private context, or become the only place important product behavior is documented.

## Location Defaults

Prefer the project's existing documentation convention. Search root docs, docs indexes, agent docs, feature docs, runbooks, and README links before choosing a new path.

When no convention exists:

- human-facing manuals and guides default to `docs/<topic>-guide.md`;
- AI-facing guides default to `docs/agents/<topic>-ai-guide.md`;
- record the fallback as an assumption in the final report.

Use kebab-case topic names unless the project clearly uses another naming style.

## Evidence Checklist

Before writing, inspect the smallest useful set of:

- existing docs, README files, docs indexes, and prior guides;
- source files, tests, schemas, configs, commands, or generated references;
- PRDs, issues, ADRs, decision notes, support notes, screenshots, or user-provided materials;
- project context, standards, glossary, and agent docs when they affect terminology or location;
- docs tooling or verification commands when the project defines them.

For each important claim, know whether it is:

- verified by current source evidence;
- copied from existing docs but not re-verified;
- inferred from partial evidence;
- an explicit user-provided fact;
- a gap or unresolved question.

## QA Checklist

Before claiming the document is ready, check:

- The audience and doc type are named.
- Human-facing docs are readable, task-oriented, and not overloaded with model notes.
- AI-facing guides are separate, concise, source-linked, and named as guides.
- Major claims link to or name source evidence.
- Commands, paths, permissions, recovery steps, and product behavior were verified or marked as assumptions.
- Private data, credentials, raw transcripts, sensitive context, and real user data are absent.
- Stale or conflicting source evidence is called out instead of smoothed over.
- Local links and nearby headings were re-read.
- Static-site, publishing, hosting, generated navigation, and deployment scope did not creep in.
- Any broader documentation drift is routed to `doc-sync`.
- Skipped checks and remaining gaps are listed in the final report.

## Common Anti-Patterns

Avoid these documentation failures:

- FAQ pileup: unrelated questions accumulate until readers cannot find the main path.
- Transcript dump: raw conversation becomes documentation without source checking or structure.
- Agent notes in the manual: human docs become awkward because model-oriented routing notes are mixed in.
- Context-name confusion: AI-facing guides are named like context source-of-truth docs when the project uses context docs for vocabulary or source routing.
- Invented certainty: unverified product behavior, commands, support promises, or operational steps are stated as facts.
- Drift laundering: docs are updated to make an implementation mismatch look intentional.
- Static-site creep: a manual request turns into publishing, hosting, generated navigation, or deployment work without approved scope.
