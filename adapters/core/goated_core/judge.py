"""The core's Python call: one event of a session in, one decision out.

Each function judges one kind of event of the event model (ADR 0004): a
pending call, a turn's end, a finished call, a submitted prompt, and a
session start. The caller says where the event happens (`Situation`) and
how to read the session's turns (a `TurnReader`); the core loads the
session's saved facts by its id, judges, saves, and answers with a
`Decision`. Hold texts keep their harness wording in `wording` slots, which
the caller fills: `request.decide` fills them with neutral words, and the
Claude Code adapter with its own.

A function raises what its caller's reader raises, and `StateUnsafe` when
the state folder cannot be trusted; the caller lets the event through then,
as the fail-open rule requires. Saving is best effort: a decision stands,
with a warning, when its state cannot be saved.
"""

from __future__ import annotations

import functools
from collections.abc import Callable
from pathlib import Path
from typing import NamedTuple

from . import actions, events, friction, gates, reference_reads
from . import usage_log as usage_log_module
from .events import Call, Result, Turn
from .overrides import GOATED_SKILLS, parse_overrides
from .state import SessionState, StateStore, StateUnsafe

# The turn marker's purpose for the early closeout note (Ticket 096), apart
# from the unseen-line advice's and each hold's.
CLOSEOUT_NOTE = "closeout-note"

# Notice kinds, as the event model's `notice` names them.
FAIL_OPEN = "fail_open"
WARNING = "warning"
OVERRIDE_RECORDED = "override_recorded"
CLOSEOUT_NOTE_KIND = "closeout_note"
SESSION_NOTICE = "session_notice"
SKIP_CARRIED = "skip_carried"
READS_OWED = "reads_owed"
ROUTE_CONTINUED = "route_continued"

# Session start sources, as the event model's `session_start` names them.
NEW = "new"
RESUMED = "resumed"
AFTER_COMPACTION = "after_compaction"
CLEARED = "cleared"

RETROSPECTIVE_NOTICE = (
    "{count} GOATED holds this session were declined or left unanswered. The "
    "`retrospective` skill can turn that friction into improvements to the "
    "project's checks, standards, or instructions, such as after a wave of "
    "delegated tickets is merged. This is a notice; nothing is held."
)

# How the caller reads the session's turns: given the key of the last turn
# the core has seen (None for none), the turns back to and including it,
# oldest first, ending with the current turn, and the caller's key for the
# prompt that opened the current turn (None when it has none). It raises
# when the current turn cannot be read.
TurnReader = Callable[[str | None], tuple[list[Turn], object]]


class Settings:
    """What the core reads besides the events: where it keeps session state
    (`state_dir`), the skill namespaces whose `ns:skill` loads count as GOATED
    skills, the installed registry the `reference-reads` gate reads (None
    reads none; `registry_named`: the user named that path, so a missing
    file there is worth a warning), `upgrade_state`, which a caller whose
    earlier versions saved state in its own words passes (see `StateStore`),
    and `usage_log`, the usage log each event is appended to
    (`usage_log.UsageLog`; None keeps none).
    """

    __slots__ = ("state_dir", "skill_namespaces", "registry_path", "registry_named",
                 "upgrade_state", "usage_log")

    def __init__(self, state_dir: Path, skill_namespaces: tuple[str, ...] = (),
                 registry_path: Path | None = None, registry_named: bool = False,
                 upgrade_state: Callable[[object], object] | None = None,
                 usage_log: usage_log_module.UsageLog | None = None) -> None:
        self.state_dir = Path(state_dir)
        self.skill_namespaces = tuple(skill_namespaces)
        self.registry_path = Path(registry_path) if registry_path is not None else None
        self.registry_named = registry_named
        self.upgrade_state = upgrade_state
        self.usage_log = usage_log

    def store(self) -> StateStore:
        return StateStore(self.state_dir, self.upgrade_state)


