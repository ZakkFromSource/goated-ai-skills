# Agent Workflows

Skills in this category define reusable operating patterns for installed agent workflows: session starts, target-project context maps, context calibration, standards calibration, instruction integration, handoffs, and skill porting.

They should be portable by default, avoid assuming one instruction-file convention, and document adapter notes only when a specific agent framework requires them.

## Implemented Skills

- `session-start-progressive-disclosure` - starts sessions with the smallest useful context and routes the next workflow step.
- `context-matrix-map` - creates source-grounded context maps for future agents.
- `project-context-calibration` - creates or refreshes durable project context language.
- `project-standards-calibration` - records documented, inferred, and user-confirmed project standards.
- `agent-instructions-integrator` - routes agent instruction artifacts to installed skills and durable project artifacts.
- `handoff` - writes compact continuity notes for future agents or sessions.
- `framework-agnostic-skill-porting` - converts existing workflows into GOATED skill shape until issue `029` renames and expands it.
