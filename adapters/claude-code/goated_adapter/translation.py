"""Claude Code's tool calls in the event model's terms, and the rules' text in Claude Code's words.

The rules judge calls by kind (`events`) and write hold texts with slots for
harness wording (`wording`). This module, with the transcript reader and the
hook entry point, is the one place that knows Claude Code: which tool makes
which kind of call, which input fields carry what, and how a hold names
Claude Code's tools.
"""

from __future__ import annotations

import re

from goated_core import events, shell, wording
from goated_core.events import Call, Edit

# File edit tools, each with the input field that names its file.
FILE_WRITE_TOOLS = {"Edit": "file_path", "Write": "file_path", "MultiEdit": "file_path",
                    "NotebookEdit": "notebook_path"}
# Shell tools, each with the shell it runs in.
COMMAND_TOOLS = {"Bash": events.POSIX, "PowerShell": events.POWERSHELL}
START_SESSION = "mcp__ccd_session__start_session"
# Tools that start another agent, each with the input field that carries the
# brief. A call without a brief (an offer card, or starting a saved proposal)
# hands over no text, so it is not held.
SPAWN_BRIEF_FIELDS = {
    "Agent": "prompt",
    "Task": "prompt",  # The spawn tool's name in older Claude Code versions.
    START_SESSION: "prompt",
    "mcp__ccd_session__hand_off_to_session": "remaining_plan",
}
# The spawn tools that start a subagent; the others start a side session.
SUBAGENT_TOOLS = frozenset({"Agent", "Task"})
# A `start_session` call with one of these `initiation` values, and no
# `proposal_id` (the field that starts a saved proposal), only shows a card:
# nothing runs until the user starts it (spec R7). Any other value, or none,
# starts a session.
CARD_INITIATIONS = frozenset({"offer", "own_initiative"})
# Subagent types Claude Code ships with no edit, write, or shell tool:
# `claude-code-guide` has Glob, Grep, Read, WebFetch, and WebSearch. `Explore`
# and `Plan` are not here: they keep Bash and PowerShell. The name is
# trusted: a project or user agent file of the same name replaces the
# built-in. Names match exactly.
READ_ONLY_SUBAGENTS = frozenset({"claude-code-guide"})
# MCP tools that open a pull or merge request, such as a GitHub server's.
PR_TOOL_RE = re.compile(r"^mcp__.+__create_(?:pull|merge)_request$")
# MCP tools that record a commit, such as a GitHub server's file tools or a git
# server's commit tool; each carries its message in `message`.
COMMIT_TOOL_RE = re.compile(
    r"^mcp__.+__(?:push_files|create_or_update_file|delete_file|git_commit|create_commit"
    r"|commit_changes|commit)$"
)
# The one input field of each built-in tool that may carry route and skip
# lines: a field that describes the call rather than holds its payload. Other
# tools, MCP tools included, carry none, since their `description` is often
# the payload, such as an issue or merge-request body. The skill-usage mod
# keeps the same table (`LINE_FIELDS` in its `hooks/classify.ts`).
LINE_FIELDS = {
    "Bash": "description",
    "PowerShell": "description",
    "Agent": "description",
    "Task": "description",
    "Skill": "args",
}
# The fields of a Read call's input that ask for part of a file.
READ_RANGE_FIELDS = frozenset({"limit", "offset", "pages"})


def is_judged(tool_name: str) -> bool:
    """True for a tool some gate may hold before it runs (the hook matcher must cover these)."""

    return (tool_name in FILE_WRITE_TOOLS or tool_name in COMMAND_TOOLS
            or tool_name in SPAWN_BRIEF_FIELDS or bool(PR_TOOL_RE.match(tool_name))
            or bool(COMMIT_TOOL_RE.match(tool_name)))


