"""Action gates (commit, pull request and its review, spawn, design, security,
conflict resolution, repeated failure) and the closeout gate.

These enforce skill triggers the skills already state (ADR 0003): commit with
`commit-message`, open a pull request with `pr-description` (and, when it is
large, `standards-and-spec-review`), brief a new agent
with `handoff`'s spawn brief or `subagent-driven-development`, design with
`software-design-principles`, review sensitive surfaces with
`code-security-review`, resolve a merge conflict with
`resolving-merge-conflicts`, investigate a check that keeps failing with
`diagnose`, close a code-changing turn with proof, `doc-sync`, `handoff`,
the design red flags, a
review when the branch is large, and `verification-before-completion` when
the work is large, delegated, sensitive, or on a `full` route, and close a
turn that changed setup with `setup-scribe`. The `reference-reads` gate
enforces the reads the installed registry declares for a loaded skill's
references (`reference_reads`). The `review-intake` gate starts the fixes
after a reviewer subagent's report with `receiving-code-review`.

Every decision is a pure function of the current turn as the transcript
records it, the user's typed overrides for that turn, and what counts from
earlier turns until the next compaction (`SinceCompaction`): skill loads,
design and skill reference reads, and spawn-brief template reads, whose text
is still in the agent's context. So an unchanged retry always gets the same answer
(spec R6), and a hold stops firing as soon as the turn shows compliance.
Everything else counts only within the current turn: skip lines, overrides,
change reads, and checks. Inside a subagent nothing carries over from its
earlier turns. The inputs from outside the transcript include a pull
request's size, which the `pr-review` gate asks git for, and only when its
hold would otherwise fire; the branch's work, which the closeout's Review
and Verification items ask git for only when nothing else met them; which
brief templates the turn's spawns followed, which the hooks record when the
`spawn` gate lets one through; and the registry's reference declarations,
read only for a write to a project file.

Strict holds clear only on proof or a user override. Justified-skip holds also
clear on a `goated-skip: <skill>: <reason>` line in the current turn.

Holds whose step reviews or describes the change (the closeout's design,
docs, and security items, the commit, the pull request, and its review) also
need a change read (spec R7): a finished call, after the skill load or reference
read and after the last code change, that put the change's content in front
of the agent. That is a command printing the diff, or a read of a file the
turn changed. It shows the agent the change; it cannot prove a review.

The gates judge calls by kind (`events`): a file write, a shell command, a
spawn, or a call that only records a commit or opens a pull request.
"""

from __future__ import annotations

import functools
import os
import posixpath
from collections.abc import Callable, Iterable, Iterator
from typing import NamedTuple
import re
import subprocess
import time
from stat import S_ISLNK, S_ISREG

from . import contracts, design_reads, events, reference_reads, shell
from .events import Call, Turn
from .gates import (
    CHAINED_STEPS, CHANGE_READ, SKIP_LINE_RULE, STRICT, UNFINISHED_READ, Hold, ask_purpose,
    goated_skill_name, short_form,
)
from .markers import parse_reply
from .wording import (
    FILE_EDIT_TOOLS, LINE_ENDINGS, NO_RANGE, READ, READ_TOOL, SKILL_TOOL, short_advice,
    unseen_line_advice,
)

JUSTIFIED_SKIP = "justified-skip"

COMMIT_SKILL = "commit-message"
PR_SKILL = "pr-description"
DESIGN_SKILL = "software-design-principles"
SECURITY_SKILL = "code-security-review"
DOC_SYNC_SKILL = "doc-sync"
HANDOFF_SKILL = "handoff"
PROOF_SKILL = "verification-before-completion"
INTAKE_SKILL = "receiving-code-review"
DIAGNOSE_SKILL = "diagnose"
# How many failures in a row of one check command, in one turn, make the repeated-failure hold.
REPEATED_FAILURES = 2
# A trailing pipe into an output filter, whose arguments hold no further pipe.
PIPE_TAIL_RE = re.compile(
    r"\s*\|\s*(?:tail|head|grep|egrep|findstr|more|less|tee|tee-object|select-object|select"
    r"|select-string|sls|out-host|out-string)\b[^|]*$",
    re.IGNORECASE,
)
STDERR_MERGE_RE = re.compile(r"\s*(?:2|\*)>&1$")
# A leading `cd` to one folder, joined to the rest by `&&` or `;` (spec R2).
LEADING_CD_RE = re.compile(
    r"""^cd\s+(?:"(?P<dq>[^"]*)"|'(?P<sq>[^']*)'|(?P<bare>[^\s;&|"']+))\s*(?:&&|;)\s*"""
)
# pytest's line saying collection errors stopped the run before any test ran.
COLLECTION_INTERRUPTED_RE = re.compile(r"^!+ Interrupted: \d+ errors? during collection",
                                       re.MULTILINE)
# Each test runner's run summary, and in it the counts of tests that failed
# or errored (spec R1): pytest's last line, unittest's `FAILED (...)`, jest's
# `Tests:` line, and cargo's `test result:`. Other runners the gate reads,
# such as go test, print no count.
FAILURE_COUNT_SIGNS = tuple(
    (re.compile(summary, re.MULTILINE), re.compile(counted)) for summary, counted in (
        (r"^=*\s*(\d+ (?:passed|failed|errors?|skipped|xfailed|xpassed|warnings?|deselected"
         r"|rerun)(?:, \d+ \w+)*) in \d+(?:\.\d+)?s\b", r"\b(\d+) (?:failed|errors?)\b"),
        (r"^FAILED \((.*)\)\s*$", r"\b(?:failures|errors)=(\d+)"),
        (r"^Tests:\s+(.*\btotal)\s*$", r"\b(\d+) failed\b"),
        (r"^test result: FAILED\. (.*)$", r"\b(\d+) failed\b"),
    )
)
# What test runners, linters, and compilers print when they fail.
FAILURE_SIGNS_RE = re.compile(
    r"\b[1-9]\d* (?:failed|failing|errors?|fail)\b|^FAILED\b|^FAIL\b|--- FAIL|npm ERR!"
    r"|^npm error\b|\berror TS\d+|\berror\[E\d+\]|test result: FAILED|^error: ",
    re.MULTILINE,
)

class _LoadErrorSigns(NamedTuple):
    """How one test runner reports a test module it could not load.

    `start` is the runner's own header for one such error; the error's text
    runs to the next line matching `end`. `real_failure` is what the runner
    prints for a failure in a test that did run.
    """

    start: re.Pattern
    end: re.Pattern
    real_failure: re.Pattern


def _signs(start: str, end: str, real_failure: str) -> _LoadErrorSigns:
    return _LoadErrorSigns(*(re.compile(p, re.MULTILINE) for p in (start, end, real_failure)))


# What test runners print when a test module could not be loaded. A run whose
# only failures are such errors, each caused by a missing module or name,
# failed before any test ran: in TDD the first red run is often one, because
# the module under test does not exist yet, and the agent knows why. A module
# that is there but broken (a SyntaxError, a NameError) is the edit-and-crash
# loop the gate exists for, so it counts. Only the runner's own headers count,
# so a test that prints import-error text is a real failure.
LOAD_ERROR_SIGNS = (
    _signs(  # pytest
        r"^_+ ERROR collecting \S.* _+$", r"^(?:_{3,} \S|={3,} )",
        r"^(?:=+ )?[1-9]\d* failed\b|^(?:FAILED|ERROR) \S+::",
    ),
    _signs(  # unittest
        r"^ERROR: \S+ \(unittest\.loader\._FailedTest\b", r"^={20,}$|^Ran \d+ tests? in ",
        r"^FAIL: |^ERROR: (?!\S+ \(unittest\.loader\._FailedTest\b)|^FAILED \(.*\bfailures=[1-9]",
    ),
    _signs(  # jest
        r"^\s*● Test suite failed to run$", r"^\s*●|^\s*(?:FAIL|PASS) |^Test Suites:",
        r"^Tests:.*\b[1-9]\d* failed\b|^\s*● (?!Test suite failed to run$)",
    ),
)
# The lines in a load error's text that name its cause, the last one winning:
# a Python exception line, plain or with pytest's `E` prefix; pytest's own
# line for an import error, which it prints before the traceback, so it
# survives a cut; and jest's missing-module message.
LOAD_ERROR_CAUSE_RE = re.compile(
    r"^(?:E\s+|\s*)(?:(?P<exception>[A-Z]\w*(?:Error|Exception)):"
    r"|(?P<missing>ImportError while importing test module|Cannot find module) ')",
    re.MULTILINE,
)
MISSING_MODULE_EXCEPTIONS = frozenset({"ImportError", "ModuleNotFoundError"})
SETUP_SKILL = "setup-scribe"
REVIEW_SKILL = "standards-and-spec-review"
RED_FLAGS_REFERENCE = "software-design-principles/references/red-flags.md"
# The question `red-flags.md` ends with, which the closeout's red-flags item
# repeats. No hold checks an answer.
RED_FLAGS_QUESTION = "Name one input that would break this change, and say what happens."
# How a hold asks for a required file: a read of part of it does not count
# (`Call.whole_read_path`).
WHOLE_READ = f"whole with {READ_TOOL}, {NO_RANGE}"
# How a hold asks for a change read (`gates.CHANGE_READ`), for a turn that
# changed no file it names, where a file read cannot count.
DIFF_ONLY_READ = (
    "this turn changed no file it can name, so print the diff with a git diff or git "
    "show command; a listing of names or counts, such as --stat or --name-only, does "
    "not count"
)
# Merge conflicts (spec G1). Markers count only at a line start, as git
# writes them, or after the line number a Read result puts there; `=======`
# alone is also a heading underline, so it is not one.
CONFLICT_SKILL = "resolving-merge-conflicts"
CONFLICT_MARKER_RE = re.compile(r"^(?:[ \t]*\d+(?:\t|→))?(?:<{7}|>{7})(?: |\r?$)", re.MULTILINE)
# A whole conflict block, in order, as an edit resolving one removes it
# (`_resolves_conflict`), and any marker line, which its added text must not hold.
CONFLICT_BLOCK_RE = re.compile(r"^<{7} .*?^={7}[ \t]*\r?$.*?^>{7} ", re.MULTILINE | re.DOTALL)
CONFLICT_LINE_RE = re.compile(r"^(?:<{7}|>{7})(?: |\r?$)|^={7}[ \t]*\r?$", re.MULTILINE)
# In `git diff` output (spec R10): the line opening a file's section, which
# names the file for a combined diff (`--cc`), its new name in a `+++` line
# before the first hunk, and a marker the diff adds, after the one or two
# `+` of its prefix (`++<<<<<<<` in a combined diff, `+<<<<<<<` in another).
GIT_DIFF_SECTION_RE = re.compile(r"^diff --(cc|combined|git) (.*)$")
GIT_DIFF_NEW_NAME_RE = re.compile(r"^\+\+\+ (.*)$")
GIT_DIFF_MARKER_RE = re.compile(r"^\+{1,2}(?:<{7}|>{7})(?: |$)")
# A name git quotes, C-style, because it holds a space, a quote, a control
# character, or a non-ASCII byte, which git writes as three octal digits.
GIT_QUOTED_NAME_END_RE = re.compile(r'"(?:[^"\\]|\\.)*"$')
GIT_NAME_ESCAPES = {"a": 7, "b": 8, "t": 9, "n": 10, "v": 11, "f": 12, "r": 13,
                    '"': 34, "\\": 92}
# `git` and any global options before its subcommand, within one simple command.
_GIT = r"(?<![\w-])git(?:\.exe)?\s(?:[^;&|\n]*\s)?"
_GIT_OPERATIONS = r"merge|rebase|cherry-pick|revert"
# A command naming one of the operations the skill covers; a `pull` merges or rebases.
GIT_CONFLICT_COMMAND_RE = re.compile(rf"{_GIT}(?:{_GIT_OPERATIONS}|pull)(?![\w-])")
# A command that ends one, whether the conflict was resolved or given up.
GIT_CONFLICT_END_RE = re.compile(
    rf"{_GIT}(?:{_GIT_OPERATIONS})\s(?:[^;&|\n]*\s)?--(?:abort|quit|continue|skip)(?![\w-])"
)
# The line git prints when one of them stops on a conflict: a merge's, or a
# rebase's, cherry-pick's, or revert's (older git prefixes `error: `).
GIT_CONFLICT_RESULT_RE = re.compile(
    r"^(?:Automatic merge failed|(?:error: )?could not (?:apply|revert) )",
    re.MULTILINE | re.IGNORECASE,
)
# An edit adding at least this many lines is a design change, not a tiny fix.
DESIGN_MIN_LINES = 5
# A comment-only edit (`design_reads.comment_only`) adding fewer lines than
# this is no design change either (round 4, R3): it explains code, not changes it.
COMMENT_EDIT_MIN_LINES = 20
# A shell write adding at least this many lines, counted, lands past the read
# gates, owing its reads to the Reads closeout item (round 5, R5). A file edit
# tool's write lands at any size (round 6, R1); shell writes keep this floor,
# as Ticket 118 leaves them out of its scope.
READS_LAND_MIN_LINES = 30
# A pull request, or a branch's work at the closeout, changing at least this
# many lines against its base, added plus deleted, in code files outside test
# paths (spec R11), is large enough to review before it lands: the threshold
# `standards-and-spec-review` states (contract, Branch Size).
REVIEW_MIN_LINES = 400
# Once the Review or Verification item is met or declined, a later turn of the
# task meets it while the branch has grown by fewer than this many lines since
# (round 7, R1; decision D6).
REVIEW_POINT_GROWTH = 50
# The route intensity whose work always needs `verification-before-completion` (spec R3).
FULL_ROUTE = "full"
# How long the size check's git calls may take in all before it gives up and
# holds nothing.
SIZE_TIMEOUT_SECONDS = 2.0
# `git diff` arguments for per-file counts (`_numstat_lines`): NUL-ended
# records, so no path is quoted, paths from the top of the checkout, and no
# external diff or text-conversion program.
NUMSTAT_ARGS = ("--numstat", "-z", "--no-relative", "--no-ext-diff", "--no-textconv")
# How much of an untracked file the branch-size check reads at a time.
UNTRACKED_READ_BYTES = 1 << 20
# Where a pull request merges into when it names no base, in order of preference.
DEFAULT_BASE_REFS = (
    "refs/remotes/origin/HEAD", "refs/remotes/origin/main", "refs/remotes/origin/master",
    "refs/heads/main", "refs/heads/master",
)

CODE_EXTENSIONS = frozenset(
    ".py .js .jsx .ts .tsx .mjs .cjs .go .rs .java .kt .kts .swift .c .h .cpp .hpp .cc .cs "
    ".rb .php .scala .ps1 .psm1 .sh .bash .lua .dart .vue .svelte .sql .ex .exs .clj .fs "
    ".zig .r .jl .ipynb".split()
)
DOC_EXTENSIONS = (".md", ".mdx", ".rst", ".adoc", ".txt")
# `.txt` files that build the project rather than document it (`is_doc`).
TXT_BUILD_FILES = frozenset({"cmakelists.txt"})
# Security-sensitive surfaces, by path. The first matching category is named.
# Paths are lowercased with camelCase humps split by `_` first, and words must
# stand alone between `/`, `.`, `_`, or `-`, so `tokenizer.py` and `author.py`
# are not secrets or auth, while `api_token.py` and `userAuth.ts` are.
# `session` is no auth word of its own (round 7, R5): `src/runtime/session.py`
# is held for nothing, while `auth/session.py` and `login_session.py` are held
# for the other auth word beside it.
_ALONE = r"(?<![a-z0-9])(?:{})(?![a-z0-9])"
SECURITY_CATEGORIES = (
    ("dependencies", re.compile(
        r"(?:^|/)(?:package(?:-lock)?\.json|pnpm-lock\.yaml|yarn\.lock|requirements[^/]*\.(?:txt|in)"
        r"|pyproject\.toml|poetry\.lock|uv\.lock|pipfile(?:\.lock)?|cargo\.(?:toml|lock)"
        r"|go\.(?:mod|sum)|gemfile(?:\.lock)?|composer\.(?:json|lock)|[^/]+\.csproj)$")),
    ("secrets", re.compile(
        r"(?:^|/)\.env(?:\.[^/]*)?$|\.(?:pem|key|p12|pfx)$|(?:^|/)id_(?:rsa|ed25519|ecdsa)|"
        + _ALONE.format(r"secrets?|credentials?|tokens?|api_?keys?"))),
    ("auth", re.compile(_ALONE.format(
        r"auth|authn|authz|authenticat\w*|authoriz\w*|oauth2?|login|logout|signin|jwt"
        r"|passwords?|permissions?|rbac|acls?|polic(?:y|ies)"))),
    ("persistence", re.compile(r"(?:^|/)migrations?/|(?:^|/)schema\.(?:sql|prisma)$|\.sql$")),
    ("deploy-and-ci", re.compile(
        r"(?:^|/)dockerfile|docker-compose|(?:^|/)\.github/workflows/|\.gitlab-ci|(?:^|/)terraform/"
        r"|\.tf$|(?:^|/)k8s/|(?:^|/)helm/|serverless\.ya?ml$")),
)
# Only dependency manifests among docs-like files (`requirements.txt`) are sensitive.
ALWAYS_CHECKED_CATEGORIES = frozenset({"dependencies"})
# The categories a word in a file's name selects, which test code does not meet
# (round 6, R9); dependencies, persistence and deploy-and-ci match by a file's
# kind or folder, so test code still meets them.
TEST_CODE_SPARED = frozenset({"auth", "secrets"})
# Env and settings files whose change is setup (spec G3): `.env` and `.env.*`,
# and `settings*.json` under `.claude/` or `.vscode/`. They count only inside
# the project (spec R9), so a scratch folder's or `~/.claude`'s settings do not.
SETUP_FILE_RE = re.compile(
    r"(?:^|/)\.env(?:\.[^/]*)?$|(?:^|/)\.(?:claude|vscode)/settings[^/]*\.json$", re.IGNORECASE
)
# Example env files, whose comments document settings rather than set them, so
# a change to their comments alone is no setup (round 7, R9; `_env_comments_only`).
EXAMPLE_ENV_FILES = frozenset({".env.example", ".env.sample", ".env.template"})


class SinceCompaction(NamedTuple):
    """What counts from earlier turns until the next compaction (spec R3, R4):
    the GOATED skills loaded (`tdd`), the design references read
    (`errors.md`), the spawn-brief templates read
    (`contracts.BriefTemplate.reference`), and the skill references read
    (`reference_reads.Reference.path`). `spans_turns` is False for a
    subagent, where only its current turn counts, so its holds ask for a
    load or read in this turn; the sets are then empty."""

    loads: frozenset[str] = frozenset()
    references_read: frozenset[str] = frozenset()
    templates_read: frozenset[str] = frozenset()
    spans_turns: bool = False
    skill_references_read: frozenset[str] = frozenset()


# A file's kind, as a lasting skip covers it (spec R4), with how a notice names it.
FILE_KINDS = {
    "test": "test files",
    "configuration": "configuration files",
    "code": "code files other than tests",
    "other": "files that are neither code nor configuration",
}