class Situation:
    """Where one event happens, as the caller knows it.

    `session_id` keys the session's saved facts. `agent_id` names the
    subagent acting, or is None for the main agent. `project` says which
    files are the project's (`actions.find_project`). `agent_folders` are
    the harness's own configuration folders, where no write is scratch.
    `installed_skills()` gives the skill names the harness can find, or None
    when it cannot tell; it is called only when needed. `subagents(turn)`
    gives the turns of each agent `turn`'s spawns started, by agent id, and
    the ids whose turns could not be read; by default, none.
    `project_folder` is the project's folder as the harness names it, whose
    key the usage log records (never the path itself), or None.
    `context_docs()` gives the project's own context documents that exist,
    as paths from its root (`gates.CONTEXT_DOCS`), which the caller checks;
    the core reads no file for them. It is called only when a text names
    them; by default, none.
    """

    __slots__ = ("session_id", "agent_id", "project", "agent_folders", "installed_skills",
                 "context_docs", "subagents", "project_folder")

    def __init__(self, session_id: str, *, agent_id: str | None = None,
                 project: actions.Project | None = None, agent_folders: list[str] = (),
                 installed_skills: Callable[[], frozenset[str] | None] = lambda: None,
                 context_docs: Callable[[], list[str]] = lambda: [],
                 subagents: Callable[[Turn], tuple[dict, list[str]]] = lambda turn: ({}, []),
                 project_folder: str | None = None) -> None:
        self.session_id = session_id
        self.agent_id = agent_id
        self.project = project
        self.agent_folders = list(agent_folders)
        self.installed_skills = installed_skills
        self.context_docs = context_docs
        self.subagents = subagents
        self.project_folder = project_folder


class Notice(NamedTuple):
    """Something to tell the agent or the user that holds nothing: its kind
    (`FAIL_OPEN`, `WARNING`, `OVERRIDE_RECORDED`, `CLOSEOUT_NOTE_KIND`,
    `SESSION_NOTICE`, `SKIP_CARRIED`, `READS_OWED`, `ROUTE_CONTINUED`) and
    its text."""

    kind: str
    text: str


class Decision:
    """The core's answer to one event: the holds it meets, in the order the
    gates fire (`gates.Shown`; none means allow), and its notices, in the
    order they arose. `shell` is the shell kind of the session's last shell
    command, or None before its first, for a harness that names a shell
    call that can carry a line."""

    __slots__ = ("holds", "notices", "shell")

    def __init__(self, holds: list[gates.Shown] = (), notices: list[Notice] = (),
                 shell: str | None = None) -> None:
        self.holds = list(holds)
        self.notices = list(notices)
        self.shell = shell

    @property
    def held(self) -> bool:
        return bool(self.holds)

    def message(self) -> str:
        """Every hold in one message, hold lines and texts, as a harness with
        one reason field shows it; "" for none."""

        return gates.message(self.holds)

    def texts(self, *kinds: str) -> list[str]:
        """The texts of the notices of `kinds`, in order."""

        return [notice.text for notice in self.notices if notice.kind in kinds]


def _warnings(*texts: str | None) -> list[Notice]:
    return [Notice(WARNING, text) for text in texts if text]


def overrides_for(state: SessionState, turn: Turn, prompt_key: object) -> dict:
    """The overrides `record_prompt` kept, only for the typed prompt that
    opened `turn`, whose key the caller gives as `prompt_key` (None when it
    has none): a kept key that differs from it applies none."""

    stored = state.overrides or {}
    if not turn.typed:
        return {}
    if stored.get("prompt") and prompt_key and stored["prompt"] != prompt_key:
        return {}
    return stored


def _one_hook_at_a_time(judge_event: Callable[..., "Decision"]) -> Callable[..., "Decision"]:
    """Judge an event that loads, changes, and saves the session's state while
    holding the session's lock (`StateStore.locked`), so hooks the harness
    runs at once, such as those of several edits sent in one message, do not
    drop each other's changes: what one edit owes, or a lasting skip."""

    @functools.wraps(judge_event)
    def judged(settings: Settings, situation: Situation, *args, **kwargs) -> Decision:
        with settings.store().locked(situation.session_id):
            return judge_event(settings, situation, *args, **kwargs)

    return judged


