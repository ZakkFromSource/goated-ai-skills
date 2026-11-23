"""Run a conformance scenario against the Claude Code adapter (Ticket 079).

A scenario (`stack/fixtures/enforcement/`) is written in the event model's
terms and names no harness. This module is the bridge: it maps each step to
what Claude Code records and the hook it runs, using the synthetic sessions of
`claude_code_adapter_support`, and maps each hook's output back to a decision.
It also builds the event-model request each judged step stands for, so the
caller can check the scenario against the schema. `core_scenarios` runs the
same scenarios against the shared core directly (Ticket 081).
"""

from __future__ import annotations

import copy
import json
import os
import re
from pathlib import Path
from typing import NamedTuple
from unittest import mock

from claude_code_adapter_support import (
    REPO_ROOT, Session, git_branch_with_change, grow_branch, parse, reason,
)
from enforcement_support import expectation_mismatch, item_labels
from goated_core import wording

REGISTRY = REPO_ROOT / "stack" / "goated-stack.yaml"

HOLD_LINE = re.compile(r"^goated-hold: ([a-z]+(?:-[a-z]+)*) \| (strict|justified-skip)$", re.M)
ADAPTER_NAME = "GOATED Claude Code adapter"
FAIL_OPEN = "so this action was allowed without checks."
OVERRIDE_RECORDED = "recorded your override"
# The notices a prompt's additionalContext may carry besides session notices,
# each told by words its text holds.
PROMPT_NOTICES = (("override_recorded", OVERRIDE_RECORDED),
                  ("route_continued", "runs as `goated-route: continue`"))
# The notices a pending call's additionalContext may carry, each told by words its text holds.
PENDING_CALL_NOTICES = (("skip_carried", "through without a read of"),
                        ("reads_owed", "land before a read of"))
BRIEF_OPENING = "Background (from the session that started this one):"
SESSION_SOURCES = {"new": "startup", "resumed": "resume", "after_compaction": "compact",
                   "cleared": "clear"}
# Claude Code tools for the call kinds that have one tool each.
COMMIT_TOOL = "mcp__git__git_commit"
PULL_REQUEST_TOOL = "mcp__github__create_pull_request"
OTHER_TOOL = "WebFetch"
START_SESSION = "mcp__ccd_session__start_session"
# A built-in agent type with no write, edit, or shell tool.
READ_ONLY_AGENT = "claude-code-guide"
# The subagent a scenario with `setup.agent: subagent` runs in.
SUBAGENT_ID = "scenario1"


class Result(NamedTuple):
    """What a run found: each step whose decision differed, and the request
    each judged step stands for."""

    failures: list[str]
    requests: list[dict]


def run_scenario(root: Path, scenario: dict) -> Result:
    """Run `scenario` in a fresh synthetic session under `root`."""

    return _Run(root, scenario).run()


