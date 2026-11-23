"""The routing gates, and the hold type, hold message, shared hold texts and
load naming every gate shares.

This module owns which tools the routing gates hold, which skill loads count,
and when a routing hold clears; `actions.py` owns the action and closeout
gates. The rules enforce contracts defined elsewhere, never new ones
(ADR 0003):

- router first: `using-goated-ai-skills` says to load it before the first edit
  or command of a task;
- route line: the router's output contract ends routing with a
  `goated-route:` line;
- pipeline: a route's `requires:` skills "must load before the first write".
  The shared policy says to drop a skill that does not apply by writing a
  corrected route line (the last one wins), so this hold is strict. A load
  counts from its call until the next compaction (spec R3), when its text
  leaves the context. In a session routed by its brief, the router's
  orientation skill, when installed, joins a `standard` or `full` route;
  whole reads of `ORIENTATION_READS` distinct files meet it as well as its
  load does (spec R3), since targeted reading is that skill's own work. A
  whole shell print of a file counts as a whole read of it here, and only
  here (Ticket 110).

The routing gates judge file writes, shell commands, and spawns. A spawn
that only proposes work (`starts_now` false) runs nothing, so it passes
them all; a spawn of a read-only agent only delegates reads, so it passes
`pipeline` (and the `spawn` gate in actions.py) but still needs the router
and a route line.

A write whose every file is scratch, outside the project and any other checkout
(`actions.writes_only_scratch`), meets none of these holds (spec R4): routing
guards the project's work, not a scratch copy.
"""

from __future__ import annotations

import copy
import hashlib
import os
import re
from typing import Callable, NamedTuple

from . import contracts, design_reads, events, markers, reference_reads, shell, wording
from .events import Call, Turn
from .state import SessionState, Task
from .wording import NO_RANGE, READ, SKILL_TOOL, short_advice, unseen_line_advice

ROUTER_SKILL = "using-goated-ai-skills"
ORIENTATION_SKILL = "session-start-progressive-disclosure"
# How many distinct files a briefed session reads whole to orient without the skill.
ORIENTATION_READS = 3
# How many distinct project files it reads or prints, whole or in part, to orient
# without the skill (round 6's R3, decision U1).
ORIENTATION_FILES = 5
# The call kinds the routing gates judge.
ROUTED_KINDS = frozenset({events.FILE_WRITE, events.SHELL_COMMAND, events.SPAWN})

STRICT = "strict"


class Hold:
    """A held tool call: which gate, what kind, and what the agent must do.

    `short` says the same in brief (`short_form`), for a later hold in the
    turn that asks the same (`text`). None when the full text is already as
    short.
    """

    __slots__ = ("gate", "kind", "instruction", "short")

    def __init__(self, gate: str, kind: str, instruction: str,
                 short: "ShortForm | None" = None) -> None:
        self.gate = gate
        self.kind = kind
        self.instruction = instruction
        self.short = short

    def text(self, claim: Callable[[str], bool]) -> str:
        """The text this hold shows: its short form once the turn has shown
        the same ask in full, else the full text. `claim` is as `shown_holds`
        takes it; the purpose is the gate and what is unmet (`ask_purpose`),
        so a gate's new ask, such as a change read after a load, comes in full."""

        if self.short and not claim(ask_purpose(self.gate, self.short.unmet)):
            return self.short.text
        return self.instruction

    def with_note(self, note: str) -> "Hold":
        """A new hold, the same as this one but with `note` ending its full
        and short texts; the short form's ask (`unmet`) is unchanged."""

        noted = copy.copy(self)  # Its gate and kind are this hold's, read where it was built.
        noted.instruction = f"{self.instruction} {note}"
        noted.short = self.short and self.short._replace(text=f"{self.short.text} {note}")
        return noted


def ask_purpose(gate: str, ask: str) -> str:
    """The turn marker's purpose for one ask of `gate`, named by `ask`."""

    return f"{gate}-{hashlib.sha256(ask.encode('utf-8')).hexdigest()[:16]}"