class LastingSkip(NamedTuple):
    """One reference a skip line excused for the rest of the task (spec R4):
    the gate that held for it (`design-reads` or `reference-reads`), the
    skill the skip line named, the kind of file (`FILE_KINDS`), and the
    reference as the gate keys its reads."""

    gate: str
    skill: str
    kind: str
    reference: str


class OwedRead(NamedTuple):
    """One reference a write that landed past a read gate still owes (round 5,
    R5), which the Reads closeout item asks for: the gate, the skill whose
    skip line answers it, the kind of file (`FILE_KINDS`; "" for a write
    naming no project file), the reference as the gate keys its reads, and
    the file written ("" for none)."""

    gate: str
    skill: str
    kind: str
    reference: str
    path: str


class TaskSkips:
    """The current task's lasting skips, and the reads a landed write owes, as
    one judged call sees them.

    `kept` are those earlier calls made, as (gate, skill, kind, reference).
    The `design-reads` and `reference-reads` gates add to `cleared` the
    lasting skips this turn's skip lines make, and to `notices` one text for
    each gate a kept skip let the call through. A write that may land
    (`_lands`) and that a gate would hold for reads alone lands instead:
    the gate adds its references to `owed`, and `check_action` gives
    `owed_notices` the call's one notice naming those the turn did not
    already owe (round 6, R1). The caller saves `cleared`, and `owed` when
    the call goes through, and shows the notices. A caller that keeps no
    state, as for a subagent, passes none: every skip line lasts its turn,
    and every write is held for its reads, since nothing would keep what it
    owes.

    A kept skip's notice is given once per task for each gate, skill and
    file kind (round 7, R3): `shown` are those keys an earlier call's notice
    already named, and the gates add to `carried` the keys this call's
    notices name, which the caller saves when the call goes through."""

    def __init__(self, kept=(), shown=()) -> None:
        self.kept = frozenset(LastingSkip(*skip) for skip in kept)
        self.shown = frozenset(tuple(key) for key in shown)
        self.carried: list[tuple[str, str, str]] = []
        self.cleared: list[LastingSkip] = []
        self.notices: list[str] = []
        self.owed: list[OwedRead] = []
        self.owed_notices: list[str] = []
        # Each gate that let this call land owing reads, in firing order:
        # (gate, the name the notice gives it, its needs, how it labels each).
        self.landings: list[tuple[str, str, list[_Need], Callable[[str, object], str]]] = []


class _Need(NamedTuple):
    """One reference a read gate asks for before a write to `path`: the file's
    `kind` (None for a write naming no project file, for which no skip
    outlasts its turn), the `skill` whose skip line answers it, the
    `reference` as the gate keys its reads, and the gate's own `detail` on why."""

    path: str | None
    kind: str | None
    skill: str
    reference: str
    detail: object


def file_kind(path: str, project: Project | None) -> str:
    """The kind of file `path` is, as a lasting skip covers it (`FILE_KINDS`)."""

    if is_test(path, project):
        return "test"
    if is_code(path):
        return "code"
    return "configuration" if design_reads.is_config(path) else "other"


def _unexcused(proof: "_Proof", gate: str, needs: list[_Need],
               label: Callable[[str], str]) -> list[_Need]:
    """The needs `gate` still holds for, under spec R4. A need whose skill a
    skip line of this turn names is cleared, and that skip lasts the task for
    its reference on files of its kind; a need such a lasting skip covers
    passes. When every need passes and a lasting skip let one through, the
    call carries a notice naming the skip, unless an earlier call of the
    task named the same gate, skill and kind (`TaskSkips.shown`). `label`
    names a reference as the hold does."""

    task = proof.task_skips
    held, carried = [], []
    for need in needs:
        skip = LastingSkip(gate, need.skill, need.kind or "", need.reference)
        if need.skill in proof.skips:
            if need.kind:
                task.cleared.append(skip)
        elif need.kind and skip in task.kept:
            carried.append(need)
        else:
            held.append(need)
    fresh = [need for need in carried if (gate, need.skill, need.kind) not in task.shown]
    if fresh and not held:
        task.notices.append(_carried_notice(gate, fresh, label))
        task.carried += [(gate, need.skill, need.kind) for need in fresh]
    return held


def _carried_notice(gate: str, carried: list[_Need], label: Callable[[str], str]) -> str:
    """The notice for a write `gate` let through on lasting skips alone."""

    unique = lambda values: list(dict.fromkeys(values))
    files = _listed(unique(f'"{_file_name(need.path)}"' for need in carried))
    references = ", ".join(unique(label(need.reference) for need in carried))
    lines = " and ".join(unique(f"`goated-skip: {need.skill}`" for need in carried))
    kinds = _listed(unique(FILE_KINDS[need.kind] for need in carried))
    return (f"the {gate} gate let this write to {files} through without a read of "
            f"{references}: an earlier {lines} line in this task cleared that for {kinds}, "
            "and it lasts until the task ends or the context compacts")


def _may_land(call: Call, shell_lines: int | None = None) -> bool:
    """Whether a write the read gates would hold for reads alone may land
    instead, owing them (`_lands`). A file edit tool's write lands at any
    size (round 6, R1) when it shows the text it adds; a shell write
    (`shell_lines`, the lines it shows it writes into judged files, or None
    when they cannot be counted) lands at `READS_LAND_MIN_LINES` or more
    (round 5, R5). A write whose text cannot be seen is held, so a shell
    write showing no text cannot slip past, and so is a call with no `id`,
    since the closeout finds a landed write by its id."""

    if not call.id:
        return False
    if call.kind == events.SHELL_COMMAND:
        return shell_lines is not None and shell_lines >= READS_LAND_MIN_LINES
    return countable_lines(call) is not None


def _lands(proof: "_Proof", gate: str, needs: list[_Need], landable: bool,
           label: Callable[[str, object], str], named: str | None = None) -> bool:
    """Whether a write `gate` would hold for `needs`, the reads it still
    lacks, lands instead: it is `landable` (`_may_land`) and the caller keeps
    the task's state. A landed write's needs are owed under `gate`, as its
    lasting skips are keyed, for the Reads closeout item, and the call's
    notice (`_owed_notice`) names the gate as `named` (by default `gate`)
    and each reference by `label(reference, detail)`."""

    if not (proof.keeps_task and landable):
        return False
    task = proof.task_skips
    task.owed += [OwedRead(gate, n.skill, n.kind or "", n.reference, n.path or "") for n in needs]
    task.landings.append((gate, named or gate, needs, label))
    return True


def _owed_reference(gate: str, reference: str) -> str:
    """A reference a read gate's landed write owes, as the Reads item and the
    notice name it: a design reference by its path under the skill's folder,
    a registry reference by its own path."""

    return f"{design_reads.SKILL_REFERENCES}{reference}" if gate == "design-reads" else reference


def _owed_notice(task: TaskSkips, owed_before: dict[str, list[OwedRead]], turn: Turn) -> list[str]:
    """The one notice for a call the read gates let land owing reads (round
    6, R1), or none: it names only references neither an earlier write of
    the turn that landed (`owed_before`, by call id) nor another gate of
    this call already owes, so the turn's first such write lists them all
    and a later one only what it adds. A write `turn` shows failed, or
    refused, owes nothing, as the Reads item judges; one not finished yet,
    such as another edit of the same message, counts. A reference already
    read is never owed."""

    unique = lambda values: list(dict.fromkeys(values))
    failed = {call.id for call in turn.calls
              if call.id and call.result is not None and not call.ok}
    already_owed = {_owed_reference(read.gate, read.reference)
                    for call_id, reads in owed_before.items() if call_id not in failed
                    for read in reads}
    clauses, skills = [], []
    for gate, name, needs, label in task.landings:
        fresh = []
        for need in needs:
            reference = _owed_reference(gate, need.reference)
            if reference not in already_owed:
                already_owed.add(reference)
                fresh.append(need)
        if not fresh:
            continue
        files = _listed(unique(f'"{_file_name(n.path)}"' for n in fresh if n.path))
        target = f" to {files}" if files else ""
        references = ", ".join(unique(label(n.reference, n.detail) for n in fresh))
        clauses.append(f"the {name} gate let this write{target} land before a read of {references}")
        skills += [n.skill for n in fresh]
    if not clauses:
        return []
    skip_lines = " or ".join(unique(f"`goated-skip: {skill}: <reason>`" for skill in skills))
    return [f"{'; '.join(clauses)}. Read each {WHOLE_READ} before a commit or your final "
            "report, then read the change itself and revise it against them; the closeout's "
            f"Reads item asks for both. If one does not apply, write {skip_lines} on its own "
            "line instead"]


class _Proof:
    """What the current turn shows, with what counts from earlier turns
    (`earlier`): loads, skip lines, reads, and user skips. `turn_loads` are
    the turn's own loads; `loads` add the earlier ones. `within` is what a
    hold adds after asking for a load or read: " in this turn" when earlier
    turns do not count, else "". `extra_text` is reply text the transcript
    may not hold yet, such as the reply a Stop is finishing. `task_skips`
    are the task's lasting skips (`TaskSkips`); none when not given, and
    then `keeps_task` is False, so no write lands owing reads."""

    def __init__(self, turn: Turn, overrides: dict, namespaces: tuple[str, ...],
                 extra_text: str = "", earlier: SinceCompaction = SinceCompaction(),
                 task_skips: TaskSkips | None = None) -> None:
        self.turn = turn
        self.keeps_task = task_skips is not None
        self.task_skips = task_skips or TaskSkips()
        self.namespaces = namespaces
        self.extra_text = extra_text
        self.turn_loads = {goated_skill_name(raw, namespaces) for raw in turn.loads} - {None}
        self.loads = self.turn_loads | earlier.loads
        self.references_read = earlier.references_read | set(design_reads.reads_in(turn.calls))
        self.templates_read = earlier.templates_read | set(contracts.templates_read(turn.calls))
        self.skill_references_read = (earlier.skill_references_read
                                      | set(reference_reads.reads_in(turn.calls)))
        self.within = "" if earlier.spans_turns else " in this turn"
        self.skips = {skip["skill"] for skip in turn.skips}
        if extra_text:
            self.skips |= {skip["skill"] for skip in parse_reply(extra_text).skips}
        self.user_skips = set(overrides.get("skills") or ())
        self.overrides = overrides

    def loaded(self, skill: str) -> bool:
        return skill in self.loads or skill in self.user_skips

    def skipped(self, skill: str) -> bool:
        return skill in self.skips or skill in self.user_skips

    def loaded_or_skipped(self, skill: str) -> bool:
        return self.loaded(skill) or skill in self.skips

    def load_index(self, skill: str) -> int | None:
        """Where in the turn's calls `skill` first loaded: -1 when the prompt
        invoked it as `/<skill>` or it loaded in an earlier turn, None when it
        does not count as loaded."""

        if skill not in self.loads:
            return None
        for index, call in enumerate(self.turn.calls):
            if (call.kind == events.SKILL_LOAD and call.ok
                    and goated_skill_name(call.skill, self.namespaces) == skill):
                return index
        return -1

    def read_index(self, reference: str, after: int = -1) -> int | None:
        """Where the first finished whole Read of `reference` after call `after` is, if any."""

        return next((index for index in self._read_indexes(reference) if index > after), None)

    def last_read_index(self, reference: str, before: int) -> int | None:
        """Where the last finished whole Read of `reference` before call `before` is, if any."""

        return next((index for index in reversed(self._read_indexes(reference)) if index < before), None)

    def _read_indexes(self, reference: str) -> list[int]:
        """Where each finished whole Read of `reference` in the turn is, in
        order (`Call.whole_read_path`): the one predicate `read_index` and
        `last_read_index` share."""

        return [
            index for index, call in enumerate(self.turn.calls)
            if (path := call.whole_read_path()) and _ends_with_path(path, reference)
        ]


class ReviewPoints:
    """The branch sizes at which the task's Review and Verification items were
    last met or declined (round 7, R1), keyed by item label, as one judged
    event sees them.

    `kept` are those earlier turns recorded. The closeout adds to `met` the
    size at which an item is met or declined by this turn's own evidence: a
    reviewer agent, the review skill with a change read, the verification
    skill's load, or a skip line. The caller saves `met`. While only branch
    size asks for an item, a later turn meets it while the branch has grown
    by fewer than `REVIEW_POINT_GROWTH` lines since its kept point. A caller
    that keeps no state, as for a subagent, passes none."""

    def __init__(self, kept: dict[str, int] | None = None) -> None:
        self.kept = dict(kept or {})
        self.met: dict[str, int] = {}

    def record(self, label: str, size: int | None) -> None:
        """Note that `label` was met or declined this turn on a branch of `size` lines."""

        if size is not None:
            self.met[label] = size

    def covers(self, label: str, size: int) -> bool:
        """Whether an earlier turn's point for `label` still covers a branch of `size` lines."""

        point = self.kept.get(label)
        return point is not None and size - point < REVIEW_POINT_GROWTH


class Closeout(NamedTuple):
    """What a commit's closeout hold reads besides the turn: `spawn_templates`,
    `intensity`, `briefed`, `owed_reads`, and `points`, as `check_closeout`
    takes them."""

    spawn_templates: dict[str, list[str]] | None = None
    intensity: str | None = None
    briefed: bool = False
    owed_reads: dict[str, list[OwedRead]] | None = None
    points: ReviewPoints | None = None


def check_action(call: Call, turn: Turn, overrides: dict,
                 namespaces: tuple[str, ...] = (), project: Project | None = None,
                 subagents: Callable[[], dict] | None = None,
                 earlier: SinceCompaction = SinceCompaction(),
                 closeout: Closeout | None = None,
                 references: Callable[[], tuple] | None = None,
                 task_skips: TaskSkips | None = None) -> list[Hold]:
    """Return every action hold this call meets, in the order the gates fire,
    one per gate; the call's own entry is not yet proof.

    Each gate gives the answer it would give alone (Ticket 095), and the
    closeout at a commit is judged beside the `commit` gate, so one held
    commit names everything it still needs (spec R4).

    `project` says which files are the project's (see `find_project`): only files
    inside it meet the design and security gates, and only changes to them
    are the turn's changes a change read must follow; git measures a pull
    request in its `cwd`. `subagents` returns the turns
    of each subagent this turn spawned, as `check_closeout` takes them; it is
    called only when a commit or pull request needs its change read, since
    reading their transcripts takes time. `earlier` is what counts from
    earlier turns until the next compaction. With `closeout`, a commit is
    held while the turn has unmet closeout items (Ticket 059),
    a subagent's own turn included (Ticket 098); without it, it is not. The
    `review-intake` gate reads the spawn templates `closeout` records, so
    without it, or in a subagent, which records none, it holds nothing.
    `references` returns the registry's declared references
    (`reference_reads.load`), called only for a write; without it, as for a
    subagent, the `reference-reads` gate holds nothing.
    `subagents` is also called for a write to a security-sensitive file when a
    loaded skill declares references, since the turn's sensitive categories
    include its subagents' changes.
    `task_skips` are the task's lasting skips, which the `design-reads` and
    `reference-reads` gates read and add to (`TaskSkips`), and where a write
    those gates let land (`_may_land`) records what it owes; without it,
    every skip line lasts its turn and no write lands owing reads.
    """

    proof = _Proof(turn, overrides, namespaces, earlier=earlier, task_skips=task_skips)
    reviewed = lambda path: _review_intake_hold(path, proof, closeout)
    spawned = functools.cache(subagents) if subagents else dict
    # The design and reference-reads gates may both read the registry for one write.
    references = functools.cache(references) if references else None
    changes = lambda: _Changes(turn, spawned(), project)
    at_commit = lambda by_tool=False: closeout and check_closeout(
        turn, overrides, namespaces, subagents=spawned(), project=project,
        at_commit=True, by_tool=by_tool, earlier=earlier,
        spawn_templates=closeout.spawn_templates, intensity=closeout.intensity,
        briefed=closeout.briefed, owed_reads=closeout.owed_reads, task_skips=task_skips,
        points=closeout.points,
    )
    cwd = project.cwd if project else None  # Where git measures a pull request's size.
    owes_reads = bool(closeout and closeout.owed_reads)
    holds = _Holds()
    if call.kind == events.SHELL_COMMAND:
        command = shell.analyze(call.command, call.shell)
        if command.writes:
            holds.add(lambda: _conflict_hold(command.write_targets, call, proof))
        if command.commit:
            holds.add(lambda: _commit_hold(command.commit_message, proof, changes,
                                           owes_reads=owes_reads))
            holds.add(at_commit)
        if command.opens_pr:
            holds.add(lambda: _pr_hold(proof, changes))
            holds.add(lambda: _pr_review_hold(
                lambda: _shell_pr_sizes(cwd, command.pull_requests), proof, changes))
        # Each gate judges every project file the command writes at once, so its
        # one hold asks for everything they need (Ticket 095).
        inside = [t for t in command.write_targets
                  if _in_project(t, project, t not in command.unplaced_targets)]
        paths = [_norm(t) for t in inside]
        holds.add(lambda: _security_hold(paths, proof, project))
        holds.add(lambda: next(filter(None, map(reviewed, paths)), None))
        # A script's write to a path built at run time is inside, and code (UNNAMED_FILES).
        scripted = [_norm(t) for t in inside if t in command.script_targets]
        holds.add(lambda: _scripted_edit_hold(scripted, command.script_unknown_writes, proof))
        if command.non_check_writes:
            # As for the repeated-failure gate, a check's own output is not a write
            # the turn makes; a target written from an unknown folder has no place.
            # A write naming no project file (`git apply`, a scratch file, an
            # unknown folder) still meets the turn's gate signals (None).
            placed = [_norm(t) for t in inside if t not in command.unplaced_targets]
            judged = [t for t in inside
                      if t not in command.unplaced_targets and t not in command.script_targets]
            landable = _may_land(call, _shell_written_lines(command, judged))
            holds.add(lambda: _design_hold(_shell_text_writes(command, project), None, proof,
                                           project, references, landable))
            holds.add(lambda: _reference_reads_hold(placed or [None], None, proof, project,
                                                    references, changes, landable))
            holds.add(lambda: _repeated_failure_hold(proof, project))
    elif call.kind == events.PULL_REQUEST:
        holds.add(lambda: _pr_hold(proof, changes, by_tool=True))
        holds.add(lambda: _pr_review_hold(
            lambda: [(changed_lines(cwd, call.base, call.head, call.repository), None)],
            proof, changes, by_tool=True))
    elif call.kind == events.COMMIT:
        holds.add(lambda: _commit_hold(call.message, proof, changes, by_tool=True,
                                       owes_reads=owes_reads))
        holds.add(lambda: at_commit(by_tool=True))
    elif call.kind == events.SPAWN:
        # A read-only agent's search brief needs no handoff template.
        if call.brief.strip() and not call.read_only:
            holds.add(lambda: _spawn_hold(call.brief, proof))
    elif call.kind == events.FILE_WRITE:
        path = _norm(call.path)
        # A conflict is open, and a check keeps failing, wherever the file lives
        # (a worktree may sit outside the project folder), as the shell branch
        # above holds every write target for them.
        holds.add(lambda: _conflict_hold([path], call, proof))
        landable = _may_land(call)
        if _in_project(path, project):
            # A scratch file elsewhere is not the project's design or security.
            holds.add(lambda: _security_hold([path], proof, project))
            holds.add(lambda: reviewed(path))
            holds.add(lambda: _design_hold({path: _small_edit(call)}, call, proof,
                                           project, references, landable))
            holds.add(lambda: _reference_reads_hold([path], call, proof, project,
                                                    references, changes, landable))
        else:
            # Only the turn's gate signals reach it, as the repeated-failure gate does.
            holds.add(lambda: _reference_reads_hold([None], None, proof, project, references,
                                                    changes, landable))
        holds.add(lambda: _repeated_failure_hold(proof, project))
    if task_skips is not None:
        task_skips.owed_notices = _owed_notice(
            task_skips, (closeout and closeout.owed_reads) or {}, turn)
    return holds.found


