"""Per-session core state, one small JSON file per session id the caller supplies.

State holds only what the current turn cannot answer on its own:
the current task's route, whether missing or reset state lost the task, what
counts until the next compaction (whether the router loaded, which GOATED
skills loaded, which design references, skill references, and spawn-brief
templates were read, and digests of the first distinct files read), the
task's lasting skips (`actions.LastingSkip`) and what their notices named,
the task's review points (`actions.ReviewPoints`) and the list its last
closeout note named, the reads the current turn's
landed writes owe (`actions.OwedRead`), which
template each of the current turn's spawns' briefs followed, the last turn
seen, the latest user overrides, and the friction count (`friction.py`). Beside it,
markers name what the current turn's holds already gave in full, a
record per project names what its onboarding notice last named, and a lock
file is held while a hook changes the session's state. Apart from
the short override phrases a user typed, it holds no prompt or reply text.
"""

from __future__ import annotations

import contextlib
import hashlib
import json
import os
import re
import time
from collections.abc import Callable, Iterator
from pathlib import Path

UNSAFE_NAME_CHARS = re.compile(r"[^a-z0-9_-]")
# A name `_safe_name` keeps as it is.
SAFE_NAME_RE = re.compile(r"[a-z0-9_-]{1,128}")
# Joins a changed name's readable prefix to its digest (`_safe_name`).
HASH_SEPARATOR = "="
REPLACE_ATTEMPTS = 5
REPLACE_RETRY_SECONDS = 0.02
# Beside the state files: one empty file per session, and one per subagent of
# it, named for the turn that claimed it.
TURN_MARKERS_DIR = "turn-markers"
# Separates a subagent's id from its session's in a marker name; no safe name
# holds it, so a session's marker prefix never matches a subagent's.
AGENT_SEPARATOR = "~"
# Beside the state files: per project, which onboarding skills its notice
# last named.
ONBOARDING_DIR = "onboarding-notices"
# Beside the state files: one lock file per session while a hook loads,
# changes, and saves its state (`StateStore.locked`).
LOCKS_DIR = "locks"
# How long a hook waits for another hook's lock before it goes on without
# it, and how old a lock is before it counts as left by a hook that died
# even when its holder cannot be told; no more than the wait, so a dead
# holder's lock is broken before any hook gives up on it. A judgement takes
# well under a second; a hook must never hang.
LOCK_WAIT_SECONDS = 5.0
LOCK_STALE_SECONDS = 5.0
# A lock file holds its holder's process id, written just after the file is
# made; one still empty this long after was left by a hook that died first.
LOCK_EMPTY_GRACE_SECONDS = 0.5
LOCK_RETRY_SECONDS = 0.01


class Task:
    """The current task: its route, the turn whose route line started it, and
    whether it was routed: by a route line other than bare `continue`, by the
    brief that started the session, or in a turn that met router-first by the
    router's load or a person's override (`gates.note_task_routed`). Only a
    routed task carries a person's follow-up as `continue` (Ticket 119)."""

    __slots__ = ("route", "started_turn", "routed")

    def __init__(self, route: dict, started_turn: str, routed: bool | None = None) -> None:
        self.route = route
        self.started_turn = started_turn
        self.routed = route.get("form") != "continue" if routed is None else routed

    def to_json(self) -> dict:
        return {"route": self.route, "started_turn": self.started_turn, "routed": self.routed}