@_one_hook_at_a_time
def judge_call(settings: Settings, situation: Situation, call: Call,
               read: TurnReader) -> Decision:
    """Judge `call`, about to run: every hold it meets, in one decision."""

    if situation.agent_id is not None:
        return _judge_subagent_call(settings, situation, call, read)
    store = settings.store()
    state, state_warning = store.load(situation.session_id)
    turns, prompt_key = read(state.last_turn)
    settled = _fold(state, turns, settings, situation)
    current = turns[-1]
    overrides = overrides_for(state, current, prompt_key)
    gates.note_task_routed(state, current, overrides)
    unread: list[str] = []

    def spawned() -> dict:
        # Unreadable subagent turns count as no changes, with a warning, as at the turn's end.
        found, missed = situation.subagents(current)
        unread.extend(missed)
        return found

    earlier = _since_compaction(state)
    task_skips = actions.TaskSkips(state.lasting_skip_keys(), state.carried_notice_keys())
    points = actions.ReviewPoints(state.review_point_lines())
    registry_warnings: list[str] = []
    routing = gates.check_routing(
        state, call, current, overrides,
        orientation_installed=lambda: gates.ORIENTATION_SKILL in (
            situation.installed_skills() or ()),
        writes_scratch=lambda: actions.writes_only_scratch(
            call, situation.project, situation.agent_folders),
        context_docs=situation.context_docs,
    )
    # Every gate judges the call, so one decision carries every hold (Ticket 095).
    holds = routing + actions.check_action(
        call, current, overrides, settings.skill_namespaces, situation.project, spawned,
        earlier,
        closeout=actions.Closeout(state.spawn_templates_of(current.key),
                                  _route_intensity(state), state.briefed,
                                  _owed_reads(state, current.key), points),
        references=lambda: _registry_references(settings, registry_warnings),
        task_skips=task_skips,
    )
    state.record_lasting_skips(current.key, task_skips.cleared)
    state.record_review_points(current.key, points.met)
    if not holds:
        # A lasting skip's notice is given once per task for its gate, skill and kind.
        state.record_carried_notices(current.key, task_skips.carried)
    if not holds and call.id:
        # Which templates a spawn's brief followed, for the closeout.
        templates = actions.brief_templates(
            call, current, overrides, settings.skill_namespaces, earlier)
        if templates:
            state.record_spawn_templates(current.key, call.id, templates)
        # What a write that landed past a read gate still owes, for the Reads item.
        if task_skips.owed:
            state.record_owed_reads(current.key, call.id, task_skips.owed)
    settled += friction.observe(state, current, friction.action_of(call), holds)
    shown = gates.shown_holds(holds, lambda purpose: _claim_turn(
        store, situation.session_id, current.key, purpose), call=call)
    # A held call did not go through, so no lasting skip let it through, and it owes nothing.
    notices = [] if holds else (
        [Notice(SKIP_CARRIED, text) for text in task_skips.notices]
        + [Notice(READS_OWED, text) for text in task_skips.owed_notices])
    notices += _warnings(state_warning, _save(store, situation.session_id, state),
                         _unread_warning(unread), *registry_warnings)
    held_class = actions.file_class(call, situation.project) if holds else None
    log = _logged(settings, situation, lambda r: (
        r.turns(turns, pending=call), r.outcomes(settled), r.holds(shown, file_class=held_class),
        r.notices(_kinds(notices))))
    return Decision(shown, notices + _warnings(log), state.shell)


def _owed_reads(state: SessionState, turn: str) -> dict[str, list[actions.OwedRead]]:
    """The reads `turn`'s landed writes owe, as the closeout takes them."""

    return {call_id: [actions.OwedRead(**read) for read in reads]
            for call_id, reads in state.owed_reads_of(turn).items()}