class _Holds:
    """The holds one call meets so far, in the order the gates fire. Each
    gate is judged once per call, over every file it writes."""

    def __init__(self) -> None:
        self.found: list[Hold] = []

    def add(self, judge: Callable[[], Hold | None]) -> None:
        """Run one gate's `judge` and keep its hold, if any."""

        hold = judge()
        if hold is not None:
            self.found.append(hold)


def _commit_hold(message: str | None, proof: _Proof, changes: Callable[[], "_Changes"],
                 by_tool: bool = False, owes_reads: bool = False) -> Hold | None:
    """Hold a commit until `commit-message` loads, its inline message (`message`,
    if known) keeps the contract, and the change is read after the turn's last
    material change (`_Changes.last_material`), before or after the load;
    `by_tool`: an MCP tool records it, not a git command; `owes_reads`: a
    write of the turn landed owing reads (`_change_read_ask`). One hold names
    every one of the three still unmet (spec R4); one alone keeps its own text."""

    supplied = proof.overrides.get("commit_message")
    if supplied and message is not None and (
        _subject(message) == _subject(supplied)
    ):
        return None  # The user typed this message (spec R8).
    if COMMIT_SKILL in proof.user_skips:
        return None
    load = None if proof.loaded(COMMIT_SKILL) else _Ask(
        f"Load the `{COMMIT_SKILL}` skill with {SKILL_TOOL}{proof.within} and draft the "
        "message with it.",
        f"`{COMMIT_SKILL}` has not loaded", "Load it and draft the message with it.")
    problems = contracts.commit_message_problems(message) if message is not None else []
    # No backticks: this ask is for a fix, not a load, and backticks name a skill to load.
    contract = _Ask(f"Fix the commit message, which breaks the {COMMIT_SKILL} contract: "
                    + "; ".join(problems) + ".", "", "") if problems else None
    current = changes()
    read = _change_read_ask(current, by_tool, "committing it",
                            "check that the message describes it and run the commit again",
                            since=current.last_material, owes_reads=owes_reads,
                            apart="the commit")
    asks = [ask for ask in (load, contract, read) if ask]
    typed = ("A commit message the user typed in their prompt stands it down when the commit "
             "uses that message.")
    strict = "This hold is strict: a goated-skip line does not clear it."
    if not asks:
        return None
    if asks == [contract]:
        return Hold("commit", STRICT, contract.text + " Then run the commit again.")
    if asks == [load]:
        return Hold(
            "commit", STRICT,
            f"{load.text.removesuffix('.')}, then run the commit again. {CHAINED_STEPS} "
            f"{strict} {typed}",
            short_form(load.unmet, "Load it, draft the message with it, and run the commit "
                                   f"again. {typed}"),
        )
    if asks == [read]:
        return _change_read_hold("commit", COMMIT_SKILL, read)
    # Several asks: each in turn, the rerun last, then the rules they share.
    rerun = "" if read else " Then run the commit again."
    reads_rule = f" {UNFINISHED_READ}" if read else ""
    text = (" ".join(ask.text for ask in asks) + rerun + f" {CHAINED_STEPS}{reads_rule} "
            f"{strict}" + (f" {typed}" if load else ""))
    # A bad message has no short form: what to fix is in its text alone.
    short = None if contract else short_form(
        " and ".join(ask.unmet for ask in asks),
        " ".join(ask.clear for ask in asks) + (f" {typed}" if load else ""))
    return Hold("commit", STRICT, text, short)


def _pr_hold(proof: _Proof, changes: Callable[[], "_Changes"],
             by_tool: bool = False) -> Hold | None:
    if PR_SKILL in proof.user_skips:
        return None
    if proof.loaded(PR_SKILL):
        return _change_read_hold("pull-request", PR_SKILL, _change_read_ask(
            changes(), by_tool, "opening the pull request",
            "check that the title and body describe it and open the pull request again"))
    return Hold(
        "pull-request", STRICT,
        f"Load the `{PR_SKILL}` skill with {SKILL_TOOL}{proof.within} and draft the "
        f"title and body with it, then open the pull request again. {CHAINED_STEPS} This "
        "hold is strict: a goated-skip line does not clear it.",
        short_form(f"`{PR_SKILL}` has not loaded", "Load it, draft the title and body with "
                   "it, and open the pull request again."),
    )


def _pr_review_hold(sizes: Callable[[], Iterable[tuple[int | None, str | None]]],
                    proof: _Proof, changes: Callable[[], "_Changes"],
                    by_tool: bool = False) -> Hold | None:
    """Hold a call whose pull requests include one that changes
    `REVIEW_MIN_LINES` or more lines until `standards-and-spec-review` loads
    and the change is read after the last change, before or after the load
    (Ticket 092), or a skip line names it. `sizes` gives each pull request's
    size (None: unknown) and how the hold names it (None: "this pull
    request", for a call opening only one), measuring each only as it is
    taken, so the first large one ends the measuring. Judged together with
    the `pull-request` gate (Ticket 095); `sizes` runs only when the turn's
    proof would not already clear it."""

    if proof.skipped(REVIEW_SKILL):
        return None
    hold = None
    if proof.loaded(REVIEW_SKILL):
        hold = _change_read_hold("pr-review", REVIEW_SKILL, _change_read_ask(
            changes(), by_tool, "opening the pull request",
            "review it and open the pull request again"), review=True)
        if hold is None:
            return None
    size, name = next(((size, name) for size, name in sizes()
                       if size is not None and size >= REVIEW_MIN_LINES), (None, None))
    if size is None:
        return None
    return hold or Hold(
        "pr-review", JUSTIFIED_SKIP,
        f"Load `{REVIEW_SKILL}` with {SKILL_TOOL}{proof.within} and review the change with "
        "it: " + (f"{name}," if name else "this pull request") + f" has {size} changed lines "
        f"of non-test code against its base, {REVIEW_MIN_LINES} or more, so it is large "
        "enough to review before it lands. If size is not "
        "what makes it worth reviewing, such as generated or vendored files, write "
        f"`goated-skip: {REVIEW_SKILL}: <reason>` on its own line instead. Then open the "
        f"pull request again. {CHAINED_STEPS} "
        + unseen_line_advice("skip line", f"skip {REVIEW_SKILL}"),
        short_form(f"a review of {name} ({size} lines)" if name
                   else f"a review of this {size}-line pull request",
                   f"Load `{REVIEW_SKILL}` and review the change with it, or write "
                   f"`goated-skip: {REVIEW_SKILL}: <reason>`. "
                   + short_advice("skip line", f"skip {REVIEW_SKILL}")),
    )


def _shell_pr_sizes(cwd: str | None, pull_requests: list[shell.PullRequest]
                    ) -> Iterator[tuple[int | None, str | None]]:
    """`_pr_review_hold`'s sizes for the pull requests one shell command
    opens, each measured with its own base, head and repository (spec R14),
    under one `SIZE_TIMEOUT_SECONDS` limit for them all; two that name the
    same base, head and repository are measured once. One alone is named as
    before; of several, each by its place, its base and any head."""

    deadline = time.monotonic() + SIZE_TIMEOUT_SECONDS
    measured: dict[tuple, int | None] = {}
    # Branch names are quoted, not backticked: backticks name a skill to load.
    quoted = lambda branch: branch.replace("`", "'")
    for number, pr in enumerate(pull_requests, 1):
        name = None
        if len(pull_requests) > 1:
            name = (f"pull request {number} of {len(pull_requests)} in this command, into "
                    + (quoted(pr.base) if pr.base else "its default base")
                    + (f" from {quoted(pr.head)}" if pr.head else ""))
        key = (pr.base, pr.head, pr.repository)
        if key not in measured:
            measured[key] = changed_lines(cwd, pr.base, pr.head, pr.repository,
                                          deadline=deadline)
        yield measured[key], name


class _WorkingTree:
    """The type of `WORKING_TREE`; it has no other value."""

    def __repr__(self) -> str:
        return "WORKING_TREE"


# A `changed_lines` head that is the working tree itself: the branch's
# commits, staged and unstaged changes, and untracked files git does not
# ignore. Not a string, so no branch name a tool supplies can ask for it.
WORKING_TREE = _WorkingTree()


def changed_lines(cwd: str | None, base: str | None, head: str | _WorkingTree | None = None,
                  repository: str | None = None, *, deadline: float | None = None
                  ) -> int | None:
    """Lines added plus deleted on `head` since it left `base`, as git in `cwd`
    reports them, in code files outside test paths only (`_counts_for_size`);
    None when that cannot be measured.

    `base` is the branch the pull request merges into, found as `origin/<base>`
    or the local branch; without one, the first of `DEFAULT_BASE_REFS` that
    exists. `head` is the branch it merges from, found as the local branch or
    `origin/<head>`; without one, the checked-out `HEAD`. A base or head that
    is in neither place, such as another fork's branch, is unknown.
    `repository` ("owner/repo") is the repository a tool or a shell
    `--repo`/`-R` aims at: unless it is the checkout's `origin`, this checkout
    says nothing about its size. One that is not an `owner/repo` path names
    no checkout.

    With `head` as `WORKING_TREE`, the measure is the branch's work as it
    stands (spec R1): the working tree against where the checked-out branch
    left `base`, plus every line of each untracked code file git does not
    ignore.
    A checkout on the base branch itself, or a detached one, has no branch
    work to compare, so it is unknown too.

    Two git calls, three with `repository`, five for the working tree, within
    `SIZE_TIMEOUT_SECONDS` in all, or by `deadline` (a `time.monotonic()`
    time) when the call shares one limit with other measures. Every name
    reaches git inside a full ref name (`refs/...`), so none reads as an
    option, and external diff and text-conversion programs are switched off,
    so only git runs.
    """

    if not cwd:
        return None
    if deadline is None:
        deadline = time.monotonic() + SIZE_TIMEOUT_SECONDS
    if repository is not None:
        if not events.REPOSITORY_RE.match(repository):
            return None
        url = _git(["config", "--get", "remote.origin.url"], cwd, deadline)
        if url is None or not _names_repository(url, repository):
            return None
    working_tree = head is WORKING_TREE
    base_refs = ((f"refs/remotes/origin/{base}", f"refs/heads/{base}") if base
                 else DEFAULT_BASE_REFS)
    head_refs = ((f"refs/heads/{head}", f"refs/remotes/origin/{head}")
                 if isinstance(head, str) and head else ())
    listed = _git(["for-each-ref", "--format=%(refname) %(symref)", *base_refs, *head_refs],
                  cwd, deadline)
    if listed is None:
        return None
    # A pattern also lists refs below it, so match exactly. `origin/HEAD` names
    # the branch it points at, which is the base branch's own name.
    targets = dict((line.split(" ", 1) + [""])[:2] for line in listed.splitlines())
    base_ref = next((ref for ref in base_refs if ref in targets), None)
    head_ref = next((ref for ref in head_refs if ref in targets), None) if head_refs else "HEAD"
    if base_ref is None or head_ref is None:
        return None
    if working_tree:
        # Where a base branch is both local and on `origin`, the branch left
        # whichever is closer to it: work merged locally and not yet pushed
        # leaves `origin/<base>` behind (spec R1).
        name = _branch_name(targets[base_ref] or base_ref)
        bases = dict.fromkeys(
            [base_ref] + [ref for ref in (f"refs/remotes/origin/{name}", f"refs/heads/{name}")
                          if ref in targets])
        return _branch_work_lines(cwd, list(bases), name, deadline)
    stat = _git(["diff", *NUMSTAT_ARGS, f"{base_ref}...{head_ref}", "--"], cwd, deadline)
    return None if stat is None else _numstat_lines(stat)


def _branch_name(ref: str) -> str:
    """A local or `origin` branch's name, from its full ref name."""

    return ref.strip().removeprefix("refs/heads/").removeprefix("refs/remotes/origin/")


def _branch_work_lines(cwd: str, base_refs: list[str], base_branch: str,
                       deadline: float) -> int | None:
    """`changed_lines` with the working tree as its head, once the base is
    found: `base_refs` are the existing refs of the base branch, named
    `base_branch`, and the branch is measured from the fork point closest
    to it among them."""

    found = _git(["rev-parse", "--show-toplevel", "--symbolic-full-name", "HEAD"], cwd, deadline)
    top, branch = ((found or "").splitlines() + ["", ""])[:2]
    if not top or not branch.startswith("refs/heads/"):
        return None  # Detached, or on a branch with no commit yet.
    if _branch_name(branch) == base_branch:
        return None  # On the base branch: nothing to compare it with.
    # With several bases, git gives the best common ancestor of HEAD and any of
    # them: the fork point no other one descends from, the closest to HEAD.
    fork = _git(["merge-base", "HEAD", *base_refs], cwd, deadline)
    if fork is None:
        return None
    stat = _git(["diff", *NUMSTAT_ARGS, fork.strip(), "--"], cwd, deadline)
    # `:/` lists from the top of the checkout; `--full-name` names paths from there too.
    untracked = _git(["ls-files", "--others", "--exclude-standard", "--full-name", "-z", "--",
                      ":/"], cwd, deadline)
    if stat is None or untracked is None:
        return None
    total = _numstat_lines(stat)
    for path in filter(_counts_for_size, untracked.split("\0")):
        lines = _text_lines(os.path.join(top, path), deadline)
        if lines is None:
            return None
        total += lines
    return total


def _text_lines(path: str, deadline: float) -> int | None:
    """The lines in the file at `path`, as `git diff` would count them added:
    1 for a symbolic link, whose target is never read, and 0 for a binary
    file (one holding a NUL byte), anything else that is not a regular file,
    or one that cannot be read. None when `deadline` passes first; it is
    checked between reads, so a huge file cannot hold the hook past it."""

    lines, last = 0, b"\n"
    try:
        mode = os.lstat(path).st_mode
        if S_ISLNK(mode):
            return 1  # git records a link as one line: its target's path.
        if not S_ISREG(mode):
            return 0
        with open(path, "rb") as text:
            while chunk := text.read(UNTRACKED_READ_BYTES):
                if time.monotonic() > deadline:
                    return None
                if b"\0" in chunk:
                    return 0
                lines += chunk.count(b"\n")
                last = chunk[-1:]
    except OSError:
        return 0  # Gone since git listed it, or unreadable: it adds nothing to see.
    return lines + (last != b"\n")  # A last line with no newline still counts.


def _counts_for_size(path: str) -> bool:
    """Whether a changed file's lines count toward a branch's or pull request's
    size (spec R11): a code file outside test paths, judged by its path from
    the top of the checkout. Docs, fixtures, configuration and tests add nothing."""

    return is_code(path) and not design_reads.is_test_path(path)


def _numstat_lines(stat: str) -> int:
    """Lines added plus deleted in the files that `_counts_for_size`, from
    `git diff` output with `NUMSTAT_ARGS`. Each record is "added<TAB>deleted<TAB>path",
    or, for a rename or copy, "added<TAB>deleted<TAB>" then the old and the new
    path, each ended by NUL; a binary file's counts are "-"."""

    total = 0
    fields = iter(stat.split("\0"))
    for record in fields:
        if not record:
            continue
        added, deleted, path = record.split("\t", 2)
        if not path:  # A rename or copy: judged by where the file now is.
            next(fields, "")
            path = next(fields, "")
        if added != "-" and _counts_for_size(path):
            total += int(added) + int(deleted)
    return total


def _git(args: list[str], cwd: str, deadline: float) -> str | None:
    """Run git with `args` in `cwd` and return its output; None when it fails,
    is missing, or runs past `deadline`. The C locale keeps git's words
    English, and undecodable bytes are replaced, never raised."""

    remaining = deadline - time.monotonic()
    if remaining <= 0:
        return None
    try:
        result = subprocess.run(
            ["git", "-c", "core.fsmonitor=false", *args],
            cwd=cwd, capture_output=True, encoding="utf-8", errors="replace",
            timeout=remaining,
            env={**os.environ, "GIT_OPTIONAL_LOCKS": "0", "LC_ALL": "C", "LANG": "C"},
        )
    except (OSError, subprocess.SubprocessError):
        return None  # No git, no such folder, or too slow: the size is unknown.
    return result.stdout if result.returncode == 0 else None


def _names_repository(url: str, repository: str) -> bool:
    """True when the remote `url` (HTTPS or SSH form) is `repository`, "owner/repo"."""

    path = url.strip().lower().rstrip("/").removesuffix(".git")
    wanted = repository.lower()
    return path.endswith("/" + wanted) or path.endswith(":" + wanted)


class _Ask(NamedTuple):
    """One unmet ask of a hold that may name several (spec R4): its `text`
    in full, without the rules the hold ends with, and `unmet` and `clear`
    for its short form (`short_form`)."""

    text: str
    unmet: str
    clear: str


def _change_read_ask(changes: "_Changes", by_tool: bool, doing: str, then: str,
                     since: int | None = None, owes_reads: bool = False,
                     apart: str = "") -> _Ask | None:
    """The change read a commit or pull request still needs, or None: a read
    must follow call `since`, by default the turn's last change to any
    project file, before or after the skill's load (Tickets 059 and 092).
    `owes_reads`: a write of the turn landed owing reads, so the ask says to
    read those first. `apart` names the held call, such as "the commit", when
    the ask says to make the read in an earlier message than it (round 7,
    R10): a read sent in the call's own message has not finished when the
    call is judged.

    An MCP tool (`by_tool`) passes when the turn changed no project file: it
    carries the change in its own input, and outside a git checkout no diff
    can run and no changed file exists to Read, so the strict hold would have
    no way out.
    """

    since = changes.last_change if since is None else since
    if by_tool and changes.last_change < 0:
        return None
    if changes.read_after(since):
        return None
    how = CHANGE_READ if changes.paths else DIFF_ONLY_READ
    after = ", after your last change" if since >= 0 else ""
    # The Reads item counts only a read of the file made after the references
    # it owes, so one read made in that order meets both (round 6, R11).
    ask = (f"Read the references this turn's writes owe first, if any is still unread, then "
           f"the change before {doing}{after}, so one read of it meets the Reads item too"
           if owes_reads else f"Read the change before {doing}{after}")
    earlier = (f" Make that read in an earlier message than {apart}, since a read sent in "
               f"{apart}'s own message cannot count for it." if apart else "")
    return _Ask(
        f"{ask}: {how}.{earlier} Then {then}.",
        f"a change read{after}",
        (f"Print the diff or {READ} a file you changed" if changes.paths
         else f"Print the diff with a git diff or git show command (a {READ} cannot "
              "count: this turn changed no file it can name)")
        + f", then {then}. A --stat or --name-only listing does not count, nor "
        "does a read chained in this command or made in parallel."
        + (f" Make the read in an earlier message than {apart}." if apart else ""),
    )