class SessionState:
    """Everything the adapter remembers about one session between hook calls."""

    __slots__ = (
        "router_loaded", "last_turn", "task", "task_unknown", "overrides", "policy_notice_shown",
        "reference_reads", "brief_routed", "brief_task", "briefed", "loads", "template_reads",
        "skill_reference_reads", "spawn_templates", "open_holds", "held_gates", "friction",
        "retrospective_notice_shown", "files_read", "files_seen", "shell", "lasting_skips", "owed_reads",
        "review_points", "carried_notices", "closeout_noted",
    )

    def __init__(self) -> None:
        self.router_loaded = False
        # True while the route came from the brief that opened the session and
        # no prompt a person typed has opened a turn since: router-first is met.
        self.brief_routed = False
        # True while the current task is the one the brief's turn started and
        # no compaction has come since: in it, a person's prompt then a
        # `goated-route: continue` line meets router-first (spec R8). Unlike
        # `brief_routed`, a typed prompt does not end it, and it switches on no
        # briefed-session orientation.
        self.brief_task = False
        # True once the session's first prompt is known to be a brief from the
        # session that started it, which reviews the work (spec R10). A fact
        # about the session: no typed prompt or compaction ends it.
        self.briefed = False
        self.last_turn: str | None = None
        self.task: Task | None = None
        # True when saved state was missing or unreadable: the session may have
        # had a task, so `continue` cannot start one until a full route line
        # does, or the session is shown to have none.
        self.task_unknown = False
        # The overrides a person typed in the latest prompt (`overrides.parse_overrides`),
        # with `prompt`, the caller's key for that prompt (None when it gave none),
        # so they apply only to the turn that prompt opened (`judge.overrides_for`).
        self.overrides: dict = {}
        self.policy_notice_shown = False
        # The GOATED skills (`tdd`) loaded since the last compaction.
        self.loads: list[str] = []
        # The design references (`errors.md`) read since the last compaction.
        self.reference_reads: list[str] = []
        # The skill references the registry can declare
        # (`tdd/references/test-design.md`) read since the last compaction.
        self.skill_reference_reads: list[str] = []
        # The spawn-brief templates (`contracts.BriefTemplate.reference`) read
        # since the last compaction.
        self.template_reads: list[str] = []
        # Digests of the first distinct files read whole since the last
        # compaction, up to `gates.ORIENTATION_READS`: enough of them orient a
        # session routed by its brief. A digest keeps file names out of state.
        self.files_read: list[str] = []
        # Digests of the first distinct project files read or printed, whole
        # or in part, since the last compaction, up to `gates.ORIENTATION_FILES`:
        # enough of them orient such a session too (round 6's R3).
        self.files_seen: list[str] = []
        # The current task's lasting skips since the last compaction (spec R4):
        # {"gate", "skill", "kind", "reference", "turn"}, the turn being the one
        # whose skip line cleared the hold (`record_lasting_skips`).
        self.lasting_skips: list[dict] = []
        # The current task's review points (round 7, R1), by closeout item
        # label (`Review`, `Verification`): {"lines": <branch size>, "turn":
        # <turn key>}, the turn being the one that met or declined the item.
        # Unlike the lasting skips, they survive a compaction; a new task ends them.
        self.review_points: dict = {}
        # What a lasting skip's notice already named in the current task
        # (round 7, R3): {"gate", "skill", "kind", "turn"}. It ends with the
        # lasting skips it is about.
        self.carried_notices: list[dict] = []
        # The labels of the items the task's last closeout note named, and the
        # turn that gave it (round 7, R4): {"labels": [...], "turn": <turn key>},
        # or {} for none. A new task ends it.
        self.closeout_noted: dict = {}
        # The reads each write of one turn owes, which a read gate let land
        # (round 5, R5): {"turn": <turn key>, "edits": {<call_id>: [<owed read>]}},
        # each owed read {"gate", "skill", "kind", "reference", "path"}.
        self.owed_reads: dict = {}
        # The brief templates (`contracts.BriefTemplate.reference`) each spawn of
        # one turn followed when the spawn gate let it through:
        # {"turn": <turn key>, "edits": {<call_id>: [<template>]}}.
        self.spawn_templates: dict = {}
        # The friction count (`friction.py`): holds still open, as
        # `friction.observe` keeps them; the gates that held in one turn,
        # {"turn": <turn key>, "gates": [<gate>]}; how many holds were declined
        # or left unanswered; and whether the retrospective notice was shown.
        self.open_holds: list[dict] = []
        self.held_gates: dict = {}
        self.friction = 0
        self.retrospective_notice_shown = False
        # The shell (`events.POSIX` or `events.POWERSHELL`) of the session's last
        # shell command, or None before its first: the carrier a hold names (Ticket 095).
        self.shell: str | None = None

    def forget_context(self, boundary_turn: str | None = None) -> None:
        """Drop what counted only while its text was in the agent's context: the
        router and other loads, the brief's route and its hold on the task,
        the design references, skill references, spawn-brief templates, and
        files read, and the lasting skips. Called at a compaction or `/clear`.
        `boundary_turn` is the compaction's own turn when it is folded again:
        its lasting skips came after the compaction, so they stay."""

        self.router_loaded = False
        self.brief_routed = False
        self.brief_task = False
        self.loads = []
        self.reference_reads = []
        self.skill_reference_reads = []
        self.template_reads = []
        self.files_read = []
        self.files_seen = []
        self.end_lasting_skips(boundary_turn)

    def end_task(self, boundary_turn: str | None = None) -> None:
        """End what lasts only for the current task, as a new task's route
        line or a `/clear` ends it: its lasting skips and their notices, its
        review points, and its closeout note's list, keeping only those
        `boundary_turn`, the turn that started the new task, recorded, since
        that turn may be folded again after them."""

        self.end_lasting_skips(boundary_turn)
        self.review_points = {label: point for label, point in self.review_points.items()
                              if point["turn"] == boundary_turn}
        if self.closeout_noted.get("turn") != boundary_turn:
            self.closeout_noted = {}

    def record_carried_notices(self, turn: str, keys) -> None:
        """Keep the (gate, skill, kind) keys a call of `turn` gave the lasting-skip notice for."""

        known = set(self.carried_notice_keys())
        for gate, skill, kind in keys:
            if (gate, skill, kind) not in known:
                known.add((gate, skill, kind))
                self.carried_notices.append(
                    {"gate": gate, "skill": skill, "kind": kind, "turn": turn})

    def carried_notice_keys(self) -> list[tuple[str, str, str]]:
        """The (gate, skill, kind) keys the task's lasting-skip notices already named."""

        return [(n["gate"], n["skill"], n["kind"]) for n in self.carried_notices]

    def record_review_points(self, turn: str, met: dict[str, int]) -> None:
        """Keep the review points (`actions.ReviewPoints.met`) that `turn` set."""

        for label, lines in met.items():
            self.review_points[label] = {"lines": lines, "turn": turn}

    def review_point_lines(self) -> dict[str, int]:
        """The task's review points, as branch sizes by item label."""

        return {label: point["lines"] for label, point in self.review_points.items()}

    def end_lasting_skips(self, boundary_turn: str | None = None) -> None:
        """End the lasting skips at a new task or a compaction, keeping only
        those `boundary_turn` recorded: it is the turn that crossed the
        boundary, which may be folded again after its own skip lines."""

        self.lasting_skips = [s for s in self.lasting_skips if s["turn"] == boundary_turn]
        self.carried_notices = [n for n in self.carried_notices if n["turn"] == boundary_turn]

    def record_lasting_skips(self, turn: str, skips) -> None:
        """Keep the lasting skips (`actions.LastingSkip`) that a skip line of `turn` made."""

        known = set(self.lasting_skip_keys())
        for skip in skips:
            if tuple(skip) not in known:
                known.add(tuple(skip))
                self.lasting_skips.append({**skip._asdict(), "turn": turn})

    def lasting_skip_keys(self) -> list[tuple[str, str, str, str]]:
        """The task's lasting skips, each as (gate, skill, kind, reference)."""

        return [(s["gate"], s["skill"], s["kind"], s["reference"]) for s in self.lasting_skips]

    def record_spawn_templates(self, turn: str, call_id: str, templates: list[str]) -> None:
        """Keep which brief templates a spawn the spawn gate let through
        followed, for the turn's closeout; an earlier turn's spawns are dropped."""

        self.spawn_templates = _with_call(self.spawn_templates, turn, call_id, templates)

    def spawn_templates_of(self, turn: str) -> dict[str, list[str]]:
        """What `record_spawn_templates` kept for `turn`'s spawns, by call_id."""

        return _calls_of(self.spawn_templates, turn)

    def record_owed_reads(self, turn: str, call_id: str, owed) -> None:
        """Keep the reads (`actions.OwedRead`) a write of `turn` owes, which a
        read gate let land, for the turn's Reads item; an earlier turn's are
        dropped, as the closeout judges only its own turn."""

        self.owed_reads = _with_call(self.owed_reads, turn, call_id,
                                     [read._asdict() for read in owed])

    def owed_reads_of(self, turn: str) -> dict[str, list[dict]]:
        """What `record_owed_reads` kept for `turn`'s writes, by call_id."""

        return _calls_of(self.owed_reads, turn)

    def to_json(self) -> dict:
        return {
            "router_loaded": self.router_loaded,
            "brief_routed": self.brief_routed,
            "brief_task": self.brief_task,
            "briefed": self.briefed,
            "last_turn": self.last_turn,
            "task": self.task.to_json() if self.task else None,
            "task_unknown": self.task_unknown,
            "overrides": self.overrides,
            "policy_notice_shown": self.policy_notice_shown,
            "loads": self.loads,
            "reference_reads": self.reference_reads,
            "skill_reference_reads": self.skill_reference_reads,
            "template_reads": self.template_reads,
            "files_read": self.files_read,
            "files_seen": self.files_seen,
            "spawn_templates": self.spawn_templates,
            "open_holds": self.open_holds,
            "held_gates": self.held_gates,
            "friction": self.friction,
            "retrospective_notice_shown": self.retrospective_notice_shown,
            "shell": self.shell,
            "lasting_skips": self.lasting_skips,
            "owed_reads": self.owed_reads,
            "review_points": self.review_points,
            "carried_notices": self.carried_notices,
            "closeout_noted": self.closeout_noted,
        }

    @classmethod
    def from_json(cls, data: object) -> "SessionState":
        """Rebuild state from `to_json` output; raise ValueError on any other shape."""

        if not isinstance(data, dict):
            raise ValueError("state is not an object")
        state = cls()
        state.router_loaded = _expect(data.get("router_loaded", False), bool)
        state.brief_routed = _expect(data.get("brief_routed", False), bool)
        state.brief_task = _expect(data.get("brief_task", False), bool)
        state.briefed = _expect(data.get("briefed", False), bool)
        state.policy_notice_shown = _expect(data.get("policy_notice_shown", False), bool)
        state.last_turn = _expect(data.get("last_turn"), (str, type(None)))
        state.task_unknown = _expect(data.get("task_unknown", False), bool)
        state.loads = _string_list(data.get("loads", []))
        state.reference_reads = _string_list(data.get("reference_reads", []))
        state.skill_reference_reads = _string_list(data.get("skill_reference_reads", []))
        state.template_reads = _string_list(data.get("template_reads", []))
        state.files_read = _string_list(data.get("files_read", []))
        state.files_seen = _string_list(data.get("files_seen", []))
        state.spawn_templates = _valid_calls(data.get("spawn_templates", {}))
        state.open_holds = [_valid_open_hold(h) for h in _expect(data.get("open_holds", []), list)]
        state.held_gates = _valid_held_gates(data.get("held_gates", {}))
        state.friction = _expect(data.get("friction", 0), int)
        state.retrospective_notice_shown = _expect(
            data.get("retrospective_notice_shown", False), bool)
        state.shell = _expect(data.get("shell"), (str, type(None)))
        state.lasting_skips = [_valid_lasting_skip(s)
                               for s in _expect(data.get("lasting_skips", []), list)]
        state.owed_reads = _valid_owed_reads(data.get("owed_reads", {}))
        state.review_points = _valid_review_points(data.get("review_points", {}))
        state.carried_notices = [
            {key: _expect(_expect(notice, dict).get(key), str)
             for key in ("gate", "skill", "kind", "turn")}
            for notice in _expect(data.get("carried_notices", []), list)]
        noted = _expect(data.get("closeout_noted", {}), dict)
        state.closeout_noted = ({"labels": _string_list(noted.get("labels")),
                                 "turn": _expect(noted.get("turn"), str)} if noted else {})
        task = _expect(data.get("task"), (dict, type(None)))
        if task is not None:
            state.task = Task(
                route=_valid_route(task.get("route")),
                started_turn=_expect(task.get("started_turn"), str),
                routed=_expect(task.get("routed"), (bool, type(None))),
            )
        overrides = _expect(data.get("overrides", {}), dict)
        if overrides:
            state.overrides = {
                "prompt": _expect(overrides.get("prompt"), (str, type(None))),
                "routing": _expect(overrides.get("routing", False), bool),
                "skills": _string_list(overrides.get("skills", [])),
                "commit_message": _expect(overrides.get("commit_message"), (str, type(None))),
                "phrases": _string_list(overrides.get("phrases", [])),
            }
        return state