def call_of(tool_name: str, tool_input: object, tool_id: str = "") -> Call:
    """The event model's call for one Claude Code tool call."""

    tool_input = tool_input if isinstance(tool_input, dict) else {}
    line = tool_input.get(LINE_FIELDS.get(tool_name, ""))
    common = {"id": tool_id, "line_text": line if isinstance(line, str) else "",
              "action": _action(tool_name)}
    if tool_name in FILE_WRITE_TOOLS:
        # Claude Code lets an Edit with empty old text, and no `edits` list,
        # make the file it names.
        creates = ("content" not in tool_input and tool_input.get("old_string") == ""
                   and "edits" not in tool_input)
        return Call(events.FILE_WRITE, path=_text(tool_input.get(FILE_WRITE_TOOLS[tool_name])),
                    whole_file="content" in tool_input, creates=creates,
                    edits=_edits(tool_name, tool_input), **common)
    if tool_name in COMMAND_TOOLS:
        return Call(events.SHELL_COMMAND, command=_text(tool_input.get("command")),
                    shell=COMMAND_TOOLS[tool_name],
                    background=tool_input.get("run_in_background") is True, **common)
    if tool_name in SPAWN_BRIEF_FIELDS:
        return Call(events.SPAWN, brief=_text(tool_input.get(SPAWN_BRIEF_FIELDS[tool_name])),
                    starts_now=not _shows_a_card(tool_name, tool_input),
                    read_only=(tool_name in SUBAGENT_TOOLS
                               and tool_input.get("subagent_type") in READ_ONLY_SUBAGENTS),
                    separate=tool_name not in SUBAGENT_TOOLS, **common)
    if tool_name == "Read":
        return Call(events.FILE_READ, path=_text(tool_input.get("file_path")),
                    whole=not READ_RANGE_FIELDS & tool_input.keys(), **common)
    if tool_name == "Skill" and (skill := skill_name(tool_input.get("skill"))):
        return Call(events.SKILL_LOAD, skill=skill, **common)
    if COMMIT_TOOL_RE.match(tool_name):
        return Call(events.COMMIT, message=_known(tool_input.get("message")), **common)
    if PR_TOOL_RE.match(tool_name):
        owner, repo = _named(tool_input, "owner"), _named(tool_input, "repo")
        repository = f"{owner}/{repo}" if owner and repo else None
        return Call(events.PULL_REQUEST, base=_named(tool_input, "base", "target_branch"),
                    head=_named(tool_input, "head", "source_branch"),
                    repository=(repository if repository and events.REPOSITORY_RE.match(repository)
                                else None), **common)
    return Call(events.OTHER, **common)


def _action(tool_name: str) -> str:
    """The call's `action` key, the tool that makes it, so calls of one kind
    by different tools count apart: a spawn tool's as `spawn:<tool>`, any
    other's as `tool:<tool>`, as sessions saved before the event model hold
    them. The rules key file writes, reads, and commands themselves."""

    return ("spawn:" if tool_name in SPAWN_BRIEF_FIELDS else "tool:") + tool_name


def upgrade_state(data: object) -> object:
    """Saved session state in the core's words, for state an earlier adapter
    saved in Claude Code's: the override record keyed by `prompt_id`, where
    the core keys it by `prompt`, and the last shell saved as its tool name
    ("Bash", "PowerShell") rather than its shell kind. Anything else is
    returned as it came, for the core to check."""

    if not isinstance(data, dict):
        return data
    overrides = data.get("overrides")
    if isinstance(overrides, dict) and "prompt_id" in overrides and "prompt" not in overrides:
        data["overrides"] = {("prompt" if key == "prompt_id" else key): value
                             for key, value in overrides.items()}
    shell_kind = data.get("shell")
    if isinstance(shell_kind, str):
        data["shell"] = COMMAND_TOOLS.get(shell_kind, shell_kind)
    return data


def skill_name(value: object) -> str:
    """Normalize a Skill-tool argument such as `/tdd args` to `tdd`, keeping any
    `namespace:` prefix for the gates to judge."""

    if not isinstance(value, str):
        return ""
    words = value.strip().lstrip("/").split()
    return words[0] if words else ""


def shell_tool(kind: str | None) -> str | None:
    """The Claude Code tool of a shell kind, or None for None."""

    return next((tool for tool, shell_kind in COMMAND_TOOLS.items() if shell_kind == kind), None)


def _edits(tool_name: str, tool_input: dict) -> tuple[Edit, ...]:
    """A file edit tool's changes; text that is not a string is unknown (None).

    An input with `content` writes the whole file: its one edit adds the
    content, replacing whatever the file held. A notebook edit does not say
    which cell text it replaces, and a delete adds none. An edit's old and
    new strings come first, then each entry of `edits`, an entry that is not
    an edit being wholly unknown. An input that names no text at all is one
    unknown edit; an empty `edits` list alone is no edit.
    """

    if "content" in tool_input:
        return (Edit(None, _known(tool_input.get("content"))),)
    if tool_name == "NotebookEdit":
        return (Edit(None, _known(tool_input.get("new_source"))),)
    edits = []
    if "old_string" in tool_input or "new_string" in tool_input:
        edits.append(Edit(_known(tool_input.get("old_string")),
                          _known(tool_input.get("new_string"))))
    listed = tool_input.get("edits")
    if isinstance(listed, list):
        edits += [Edit(_known(e.get("old_string")), _known(e.get("new_string")))
                  if isinstance(e, dict) else Edit(None, None) for e in listed]
    elif not edits:
        edits.append(Edit(None, None))
    return tuple(edits)


def _shows_a_card(tool_name: str, tool_input: dict) -> bool:
    """True for a `start_session` call that only shows a card (`CARD_INITIATIONS`).
    Only a string `initiation` can name a card."""

    initiation = tool_input.get("initiation")
    return (tool_name == START_SESSION and isinstance(initiation, str)
            and initiation in CARD_INITIATIONS and tool_input.get("proposal_id") is None)