def _change_read_hold(gate: str, skill: str, ask: _Ask | None,
                      review: bool = False) -> Hold | None:
    """The hold for a change read `ask` (`_change_read_ask`), or None.
    `review`: the hold asks for a review done with `skill`, and it is
    justified-skip, so a skip line naming `skill` clears it."""

    if ask is None:
        return None
    # Not backticked: a reader of hold texts (contract, Hold Text) would take a
    # backticked skip line as an ask only a skip line answers, and count a read
    # that clears this hold as ignored.
    tail = (f"Or write a skip line, goated-skip: {skill}: <reason>, on its own line. "
            + unseen_line_advice("skip line", f"skip {skill}") if review
            else "This hold is strict: a goated-skip line does not clear it.")
    short_tail = (f" Or write a skip line, goated-skip: {skill}: <reason>. "
                  + short_advice("skip line", f"skip {skill}") if review else "")
    return Hold(
        gate, JUSTIFIED_SKIP if review else STRICT,
        f"{ask.text} {CHAINED_STEPS} {UNFINISHED_READ} {tail}",
        short_form(ask.unmet, f"{ask.clear}{short_tail}".rstrip()),
    )


def _spawn_hold(brief: str, proof: _Proof) -> Hold | None:
    if proof.user_skips & {t.skill for t in contracts.BRIEF_TEMPLATES}:
        return None  # The user typed `skip handoff` or `skip subagent-driven-development`.
    loaded = [t for t in contracts.BRIEF_TEMPLATES if t.skill in proof.loads]
    if not loaded:
        return Hold(
            "spawn", STRICT,
            f"Load `{HANDOFF_SKILL}` with {SKILL_TOOL}{proof.within} before starting another "
            "agent or session with a brief, read its `references/spawn-brief.md` whole, and "
            "write the brief from that template ("
            + ", ".join(contracts.HANDOFF_TEMPLATE.headings)
            + ", and its skills line at least). For a "
            "scoped implementation or review task, load `subagent-driven-development` "
            "and fill its implementer or reviewer prompt instead. Nothing was started. "
            "This hold is strict: a goated-skip line does not clear it.",
            short_form(f"load `{HANDOFF_SKILL}` and read its `references/spawn-brief.md` whole, "
                       "or load `subagent-driven-development` and fill its prompt",
                       "Then write the brief from it. Nothing was started."),
        )
    read = _templates_read(proof)
    if not read:
        files = " or ".join(f"`{t.reference}`" for t in loaded)
        return Hold(
            "spawn", STRICT,
            f"Read {files} {WHOLE_READ}{proof.within}, and write the brief from it. "
            "The template is the point of this step, so the skill load alone does not "
            "clear the hold. Nothing was started.",
            short_form(f"read {files} {WHOLE_READ}", "Then write the brief from it. Nothing was "
                       "started."),
        )
    problems = []
    if not _matched_templates(brief, proof):
        lacking_headings = [t for t in read if t.missing_headings(brief)]
        lacking_status = [t for t in read if t not in lacking_headings]
        if lacking_headings:
            gaps = "; ".join(
                f"`{t.reference}` needs "
                + ", ".join(f"`## {h}`" for h in t.missing_headings(brief))
                for t in lacking_headings
            )
            problems.append(f"Add the headings its template keeps as Markdown headings, "
                            f"since the brief lacks them: {gaps}.")
        if lacking_status:
            # Ticket 126: a report section of prose lost the report it asks for.
            sections = " or ".join(f"`## {h}`" for h in dict.fromkeys(
                t.report for t in lacking_status))
            # Only skill names are backticked as bare words (contract, Hold Messages).
            *first, last = contracts.STATUS_VALUES
            problems.append(
                f"Add the Status line under {sections}, outside code blocks, naming the "
                f"four values {', '.join(first)} and {last}, since the brief's report "
                "section lacks it: copy that section as its template writes it."
            )
    line_problem = contracts.skills_line_problem(brief)
    if line_problem:
        # The line's form is defined in handoff's references/spawn-brief.md (Ticket 071).
        problems.append(
            "Name the skills the new agent should read before it starts, on a line of its "
            "own or as a list item, outside code blocks and not in bold, by their installed "
            "names, bare or with a plugin namespace: `goated-skills: <skill>, <skill>`, or "
            f"`goated-skills: none: <reason>` when none applies, since the brief {line_problem}. "
            "The agent loads each with its skill tool, or reads its SKILL.md file when it "
            "has none."
        )
    if not problems:
        return None
    return Hold("spawn", STRICT, " ".join(problems) + " Then start it again. Nothing was started.")


def _templates_read(proof: _Proof) -> list[contracts.BriefTemplate]:
    """The brief templates whose skill counts as loaded and which were read."""

    return [t for t in contracts.BRIEF_TEMPLATES
            if t.skill in proof.loads and t.reference in proof.templates_read]


def _matched_templates(brief: str, proof: _Proof) -> list[contracts.BriefTemplate]:
    """The templates `brief` follows: loaded, read, and with every heading they
    keep and their report section's Status line."""

    return [t for t in _templates_read(proof) if t.follows(brief)]


def brief_templates(call: Call, turn: Turn, overrides: dict,
                    namespaces: tuple[str, ...] = (),
                    earlier: SinceCompaction = SinceCompaction()) -> list[str]:
    """The `reference` of each brief template a spawn's brief follows, as the
    `spawn` gate judges it, for the closeout's Review item; [] for a call
    that is no spawn. A brief that follows
    `contracts.REVIEWER_TEMPLATE` starts a reviewer subagent. Call it for a
    call `check_action` let through."""

    if call.kind != events.SPAWN:
        return []
    proof = _Proof(turn, overrides, namespaces, earlier=earlier)
    return [t.reference for t in _matched_templates(call.brief, proof)]


def _review_intake_hold(path: str, proof: _Proof, closeout: Closeout | None) -> Hold | None:
    """Hold a write to a project code file once a reviewer subagent's report
    has arrived in the turn, until `receiving-code-review` counts as loaded
    (Ticket 070), as the skill's Activation states. A skip line naming the
    skill clears it for the turn. Without `closeout`, or in a subagent, which
    records no spawn templates, nothing is held."""

    if not closeout or not is_code(path) or proof.loaded_or_skipped(INTAKE_SKILL):
        return None
    templates = closeout.spawn_templates or {}
    if not any(_reviewer_returned(call, proof, templates) for call in proof.turn.calls):
        return None
    return Hold(
        "review-intake", JUSTIFIED_SKIP,
        f"Load `{INTAKE_SKILL}` with {SKILL_TOOL} before the first code edit, since a "
        "reviewer subagent reported in this turn, and classify each finding as accepted, "
        "rejected, unclear, or a user decision; then fix only the accepted ones. If the "
        f"report has nothing to act on, write `goated-skip: {INTAKE_SKILL}: <reason>` on its "
        "own line instead. This edit was not applied. "
        + unseen_line_advice("skip line", f"skip {INTAKE_SKILL}"),
        _load_or_skip(INTAKE_SKILL, "a reviewer's report has arrived"),
    )


def _load_or_skip(skill: str, unmet: str) -> str:
    """The short form of a justified-skip hold that `skill`'s load or skip line clears."""

    return short_form(unmet, f"Load `{skill}` with {SKILL_TOOL}, or write "
                             f"`goated-skip: {skill}: <reason>`. "
                      + short_advice("skip line", f"skip {skill}"))


def _reviewer_returned(call, proof: _Proof, spawn_templates: dict[str, list[str]]) -> bool:
    """True for a finished spawn of a subagent that started work now, whose
    brief followed the reviewer prompt (`spawn_templates`, by call id) and
    whose report has arrived: at once, or for one started in the background,
    once its completion arrived in the turn. A held or failed spawn reported
    nothing, and one that only proposes the work (`starts_now` false) ran
    nothing. A separate agent's result, such as a side session's, arrives at
    once but only says its review started, so it never counts."""

    return (
        call.ok and call.kind == events.SPAWN and call.starts_now and not call.separate
        and contracts.REVIEWER_TEMPLATE.reference in spawn_templates.get(call.id, ())
        and (not call.launched_async or call.agent_id in proof.turn.finished_agents)
    )


def _security_hold(paths: list[str], proof: _Proof, project: Project | None) -> Hold | None:
    """Hold a write to the project files `paths`, one call's, while any is a
    security-sensitive surface (`sensitive_category`), until
    `code-security-review` loads or is skipped; one hold names every such file."""

    sensitive = [(_file_name(p), c) for p in paths if (c := sensitive_category(p, project))]
    if not sensitive or proof.loaded_or_skipped(SECURITY_SKILL):
        return None
    surfaces = _listed([f"\"{name}\" ({category})" for name, category in sensitive])
    if len(sensitive) == 1:
        name, category = sensitive[0]
        why = f"\"{name}\" is a security-sensitive surface ({category})."
    else:
        why = f"{surfaces} are security-sensitive surfaces."
    return Hold(
        "security", JUSTIFIED_SKIP,
        f"Load `{SECURITY_SKILL}` with {SKILL_TOOL}{proof.within} and review this change "
        f"with it: {why} If the change crosses no trust boundary and touches no auth, secrets, "
        "persistence, execution, dependency, or deployment behaviour, write "
        f"`goated-skip: {SECURITY_SKILL}: <reason>` on its own line instead. This edit "
        "was not applied. " + unseen_line_advice("skip line", f"skip {SECURITY_SKILL}"),
        _load_or_skip(SECURITY_SKILL, f"a review of {surfaces}"),
    )


def _file_name(path: str) -> str:
    return path.rsplit('/', 1)[-1]


def _listed(names: list[str]) -> str:
    """`names` joined as a list in a sentence: "a", "a and b", "a, b, and c"."""

    if len(names) < 3:
        return " and ".join(names)
    return ", ".join(names[:-1]) + ", and " + names[-1]


def _scripted_edit_hold(paths: list[str], unknown: bool, proof: _Proof) -> Hold | None:
    """Hold an inline interpreter script that writes the project code files
    among `paths`, or, when `unknown`, a file it names only at run time,
    which is held as code would be, as an unnamed write counts as code for
    the closeout; one hold names them all. Its kind cannot be told, so the
    text says so rather than calling the file code (spec R4). A script's
    edit meets no design or reference read, so the hold asks for a file edit
    tool; a skip line or the typed override for the design skill clears it
    for the turn, loading the skill does not. So the text names the skill
    only in its skip line: a bare backticked name reads as a skill to load
    (`friction.py`)."""

    code = [f"\"{_file_name(p)}\"" for p in paths if is_code(p)]
    if (not code and not unknown) or proof.skipped(DESIGN_SKILL):
        return None
    named = [("the code file " if len(code) == 1 else "the code files ") + _listed(code)] \
        if code else []
    if unknown:
        named.append("a file it names only at run time, whose kind cannot be told, "
                     "so it is held as code would be")
    what = " and ".join(named)
    return Hold(
        "scripted-edit", JUSTIFIED_SKIP,
        f"Make the change with a file edit tool {FILE_EDIT_TOOLS}, where the design and "
        f"reference holds can judge it: an inline script in this command writes {what}. "
        f"{LINE_ENDINGS}A script suits only a mechanical rewrite across many files; for one, "
        f"write `goated-skip: {DESIGN_SKILL}: <reason>` on its own line instead. Loading "
        "the skill does not clear this hold. This command was not run. "
        + unseen_line_advice("skip line", f"skip {DESIGN_SKILL}"),
        short_form(f"an inline script writes {what}",
                   "Make the change with a file edit tool, or write "
                   f"`goated-skip: {DESIGN_SKILL}: <reason>`. "
                   + short_advice("skip line", f"skip {DESIGN_SKILL}")),
    )


def _conflict_hold(paths: list[str], call: Call, proof: _Proof) -> Hold | None:
    """Hold a write to `paths`, by `call`, while a conflict is open in the
    turn (spec G1): the write removes conflict markers, writes a file the
    turn showed with markers in it (see `_open_conflict`), or follows a git
    merge, rebase, cherry-pick, revert, or pull whose result reported a
    conflict that no later abort, continue, or commit ended. Only the turn is
    read, never the repository on disk, so a conflict opened in an earlier
    turn is seen only through its markers."""

    if proof.loaded_or_skipped(CONFLICT_SKILL):
        return None
    edits_markers = any(removed is not None and CONFLICT_MARKER_RE.search(removed)
                        for removed, _ in call.edits)
    git_open, marked_files, _ = _open_conflict(proof.turn)
    writes_marked = any(_same_file(marked, path) for marked in marked_files for path in paths)
    if not (edits_markers or git_open or writes_marked):
        return None
    return Hold(
        "conflict-resolution", JUSTIFIED_SKIP,
        f"Load `{CONFLICT_SKILL}` with {SKILL_TOOL}{proof.within} and resolve the "
        "conflict from the intent behind both sides: a merge conflict is open in this "
        "turn. If this write does not resolve the conflict, write "
        f"`goated-skip: {CONFLICT_SKILL}: <reason>` on its own line instead. This write "
        "was not applied. " + unseen_line_advice("skip line", f"skip {CONFLICT_SKILL}"),
        _load_or_skip(CONFLICT_SKILL, "a merge conflict is open"),
    )


class _Conflict(NamedTuple):
    """A turn's conflict state, as `_open_conflict` reads it: whether a git
    conflict is still `git_open`, the `marked_files` shown with markers, and
    whether a finished edit resolved a conflict (`resolved_by_edit`,
    `_resolves_conflict`), each since the last conflict ended."""

    git_open: bool
    marked_files: list[str]
    resolved_by_edit: bool

    @property
    def being_resolved(self) -> bool:
        """Whether a commit now ends a conflict (round 6, R8): a git conflict is
        open, or an edit resolved one, as a conflict opened in an earlier turn
        shows itself. Markers only shown, or removed from a doc or one line
        at a time, are not a conflict to end."""

        return self.git_open or self.resolved_by_edit


def _resolves_conflict(write: Call, project: Project | None) -> bool:
    """Whether a file edit resolves a conflict (round 6, R8, the lead's narrow
    rule): the file is no doc (`is_doc`), one edit's removed text holds a
    whole conflict block in order (`CONFLICT_BLOCK_RE`), and that edit's
    added text holds no marker line. A doc's marker example, or one marker
    line removed alone, resolves nothing."""

    return not is_doc(write.path, project) and any(
        old is not None and new is not None and CONFLICT_BLOCK_RE.search(old)
        and not CONFLICT_LINE_RE.search(new)
        for old, new in write.edits)


def _open_conflict(turn: Turn, project: Project | None = None) -> _Conflict:
    """Read the turn's calls in order and return whether a git conflict is still
    open, the files shown with markers, and whether an edit resolved a
    conflict, each since the last conflict ended.

    A git merge, rebase, cherry-pick, revert, or pull whose result reports a
    conflict opens one (a conflicting stash pop or apply prints none of git's
    stop lines). A finished abort, quit, continue, or skip of one of them, a
    finished shell `git commit`, or a finished `commit` call ends it, unless
    that same call reports a new conflict.

    A file is shown with markers by a finished file read whose text has one,
    by a finished command whose output has one and that runs a file printer
    naming the file (spec R10, so `cat a b` shows both), or by a finished
    `git diff` whose section for the file adds one. Markers are removed by a
    finished edit that resolves a conflict (`_resolves_conflict`); `project`
    tells a doc, whose edits never do, from code.
    """

    git_open, marked_files, removed = False, [], False
    for call in turn.calls:
        if call.kind == events.FILE_READ:
            if call.ok and CONFLICT_MARKER_RE.search(call.output):
                marked_files.append(call.path)
        elif call.kind == events.FILE_WRITE:
            removed = removed or (call.ok and _resolves_conflict(call, project))
        elif call.kind == events.COMMIT:
            if call.ok:
                git_open, marked_files, removed = False, [], False
        elif call.kind == events.SHELL_COMMAND:
            command = call.command
            if GIT_CONFLICT_COMMAND_RE.search(command) and GIT_CONFLICT_RESULT_RE.search(call.output):
                git_open = True
                continue
            if not call.ok:
                continue
            analysis = shell.analyze(command, call.shell)
            if GIT_CONFLICT_END_RE.search(command) or analysis.commit:
                git_open, marked_files, removed = False, [], False
                continue
            if CONFLICT_MARKER_RE.search(call.output):
                marked_files += analysis.shown_files
            if analysis.shows_git_diff:
                marked_files += _diff_files_adding_markers(call.output)
    return _Conflict(git_open, marked_files, removed)


def _diff_files_adding_markers(output: str) -> list[str]:
    """The files whose section of `git diff` output adds a conflict marker,
    named as the diff names them (from the repository's top folder)."""

    files, path, in_header = [], None, False
    for line in output.splitlines():
        section = GIT_DIFF_SECTION_RE.match(line)
        if section:
            kind, names = section.groups()
            # `diff --git a/x b/x` names the file twice; its `+++` line names it once.
            if kind != "git":
                path = _git_unquoted(names)
            elif quoted := GIT_QUOTED_NAME_END_RE.search(names):
                path = _git_unquoted(quoted.group()).removeprefix("b/")
            else:
                path = names.rpartition(" b/")[2] if " b/" in names else None
            in_header = True
        elif in_header and line.startswith("@@"):
            in_header = False
        elif in_header and (new_name := GIT_DIFF_NEW_NAME_RE.match(line)):
            name = new_name.group(1)
            path = None if name == "/dev/null" else _git_unquoted(name).removeprefix("b/")
        elif not in_header and path and path not in files and GIT_DIFF_MARKER_RE.match(line):
            files.append(path)
    return files


def _git_unquoted(name: str) -> str:
    """`name` as git wrote it in a diff header, with git's C-style quoting
    undone; a name that is not in double quotes is returned unchanged. Octal
    escapes are the bytes of the name's UTF-8 spelling."""

    if len(name) < 2 or not (name.startswith('"') and name.endswith('"')):
        return name
    body, spelled, i = name[1:-1], bytearray(), 0
    while i < len(body):
        octal = body[i + 1:i + 4]
        if body[i] == "\\" and len(octal) == 3 and all(c in "01234567" for c in octal):
            spelled.append(int(octal, 8) & 0xFF)
            i += 4
        elif body[i] == "\\" and body[i + 1:i + 2] in GIT_NAME_ESCAPES:
            spelled.append(GIT_NAME_ESCAPES[body[i + 1]])
            i += 2
        else:
            spelled += body[i].encode("utf-8")
            i += 1
    return spelled.decode("utf-8", errors="replace")