def _with_call(record: dict, turn: str, call_id: str, values: list[str]) -> dict:
    """`record`, a per-turn record of calls ({"turn": <turn key>, "edits":
    {<call_id>: [<value>]}}), with this call's values kept; a record of an
    earlier turn is replaced."""

    if record.get("turn") != turn:
        record = {"turn": turn, "edits": {}}
    record["edits"][call_id] = list(values)
    return record


def _calls_of(record: dict, turn: str) -> dict[str, list[str]]:
    """The values `_with_call` kept for `turn`'s calls, by call_id."""

    return dict(record["edits"]) if record.get("turn") == turn else {}


def _valid_calls(data) -> dict:
    """A per-turn record of calls as `to_json` saved it; ValueError on any other shape."""

    record = _expect(data, dict)
    if not record:
        return {}
    edits = _expect(record.get("edits"), dict)
    return {
        "turn": _expect(record.get("turn"), str),
        "edits": {_expect(k, str): _string_list(v) for k, v in edits.items()},
    }


def _valid_open_hold(data) -> dict:
    """An open hold as `friction.observe` saved it; ValueError on any other shape."""

    hold = _expect(data, dict)
    seen = _expect(hold.get("seen"), dict)
    return {
        "gate": _expect(hold.get("gate"), str),
        "turn": _expect(hold.get("turn"), str),
        "action": _expect(hold.get("action", ""), str),
        "strict": _expect(hold.get("strict"), bool),
        "skills": _string_list(hold.get("skills")),
        "references": _string_list(hold.get("references")),
        "skippable": _string_list(hold.get("skippable")),
        "seen": {_expect(k, str): _expect(v, int) for k, v in seen.items()},
    }