class _Run:
    def __init__(self, root: Path, scenario: dict) -> None:
        self.s = Session(root)
        self.s.project.mkdir(parents=True, exist_ok=True)
        self.scenario = scenario
        self.turns: list[dict] = []
        self.failures: list[str] = []
        self.requests: list[dict] = []
        self.outside = root / "outside"
        # The repo's registry, where an installed adapter finds its distribution's.
        self.s.config.registry_path = REGISTRY
        setup = scenario.get("setup", {})
        for skill in setup.get("installed_skills", []):
            folder = self.s.config.home / ".claude" / "skills" / skill
            folder.mkdir(parents=True, exist_ok=True)
            (folder / "SKILL.md").write_text(f"---\nname: {skill}\n---\n", encoding="utf-8")
        if "branch_changed_lines" in setup:
            git_branch_with_change(self.s.project, setup["branch_changed_lines"],
                                   origin_url=setup.get("origin_url"))
        # In a subagent, Claude Code runs no prompt hook, and each call's hook
        # input names the agent; its entries go to its own transcript.
        self.in_subagent = setup.get("agent") == "subagent"
        self.agent = {"role": "subagent", "id": SUBAGENT_ID} if self.in_subagent \
            else {"role": "main"}
        self.subagent_fields = {"agent_id": SUBAGENT_ID, "agent_type": "general-purpose"} \
            if self.in_subagent else {}
        if self.in_subagent:
            self.s = self.s.subagent(SUBAGENT_ID)
        # The agents this session's spawns started, oldest first.
        self.agents: list[str] = []

    def run(self) -> Result:
        # Claude Code's hooks run as its user, so the home a leading `~`
        # names is the session's own: the synthetic home.
        home = str(self.s.config.home)
        with mock.patch.dict(os.environ, {"HOME": home, "USERPROFILE": home}):
            return self._run_steps()

    def _run_steps(self) -> Result:
        steps = self.scenario["steps"]
        for number, step in enumerate(steps, 1):
            self.number = number
            if "prompt" in step:
                # A skill a person invokes is the prompt that names it.
                after = steps[number] if number < len(steps) else {}
                self._prompt(step, invokes=after.get("skill_invoked"))
            elif "reply" in step:
                self.s.say(step["reply"])
                self._entry({"type": "reply_text", "text": step["reply"]})
            elif "call" in step:
                self._call(step)
            elif "skill_invoked" in step:
                self._skill_invoked(step["skill_invoked"],
                                    before=steps[number - 2] if number > 1 else {})
            elif "agent_finished" in step:
                self._agent_finished(step["agent_finished"])
            elif "compaction" in step:
                self._compaction()
            elif "branch_grows" in step:
                grow_branch(self.s.project, step["branch_grows"])
            elif "turn_end" in step:
                self._turn_end(step)
            elif "session_start" in step:
                self._session_start(step)
            else:
                raise ValueError(f"step {number}: the bridge cannot run {sorted(step)}")
        return Result(self.failures, self.requests)

    # Steps --------------------------------------------------------------

    def _prompt(self, step: dict, invokes: str | None = None) -> None:
        """Record a prompt. `invokes` is the skill the next step says a person
        invoked: Claude Code records the prompt as that skill's command, with
        the prompt's text as its arguments."""

        prompt = step["prompt"]
        text = self._expand(prompt["text"])
        for n, pasted in enumerate(prompt.get("pasted", []), 1):
            text += f'\n<pasted_content id="p{n}">\n{pasted}\n</pasted_content id="p{n}">'
        author, continues = prompt["author"], step.get("continues", False)
        if invokes is not None and (author != "person" or continues or self.in_subagent):
            raise ValueError(f"step {self.number}: Claude Code records a skill a person "
                             "invokes only as a prompt a person types that opens a turn")
        if self.in_subagent:
            if author != "session" or continues or prompt.get("starts_session"):
                raise ValueError(f"step {self.number}: in a subagent the bridge records only "
                                 "its parent's prompts that open a turn")
            output = self.s.prompt(text, hook=False)
        elif invokes is not None:
            output = self.s.prompt(f"<command-message>{invokes}</command-message>\n"
                                   f"<command-name>/{invokes}</command-name>\n"
                                   f"<command-args>{text}</command-args>")
        elif author == "person" and not continues:
            output = self.s.prompt(text)
        elif author == "session" and prompt.get("starts_session"):
            output = self.s.prompt(f"{BRIEF_OPENING}\n\n{text}", origin=None,
                                   turnOrigin="host_synthetic", promptSource="sdk")
        elif author == "session" and continues:
            # A continuing prompt from another agent is a report from one this
            # session spawned: the latest spawn whose result names its agent.
            if not self.agents:
                raise ValueError(f"step {self.number}: a continuing session prompt is a "
                                 "spawned agent's report, and no spawn named an agent")
            output = self.s.peer(text, handback=True, sender=self.agents[-1])
        elif author == "session":
            output = self.s.peer(text)
        elif author == "host" and continues:
            output = self.s.notify(text)
        elif author == "host":
            # A prompt the desktop app writes itself opens a turn.
            output = self.s.prompt(text, origin=None, turnOrigin="host_synthetic")
        elif author == "unknown" and not continues:
            # An origin kind the adapter does not know.
            output = self.s.prompt(text, origin={"kind": "unrecognized"})
        else:
            raise ValueError(f"step {self.number}: the bridge cannot record a "
                             f"{'continuing ' if continues else ''}{author} prompt")
        if continues:
            self._entry(prompt)
        else:
            self.turns.append({"key": f"t{len(self.turns) + 1}", "opener": prompt,
                               "entries": []})
        self._judged(step.get("expect"), {"type": "prompt_submitted"},
                     _decision(parse(output), "context"))

    def _call(self, step: dict) -> None:
        call = step["call"]
        tool, tool_input = self._tool(call)
        tool_id, output = self.s._judge(tool, tool_input, **self.subagent_fields)
        self._judged(step.get("expect", {"decision": "allow"}),
                     {"type": "pending_call", "call": call}, _decision(output, "tool"))
        held = reason(output)
        result = ({"ok": False, "held": True, "output": held} if held
                  else step.get("result", {"ok": True}))
        if "expect_after" in step:
            response = {"success": True} if result["ok"] else {"error": "failed"}
            after = parse(self.s.hook("PostToolUse", tool_name=tool, tool_input=tool_input,
                                      tool_use_id=tool_id, tool_response=response))
            self._judged(step["expect_after"],
                         {"type": "finished_call", "call": call, "result": result},
                         _decision(after, "context"))
        self._record(tool_id, call, result)
        self._entry({"type": "call", "call": call, "result": result})
        if result.get("agent"):
            self.agents.append(result["agent"]["id"])

    def _skill_invoked(self, skill: str, before: dict) -> None:
        """Claude Code adds the body of a skill invoked by its command after
        the prompt (`_prompt`), which proves the load. `before` is the step
        before this one, which must be that prompt."""

        prompt = before.get("prompt") or {}
        if prompt.get("author") != "person" or before.get("continues"):
            raise ValueError(f"step {self.number}: Claude Code records a skill a person "
                             "invokes only right after the prompt that invokes it, one a "
                             "person types that opens a turn")
        self.s._append({"type": "user", "isMeta": True, "message": {"role": "user", "content": [
            {"type": "text", "text": f"Base directory for this skill: {skill}"}]}})
        self._entry({"type": "skill_invoked", "skill": skill})

    def _agent_finished(self, agent_id: str) -> None:
        """Claude Code reports a background agent's end as a task notification
        naming the agent, which continues the turn."""

        if self.in_subagent:
            raise ValueError(f"step {self.number}: a subagent's own background agents "
                             "are not recorded by the bridge")
        self.s.notify("Done.", task_id=agent_id)
        self._entry({"type": "agent_finished", "agent_id": agent_id})

    def _compaction(self) -> None:
        if self.in_subagent:
            # A subagent's compaction is recorded in its own transcript, and
            # Claude Code runs no session-start hook for it.
            self.s._append({"type": "system", "subtype": "compact_boundary",
                            "content": "Conversation compacted"})
            self.s._append({"type": "user", "isCompactSummary": True,
                            "message": {"role": "user", "content": "Summary of earlier work."}})
        else:
            self.s.compact()
        self.turns.append({"key": f"t{len(self.turns) + 1}",
                           "opener": {"type": "compaction"}, "entries": []})

    def _turn_end(self, step: dict) -> None:
        if self.in_subagent:
            # Claude Code ends a subagent's turn with its own hook event. The
            # adapter registers no SubagentStop hook, so Claude Code never
            # runs it, and the step is trivially allowed; the bridge calls it
            # to show the adapter would allow it if it were registered.
            output = parse(self.s.hook("SubagentStop", stop_hook_active=False,
                                       last_assistant_message="", **self.subagent_fields))
        else:
            output = parse(self.s.hook("Stop", stop_hook_active=False,
                                       last_assistant_message=""))
        decision = _decision(output, "stop")
        self._judged(step.get("expect", {"decision": "allow"}), {"type": "turn_end"}, decision)
        if decision["decision"] == "allow":
            self._entry({"type": "turn_ended"})

    def _session_start(self, step: dict) -> None:
        event = {"type": "session_start", "source": step["session_start"]}
        if self.in_subagent:
            # A subagent starts with its own hook event. The adapter registers
            # no SubagentStart hook, so the step is trivially allowed, as for
            # SubagentStop above.
            output = parse(self.s.hook("SubagentStart", **self.subagent_fields))
        else:
            output = parse(self.s.hook("SessionStart",
                                       source=SESSION_SOURCES[step["session_start"]]))
        self._judged(step.get("expect"), event, _decision(output, "context"))

    # Claude Code's side -------------------------------------------------

    def _tool(self, call: dict) -> tuple[str, dict]:
        """The Claude Code tool and input that make `call`."""

        kind, line = call["kind"], call.get("line_text")
        if "action" in call:
            raise ValueError(f"step {self.number}: Claude Code gives each call its own "
                             "action key, from its tool and input")
        # Claude Code reads a line only from a shell or agent call's
        # description and a Skill call's args; anything else cannot carry one.
        if line is not None and not (kind in ("shell_command", "skill_load")
                                     or (kind == "spawn" and call["starts_now"])):
            raise ValueError(f"step {self.number}: Claude Code has no field to carry "
                             f"line_text on a {kind} call")
        if kind == "file_write":
            path, edits = self._expand(call["path"]), call["edits"]
            if call.get("whole_file"):
                if len(edits) != 1 or edits[0]["removed"] is not None or edits[0]["added"] is None:
                    raise ValueError(f"step {self.number}: Claude Code writes a whole file "
                                     "as one edit that adds the content")
                return "Write", {"file_path": path, "content": edits[0]["added"]}
            if call.get("creates"):
                # Claude Code lets an Edit with empty old text make a file.
                if len(edits) != 1 or edits[0]["removed"] != "" or edits[0]["added"] is None:
                    raise ValueError(f"step {self.number}: Claude Code makes a file by an "
                                     "edit only with one edit that removes nothing")
                return "Edit", {"file_path": path, "old_string": "",
                                "new_string": edits[0]["added"]}
            if any(e["removed"] is None for e in edits):
                # Only a notebook edit writes text without saying what it replaces.
                if len(edits) != 1:
                    raise ValueError(f"step {self.number}: Claude Code leaves replaced text "
                                     "unknown only in a notebook edit of one cell")
                added = edits[0]["added"]
                return "NotebookEdit", {"notebook_path": path, "cell_id": "cell-1", **(
                    {"new_source": added} if added is not None else {"edit_mode": "delete"})}
            if any(e["added"] is None for e in edits):
                raise ValueError(f"step {self.number}: Claude Code shows the text of every "
                                 "edit but a notebook cell's")
            pairs = [{"old_string": e["removed"], "new_string": e["added"]} for e in edits]
            if len(pairs) == 1 and pairs[0]["old_string"] != "":
                return "Edit", {"file_path": path, **pairs[0]}
            # A MultiEdit never makes a file, so an edit that removes nothing
            # without `creates` goes in one.
            return "MultiEdit", {"file_path": path, "edits": pairs}
        if kind == "shell_command":
            tool_input = {"command": self._expand(call["command"])}
            if line:
                tool_input["description"] = line
            if call.get("background"):
                tool_input["run_in_background"] = True
            return ("PowerShell" if call["shell"] == "powershell" else "Bash"), tool_input
        if kind == "skill_load":
            return "Skill", {"skill": call["skill"], **({"args": line} if line else {})}
        if kind == "file_read":
            return "Read", {"file_path": self._expand(call["path"]),
                            **({} if call["whole"] else {"limit": 20})}
        if kind == "spawn":
            if not call["starts_now"]:
                initiation = "own_initiative" if call["brief"] else "offer"
                return START_SESSION, {"initiation": initiation, "title": "Task",
                                       "prompt": call["brief"]}
            if call.get("separate"):
                if line or call.get("read_only"):
                    raise ValueError(f"step {self.number}: Claude Code's side session "
                                     "carries no line and no agent type")
                return START_SESSION, {"initiation": "user_asked", "title": "Task",
                                       "prompt": call["brief"]}
            tool_input = {"prompt": call["brief"],
                          "subagent_type": READ_ONLY_AGENT if call.get("read_only")
                          else "general-purpose"}
            if line:
                tool_input["description"] = line
            return "Agent", tool_input
        if kind == "commit":
            return COMMIT_TOOL, {"message": call.get("message")}
        if kind == "pull_request":
            tool_input = {"title": "Change", "body": "What changed."}
            tool_input.update({key: call[key] for key in ("base", "head") if key in call})
            if "repository" in call:
                tool_input["owner"], tool_input["repo"] = call["repository"].rsplit("/", 1)
            return PULL_REQUEST_TOOL, tool_input
        return OTHER_TOOL, {"url": "https://example.invalid"}

    def _record(self, tool_id: str, call: dict, result: dict) -> None:
        """Record the call's result as Claude Code does, for its kind."""

        text = result.get("output") or ("ok" if result["ok"] else "Exit code 1\nfailed")
        if result.get("ran") is False and not result.get("held"):
            if result["ok"]:
                raise ValueError(f"step {self.number}: a call that never ran did not succeed")
            # How Claude Code records a call the person refused.
            text = ("The user doesn't want to proceed with this tool use. The tool use was "
                    "rejected (eg. if it was a file edit, the new_string was NOT written to "
                    "the file).")
        extra = None
        agent = result.get("agent")
        if call["kind"] == "skill_load" and result["ok"]:
            extra = {"toolUseResult": {"success": True, "commandName": call["skill"]}}
        elif agent:
            extra = {"toolUseResult": {
                "status": "async_launched" if agent.get("background") else "completed",
                "agentId": agent["id"]}}
        self.s._tool_result(tool_id, text, is_error=not result["ok"], extra=extra)
        if call["kind"] == "skill_load" and result["ok"]:
            self.s._append({"type": "user", "isMeta": True, "sourceToolUseID": tool_id,
                            "message": {"role": "user", "content": [
                                {"type": "text",
                                 "text": f"Base directory for this skill: {call['skill']}"}]}})

    def _expand(self, text: str) -> str:
        """Fill the placeholder `{outside}`: a folder outside the project and
        any checkout, as a scratch file's folder is."""

        return text.replace("{outside}", self.outside.as_posix())

    # The event model's side ---------------------------------------------

    def _entry(self, entry: dict) -> None:
        if not self.turns:
            raise ValueError(f"step {self.number}: an entry before any prompt")
        self.turns[-1]["entries"].append(entry)

    def _judged(self, expect: dict | None, event: dict, got: dict) -> None:
        """Record the request this step stands for, and compare its decision
        with `expect`; with no `expect`, the step is not checked."""

        self.requests.append({
            "event_model": 5,
            "session": {"id": self.s.session_id, "agent": self.agent},
            "project": {"folders": [self.s.project.as_posix()],
                        "working_folder": self.s.cwd.as_posix(),
                        "home": self.s.config.home.as_posix()},
            "turns": copy.deepcopy(self.turns),
            "event": event,
        })
        mismatch = expectation_mismatch(expect, got)
        if mismatch is not None:
            self.failures.append(
                f"step {self.number} ({event['type']}): expected {mismatch[0]}, got {got}")