class ShortForm(NamedTuple):
    """A hold's short form: `unmet`, what is still missing, which names the
    ask, and `text`, the whole short form, which also says every constraint
    needed to clear it and keeps each skill, reference and skip line the
    full text names."""

    unmet: str
    text: str


def short_form(unmet: str, clear: str) -> ShortForm:
    """The short form for `unmet` and `clear`, how to clear it, ending in a full stop."""

    return ShortForm(unmet, f"Still unmet: {unmet}. {clear}")


# The turn marker's purpose for the unseen-line advice; a hold's ask has its
# own purpose (`ask_purpose`).
ADVICE = "advice"

# Paragraphs several holds or closeout items share (Ticket 095). How a hold
# asks for a change read; no command is backticked, since a reader of hold
# texts takes a backticked name as a skill to load (contract, Hold Text).
CHANGE_READ = (
    f"print its diff with a git diff or git show command, or {READ} a file you changed; "
    "a listing of names or counts, such as --stat or --name-only, does not count"
)
CHAINED_STEPS = "The whole command was held, so rerun any steps chained before it too."
UNFINISHED_READ = ("A read chained in the same command, or made in parallel with this call, "
                   "has not finished, so it does not count.")
SKIP_LINE_RULE = "A skip line must name the skill and give a reason of three or more words."
# Each shared paragraph, with what its later copies in one message become.
_SHARED_TEXTS = (
    (CHANGE_READ, f"print the diff or {READ} a file you changed, as above"),
    (CHAINED_STEPS + " ", ""),
    (CHAINED_STEPS, ""),
    (UNFINISHED_READ + " ", ""),
    (SKIP_LINE_RULE, ""),
)


def _once(texts: list[str], full: str, again: str) -> list[str]:
    """`texts`, read in order as one text, with every copy of `full` after
    the first replaced by `again`. No copy spans two texts: no shared
    paragraph holds a hold line or the blank line between holds."""

    kept, seen = [], False
    for text in texts:
        if not seen and (first := text.find(full)) >= 0:
            seen, end = True, first + len(full)
            text = text[:end] + text[end:].replace(full, again)
        elif seen:
            text = text.replace(full, again)
        kept.append(text)
    return kept


class Shown(NamedTuple):
    """One hold as a decision shows it: its gate, its kind, and the text that
    follows its `goated-hold:` line, harness wording still in `wording` slots."""

    gate: str
    kind: str
    text: str

    def line(self) -> str:
        """The hold line, as the contract's Hold Messages section defines it."""

        return f"goated-hold: {self.gate} | {self.kind}"


def message(shown: list[Shown]) -> str:
    """The one message that carries `shown`, as `shown_holds` gives them:
    each hold's line and text, with a blank line between holds."""

    return "\n\n".join(f"{hold.line()}\n{hold.text}" for hold in shown)


# Ends a held file edit's message: the harness may run the other calls of its
# message, so the file may have changed (round 6, R11).
EDIT_HELD = ("Other calls of this message may have landed, so read the file before sending "
             "the edit again.")


