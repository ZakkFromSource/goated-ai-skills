"""Run the enforcement conformance scenarios through an adapter (Ticket 083).

    uv run python scripts/run_conformance.py TRANSLATOR [--only TEXT] [--file NAME]

The scenarios (`stack/fixtures/enforcement/*.yaml`) are written in the
event model's terms and name no harness. An adapter's author supplies a
translator: a Python file whose `make_translator(setup)` (or the function
named after a colon, as `path.py:factory`) returns an object that plays
each step into their harness, with their adapter in it, and reads the
adapter's answer back as an event-model decision. The runner reads the
scenarios, builds each one's project, plays its steps through a fresh
translator, compares each judged step's decision with the step's
expectation, and reports each scenario as passing or failing, naming the
step with the decision it expected and the one it got. The command exits 0
when every scenario it ran passes, and 1 when one fails or none ran. It
exits 2 for arguments it cannot use: a translator it cannot load for any
reason, or a `--file` naming no scenario file (`routing` and `routing.yaml`
name the same one).

A translator has these methods, each called once per step of its kind:

- `prompt(prompt, continues)` -> decision: a prompt, the event model's
  `prompt` object, is submitted. `continues` is true when it arrives inside
  a turn that has not ended, rather than opening a turn.
- `reply(text)`: the agent writes reply text.
- `call(call, result)` -> (decision, decision or None): the agent makes a
  call, the event model's `call` object (no `id`; the harness gives one).
  The first decision is the one before it runs. When that allows it, it
  runs and returns `result`, the event model's `result` (`{"ok": true}`
  when the scenario gives none); the second
  decision is the one the adapter got after it ran, or None when the
  adapter judged nothing then.
- `skill_invoked(skill)`: a person invokes a skill.
- `agent_finished(agent_id)`: a background agent finishes.
- `compaction()`: the harness compacts the conversation.
- `turn_end()` -> decision: the agent ends its turn.
- `session_start(source)` -> decision: a session starts, from `new`,
  `resumed`, `after_compaction` or `cleared`.

A `branch_grows` step calls no method: the runner adds that many changed
lines of code to the project's checkout itself, as a new untracked file.

A decision is the event model's `decision`: `decision`, `holds` with each
hold's `gate` and `kind`, and `notices` with each notice's `kind`. Hold
text is read only for a closeout hold's item lines. `setup`, given to
`make_translator`, is a dict: `home`; `project`, `<home>/work/project`,
already made; `outside`, a folder outside the project and any checkout;
`state_dir`, an empty folder the adapter may keep state in; `usage_log`,
the usage log the adapter should write, always None, so a scenario run
writes no log, whatever the environment names; `installed_skills`, a
list, or None when the scenario does not say; and
`agent`, the event model's `session.agent`. Every path is a `Path`.
"""

from __future__ import annotations

import argparse
import copy
import importlib.util
import re
import subprocess
import sys
import tempfile
from collections.abc import Callable
from pathlib import Path
from typing import Any, NamedTuple

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
SCENARIOS = REPO_ROOT / "stack" / "fixtures" / "enforcement"
DEFAULT_FACTORY = "make_translator"
# The subagent a scenario with `setup.agent: subagent` runs in.
SUBAGENT_ID = "scenario1"
# A closeout item's line, as the contract's Hold Messages section defines it.
ITEM_LABEL = re.compile(r"^- ([A-Z][a-z]+): ", re.M)
# Notices that mean the adapter could not judge: never expected unless named.
FAILURE_NOTICES = frozenset({"fail_open", "warning"})
# `path.py:factory`, the factory named after the file.
_FACTORY_SPEC = re.compile(r"^(?P<path>.+\.py):(?P<name>[A-Za-z_]\w*)$")

MakeTranslator = Callable[[dict], Any]


class ScenarioResult(NamedTuple):
    """One scenario's run: its name, `<file>: <scenario name>`, and a line
    for each step whose decision differed from its expectation."""

    name: str
    failures: list[str]

    @property
    def passed(self) -> bool:
        return not self.failures