def _valid_lasting_skip(data) -> dict:
    """A lasting skip as `record_lasting_skips` saved it; ValueError on any other shape."""

    entry = _expect(data, dict)
    return {key: _expect(entry.get(key), str)
            for key in ("gate", "skill", "kind", "reference", "turn")}


def _valid_owed_reads(data) -> dict:
    """The owed reads as `record_owed_reads` saved them; ValueError on any other shape."""

    record = _expect(data, dict)
    if not record:
        return {}
    calls = _expect(record.get("edits"), dict)
    return {
        "turn": _expect(record.get("turn"), str),
        "edits": {_expect(call_id, str): [
            {key: _expect(_expect(read, dict).get(key), str)
             for key in ("gate", "skill", "kind", "reference", "path")}
            for read in _expect(reads, list)] for call_id, reads in calls.items()},
    }


def _valid_review_points(data) -> dict:
    """The review points as `record_review_points` saved them; ValueError on any other shape."""

    points = {}
    for label, point in _expect(data, dict).items():
        point = _expect(point, dict)
        lines = point.get("lines")
        if isinstance(lines, bool) or not isinstance(lines, int):
            raise ValueError("a review point's lines are not a count")
        points[_expect(label, str)] = {"lines": lines, "turn": _expect(point.get("turn"), str)}
    return points