def shown_holds(holds: list[Hold], claim: Callable[[str], bool],
                call: Call | None = None) -> list[Shown]:
    """How `holds`, every hold one call or turn end meets, in the order the
    gates fire, are shown in one message (Ticket 095): each with its own text,
    whose harness wording is still in `wording` slots.

    `claim(purpose)` claims the turn's marker for `purpose` and returns True
    only for its first claim in the turn, so calls held in parallel, which
    see no result of each other, still share one full text. It must return
    True when it cannot claim, so the full text is then given. Each hold
    chooses its full or short text (`Hold.text`): an ask's first hold in the
    turn is full, its later ones short. The
    unseen-line advice (purpose `ADVICE`) is given in full once per turn;
    elsewhere it is one sentence that keeps the typed override. When one
    hold carries the advice, it stays in that hold. When several do
    (Ticket 111), each drops its own and the last hold's text ends with one
    clearing section (`wording.clearing_section`) for every line they ask for
    and every typed override, once each. Every other shared paragraph is
    given once per message: in the first hold that holds it, its later
    copies shortened.

    `call`: the held call, None at a turn's end. When a hold a line can clear
    holds it, the last hold's text ends with the carrier slot, after any
    clearing section, where the harness names a call that can carry the line
    if this call has no field for one. A held file edit's last text ends,
    before that slot, with `EDIT_HELD` on its own line.
    """

    line_clears = any(_full_advice(hold.instruction) for hold in holds)
    texts = [hold.text(claim) for hold in holds]
    advised = [i for i, text in enumerate(texts) if wording.ADVICE_RE.search(text)]
    if len(advised) > 1:
        texts = _with_clearing_section(texts, claim)
    else:
        for i in advised:
            found = _full_advice(texts[i])
            if found is not None and not claim(ADVICE):
                texts[i] = (texts[i][:found.start()] + short_advice(found[2], found[3])
                            + texts[i][found.end():])
    for full, again in _SHARED_TEXTS:
        texts = _once(texts, full, again)
    if call is not None and call.kind == events.FILE_WRITE and texts:
        texts[-1] += f"\n{EDIT_HELD}"
    if line_clears and call is not None and texts:
        texts[-1] += f"\n{wording.CARRIER}"
    return [Shown(hold.gate, hold.kind, text) for hold, text in zip(holds, texts)]


# A line-advice slot with the space before it, as a hold's sentence leads into it.
_ADVICE_IN_TEXT = re.compile(f" ?{wording.ADVICE_RE.pattern}")


def _with_clearing_section(texts: list[str], claim: Callable[[str], bool]) -> list[str]:
    """`texts` with every line-advice slot taken out, and the last ending, on
    a line of its own, with one clearing section for the lines and overrides
    they named: full when this claims the turn's advice, else short."""

    lines, way_outs = [], []

    def take(found: re.Match) -> str:
        lines.append(found[2])
        way_outs.append(found[3])
        return ""

    texts = [_ADVICE_IN_TEXT.sub(take, text) for text in texts]
    texts[-1] += "\n" + wording.clearing_section(lines, way_outs, full=claim(ADVICE))
    return texts


def _full_advice(text: str):
    """The first full unseen-line advice slot in `text`, as a match, or None."""

    return next((found for found in wording.ADVICE_RE.finditer(text)
                 if found[1] == wording.FULL_ADVICE), None)


def goated_skill_name(raw: str, namespaces: tuple[str, ...]) -> str | None:
    """Return the GOATED skill a loaded name refers to, or None for another skill.

    A bare name counts; `ns:name` counts only when `ns` is a configured GOATED
    namespace, so another plugin's `tdd` never satisfies `requires: tdd`.
    """

    namespace, _, name = raw.rpartition(":")
    if not namespace:
        return name or None
    return name if namespace in namespaces else None