def _design_hold(writes: dict[str, bool], write: Call | None, proof: _Proof,
                 project: Project | None,
                 references: Callable[[], tuple] | None,
                 landable: bool = False) -> Hold | None:
    """Hold a write of project files until its design is done (spec R5).
    `writes` maps each file the call writes to whether its write is small,
    adding fewer than `DESIGN_MIN_LINES` lines or a short comment-only edit
    (`_small_edit`).

    The `design` gate holds a turn's first substantial non-test code edit until
    `software-design-principles` loads and every reference the edit's signals
    select is read. The `design-reads` gate holds any later edit the
    design-reads rules apply to, once the skill is loaded, until the
    references it requires are read. `design_reads` says which those are; a
    test edit is judged by the registry's rule for test edits, from
    `references` (`_test_edit`). A load or a read counts until the next
    compaction; a skip line or the user's skip of the skill clears both gates.
    Once the skill counts as loaded, both gates ask only for reads, so a skip
    line that clears them lasts the task for those references on files of
    the same kind (spec R4, `_unexcused`), keyed as `design-reads`. A skip
    line that clears a `design` hold asking for the load lasts its turn.

    `write` is the call's file write, for its one file, or None for a
    shell write of new text (Ticket 098: `_shell_text_writes`),
    whose text the gates cannot read: it selects only what its path selects
    (a configuration file, the third code file), and a test file it writes
    selects nothing. One hold asks for what every file needs: `design` when
    any of them is the turn's first substantial code change.

    Once the skill counts as loaded, a `landable` write (`_may_land`) lands
    instead, owing its reads (`_lands`), whichever gate would hold it; a
    `design` hold asking for the load never lands.
    """

    if DESIGN_SKILL in proof.user_skips:
        return None
    loaded = proof.loaded(DESIGN_SKILL)
    earlier = _project_code_writes(proof.turn, project)
    judged, first, needs = False, False, []
    paths = list(writes)
    for path, small in writes.items():
        need = _design_need(path, write, small, loaded, earlier, project, references)
        if need is not None:
            judged, first = True, first or need[0]
            kind = file_kind(path, project)
            needs += [_Need(path, kind, DESIGN_SKILL, name, why) for name, why in need[1].items()
                      if name not in proof.references_read]
    if not judged:
        return None
    if loaded:
        needs = _unexcused(proof, "design-reads", needs,
                           lambda name: f"`{design_reads.SKILL_REFERENCES}{name}`")
    elif DESIGN_SKILL in proof.skips:
        return None
    unread: dict[str, str] = {}
    for need in needs:
        unread.setdefault(need.reference, need.detail)
    # Unloaded, every judged write is substantial and held; loaded, only one with unread references.
    if loaded and not unread:
        return None
    # Loaded, both gates ask only for reads, so a landable write owes them;
    # the two share their lasting skips, keyed as `design-reads`.
    if loaded and _lands(proof, "design-reads", needs, landable,
                         lambda name, why: f"`{design_reads.SKILL_REFERENCES}{name}` ({why})",
                         named="design" if first else "design-reads"):
        return None
    edit = "edit" if write is not None else "command"
    # A shell write may be scripted to keep a file's line endings (round 7, R6).
    not_done = "This edit was not applied." if write is not None else \
        f"{LINE_ENDINGS}This command was not run."
    if loaded and not first:
        names = _listed([f"\"{_file_name(p)}\"" for p in paths])
        return Hold(
            "design-reads", JUSTIFIED_SKIP,
            f"Read each design reference this {edit} of {names} needs {WHOLE_READ}, before "
            f"the {edit}, and apply it: {_reference_list(unread)}. None has been read since "
            f"the last compaction. If the {edit} has no design in it, "
            f"write `goated-skip: {DESIGN_SKILL}: <reason>` on its own line instead; it lasts "
            "the task for these references on files of the same kind. "
            f"{not_done} "
            + unseen_line_advice("skip line", f"skip {DESIGN_SKILL}"),
            _design_short(f"read {_reference_list(unread)} {WHOLE_READ} before this {edit} "
                          f"of {names}"),
        )
    steps = [] if loaded else [
        f"load `{DESIGN_SKILL}` with {SKILL_TOOL}{proof.within} and apply its 'Before "
        "changing code' rules before this substantial code change"
    ]
    if unread:
        which = "it" if steps else "this substantial code change"
        steps.append(f"read each reference {which} requires {WHOLE_READ}: "
                     f"{_reference_list(unread)}")
    asked = "; ".join(steps)
    return Hold(
        "design", JUSTIFIED_SKIP,
        f"{asked[0].upper()}{asked[1:]}. If the {edit} is "
        f"mechanical, with no design in it, write `goated-skip: {DESIGN_SKILL}: <reason>` on "
        f"its own line instead. {not_done} "
        + unseen_line_advice("skip line", f"skip {DESIGN_SKILL}"),
        _design_short("; ".join(steps)),
    )


def _design_need(path: str, write: Call | None, small: bool, loaded: bool,
                 earlier: list[tuple[str, bool]], project: Project | None,
                 references: Callable[[], tuple] | None) -> tuple[bool, dict[str, str]] | None:
    """What a write of `path` needs from the design gates, as `_design_hold`
    describes: whether it is the turn's first substantial code change, and
    the references its signals select, each with why; or None when neither
    gate judges it. `small`: it is too small for the design gates (`_small_edit`).
    `earlier` are the turn's project code writes so far."""

    code, test = is_code(path), is_test(path, project)
    test_data = design_reads.is_test_data_path(_path_in_project(path, project))
    if not design_reads.applies(path, is_code=code, is_test_data=test_data):
        return None
    shell_write = write is None
    # A test file is never substantial: in TDD the test comes first, and the
    # design happens in the code after it (Ticket 057).
    substantial = code and not test and not small
    if not loaded and not substantial:
        return None
    written_before = any(p == path for p, _ in earlier)
    if shell_write and test:
        required = {}
    else:
        required = design_reads.required(
            path, write, is_code=code, is_test=test, small=small,
            written_before=written_before,
            other_code_files=len({p for p, _ in earlier if p != path and not is_test(p, project)}),
            cwd=project.cwd if project else None,
            test_edit=_test_edit(path, write, project, references,
                                 written_before=written_before) if test else None,
            comment_on_little_code=write is not None and _comment_on_little_code(write),
        )
    first = substantial and not any(not s for p, s in earlier if not is_test(p, project))
    return first, required


def _design_short(unmet: str) -> str:
    """The short form of a design gate's hold, whose `unmet` steps its skip line answers too."""

    return short_form(unmet, f"Or write `goated-skip: {DESIGN_SKILL}: <reason>`. "
                      + short_advice("skip line", f"skip {DESIGN_SKILL}"))


def _test_edit(path: str, write: Call, project: Project | None,
               references: Callable[[], tuple] | None, *, written_before: bool) -> str | None:
    """Why an edit of test file `path` designs a test, so the design gates ask
    for `coding.md`, or None. The registry's rule for test edits decides
    (`reference_reads.file_kind_signal`), as it decides `tdd`'s
    `test-design.md` (spec R9). Without one, as with no registry, any edit
    that is not small does, failing toward holding."""

    signal = reference_reads.file_kind_signal(references() if references else (), "test")
    if signal is None:
        return None if _small_edit(write) else "edits a test file"
    cwd = project.cwd if project else None
    return reference_reads.fires(signal, reference_reads.Edit(
        is_code=True, is_test=True, added_code=design_reads.added_code(path, write, cwd),
        new_file=design_reads.creates_file(path, write, written_before=written_before, cwd=cwd),
    ))


def _reference_reads_hold(paths: list[str | None], write: Call | None, proof: _Proof,
                          project: Project | None, references: Callable[[], tuple] | None,
                          changes: Callable[[], "_Changes"],
                          landable: bool = False) -> Hold | None:
    """Hold a write until the skill references its signals select are read
    (registry reference reads spec, R5). `paths` are the project files one
    call writes, judged together so one hold asks for every reference any of
    them selects, or [None] for a write naming no project file, which only
    the turn's gate signals reach.

    Only references of a skill that counts as loaded and has no typed skip
    this turn are judged (`reference_reads.selected`), on what this
    write and the turn before it show: the code the write adds, read from
    `write` (None for a shell write, which adds no code the gate can
    read), where the file is in the project, whether the repeated-failure
    gate's condition holds, and, for a sensitive file, the security
    categories of the turn's `changes` with this one's. A reference counts as
    read after a finished whole read of it since the last compaction. With no
    `references`, or a registry that declares none, nothing is held. A skip
    line naming a reference's skill clears it, and lasts the task for that
    reference on files of the same kind (spec R4, `_unexcused`). A
    `landable` write (`_may_land`) lands instead, owing its reads (`_lands`).
    """

    declared = [r for r in references() if proof.loaded(r.skill)
                and r.skill not in proof.user_skips] if references else []
    if not declared:
        return None
    # `repeated-failure` is the one gate in `reference_reads.OBSERVED_GATES`.
    gates = frozenset({"repeated-failure"} if _repeated_check(proof.turn, project) else ())
    needs = []
    for path in paths:
        kind = file_kind(path, project) if path else None
        for reference, why in reference_reads.selected(
                declared, _reference_edit(path, write, proof, project, changes, gates)):
            if reference.path not in proof.skill_references_read:
                needs.append(_Need(path, kind, reference.skill, reference.path, (reference, why)))
    found: dict = {}  # Each reference still held for, with the first reason.
    held = _unexcused(proof, "reference-reads", needs, lambda path: f"`{path}`")
    for need in held:
        found.setdefault(need.reference, need.detail)
    if not found or _lands(proof, "reference-reads", held, landable,
                           lambda path, detail: f"`{path}` ({detail[1]})"):
        return None
    unread = list(found.values())
    skills = list(dict.fromkeys(r.skill for r, _ in unread))
    listing = ", ".join(f"`{r.path}` ({why})" for r, why in unread)
    skip_lines = " or ".join(f"`goated-skip: {skill}: <reason>`" for skill in skills)
    way_out = f"skip {skills[0]}" if len(skills) == 1 else "skip <skill>"
    names = [f"\"{_file_name(p)}\"" for p in paths if p]
    target = f" to {_listed(names)}" if names else ""
    return Hold(
        "reference-reads", JUSTIFIED_SKIP,
        f"Read each skill reference this write{target} needs {WHOLE_READ}, before the "
        f"write, and apply it: {listing}. None has been read since the last compaction; "
        "the GOATED registry declares when each is required. If one does not apply to "
        "this write, "
        f"write {skip_lines} on its own line instead, naming its skill; it lasts the task "
        "for these references on files of the same kind. This write was not "
        "applied. " + unseen_line_advice("skip line", way_out),
        short_form(f"read {listing} {WHOLE_READ}",
                   f"Or write {skip_lines}. " + short_advice("skip line", way_out)),
    )


def _reference_edit(path: str | None, write: Call | None, proof: _Proof,
                    project: Project | None, changes: Callable[[], "_Changes"],
                    gates: frozenset) -> reference_reads.Edit:
    """What the reference signals judge of one write to `path` (None: a
    write naming no project file), as `_reference_reads_hold` describes."""

    if path is None:
        return reference_reads.Edit(is_code=False, is_test=False, added_code=[], gates=gates)
    category, cwd = sensitive_category(path, project), project.cwd if project else None
    added = design_reads.added_lines(path, write, cwd)
    return reference_reads.Edit(
        is_code=is_code(path), is_test=is_test(path, project),
        added_code=added.code, in_strings=added.in_strings,
        project_paths=tuple(_paths_in_project(path, project)),
        gates=gates,
        categories=frozenset({category, *(c for _, c in changes().sensitive)})
        if category else frozenset(),
        new_file=write is not None and design_reads.creates_file(
            path, write, cwd=cwd,
            written_before=any(p == path for p, _ in _project_code_writes(proof.turn, project))),
    )


def _reference_list(references: dict[str, str]) -> str:
    """The references as the holds name them, in the given order. Each path is
    backticked like the closeout's red-flags path; a reader of hold texts
    takes only a bare backticked name as a skill (contract, Hold Text)."""

    return ", ".join(f"`{design_reads.SKILL_REFERENCES}{name}` ({why})" for name, why in references.items())


def _project_code_writes(turn: Turn, project: Project | None) -> list[tuple[str, bool]]:
    """Each finished write of a project code file in the turn that the design
    gates judge: an edit tool call, or a shell command's write of new text
    (`_shell_text_writes`). Each comes as its path and whether it is small
    (`_small_edit`)."""

    writes = []
    for call in turn.calls:
        if call.ok and call.kind == events.FILE_WRITE:
            path = _norm(call.path)
            if is_code(path) and _in_project(path, project):
                writes.append((path, _small_edit(call)))
        elif call.ok and call.kind == events.SHELL_COMMAND:
            command = shell.analyze(call.command, call.shell)
            if command.non_check_writes:
                writes += [(path, small) for path, small
                           in _shell_text_writes(command, project).items() if is_code(path)]
    return writes


def _shell_text_writes(command: shell.ShellCommand, project: Project | None) -> dict[str, bool]:
    """Each project file `command` puts new text into, as the design gates
    judge a shell write (Ticket 098), with whether that text is small: fewer
    than `DESIGN_MIN_LINES` lines shown in all, text it does not show counting
    as large. Two spellings of one file (`./src/a.py`, `src\\a.py`) are one
    file, whose writes add up. A file written from an unknown folder has no
    place, and a script's files are the `scripted-edit` gate's, so neither
    is here. Copies, moves, restores, and in-place edits add no text designed
    in the command, and a write naming no file names none to judge."""

    shown: dict[str, int | None] = {}
    for target, lines in command.text_writes:
        if (target in command.unplaced_targets or target in command.script_targets
                or not _in_project(target, project)):
            continue
        path = posixpath.normpath(_norm(target))
        before = shown.get(path, 0)
        shown[path] = None if before is None or lines is None else before + lines
    return {path: lines is not None and lines < DESIGN_MIN_LINES for path, lines in shown.items()}


def _shell_written_lines(command: shell.ShellCommand, judged: list[str]) -> int | None:
    """The lines of new text `command` shows it writes into `judged`, the
    write targets the read gates judge, in all, as those gates count a shell
    write to let it land (round 5, R5). Lines written anywhere else, such as
    a scratch file, do not count. None when they cannot be counted: it
    judges no named file, writes a file it does not name, writes text it
    does not show into a judged file, or changes one without new text (a
    copy, move, restore, or in-place edit), whose lines no command shows."""

    shown = [lines for target, lines in command.text_writes if target in judged]
    texted = {target for target, _ in command.text_writes}
    if (not judged or None in shown or command.unknown_writes
            or any(target not in texted for target in judged)):
        return None
    return sum(shown)


def _repeated_failure_hold(proof: _Proof, project: Project | None) -> Hold | None:
    """Hold a write once one check command has failed twice in a row in the
    turn (`_repeated_check`), until `diagnose` loads or is skipped."""

    if proof.loaded_or_skipped(DIAGNOSE_SKILL):
        return None
    repeated = _repeated_check(proof.turn, project)
    if repeated is None:
        return None
    shown = repeated if len(repeated) <= 80 else repeated[:77] + "..."
    return Hold(
        "repeated-failure", JUSTIFIED_SKIP,
        # The command is quoted, not backticked: backticks name a skill to load.
        f"Load `{DIAGNOSE_SKILL}` with {SKILL_TOOL}{proof.within} and find the root cause "
        f"before changing more: the check \"{shown.replace('`', chr(39))}\" has failed "
        f"{REPEATED_FAILURES} times in a row in this turn. If the cause is already known, write "
        f"`goated-skip: {DIAGNOSE_SKILL}: <reason>` on its own line instead. This write was "
        "not applied. Rerunning the check is not held, and a pass of it resets the count. "
        + unseen_line_advice("skip line", f"skip {DIAGNOSE_SKILL}"),
        _load_or_skip(DIAGNOSE_SKILL, "a check keeps failing in this turn"),
    )


def _repeated_check(turn: Turn, project: Project | None) -> str | None:
    """The check command that has failed `REPEATED_FAILURES` times in a row in
    `turn` with no pass since, as `_check_key` gives it, or None.

    "The same check" is the same command text, whitespace aside (spec G2),
    without a leading `cd` or a trailing pipe into output filters
    (`| tail -20`): a narrowed rerun, such as one test file of a failing
    suite, is another command. A pass of that check resets its count; other
    commands between runs do not. Only runs count: a call held, refused, or
    interrupted never ran.

    Some runs neither add to the count nor reset it (low-signal holds spec,
    R1): one whose only failures are test modules missing a module
    (`LOAD_ERROR_SIGNS`), failed or not, since a pipe can cut the failure
    signs from its output; a failed run that is the check's first since a
    finished write to a `project` test file, the red run TDD expects; and a
    failed run reporting fewer failures than the check's run before it
    (`_failure_count`), when both counts can be read.
    """

    cwd = project.cwd if project else None
    in_a_row: dict[str, int] = {}
    shown: dict[str, str] = {}
    is_check: dict[str, bool] = {}
    failures: dict[str, int | None] = {}  # Each check's failure count at its last run.
    test_writes = 0  # Finished writes to a test file so far in the turn.
    test_writes_seen: dict[str, int] = {}  # `test_writes` at each check's last run.
    for call in turn.calls:
        # A shell command's own test write comes after its run, never before.
        test_writes_before = test_writes
        test_writes += _writes_a_test(call, project)
        if call.kind != events.SHELL_COMMAND or not call.ran:
            continue
        command = call.command
        check = _check_key(command, cwd)
        key, piped = check.key, check.piped
        shown[key] = check.shown
        red_run = test_writes_seen.get(key, 0) < test_writes_before
        test_writes_seen[key] = test_writes_before
        load_errors = _load_errors(call.output)
        if load_errors == "missing-module":
            continue
        # A pipe's exit code is its last filter's, so a piped run fails by what it prints.
        failed = (
            bool(load_errors or FAILURE_SIGNS_RE.search(call.output)) if piped else not call.ok
        )
        count, earlier = _failure_count(call.output), failures.get(key)
        failures[key] = count
        if failed and (red_run or None not in (count, earlier) and count < earlier):
            continue  # The run TDD expects to fail, or a run that shows progress.
        if not failed and key not in in_a_row:
            continue  # A pass of a command that never failed changes nothing.
        if key not in is_check:
            is_check[key] = shell.analyze(command).is_check
        if is_check[key]:
            in_a_row[key] = in_a_row.get(key, 0) + 1 if failed else 0
    return next((shown[k] for k, n in in_a_row.items() if n >= REPEATED_FAILURES), None)


