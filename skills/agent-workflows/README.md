# Agent Workflows

Skills in this category define reusable operating patterns for installed agent workflows: skill routing, session starts, target-project context maps, context calibration, standards calibration, instruction integration, handoffs, and skill creation and porting.

They should be portable by default, avoid assuming one instruction-file convention, and document adapter notes only when a specific agent framework requires them.

## Implemented Skills

- `using-goated-ai-skills` - routes installed GOATED skill stacks to the right workflow while respecting user and project instructions.
- `session-start-progressive-disclosure` - starts sessions with the smallest useful context and routes the next workflow step.
- `context-matrix-map` - creates source-grounded context maps for future agents.
- `project-context-calibration` - creates or refreshes durable project context language.
- `project-standards-calibration` - records documented standards, inferred conventions, user-confirmed preferences, and unresolved questions.
- `agent-instructions-integrator` - routes agent instruction artifacts to installed skills and durable project artifacts.
- `handoff` - writes compact continuity notes for future agents or sessions.
- `framework-agnostic-skill-creator` - creates GOATED skills from clarified intent and ports existing workflows into GOATED shape.
