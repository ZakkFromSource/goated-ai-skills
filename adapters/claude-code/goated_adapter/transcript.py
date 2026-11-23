"""Read the recent turns of a Claude Code transcript, newest part only.

A Claude Code transcript is JSONL. A *turn* starts at a user prompt, or at a
compaction boundary, and runs to the end of the file or to the next such
entry. This module is the only place that knows the transcript's entry shapes
and which prompts a person typed; the rest of the adapter sees the event
model's turns (`events.Turn`), built with `translation`.

The file can be large, so it is read backward from the end in blocks and only
as far back as needed. Claude Code writes it asynchronously, so a reader asked
to judge a tool call first waits briefly for that call's own `tool_use` entry.
"""

from __future__ import annotations

import json
import os
import re
import time
from pathlib import Path
from typing import NamedTuple

from goated_core import events
from goated_core.events import (
    AgentFinished, Call, CallFinished, Compaction, Prompt, ReplyText, Result, SkillInvoked,
)
from goated_core.contracts import skills_line_problem
from goated_core.markers import parse_reply

from . import translation

BLOCK_SIZE = 256 * 1024
MAX_BYTES = 64 * 1024 * 1024
MAX_TURNS = 50
POLL_SECONDS = 0.03

# How Claude Code marks prompts it submits itself, by text prefix after any
# leading <system-reminder> blocks. Seen in desktop-app and `claude -p`
# transcripts (2.1.3xx).
#
# Never prompts: interrupt markers, wrappers around local slash-command and
# `!` shell input and output.
NOT_PROMPT_PREFIXES = (
    "[Request interrupted by user",
    "<local-command-stdout>",
    "<local-command-stderr>",
    "<local-command-caveat>",
    "<bash-input>",
    "<bash-stdout>",
    "<bash-stderr>",
)
# Results of background work: they continue the current turn.
CONTINUATION_PREFIXES = ("<task-notification>", "<side-sessions-event>")
# Requests written by another agent, another session, or the app: they start a
# turn, except the report of a subagent this session spawned, which continues
# it (see `_OwnReports` and `is_own_report`); nobody typed them here, so they
# never carry overrides. Claude Code
# 2.1.3xx opens a subagent's hand-back and another session's message alike with
# the first line below, then an `<agent-message>` or `<cross-session-message>`
# tag; the hook input carries no field saying where a prompt came from, so the
# first line is the prompt hook's only sign. The bare tags count too, in case
# a prompt arrives without that line.
#
# A session started from another session gets that session's brief as its
# first prompt, opening with one of `BRIEF_PREFIXES` (see `_brief_text`).
BRIEF_PREFIXES = (
    "Background (from the session that started this one)",
    "Task (from the session that started this one)",
)
MACHINE_PREFIXES = (
    "Another Claude session sent a message:",
    "<agent-message",
    "<cross-session-message",
    *BRIEF_PREFIXES,
)

TYPED = "typed"
MACHINE = "machine"
CONTINUATION = "continuation"
NOT_PROMPT = "not-prompt"

# After an API error the desktop app resubmits the turn with this exact text,
# after any reminder blocks (see `is_host_retry`).
HOST_RETRY_TEXT = "Try again"

REMINDER_RE = re.compile(r"\A\s*(?:<system-reminder>.*?</system-reminder>\s*)+", re.DOTALL)
ANY_REMINDER_RE = re.compile(r"<system-reminder>.*?</system-reminder>", re.DOTALL)
COMMAND_NAME_RE = re.compile(r"<command-name>/([^<\s]+)</command-name>")
SKILL_BODY_PREFIX = "Base directory for this skill:"
# A call this adapter held: Claude Code 2.1.3xx records the deny reason as
# `PreToolUse:<tool> hook error: <reason>`, and the reason opens with the hold line.
HOLD_RESULT_RE = re.compile(r"(?:PreToolUse:\S+ hook error: )?goated-hold: ")
# A result whose call never ran: a permission refusal, a hook's denial (this
# adapter's or another's), or an interruption, as Claude Code 2.1.3xx words it.
NOT_RUN_RE = re.compile(
    r"(?:The user doesn[’']t want to|Permission for this \w+ was denied|PreToolUse:\S+ hook error"
    r"|\[Request interrupted by user)"
)
# Text in a prompt the user did not type: `<system-reminder>` blocks, and text
# the user pasted (a pasted agent report may quote an override). Claude Code
# wraps a paste as `<pasted_content id="X">` ... `</pasted_content id="X">`, so
# a paste ends only at a close tag repeating its own id: a bare or other-id
# close tag inside it, or a nested paste, cannot end it early. An unclosed
# paste runs to the end of the prompt.
NOT_TYPED_RE = re.compile(
    r"<system-reminder>.*?</system-reminder>"
    r'|<pasted_content\b[^>]*?\bid="([^"]*)"[^>]*>(.*?)(?:</pasted_content\s+id="\1"\s*>|\Z)',
    re.DOTALL,
)