def _judge_subagent_call(settings: Settings, situation: Situation, call: Call,
                         read: TurnReader) -> Decision:
    """Apply only the action gates, to the subagent's own current turn (spec R9).

    Routing gates do not apply: the parent's brief carries the route. Nobody
    types a subagent's prompts, so no override applies. A commit meets the
    closeout of the subagent's own turn (Ticket 098); it was started from its
    parent's brief, so, as a briefed session, it meets no Review item, and it
    records no spawn templates, so the `review-intake` gate holds nothing.
    No session state is read or saved but the turn markers, which are the
    subagent's own.
    """

    turns, _ = read(None)
    holds = actions.check_action(
        call, turns[-1], {}, settings.skill_namespaces, situation.project,
        closeout=actions.Closeout(briefed=True),
    )
    store = settings.store()
    shown = gates.shown_holds(holds, lambda purpose: _claim_turn(
        store, situation.session_id, turns[-1].key, purpose, situation.agent_id), call=call)
    held_class = actions.file_class(call, situation.project) if holds else None
    log = _logged(settings, situation, lambda r: (
        r.turns(turns, pending=call), r.holds(shown, file_class=held_class)))
    return Decision(shown, _warnings(log), gates.last_shell(turns))


@_one_hook_at_a_time
def judge_turn_end(settings: Settings, situation: Situation, read: TurnReader,
                   final_text: str = "") -> Decision:
    """Judge the end of the current turn: the closeout of a turn that changed
    code. `final_text` is the turn's last reply text when the turns read may
    not hold it yet. A subagent's turn end is never held: its commit meets
    the closeout instead (Ticket 098)."""

    if situation.agent_id is not None:
        return Decision()
    store = settings.store()
    state, state_warning = store.load(situation.session_id)
    turns, prompt_key = read(state.last_turn)
    settled = _fold(state, turns, settings, situation)
    current = turns[-1]
    subagents, unread = situation.subagents(current)
    task_skips = actions.TaskSkips(state.lasting_skip_keys())
    points = actions.ReviewPoints(state.review_point_lines())
    overrides = overrides_for(state, current, prompt_key)
    gates.note_task_routed(state, current, overrides)
    hold = actions.check_closeout(
        current, overrides, settings.skill_namespaces,
        final_text, subagents, situation.project,
        earlier=_since_compaction(state),
        spawn_templates=state.spawn_templates_of(current.key),
        intensity=_route_intensity(state),
        briefed=state.briefed,
        owed_reads=_owed_reads(state, current.key),
        task_skips=task_skips,
        points=points,
    )
    # A skip line meeting the Reads item lasts as one clearing its gate would.
    state.record_lasting_skips(current.key, task_skips.cleared)
    state.record_review_points(current.key, points.met)
    holds = [hold] if hold else []
    settled += friction.observe(state, current, friction.STOP, holds)
    if hold is None:
        # The turn ends here, and so do its typed overrides: a subagent's
        # report arriving later continues the turn without them. Another
        # hook may still hold this end, so the turn then goes on without its
        # overrides, which only holds more.
        state.overrides = {}
    shown = gates.shown_holds(holds, lambda purpose: _claim_turn(
        store, situation.session_id, current.key, purpose))

    notices = _warnings(state_warning, _save(store, situation.session_id, state),
                        _unread_warning(unread))

    def log_turn_end(recorder: usage_log_module.Recorder) -> None:
        recorder.turns(turns, final_text)
        recorder.outcomes(settled)
        recorder.holds(shown, stop=True)
        recorder.notices(_kinds(notices))
        if not shown:
            recorder.turn_end()

    return Decision(shown, notices + _warnings(_logged(settings, situation, log_turn_end)),
                    state.shell)