def fold_turns(
    state: SessionState, turns: list[Turn], namespaces: tuple[str, ...] = (),
    folder: str | None = None,
    in_project: Callable[[str], bool] = lambda path: True,
) -> None:
    """Bring `state` up to date with turns read from the transcript, oldest first.

    Re-folding a turn already seen is harmless, so callers pass the last seen
    turn again to pick up anything written after they last looked. `folder`
    is the session's folder, which relative paths start from, or None when
    unknown. `in_project(path)` says whether a file a call read, by its
    path as written, is the project's, which only the count of distinct
    files toward orientation asks (`ORIENTATION_FILES`); by default, every
    file is.
    """

    if turns and turns[0].opens_session:
        # Every turn of the session is in hand, so whether it has a task is
        # known again even if saved state was missing or reset.
        state.task_unknown = False
    for turn in turns:
        if turn.is_compaction:
            # The compaction's `SessionStart` clears these too, but that reset
            # may never have landed (a hook that failed open, a refused save,
            # an adapter installed mid-session), so the boundary itself does.
            state.forget_context(turn.key)
        loads = [n for n in (goated_skill_name(raw, namespaces) for raw in turn.loads) if n]
        if ROUTER_SKILL in loads:
            state.router_loaded = True
        if turn.brief_route is not None:
            # The session that started this one routed the brief's work, as a
            # subagent's parent does; its required skills must still load here.
            # A prompt a person types is new work, so the exemption ends there.
            state.brief_routed = True
            state.briefed = True
        elif turn.typed:
            state.brief_routed = False
        if _brief_with_skills_line(turn):
            # A valid skills line marks a brief for the Review item too (round 7,
            # R2); without a route line it brings no briefed-session orientation.
            state.briefed = True
        route = _task_route_in(turn)
        if route is not None:
            state.task = Task(route=route, started_turn=turn.key)
            state.task_unknown = False
            state.brief_task = turn.brief_route is not None
            state.end_task(turn.key)  # A new task ends its lasting skips and points.
        elif turn.route is not None and state.task is None and not state.task_unknown:
            # Only `continue` lines, in a session with no task, such as one
            # started from another session: they start a task with no skills,
            # routed only by a brief or once its turn meets router-first
            # (`note_task_routed`).
            state.task = Task(route={"form": "continue"}, started_turn=turn.key,
                              routed=turn.brief_route is not None)
            state.brief_task = turn.brief_route is not None
        if state.router_loaded and state.task is not None and state.task.started_turn == turn.key:
            state.task.routed = True  # Its turn met router-first by the router's load.
        state.loads = _unique([*state.loads, *loads])
        state.reference_reads = _unique(
            [*state.reference_reads, *design_reads.reads_in(turn.calls)]
        )
        state.skill_reference_reads = _unique(
            [*state.skill_reference_reads, *reference_reads.reads_in(turn.calls)]
        )
        state.template_reads = _unique(
            [*state.template_reads, *contracts.templates_read(turn.calls)]
        )
        state.files_read = _unique(
            [*state.files_read, *_files_read(turn.calls, folder, whole=True)]
        )[:ORIENTATION_READS]
        if len(state.files_seen) < ORIENTATION_FILES:
            state.files_seen = _unique(
                [*state.files_seen, *_files_read(turn.calls, folder, whole=False,
                                                 in_project=in_project,
                                                 counted=state.files_seen)]
            )[:ORIENTATION_FILES]
        state.shell = last_shell([turn]) or state.shell
        state.last_turn = turn.key


def _brief_with_skills_line(turn: Turn) -> bool:
    """Whether `turn` opens with the brief that started the session (the event
    model's `brief` flag) and that brief has a valid `goated-skills:` line."""

    opener = turn.opener
    return (isinstance(opener, events.Prompt) and opener.starts_session
            and contracts.skills_line_problem(opener.text) is None)


def last_shell(turns: list[Turn]) -> str | None:
    """The shell (`events.POSIX` or `events.POWERSHELL`) of the last shell
    command in `turns`, oldest first, or None when they hold none."""

    return next((call.shell for turn in reversed(turns) for call in reversed(turn.calls)
                 if call.kind == events.SHELL_COMMAND), None)


def _files_read(calls, folder: str | None, whole: bool,
                in_project: Callable[[str], bool] = lambda path: True,
                counted: list[str] = ()) -> list[str]:
    """A digest of each file among `calls` that a finished file read read,
    or a finished, successful shell command printed
    (`shell.ShellCommand.file_prints`), in order: when `whole`, only those
    read or printed whole (`whole_prints`). Only orientation counts a shell
    print (Ticket 110): every other read a hold asks for is a file read.
    `in_project(path)` says whether a path, as the call wrote it, is the
    project's; a file it is not is left out. It is not asked of a file whose
    digest is in `counted`, already found the project's, so a turn folded
    again asks it only of files not yet counted.

    A relative path is taken from `folder`, the session's folder, when known,
    and two spellings of one path (`./`, `..`, and case and separators on
    Windows) give one digest.
    """

    def paths(call: Call) -> list[str]:
        if call.kind == events.SHELL_COMMAND:
            if not call.ok or call.background:  # A background command's result is no print.
                return []
            found = shell.analyze(call.command, call.shell)
            return found.whole_prints if whole else found.file_prints
        path = call.whole_read_path() if whole else call.read_path()
        return [path] if path else []

    def digest(path: str) -> str:
        return hashlib.sha256(os.path.normcase(os.path.normpath(
            os.path.join(folder, path) if folder else path)).encode("utf-8")).hexdigest()[:16]

    return [key for call in calls for path in paths(call)
            for key in [digest(path)] if key in counted or in_project(path)]