def load_scenarios(folder: Path = SCENARIOS) -> list[tuple[str, dict]]:
    """Every scenario under `folder`, as (`<file>: <name>`, scenario), in
    file and then document order."""

    found = []
    for path in sorted(folder.glob("*.yaml")):
        document = yaml.safe_load(path.read_text(encoding="utf-8"))
        found.extend((f"{path.stem}: {scenario['name']}", scenario)
                     for scenario in document["scenarios"])
    return found


def load_translator(spec: str) -> MakeTranslator:
    """The translator factory `spec` names: `path.py`, whose
    `make_translator` it is, or `path.py:name`. The file's own folder goes
    first on `sys.path`, so it can import the files beside it. Raises
    FileNotFoundError when there is no such file, AttributeError when it has
    no such factory."""

    match = _FACTORY_SPEC.match(spec)
    path, name = (match["path"], match["name"]) if match else (spec, DEFAULT_FACTORY)
    file = Path(path).resolve()
    if not file.is_file():
        raise FileNotFoundError(f"no translator file at {file}")
    module_spec = importlib.util.spec_from_file_location(f"_goated_translator_{file.stem}", file)
    module = importlib.util.module_from_spec(module_spec)
    if str(file.parent) not in sys.path:
        sys.path.insert(0, str(file.parent))
    module_spec.loader.exec_module(module)
    factory = getattr(module, name, None)
    if not callable(factory):
        raise AttributeError(f"{file} has no translator factory {name!r}")
    return factory


def run_scenarios(make_translator: MakeTranslator,
                  scenarios: list[tuple[str, dict]] | None = None,
                  only: str | None = None) -> list[ScenarioResult]:
    """Run each scenario (by default every one) whose name contains `only`,
    each through a fresh translator in a fresh folder, in order."""

    chosen = load_scenarios() if scenarios is None else scenarios
    return [run_scenario(name, scenario, make_translator) for name, scenario in chosen
            if only is None or only in name]


def run_scenario(name: str, scenario: dict, make_translator: MakeTranslator) -> ScenarioResult:
    """Run one scenario through a fresh translator in a fresh folder. A
    translator that raises fails the scenario at that step; the run stops
    there."""

    with tempfile.TemporaryDirectory() as folder:
        try:
            failures = _Run(Path(folder), scenario, make_translator).run()
        except _TranslatorFailed as exc:
            failures = [*exc.args[1], exc.args[0]]
    return ScenarioResult(name, failures)


def observed(decision: dict) -> dict:
    """A decision as `expectation_mismatch` reads one."""

    holds = decision.get("holds", [])
    closeout = next((h.get("text", "") for h in holds if h["gate"] == "closeout"), "")
    return {"decision": decision["decision"],
            "holds": [(h["gate"], h["kind"]) for h in holds],
            "items": item_labels(closeout),
            "notices": [n["kind"] for n in decision.get("notices", [])]}


def item_labels(closeout_text: str) -> list[str]:
    """The labels of the items a closeout hold's text lists, sorted."""

    return sorted(set(ITEM_LABEL.findall(closeout_text)))


def expectation_mismatch(expect: dict | None, got: dict) -> tuple[dict, dict] | None:
    """What a step `expect`ed and what it `got`, when they differ, else None.

    `got` is a decision as `observed` gives it: `decision`, `holds` as
    (gate, kind) pairs in firing order, `items`, the closeout hold's item
    labels, and `notices`, their kinds. With no `expect`, the step is not
    checked, but a decision that could not judge never passes. Holds match
    by gate and kind; items only when the expectation names them; notices
    exactly when it names them, and otherwise only the failure kinds count.
    """

    if expect is None:
        expect = {"decision": got["decision"], "holds": [
            {"gate": gate, "kind": kind} for gate, kind in got["holds"]]}
    holds = expect.get("holds", [])
    wanted = {"decision": expect["decision"],
              "holds": [(h["gate"], h["kind"]) for h in holds]}
    found = {"decision": got["decision"], "holds": got["holds"]}
    labels = next((h["items"] for h in holds if "items" in h), None)
    if labels is not None:
        wanted["items"], found["items"] = sorted(labels), got["items"]
    if "notices" in expect:
        wanted["notices"] = sorted(expect["notices"])
        found["notices"] = sorted(got["notices"])
    else:
        wanted["failures"] = []
        found["failures"] = sorted(FAILURE_NOTICES.intersection(got["notices"]))
    return None if wanted == found else (wanted, found)