def _named(tool_input: dict, *keys: str) -> str | None:
    """The first of `keys` the input gives a value, when that value is a string."""

    value = next((tool_input[k] for k in keys if tool_input.get(k)), None)
    return value if isinstance(value, str) else None


def _text(value: object) -> str:
    return str(value or "")


def _known(value: object) -> str | None:
    return value if isinstance(value, str) else None


# Hold text in Claude Code's words ---------------------------------------------

PHRASES = {
    wording.SKILL_TOOL: "the Skill tool",
    wording.READ_TOOL: "the Read tool",
    wording.READ: "Read",
    wording.NO_RANGE: "with no limit, offset, or pages",
    wording.FILE_EDIT_TOOLS: "(Edit, MultiEdit, or Write)",
    # Checked on 2026-11-23: Edit kept CRLF on changed and new lines, and Git
    # Bash's `sed -i` turned every CRLF into LF (round 7, R6).
    wording.LINE_ENDINGS: ("The Edit tool keeps a file's line endings, so CRLF is no reason "
                           "to use a script, and \"sed -i\" in Git Bash can strip CR from a "
                           "file. "),
}


def render(text: str, tool_name: str | None = None, session_shell: str | None = None) -> str:
    """`text` from the rules in Claude Code's words, every `wording` slot filled.

    `tool_name` is the held call's tool, None for a held `Stop`. The carrier
    slot names a call that can carry a line only for a tool with no field for
    one, in the session's shell (`session_shell`, a shell kind), or in Bash
    before the session's first shell call, since Claude Code always has Bash;
    otherwise it goes, with the line break before it. Raises ValueError for a
    slot with no wording here, a rule's mistake.
    """

    carries = tool_name is not None and tool_name not in LINE_FIELDS
    if not carries:
        text = text.replace("\n" + wording.CARRIER, "")

    def fill(slot: re.Match) -> str:
        if slot[0] == wording.CARRIER:
            return _carrier(shell_tool(session_shell) or "Bash") if carries else ""
        if slot[0] in PHRASES:
            return PHRASES[slot[0]]
        if clearing := wording.clearing_of(slot[0]):
            return _advice(clearing.full, clearing.line, "each",
                           wording.typed(clearing.way_outs))
        advice = wording.ADVICE_RE.fullmatch(slot[0])
        if advice is None:
            raise ValueError(f"no Claude Code wording for the slot {slot[1]!r}")
        name, line, way_out = advice.groups()
        return _advice(name == wording.FULL_ADVICE, line, "the", wording.typed((way_out,)))

    return wording.SLOT_RE.sub(fill, text)


def _advice(full: bool, line: str, which: str, overrides: str) -> str:
    """A line-advice slot's text, or a clearing section's, full or short, for
    `line` ("skip line", "route or skip line"), put as `which` ("the" for one
    hold's line, "each" for a section's), and the typed `overrides`. A line in
    reply text may never be seen (README "Known Limits"), so the advice
    points to the fields of a call `LINE_FIELDS` names, then to the user's
    way out. It names those fields without backticks, since the skill-usage
    mod reads every backticked bare word in a hold as a skill. Claude Code
    judged one message's writes in order, each seeing the calls before it,
    in one probe run per shape (`docs/reference/carrier-probe-2026-11-19.md`),
    so the advice says a line may ride earlier in the same message, and
    promises no more."""

    if not full:
        return (
            f"Put {which} {line} on its own line in a shell or agent call's description or a "
            "Skill call's args, as this turn's first such hold explained, or tell the user "
            f"they can type {overrides} in their prompt."
        )
    return (
        f"A {line} in reply text may not be seen: Claude Code records a message only "
        "after this check, and can store the text of a message that makes a tool call "
        "as a summary that drops the line. A line in the description field of a shell "
        "or agent call, or in a Skill call's args, is read as written and counts from "
        f"that call on. Put {which} {line} on its own line there: in this call's description "
        "if it has one, or else in a call made earlier in the same message, when the held "
        "call is a write, or in an earlier message of this turn. Then make the call again. "
        f"If that is held again, tell the user they can type {overrides} in their prompt."
    )


def _carrier(tool: str) -> str:
    """The sentence naming a plain read in `tool` ("Bash" or "PowerShell")
    that passes every hold and carries a line. Nothing in it is backticked,
    since the skill-usage mod reads a backticked word as a skill."""

    command = shell.POWERSHELL_NO_OP if tool == "PowerShell" else "true"
    return (f"This call has no field for a line: put it on its own line in the description "
            f"of a {tool} call with the command {command}, earlier in the same message or in "
            "an earlier message, then make this call again.")