def _decision(output: dict, shape: str) -> dict:
    """The decision a hook's output stands for. `shape` names where the hook
    puts a hold: `tool` (a denied call), `stop` (a blocked end), or `context`
    (a hook that never holds). `items` are the closeout hold's item labels."""

    shown = json.dumps(output)
    if wording.OPEN in shown or wording.CLOSE in shown:
        raise AssertionError(f"a wording slot was left unfilled: {shown}")
    if shape == "tool":
        text = reason(output)
    elif shape == "stop":
        text = str(output.get("reason", "")) if output.get("decision") == "block" else ""
    else:
        text = ""
    specific = output.get("hookSpecificOutput") or {}
    context = specific.get("additionalContext", "")
    notices = []
    if context:
        if specific.get("hookEventName") == "PostToolUse":
            notices.append("closeout_note")
        elif specific.get("hookEventName") == "PreToolUse":
            # A pending call carries one notice per read gate, of either kind.
            notices += [kind for kind, mark in PENDING_CALL_NOTICES if mark in context]
        elif any(mark in context for _, mark in PROMPT_NOTICES):
            notices += [kind for kind, mark in PROMPT_NOTICES if mark in context]
        else:
            notices.append("session_notice")
    notices += _warnings(output.get("systemMessage", ""), context)
    holds, items = [], []
    found = list(HOLD_LINE.finditer(text))
    for n, match in enumerate(found):
        holds.append((match[1], match[2]))
        if match[1] == "closeout":
            section = text[match.end():found[n + 1].start() if n + 1 < len(found) else None]
            items = item_labels(section)
    return {"decision": "hold" if text else "allow", "holds": holds, "items": items,
            "notices": notices}


def _warnings(message: str, context: str) -> list[str]:
    """The notice kinds the user-facing message adds. It repeats the hook's
    context notices, sentence parts joined by "; ", and adds any warnings;
    only a part the context does not hold is a warning."""

    if not message:
        return []
    if message.endswith(FAIL_OPEN):
        return ["fail_open"]
    body = message.removeprefix(f"{ADAPTER_NAME}: ").removesuffix(".")
    extra = [part for part in body.split("; ") if part.rstrip(".") not in context]
    return ["warning"] if extra else []