def _task_route_in(turn: Turn) -> dict | None:
    """Return the route of the task `turn` starts, or None.

    Every route line that is not `continue` starts a task; the last one is its
    route. A `continue` line keeps whatever task the turn already started.
    """

    return next((route for route in reversed(turn.routes) if route["form"] != "continue"), None)


def _turn_route(state: SessionState, turn: Turn) -> dict | None:
    """The route `turn` runs under, or None when it needs a route line.

    That is the turn's winning route line; failing one, a prompt from
    another session, in a session with a task, runs as
    `goated-route: continue`, since it is not a new task the router must
    judge (round 4's R5), and so does a person's prompt in a task an earlier
    turn started, since a follow-up mostly continues the task, as a notice
    at the prompt says (round 6's R2, decision T1). A task this turn's own
    judged call started, by a line the turns read do not show yet, is not
    one: that would carry a line to its sibling calls, which the carrier
    rule does not. Only the route carries over; overrides come only from a
    person's prompt, and skips, checks and change reads count within their
    turn. A route-like line that fails the grammar meant to route the turn,
    so it still needs a valid one and the hold quotes the bad line.
    """

    if turn.route is not None:
        return turn.route
    opener, task = turn.opener, state.task
    if (turn.malformed or not isinstance(opener, events.Prompt) or opener.starts_session
            or task is None):
        return None
    if opener.author == events.SESSION or (
            opener.author == events.PERSON and task.routed and task.started_turn != turn.key):
        return {"form": "continue"}
    return None


def note_task_routed(state: SessionState, turn: Turn, overrides: dict) -> None:
    """Mark the task `turn` started as routed when a person's override for
    the turn stands down routing, as folding the turn already does when the
    router loaded in it (`fold_turns`) and as a task a route line other than
    `continue` or a brief started already is. Only a routed task carries a
    person's later prompt as `continue` (`_turn_route`), so a bare
    `continue` line written without the router does not exempt the turns
    after it. `turn` is the current turn, already folded into `state`;
    `overrides` are the ones a person typed for it."""

    task = state.task
    if (task is not None and not task.routed and task.started_turn == turn.key
            and (overrides.get("routing") or ROUTER_SKILL in (overrides.get("skills") or ()))):
        task.routed = True


def writes_like_an_edit(call: Call) -> bool:
    """True for a file write, a spawn that starts work now, or a shell command
    that writes files. A spawn that only proposes work runs nothing."""

    if call.kind == events.FILE_WRITE:
        return True
    if call.kind == events.SPAWN:
        return call.starts_now
    if call.kind == events.SHELL_COMMAND:
        return shell.analyze(call.command, call.shell).writes
    return False


# What a hold adds for a posix command that redirects into nul (Ticket 104).
POSIX_NUL_NOTE = (
    "In a posix shell nul is no null device: this command writes a file named nul. "
    "To discard output there, redirect it into /dev/null."
)