def typed_prompt(text: str) -> Prompt:
    """A prompt a person typed, as the event model holds it: each reminder
    block and paste becomes a space in its text, and each paste's body goes
    to `pasted`."""

    pasted = tuple(match.group(2) for match in NOT_TYPED_RE.finditer(text) if match.group(2) is not None)
    return Prompt(events.PERSON, NOT_TYPED_RE.sub(" ", text), pasted)


def prompt_text_kind(text: str) -> str:
    """Classify prompt text alone: typed, machine, continuation, or not-prompt.

    Hooks that see only the prompt text use this; the transcript reader also
    uses the entry's structured fields, which are more reliable.
    """

    body = REMINDER_RE.sub("", text, count=1).lstrip()
    if body.startswith(NOT_PROMPT_PREFIXES):
        return NOT_PROMPT
    if body.startswith(CONTINUATION_PREFIXES):
        return CONTINUATION
    if body.startswith(MACHINE_PREFIXES):
        return MACHINE
    return TYPED


def is_host_retry(text: str) -> bool:
    """True when prompt text, after any leading reminders, is the app's retry.

    Text alone cannot show who wrote it, so the transcript reader also checks
    that the entry is host-written (see `_opener_kind`). The text carries no
    override, so the prompt hook leaves the turn's overrides in place.
    """

    return REMINDER_RE.sub("", text, count=1).strip() == HOST_RETRY_TEXT


class TranscriptUnreadable(Exception):
    """The transcript cannot be read well enough to judge the current call."""


class Reading(NamedTuple):
    """What `read_recent_turns` read: the turns, oldest first, ending with the
    current turn, and the id of the prompt that opened the current turn, None
    when it has none."""

    turns: list[events.Turn]
    prompt_id: str | None


class _Chunk:
    """One turn as read from the transcript, before it is built into an
    `events.Turn`: its key, opener, and entries in the event model's terms,
    the id of its opening prompt, and the ids of every prompt it holds. A
    turn opened by a brief from the session that started this one keeps the
    brief's text (`_brief_text`) in `brief`; `starts_session` is set once
    reading shows that brief opened the session, so its route counts."""

    __slots__ = ("key", "opener", "entries", "prompt_id", "prompt_ids", "brief",
                 "starts_session")

    def __init__(self, key: str) -> None:
        self.key = key
        self.opener: Prompt | Compaction | None = None
        self.entries: list = []
        self.prompt_id: str | None = None
        self.prompt_ids: set[str] = set()
        self.brief: str | None = None
        self.starts_session = False

    def turn(self, *, opens_session: bool, pending: Call | None = None) -> events.Turn:
        opener = self.opener
        if self.starts_session and self.brief is not None:
            opener = Prompt(events.SESSION, self.brief, starts_session=True)
        return events.Turn(self.key, opener, self.entries, opens_session=opens_session,
                           pending=pending)


