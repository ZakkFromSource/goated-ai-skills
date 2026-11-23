"""Slots in the rules' hold texts for words only a harness can say.

A hold sometimes names how the agent does something in its harness: the
tool that loads a skill or reads a file, where a route or skip line can go
so the harness keeps it, and which call carries a line for a call with none.
The rules hold no harness wording (ADR 0004): they write a slot here. An
adapter that calls the core in Python (`judge`) may fill each slot from its
own table before the text is shown (`translation.render` for Claude Code);
the core's request call (`request.decide`), and so its command, fills them
with the neutral words of `neutral`, so no decision it returns carries a
slot.

A slot is its name, then any arguments each after `|`, between `OPEN` and
`CLOSE`: two private-use characters no keyboard types, so text a hold
quotes, such as a malformed route line or a file name, is never read as a
slot. `SLOT_RE` finds slots; `NAMES` are every slot's name.
"""

from __future__ import annotations

import re
from typing import NamedTuple

OPEN = ""
CLOSE = ""
SLOT_RE = re.compile(f"{OPEN}([a-z-]+)((?:\\|[^|{OPEN}{CLOSE}]+)*){CLOSE}")


def _slot(name: str, *arguments: str) -> str:
    return OPEN + "|".join((name, *arguments)) + CLOSE


# How the agent loads a skill, as the object of "with", such as "the
# harness's skill loader".
SKILL_TOOL = _slot("skill-tool")
# How the agent reads a file, as the object of "with", such as "a file read".
READ_TOOL = _slot("read-tool")
# A file read call, as a noun or a verb, such as "read".
READ = _slot("read")
# What makes a file read whole, such as "with no range".
NO_RANGE = _slot("no-range")
# The file edit calls, after "a file edit tool", such as "(a file write call)".
FILE_EDIT_TOOLS = _slot("file-edit-tools")
# What the harness's file edit tools and shell do to a file's line endings, as
# a sentence with its trailing space, in a hold on a script or shell write
# (round 7, R6), or nothing: agents script edits to keep CRLF, and only a
# harness can say whether its edit tool keeps it.
LINE_ENDINGS = _slot("line-endings")
# Ends a call's hold that a line can clear, on a line of its own: the harness
# names a call that can carry the line when the held call has no field for
# one, or says nothing and drops the line.
CARRIER = _slot("carrier")

FULL_ADVICE = "line-advice"
SHORT_ADVICE = "line-advice-short"
FULL_CLEARING = "clearing"
SHORT_CLEARING = "clearing-short"
NAMES = frozenset({"skill-tool", "read-tool", "read", "no-range", "file-edit-tools",
                   "line-endings", "carrier",
                   FULL_ADVICE, SHORT_ADVICE, FULL_CLEARING, SHORT_CLEARING})
# A line-advice slot; its groups are the slot's name, the line, and the way out.
ADVICE_RE = re.compile(
    f"{OPEN}({FULL_ADVICE}|{SHORT_ADVICE})\\|([^|{CLOSE}]+)\\|([^|{CLOSE}]+){CLOSE}")


def unseen_line_advice(line: str, way_out: str) -> str:
    """The slot for recovery advice in a hold that a route or skip line can
    clear. `line` names the line ("route line", "skip line"); `way_out` is
    the typed override that stands the hold down. A line in reply text may
    never be seen, so the harness says where else it can go, then gives the
    user's way out. `gates.shown_holds` shortens it on every hold of a turn but
    one (`short_advice`), and moves it into one `clearing_section` when a
    message carries several holds that hold it."""

    return _slot(FULL_ADVICE, line, way_out)


def short_advice(line: str, way_out: str) -> str:
    """The slot for the one sentence that stands for `unseen_line_advice`
    once a turn has had it."""

    return _slot(SHORT_ADVICE, line, way_out)


class Clearing(NamedTuple):
    """A clearing section, as `clearing_of` reads its slot: `full` when it
    stands for the full advice, else for its one sentence; `line`, the lines
    it places, such as "skip line" or "route or skip line"; `way_outs`, each
    hold's typed override, once each, in the holds' order."""

    full: bool
    line: str
    way_outs: tuple[str, ...]


def clearing_section(lines: list[str], way_outs: list[str], full: bool) -> str:
    """The slot for the one section that ends a message of several holds a
    line can clear, in place of each hold's own advice (`gates.shown_holds`):
    the full advice when `full`, else its one sentence, for the distinct
    `lines` the holds ask for and each distinct typed override."""

    kinds = dict.fromkeys(line.removesuffix(" line") for line in lines)
    return _slot(FULL_CLEARING if full else SHORT_CLEARING, " or ".join(kinds) + " line",
                 *dict.fromkeys(way_outs))


def clearing_of(slot: str) -> Clearing | None:
    """The clearing section `slot`, one whole slot as `SLOT_RE` finds it,
    stands for, or None for another slot."""

    name, *arguments = slot.removeprefix(OPEN).removesuffix(CLOSE).split("|")
    if name not in (FULL_CLEARING, SHORT_CLEARING) or len(arguments) < 2:
        return None
    return Clearing(name == FULL_CLEARING, arguments[0], tuple(arguments[1:]))


def typed(way_outs: tuple[str, ...]) -> str:
    """The overrides `way_outs`, backticked and joined as alternatives:
    "`a`", "`a` or `b`", "`a`, `b`, or `c`"."""

    quoted = [f"`{way_out}`" for way_out in way_outs]
    if len(quoted) < 3:
        return " or ".join(quoted)
    return ", ".join(quoted[:-1]) + ", or " + quoted[-1]


# Neutral words -----------------------------------------------------------------

# Each phrase slot in words any harness can show.
NEUTRAL_PHRASES = {
    SKILL_TOOL: "the harness's skill loader",
    READ_TOOL: "a file read",
    READ: "read",
    NO_RANGE: "with no range",
    FILE_EDIT_TOOLS: "(a file write call)",
    LINE_ENDINGS: "",
}


def neutral(text: str) -> str:
    """`text` with every slot filled in neutral words.

    Every call of the event model may carry a line in its `line_text`, so
    the carrier slot says nothing and goes with the line break before it.
    The line advice, and a clearing section, say where a line counts,
    without a harness's reasons for why reply text may not be seen. Raises
    ValueError for a slot with no neutral words, a rule's mistake.
    """

    text = text.replace("\n" + CARRIER, "")

    def fill(slot: re.Match) -> str:
        if slot[0] == CARRIER:
            return ""
        if slot[0] in NEUTRAL_PHRASES:
            return NEUTRAL_PHRASES[slot[0]]
        if clearing := clearing_of(slot[0]):
            return _neutral_advice(clearing.full, f"each {clearing.line}",
                                   typed(clearing.way_outs))
        advice = ADVICE_RE.fullmatch(slot[0])
        if advice is None:
            raise ValueError(f"no neutral wording for the slot {slot[1]!r}")
        name, line, way_out = advice.groups()
        return _neutral_advice(name == FULL_ADVICE, f"the {line}", typed((way_out,)))

    return SLOT_RE.sub(fill, text)


def _neutral_advice(full: bool, lines: str, overrides: str) -> str:
    """The neutral advice, full or short, for `lines` ("the skip line",
    "each route or skip line") and the typed `overrides`."""

    if not full:
        return (f"Put {lines} on its own line, as this turn's first such hold "
                f"explained, or tell the user they can type {overrides} in their prompt.")
    return (f"Put {lines} on its own line in reply text or in a call's line text; it "
            f"counts from there on. Then make the call again. If that is held again, "
            f"tell the user they can type {overrides} in their prompt.")