def check_routing(
    state: SessionState,
    call: Call,
    turn: Turn,
    overrides: dict,
    orientation_installed: Callable[[], bool],
    writes_scratch: Callable[[], bool],
    context_docs: Callable[[], list[str]] = lambda: [],
) -> list[Hold]:
    """The routing holds that apply to this main-agent call, in order, as
    `_routing_holds` judges them. When the call is a posix command that
    redirects into nul (`shell.ShellCommand.redirects_into_nul`), the last
    hold's full and short texts end with `POSIX_NUL_NOTE`; for another
    command that looks like a plain read, with the part that made it none
    (`shell.ShellCommand.write_part`)."""

    holds = _routing_holds(state, call, turn, overrides, orientation_installed, writes_scratch,
                           context_docs)
    if holds and call.kind == events.SHELL_COMMAND:
        command = shell.analyze(call.command, call.shell)
        if command.redirects_into_nul:
            holds[-1] = holds[-1].with_note(POSIX_NUL_NOTE)
        elif command.write_part:
            holds[-1] = holds[-1].with_note(
                f"This command is no plain read because of {command.write_part}.")
    return holds


def _routing_holds(
    state: SessionState,
    call: Call,
    turn: Turn,
    overrides: dict,
    orientation_installed: Callable[[], bool],
    writes_scratch: Callable[[], bool],
    context_docs: Callable[[], list[str]] = lambda: [],
) -> list[Hold]:
    """Return the routing holds that apply to this main-agent call, in order.

    `router-first` and `route-line` are judged together (Ticket 095); only
    `pipeline` waits for the route, so it is judged once the router counts
    as loaded and the turn has a route line. `turn` is the current turn,
    already folded into `state`. `overrides` are the ones the user typed for
    this turn (see `overrides.parse_overrides`).
    Commands meet only router-first unless they write files, and a command
    made only of plain reads (`shell.ShellCommand.read_only`) passes it too.
    A spawn of a read-only agent passes pipeline, and a spawn that only
    proposes work passes every routing gate. `orientation_installed` says
    whether the orientation skill is installed; it is asked only when a
    briefed route would require that skill (`_brief_orientation`).
    `writes_scratch` says whether the call is a write whose every file is
    scratch (`actions.writes_only_scratch`); such a write passes every routing gate,
    and it is asked only of a call one of them would otherwise hold.
    `context_docs()` gives the project's context documents that exist
    (`CONTEXT_DOCS`), which the orientation hold names; it is asked only then.
    """

    if (call.kind not in ROUTED_KINDS or overrides.get("routing")
            or (call.kind == events.SPAWN and not call.starts_now)):
        return []
    user_skipped = set(overrides.get("skills") or ())
    routed = (state.router_loaded or state.brief_routed or ROUTER_SKILL in user_skipped
              or _continues_task(state, turn))
    holds = []
    if not routed:
        if call.kind == events.SHELL_COMMAND and shell.analyze(call.command, call.shell).read_only:
            return []
        if writes_scratch():
            return []
        holds.append(_router_first_hold(state))
    if not writes_like_an_edit(call) or writes_scratch():
        return holds
    route = _turn_route(state, turn)
    if route is None:
        return holds + [Hold("route-line", STRICT, *_route_line_texts(turn))]
    if route["form"] == "continue" and state.task is None:
        # Only when saved state was missing or reset: otherwise folding the
        # turn started a task.
        return holds + [Hold(
            "route-line",
            STRICT,
            "Write the route line the router selects for this task: "
            "`goated-route: continue` was written, but the adapter's saved state for "
            "this session was missing or reset, so it cannot tell which task continues.",
        )]
    task = state.task
    if not routed or task is None or task.route["form"] != "route":
        return holds  # `direct` exempts the task; pipeline waits for the router.
    if call.kind == events.SPAWN and call.read_only:
        return holds

    def unmet(skill: str) -> bool:
        return skill not in state.loads and skill not in user_skipped

    orient = (
        _brief_orientation(state, task)
        and unmet(ORIENTATION_SKILL)
        and len(state.files_read) < ORIENTATION_READS
        and len(state.files_seen) < ORIENTATION_FILES
        and orientation_installed()
    )
    route_skills = [
        skill for skill in task.route["requires"] if unmet(skill) and not (orient and skill == ORIENTATION_SKILL)
    ]
    if not route_skills and not orient:
        return []
    parts, missing = [], []
    if route_skills:
        names = ", ".join(f"`{skill}`" for skill in route_skills)
        parts.append(f"Load {names} with {SKILL_TOOL} and follow each: the current route "
                     "requires them before the first write or spawn.")
        missing.append(f"load {names}")
    if orient:
        # Backticked once, in the sentence a reader of hold texts takes for the
        # skill the brief added.
        how = ("Load the orientation skill too" if route_skills
               else f"Load the orientation skill with {SKILL_TOOL} and follow it")
        parts.append(
            f"{how}, or orient by finishing {READ} calls of three distinct files, each read "
            f"whole {NO_RANGE}, or reads of five distinct project files, whole or in part, "
            "such as the sources the brief names. A session started from a brief loads "
            f"`{ORIENTATION_SKILL}` before its first write or spawn when its route is "
            "standard or full, or orients so. A finished shell command that prints a file "
            "counts as a read of it: cat or Get-Content with no range and no pipe as a whole "
            "one, head, tail, sed -n, or a ranged Get-Content as one in part. A search "
            "such as grep never counts."
        )
        pointer = context_pointer(context_docs())
        if pointer:
            parts.append(pointer)
        # A reader of hold texts takes this sentence's opening for the skill the
        # brief added.
        missing.append(f"A session started from a brief loads `{ORIENTATION_SKILL}` or "
                       f"finishes {READ} calls of three distinct files, each whole, or of "
                       "five distinct project files, whole or in part, or shell commands "
                       "that print them")
    parts.append(
        "A load counts until the next compaction, in this turn or an earlier one"
        + (", and so does a read." if orient else ".")
    )
    if route_skills:
        parts.append(
            ("If a route skill" if orient else "If one")
            + " does not apply, write a corrected route line without it; the last route line wins."
        )
    drops_orientation = (
        "Only a corrected `goated-route: direct` line or a lightweight route line "
        "drops the orientation skill."
    )
    if orient:
        parts.append(drops_orientation)
    return [Hold(
        "pipeline",
        STRICT,
        " ".join(parts) + " " + unseen_line_advice("route line", "skip routing"),
        short_form("; ".join(missing), ("Or write a corrected route line without a skill "
                                        "that does not apply. " if route_skills else "")
                   + (drops_orientation + " " if orient else "")
                   + short_advice("route line", "skip routing")),
    )]