def read_recent_turns(
    path: str | os.PathLike,
    *,
    since_key: str | None,
    prompt_id: str | None = None,
    wait_seconds: float = 0.0,
    sidechain: bool = False,
    current_call: Call | None = None,
) -> Reading:
    """Return recent turns, oldest first, ending with the current turn.

    Turns are collected back to and including the turn keyed `since_key`, the
    last turn the caller has already seen, so that anything written after the
    caller last looked is included. Without `since_key`, or when it is not
    found within the read limits, only the turns read so far are returned.
    Without `since_key`, reading goes on past the current turn only far enough
    to tell whether an earlier turn exists (see `events.Turn.opens_session`).
    Reading never crosses a compaction boundary. It raises
    `TranscriptUnreadable` only when the current turn itself cannot be read.

    When `prompt_id` is given, the current turn must hold an entry of that
    prompt: the reader re-reads for up to `wait_seconds` while the transcript
    catches up, then raises `TranscriptUnreadable`. It never waits for the
    call being judged. In an interactive session Claude Code records the
    assistant message holding that call, with any text and sibling calls in
    it, only after PreToolUse returns, so callers take the call from the hook
    input instead. `current_call` is that call: the route and skip lines it
    carries count in the current turn, once even if the transcript already
    shows it.

    `sidechain` reads a subagent's own transcript, where every entry is a
    sidechain entry and every prompt was written by the parent agent, so none
    is typed.
    """

    deadline = time.monotonic() + max(wait_seconds, 0.0)
    while True:
        chunks, opens_session = _read_turns_once(Path(path), since_key, sidechain)
        current = chunks[-1]
        if (prompt_id is None or isinstance(current.opener, Compaction)
                or prompt_id in current.prompt_ids):
            turns = [chunk.turn(opens_session=opens_session and index == 0,
                                pending=current_call if chunk is current else None)
                     for index, chunk in enumerate(chunks)]
            return Reading(turns, current.prompt_id)
        if time.monotonic() >= deadline:
            raise TranscriptUnreadable(
                "the transcript does not yet show the prompt this call belongs to"
            )
        time.sleep(POLL_SECONDS)


def _read_turns_once(path: Path, since_key: str | None,
                     sidechain: bool) -> tuple[list[_Chunk], bool]:
    """The turns read, oldest first, and whether the oldest opens the session."""

    # Each chunk is one turn's entries, oldest first, with its opener kind;
    # chunks are collected newest first and built into turns at the end, once
    # every own-report candidate is settled (see `_OwnReports`).
    chunks: list[tuple[str | None, list[dict]]] = []
    pending: list[dict] = []
    reports = _OwnReports()
    # Set once the current turn is read without `since_key`, or once a turn
    # opened by a brief with a route line ends the read: the reader then
    # only looks for an earlier turn's opener, collecting nothing.
    probing = False
    # Set once the turns wanted are read: the reader then only looks for the
    # spawns that own-report candidates name.
    settling = False
    # The oldest chunk read so far when its opener is such a brief: its route
    # counts only if no earlier turn exists.
    brief_chunk: list[dict] | None = None
    # An opener was found before the oldest chunk while probing.
    earlier_opener = False
    reached_start = False
    try:
        for line in _lines_backward(path):
            if line is None:
                # Read limit reached. Older unseen turns are given up, as if
                # `since_key` were not found; the current turn must be whole.
                if not chunks:
                    raise TranscriptUnreadable(
                        "the current turn is too large to read quickly"
                    )
                break
            try:
                entry = json.loads(line)
            except ValueError:
                # The last line may still be half-written; older bad lines are
                # skipped rather than trusted.
                continue
            if not isinstance(entry, dict):
                continue
            if not sidechain:
                reports.see(entry)
            kind = _opener_kind(entry, sidechain)
            if settling:
                if kind == "compaction" or reports.settled:
                    break
                continue
            if kind == MACHINE and not sidechain and reports.hold(entry, probing):
                kind = None
            is_opener = kind in (TYPED, MACHINE, "compaction")
            if probing:
                if is_opener:
                    earlier_opener = True
                    settling = True
                    if reports.settled:
                        break
                continue
            pending.append(entry)
            if not is_opener:
                continue
            entries = list(reversed(pending))
            chunks.append((kind, entries))
            pending = []
            # A brief marks itself by a route line or, for the Review item
            # only, a valid skills line (round 7, R2).
            brief = (kind == MACHINE and not sidechain and (text := _brief_text(entries[0]))
                     is not None and (parse_reply(text).route is not None
                                      or skills_line_problem(text) is None))
            brief_chunk = entries if brief else None
            if kind == "compaction":
                break
            done = (str(entries[0].get("uuid") or "transcript-start") == since_key
                    or len(chunks) >= MAX_TURNS)
            if done and brief_chunk is None:
                settling = True
                if reports.settled:
                    break
            elif done or since_key is None:
                probing = True
        else:
            reached_start = not settling
    except OSError as exc:
        raise TranscriptUnreadable(f"the transcript could not be read ({exc.strerror})")

    if reached_start and not probing and (pending or not chunks):
        # Without `since_key`, entries before the first prompt are
        # session-start attachments and are dropped; otherwise they (or a
        # transcript with no prompt yet) form a turn of their own.
        chunks.append((None, list(reversed(pending))))
    turns: list[_Chunk] = []
    brief_turn: _Chunk | None = None
    for kind, entries in reversed(chunks):
        for index, (part_kind, part) in enumerate(reports.split(kind, entries)):
            turns.append(_build_turn(part, part_kind, sidechain))
            if index == 0 and entries is brief_chunk:
                brief_turn = turns[-1]
    first = reached_start and not earlier_opener and not reports.opened_earlier_turn
    if first and brief_turn is not None:
        # No prompt opened a turn before the brief, so its route counts.
        brief_turn.starts_session = True
    return turns, first