def _valid_held_gates(data) -> dict:
    record = _expect(data, dict)
    if not record:
        return {}
    return {"turn": _expect(record.get("turn"), str), "gates": _string_list(record.get("gates"))}


def _expect(value, kinds):
    if not isinstance(value, kinds):
        raise ValueError(f"unexpected state value {type(value).__name__}")
    return value


def _string_list(value) -> list:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ValueError("expected a list of strings")
    return list(value)


def _valid_route(route) -> dict:
    """A task's route is `direct`, a `requires:` route, or `continue` when that
    started the session's first task, with no required skills."""

    route = _expect(route, dict)
    if route.get("form") in ("direct", "continue"):
        return {"form": route["form"]}
    if route.get("form") == "route":
        requires = _string_list(route.get("requires"))
        if requires:
            return {
                "form": "route",
                "intensity": _expect(route.get("intensity"), str),
                "requires": requires,
            }
    raise ValueError("unexpected task route")


def default_root() -> Path:
    """A per-user folder no other local user can pre-create, under which a
    caller keeps its state folder.

    POSIX uses `$XDG_STATE_HOME` or `~/.local/state`, not the shared `/tmp`.
    Windows uses the per-user temp folder, found as `tempfile` would, without
    the import cost.
    """

    if os.name != "nt":
        xdg = os.environ.get("XDG_STATE_HOME")
        return Path(xdg) if xdg else Path.home() / ".local" / "state"
    for name in ("TEMP", "TMP"):
        value = os.environ.get(name)
        if value:
            return Path(value)
    return Path.home() / "AppData" / "Local" / "Temp"


class StateUnsafe(Exception):
    """The state folder could be written by another user, so it cannot be trusted."""


def ensure_private_directory(directory: Path, what: str = "state folder") -> None:
    """Make `directory` if it is missing, readable by this user alone; raise
    `StateUnsafe` on POSIX when it is a link, another user's, or writable by
    others. `what` names it in the message."""

    directory.mkdir(mode=0o700, parents=True, exist_ok=True)
    if os.name == "nt":
        return  # The Windows defaults, per-user folders, are private.
    info = directory.lstat()
    if directory.is_symlink() or info.st_uid != os.getuid() or info.st_mode & 0o022:
        raise StateUnsafe(f"its {what} {directory} is not private to this user")


