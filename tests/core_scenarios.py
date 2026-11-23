"""Run a conformance scenario against the shared core, through a way in the
caller chooses (Ticket 081).

A scenario (`stack/fixtures/enforcement/`) is written in the event model's
terms. This runner is what a minimal adapter does: it keeps the turns since
the last compaction, sends one request per judged step to a `judge`
function (one request in, one decision out, both JSON-shaped), records a
held call as held, and compares each decision with the step's expectation.
Nothing here knows a harness.
"""

from __future__ import annotations

import copy
import json
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path
from typing import NamedTuple

from enforcement_support import REPO_ROOT, expectation_mismatch, item_labels

CORE_DIR = REPO_ROOT / "adapters" / "core"
if str(CORE_DIR) not in sys.path:
    sys.path.insert(0, str(CORE_DIR))

from goated_core import request as core_request  # noqa: E402

COMMAND = CORE_DIR / "goated_judge.py"
REGISTRY = REPO_ROOT / "stack" / "goated-stack.yaml"
# The agent's own configuration folder, under the scenario's home.
AGENT_FOLDER = ".agent"
# The subagent a scenario with `setup.agent: subagent` runs in.
SUBAGENT_ID = "scenario1"

Judge = Callable[[dict], dict]


class Run(NamedTuple):
    """What a run found: each step whose decision differed from its
    expectation, and every request with the decision it got."""

    failures: list[str]
    exchanges: list[tuple[dict, dict]]


def python_judge(state_dir: Path) -> Judge:
    """The Python call, keeping state under `state_dir`."""

    settings = core_request.Settings(state_dir, registry_path=REGISTRY)
    return lambda request: core_request.decide(request, settings)


def command_judge(state_dir: Path) -> Judge:
    """The command, one process per request, keeping state under `state_dir`."""

    def judge(request: dict) -> dict:
        done = subprocess.run(
            [sys.executable, str(COMMAND), "--state-dir", str(state_dir),
             "--usage-log", str(state_dir / "usage-log.jsonl"),
             "--registry", str(REGISTRY)],
            input=json.dumps(request).encode("utf-8"), capture_output=True, check=True)
        return json.loads(done.stdout.decode("utf-8"))

    return judge


def run_scenario(root: Path, scenario: dict, judge: Judge) -> Run:
    """Run `scenario` in a fresh project under `root`, asking `judge`."""

    return _Run(root, scenario, judge).run()