def _load_errors(output: str) -> str | None:
    """What a run's output says about test modules that failed to load.

    "missing-module" when it shows at least one, every one it shows was
    caused by a missing module or name, and no test that ran failed; "other"
    when it shows one for any other reason, or beside a real failure; None
    when it shows none. Output cut before a cause reads as "other".
    """

    found, lines = False, output.splitlines()
    for signs in LOAD_ERROR_SIGNS:
        starts = [i for i, line in enumerate(lines) if signs.start.match(line)]
        if not starts:
            continue
        found = True
        if signs.real_failure.search(output):
            return "other"
        for start in starts:
            end = next((i for i in range(start + 1, len(lines)) if signs.end.match(lines[i])),
                       len(lines))
            causes = list(LOAD_ERROR_CAUSE_RE.finditer("\n".join(lines[start + 1:end])))
            last = causes[-1] if causes else None
            if last is None or not (last["missing"] or last["exception"] in MISSING_MODULE_EXCEPTIONS):
                return "other"
    return "missing-module" if found else None


def _writes_a_test(call: Call, project: Project | None) -> bool:
    """Whether `call` is a finished write, by an edit tool or a shell command,
    to a file `is_test` places as a project test file."""

    if not call.ok or call.held:
        return False
    if call.kind == events.FILE_WRITE:
        targets = [call.path]
    elif call.kind == events.SHELL_COMMAND:
        command = shell.analyze(call.command, call.shell)
        targets = [t for t in command.write_targets if t not in command.unplaced_targets]
    else:
        return False
    return any(is_test(_norm(target), project) for target in targets)


def _failure_count(output: str) -> int | None:
    """How many tests failed or errored by the run summary in `output`, or
    None when that says nothing of the tests: it shows no summary
    `FAILURE_COUNT_SIGNS` reads, or more than one, such as two runners' in
    one command; it shows a test module or suite that could not load, whose
    tests are missing from the count; or it counts no failure, so the run
    failed outside the tests."""

    if (any(signs.start.search(output) for signs in LOAD_ERROR_SIGNS)
            or COLLECTION_INTERRUPTED_RE.search(output)):
        return None
    summaries = [(found[1], counted) for summary, counted in FAILURE_COUNT_SIGNS
                 for found in summary.finditer(output)]
    if len(summaries) != 1:
        return None
    text, counted = summaries[0]
    return sum(int(n) for n in counted.findall(text)) or None


class _CheckKey(NamedTuple):
    """A check command's identity (`key`), the command as a hold shows it
    (`shown`), and whether a trailing pipe into output filters was removed."""

    key: str
    shown: str
    piped: bool


def _check_key(command: str, cwd: str | None) -> _CheckKey:
    """Identify a check command run from the session folder `cwd`.

    The command is compared whitespace aside, without a trailing pipe into
    output filters or a leading `cd` to a folder (spec R2), which `shown`
    leaves out. The folder the `cd` reaches stays in `key`, so one command
    run in two folders is two checks, unless it is `cwd` itself: `cd <cwd>
    && pytest -q` is `pytest -q`. With no `cwd`, the folder is kept relative.
    """

    shown = " ".join(command.split())
    start = cwd or ""
    folder = start
    while found := LEADING_CD_RE.match(shown):
        folder = os.path.join(folder, found["dq"] or found["sq"] or found["bare"] or "")
        shown = shown[found.end():]
    bare = shown
    while (shorter := PIPE_TAIL_RE.sub("", bare)) != bare:
        bare = shorter
    piped = bare != shown
    shown = STDERR_MERGE_RE.sub("", bare) if piped else bare
    if folder == start or _folder_key(folder) == _folder_key(start):
        return _CheckKey(shown, shown, piped)
    return _CheckKey(f"cd {_folder_key(folder)} && {shown}", shown, piped)


def _folder_key(folder: str) -> str:
    """`folder` in comparable form: normalized, case-folded where the system
    folds case, with `/` separators."""

    return os.path.normcase(os.path.normpath(folder)).replace("\\", "/")


# Closeout ---------------------------------------------------------------------

# The closeout hold's gate name, in its `goated-hold:` line.
CLOSEOUT_GATE = "closeout"
# The items a commit ending a conflict does not ask for once `resolving-merge-conflicts`
# has loaded (round 6, R8): the resolution joins two sides already written. Reads,
# Proof, Unfinished and Setup, about what the resolution itself did, still apply.
CONFLICT_COMMIT_SPARED = frozenset({"Docs", "Design", "Security", "Review", "Verification"})

def check_closeout(turn: Turn, overrides: dict, namespaces: tuple[str, ...] = (),
                   final_text: str = "", subagents: dict | None = None,
                   project: Project | None = None,
                   at_commit: bool = False, by_tool: bool = False,
                   earlier: SinceCompaction = SinceCompaction(),
                   spawn_templates: dict[str, list[str]] | None = None,
                   intensity: str | None = None, briefed: bool = False,
                   owed_reads: dict[str, list[OwedRead]] | None = None,
                   task_skips: TaskSkips | None = None,
                   points: ReviewPoints | None = None) -> Hold | None:
    """Return the closeout hold for a turn about to end, if any; `at_commit`:
    for a commit the turn is about to make, which must meet it first, made by
    an MCP commit tool when `by_tool`, which has no command to rerun.

    A turn that changed code needs, after its last code change, a check
    command (proof), in a later call or later in the same shell command, not
    run in the background (`_checks`); a comment-only edit needs none. It
    also needs `doc-sync` when non-test code changed, `handoff` when the
    last check after the change failed (work left unfinished), and a read
    of the design red flags after the change when `_designing` says the
    Design item applies; after a red-flags read, design changes that add
    fewer than `DESIGN_MIN_LINES` lines in total need only a change read
    (`_red_flags_read`). A turn that changed a security-sensitive file,
    code or not, while `code-security-review` counts as loaded, needs a
    security review. A load counts until the next compaction (`earlier`).
    The doc-sync, design, and security items each also need a change read: doc-sync's after the last code change, the
    design item's after its red-flags read and the last code change that is
    not comment-only, and security's after the last sensitive change, before
    or after its load (Ticket 092). A turn
    that installed a package it names, or wrote an env or settings file, needs
    `setup-scribe` loaded at any point in the turn (Setup). Each item accepts
    a skip line; `final_text` is the reply being finished, which
    may not be in the transcript yet.

    `subagents` maps the agent id of each subagent this turn spawned to its
    turns. Their code changes count as made at the spawn; a subagent that ran
    a check after its own last change has already proved them. Only files
    inside `project` count (see `find_project`); a scratch file elsewhere does not.

    A turn that changed code on a branch whose work against its base is
    `REVIEW_MIN_LINES` or more (`changed_lines` with `WORKING_TREE`, asked
    only when the item is not already met) needs a review (spec R1);
    `spawn_templates` maps the tool_use_id of each spawn the `spawn` gate let
    through in this turn to the templates its brief followed
    (`brief_templates`), which names its reviewer subagents. A turn that
    changed code or a sensitive file needs `verification-before-completion`
    (spec R3) when `intensity`, the task's route intensity, is `full`, a
    subagent changed code, a sensitive file changed, or the branch is large.
    A `briefed` session, one whose first prompt was a brief from the session
    that started it, meets no Review item: that session reviews the work
    (spec R10). A doc changed after the last code change, with a change read
    after it, meets Docs with no load (round 6, R7). A commit that ends a
    conflict (`_Conflict.being_resolved`), with
    `resolving-merge-conflicts` loaded, is not asked for Docs, Design,
    Security, Review or Verification (`CONFLICT_COMMIT_SPARED`, round 6, R8).

    `owed_reads` maps the call id of each write of the turn that landed past
    a read gate to the reads it owes (`OwedRead`), which the Reads item asks
    for (`_reads_item`). `task_skips` are the task's lasting skips, which
    cover an owed read; a skip line meeting the item adds to its `cleared`.

    `points` are the task's review points (`ReviewPoints`): while branch size
    alone asks for Review or Verification, a point an earlier turn of the
    task recorded meets it until the branch has grown by
    `REVIEW_POINT_GROWTH` lines since (round 7, R1). Meeting or declining
    either item in this turn adds its point to `points.met`.
    """

    changes = _Changes(turn, subagents or {}, project)
    branch_size = functools.cache(
        lambda: changed_lines(project.cwd if project else None, None, WORKING_TREE))
    proof = _Proof(turn, overrides, namespaces, final_text, earlier, task_skips)
    items = _closeout_items(
        changes, proof, subagents or {}, spawn_templates or {}, intensity, briefed,
        branch_size, owed_reads, points or ReviewPoints())
    # A commit that ends a conflict the skill resolved asks for less (round 6, R8).
    if (at_commit and CONFLICT_SKILL in proof.loads
            and _open_conflict(turn, project).being_resolved):
        items = [item for item in items if item.label not in CONFLICT_COMMIT_SPARED]
    if not items:
        return None
    labels = [i.label for i in items]
    what = (
        "changed setup" if labels == ["Setup"]
        else "landed a write before its reads" if labels == ["Reads"]
        else "changed code" if changes.code
        else "changed a security-sensitive file" if changes.sensitive else "changed files"
    )
    when = "committing in" if at_commit else "finishing"
    rerun = (
        f"\n{CHAINED_STEPS} A check "
        "chained before the commit in the same command has not run yet, so it does not count."
    ) if at_commit and not by_tool else ""
    return _CloseoutHold(f"Before {when} this turn, which {what}:",
                         f"Still unmet before {when} this turn:", items, rerun)


def _closeout_items(changes: "_Changes", proof: _Proof, subagents: dict,
                    spawn_templates: dict[str, list[str]], intensity: str | None,
                    briefed: bool, branch_size: Callable[[], int | None],
                    owed_reads: dict[str, list[OwedRead]] | None = None,
                    points: ReviewPoints | None = None) -> list["_Item"]:
    """Every closeout item the turn `changes` and `proof` describe still
    needs, in the closeout's order (see `check_closeout`). Reads comes
    first: revising a landed write against its references may change what
    the other items judge."""

    points = points or ReviewPoints()
    reads = _reads_item(owed_reads or {}, changes, proof)
    items = [reads] if reads else []
    items += _code_items(changes, proof) if changes.code else []
    items += [] if briefed else _review_item(changes, proof, spawn_templates, branch_size,
                                             points)
    items += _verification_item(changes, proof, intensity, branch_size, points)
    sensitive = changes.sensitive
    if sensitive and SECURITY_SKILL in proof.loads and not proof.skipped(SECURITY_SKILL):
        last_sensitive = sensitive[-1][0]
        if not changes.read_after(last_sensitive):
            categories = ", ".join(dict.fromkeys(category for _, category in sensitive))
            skip = f"`goated-skip: {SECURITY_SKILL}: <reason>`"
            items.append(_Item(
                f"- Security: read the change itself after the last sensitive change and "
                f"review it, since a security-sensitive file changed ({categories}): "
                f"{CHANGE_READ}. Or, if it crosses no trust boundary, write {skip}.",
                f"- Security: read the change after the last sensitive change and review it, "
                f"or write {skip}."))
    setup_item = _setup_item(proof.turn, subagents, proof, changes.project)
    if setup_item:
        items.append(setup_item)
    return items


def closeout_note(turn: Turn, call: Call, overrides: dict, namespaces: tuple[str, ...] = (),
                  project: Project | None = None,
                  earlier: SinceCompaction = SinceCompaction(),
                  intensity: str | None = None,
                  owed_reads: dict[str, list[OwedRead]] | None = None,
                  task_skips: TaskSkips | None = None) -> "CloseoutNote":
    """The early closeout note (Ticket 096) for `call`, a finished file edit
    of the main agent in `turn`, with no text when it changed no project
    code file or the turn's closeout would ask for nothing yet. Its labels
    let the caller give a list once per task (round 7, R4).

    The note names, by their short forms, the items the closeout would ask
    for were the turn to end now, so they can be met before the report. It
    leaves out what it cannot tell cheaply: items only a git measure of the
    branch would bring (Review, a large branch's Verification) and the work
    of spawned subagents. `call` is added to `turn` when the transcript
    does not show it yet. `owed_reads` and `task_skips` are as
    `check_closeout` takes them, so the note names the Reads item too.
    """

    if not any(map(_is_code_change, _changed_paths(call, project))):
        return CloseoutNote()
    if not (call.id and any(c.id == call.id for c in turn.calls)):
        turn.calls.append(call)
    proof = _Proof(turn, overrides, namespaces, "", earlier, task_skips)
    items = _closeout_items(_Changes(turn, {}, project), proof, {}, {}, intensity,
                            briefed=False, branch_size=lambda: None, owed_reads=owed_reads)
    if not items:
        return CloseoutNote()
    labels = tuple(i.label for i in items)
    *rest, last = labels
    return CloseoutNote(
        "this turn changed code, so its closeout will ask for "
        + (f"{', '.join(rest)} and {last}" if rest else last)
        + ". Meet each after your last code change, since a later change asks again, "
        "and before your final report, so you report once:\n"
        + "\n".join(i.short for i in items), labels)


class CloseoutNote(NamedTuple):
    """The early closeout note's `text` ("" for none) and the `labels` of the
    items it names, in order."""

    text: str = ""
    labels: tuple[str, ...] = ()


class _Item(NamedTuple):
    """One closeout item: its `text`, and its `short` form for a later
    closeout hold in the turn that lists it again, which keeps the label,
    skill, skip line and every constraint needed to meet it."""

    text: str
    short: str

    @property
    def label(self) -> str:
        """The item's name, such as `Proof`, as its text gives it (`- Proof: ...`)."""

        return self.text[2:self.text.index(":")]


class _CloseoutHold(Hold):
    """The closeout hold, whose items each come short once the turn has
    shown that item in full (Ticket 095): at a commit or a `Stop`, an item
    the turn has not yet shown comes in full."""

    __slots__ = ("heading", "short_heading", "items", "rerun")

    def __init__(self, heading: str, short_heading: str, items: list[_Item], rerun: str) -> None:
        super().__init__(CLOSEOUT_GATE, JUSTIFIED_SKIP, f"{heading}\n"
                         + "\n".join(i.text for i in items) + f"\n{SKIP_LINE_RULE}" + rerun)
        self.heading, self.short_heading, self.items, self.rerun = (
            heading, short_heading, items, rerun)

    def text(self, claim: Callable[[str], bool]) -> str:
        """The full heading and skip-line rule while any item comes in full;
        each item full on its first showing in the turn, short after. The
        rerun rules of a commit command are always kept."""

        shown = [item.text if claim(ask_purpose(self.gate, item.short)) else item.short
                 for item in self.items]
        if all(text == item.short for text, item in zip(shown, self.items)):
            return f"{self.short_heading}\n" + "\n".join(shown) + self.rerun
        return f"{self.heading}\n" + "\n".join(shown) + f"\n{SKIP_LINE_RULE}" + self.rerun


def _reads_item(owed_reads: dict[str, list[OwedRead]], changes: "_Changes",
                proof: _Proof) -> _Item | None:
    """The Reads item (round 5, R5): what the turn's writes that landed past
    a read gate still owe, or None when nothing is owed. `owed_reads` maps
    each landed write's call id to what it owes; a write that did not
    finish owes nothing.

    Each reference is owed until it is read whole after its write, a person
    skipped its skill, or a lasting skip covers it for that kind of file. A
    skip line naming its skill meets it too, and lasts as a skip line
    clearing the gate would (`TaskSkips.cleared`). Once the references are
    read, each landed file needs a change read of itself, or a printed diff,
    after the last read of what it owes; a write naming no project file has
    no change to read. Owed reads end with the turn, as the other items'
    evidence does."""

    task, unread = proof.task_skips, {}
    # Each landed file whose references were read: the last such read, and their skills.
    last_reads: dict[str, int] = {}
    read_skills: dict[str, list[str]] = {}
    for index, call in enumerate(proof.turn.calls):
        if not (call.ok and call.id in owed_reads):
            continue
        for owed in owed_reads[call.id]:
            skip = LastingSkip(owed.gate, owed.skill, owed.kind, owed.reference)
            if owed.skill in proof.skips:
                if owed.kind:
                    task.cleared.append(skip)
                continue
            if owed.skill in proof.user_skips or (owed.kind and skip in task.kept):
                continue
            reference = _owed_reference(owed.gate, owed.reference)
            read = proof.read_index(reference, after=index)
            if read is None:
                unread.setdefault(reference, owed.skill)
            elif owed.path:
                last_reads[owed.path] = max(read, last_reads.get(owed.path, -1))
                read_skills.setdefault(owed.path, []).append(owed.skill)
    skip_lines = lambda skills: " or ".join(
        f"`goated-skip: {skill}: <reason>`" for skill in dict.fromkeys(skills))
    if unread:
        listed, skips = ", ".join(f"`{r}`" for r in unread), skip_lines(unread.values())
        return _Item(
            f"- Reads: read each {WHOLE_READ}: {listed}, since a write landed before the "
            f"references it needed were read. Then read the change itself and revise it "
            f"against them: {CHANGE_READ}. Or, if one does not apply, write {skips}.",
            f"- Reads: read {listed} whole, then the change, and revise it; or write {skips}.")
    unshown = [path for path, last in last_reads.items() if not changes.read_after(last, path)]
    if unshown:
        files = _listed([f'"{_file_name(path)}"' for path in unshown])
        skips = skip_lines(skill for path in unshown for skill in read_skills[path])
        return _Item(
            f"- Reads: read the change to {files} itself, after reading the references it "
            f"needed, and revise it against them: print its diff with a git diff or git show "
            f"command, or {READ} the file it wrote. Or write {skips}.",
            f"- Reads: read the change to {files} after the references and revise it, or "
            f"write {skips}.")
    return None