class StateStore:
    """Loads and saves `SessionState` under one directory, keyed by session.

    The store only uses a directory it owns and that nobody else can write;
    otherwise it raises `StateUnsafe`, because planted state could make holds
    pass.

    `upgrade`, when given, turns a saved session file's data, as read, into
    this version's shape before it is checked: an adapter whose earlier
    versions saved state in its own words passes one, so that state keeps
    working. It must return the data, changed or not.
    """

    def __init__(self, directory: Path,
                 upgrade: Callable[[object], object] | None = None) -> None:
        self.directory = Path(directory)
        self.upgrade = upgrade

    def load(self, session_id: str) -> tuple[SessionState, str | None]:
        """Return the session's state and a warning when stored state was unusable.

        A missing file starts fresh quietly; an unreadable or corrupt one
        starts fresh and says so. Either way the fresh state marks the task
        unknown, because the session may already have had one, so `continue`
        cannot start a task until a session start or a read of the whole
        transcript shows there is none. A fresh start can only re-hold, never
        pass.
        """

        self._ensure_private_directory()
        path = self._path(session_id)
        fresh = SessionState()
        fresh.task_unknown = True
        if not path.exists():
            return fresh, None
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return SessionState.from_json(self.upgrade(data) if self.upgrade else data), None
        except (OSError, ValueError):
            return fresh, "its saved session state was unreadable and was reset"

    def save(self, session_id: str, state: SessionState) -> None:
        """Write state atomically so a concurrent hook never reads half a file."""

        self._ensure_private_directory()
        _write_json(self._path(session_id), state.to_json())

    @contextlib.contextmanager
    def locked(self, session_id: str) -> Iterator[bool]:
        """Hold the session's lock while the caller loads, changes, and saves
        its state, so of hooks judging at once each sees what the one before
        it saved: two edits of one message are judged at the same moment,
        and without it the last save drops what the other recorded (review
        of Ticket 118). Yields whether the lock is held.

        The lock is one exclusive file create, holding the holder's process
        id. A lock left by a hook that died is broken at once
        (`_abandoned`). A known limit is that two hooks breaking one
        abandoned lock at once may both take it, and a judgement slower than
        `LOCK_STALE_SECONDS` whose holder cannot be told may lose it. After
        `LOCK_WAIT_SECONDS`, or at once when the lock file cannot be made at
        all, as when a folder sits at its path, the caller goes on without
        it, as before the lock, since a hook must not hang; that risks only
        the old race."""

        folder = self.directory / LOCKS_DIR
        path = folder / f"{_safe_name(session_id)}.lock"
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
        deadline = time.monotonic() + LOCK_WAIT_SECONDS
        try:
            self._ensure_private_directory(folder)
            usable = True
        except (OSError, StateUnsafe):
            usable = False  # The caller's own load meets the same folder and says so.
        held = False
        while usable and not held:
            try:
                handle = os.open(path, flags, 0o600)
            except FileExistsError:
                if path.is_dir():
                    break  # Not a lock any hook can take or break.
                if _abandoned(path):
                    with contextlib.suppress(OSError):  # Another waiter broke it first.
                        path.unlink(missing_ok=True)
                elif time.monotonic() >= deadline:
                    break
                else:
                    time.sleep(LOCK_RETRY_SECONDS)
                continue
            except PermissionError:
                # On Windows, a lock whose deletion waits on a reader refuses
                # a new create for a moment: busy, unless a folder is there.
                if path.is_dir() or time.monotonic() >= deadline:
                    break
                time.sleep(LOCK_RETRY_SECONDS)
                continue
            except OSError:
                break
            held = True
            try:
                os.write(handle, str(os.getpid()).encode("ascii"))
            except OSError:
                pass  # The lock still holds; with no id, only its age frees it.
            finally:
                os.close(handle)
        try:
            yield held
        finally:
            if held:
                _unlink_lock(path)

    def onboarding_shown(self, project_key: str) -> list[str] | None:
        """The skills the onboarding notice last named for the project
        `project_key`, or None when it was never shown or its record is unreadable."""

        path = self._onboarding_path(project_key)
        self._ensure_private_directory(path.parent)
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return _string_list(_expect(data, dict).get("skills"))
        except (OSError, ValueError):
            return None

    def record_onboarding_shown(self, project_key: str, skills: list[str]) -> None:
        """Record which skills the project's onboarding notice now names, atomically."""

        path = self._onboarding_path(project_key)
        self._ensure_private_directory(path.parent)
        _write_json(path, {"skills": list(skills)})

    def claim_turn(self, session_id: str, turn_key: str, purpose: str,
                   agent_id: str | None = None) -> bool:
        """Claim the marker for `purpose` in `turn_key`; True for the first claim.

        `purpose` names what the claim gives once per turn, such as the
        unseen-line advice or one gate's full text (Ticket 095); claims for
        different purposes in one turn never meet. The marker belongs to the
        session, or to its subagent `agent_id`, so each subagent's turns claim
        apart from the parent's. The claim is one exclusive file create, so of
        several hooks claiming at once exactly one gets True. A successful
        claim drops the same owner's markers of other turns, whatever their
        purpose. Raises OSError, or StateUnsafe, when the marker cannot be
        made or read.
        """

        folder = self.directory / TURN_MARKERS_DIR
        self._ensure_private_directory(folder)
        prefix, turn, marker = self._marker(session_id, turn_key, purpose, agent_id)
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
        try:
            os.close(os.open(marker, flags, 0o600))
        except FileExistsError:
            return False
        self._drop_markers(folder, prefix, keep=turn)
        return True

    def turn_claimed(self, session_id: str, turn_key: str, purpose: str) -> bool:
        """Whether the session's marker for `purpose` in `turn_key` was already
        claimed (`claim_turn`). It claims nothing, and a marker it cannot see
        counts as not claimed."""

        return self._marker(session_id, turn_key, purpose)[2].is_file()

    def _marker(self, session_id: str, turn_key: str, purpose: str,
                agent_id: str | None = None) -> tuple[str, str, Path]:
        """The owner's marker name prefix, the turn's, and the marker's path."""

        owner = _safe_name(session_id)
        if agent_id is not None:
            owner += AGENT_SEPARATOR + _safe_name(agent_id)
        prefix = f"{owner}."
        turn = f"{prefix}{_safe_name(turn_key)}."
        return prefix, turn, self.directory / TURN_MARKERS_DIR / f"{turn}{_safe_name(purpose)}"

    def clear_turn_markers(self, session_id: str) -> None:
        """Drop the turn markers of the session and its subagents, best effort,
        as its state is reset."""

        folder = self.directory / TURN_MARKERS_DIR
        if folder.is_dir():
            self._drop_markers(folder, f"{_safe_name(session_id)}.")
            self._drop_markers(folder, f"{_safe_name(session_id)}{AGENT_SEPARATOR}")

    @staticmethod
    def _drop_markers(folder: Path, prefix: str, keep: str | None = None) -> None:
        """Drop the markers whose names start with `prefix`, but those that
        start with `keep`, best effort."""

        # Safe names hold no ".", separator, or glob character, so the prefix
        # matches only its owner's markers, and `keep` only one turn's.
        for old in folder.glob(f"{prefix}*"):
            if keep is None or not old.name.startswith(keep):
                try:
                    old.unlink(missing_ok=True)
                except OSError:
                    pass  # A stale marker only names an old turn; the next claim retries.

    def _ensure_private_directory(self, directory: Path | None = None) -> None:
        ensure_private_directory(directory or self.directory)

    def _path(self, session_id: str) -> Path:
        return self.directory / f"{_safe_name(session_id)}.json"

    def _onboarding_path(self, project_key: str) -> Path:
        # A digest: a project path can be long and holds characters no file name may.
        digest = hashlib.sha256(project_key.encode("utf-8")).hexdigest()[:32]
        return self.directory / ONBOARDING_DIR / f"{digest}.json"