def _lines_backward(path: Path):
    """Yield complete lines from the end of the file toward the start.

    Yields None once `MAX_BYTES` have been read, then stops.
    """

    with path.open("rb") as handle:
        handle.seek(0, os.SEEK_END)
        position = handle.tell()
        scanned = 0
        tail = b""
        while position > 0:
            if scanned >= MAX_BYTES:
                yield None
                return
            size = min(BLOCK_SIZE, position)
            position -= size
            handle.seek(position)
            block = handle.read(size) + tail
            scanned += size
            parts = block.split(b"\n")
            tail = parts[0]
            for part in reversed(parts[1:]):
                if part.strip():
                    yield part.decode("utf-8", errors="replace")
        if tail.strip():
            yield tail.decode("utf-8", errors="replace")


def _opener_kind(entry: dict, sidechain: bool = False) -> str | None:
    """Return how an entry relates to turns: an opener kind, or None."""

    if entry.get("type") == "system" and entry.get("subtype") == "compact_boundary":
        return "compaction"
    if entry.get("type") != "user":
        return None
    if entry.get("isCompactSummary"):
        return None
    if bool(entry.get("isSidechain")) != sidechain:
        return None
    if (entry.get("origin") or {}).get("kind") == "peer" or entry.get("turnOrigin") == "peer":
        # A subagent's hand-back or another session's message. Claude Code
        # records it `isMeta` but starts a new turn with it, as the adapter
        # does: whatever its text says, nobody typed it here. The reader
        # still folds the report of a subagent this session spawned into the
        # current turn (see `_OwnReports`).
        return MACHINE
    if entry.get("isMeta"):
        return None
    text = _prompt_text(entry)
    if text is None:
        return None
    by_text = prompt_text_kind(text)
    if sidechain:
        # The parent agent wrote every prompt a subagent receives.
        return MACHINE if by_text in (TYPED, MACHINE) else by_text
    if by_text in (NOT_PROMPT, CONTINUATION):
        return by_text
    origin = (entry.get("origin") or {}).get("kind")
    turn_origin = entry.get("turnOrigin")
    if turn_origin == "host_synthetic" and "origin" not in entry and is_host_retry(text):
        # The app retrying the turn after an API error: the turn, its route,
        # and its overrides go on. A person's "Try again" has a `human` origin.
        return CONTINUATION
    if origin == "task-notification" or turn_origin == "task_notification":
        return CONTINUATION
    if origin is not None:
        # The desktop app marks typed prompts `human`; any other origin is the
        # app or a scheduler acting, so it opens a turn but is not typed.
        return TYPED if origin == "human" and by_text == TYPED else MACHINE
    if turn_origin not in (None, "human", "sdk"):
        # Seen: `host_synthetic` (desktop-app prompts). Any origin other than a
        # person or the SDK caller is not typed.
        return MACHINE
    return by_text