class _TranslatorFailed(Exception):
    """The translator raised: (the line saying so, the failures before it)."""


class _Run:
    """One scenario played through one translator."""

    def __init__(self, root: Path, scenario: dict, make_translator: MakeTranslator) -> None:
        home = root / "home"
        project = home / "work" / "project"
        project.mkdir(parents=True)
        self.outside = root / "outside"
        self.outside.mkdir()
        (root / "state").mkdir()
        setup = scenario.get("setup", {})
        if "branch_changed_lines" in setup:
            _git_branch_with_change(project, setup["branch_changed_lines"], setup.get("origin_url"))
        self.project = project
        self.steps = scenario["steps"]
        self.failures: list[str] = []
        self.number = 0
        self.translator = self._translated("setup", lambda: make_translator({
            "home": home, "project": project, "outside": self.outside,
            "state_dir": root / "state",
            # Scenario sessions are tests: they never belong in a person's log.
            "usage_log": None,
            "installed_skills": (list(setup["installed_skills"])
                                 if "installed_skills" in setup else None),
            "agent": ({"role": "subagent", "id": SUBAGENT_ID}
                      if setup.get("agent") == "subagent" else {"role": "main"}),
        }))

    def run(self) -> list[str]:
        t = self.translator
        for self.number, step in enumerate(self.steps, 1):
            if "prompt" in step:
                prompt = {**step["prompt"], "text": self._expand(step["prompt"]["text"])}
                continues = bool(step.get("continues"))
                self._check(step.get("expect"), "prompt",
                            self._translated("prompt", lambda: t.prompt(prompt, continues)))
            elif "reply" in step:
                self._translated("reply", lambda: t.reply(step["reply"]))
            elif "call" in step:
                self._call(step)
            elif "skill_invoked" in step:
                self._translated("skill_invoked", lambda: t.skill_invoked(step["skill_invoked"]))
            elif "agent_finished" in step:
                self._translated("agent_finished",
                                 lambda: t.agent_finished(step["agent_finished"]))
            elif "compaction" in step:
                self._translated("compaction", t.compaction)
            elif "branch_grows" in step:
                # The project changes on disk; the translator sees no event.
                _grow_branch(self.project, step["branch_grows"])
            elif "turn_end" in step:
                self._check(step.get("expect", {"decision": "allow"}), "turn end",
                            self._translated("turn_end", t.turn_end))
            elif "session_start" in step:
                source = step["session_start"]
                self._check(step.get("expect"), f"session start {source}",
                            self._translated("session_start", lambda: t.session_start(source)))
            else:
                raise ValueError(f"step {self.number}: the runner cannot run {sorted(step)}")
        return self.failures

    def _call(self, step: dict) -> None:
        call = copy.deepcopy(step["call"])
        for key in ("path", "command"):
            if key in call:
                call[key] = self._expand(call[key])
        result = copy.deepcopy(step.get("result", {"ok": True}))
        label = f"call {call['kind']}"
        answer = self._translated(label, lambda: self.translator.call(call, result))
        before, after = answer if isinstance(answer, tuple) and len(answer) == 2 else (answer, None)
        self._check(step.get("expect", {"decision": "allow"}), label, before)
        if "expect_after" in step:
            self._check(step["expect_after"], f"{label}, after it ran", after)

    def _expand(self, text: str) -> str:
        """Fill the placeholder `{outside}`."""

        return text.replace("{outside}", self.outside.as_posix())

    def _translated(self, what: str, act: Callable[[], Any]) -> Any:
        try:
            return act()
        except Exception as exc:  # noqa: BLE001 - a translator's failure fails its scenario
            raise _TranslatorFailed(f"step {self.number} ({what}): the translator raised "
                                    f"{type(exc).__name__}: {exc}", self.failures) from exc

    def _check(self, expect: dict | None, label: str, decision: Any) -> None:
        try:
            got = observed(decision)
        except (KeyError, TypeError, AttributeError):
            self.failures.append(f"step {self.number} ({label}): expected "
                                 f"{expect or 'a decision'}, got {decision!r}, not a decision")
            return
        mismatch = expectation_mismatch(expect, got)
        if mismatch is not None:
            self.failures.append(f"step {self.number} ({label}): expected {mismatch[0]}, "
                                 f"got {mismatch[1]}")