def _safe_name(raw: str) -> str:
    """A file name part for `raw` (a session id, agent id, turn key, or
    purpose) that no other `raw` shares, on any file system.

    A name already made of lowercase letters, digits, `_` and `-`, at most
    128 of them, is kept as it is, so state saved under it before stays
    found. Any other is a readable prefix, `HASH_SEPARATOR`, and a digest of
    the whole name: the separator is in no kept name, so the two forms never
    meet, and the digest tells apart names that differ only in case, in an
    unsafe character, or past the prefix. No part holds a `.`, the marker
    separators, or a glob character.
    """

    if SAFE_NAME_RE.fullmatch(raw):
        return raw
    prefix = UNSAFE_NAME_CHARS.sub("_", raw.lower())[:64]
    return f"{prefix}{HASH_SEPARATOR}{hashlib.sha256(raw.encode('utf-8')).hexdigest()[:16]}"


def _write_json(path: Path, data) -> None:
    """Write `data` to `path` atomically so a concurrent hook never reads half a file."""

    # Unique per process, created exclusively and never through a link.
    # `tempfile` is avoided because importing it costs every hook call
    # several milliseconds.
    temp = path.with_name(f"{path.name}.{os.getpid()}.tmp")
    temp.unlink(missing_ok=True)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    try:
        with os.fdopen(os.open(temp, flags, 0o600), "w", encoding="utf-8") as stream:
            json.dump(data, stream)
        _replace(temp, path)
    except BaseException:
        temp.unlink(missing_ok=True)
        raise