@_one_hook_at_a_time
def note_finished_call(settings: Settings, situation: Situation, call: Call,
                       read: TurnReader) -> Decision:
    """After the main agent's first finished code change of a turn by a file
    write, one note naming the closeout items the turn will meet (Ticket 096).
    It never holds anything.

    `call` is the finished call, with its result. A subagent has no
    closeout, so gets no note; nor does a turn the closeout already held,
    which has seen its items, nor a turn whose list of items is the one the
    task's last note named (round 7, R4). The note ends by naming the
    project's context documents, when `situation.context_docs()` gives any
    (`gates.context_pointer`). The note's claim on the turn marker has its
    own purpose, and a claim that fails or cannot be made adds no note. Of
    the saved state, only the list the note named is written: the events
    that judge calls own the rest.
    """

    if call.kind != events.FILE_WRITE or situation.agent_id is not None or not call.ok:
        return Decision()
    store = settings.store()
    state, _ = store.load(situation.session_id)
    # The call's pending judgement saved its turn as the last seen, so a turn
    # that already has its note is known here without reading the turns.
    if state.last_turn and store.turn_claimed(situation.session_id, state.last_turn,
                                              CLOSEOUT_NOTE):
        return Decision()
    turns, prompt_key = read(state.last_turn)
    _fold_turns(state, turns, settings, situation)
    current = turns[-1]
    if (state.held_gates.get("turn") == current.key
            and actions.CLOSEOUT_GATE in state.held_gates["gates"]):
        return Decision()
    note = actions.closeout_note(
        current, call, overrides_for(state, current, prompt_key), settings.skill_namespaces,
        situation.project, _since_compaction(state), _route_intensity(state),
        _owed_reads(state, current.key), actions.TaskSkips(state.lasting_skip_keys()))
    if not note.text:
        return Decision()
    try:
        claimed = store.claim_turn(situation.session_id, current.key, CLOSEOUT_NOTE)
    except (OSError, StateUnsafe):
        claimed = False  # The note is advice: without a marker it could repeat, so none.
    # `state` was folded through this turn, so a new task's route has already ended the list.
    if not claimed or list(note.labels) == state.closeout_noted.get("labels"):
        return Decision([], [], state.shell)
    text = note.text
    pointer = gates.context_pointer(situation.context_docs())
    if pointer:
        text += "\n" + pointer
    # Save only the list, onto the state as saved: folding is the judge calls' to save.
    saved, _ = store.load(situation.session_id)
    saved.closeout_noted = {"labels": list(note.labels), "turn": current.key}
    log = _logged(settings, situation, lambda r: r.notices([CLOSEOUT_NOTE_KIND]))
    return Decision([], [Notice(CLOSEOUT_NOTE_KIND, text),
                         *_warnings(_save(store, situation.session_id, saved), log)], state.shell)