def _code_items(changes: "_Changes", proof: _Proof) -> list[_Item]:
    """The closeout items a code change needs: proof, a handoff for a failed
    check, doc-sync, and the design red flags, each with what is missing."""

    code = changes.code
    last = code[-1].index
    unproven = [c.index for c in code if not c.proven]
    items = []
    checks = _checks(proof.turn.calls[max(unproven, default=last) + 1 :])
    # Loading a verification skill is not proof; a check run, or a skip, is.
    if unproven and not checks and not proof.skipped(PROOF_SKILL):
        skip = f"`goated-skip: {PROOF_SKILL}: <reason>`"
        # A session waiting on another's result (round 4, R6), on the user, or on a
        # background check (round 5, R7) meets it with the same skip.
        waiting = f"`goated-skip: {PROOF_SKILL}: <what it waits for>`"
        items.append(_Item(
            "- Proof: run the relevant check in the foreground, since no test, lint, "
            "build, or check command ran in the foreground after the last code change. If "
            f"none can run, write {skip} and tell the user it is unverified. If you cannot check "
            "yet because you are waiting on another session's result, on the user, or on a "
            f"check running in the background, write {waiting}.",
            f"- Proof: run a check in the foreground after the last code change, or write "
            f"{skip}; when waiting on another session's result, on the user, or on a check "
            f"running in the background, {waiting}."))
    if checks and not checks[-1].ok and not proof.loaded_or_skipped(HANDOFF_SKILL):
        skip = f"`goated-skip: {HANDOFF_SKILL}: <reason>`"
        items.append(_Item(
            "- Unfinished: fix the failed check, since the last check after the change "
            f"failed; or load `{HANDOFF_SKILL}` and leave a handoff for what remains, or write "
            f"{skip}.",
            f"- Unfinished: fix the failed check, or load `{HANDOFF_SKILL}` and leave a "
            f"handoff, or write {skip}."))
    non_test = any(
        not is_test(path, changes.project) for change in code for path in change.code_paths
    )
    # A doc changed after the last code change, then read, meets Docs with no
    # load (round 6, R7); one changed only before it does not.
    later_docs = [index for index in changes.docs if index > last]
    synced = bool(later_docs) and changes.read_after(later_docs[-1])
    if non_test and not synced and not proof.skipped(DOC_SYNC_SKILL):
        loaded = proof.load_index(DOC_SYNC_SKILL)
        skip = f"`goated-skip: {DOC_SYNC_SKILL}: <reason>`"
        if loaded is None:
            items.append(_Item(
                f"- Docs: load `{DOC_SYNC_SKILL}`, then read the change itself and check "
                f"whether durable docs now drift, since code changed: {CHANGE_READ}. A doc you "
                "change "
                "after your last code change, with a change read after it, also meets this. "
                f"Or, if behavior and interfaces did not change, write {skip}.",
                f"- Docs: load `{DOC_SYNC_SKILL}` and read the change for docs drift, or "
                f"write {skip}."))
        elif not changes.read_after(last):
            # The skill is loaded, so it is named only in the skip line: no load answers this.
            # A read before the load counts (Ticket 059): the load adds nothing to see.
            items.append(_Item(
                f"- Docs: read the change itself after your last code change and check "
                f"whether durable docs now drift: {CHANGE_READ}. Or write {skip}.",
                f"- Docs: read the change after your last code change for docs drift, or "
                f"write {skip}."))
    counted = any(not c.short_comment for c in code)
    if counted and _designing(proof, changes.project) and not proof.skipped(DESIGN_SKILL):
        # Fixing a comment the red-flags scan found needs no second scan (Ticket 059).
        designed = [c for c in code if not c.comment_only]
        flags = _red_flags_read(proof, designed)
        skip = f"`goated-skip: {DESIGN_SKILL}: <reason>`"
        if flags is None:
            items.append(_Item(
                f"- Design: read `{RED_FLAGS_REFERENCE}` {WHOLE_READ}, after your last "
                f"code change (an edit of comments only aside), then read the change itself "
                f"and scan it against them: {CHANGE_READ}. Then answer their closing "
                f"question: {RED_FLAGS_QUESTION} Or write {skip}.",
                f"- Design: read `{RED_FLAGS_REFERENCE}` whole after your last code change, "
                f"then the change itself, and answer: {RED_FLAGS_QUESTION} Or write {skip}."))
        elif not changes.read_after(max([flags, *(c.index for c in designed)])):
            items.append(_Item(
                "- Design: read the change itself after reading the red flags and after your "
                "last code change, and scan it against them, not your memory of it: "
                f"{CHANGE_READ}. Then answer their closing question: {RED_FLAGS_QUESTION} "
                f"Or write {skip}.",
                "- Design: read the change after the red flags and your last code change, "
                f"and answer: {RED_FLAGS_QUESTION} Or write {skip}."))
    return items


def _review_item(changes: "_Changes", proof: _Proof, spawn_templates: dict[str, list[str]],
                 branch_size: Callable[[], int | None], points: ReviewPoints) -> list[_Item]:
    """The Review item for a turn that changed code (spec R1), or [] when the
    branch's work is not large, cannot be measured, or the item is met: by a
    reviewer subagent started after the last code change that has finished
    (one started in the background once its completion arrived in the turn),
    by the skill loaded and a change read after that change, before or after
    the load (Ticket 092), or by a skip line, each of which records the
    task's review point; or by an earlier turn's point while the branch has
    grown by fewer than `REVIEW_POINT_GROWTH` lines since it (round 7, R1).
    A turn that changed no code asks for nothing, but records the point when
    one of those meets the item in it, with any change read counting."""

    last = changes.code[-1].index if changes.code else -1
    loaded = proof.load_index(REVIEW_SKILL)
    if (proof.skipped(REVIEW_SKILL)
            or any(index > last and _reviewer_returned(call, proof, spawn_templates)
                   for index, call in enumerate(proof.turn.calls))
            or (loaded is not None and changes.read_after(last))):
        points.record("Review", branch_size())
        return []
    if not changes.code:
        return []
    size = branch_size()
    if size is None or size < REVIEW_MIN_LINES or points.covers("Review", size):
        return []
    # The template is named by its path: a reader of hold texts takes a bare
    # backticked name as a skill the item asks for, and this item's skill is the
    # review skill.
    reviewer = (
        "Or, after your last code change, start a reviewer subagent briefed from "
        f"`{contracts.REVIEWER_TEMPLATE.reference}`, the reviewer prompt; a brief from any "
        "other template is not a review."
    )
    size_text = (
        f"this branch's work is {size} changed lines of non-test code against its base, "
        f"{REVIEW_MIN_LINES} or more, counting committed, staged, unstaged, and untracked files "
        "that git does not ignore"
    )
    skip_line = f"`goated-skip: {REVIEW_SKILL}: <reason>`"
    skip = (f"Or, if size is not what makes it worth reviewing, such as generated or vendored "
            f"files, write {skip_line}.")
    short_tail = (f"or start a reviewer subagent briefed from "
                  f"`{contracts.REVIEWER_TEMPLATE.reference}`, or write {skip_line}.")
    if loaded is None:
        return [_Item(f"- Review: load `{REVIEW_SKILL}`, then read the change itself and "
                      f"review it, since {size_text}: {CHANGE_READ}. {reviewer} {skip}",
                      f"- Review: load `{REVIEW_SKILL}` and review the change, {short_tail}")]
    # The skill is loaded, so it is named only in the skip line: no load answers this.
    return [_Item(f"- Review: read the change itself after your last code change and review "
                  f"it, since {size_text}: {CHANGE_READ}. {reviewer} {skip}",
                  f"- Review: read the change after your last code change and review it, "
                  f"{short_tail}")]


def _verification_item(changes: "_Changes", proof: _Proof, intensity: str | None,
                       branch_size: Callable[[], int | None],
                       points: ReviewPoints) -> list[_Item]:
    """The Verification item (spec R3) for a turn that changed code or a
    sensitive file, or [] when no trigger holds or the item is met. Its skip
    line is the Proof item's too.

    A load of `verification-before-completion` in this turn, or a skip line,
    records the task's verification point, in any turn. When the route, a
    subagent's code, or a sensitive file asks for the item, a load that
    counts as loaded meets it, as before. When only branch size does, the
    turn's own load or skip meets it, or an earlier turn's point while the
    branch has grown by fewer than `REVIEW_POINT_GROWTH` lines since it
    (round 7, R1). `branch_size` runs only when it records a point or no
    other trigger holds."""

    this_turn = PROOF_SKILL in proof.turn_loads or proof.skipped(PROOF_SKILL)
    if this_turn:
        points.record("Verification", branch_size())
    if not (changes.code or changes.sensitive):
        return []
    triggers = []
    if intensity == FULL_ROUTE:
        triggers.append(f"the task's route is {FULL_ROUTE}")
    if any(change.by_subagent for change in changes.code):
        triggers.append("a subagent changed code")
    if changes.sensitive:
        triggers.append("a security-sensitive file changed")
    if triggers and proof.loaded_or_skipped(PROOF_SKILL):
        return []
    if not triggers:
        if this_turn:
            return []
        size = branch_size()
        if size is None or size < REVIEW_MIN_LINES or points.covers("Verification", size):
            return []
        triggers.append(
            f"this branch's work is {size} changed lines of non-test code against its base")
    skip = f"`goated-skip: {PROOF_SKILL}: <reason>`"
    return [_Item(
        f"- Verification: load `{PROOF_SKILL}` and follow it to verify the work before "
        f"claiming it is done, since {', and '.join(triggers)}. Or write {skip}, which also "
        "answers the proof item.",
        f"- Verification: load `{PROOF_SKILL}` and follow it, since "
        f"{', and '.join(triggers)}; or write {skip}.")]


def _designing(proof: _Proof, project: Project | None) -> bool:
    """Whether the turn's Design items apply: it loaded
    `software-design-principles`, or, with the skill loaded in an earlier
    turn, it made an edit the `design` gate triggers on (spec R3), so a later
    turn of small edits, short comment-only ones included, meets no Design
    item. `_code_items` also asks for none when every code change is a short
    comment-only edit."""

    if DESIGN_SKILL in proof.turn_loads:
        return True
    return DESIGN_SKILL in proof.loads and any(
        not small and not is_test(path, project)
        for path, small in _project_code_writes(proof.turn, project)
    )


def _red_flags_read(proof: _Proof, designed: list["_Change"]) -> int | None:
    """Where the red-flags read that covers the turn's `designed` changes, the
    code changes that are not comment-only, is in its calls, or None: the
    first read after the last of them, or else the turn's last read before
    it when the changes after that read add fewer than `DESIGN_MIN_LINES`
    lines in total and those before it add at least that many, so the read
    scanned a designed change (spec R8). The changes after the read are
    counted as `new_lines` counts them, so unchanged context sent with a
    follow-up does not count (round 6, R6); those it scanned keep
    `added_lines`, context included. A change whose added lines are
    unknown, a shell write or a subagent's, counts as large."""

    last = max((c.index for c in designed), default=-1)
    after = proof.read_index(RED_FLAGS_REFERENCE, after=last)
    if after is not None:
        return after
    before = proof.last_read_index(RED_FLAGS_REFERENCE, before=last)
    if before is None:
        return None
    scanned = [c.added_lines for c in designed if c.index < before]
    since = [c.new_lines for c in designed if c.index > before]
    if not _large(scanned) or _large(since):
        return None
    return before


def _large(added_lines: list[int | None]) -> bool:
    """Whether changes adding `added_lines` add `DESIGN_MIN_LINES` or more in
    total; a change whose count is unknown (None) makes them large."""

    return None in added_lines or sum(added_lines) >= DESIGN_MIN_LINES


def _setup_item(turn: Turn, subagents: dict, proof: _Proof,
                project: Project | None) -> _Item | None:
    """The Setup item, or None when the turn changed no setup or met it.

    The turn's own `setup-scribe` load or skip line meets every setup change,
    its subagents' included; a subagent's own load or skip line meets only the
    changes that subagent made, as its own check proves its own code.
    """

    if proof.loaded_or_skipped(SETUP_SKILL):
        return None
    calls = list(turn.calls) + [
        call for sub_turns in subagents.values() if not _setup_met(sub_turns, proof.namespaces)
        for sub_turn in sub_turns for call in sub_turn.calls
    ]
    setup = _setup_changes(calls, project)
    if not setup:
        return None
    skip = f"`goated-skip: {SETUP_SKILL}: <reason>`"
    return _Item(
        f"- Setup: load `{SETUP_SKILL}` and record the setup so it can be repeated, since "
        f"this turn {setup}; or, if it leaves nothing to record, write {skip}.",
        f"- Setup: load `{SETUP_SKILL}` and record the setup, or write {skip}.")


def _setup_met(sub_turns: list[Turn], namespaces: tuple[str, ...]) -> bool:
    """True when a subagent loaded `setup-scribe` or wrote a skip line naming it."""

    return any(
        goated_skill_name(raw, namespaces) == SETUP_SKILL for t in sub_turns for raw in t.loads
    ) or any(skip["skill"] == SETUP_SKILL for t in sub_turns for skip in t.skips)


def _setup_changes(calls, project: Project | None) -> str:
    """What setup the finished `calls` changed, as a phrase for the Setup item
    ('installed a package', 'wrote ".env"'), or "".

    A setup file counts only inside `project` (see `_in_project`), so a
    scratch folder's settings do not. So does a package install, unless it is
    a global or machine install, which counts wherever it ran (spec R14); one
    run from a folder the command left unknown counts.
    """

    installed, files = False, []
    for call in calls:
        if not call.ok:
            continue
        if call.kind == events.FILE_WRITE:
            targets = [] if _env_comments_only(call) else [call.path]
            unplaced = []
        elif call.kind == events.SHELL_COMMAND:
            command = shell.analyze(call.command, call.shell)
            installed = installed or command.installs_globally or any(
                folder is None or _in_project(folder or ".", project)
                for folder in command.install_folders)
            targets, unplaced = command.write_targets, command.unplaced_targets
        else:
            continue
        for target in targets:
            name = _norm(target).rsplit("/", 1)[-1]
            if (SETUP_FILE_RE.search(_norm(target)) and name not in files
                    and _in_project(target, project, target not in unplaced)):
                files.append(name)
    # Names are quoted, not backticked: a reader of hold texts takes a backticked
    # name as a skill.
    done = (["installed a package"] if installed else []) + (
        ["wrote " + ", ".join(f'"{name}"' for name in files)] if files else []
    )
    return " and ".join(done)


def _env_comments_only(write: Call) -> bool:
    """True when `write`, a file write of an example env file
    (`EXAMPLE_ENV_FILES`), adds, removes or edits only comment lines, which
    open with `#` past any spaces, and blank lines: each edit's replaced text
    holds the same other lines, trailing space aside, as the text it writes.
    A whole-file write, a write with no edits, or an edit whose text is not
    shown may change a setting, so it is not."""

    if _file_name(_norm(write.path).lower()) not in EXAMPLE_ENV_FILES:
        return False
    if write.whole_file or not write.edits:
        return False

    def settings(text: str) -> list[str]:
        return [line.rstrip() for line in text.split("\n")
                if line.strip() and not line.lstrip().startswith("#")]

    return all(removed is not None and added is not None and settings(removed) == settings(added)
               for removed, added in write.edits)


class _Change:
    """A finished call that changed files: where in the turn (`index`), which
    project files (`paths`), and which of them are code (`code_paths`).

    `proven` says it is already proved: by a check later in the same
    command, by a subagent's own check, or by changing only comments.
    `comment_only` says it is an edit that changed only comments and
    docstrings (`design_reads.comment_only`). `by_subagent` says a spawned
    subagent made it. `added_lines` is how many lines an edit tool call
    added (`countable_lines`), None when unknown; `new_lines` how many of
    them its removed text did not hold (`new_lines`), None when unknown."""

    __slots__ = ("index", "paths", "code_paths", "proven", "comment_only", "by_subagent",
                 "added_lines", "new_lines")

    def __init__(self, index: int, paths: list[str], proven: bool = False,
                 comment_only: bool = False, by_subagent: bool = False,
                 added_lines: int | None = None, new_lines: int | None = None) -> None:
        self.index = index
        self.paths = paths
        self.code_paths = [p for p in paths if _is_code_change(p)]
        self.proven = proven
        self.comment_only = comment_only
        self.by_subagent = by_subagent
        self.added_lines = added_lines
        self.new_lines = new_lines

    @property
    def short_comment(self) -> bool:
        """Whether it is a short comment-only edit, which the Design item does
        not count (`_short_comment_edit`)."""

        return _short_comment_edit(self.added_lines, lambda: self.comment_only)


class _Changes:
    """What one turn changed, and whether a later call read the change.

    `code` lists the changes to code, in order; `sensitive` lists each change
    to a security-sensitive file as (call index, category), in order;
    `last_change` is the call index of the last change to any project file,
    or -1; `last_material` that of the last change to code that is not a
    comment-only edit, or to a security-sensitive file, or -1, which a
    commit's change read must follow (spec R5); `docs` the call indexes of changes to a documentation file
    (`is_doc`), in order; `paths` are the changed files a Read can name. Changes a spawned
    subagent made count as made at its spawn.
    """

    def __init__(self, turn: Turn, subagents: dict, project: Project | None) -> None:
        self.turn = turn
        self.project = project
        changes = list(_changes(turn, subagents, project))
        self.code = [c for c in changes if c.code_paths]
        self.sensitive = [
            (c.index, category) for c in changes for path in c.paths
            if (category := sensitive_category(path, project)) is not None
        ]
        self.last_change = changes[-1].index if changes else -1
        self.last_material = max(
            [c.index for c in self.code if not c.comment_only]
            + [index for index, _ in self.sensitive], default=-1)
        self.docs = [c.index for c in changes if any(is_doc(p, project) for p in c.paths)]
        self.paths = [p for c in changes for p in c.paths if p != UNNAMED_FILES]

    def read_after(self, after: int, path: str | None = None) -> bool:
        """True when a finished call after call `after` printed the diff or read
        a file the turn changed, or, given `path`, read that file; the caller
        picks the change it must follow."""

        paths = [path] if path else self.paths
        return any(
            index > after and call.ok and self._shows_change(call, paths)
            for index, call in enumerate(self.turn.calls)
        )

    @staticmethod
    def _shows_change(call, paths: list[str]) -> bool:
        if call.kind == events.SHELL_COMMAND:
            return shell.analyze(call.command).prints_changes
        if call.kind == events.FILE_READ:
            return any(_same_file(call.path, path) for path in paths)
        return False


# Stands for files a shell write changed without naming them (`git apply`).
UNNAMED_FILES = "<files the command does not name>"


def _is_code_change(path: str) -> bool:
    return path == UNNAMED_FILES or is_code(path)


def _changes(turn: Turn, subagents: dict, project: Project | None):
    """Yield a `_Change` for each finished call that changed project files, in order."""

    for index, call in enumerate(turn.calls):
        if call.ok and call.agent_id in subagents and call.kind == events.SPAWN:
            calls = [c for sub_turn in subagents[call.agent_id] for c in sub_turn.calls]
            changed = [_changed_paths(c, project) for c in calls]
            if any(changed):
                code = [i for i, paths in enumerate(changed) if any(map(_is_code_change, paths))]
                # As for the main agent, a comment-only edit needs no check after it.
                unproven = [i for i in code if not (
                    calls[i].kind == events.FILE_WRITE
                    and design_reads.comment_only(calls[i].path, calls[i]))]
                proven = bool(code) and (
                    not unproven or _proves_itself(calls[unproven[-1]], project)
                    or bool(_checks(calls[unproven[-1] + 1 :]))
                )
                yield _Change(index, [p for paths in changed for p in paths], proven,
                              by_subagent=True)
            continue
        paths = _changed_paths(call, project)
        if paths:
            edited = call.kind == events.FILE_WRITE
            comment_only = edited and design_reads.comment_only(call.path, call)
            # Comments do not run, so a comment-only edit is already proved (Ticket 116).
            yield _Change(index, paths, comment_only or _proves_itself(call, project),
                          comment_only,
                          added_lines=countable_lines(call) if edited else None,
                          new_lines=new_lines(call) if edited else None)


def _changed_paths(call, project: Project | None) -> list[str]:
    """The project files one finished call changed; only real write targets count."""

    if not call.ok:
        return []
    if call.kind == events.FILE_WRITE:
        targets = [call.path]
        unnamed, unplaced = False, []
    elif call.kind == events.SHELL_COMMAND:
        command = shell.analyze(call.command, call.shell)
        targets, unnamed = command.write_targets, command.unknown_writes
        unplaced = command.unplaced_targets
    else:
        return []
    paths = [_norm(t) for t in targets if t and _in_project(t, project, t not in unplaced)]
    return paths + ([UNNAMED_FILES] if unnamed else [])