def _unlink_lock(path: Path) -> None:
    """Let the lock at `path` go, retried briefly: on Windows deleting it
    fails while a waiting hook has it open to read its holder's id, and a
    lock left behind under a live holder's id would hold every hook up
    until it is stale. One that still cannot be deleted is left to that."""

    for attempt in range(REPLACE_ATTEMPTS):
        try:
            path.unlink(missing_ok=True)
            return
        except PermissionError:
            if attempt < REPLACE_ATTEMPTS - 1:
                time.sleep(REPLACE_RETRY_SECONDS)
        except OSError:
            return


def _abandoned(path: Path) -> bool:
    """Whether the lock file at `path` was left by a hook that died: the
    process its id names is gone, it holds no id well after it was made, or
    it is older than `LOCK_STALE_SECONDS`, which also covers a holder whose
    process cannot be told. A file that cannot be read is not abandoned,
    since its holder may be letting it go."""

    age = _age_seconds(path)
    if age > LOCK_STALE_SECONDS:
        return True
    try:
        text = path.read_text(encoding="ascii").strip()
    except (OSError, ValueError):
        return False
    if not text:
        return age > LOCK_EMPTY_GRACE_SECONDS
    try:
        pid = int(text)
    except ValueError:
        return age > LOCK_EMPTY_GRACE_SECONDS  # Not a lock this core wrote.
    return _process_alive(pid) is False


def _process_alive(pid: int) -> bool | None:
    """Whether process `pid` still runs, or None when that cannot be told.
    On Windows it asks the process's exit code; elsewhere, signal 0, which
    tests the process without touching it (on Windows `os.kill` would end it)."""

    if pid == os.getpid():
        return True
    if pid <= 0:
        return False
    if os.name == "nt":
        import ctypes  # Only on a held lock: importing it costs every hook a few milliseconds.
        from ctypes import wintypes

        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel32.OpenProcess.argtypes = (wintypes.DWORD, wintypes.BOOL, wintypes.DWORD)
        kernel32.OpenProcess.restype = wintypes.HANDLE
        kernel32.GetExitCodeProcess.argtypes = (wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD))
        kernel32.CloseHandle.argtypes = (wintypes.HANDLE,)
        query_limited_information, invalid_parameter, still_active = 0x1000, 87, 259
        handle = kernel32.OpenProcess(query_limited_information, False, pid)
        if not handle:
            # No such process; any other refusal, such as access denied,
            # cannot be told, so the lock's age decides.
            return False if ctypes.get_last_error() == invalid_parameter else None
        try:
            code = wintypes.DWORD()
            if not kernel32.GetExitCodeProcess(handle, ctypes.byref(code)):
                return None
            return code.value == still_active
        finally:
            kernel32.CloseHandle(handle)
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except OSError:
        return None
    return True


def _age_seconds(path: Path) -> float:
    """How long ago `path` was last written; 0 when it cannot be seen, as
    when the hook holding it has just let it go."""

    try:
        return time.time() - path.stat().st_mtime
    except OSError:
        return 0.0


def _replace(source: Path, target: Path) -> None:
    """`os.replace`, retried briefly: on Windows it fails while another hook
    process has the target open for reading."""

    for attempt in range(REPLACE_ATTEMPTS):
        try:
            os.replace(source, target)
            return
        except PermissionError:
            if attempt == REPLACE_ATTEMPTS - 1:
                raise
            time.sleep(REPLACE_RETRY_SECONDS)