@_one_hook_at_a_time
def record_prompt(settings: Settings, situation: Situation, typed_text: str | None,
                  prompt_key: object = None,
                  unseen: Callable[[str | None], list[Turn] | None] = lambda since: None
                  ) -> Decision:
    """Record a prompt that opens a turn: the overrides a person typed apply
    to that turn only (`overrides_for`).

    `typed_text` is the person's own text, harness blocks and pasted text
    removed, or None for a prompt a person did not type, which records no
    override. `prompt_key` is the caller's key for the prompt, matched when
    the turn is judged. `unseen(since_key)` reads the turns since the last
    one the core saw, best effort (None when it cannot): holds the last turn
    left open are unanswered unless what followed them, which no event may
    have shown, or this prompt's overrides settle them. A prompt that
    continues a turn is not recorded at all. A subagent's prompts carry no
    override. A person's prompt in a session with a routed task also gets
    the `ROUTE_CONTINUED` notice (`gates.continued_route_notice`), judged
    after the unseen turns are folded in, so a route line written after the
    last judged call counts for the notice as it does for the gates.
    """

    if situation.agent_id is not None:
        return Decision()
    store = settings.store()
    state, state_warning = store.load(situation.session_id)
    logging = settings.usage_log is not None
    turns = None
    settled: list[tuple[str, str]] = []
    if typed_text is not None:
        known = situation.installed_skills() or GOATED_SKILLS
        found = parse_overrides(typed_text, known)
        # The log reads the last turn's tail too, unless it logged that turn's end.
        if state.open_holds or (logging and not _recorder(settings, situation).turn_ended()):
            turns = unseen(state.last_turn)
            if turns and state.open_holds:
                settled = _settle(state, turns, settings)
        settled += friction.close_turn(state, found)
    else:
        found = parse_overrides("")

    continued = None
    if typed_text is not None:
        # Only from a turn already seen, as the next judged call folds: with
        # none (after a clear, a reset, or a compaction's start), what a
        # reader returns may come from before that boundary, which the gates
        # do not fold either, so the notice and the gates agree.
        if state.last_turn is not None:
            before = turns if turns is not None else unseen(state.last_turn)
            if before:
                _fold_turns(state, before, settings, situation)
                # The overrides still kept are the last typed turn's, so a
                # `skip routing` there routes a task its later lines started.
                for turn in before:
                    gates.note_task_routed(state, turn, overrides_for(state, turn, None))
        continued = gates.continued_route_notice(state)
    state.overrides = {"prompt": prompt_key, **found}
    notices = []
    if found["phrases"]:
        typed = ", ".join(f'"{phrase}"' for phrase in found["phrases"])
        notices.append(Notice(OVERRIDE_RECORDED, f"recorded your override for this prompt: {typed}"))
    if continued:
        notices.append(Notice(ROUTE_CONTINUED, continued))
    if typed_text is not None and friction.claim_retrospective_notice(state):
        notices.append(Notice(SESSION_NOTICE, RETROSPECTIVE_NOTICE.format(count=state.friction)))
    notices += _warnings(state_warning, _save(store, situation.session_id, state))

    def log_prompt(recorder: usage_log_module.Recorder) -> None:
        # What the last turn did after its last event, then this prompt and its notices.
        if turns:
            recorder.turns(turns)
        recorder.outcomes(settled)
        if typed_text is not None:
            recorder.prompt(typed_text, found["phrases"])
        recorder.notices(_kinds(notices))

    return Decision([], notices + _warnings(_logged(settings, situation, log_prompt)),
                    state.shell)


@_one_hook_at_a_time
def start_session(settings: Settings, situation: Situation, source: str,
                  first_notices: Callable[[], list[str]] = lambda: []) -> Decision:
    """Start or restart the session's context, from `source` (`NEW`,
    `RESUMED`, `AFTER_COMPACTION`, `CLEARED`).

    After a compaction or a clear every skill must load again, and the
    design references and spawn-brief templates be read again, because their
    text was summarized away. After a compaction the route itself carries
    over (spec R5); a clear ends the task, so the next prompt is routed
    afresh (round 6's R2: the route survives a compaction only). Turns
    from before the boundary are never folded back in. A new session has no
    task yet, so `continue` may start one. `first_notices()` gives the
    harness's own session notices, asked for once per session; they are
    returned as session notices. A subagent's start changes nothing.
    """

    if situation.agent_id is not None:
        return Decision()
    store = settings.store()
    state, state_warning = store.load(situation.session_id)
    if source == NEW and state.task is None:
        state.task_unknown = False
    if source in (AFTER_COMPACTION, CLEARED):
        state.forget_context()
        friction.forget_open(state)
        state.last_turn = None
        store.clear_turn_markers(situation.session_id)
    if source == CLEARED:
        # No task is known to run: the next route line starts one afresh.
        state.task, state.task_unknown = None, False
        state.end_task()
    notices = []
    if not state.policy_notice_shown:
        state.policy_notice_shown = True
        notices = [Notice(SESSION_NOTICE, text) for text in first_notices()]
    notices += _warnings(state_warning, _save(store, situation.session_id, state))

    def log_start(recorder: usage_log_module.Recorder) -> None:
        if source == AFTER_COMPACTION:
            recorder.compaction()
        recorder.notices(_kinds(notices))

    log = (_logged(settings, situation, log_start)
           if source == AFTER_COMPACTION or notices else None)
    return Decision([], notices + _warnings(log), state.shell)


# Helpers ------------------------------------------------------------------