def _prompt_text(entry: dict) -> str | None:
    content = (entry.get("message") or {}).get("content")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        if any(isinstance(b, dict) and b.get("type") == "tool_result" for b in content):
            return None
        return " ".join(
            b.get("text", "") for b in content if isinstance(b, dict) and b.get("type") == "text"
        )
    return None


def _build_turn(entries: list[dict], kind: str | None, sidechain: bool = False) -> _Chunk:
    """One turn's entries, given oldest first, opener included, in the event
    model's terms.

    A call's entry stays where its tool_use is and takes its result when the
    result arrives, which a `CallFinished` entry marks. A tool_use id
    recorded twice keeps both entries; the result goes to the newer.
    """

    opener = entries[0] if kind else None
    chunk = _Chunk(str((opener or {}).get("uuid") or "transcript-start"))
    if opener is not None and opener.get("promptId"):
        chunk.prompt_id = str(opener["promptId"])
    # Every prompt the turn holds, including background results that continue
    # it; Claude Code marks user entries only.
    chunk.prompt_ids = {
        str(e["promptId"]) for e in entries if e.get("type") == "user" and e.get("promptId")
    }
    invoked = None
    if kind == "compaction":
        chunk.opener = Compaction()
    elif opener is not None:
        text = _prompt_text(opener) or ""
        match = COMMAND_NAME_RE.search(text)
        invoked = match.group(1) if match else None
        if kind == TYPED:
            chunk.opener = typed_prompt(text)
        else:
            chunk.opener = Prompt(_machine_author(opener, text, sidechain),
                                  ANY_REMINDER_RE.sub("\n", text))
            if not sidechain:
                chunk.brief = _brief_text(opener)

    made: dict[str, Call] = {}  # Calls with no result yet, by tool_use id.
    model = chunk.entries
    for entry in entries[1:] if opener is not None else entries:
        if bool(entry.get("isSidechain")) == sidechain:
            model += [AgentFinished(agent) for agent in sorted(_finished_agents(entry))]
        content = (entry.get("message") or {}).get("content")
        if not isinstance(content, list) or bool(entry.get("isSidechain")) != sidechain:
            continue
        if entry.get("type") == "assistant":
            for block in content:
                if not isinstance(block, dict):
                    continue
                if block.get("type") == "text":
                    model.append(ReplyText(str(block.get("text", ""))))
                elif block.get("type") == "tool_use":
                    tool_id = str(block.get("id", ""))
                    made[tool_id] = translation.call_of(
                        str(block.get("name", "")), block.get("input"), tool_id)
                    model.append(made[tool_id])
        elif entry.get("type") == "user":
            if invoked and entry.get("isMeta") and _starts_skill_body(content):
                # The prompt invoked a skill as `/<skill>`; Claude Code adds
                # its body as a meta entry, which proves the load.
                model.append(SkillInvoked(invoked))
                continue
            for block in content:
                if not isinstance(block, dict) or block.get("type") != "tool_result":
                    continue
                tool_id = str(block.get("tool_use_id", ""))
                call = made.pop(tool_id, None)
                if call is None:
                    continue
                model[model.index(call)] = call.finished(_result(entry, block))
                model.append(CallFinished(tool_id))
    return chunk


def _result(entry: dict, block: dict) -> Result:
    """A tool result's outcome. A spawn's result names its agent in
    `toolUseResult.agentId`, and says the agent started in the background with
    `status: async_launched` or `isAsync`."""

    found = entry.get("toolUseResult")
    found = found if isinstance(found, dict) else {}
    agent = found.get("agentId")
    text = _result_text(block)
    failed = bool(block.get("is_error"))
    return Result(
        ok=not failed, held=failed and bool(HOLD_RESULT_RE.match(text)), output=text,
        agent_id=agent if isinstance(agent, str) else None,
        background=found.get("status") == "async_launched" or found.get("isAsync") is True,
        ran=not NOT_RUN_RE.match(text),
    )


# A background agent's completion, in the two shapes Claude Code 2.1.3xx
# records: a `<task-notification>` whose task id is the agent's id, with a
# `completed` status, and a subagent's `<agent-message from="<id>">` hand-back.
# Each arrives as a user entry or as a `queued_command` attachment.
FINISHED_TASK_RE = re.compile(
    r"<task-notification>\s*<task-id>([^<\s]+)</task-id>(?:(?!</task-notification>).)*?"
    r"<status>completed</status>", re.DOTALL)