def _router_first_hold(state: SessionState) -> Hold:
    """The router-first hold. In the task the brief started, it also says that
    a `goated-route: continue` line meets it (`_continues_task`), with
    where that line can go so the check sees it."""

    text = (
        f"Load the `{ROUTER_SKILL}` skill with {SKILL_TOOL} before the first "
        "write, spawn, or command of a task, and follow the route it selects. "
        "Reads stay free, and so does a shell command made only of read-only "
        "commands, such as cat, grep, ls, git diff, or git branch, perhaps "
        "after a leading cd, with no output redirect but 2>/dev/null. If "
        "that skill is not installed, tell the user: they can type "
        "`skip routing` in their prompt to proceed without it."
    )
    short = (f"Load it with {SKILL_TOOL}, or tell the user they can type "
             "`skip routing` in their prompt.")
    if state.brief_task:
        continued = ("This task began from the brief that started the session: if "
                     "this prompt continues it, a `goated-route: continue` line "
                     "meets this hold without the router.")
        text += f" {continued} " + unseen_line_advice("route line", "skip routing")
        short = (f"Load it with {SKILL_TOOL}. {continued} "
                 + short_advice("route line", "skip routing"))
    return Hold("router-first", STRICT, text,
                short_form(f"the `{ROUTER_SKILL}` skill has not loaded", short))