def _git_branch_with_change(project: Path, changed_lines: int,
                            origin_url: str | None = None) -> None:
    """Make `project` a git checkout on a branch `feature` whose diff against
    `main` changes `changed_lines` lines of a code file, with a remote
    `origin` at `origin_url`, never fetched, when one is given."""

    def git(*args: str) -> None:
        subprocess.run(["git", "-c", "user.name=Test", "-c", "user.email=test@example.invalid",
                        "-c", "commit.gpgsign=false", "-c", "core.autocrlf=false", *args],
                       cwd=project, check=True, capture_output=True)

    git("init", "-q", "-b", "main")
    (project / "base.txt").write_text("base\n", encoding="utf-8")
    git("add", "base.txt")
    git("commit", "-q", "-m", "Base")
    if origin_url:
        git("remote", "add", "origin", origin_url)
    git("checkout", "-q", "-b", "feature")
    change = project / "src" / "change.py"
    change.parent.mkdir(parents=True)
    change.write_text("".join(f"line {n}\n" for n in range(changed_lines)), encoding="utf-8")
    git("add", "src/change.py")
    git("commit", "-q", "-m", "Change")


def _grow_branch(project: Path, changed_lines: int) -> None:
    """Add `changed_lines` changed lines of non-test code to the checkout at
    `project`, as a new untracked code file: a `branch_grows` step."""

    folder = project / "src"
    folder.mkdir(parents=True, exist_ok=True)
    grown = len(list(folder.glob("grown_*.py")))
    (folder / f"grown_{grown}.py").write_text(
        "".join(f"grown_{grown}_{n} = {n}\n" for n in range(changed_lines)), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run the enforcement conformance scenarios through an adapter's translator.")
    parser.add_argument("translator", help="a translator file: `path.py` or `path.py:factory`")
    parser.add_argument("--only", help="run only the scenarios whose name contains this text")
    parser.add_argument("--file", action="append", default=[],
                        help="run only this scenario file, such as `routing`; repeatable")
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return 2 if exc.code else 0
    scenarios = load_scenarios()
    files = sorted({name.split(":", 1)[0] for name, _ in scenarios})
    # `routing` or `routing.yaml`, as a person may name the file either way.
    wanted = {name.removesuffix(".yaml") for name in args.file}
    unknown = sorted(wanted.difference(files))
    if unknown:
        print(f"run_conformance: no scenario file {unknown[0]!r}; the files are "
              f"{', '.join(files)}", file=sys.stderr)
        return 2
    try:
        make_translator = load_translator(args.translator)
    except FileNotFoundError as exc:
        print(f"run_conformance: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:  # noqa: BLE001 - any failure to load the author's file is exit 2
        print(f"run_conformance: could not load the translator {args.translator} "
              f"({type(exc).__name__}: {exc})", file=sys.stderr)
        return 2
    scenarios = [(name, scenario) for name, scenario in scenarios
                 if not wanted or name.split(":", 1)[0] in wanted]
    results = run_scenarios(make_translator, scenarios, args.only)
    for result in results:
        print(f"{'PASS' if result.passed else 'FAIL'} {result.name}")
        for failure in result.failures:
            print(f"    {failure}")
    passed = sum(result.passed for result in results)
    print(f"{passed} of {len(results)} scenarios passed")
    return 0 if results and passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