class Project(NamedTuple):
    """Where the project is: `roots`, the folders whose files count as the
    project's, in comparable form, `cwd`, the session's folder as the
    harness names it, which relative paths start from, and `homes`, the
    folders a leading `~` names, or None to read it from this process's
    environment (see `_readings`)."""

    roots: tuple[str, ...]
    cwd: str
    homes: tuple[str, ...] | None = None


def find_project(cwd: str | None, *project_dirs: str | None,
                 homes: tuple[str, ...] | None = None) -> Project | None:
    """Return the project for the session's working folder `cwd`, or None,
    when every file counts as inside: `cwd` is missing, or a folder below
    cannot be read for certain.

    A file is outside only when it is outside every root, so each candidate
    root is one: each of `project_dirs` (the project's folders, as the
    harness names them; None for one it does not), `cwd`, each in every
    reading it could have (see `_readings`), and the nearest folder at or
    above each that holds a `.git` entry. So a session that changed folder
    below its checkout still has the whole checkout. `homes` are the
    folders a leading `~` names, as `Project.homes` says.
    """

    if not cwd:
        return None
    roots: list[str] = []
    for folder in filter(None, (*project_dirs, cwd)):
        readings = _readings(folder, drives=(), homes=homes)
        if readings is None:
            return None
        roots += readings
    roots += [top for top in map(_git_top, roots) if top]
    return Project(tuple(dict.fromkeys(roots)), cwd, homes)


def _git_top(folder: str) -> str | None:
    while True:
        if os.path.exists(os.path.join(folder, ".git")):
            return folder
        parent = os.path.dirname(folder)
        if parent == folder:
            return None
        folder = parent


def _in_project(path: str, project: Project | None, placed: bool = True) -> bool:
    """True unless `path` is certainly outside the project: when in doubt, inside.

    With no project, every path is inside, and so is a relative path that is
    not `placed` (a shell wrote it from a folder the command left unknown).
    A relative path is taken from the session's folder. A path is outside
    only when none of its readings (see `_readings`) is a root or under one,
    even with symbolic links and junctions resolved in both; a path with no
    certain reading is inside. Touches the disk only to expand Windows 8.3
    short names and, for a path that looks outside, to resolve links.
    """

    if project is None or not placed:
        return True
    readings = _project_readings(path, project)
    if readings is None or _under_any(readings, project.roots):
        return True
    # A link may lead into the project from outside it, or out of a root.
    return _under_any(_resolved(readings), _resolved(project.roots))


def reads_as_in_project(path: str, project: Project | None) -> bool:
    """True when `path`, as a call wrote it, reads as under one of
    `project`'s roots by its text alone, a relative path taken from the
    session's folder, or when no project is known. Unlike `_in_project` it
    resolves no link and expands no `~` or Git Bash mount, so a path only
    those would place inside reads as outside; it reads the disk only to
    expand a Windows short name (`PROGRA~1`), as the roots are."""

    if project is None:
        return True
    full = path if os.path.isabs(path) else os.path.join(project.cwd, path)
    return _under_any([_comparable(full)], project.roots)


def writes_only_scratch(call: Call, project: Project | None, agent_folders: list[str]) -> bool:
    """True for a write that touches only scratch files, so the routing gates
    let it through: every file it writes is outside the project (see
    `_in_project`), inside no git checkout, outside the agent's own
    configuration folders (`agent_folders`, each absolute or under `~`), and
    holds no project folder; when any of that cannot be checked, the file
    does not count as outside.

    The write is a file write's file, or a shell command made only of plain
    reads and writes whose files it names (see
    `shell.ShellCommand.only_reads_and_writes_files`), with at least one
    write. Any other call is not such a write.
    """

    if project is None:
        return False
    if call.kind == events.FILE_WRITE:
        targets, unplaced = [call.path], []
    elif call.kind == events.SHELL_COMMAND:
        command = shell.analyze(call.command, call.shell)
        if not command.only_reads_and_writes_files:
            return False
        targets, unplaced = command.write_targets, command.unplaced_targets
    else:
        return False
    agents: list[str] = []
    for folder in agent_folders:
        # A folder under `~` is read as a shell would; any other is taken as
        # written, since the harness named it and no shell expands it.
        readings = (_readings(folder, (), project.homes) if folder.startswith("~")
                    else [_comparable(folder)])
        if readings is None:
            return False
        agents += readings
    agents += _resolved(agents)
    return bool(targets) and all(
        target and _scratch(target, project, target not in unplaced, agents) for target in targets
    )


def _scratch(path: str, project: Project, placed: bool, agents: list[str]) -> bool:
    """Whether `path` is certainly a scratch file: see `writes_only_scratch`."""

    if _in_project(path, project, placed):
        return False
    readings = _project_readings(path, project)
    if readings is None:
        return False
    every = readings + _resolved(readings)
    roots = [*project.roots, *_resolved(project.roots)]
    if _under_any(roots, every) or _under_any(every, agents):
        return False
    return not any(_in_checkout(reading) is not False for reading in every)


def _in_checkout(path: str) -> bool | None:
    """Whether `path`, or a folder above it, holds a `.git` entry (a file in
    a worktree, a folder in a clone); None when a folder cannot be checked."""

    folder = path
    while True:
        try:
            os.lstat(os.path.join(folder, ".git"))
            return True
        except (FileNotFoundError, NotADirectoryError):
            pass
        except OSError:
            return None
        parent = os.path.dirname(folder)
        if parent == folder:
            return False
        folder = parent


def is_test(path: str, project: Project | None) -> bool:
    """Whether `path` is a test file, judged by its path inside the project
    (`design_reads.is_test_path`), so folders above the project do not count.
    A file whose place in the project is unknown is not a test file."""

    return design_reads.is_test_path(_path_in_project(path, project))


def _path_in_project(path: str, project: Project | None) -> str | None:
    """`path` below the outermost project root holding it, with `/` separators
    and in comparable form, or None: no project, no certain reading, or
    outside every root. A path reached only through a link is outside."""

    inside = _paths_in_project(path, project)
    return max(inside, key=len) if inside else None


def _paths_in_project(path: str, project: Project | None) -> list[str]:
    """`path` below each project root holding it, with `/` separators and in
    comparable form; empty for no project, no certain reading, or outside
    every root. A path reached only through a link is outside."""

    readings = _project_readings(path, project) if project else None
    return [
        full[len(root.rstrip(os.sep)) + 1:].replace(os.sep, "/")
        for full in readings or () for root in project.roots
        if full.startswith(root.rstrip(os.sep) + os.sep)
    ]


def _project_readings(path: str, project: Project) -> list[str] | None:
    """`_readings` of `path`, a relative one taken from the session's folder."""

    rooted = path.startswith(("/", "\\", "~")) or (os.name == "nt" and DRIVE_RE.match(path))
    if not rooted:
        path = project.cwd.rstrip("/\\") + "/" + path
    return _readings(path, {os.path.splitdrive(root)[0] for root in project.roots},
                     project.homes)


def _under_any(paths, roots) -> bool:
    return any(
        full == root or full.startswith(root.rstrip(os.sep) + os.sep)
        for full in paths for root in roots
    )


def _resolved(paths) -> list[str]:
    return [os.path.normcase(os.path.realpath(path)) for path in paths]


DRIVE_RE = re.compile(r"^[A-Za-z]:")
ABSOLUTE_WINDOWS_RE = re.compile(r"^[A-Za-z]:[\\/]")
# Git Bash names a Windows drive as a one-letter top folder: `/c/Users` is `C:/Users`.
GIT_BASH_DRIVE_RE = re.compile(r"^/([A-Za-z])(?=/|$)")
# Characters a shell or Windows expands, so a path holding one names no file for certain.
EXPANDED_CHARS = frozenset("$`%*?")


def _readings(path: str, drives, homes: tuple[str, ...] | None = None) -> list[str] | None:
    """Every file absolute `path` may name, in comparable form, or None when
    it cannot be read for certain.

    None for a path a shell expands (a variable, a glob), one under `~-`,
    `~+`, or another user's `~name`, and the Windows forms this does not
    normalize: device paths (`\\\\?\\`, `//?/`, `\\\\.\\`), network paths, a
    drive-relative `C:x`, and a name ending in a dot or space. A leading `~`
    is each of `homes`, the homes the harness names; with None, the user's
    home as this process sees it, read as both the profile folder and `HOME`.

    On Windows, a path rooted with no drive is None unless Git Bash reads it
    for certain (see `_git_bash_mounts`). Such a path may also be a folder on
    any of `drives` or the process's own drive, so those are readings too.
    """

    if any(ch in EXPANDED_CHARS for ch in path):
        return None
    if path.startswith("~"):
        if path != "~" and path[1] not in "/\\":
            return None
        if homes is None:
            # `HOME`, which Git Bash sets, may differ from the profile folder Python reads.
            home = os.environ.get("HOME") or ""
            homes = (os.path.expanduser("~"), home or os.path.expanduser("~"))
        if not homes or any(home.startswith("~") for home in homes):
            return None
        each = [_readings(home + path[1:], drives) for home in sorted(set(homes))]
        return None if None in each else [r for readings in each for r in readings]
    slashed = path.replace("\\", "/")
    if slashed.startswith("//"):
        return None
    readings = [path]
    if os.name == "nt":
        if DRIVE_RE.match(slashed) and slashed[2:3] != "/":
            return None
        if any(part.endswith((".", " ")) and part not in (".", "..")
               for part in slashed.split("/")):
            return None  # Windows drops a name's trailing dots and spaces, not always alike.
        if slashed.startswith("/"):
            mounted = _git_bash_mounts(slashed)
            if not mounted:
                return None
            on_drives = set(drives) | {os.path.splitdrive(os.getcwd())[0]}
            readings = [d + slashed for d in sorted(on_drives)] + mounted
    return [_comparable(reading) for reading in readings]


def _git_bash_mounts(slashed: str) -> list[str]:
    """The Windows paths Git Bash may read rooted `slashed` as, or [] when
    that is not certain.

    `/c/x` is `C:/x` when drive C exists. `/tmp/x` is `x` in the user's temp
    folder, which Git Bash mounts on `/tmp`; Windows takes that folder from
    `TMP` or else `TEMP`, so each that is set is a reading, and both must
    be absolute Windows paths. Git Bash also mounts `/` on its install folder,
    and a user may add mounts, so no other rooted path is certain.
    """

    drive = GIT_BASH_DRIVE_RE.match(slashed)
    if drive:
        root = drive.group(1).upper() + ":"
        return [root + (slashed[2:] or "/")] if os.path.exists(root + "/") else []
    if slashed != "/tmp" and not slashed.startswith("/tmp/"):
        return []
    temps = [value for value in map(os.environ.get, ("TMP", "TEMP")) if value]
    if not temps or not all(
        ABSOLUTE_WINDOWS_RE.match(t) and not any(ch in EXPANDED_CHARS for ch in t) for t in temps
    ):
        return []
    return [t.rstrip("/\\") + slashed[len("/tmp"):] for t in temps]


def _comparable(path: str) -> str:
    return os.path.normcase(_long_path(os.path.abspath(path)))


def _long_path(path: str) -> str:
    """On Windows, absolute `path` with its 8.3 short names (`PROGRA~1`)
    expanded, as far as its folders exist; elsewhere, or with no `~`, as is."""

    if os.name != "nt" or "~" not in path:
        return path
    import ctypes  # Only Windows short names need it; most hook calls never get here.

    buffer = ctypes.create_unicode_buffer(32768)
    head, missing = path, []
    while True:
        if ctypes.windll.kernel32.GetLongPathNameW(head, buffer, len(buffer)):
            return os.path.join(buffer.value, *reversed(missing))
        parent, name = os.path.split(head)
        if not name or parent == head:
            return path  # No part of it exists, so nothing can be expanded.
        missing.append(name)
        head = parent


def _proves_itself(call, project: Project | None) -> bool:
    """True when a shell call ran a check after each code file it wrote in
    the project (see `ShellCommand.unchecked_targets`).

    The call's result stands for the whole command, so a check that failed
    still counts when the command hid its status (`pytest || true`,
    `pytest; echo done`, `pytest | tail`); the Unfinished item then cannot
    see the failure either. A call run in the background proves nothing
    (`_checks`).
    """

    if call.kind != events.SHELL_COMMAND or call.background:
        return False
    command = shell.analyze(call.command, call.shell)
    return not command.unchecked_unknown_writes and not any(
        is_code(_norm(target)) for target in command.unchecked_targets
        if target and _in_project(target, project, target not in command.unplaced_targets)
    )


def _checks(calls) -> list:
    """The shell calls in `calls` that ran a check. One the harness ran in the
    background is not a check (Ticket 116): its launch proves nothing, and
    its result is not read."""

    return [
        call for call in calls
        if call.kind == events.SHELL_COMMAND and not call.background
        and shell.analyze(call.command).is_check
    ]


# Paths and edits ----------------------------------------------------------------

def is_code(path: str) -> bool:
    dot = path.rfind(".")
    return dot > path.rfind("/") and path[dot:].lower() in CODE_EXTENSIONS


def is_doc(path: str, project: Project | None) -> bool:
    """Whether `path` is a documentation file, by its extension
    (`DOC_EXTENSIONS`). A dependency manifest such as `requirements.txt`,
    which is security-sensitive, is not one; nor is a `.txt` file under a
    test path, such as a golden output file, or a build file
    (`TXT_BUILD_FILES`)."""

    lowered = _norm(path).lower()
    if not lowered.endswith(DOC_EXTENSIONS) or security_category(path) is not None:
        return False
    return not lowered.endswith(".txt") or not (
        _file_name(lowered) in TXT_BUILD_FILES or is_test(path, project))


def security_category(path: str) -> str | None:
    if not path:
        return None
    lowered = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", _norm(path)).lower()
    is_doc = lowered.endswith(DOC_EXTENSIONS)
    for name, pattern in SECURITY_CATEGORIES:
        if (not is_doc or name in ALWAYS_CHECKED_CATEGORIES) and pattern.search(lowered):
            return name
    return None


def sensitive_category(path: str, project: Project | None) -> str | None:
    """The security category of a project file at `path` (`security_category`),
    or None for test code whose category comes from a word in its name
    (round 6, R9): a code file that is a test file (`is_test`), matched as
    `TEST_CODE_SPARED` says, as `tests/test_login_x.py` is by `login`.
    A test file that is not code (`tests/.env`), and test code matched by
    its kind (`migrations/0001_test.sql`), stay sensitive. The `security`
    gate, the Security closeout item and the `sensitive-category-count`
    signal all judge files by it."""

    category = security_category(path)
    if category in TEST_CODE_SPARED and is_code(path) and is_test(path, project):
        return None
    return category


def countable_lines(write: Call) -> int | None:
    """The lines a file write adds, every line of each edit's added text, or
    None when they cannot be counted: an edit adds text it does not show.
    A write with no edits adds none."""

    if any(added is None for _, added in write.edits):
        return None
    return sum(len(added.split("\n")) for _, added in write.edits if added)


def new_lines(write: Call) -> int | None:
    """The lines a file write adds that the text it replaces did not hold:
    each non-blank line of an edit's added text whose content, indentation
    aside, is not a line of that edit's removed text, as the reference
    signals count added code (`design_reads.added_lines`). Unchanged context
    sent with an edit adds none. Text an edit replaces without saying what
    (a whole-file write) counts as empty, so all its lines are new; None
    when an edit does not show what it adds."""

    if any(added is None for _, added in write.edits):
        return None
    total = 0
    for removed, added in write.edits:
        kept = {line.strip() for line in (removed or "").split("\n")}
        total += sum(1 for line in added.split("\n") if line.strip() and line.strip() not in kept)
    return total


def _small_edit(write: Call) -> bool:
    """Whether a file write is too small for the design gates: it adds fewer
    than `DESIGN_MIN_LINES` lines, or is a short comment-only edit
    (`_short_comment_edit`). One whose added lines cannot be counted is not
    small."""

    lines = countable_lines(write)
    return lines is not None and (lines < DESIGN_MIN_LINES or _short_comment_edit(
        lines, lambda: design_reads.comment_only(write.path, write)))


def _comment_on_little_code(write: Call) -> bool:
    """Whether a code edit adds too little for its comment to select
    `readability.md` (round 5, K1): fewer than `DESIGN_MIN_LINES` code lines
    and fewer than `COMMENT_EDIT_MIN_LINES` comment lines
    (`design_reads.written_line_counts`), a comment-only edit included. It
    changes only that signal: the write may still be substantial for the
    `design` gate. One whose lines cannot be split, as in a language whose
    comments the core does not read, is judged by its size alone, as
    before."""

    counts = design_reads.written_line_counts(write.path, write)
    return (counts is not None and counts.code < DESIGN_MIN_LINES
            and counts.comments < COMMENT_EDIT_MIN_LINES)


def _short_comment_edit(added_lines: int | None, comment_only: Callable[[], bool]) -> bool:
    """Whether an edit adding `added_lines` lines, None when unknown, is a
    comment-only edit adding fewer than `COMMENT_EDIT_MIN_LINES`: the design
    gates find it small, and the Design item does not count it.
    `comment_only` is asked only when the count is short enough."""

    return added_lines is not None and added_lines < COMMENT_EDIT_MIN_LINES and comment_only()


def _subject(message: str) -> str:
    return " ".join(message.strip().split("\n", 1)[0].split())


def _norm(path: str) -> str:
    return path.replace("\\", "/")


# The classes of file the usage log gives a hold (round 6, R15).
FILE_CLASSES = ("code", "test", "docs", "configuration", "other")


def file_class(call: Call, project: Project | None) -> str | None:
    """The class of the file a held `call` writes, one of `FILE_CLASSES`, for
    the usage log, which never keeps the path: a file write's file, or the
    first file a shell command names as written. None for a call that names
    no file it writes, such as a commit or a spawn. A test file is judged by
    its place in the project, or by the path itself when no project is
    known; a configuration file as the design gates judge one
    (`design_reads.is_config`)."""

    if call.kind == events.FILE_WRITE:
        path = _norm(call.path)
    elif call.kind == events.SHELL_COMMAND:
        targets = shell.analyze(call.command, call.shell).write_targets
        path = _norm(targets[0]) if targets else ""
    else:
        path = ""
    if not path:
        return None
    if design_reads.is_test_path(_path_in_project(path, project) if project else path):
        return "test"
    if is_code(path):
        return "code"
    if is_doc(path, project):
        return "docs"
    return "configuration" if design_reads.is_config(path) else "other"


def _same_file(read: str, changed: str) -> bool:
    """True when two paths, either relative, name the same file; judged from
    the text alone, so a relative path matches any file it ends."""

    a, b = (_norm(p).lower().removeprefix("./") for p in (read, changed))
    return bool(a and b) and (a == b or a.endswith("/" + b) or b.endswith("/" + a))


def _ends_with_path(path: str, suffix: str) -> bool:
    path = _norm(path).lower()
    return path == suffix or path.endswith("/" + suffix)