def _continues_task(state: SessionState, turn: Turn) -> bool:
    """True when `turn` continues a task the router would only say
    `continue` to, so router-first is met without it. That is either:

    - a turn a person's prompt opened that runs as `goated-route: continue`,
      by its own line or none (`_turn_route`), in a routed task an earlier
      turn started (round 6's R2). The task survives a compaction, so this
      does too; its required skills are still asked for again by
      `pipeline`. A task started by a bare `continue` line with no router is
      not routed (`note_task_routed`), so it carries no later turn; or
    - a turn of any author whose own route line is `goated-route: continue`
      while the brief's task runs with no compaction since (round 5's R8,
      Ticket 117), which another session's message meets too.

    A turn whose route line starts a new task, or with no valid route line
    but one that fails the grammar, is neither, nor is a `continue` line
    that started the task itself. Only router-first reads this;
    briefed-session orientation stays with `brief_routed`, so continuing
    does not bring it back.
    """

    if state.brief_task and turn.route is not None and turn.route["form"] == "continue":
        return True
    route, task = _turn_route(state, turn), state.task
    return (turn.typed and route is not None and route["form"] == "continue"
            and task is not None and task.routed and task.started_turn != turn.key)


# A project's own context documents, as paths from its root, which the
# onboarding skills write: the context file, the context matrix, and the
# standards profile (round 6's R13). An adapter reports which exist.
CONTEXT_DOCS = ("CONTEXT.md", "docs/agents/context-matrix.md", "docs/agents/project-standards.md")


def context_pointer(docs: list[str]) -> str:
    """The sentence naming the project's context documents that exist,
    `docs`, for the orientation hold and the closeout note, or "" for none."""

    if not docs:
        return ""
    names = [f"`{doc}`" for doc in docs]
    listed = names[0] if len(names) == 1 else ", ".join(names[:-1]) + " and " + names[-1]
    return (f"This project's own context documents, for its terms, sources, and "
            f"standards: {listed}.")


CONTINUED_ROUTE_NOTICE = (
    "this prompt runs as `goated-route: continue` in the current task, so it needs "
    "no route line; if it asks for new work, write a new route line before the "
    "first write. This is a notice; nothing is held."
)


def continued_route_notice(state: SessionState) -> str | None:
    """The notice for a person's prompt about to open a turn in `state`'s
    session: `CONTINUED_ROUTE_NOTICE` when the session has a routed task, so
    the turn will run as `continue` until a route line says otherwise
    (`_turn_route`), else None. Saved state that was missing or reset knows
    no task, so it gives none. The caller brings `state` up to date with the
    turns before the prompt first."""

    task = state.task
    return CONTINUED_ROUTE_NOTICE if task is not None and task.routed else None


def _brief_orientation(state: SessionState, task: Task) -> bool:
    """True when the orientation skill joins the task's route because of its brief.

    The router selects orientation in a session started from a brief, and the
    spawn-brief template says that session loads it first (spec R4), on a
    `standard` or `full` route only, as the registry's `profile_eligibility`
    lists. It ends when the brief's route stops meeting router-first: at a
    typed prompt or a compaction. The caller also checks that it is installed.
    """

    return state.brief_routed and task.route.get("intensity") in ("standard", "full")


def _route_line_texts(turn: Turn) -> tuple[str, ShortForm]:
    """The route-line hold's full text and short form; both quote the turn's
    lines that do not match the grammar."""

    forms = ("`goated-route: direct`, `goated-route: <intensity> | requires: <skills>`, "
             "or `goated-route: continue`")
    text = (
        "End routing with a route line on its own line before the first write or spawn "
        f"after a user prompt, as the router's output contract defines: {forms} "
        "when this prompt continues the current task "
        "or, in a session with no task yet, work begun elsewhere. "
        + unseen_line_advice("route line", "skip routing")
    )
    short = f"Write one of {forms}. " + short_advice("route line", "skip routing")
    if turn.malformed:
        quoted = "; ".join(f"`{line}` ({markers.malformed_reason(line)})"
                           for line in turn.malformed)
        malformed = f" These lines in this turn do not match the grammar: {quoted}."
        text += malformed
        short += malformed
    return text, short_form("this turn has no route line", short)


def _unique(names) -> list[str]:
    seen: list[str] = []
    for name in names:
        if name and name not in seen:
            seen.append(name)
    return seen