def _fold(state: SessionState, turns: list[Turn], settings: Settings,
          situation: Situation) -> list[tuple[str, str]]:
    """Bring `state` up to date with `turns`, and settle the friction
    count's open holds against them; returns those settled, as (gate, outcome)."""

    _fold_turns(state, turns, settings, situation)
    return _settle(state, turns, settings)


def _fold_turns(state: SessionState, turns: list[Turn], settings: Settings,
                situation: Situation) -> None:
    """`gates.fold_turns`, relative paths taken from the session's folder and
    files judged the project's as `actions.reads_as_in_project` reads them."""

    gates.fold_turns(state, turns, settings.skill_namespaces,
                     situation.project.cwd if situation.project else None,
                     lambda path: actions.reads_as_in_project(path, situation.project))


def _settle(state: SessionState, turns: list[Turn],
            settings: Settings) -> list[tuple[str, str]]:
    return friction.settle(state, turns,
                           lambda raw: gates.goated_skill_name(raw, settings.skill_namespaces))


def _kinds(notices: list[Notice]) -> list[str]:
    """The kinds of `notices`, in order, as the usage log keeps them (round 6, R15)."""

    return [notice.kind for notice in notices]


def _logged(settings: Settings, situation: Situation,
            say: Callable[[usage_log_module.Recorder], object]) -> str | None:
    """Append to the usage log what `say` tells a recorder, when the settings
    keep a log; the warning when it could not be written, else None."""

    if settings.usage_log is None:
        return None
    recorder = _recorder(settings, situation)
    try:
        say(recorder)
    except Exception as exc:  # noqa: BLE001 - the log never blocks a call
        return f"could not write the usage log ({type(exc).__name__})"
    return recorder.flush()


def _recorder(settings: Settings, situation: Situation) -> usage_log_module.Recorder:
    """The usage log's recorder for this event; `settings.usage_log` is set."""

    return usage_log_module.Recorder(
        settings.usage_log, settings.state_dir, situation.session_id, situation.agent_id,
        situation.project_folder, lambda: situation.installed_skills() or GOATED_SKILLS)


def _registry_references(settings: Settings, warnings: list[str]) -> tuple:
    """The installed registry's declared references, or () when it cannot be
    used, failing open: a registry that does not parse, or a missing one the
    user named, adds a warning to `warnings`; a missing default is silent."""

    try:
        return reference_reads.load(settings.registry_path)
    except reference_reads.RegistryUnreadable as exc:
        if not exc.missing or settings.registry_named:
            warnings.append(f"could not use the GOATED registry at {settings.registry_path} "
                            f"({exc}), so the reference-reads gate asked for nothing")
        return ()


def _route_intensity(state: SessionState) -> str | None:
    """The current task's route intensity (`full`), or None without a `requires:` route."""

    return state.task.route.get("intensity") if state.task else None


def _since_compaction(state: SessionState) -> actions.SinceCompaction:
    """What the main agent's saved state says counts until the next compaction."""

    return actions.SinceCompaction(
        frozenset(state.loads), frozenset(state.reference_reads), frozenset(state.template_reads),
        spans_turns=True, skill_references_read=frozenset(state.skill_reference_reads))


def _claim_turn(store: StateStore, session_id: str, turn_key: str, purpose: str,
                agent_id: str | None = None) -> bool:
    """`StateStore.claim_turn`, or True when the marker cannot be claimed or
    read: the hold then gives its full text, and nothing fails."""

    try:
        return store.claim_turn(session_id, turn_key, purpose, agent_id)
    except (OSError, StateUnsafe):
        return True


def _unread_warning(unread: list[str]) -> str | None:
    """The warning for subagents whose turns could not be read, whose
    changes the action and closeout gates therefore left out; None for none."""

    if not unread:
        return None
    return ("could not read the transcript of subagent " + ", ".join(unread)
            + ", so its changes were not checked")


def _save(store: StateStore, session_id: str, state: SessionState) -> str | None:
    """Save best effort: a hold already decided stands even if saving fails."""

    try:
        store.save(session_id, state)
    except OSError as exc:
        return f"could not save its session state ({exc.strerror or type(exc).__name__})"
    return None