class _Run:
    def __init__(self, root: Path, scenario: dict, judge: Judge) -> None:
        self.judge = judge
        self.home = root / "home"
        self.project = self.home / "work" / "project"
        self.project.mkdir(parents=True)
        self.outside = root / "outside"
        setup = scenario.get("setup", {})
        if "branch_changed_lines" in setup:
            # A git helper, not a harness's: it builds the checkout.
            from claude_code_adapter_support import git_branch_with_change
            git_branch_with_change(self.project, setup["branch_changed_lines"],
                                   origin_url=setup.get("origin_url"))
        self.installed = list(setup.get("installed_skills", []))
        self.agent = ({"role": "subagent", "id": SUBAGENT_ID}
                      if setup.get("agent") == "subagent" else {"role": "main"})
        self.steps = scenario["steps"]
        self.turns: list[dict] = []
        self.failures: list[str] = []
        self.exchanges: list[tuple[dict, dict]] = []
        self.calls = 0

    def run(self) -> Run:
        for number, step in enumerate(self.steps, 1):
            self.number = number
            if "prompt" in step:
                prompt = {**step["prompt"], "text": self._expand(step["prompt"]["text"])}
                if step.get("continues"):
                    self._entry(prompt)
                else:
                    self.turns.append({"key": f"t{len(self.turns) + 1}", "opener": prompt,
                                       "entries": []})
                self._judged(step.get("expect"), {"type": "prompt_submitted"})
            elif "reply" in step:
                self._entry({"type": "reply_text", "text": step["reply"]})
            elif "call" in step:
                self._call(step)
            elif "skill_invoked" in step:
                self._entry({"type": "skill_invoked", "skill": step["skill_invoked"]})
            elif "agent_finished" in step:
                self._entry({"type": "agent_finished", "agent_id": step["agent_finished"]})
            elif "compaction" in step:
                self.turns.append({"key": f"t{len(self.turns) + 1}",
                                   "opener": {"type": "compaction"}, "entries": []})
            elif "branch_grows" in step:
                from claude_code_adapter_support import grow_branch
                grow_branch(self.project, step["branch_grows"])
            elif "turn_end" in step:
                decision = self._judged(step.get("expect", {"decision": "allow"}),
                                        {"type": "turn_end"})
                if decision["decision"] == "allow":
                    self._entry({"type": "turn_ended"})
            elif "session_start" in step:
                self._judged(step.get("expect"),
                             {"type": "session_start", "source": step["session_start"]})
            else:
                raise ValueError(f"step {number}: the runner cannot run {sorted(step)}")
        return Run(self.failures, self.exchanges)

    def _call(self, step: dict) -> None:
        call = self._expanded_call(step["call"])
        decision = self._judged(step.get("expect", {"decision": "allow"}),
                                {"type": "pending_call", "call": call})
        if decision["decision"] == "hold":
            text = "\n\n".join(hold["text"] for hold in decision["holds"])
            result = {"ok": False, "held": True, "output": text}
        else:
            result = step.get("result", {"ok": True})
        if "expect_after" in step:
            self._judged(step["expect_after"],
                         {"type": "finished_call", "call": call, "result": result})
        self._entry({"type": "call", "call": call, "result": result})

    def _expanded_call(self, call: dict) -> dict:
        """`call` as an adapter sends it: placeholders filled, and an id, as
        a harness gives each call one."""

        self.calls += 1
        call = copy.deepcopy(call)
        call.setdefault("id", f"call{self.calls}")
        for key in ("path", "command"):
            if key in call:
                call[key] = self._expand(call[key])
        return call

    def _expand(self, text: str) -> str:
        """Fill the placeholder `{outside}`: a folder outside the project and
        any checkout, as a scratch file's folder is."""

        return text.replace("{outside}", self.outside.as_posix())

    def _entry(self, entry: dict) -> None:
        if not self.turns:
            raise ValueError(f"step {self.number}: an entry before any prompt")
        self.turns[-1]["entries"].append(entry)

    def _since_compaction(self) -> list[dict]:
        starts = [n for n, turn in enumerate(self.turns)
                  if turn["opener"].get("type") == "compaction"]
        return copy.deepcopy(self.turns[starts[-1] if starts else 0:])

    def _judged(self, expect: dict | None, event: dict) -> dict:
        request = {
            "event_model": 5,
            "session": {"id": "scenario-session", "agent": self.agent},
            "project": {"folders": [self.project.as_posix()],
                        "working_folder": self.project.as_posix(),
                        "home": self.home.as_posix(),
                        "agent_folders": [(self.home / AGENT_FOLDER).as_posix()],
                        "installed_skills": self.installed},
            "turns": self._since_compaction(),
            "event": event,
        }
        decision = self.judge(request)
        self.exchanges.append((request, decision))
        mismatch = expectation_mismatch(expect, observed(decision))
        if mismatch is not None:
            self.failures.append(
                f"step {self.number} ({event['type']}): expected {mismatch[0]}, "
                f"got {mismatch[1]}")
        return decision


def observed(decision: dict) -> dict:
    """A core decision as `expectation_mismatch` reads one."""

    closeout = next((h["text"] for h in decision["holds"] if h["gate"] == "closeout"), "")
    return {"decision": decision["decision"],
            "holds": [(h["gate"], h["kind"]) for h in decision["holds"]],
            "items": item_labels(closeout),
            "notices": [n["kind"] for n in decision["notices"]]}