HAND_BACK_RE = re.compile(r'<agent-message from="([^"\s]+)">')


def _finished_agents(entry: dict) -> set[str]:
    """The ids of the background agents whose completion this entry carries."""

    attachment = entry.get("attachment")
    if isinstance(attachment, dict):
        text = attachment.get("prompt") if attachment.get("type") == "queued_command" else None
    elif entry.get("type") == "user":
        content = (entry.get("message") or {}).get("content")
        text = content if isinstance(content, str) else " ".join(
            str(b.get("text", "")) for b in content or ()
            if isinstance(b, dict) and b.get("type") == "text")
    else:
        text = None
    if not isinstance(text, str) or "<" not in text:
        return set()
    return set(FINISHED_TASK_RE.findall(text)) | set(HAND_BACK_RE.findall(text))


# A subagent's final report delivered as a prompt, as Claude Code 2.1.3xx
# records it: after any reminders, an optional fixed first line, then the
# report's tag naming the agent.
REPORT_RE = re.compile(
    r'\A(?:Another Claude session sent a message:[ \t]*\r?\n\s*)?<agent-message from="([^"\s]+)">'
)
# Another session's or agent's message, as Claude Code 2.1.3xx wraps it; the
# group is the sender its tag names (see `_machine_author`).
PEER_MESSAGE_RE = re.compile(
    r'\A(?:Another Claude session sent a message:[ \t]*\r?\n\s*)?'
    r'<(?:cross-session-message|agent-message) from="([^"\s]+)"[^>]*>'
)


def is_own_report(path: str | os.PathLike, text: str) -> bool:
    """True when prompt text is the report of a subagent this session spawned.

    For the prompt hook, which runs before the prompt is recorded: the
    transcript must already show a spawn result naming the report's agent
    (see `_spawned_agent`), after the last compaction and within the read
    limit. Any doubt, an unreadable transcript included, answers False, so the
    prompt opens a turn as any other machine-written prompt does.
    """

    sender = _report_sender(text)
    if sender is None:
        return False
    try:
        for line in _lines_backward(Path(path)):
            if line is None:
                return False
            try:
                entry = json.loads(line)
            except ValueError:
                continue
            if not isinstance(entry, dict):
                continue
            if _spawned_agent(entry) == sender:
                return True
            if _opener_kind(entry) == "compaction":
                return False
    except OSError:
        return False
    return False


def _machine_author(entry: dict, text: str, sidechain: bool) -> str:
    """Who wrote `entry`, a prompt nobody typed here, as an event-model author.

    `session` only where another session or agent surely sent it: every
    prompt of a subagent's own transcript (its parent's), and a `peer` prompt
    whose `<cross-session-message>` or `<agent-message>` tag names the sender
    its `origin.from` names. The brief that starts a session becomes
    `session` once reading shows it opened the session (`_Chunk.turn`).
    `host` for prompts the desktop app or its scheduler wrote, and `unknown`
    for anything else, such as a peer prompt in a wrapper not known here. The
    core lets only `session` prompts continue a task's route (Ticket 102).
    """

    if sidechain:
        return events.SESSION
    origin = entry.get("origin") if isinstance(entry.get("origin"), dict) else {}
    kind = origin.get("kind")
    if kind == "peer" or entry.get("turnOrigin") == "peer":
        match = PEER_MESSAGE_RE.match(REMINDER_RE.sub("", text, count=1).lstrip())
        sender = origin.get("from")
        return events.SESSION if match and sender == match.group(1) else events.UNKNOWN
    if kind == "scheduled" or (not origin and entry.get("turnOrigin") == "host_synthetic"):
        return events.HOST
    return events.UNKNOWN


def _report_sender(text: str) -> str | None:
    """The agent id a subagent's report names, from prompt text alone, or None."""

    match = REPORT_RE.match(REMINDER_RE.sub("", text, count=1).lstrip())
    return match.group(1) if match else None


def _spawned_agent(entry: dict) -> str | None:
    """The agent id a main-transcript spawn result records, or None.

    Claude Code records it as `toolUseResult.agentId` on the result of an
    `Agent` (or `Task`) call, foreground or background alike.
    """

    if entry.get("type") != "user" or entry.get("isSidechain"):
        return None
    result = entry.get("toolUseResult")
    agent = result.get("agentId") if isinstance(result, dict) else None
    return agent if isinstance(agent, str) and agent else None


class _OwnReports:
    """Ties reports delivered as prompts to the spawns of this session.

    The reader goes backward, so it meets a report before the spawn that
    started its agent. A report candidate, a peer prompt whose `origin.from`
    is the agent its `<agent-message>` tag names, is held as part of the turn
    until reading meets an older spawn result naming that agent. One left
    untied, because reading stopped at a compaction, the read limit, or the
    start of the file first, opens a turn after all (`split`).
    """

    def __init__(self) -> None:
        # Agent id -> uuids of the reports naming it, not yet tied to a spawn.
        self._waiting: dict[str, list[str]] = {}
        # Reports held while the reader only looked for an earlier turn.
        self._probed: set[str] = set()

    @property
    def settled(self) -> bool:
        return not self._waiting

    @property
    def opened_earlier_turn(self) -> bool:
        """An untied report was read while only looking for an earlier turn."""

        return any(uuid in self._probed for uuids in self._waiting.values() for uuid in uuids)

    def hold(self, entry: dict, probing: bool) -> bool:
        """Hold `entry` as a report candidate; False when it is not one."""

        origin = entry.get("origin")
        sender = origin.get("from") if isinstance(origin, dict) else None
        uuid = entry.get("uuid")
        if not isinstance(sender, str) or not isinstance(uuid, str):
            return False
        if _report_sender(_prompt_text(entry) or "") != sender:
            return False
        self._waiting.setdefault(sender, []).append(uuid)
        if probing:
            self._probed.add(uuid)
        return True

    def see(self, entry: dict) -> None:
        """Tie every waiting report to the spawn `entry` records, if any."""

        agent = _spawned_agent(entry)
        if agent is not None:
            self._waiting.pop(agent, None)

    def split(self, kind: str | None, entries: list[dict]):
        """Yield `(kind, entries)` for each turn in one chunk, oldest first.

        An untied report starts a turn of its own, written by a machine.
        """

        untied = {uuid for uuids in self._waiting.values() for uuid in uuids}
        start = 0
        for index, entry in enumerate(entries):
            if entry.get("uuid") not in untied:
                continue
            if index:
                yield kind, entries[start:index]
            # Only the start-of-file chunk, which has no opener, can begin
            # with one.
            kind, start = MACHINE, index
        yield kind, entries[start:]


def _brief_text(opener: dict) -> str | None:
    """The text of a brief from the session that started this one, or None.

    Desktop-app builds seen in November 2026 submit that brief as the new
    session's first prompt: one or more `<system-reminder>` blocks, then text
    opening with one of `BRIEF_PREFIXES`, recorded with
    `turnOrigin: host_synthetic`, no `origin`, and no `isMeta`. Older builds
    recorded `turnOrigin: sdk`, which is not recognized. A typed prompt carries
    `origin.kind: human`, and another session's message is `isMeta` with a
    `peer` origin, so neither matches. The route is the last valid route line
    on its own line anywhere in the brief; lines inside reminder blocks, which
    quote instruction files, never count. The caller confirms the prompt was
    the session's first.
    """

    if opener.get("turnOrigin") != "host_synthetic" or "origin" in opener:
        return None
    if opener.get("isMeta"):
        return None
    body = REMINDER_RE.sub("", _prompt_text(opener) or "", count=1).lstrip()
    if not body.startswith(BRIEF_PREFIXES):
        return None
    return ANY_REMINDER_RE.sub("\n", body)


def _starts_skill_body(content: list) -> bool:
    first = content[0] if content else None
    return isinstance(first, dict) and str(first.get("text", "")).startswith(SKILL_BODY_PREFIX)


def _result_text(block: dict) -> str:
    """A tool result's text, whether recorded as a string or as text blocks."""

    content = block.get("content")
    if isinstance(content, list):
        return "".join(
            str(part.get("text", "")) for part in content if isinstance(part, dict)
        )
    return str(content or "")
