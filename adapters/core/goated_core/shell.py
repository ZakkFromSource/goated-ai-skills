"""What a POSIX shell or PowerShell command does, as far as the gates care.

`analyze` reads one command string and answers: does it write files, and
which; is it a `git commit`, and with what inline message; does it open a pull
request; and does it run a check that proves a change. This module is the
only place that knows shell syntax; the gates see `ShellCommand` objects.

The command is split into segments (simple commands joined by `;`, `&&`,
`||`, `|`, `&`, newlines, parentheses, braces, or `$(`), with quotes, escapes,
line continuations, comments, heredocs, PowerShell here-strings, `[[ ]]`
tests, and arithmetic understood well enough that `echo "a > b"`,
`[[ $a > $b ]]`, and `ls # a > b` write nothing. Each segment's real command
word is found past wrappers such as `sudo -u x`, `env`, `timeout 60`, `nice`,
`xargs`, and `cmd /c`. It is still a lexical reading, not a shell: a command
run through `bash -c`, `eval`, `Invoke-Expression`, backticks, a heredoc fed to
a shell, or a git alias is not seen. The enforcement contract's Shell Reading
states these limits.
"""

from __future__ import annotations

import re
from typing import NamedTuple

from . import script_writes
from .events import POSIX, POWERSHELL

# Redirect targets that write no file, lowercased, by shell. `nul` is the null
# device in PowerShell, but in a posix shell it is a file named `nul`, and
# there the null device is `/dev/null`.
NULL_TARGETS = {
    POSIX: frozenset({"/dev/null", "$null", "/dev/stderr", "/dev/stdout"}),
    POWERSHELL: frozenset({"/dev/null", "$null", "nul", "/dev/stderr", "/dev/stdout"}),
}
WINDOWS_NULL_DEVICE = "nul"
DOTNET_WRITE_RE = re.compile(
    r"\[(?:system\.)?io\.(?:file|directory)\]::(?:write|append|copy|move|delete|create|replace)",
    re.IGNORECASE,
)
# A bash escape outside quotes; elsewhere a backslash is kept, so Windows paths survive.
ESCAPABLE = frozenset(" \t\"'\\$`;&|<>(){}#*?[]~!")
SEPARATORS = frozenset(";|&\n(){}")

# Write commands, by how their file arguments are read. Bash first, then
# PowerShell cmdlets and the aliases Windows PowerShell 5.1 ships.
TARGETS_ARE_ARGS = frozenset(
    {
        "rm", "rmdir", "touch", "truncate", "tee", "unlink", "shred", "ln",
        "mv", "move", "ren", "rename",
        "del", "erase", "rd", "ri", "remove-item", "mi", "move-item", "rni", "rename-item",
        "tee-object", "clear-content", "clc", "new-item", "ni",
    }
)
TARGET_IS_LAST_ARG = frozenset({"cp", "copy", "cpi", "copy-item", "install"})
# PowerShell cmdlets whose first positional argument, or -Path, is the file.
TARGET_IS_PATH_PARAM = frozenset(
    {"set-content", "sc", "add-content", "ac", "out-file", "export-csv", "export-clixml"}
)
PS_PATH_PARAMS = frozenset({"-path", "-literalpath", "-filepath", "-destination", "-outfile"})
PS_VALUE_PARAMS = PS_PATH_PARAMS | frozenset(
    {"-value", "-encoding", "-itemtype", "-name", "-include", "-exclude", "-filter",
     "-delimiter", "-inputobject", "-newname", "-uri", "-method"}
)
# Commands that print the files they name (spec R10), each with its options
# that take a value that is no file: a count, a delimiter, or an encoding
# (`cat -n` only numbers lines). `type` and `gc` are Get-Content's aliases in
# PowerShell, which takes its parameters by name; `type` in Bash describes
# commands, so its output never holds a file's text.
_COUNTS = frozenset({"-n", "-c", "--lines", "--bytes"})
_GET_CONTENT_VALUES = frozenset(
    {"-totalcount", "-head", "-first", "-tail", "-last", "-readcount", "-delimiter",
     "-encoding", "-stream",
     # PowerShell's common parameters that take a value, with their aliases.
     "-erroraction", "-ea", "-warningaction", "-wa", "-outvariable", "-ov",
     "-errorvariable", "-ev"}
)
FILE_PRINTERS = {
    "cat": frozenset(), "head": _COUNTS, "tail": _COUNTS,
    "get-content": _GET_CONTENT_VALUES, "gc": _GET_CONTENT_VALUES, "type": _GET_CONTENT_VALUES,
}
PS_FILE_PRINTERS = frozenset({"get-content", "gc", "type"})
# The Get-Content parameters that print only part of a file (Ticket 110).
# PowerShell takes a parameter by any prefix of its name, so a prefix of one
# of these counts as it (`-Tot 5`); `-T`, which PowerShell finds ambiguous
# and refuses, counts too.
PS_RANGE_PARAMS = frozenset({"-totalcount", "-head", "-first", "-tail", "-last"})
# Writes whose files cannot be read from the command line.
UNKNOWN_TARGET_COMMANDS = frozenset({"patch"})
DOWNLOADERS = frozenset({"curl", "wget", "invoke-webrequest", "iwr", "invoke-restmethod", "irm"})
GIT_UNKNOWN_TARGET_SUBCOMMANDS = frozenset({"apply", "am", "clean"})
GIT_GLOBAL_WITH_VALUE = frozenset({"-c", "-C", "--git-dir", "--work-tree", "--namespace"})
# Change reads (spec R7): git subcommands that print the changes' content by
# default, the options that ask for it explicitly, and the options that print
# names, counts, nothing, or into a file instead (matched as prefixes, so
# `--stat=80` counts as `--stat`).
GIT_PATCH_BY_DEFAULT = frozenset({"diff", "show"})
GIT_PATCH_FLAGS_RE = re.compile(r"-p|-u|-U\d*|--patch(?:-with-(?:stat|raw))?|--unified(?:=\d+)?")
GIT_NO_PATCH_FLAGS = (
    "--stat", "--shortstat", "--numstat", "--dirstat", "--compact-summary", "--summary",
    "--name-only", "--name-status", "--no-patch", "--check", "--raw",
)
# Options that print nothing to the agent, even beside a patch option.
GIT_SILENT_FLAGS_RE = re.compile(r"--quiet|--output(?:=.*)?")
# `gh pr diff` and `glab mr diff` print a pull or merge request's patch.
FORGE_DIFFS = {"gh": "pr", "glab": "mr"}
# The options of `gh pr create` and `glab mr create` that take a value, by the
# role each names: "base" (the branch merged into), "head" (the branch merged
# from), "repository" (the repository the request opens in), or None. A value
# is never read as an option, so `--description "-bump deps"` names no base.
PR_VALUE_OPTIONS = {
    "gh": {
        "--base": "base", "-B": "base", "--head": "head", "-H": "head",
        "--repo": "repository", "-R": "repository",
        **dict.fromkeys(("--assignee", "-a", "--body", "-b", "--body-file", "-F", "--label",
                         "-l", "--milestone", "-m", "--project", "-p", "--recover",
                         "--reviewer", "-r", "--template", "-T", "--title", "-t")),
    },
    "glab": {
        "--target-branch": "base", "-b": "base", "--source-branch": "head", "-s": "head",
        "--repo": "repository", "-R": "repository",
        **dict.fromkeys(("--assignee", "-a", "--description", "-d", "--related-issue", "-i",
                         "--label", "-l", "--milestone", "-m", "--reviewer",
                         "--target-project", "--title", "-t")),
    },
}

# Wrappers that run the next word as the command, with the options of each
# that take a value.
WRAPPERS = {
    "sudo": {"-u", "-g", "-h", "-p", "-C", "-D", "-r", "-t", "-U"},
    "doas": {"-u", "-C"},
    "env": {"-u", "-C", "-S"},
    "nice": {"-n"},
    "ionice": {"-c", "-n", "-p"},
    "timeout": {"-s", "-k"},
    "nohup": set(),
    "command": set(),
    "builtin": set(),
    "exec": {"-a"},
    "time": {"-f", "-o"},
    "stdbuf": {"-i", "-o", "-e"},
    "xargs": {"-I", "-n", "-P", "-L", "-d", "-E", "-s", "-a"},
}

# Check commands: tools that are checks by name, and runners whose first
# argument decides.
CHECK_TOOLS = frozenset(
    {
        "pytest", "py.test", "tox", "nox", "jest", "vitest", "mocha", "ava", "eslint", "ruff",
        "flake8", "pylint", "mypy", "pyright", "tsc", "ctest", "phpunit", "rspec",
        "shellcheck", "golangci-lint", "invoke-pester", "bats", "pre-commit",
    }
)
CHECK_MODULES = frozenset(
    {"pytest", "unittest", "mypy", "ruff", "tox", "nox", "pyright", "flake8", "pylint", "doctest"}
)
SUBCOMMAND_CHECKS = {
    "cargo": {"test", "check", "clippy", "build", "nextest"},
    "go": {"test", "vet", "build"},
    "dotnet": {"test", "build"},
    "npm": {"test", "t"},
    "pnpm": {"test", "t"},
    "yarn": {"test"},
    "bun": {"test"},
    "deno": {"test", "check", "lint"},
}
SCRIPT_RUNNERS = frozenset({"npm", "pnpm", "yarn", "bun"})
TARGET_RUNNERS = frozenset({"make", "just", "task", "rake", "mvn", "mvnw", "gradle", "gradlew"})
COMMAND_RUNNERS = {  # runner -> subcommand that runs the rest as a command ("" for none)
    "uv": "run", "poetry": "run", "pipenv": "run", "pdm": "run", "hatch": "run",
    "bundle": "exec", "npx": "", "pnpx": "", "bunx": "",
}
INTERPRETERS = frozenset(
    {"python", "python3", "py", "node", "bash", "sh", "zsh", "pwsh", "powershell", "ruby",
     "perl", "php"}
)
class _CodeOptions(NamedTuple):
    """How an interpreter takes inline code. `code` are the short options
    whose value is the code, `values` the short options that take another
    value, `module` those that run a named module instead; `long_code` and
    `long_values` are the long options of the first two kinds. `attached`
    says the code may follow its option in the same word (`-cprint(1)`);
    `shell` says the code is a command line (`bash -c 'npm test'`)."""

    code: str
    values: str = ""
    module: str = ""
    long_code: frozenset = frozenset()
    long_values: frozenset = frozenset()
    attached: bool = True
    shell: bool = False


_PYTHON = _CodeOptions("c", "WX", "m", long_values=frozenset({"--check-hash-based-pycs"}))
_SHELL = _CodeOptions("c", "oO", long_values=frozenset({"--rcfile", "--init-file"}),
                      attached=False, shell=True)
# Interpreters that take code inline (`python -c`, `node -e`, `bash -c`), by name.
INLINE_CODE = {
    "python": _PYTHON, "python3": _PYTHON, "py": _PYTHON,
    "node": _CodeOptions("ep", "rC", long_code=frozenset({"--eval", "--print"}),
                         long_values=frozenset({"--require", "--import", "--loader"}),
                         attached=False),
    "ruby": _CodeOptions("e", "ICrE"), "perl": _CodeOptions("eE", "I"),
    "php": _CodeOptions("r", "cdfz"), "bash": _SHELL, "sh": _SHELL, "zsh": _SHELL,
    "bun": _CodeOptions("ep", long_code=frozenset({"--eval", "--print"}), attached=False),
}
# PowerShell's options that take a value, lowercased with their short forms.
PS_VALUE_OPTIONS = frozenset({
    "-executionpolicy", "-ep", "-ex", "-windowstyle", "-w", "-workingdirectory", "-wd",
    "-outputformat", "-of", "-o", "-inputformat", "-if", "-in", "-settingsfile",
    "-configurationname", "-version", "-v", "-psconsolefile", "-custompipename",
})
CHECK_WORD_RE = re.compile(
    r"(?<![a-z0-9])(?:test|tests|check|checks|validate|verify|lint|typecheck|build|ci)(?![a-z0-9])",
    re.IGNORECASE,
)


class PullRequest:
    """One pull request a shell command opens, as its own simple command
    names it. `base` and `head` are the branches it merges into and from
    (`--base`/`-B` and `--head`/`-H` for gh, `--target-branch`/`-b` and
    `--source-branch`/`-s` for glab), else None; `repository` is the
    repository it names with `--repo` or `-R`, as its path (`owner/repo`,
    `group/sub/repo`) without any host or URL around it, else None (spec R7)."""

    __slots__ = ("base", "head", "repository")

    def __init__(self, base: str | None, head: str | None, repository: str | None) -> None:
        self.base = base
        self.head = head
        self.repository = repository


class ShellCommand:
    """The facts the gates need about one shell command.

    `writes` says it writes, copies, moves, or deletes files. `write_targets`
    are the files it names as written (redirect targets, copy destinations,
    removed or moved files, in-place edits), each joined to any `cd` before
    it in the command that can be followed (see `_change_directory`).
    `unplaced_targets` are the relative ones written from a folder the
    command left unknown, so where they are cannot be said. `unknown_writes` says some
    write's files cannot be read from the command (`git apply`, `patch`, a
    download without an output name). `commit` is True for a `git commit`
    that records one (not `--dry-run`); `commit_message` is its message when
    that commit carries it inline, else None. `pull_requests` holds a
    `PullRequest` for each `gh pr create|new` and `glab mr create|new` in it,
    in order, each read from its own simple command's options alone (spec
    R14); `opens_pr` says there is one. `is_check` says it runs a
    test, lint, build, or check, not sent to the background (`pytest &` is
    a launch, whose result the command does not wait for, so it is no
    check); `non_check_writes` says some simple command
    in it writes and is not itself a check (`sed -i … && pytest`, but not
    `pytest > out.txt`). `unchecked_targets` are the write targets no check
    certainly ran after, and `unchecked_unknown_writes` says some unnamed
    write is one. A check proves the writes before it when every command
    from the write to the check is joined by `&&`, `;`, or a newline
    (`cp a.py src/a.py && pytest`), none of them is an `exit` or the like,
    and neither runs inside a branch, loop, function, or group; the check
    itself must not run in the background (`pytest &`). A check's own
    output and anything written after it stay unchecked (`pytest | tee
    log.txt`). `prints_changes` says it prints changes'
    content to the agent: a git diff or show, a patch log, or patches on
    stdout; a listing of names or counts (`--stat`, `--name-only`) does not.
    Only git is read; another version control system's diff is not seen.
    `shown_files` are the files a file printer (`FILE_PRINTERS`, such as
    `cat` or `Get-Content`) in it names, from where the command started, so
    its output may hold their text; `shows_git_diff` says it runs `git diff`,
    whose output names each file's section (spec R10). `whole_prints` are
    those of its files a whole print shows the agent whole (Ticket 110): a
    `cat`, or in PowerShell a `Get-Content`, `gc`, `type` or `cat` with no
    range parameter (`PS_RANGE_PARAMS`), whose output goes neither into a
    pipe nor into a file, not run as a background job (`&`), outside any
    compound command, group or substitution, in the command's trailing `&&`
    chain (see `_sets_status`); a file named by a word the shell expands,
    or from a folder the command left unknown, is left out. `file_prints`
    are the files it shows the agent whole or in part, on the same terms
    (round 6's R3): those, and the files of a posix `head`, `tail`, or
    `sed -n` (never `sed -i`), and of a ranged `Get-Content`. A search that
    prints matching lines (`grep`, `rg`, `Select-String`) prints no file.
    `script_targets` are the write targets that code given to an interpreter
    inline names (`python -c`, `node -e`, a heredoc on `python -`; see
    `_inline_script`), and `script_unknown_writes` says such code writes a
    file it names only at run time; both are also in the facts above.
    `text_writes` lists each write that puts new text into a target (a
    redirect, `tee`, `Set-Content`, `Add-Content`, `Out-File`, or `New-Item`
    with a value; Ticket 098), in order, as the target and how many lines of
    that text the command shows, as a heredoc's body or the arguments of
    `echo`, `printf`, or `-Value`; or None when it does not show it, as for
    a program's output or text holding a variable, command substitution,
    or subexpression. One target may appear more than once, under any
    spelling. A copy, move, restore, or in-place edit carries no new text,
    so its targets are not here.
    A package install is one that installs or adds a dependency or tool it
    names (`uv add httpx`), not a bare restore such as `npm install`.
    `installs_globally` says it runs a global, machine, or per-user install
    (`GLOBAL_INSTALLS`, `GLOBAL_OPTIONS`, or any install under `sudo`), which
    counts for the Setup item wherever it runs; `install_folders` holds the
    folder each other install goes into: the one a folder option names
    (`FOLDER_OPTIONS`), else the one it runs in, "" for the command's
    starting folder, a path after a followed `cd`, or None when that cannot
    be named (spec R14).
    `read_only` says every simple command in it is a plain read (see
    `READ_ONLY_COMMANDS`), perhaps after a leading `cd` to a plain path,
    joined only by pipes or list separators, with no wrapper, redirect into
    a file (a Bash `2>/dev/null` aside), heredoc, group, substitution, or
    background job, and with none of the text in `NOT_PLAINLY_SPELLED_RE`
    outside what a whole quoted argument exempts (see `_outside_quoted_arguments`);
    when the reading is in doubt it is False. `only_reads_and_writes_files`
    is the same test loosened only for file work: each simple command may
    instead be a `cd`, a command that only writes the files it names
    (`FILE_WRITERS`, such as `cp` or `rm`), or a plain read whose output is
    redirected into a file, and every write's files are named. It says
    nothing about where those files are.
    `redirects_into_nul` says it is a posix command that redirects into
    `nul` (any case), which there writes a file named `nul` rather than
    discarding the output (Ticket 104); that file is in the facts above.
    `write_part` is, for a command that looks like a plain read, since each
    simple command in it is named as one (`READ_ONLY_COMMANDS`, `cd`, or
    `git`), but is not one, the first part that made it no plain read, in
    words a hold can quote, such as `the redirect into "b.txt"` (round 6,
    R11); else None.
    """

    __slots__ = (
        "writes", "write_targets", "unplaced_targets", "unknown_writes", "commit",
        "commit_message", "pull_requests", "is_check",
        "non_check_writes", "unchecked_targets", "unchecked_unknown_writes", "prints_changes",
        "installs_globally", "install_folders", "read_only", "only_reads_and_writes_files",
        "script_targets", "script_unknown_writes", "text_writes", "redirects_into_nul",
        "shown_files", "whole_prints", "file_prints", "shows_git_diff", "write_part",
    )

    def __init__(self) -> None:
        self.writes = False
        self.write_targets: list[str] = []
        self.unplaced_targets: list[str] = []
        self.unknown_writes = False
        self.commit = False
        self.commit_message: str | None = None
        self.pull_requests: list[PullRequest] = []
        self.is_check = False
        self.non_check_writes = False
        self.unchecked_targets: list[str] = []
        self.unchecked_unknown_writes = False
        self.prints_changes = False
        self.installs_globally = False
        self.install_folders: list[str | None] = []
        self.read_only = False
        self.script_targets: list[str] = []
        self.script_unknown_writes = False
        self.text_writes: list[tuple[str, int | None]] = []
        self.only_reads_and_writes_files = False
        self.redirects_into_nul = False
        self.shown_files: list[str] = []
        self.whole_prints: list[str] = []
        self.file_prints: list[str] = []
        self.shows_git_diff = False
        self.write_part: str | None = None

    @property
    def opens_pr(self) -> bool:
        return bool(self.pull_requests)


def analyze(command: str, shell: str = POSIX) -> ShellCommand:
    """Return what `command`, run in `shell` (`events.POSIX` or `events.POWERSHELL`), does;
    never raises on odd input. In a PowerShell command, .NET write text
    counts as a write wherever it appears; see `_runs_dotnet_write` for Bash."""

    result = ShellCommand()
    directory: str | None = ""
    # Writes a check may still prove: each later command so far runs after them, in order.
    awaiting: list[str] = []
    awaiting_unknown = False
    segments = _segments(command)
    for index, segment in enumerate(segments):
        start = len(result.write_targets)
        before = segments[index - 1] if index else None
        piped = _piped_text(before) if before is not None and before.after == "|" else None
        directory, unknown, is_check = _add_segment(result, segment, directory, shell, piped,
                                                    _sets_status(segments, index))
        if is_check and not segment.nested and segment.after in CHECK_ENDS:
            awaiting, awaiting_unknown = [], False
        awaiting += result.write_targets[start:]
        awaiting_unknown = awaiting_unknown or unknown
        if (segment.nested or segment.after not in IN_ORDER
                or _resolve(segment.words)[0] in STOPS):
            result.unchecked_targets += awaiting
            result.unchecked_unknown_writes |= awaiting_unknown
            awaiting, awaiting_unknown = [], False
        if segment.after not in AND_THEN and directory != "":
            directory = None  # What runs next runs even if a `cd` before it failed.
    result.unchecked_targets += awaiting
    result.unchecked_unknown_writes |= awaiting_unknown
    if DOTNET_WRITE_RE.search(command) and (
        shell == POWERSHELL
        or RUNS_POWERSHELL_RE.search(command)
        or any(map(_runs_script, segments))
        or any(_runs_dotnet_write(segments, index) for index in range(len(segments)))
    ):
        # Where in the command it runs is not read, so no check proves it.
        result.writes = result.unknown_writes = result.unchecked_unknown_writes = True
    result.read_only = (
        bool(segments) and not result.writes
        and not NOT_PLAINLY_SPELLED_RE.search(_outside_quoted_arguments(command))
        and all(_reads_only(segment, index == 0, shell) for index, segment in enumerate(segments))
    ) or (shell == POWERSHELL and command.strip().lower() == POWERSHELL_NO_OP)
    if not result.read_only and segments and all(
            _resolve(segment.words)[0] in READ_COMMAND_NAMES for segment in segments):
        result.write_part = _write_part(command, segments, shell)
    result.only_reads_and_writes_files = (
        bool(segments) and not result.unknown_writes and not NOT_PLAINLY_SPELLED_RE.search(command)
        and all(_reads_only(segment, index == 0, shell) or _works_on_files_only(segment, shell)
                for index, segment in enumerate(segments))
    )
    return result


# Text tools, which cannot start a program, so `.NET` call text handed to
# them is data. Interpreters and `git` (through an alias or hook) can start
# PowerShell, so they are not here.
NO_POWERSHELL = frozenset(
    {"cat", "echo", "printf", "grep", "rg", "head", "tail", "sort", "uniq", "wc",
     "cut", "tr", "tee", "less", "more", "write-output", "write-host", "select-object",
     "select-string", "measure-object", "out-string", "out-host"}
)
# A Bash command naming PowerShell or its `Invoke-Expression` anywhere, even in
# a string, may run `.NET` text written earlier in it, so that text all counts.
RUNS_POWERSHELL_RE = re.compile(
    r"(?<![\w.-])(?:pwsh|powershell|iex|invoke-expression)(?:\.exe)?(?![\w-])", re.IGNORECASE
)
# PowerShell script files: text written into one may run in this call or a later one.
POWERSHELL_SCRIPTS = (".ps1", ".psm1", ".psd1")


def _runs_script(segment: "_Segment") -> bool:
    """True when `segment` runs a PowerShell script, as the PowerShell tool
    does without naming PowerShell: `& x.ps1` (the `&` ends the segment
    before), `. x.ps1`, or a bare `x.ps1`."""

    name, _, args = _resolve(segment.words)
    if name in (".", "source"):
        name = _bare(args[0]) if args else ""
    return name.endswith(POWERSHELL_SCRIPTS)


def _runs_dotnet_write(segments: list["_Segment"], index: int) -> bool:
    """True when segment `index` of `segments` may run a `.NET` file write,
    such as `[IO.File]::WriteAllText(...)`, which names its file only in code.

    Text a program in `NO_POWERSHELL` is given is data, such as text `echo`
    prints or a heredoc fed to `cat`, unless it can still run
    code here (`$(`, a backtick, outside a quoted-delimiter heredoc), the
    segment pipes into a program outside `NO_POWERSHELL`, or it or a program
    it pipes into writes a PowerShell script file. Text anywhere else
    counts: PowerShell may run it, or a shell may pass it on.
    """

    segment = segments[index]
    if not any(DOTNET_WRITE_RE.search(t) for t in segment.words + segment.heredocs):
        return False
    expanded = segment.words + [
        h for h, quoted in zip(segment.heredocs, segment.quoted_heredocs) if not quoted
    ]
    if any(("$(" in t or "`" in t) and DOTNET_WRITE_RE.search(t) for t in expanded):
        return True
    # The segment's output may carry the text on, through each pipe after it.
    for later in segments[index:]:
        name, _, args = _resolve(later.words)
        if name in COMMAND_RUNNERS:
            name = _runner_command(name, args)[0]
        if name not in NO_POWERSHELL:
            return True
        # Into a script file, wherever it is, the text may run in a later call.
        written = later.redirects + (_positional(args) if name in ("tee", "tee-object") else [])
        if any(_bare(target).endswith(POWERSHELL_SCRIPTS) for target in written):
            return True
        if later.after != "|":
            return False
    return False


def _add_segment(result: ShellCommand, segment: "_Segment", directory: str | None,
                 shell: str, piped: tuple[str, bool] | None = None,
                 sets_status: bool = False) -> tuple[str | None, bool, bool]:
    """Add one segment's facts to `result`, its write targets taken from
    `directory` (see `_change_directory`) and its redirects read as `shell`
    reads them; return the directory later segments run in, whether it
    writes files it does not name, and whether it is a check. `piped` is the
    text the segment before pipes into it, when a text producer gives it
    (see `_piped_text`). `sets_status` says the command fails whenever this
    segment fails, as `_sets_status` reads it."""

    null_targets = NULL_TARGETS[shell]
    targets = [t for t in segment.redirects if t.lower() not in null_targets]
    if shell == POSIX and any(t.lower() == WINDOWS_NULL_DEVICE for t in targets):
        result.redirects_into_nul = True
    unknown = False
    prints = False
    name, original, args = _resolve(segment.words)
    # The lines of new text each target gets (`text_writes`). Output is shown
    # when a text producer gives it, or when `cat` with no file passes on
    # shown text piped into it.
    output = _piped_text(segment)
    if output is None and name == "cat" and not _positional(args):
        output = piped
    texts = {t: _shown_lines(output) if t in segment.out_redirects else None for t in targets}
    next_directory = directory
    if name in CHANGE_DIRECTORY:
        followed = segment.chained and segment.after in AND_THEN
        next_directory = _change_directory(name, args, directory) if followed else None
    elif name in TARGETS_ARE_ARGS:
        named = _ps_paths(args) if name.count("-") else _positional(args)
        targets += named
        if name in TEXT_COPIERS:
            texts.update(dict.fromkeys(named, _shown_lines(piped or _standard_input(segment))))
        elif name in TEXT_CREATORS and _ps_has_value(args):
            texts.update(dict.fromkeys(named[:1], _ps_written_lines(name, args, None)))
    elif name in TARGET_IS_LAST_ARG:
        positional = _ps_paths(args) if name.count("-") else _positional(args)
        targets += positional[-1:]
    elif name in TARGET_IS_PATH_PARAM:
        path = _ps_paths(args)[:1]
        targets += path
        if name in TEXT_WRITERS:
            texts.update(dict.fromkeys(path, _ps_written_lines(name, args, piped)))
    elif name in ("sed", "perl", "ruby") and _edits_in_place(args):
        targets += _in_place_files(name, args)
    elif name in DOWNLOADERS:
        output, writes = _download_target(name, args)
        targets += [output] if output else []
        unknown = writes and not output
    elif name in UNKNOWN_TARGET_COMMANDS:
        unknown = True
    elif name == "git":
        sub, rest = _git_subcommand(args)
        git_targets, git_unknown = _git_writes(sub, rest)
        targets += git_targets
        unknown = git_unknown
        if sub == "commit" and "--dry-run" not in rest:
            result.commit = True
            message = _commit_message(rest, segment.heredocs)
            if message is not None:
                result.commit_message = message
        if _git_prints_changes(sub, rest):
            prints = True
        if sub == "diff":
            result.shows_git_diff = True
    elif name in FILE_PRINTERS or name == "sed":
        if name in FILE_PRINTERS:
            result.shown_files += [_from_directory(directory, f)
                                   for f in _printed_files(name, args)]
        if directory is not None and sets_status:
            printed, whole = _printed(name, args, segment, shell)
            placed = [_from_directory(directory, f) for f in printed]
            result.file_prints += placed
            if whole:
                result.whole_prints += placed
    elif name in FORGE_DIFFS:
        rest = _skip_options(args, {"-R", "--repo"})
        noun = FORGE_DIFFS[name]
        if rest[:1] == [noun] and _forge_verb(rest[1:]) in ("create", "new"):
            # `-R`/`--repo`, the base and the head count before the noun,
            # between it and the verb, or after the verb.
            named = _pr_options(args, PR_VALUE_OPTIONS[name])
            repository = named.get("repository")
            result.pull_requests.append(PullRequest(
                named.get("base"), named.get("head"),
                None if repository is None else _repository_path(repository)))
        if rest[:2] == [noun, "diff"] and "--name-only" not in rest:
            prints = True
    scripted: list[str] = []  # The files inline interpreter code writes.
    script = _inline_script(name, args, _standard_input(segment) or piped)
    if script is not None:
        scripted, script_unknown = script_writes.writes(*script)
        if script_unknown:
            unknown = result.script_unknown_writes = True
    # Output redirected into a file never reached the agent; a stderr redirect leaves it.
    if prints and not [t for t in segment.out_redirects if t.lower() not in null_targets]:
        result.prints_changes = True
    is_check = segment.after != "&" and _is_check(name, original, args)
    if is_check:
        result.is_check = True
    wrappers = segment.words[: len(segment.words) - len(args) - 1]
    install = _package_install(name, args, elevated=any(_bare(w) == "sudo" for w in wrappers))
    if install and install.is_global:
        result.installs_globally = True
    elif install:
        result.install_folders.append(_install_folder(directory, install.folder))
    for target, from_script in [(t, False) for t in targets] + [(t, True) for t in scripted]:
        if not target:
            continue
        if directory is None and not _is_absolute(target):
            result.unplaced_targets.append(target)
        result.write_targets.append(_from_directory(directory, target))
        if from_script:
            result.script_targets.append(result.write_targets[-1])
        elif target in texts:
            result.text_writes.append((result.write_targets[-1], texts[target]))
    if targets or scripted or unknown:
        result.writes = True
        if not is_check:
            result.non_check_writes = True
    if unknown:
        result.unknown_writes = True
    return next_directory, unknown, is_check


# Plain reads ---------------------------------------------------------------------
#
# `router-first` lets reads through before the router loads, so an agent can
# look around before it routes. A shell command passes only when it is made of
# the reads below; anything else, including a command this table does not
# know, is held.

# Commands that print files, listings, matches, text, or counts, and change
# nothing. Each still passes only without the arguments that
# `_refused_argument` refuses for it. PowerShell's read cmdlets come with the
# aliases Windows PowerShell 5.1 ships (`ls`, `dir`, `cat`, `echo`, `pwd`,
# `sort`, and `diff` are aliases there too).
READ_ONLY_COMMANDS = frozenset(
    {
        "cat", "head", "tail", "ls", "dir", "grep", "rg", "wc", "find",
        "pwd", "echo", "sort", "uniq", "cut", "tr", "diff", "stat", "file",
        "which", "true", ":",
        "get-content", "gc", "get-childitem", "gci", "select-string", "sls",
    }
)
# A PowerShell command that does nothing, as `true` does in Bash (`true` is
# no command there): the carrier a hold names for a skip or route line (Ticket 095).
POWERSHELL_NO_OP = "$null"
# Arguments that turn a read into a write or make it run another program,
# refused as prefixes: `find` runs or deletes with -exec, -ok, and -delete and
# writes files with -fprint and -fls; `rg --pre` runs a program on every file
# it searches, and `rg --hostname-bin` runs one to name the host.
READ_ONLY_REFUSED_ARGS = {
    "find": ("-exec", "-ok", "-delete", "-fprint", "-fls"),
    "rg": ("--pre", "--hostname-bin"),
}
# The same for GNU tools, which take a long option by any prefix of its name
# (`--out` for `--output`) and short options run together (`-uo`): a long
# option naming any prefix of one here, and a run of short options holding
# a letter here, are refused. `sort` writes its output with `-o` and
# temporary files with `-T`, and runs `--compress-program`; `diff -l`
# pipes its output through `pr`; `file -C` writes a compiled magic file,
# `-z` and `-Z` run decompressors, and `-m` takes a list of magic files
# whose separator differs between builds.
READ_ONLY_REFUSED_OPTIONS = {
    "sort": ("oT", ("output", "compress-program", "temporary-directory")),
    "diff": ("l", ("paginate",)),
    "file": ("CzZm", ("compile", "uncompress", "uncompress-noreport", "magic-file")),
}
# `uniq` writes its second operand; these options take the next word as a value.
UNIQ_VALUE_OPTIONS = frozenset(
    {"-f", "-s", "-w", "--skip-fields", "--skip-chars", "--check-chars"}
)
# git subcommands that print the repository's state or history, with any
# arguments but those in GIT_READ_REFUSED_ARGS.
GIT_READ_SUBCOMMANDS = frozenset({"status", "diff", "log", "show", "rev-parse", "ls-files", "blame"})
# Their arguments refused: `--output` writes the printed text to a file, and
# `--ext-diff`, `--textconv`, and `--show-signature` (which runs
# `gpg.program`) ask for programs the repository's config names. Refusing
# them does not stop those programs: a plain `git diff`,
# `git show`, or `git log -p` runs `diff.external` and textconv drivers too
# (contract, Change Reads). These subcommands take no abbreviated long option
# (`git diff --out=x` is refused by git), so the names are matched as written.
GIT_READ_REFUSED_ARGS = ("--output", "--ext-diff", "--textconv", "--show-signature")
# `git branch` lists branches only with these options, matched whole: git
# takes any prefix of a long option, and `--edit` opens an editor as
# `--edit-description`. A name to create or change is refused, so a word
# that is no option passes only as a pattern after `--list`; not after `-l`,
# which meant `--create-reflog` before git 2.23 (`git branch -l x` created x).
GIT_BRANCH_LIST_OPTIONS = frozenset(
    {"-a", "--all", "-r", "--remotes", "-v", "-vv", "--verbose", "-l", "--list",
     "--show-current", "--color", "--no-color", "-i", "--ignore-case", "--no-column",
     "--no-abbrev"}
)
# Its options that take a value, as `--sort=x` or as the next word.
GIT_BRANCH_VALUE_OPTIONS = frozenset(
    {"--contains", "--no-contains", "--merged", "--no-merged", "--points-at", "--sort",
     "--format"}
)
# `git worktree list` and its options; any other worktree subcommand changes one.
GIT_WORKTREE_LIST_OPTIONS = frozenset({"--porcelain", "-v", "--verbose", "-z"})
# `git remote` prints remotes bare, with `-v`, or as `get-url`. `show`
# contacts each remote, which runs ssh or a credential helper, so it is held.
GIT_REMOTE_LIST = ([], ["-v"], ["--verbose"])
GIT_REMOTE_GET_URL_OPTIONS = frozenset({"--push", "--all"})
# The only git options allowed before the subcommand: `-C` picks the folder,
# and the others turn the pager off. `-c` can set a program to run, such as
# a pager or external diff, so it and every other global option are refused.
GIT_READ_GLOBAL_OPTIONS = frozenset({"-C", "--no-pager", "-P"})
# Separators a read may end at: pipes and the list separators. Not `&`, which
# leaves a job running, nor an opening `(`, `{`, or `$(`, nor a closing one.
READ_ONLY_ENDS = ("", "|", "&&", "||", ";", "\n")
# The `&` of `>&1` or `>&-`: duplicating or closing a descriptor writes no
# file. The number or `-` must end the word: `>&1x` writes the file `1x`.
FD_DUPLICATE = r"&(?:\d+|-)(?=[\s|;&<>()]|$)"
FD_DUPLICATE_RE = re.compile(FD_DUPLICATE)
# Text this lexical reading may not follow as the shell does, so a command
# holding any of it is never a plain read, even inside quotes:
# - `$` expands, and runs code through `$(…)` in double quotes, `${x:=$(…)}`,
#   or `$(( ))`, in bash and PowerShell alike;
# - a backtick substitutes in bash and escapes in PowerShell;
# - a backslash escapes any character in bash (`-del\ete` is `-delete`) but
#   is a plain character in PowerShell (`a\; Remove-Item b` runs both);
# - `<<<` feeds a word that is expanded first;
# - `>&` with no whole descriptor after it writes a file;
# - any character but printable ASCII, a newline, or a tab: PowerShell reads
#   curly quotes as quotes and a lone carriage return or U+2028 as a line
#   break, which this reading does not;
# - a PowerShell block comment, `<#`, which ends at `#>`, not at the line's end;
# - a PowerShell here-string, `@"` or `@'`;
# - `[[` or `]]`: outside command position they are plain words, and a `>`
#   after them redirects, while this reading would take it for a comparison;
# - `//`, which starts a UNC path (`//host/share`) read over the network,
#   where Windows may send the user's credentials;
# - PowerShell's stop-parsing token `--%`, after which the rest of the line
#   goes to a native program unparsed, quotes included;
# - `::` before a separator, a PowerShell provider path
#   (`FileSystem::\\host\share`), which can reach the network too.
# A backslash and `//` inside a whole single-quoted argument are exempt, and so
# is a literal backslash inside a whole double-quoted one; see
# `_outside_quoted_arguments`.
NOT_PLAINLY_SPELLED_RE = re.compile(
    rf"[$`\\]|<<<|>(?=&)(?!{FD_DUPLICATE})|[^\t\n\x20-\x7e]|<#|@[\"']|\[\[|\]\]|//|--%"
    r"|::[\\/]"
)
# Characters before a word starts, and after one ends, for a whole quoted argument.
BEFORE_WORD = frozenset(" \t\n|;&(")
AFTER_WORD = frozenset(" \t\n|;&()<>")
# Inside quoted text, two path separators may start a UNC path anywhere a
# program splits a value off (`-f//host/p`, `--file=\\host\p`), so they
# pass only right after a URL scheme (`https://`): its own word's letters,
# digits, `+`, `.`, or `-`, opening with a letter, then `:`.
SEPARATOR_PAIR_RE = re.compile(r"[\\/]{2}")
URL_SCHEME_END_RE = re.compile(r"(?:^|[^\w+.-])[A-Za-z][\w+.-]*:$")
# A backslash inside double quotes that both shells keep as written (round 7,
# R8): bash escapes only `$`, a backquote, `"`, `\` or a newline there, as POSIX
# says, and PowerShell escapes nothing with it. One before any of those, or at
# the text's end (before its closing quote), is an escape in bash alone.
DOUBLE_QUOTED_LITERAL_BACKSLASH = r'\\(?=[^$`"\\\n])'
# A provider path, kept unblanked so NOT_PLAINLY_SPELLED_RE sees it.
PROVIDER_PATH_RE = re.compile(r"::[\\/]")
# Characters bash expands into file names, even when this reading saw them
# quoted: it keeps no record of the quotes.
GLOB_CHARS = frozenset("*?[")
# The one redirect a read may make in Bash, where it is the null device.
BASH_NULL_DEVICE = "/dev/null"


def _outside_quoted_arguments(command: str) -> str:
    """`command` with the backslashes and slashes of each whole
    single-quoted argument blanked out, and the backslashes of each whole
    double-quoted one that both shells keep as written
    (`DOUBLE_QUOTED_LITERAL_BACKSLASH`), so that `NOT_PLAINLY_SPELLED_RE`
    passes them (`grep -n 'def\\s+x' a.py`, `grep -n "^#\\|^##" a.md`),
    unless the argument may name a UNC path. Bash and PowerShell both read
    a single-quoted text literally, and agree on those backslashes, so they
    agree on it only while they agree on where each quote opens:
    the text is read from the start, and once a backslash or backtick is
    met outside quotes, where bash escapes the next character and
    PowerShell may not, `command` is returned unchanged, and so is held.
    A quote inside a word (`x'\\s'`) is not blanked either."""

    out: list[str] = []
    word_start = True
    i, n = 0, len(command)
    while i < n:
        c = command[i]
        if c in "\\`":
            return command
        if c in "'\"":
            end = command.find(c, i + 1)
            if end < 0:
                out.append(command[i:])
                break
            text = command[i + 1 : end]
            whole = word_start and command[end + 1 : end + 2] in AFTER_WORD | {""}
            if whole and not _may_name_network_path(text):
                text = re.sub(r"[\\/]" if c == "'" else DOUBLE_QUOTED_LITERAL_BACKSLASH, "_", text)
            out.append(c + text + c)
            i, word_start = end + 1, False
        elif c == "#" and word_start:
            end = command.find("\n", i)
            end = n if end < 0 else end
            out.append(command[i:end])  # A comment, kept as written.
            i = end
        else:
            out.append(c)
            i, word_start = i + 1, c in BEFORE_WORD
    return "".join(out)


def _may_name_network_path(text: str) -> bool:
    """True when quoted `text` may hold a UNC or provider path: two
    separators anywhere but right after a URL scheme, or `::` before one."""

    if PROVIDER_PATH_RE.search(text):
        return True
    return any(not URL_SCHEME_END_RE.search(text[: pair.start()])
               for pair in SEPARATOR_PAIR_RE.finditer(text))


# Commands whose only effect is to write, copy, move, link, or remove the
# files they name. Left out: `install`, whose `--strip-program` runs a
# program, and `rename`, which is Perl's on many systems and runs its
# expression as code.
FILE_WRITERS = (TARGETS_ARE_ARGS | TARGET_IS_LAST_ARG | TARGET_IS_PATH_PARAM) - {"install", "rename"}


def _works_on_files_only(segment: "_Segment", shell: str) -> bool:
    """True when `segment`, written as the bare command, only changes
    folder, only writes the files it names (`FILE_WRITERS`), or is a plain
    read but for redirecting its output into a file (`cat <<'EOF' > x`)."""

    name, original, _ = _resolve(segment.words)
    if segment.words[0] != original or original.lower() != name:
        return False
    if segment.nested or segment.after not in READ_ONLY_ENDS:
        return False
    if name in FILE_WRITERS or name in CHANGE_DIRECTORY:
        return True
    return _reads_only(segment, False, shell, writes_output=True)


def _reads_only(segment: "_Segment", first: bool, shell: str, writes_output: bool = False) -> bool:
    """True when `segment` is a plain read, written as the bare command.

    A wrapper (`sudo`, `xargs`), a variable assignment, or a keyword before
    the command can run something else or change what runs, so the command
    word must come first. It must be the bare name, in any case, with no
    folder or extension: `./cat` or `cat.cmd` may be any program. It has no
    output redirect, not even into a null device: `nul` is a real file in
    bash, and `/dev/null` a real path in PowerShell. The one exception is a
    Bash redirect of another stream than standard output into `/dev/null`
    (`2>/dev/null`). The command's `first` segment may also be a `cd` to
    one plain path, which moves the reads after it but writes nothing.
    With `writes_output`, it may also redirect its output into files and
    read a heredoc.
    """

    name, original, args = _resolve(segment.words)
    if segment.words[:1] != [original] or original.lower() != name:
        return False
    if segment.nested or segment.after not in READ_ONLY_ENDS:
        return False
    if segment.heredocs and not writes_output:
        return False
    if segment.redirects and not writes_output and not (
        shell == POSIX and not segment.out_redirects
        and all(target == BASH_NULL_DEVICE for target in segment.redirects)
    ):
        return False
    if name == "cd":
        path = _change_target(name, args)
        return first and path is not None and _plain(path)
    if name == "git":
        return _git_reads_only(args)
    if name not in READ_ONLY_COMMANDS:
        return False
    if name == "uniq" and (
        len(_positional(_drop_values(args, UNIQ_VALUE_OPTIONS))) > 1
        or any(GLOB_CHARS.intersection(arg) for arg in args)  # `uniq *.txt` names two.
    ):
        return False
    return not any(_refused_argument(name, arg) for arg in args)


# The command names a plain read may have, for `ShellCommand.write_part`.
READ_COMMAND_NAMES = READ_ONLY_COMMANDS | {"cd", "git"}


def _write_part(command: str, segments: list["_Segment"], shell: str) -> str | None:
    """The first part of `command` that makes it no plain read, tested in the
    order `_reads_only` and `analyze` test it, in words a hold quotes; None
    when no single part can be named."""

    spelled = NOT_PLAINLY_SPELLED_RE.search(_outside_quoted_arguments(command))
    if spelled:
        # A backtick is named, not quoted: a reader of hold texts pairs backticks.
        text = "a backtick" if spelled[0] == "`" else f'the text "{spelled[0]}"'
        return f"{text}, which this reading cannot follow as the shell does"
    for index, segment in enumerate(segments):
        if _reads_only(segment, index == 0, shell):
            continue
        name, original, args = _resolve(segment.words)
        if segment.words[:1] != [original]:
            return f'"{segment.words[0]}" before the command'
        if original.lower() != name:
            return f'the command written as "{original}"'
        if segment.after == "&":
            return "the background job (&)"
        if segment.nested or segment.after not in READ_ONLY_ENDS:
            return "a group or substitution"
        if segment.heredocs:
            return "a heredoc"
        if segment.redirects:
            target = next((t for t in segment.redirects if t != BASH_NULL_DEVICE),
                          segment.redirects[0])
            return f'the redirect into "{target}"'
        if name == "cd":
            return "a cd after the first command" if index else "a cd to a path it cannot read"
        if name == "git":
            return f'"{" ".join(["git", *args])}"'
        if name == "uniq":
            return "a second file named to uniq, which it writes"
        refused = next((arg for arg in args if _refused_argument(name, arg)), None)
        if refused is not None:
            return f'the argument "{refused}"'
    return None


def _refused_argument(name: str, arg: str) -> bool:
    """True when `arg` makes the read `name` write a file or run a program."""

    if arg.startswith(READ_ONLY_REFUSED_ARGS.get(name, ())):  # `-fprint` covers `-fprintf`.
        return True
    letters, long_names = READ_ONLY_REFUSED_OPTIONS.get(name, ("", ()))
    if arg.startswith("--"):
        given = arg[2:].split("=", 1)[0]
        return bool(given) and any(full.startswith(given) for full in long_names)
    return arg.startswith("-") and any(letter in arg[1:] for letter in letters)


def _git_reads_only(args: list[str]) -> bool:
    index = 0
    while index < len(args) and args[index].startswith("-"):
        if args[index] not in GIT_READ_GLOBAL_OPTIONS:
            return False
        index += 2 if args[index] == "-C" else 1
    if index >= len(args):
        return False
    sub, rest = args[index], args[index + 1:]
    if any(arg.startswith(GIT_READ_REFUSED_ARGS) for arg in rest):
        return False
    if sub in GIT_READ_SUBCOMMANDS:
        return True
    if sub == "branch":
        return _git_branch_lists(rest)
    if sub == "worktree":
        return rest[:1] == ["list"] and all(a in GIT_WORKTREE_LIST_OPTIONS for a in rest[1:])
    if sub == "remote":
        if rest in GIT_REMOTE_LIST:
            return True
        names = [a for a in rest[1:] if a not in GIT_REMOTE_GET_URL_OPTIONS]
        return rest[:1] == ["get-url"] and len(names) == 1 and not names[0].startswith("-")
    return False


def _git_branch_lists(args: list[str]) -> bool:
    """True when `git branch args` only lists branches."""

    patterns = False
    listing = False
    index = 0
    while index < len(args):
        arg = args[index]
        option = arg.split("=", 1)[0]
        if arg == "--list":
            listing = True
        elif option in GIT_BRANCH_VALUE_OPTIONS and "=" not in arg:
            # git takes the next word as the value; a glob there expands into
            # several, and a name left over is a branch to create.
            index += 1
            if GLOB_CHARS.intersection(args[index] if index < len(args) else ""):
                return False
        elif option in GIT_BRANCH_VALUE_OPTIONS:
            pass
        elif option in ("--color", "--abbrev") and "=" in arg:
            pass
        elif arg.startswith("-"):
            if arg not in GIT_BRANCH_LIST_OPTIONS:
                return False
        else:
            patterns = True
        index += 1
    return listing or not patterns


# Directory changes ---------------------------------------------------------------
#
# A write target is relative to the folder its segment runs in. A `cd` earlier
# in the same command moves that folder, so `cd /elsewhere && mv a b` writes
# `/elsewhere/a`. Only a `cd` that is certain to have run, and to name its
# folder, is followed: one in the command's leading `&&` chain (see
# `_Segment.chained`), not run in a pipeline or the background, to a plain path.
# The directory is "" before any `cd`, a path once one is followed, and None,
# for the rest of the command, once a `cd` cannot be followed or a separator
# other than `&&` follows a `cd` that was. Relative targets written from an
# unknown directory are unplaced: the gates count them as inside the project.

# A plain folder change, and its aliases: the only one followed.
FOLLOWED_CHANGE = frozenset({"cd", "chdir", "set-location", "sl"})
# Every folder change. The folder stacks are never followed: `pushd -n` does not
# move, `pushd +1` rotates, and `popd` returns to a folder the command does not name.
CHANGE_DIRECTORY = FOLLOWED_CHANGE | {"pushd", "popd", "push-location", "pop-location"}
# Separators after which the next command runs only if this one succeeded ("":
# the command's end).
AND_THEN = ("&&", "")
# Separators after which the next command runs only once this one has finished
# (after `&&`, only if it succeeded): a check after them ran after the write.
IN_ORDER = ("&&", ";", "\n")
# Separators that may end a check that proves the writes before it: any that
# lets the check finish before the command goes on, so not `&` or a group opening.
CHECK_ENDS = IN_ORDER + ("", "||", "|")
# Commands after which the rest of the command may not run.
STOPS = frozenset({"exit", "return", "exec", "logout", "break", "continue", "throw"})
DRIVE_RE = re.compile(r"^[A-Za-z]:[\\/]")
# Characters a shell expands, so a path holding one names no folder for certain.
EXPANDED_CHARS = frozenset("$`%*?[{(")


def _change_directory(name: str, args: list[str], directory: str | None) -> str | None:
    """Return the directory after `name args`, a `cd` certain to have run in
    `directory`, or None when that folder cannot be named."""

    if directory is None or name not in FOLLOWED_CHANGE:
        return None
    path = _change_target(name, args)
    if path is None or not _plain(path):
        return None
    if not _is_absolute(path) and not _explicitly_relative(path):
        return None  # Bash may find a bare name such as `sub` through CDPATH instead.
    return _logical(_from_directory(directory, path))


def _logical(path: str) -> str | None:
    """Folder `path` as `cd` and `Set-Location` hold it: each `..` drops the
    name before it from the text (bash's default `cd -L`), before any Git Bash
    mount is reached, so `/tmp/../c/x` is `/c/x`. None when a `..` would climb
    above `~`, whose parent the text does not name."""

    if path.startswith(("//", "\\\\")):
        return path  # A network or device path: not read further (see actions).
    root = ""
    rest = path
    if path.startswith(("/", "\\")):
        root, rest = "/", path[1:]
    elif DRIVE_RE.match(path):
        root, rest = path[:2] + "/", path[3:]
    elif path == "~" or path.startswith(("~/", "~\\")):
        root, rest = "~/", path[2:]
    names: list[str] = []
    for name in re.split(r"[\\/]", rest):
        if name in ("", "."):
            continue
        if name != "..":
            names.append(name)
        elif names and names[-1] != "..":
            names.pop()
        elif root == "~/":
            return None
        elif not root:
            names.append("..")  # Above the starting folder, which the text does not name.
    return root + "/".join(names) if root or names else "."


def _change_target(name: str, args: list[str]) -> str | None:
    """The one folder argument of a `cd` or `Set-Location` that has no other
    argument or option (bar `--`, or `-Path`/`-LiteralPath` naming the folder),
    else None. A `-` or `+` argument, such as `cd -` or `cd +1`, is not a folder."""

    rest = args
    if name in ("cd", "chdir") and args[:1] == ["--"]:
        rest = args[1:]
    elif name in ("set-location", "sl") and args:
        option, colon, value = args[0].partition(":")
        if option.lower() in ("-path", "-literalpath"):
            rest = [value] + args[1:] if colon else args[1:]
    if len(rest) != 1 or rest[0][:1] in ("-", "+", ""):
        return None
    return rest[0]


def _explicitly_relative(path: str) -> bool:
    return path in (".", "..") or path.startswith(("./", "../", ".\\", "..\\"))


def _plain(path: str) -> bool:
    """True when `path` names one folder as written: no expansion, and `~`
    only as the user's home (`~-`, `~+`, and `~user` name others)."""

    if any(ch in EXPANDED_CHARS for ch in path):
        return False
    return not path.startswith("~") or path == "~" or path[1] in "/\\"


def _from_directory(directory: str | None, path: str) -> str:
    """`path` as seen from where the command started, when it was written in `directory`."""

    if not directory or _is_absolute(path):
        return path
    return directory.rstrip("/\\") + "/" + path


def _install_folder(directory: str | None, folder: str | None) -> str | None:
    """Where a project install goes, for `install_folders`: the folder a
    folder option names, seen from `directory`, else `directory` itself.
    None when that cannot be named: an option value the shell expands, or a
    relative one written from an unknown directory."""

    if folder is None:
        return directory
    if not _plain(folder) or (directory is None and not _is_absolute(folder)):
        return None
    return _from_directory(directory, folder)


def _is_absolute(path: str) -> bool:
    return path.startswith(("/", "\\", "~")) or bool(DRIVE_RE.match(path))


# Tokenizing --------------------------------------------------------------------


# Words that open or continue a compound command, which runs its parts only on
# a condition, and `!`, which inverts a command's status: after `! cd x`, an
# `&&` runs exactly when the `cd` failed.
SHELL_KEYWORDS = frozenset(
    {"if", "then", "else", "elif", "do", "while", "until", "for", "select", "!"}
)
# Words that open a compound command, and the words that close one.
COMPOUND_OPEN = frozenset({"if", "while", "until", "for", "select", "case"})
COMPOUND_CLOSE = frozenset({"fi", "done", "esac"})
# Separators that open a group, by the separator that closes it.
GROUP_CLOSE = {"(": ")", "$(": ")", "{": "}"}


class _Segment:
    """One simple command: its words, the files it redirects output into
    (`out_redirects`: those that take its standard output), the bodies of
    heredocs it opened, and `after`, the separator that ended it ("" at the
    command's end). `chained` says it is in the command's leading `&&` chain:
    every separator before it is `&&`, and no compound command, group, or
    script block (`if`, a loop, `case`, `( )`, `{ }`, `$( )`) opened before
    or at it. `nested` says it runs inside a compound command or group that
    is still open (a branch, a loop or function body, a subshell), or starts
    with a keyword (`then`, `!`), so whether and when it runs is not certain.
    `quoted_heredocs` says, for each heredoc, whether its delimiter is quoted
    (`<<'EOF'`), so the shell expands nothing in its body. `quoted_words`
    says, for each word, whether it opened with a quote or here-string."""

    __slots__ = ("words", "quoted_words", "redirects", "out_redirects", "heredocs",
                 "quoted_heredocs", "here_strings", "after", "chained", "nested")

    def __init__(self) -> None:
        self.words: list[str] = []
        self.quoted_words: list[bool] = []
        self.redirects: list[str] = []
        self.out_redirects: list[str] = []
        self.heredocs: list[str] = []
        self.quoted_heredocs: list[bool] = []
        self.here_strings: list[str] = []
        self.after = ""
        self.chained = False
        self.nested = False


def _segments(command: str) -> list[_Segment]:
    text = command
    segments: list[_Segment] = []
    current = _Segment()
    word: list[str] | None = None
    redirect_next = False  # the next word is a redirect target
    redirect_stdout = False  # that redirect takes standard output
    in_test = False  # inside [[ ]], where < and > compare
    # Heredocs waiting for their body: delimiter, strip tabs, quoted, owner.
    pending: list[tuple[str, bool, bool, _Segment]] = []
    chain = True  # every separator so far is `&&`
    open_groups: list[str] = []  # what closes each open group or compound command
    i, n = 0, len(text)

    here_string_next = False  # the next word is a `<<<` here-string, fed to standard input
    word_quoted = False  # the word being read opened with a quote or here-string

    def end_word() -> None:
        nonlocal word, redirect_next, in_test, here_string_next, word_quoted
        if word is None:
            return
        value = "".join(word)
        word = None
        quoted, word_quoted = word_quoted, False
        if here_string_next:
            current.here_strings.append(value)
            here_string_next = False
            return
        if redirect_next:
            current.redirects.append(value)
            if redirect_stdout:
                current.out_redirects.append(value)
            redirect_next = False
            return
        if value == "[[" and all(w in SHELL_KEYWORDS for w in current.words):
            # Only as the command word, after any keywords (`if [[`, `! [[`):
            # elsewhere `[[` is a plain word and a `>` after it redirects.
            in_test = True
        elif value == "]]":
            in_test = False
        current.words.append(value)
        current.quoted_words.append(quoted)

    def end_segment(after: str = "") -> None:
        """End the current segment at separator `after`."""

        nonlocal current, in_test, chain
        end_word()
        first = current.words[0] if current.words else ""
        if first in COMPOUND_OPEN:
            open_groups.append(first)
        if current.words or current.redirects or current.heredocs:
            if first in SHELL_KEYWORDS:
                chain = False
            current.chained = chain
            current.nested = bool(open_groups) or first in SHELL_KEYWORDS
            current.after = after
            segments.append(current)
        if first in COMPOUND_CLOSE and open_groups and open_groups[-1] in COMPOUND_OPEN:
            open_groups.pop()
        if after in GROUP_CLOSE:
            open_groups.append(GROUP_CLOSE[after])
        elif open_groups and after == open_groups[-1]:
            open_groups.pop()
        if after not in AND_THEN:
            chain = False
        current = _Segment()
        in_test = False

    while i < n:
        c = text[i]
        continuation = c in "\\`" and re.match(r"[\\`]\r?\n", text[i : i + 3])
        if continuation:
            # A bash `\` or PowerShell backtick line continuation, outside quotes.
            end_word()
            i += continuation.end()
        elif c in " \t\r":
            end_word()
            i += 1
        elif c == "\n":
            end_word()
            i += 1
            for delimiter, strip_tabs, quoted, owner in pending:
                body, i = _heredoc_body(text, i, delimiter, strip_tabs)
                owner.heredocs.append(body)
                owner.quoted_heredocs.append(quoted)
            pending = []
            end_segment("\n")
        elif c == "#" and word is None:
            end = text.find("\n", i)
            i = n if end < 0 else end
        elif c == "'":
            end = text.find("'", i + 1)
            end = n if end < 0 else end
            word_quoted = word_quoted if word is not None else True
            word = (word or []) + list(text[i + 1 : end])
            i = end + 1
        elif c == '"':
            word_quoted = word_quoted if word is not None else True
            value, i = _double_quoted(text, i + 1)
            word = (word or []) + list(value)
        elif c == "@" and word is None and text[i + 1 : i + 2] in ("'", '"') and (
            text[i + 2 : i + 3] in ("\n", "\r")
        ):
            word_quoted = True
            quote = text[i + 1]
            start = text.find("\n", i) + 1
            end = text.find("\n" + quote + "@", start - 1)
            end = n if end < 0 else end
            word = list(text[start:end].rstrip("\r"))
            i = min(n, end + 3)
        elif c == "\\" and i + 1 < n and text[i + 1] in ESCAPABLE:
            word = (word or []) + [text[i + 1]]
            i += 2
        elif text.startswith("$((", i) or (text.startswith("((", i) and word is None):
            i = _skip_arithmetic(text, i + (1 if c == "$" else 0))
            word = (word or []) + ["0"]
        elif text.startswith("${", i):
            end = text.find("}", i)
            end = n if end < 0 else end
            word = (word or []) + list(text[i : end + 1])
            i = end + 1
        elif text.startswith("<<<", i) and not in_test:
            end_word()
            i += 3
            here_string_next = True
        elif text.startswith("<<", i) and not in_test:
            end_word()
            match = re.match(r"<<(-?)[ \t]*(['\"]?)([A-Za-z_][\w.-]*)\2", text[i:])
            if match:
                pending.append((match.group(3), bool(match.group(1)), bool(match.group(2)),
                                current))
                i += match.end()
            else:
                i += 2
        elif c in "<>" and not in_test:
            fd_prefix = word is not None and all(ch.isdigit() or ch in "&*" for ch in word)
            fd = "".join(word) if fd_prefix and word is not None else ""
            if fd_prefix:
                word = None
            end_word()
            i = _redirect(text, i, c)
            if c == ">" and not text.startswith("&", i):
                redirect_next = True
                redirect_stdout = fd in ("", "1", "&", "*")
            elif c == ">" and not FD_DUPLICATE_RE.match(text, i):
                # `>&word`, `>& word`: a word that is no descriptor is a file,
                # written with both streams, as `&>word` writes it.
                i += 1
                redirect_next = True
                redirect_stdout = fd in ("", "1", "&", "*")
            elif text.startswith("&", i):
                i = _skip_fd(text, i)
            else:
                redirect_next = False
                word = None
                # An input redirect's file is read, not written: drop it.
                while i < n and text[i] in " \t":
                    i += 1
                while i < n and text[i] not in " \t\n;|&()<>":
                    i += 1
        elif c == "&" and text.startswith(">", i + 1):
            end_word()
            i += 1  # `&>file`: the `>` is handled next
            word = ["&"]
        elif c == "$" and text.startswith("(", i + 1):
            end_segment("$(")
            i += 2
        elif c in SEPARATORS:
            separator = text[i : i + 2] if text.startswith(("&&", "||"), i) else c
            end_segment(separator)
            i += len(separator)
        else:
            word = (word or []) + [c]
            i += 1
    end_segment()
    return segments


def _double_quoted(text: str, i: int) -> tuple[str, int]:
    out: list[str] = []
    n = len(text)
    while i < n and text[i] != '"':
        if text[i] in "\\`" and i + 1 < n and text[i + 1] in '"\\$`':
            out.append(text[i + 1])
            i += 2
        else:
            out.append(text[i])
            i += 1
    return "".join(out), i + 1


def _heredoc_body(text: str, i: int, delimiter: str, strip_tabs: bool) -> tuple[str, int]:
    lines = []
    while i < len(text):
        end = text.find("\n", i)
        end = len(text) if end < 0 else end
        line = text[i:end].rstrip("\r")
        i = end + 1
        if (line.lstrip("\t") if strip_tabs else line).strip() == delimiter:
            return "\n".join(lines), i
        lines.append(line)
    return "\n".join(lines), len(text)


def _skip_arithmetic(text: str, i: int) -> int:
    depth = 0
    while i < len(text):
        if text[i] == "(":
            depth += 1
        elif text[i] == ")":
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    return i


def _redirect(text: str, i: int, c: str) -> int:
    i += 1
    if c == ">" and i < len(text) and text[i] in ">|":
        i += 1
    return i


def _skip_fd(text: str, i: int) -> int:
    i += 1  # the `&` of `>&1` or `2>&-`
    while i < len(text) and (text[i].isdigit() or text[i] == "-"):
        i += 1
    return i


# Reading a segment ------------------------------------------------------------


def _resolve(words: list[str]) -> tuple[str, str, list[str]]:
    """Return the real command word (bare and lowercased), as written, and its arguments."""

    i = 0
    while i < len(words):
        word = words[i]
        name = _bare(word)
        if re.match(r"^[A-Za-z_]\w*=", word) or word in ("{", "}", "!") or word in SHELL_KEYWORDS:
            i += 1
        elif name in WRAPPERS:
            i += 1
            takes_value = WRAPPERS[name]
            while i < len(words) and (words[i].startswith("-") or "=" in words[i]):
                i += 2 if words[i] in takes_value else 1
            if name == "timeout" and i < len(words):
                i += 1  # the duration
        elif name == "cmd" and i + 1 < len(words) and words[i + 1].lower() in ("/c", "/k"):
            i += 2
            while i < len(words) and words[i].startswith("/") and len(words[i]) == 2:
                i += 1
        else:
            return name, word, words[i + 1 :]
    return "", "", []


def _bare(word: str) -> str:
    name = word.replace("\\", "/").rsplit("/", 1)[-1].lower()
    for suffix in (".exe", ".cmd", ".bat"):
        if name.endswith(suffix):
            return name[: -len(suffix)]
    return name


def _printed_files(name: str, args: list[str]) -> list[str]:
    """The files the file printer `name` prints, read from `args`."""

    values = FILE_PRINTERS[name]
    if name in PS_FILE_PRINTERS:
        return _ps_paths(args, values)
    return _positional(_drop_values(args, values))


def _sets_status(segments: list["_Segment"], index: int) -> bool:
    """True when the command fails whenever segment `index` fails: it sits in
    the command's trailing `&&` chain, every separator after it `&&` or a
    later pipe, so no `;`, `||`, newline, or `&` lets a later command set the
    exit status instead (`cat a || true` succeeds with no print)."""

    return segments[index].after in AND_THEN and all(
        later.after in (*AND_THEN, "|") for later in segments[index + 1:])


def _printed(name: str, args: list[str], segment: "_Segment",
             shell: str) -> tuple[list[str], bool]:
    """The files the printer `name` (a `FILE_PRINTERS` name or `sed`), run
    in `shell`, shows the agent, as written, and whether it shows them
    whole, as `ShellCommand.file_prints` and `whole_prints` say. The caller
    checks that the command's exit status is the print's."""

    if segment.nested or segment.after in ("|", "&") or segment.out_redirects:
        return [], False
    if name == "sed":
        # Only `-n` prints just the lines its script asks for; `-i` writes.
        quiet = not _edits_in_place(args) and any(
            arg in ("--quiet", "--silent") or (arg[:1] == "-" and arg[1:2] != "-" and "n" in arg)
            for arg in args)
        printed = _in_place_files(name, args) if quiet and not _sed_may_write(args) else []
        whole = False
    elif name in ("head", "tail"):
        # A program of its own in either shell: no PowerShell command has these names.
        printed, whole = _printed_files(name, args), False
    elif shell == POSIX:
        # A posix `type` describes commands; only `cat` prints there.
        printed, whole = (_printed_files(name, args) if name == "cat" else []), True
    else:
        # PowerShell's `cat` is an alias of Get-Content, so it takes the same parameters.
        printed = _printed_files("get-content", args)
        whole = not any(_is_range_param(arg) for arg in args)
    # A word the shell expands may name no file, or several.
    return [path for path in printed if _plain(path) and not path.startswith("~")], whole


# A `w` or `W` command, or an `s` command's `w` flag, followed by its file name
# or the script's end: such a script writes a file, and may print nothing.
SED_WRITE_RE = re.compile(r"[wW](\s|$)")


def _sed_may_write(args: list[str]) -> bool:
    """True when `sed`'s script, as `args` give it, may write a file: it has a
    `w` or `W` command or flag (`SED_WRITE_RE`), or comes from a file (`-f`)
    the command does not show. A `w` inside a pattern may match too, which
    only leaves a print uncounted."""

    scripts, given, i = [], False, 0
    while i < len(args):
        arg = args[i]
        if arg in ("-f", "--file") or arg.startswith("--file=") or (
                arg[:1] == "-" and arg[1:2] != "-" and arg.endswith("f")):
            return True
        if arg in ("-e", "--expression") or (arg[:1] == "-" and arg[1:2] != "-"
                                             and arg.endswith("e")):
            scripts.append(args[i + 1] if i + 1 < len(args) else "")
            given, i = True, i + 2
            continue
        if arg.startswith("--expression="):
            scripts.append(arg.partition("=")[2])
            given = True
        i += 1
    if not given:
        scripts = _positional(args)[:1]
    return any(SED_WRITE_RE.search(script) for script in scripts)


def _is_range_param(arg: str) -> bool:
    """True when `arg` names a Get-Content range parameter, by any prefix."""

    param = arg.lower().partition(":")[0]
    return len(param) > 1 and param.startswith("-") and any(
        name.startswith(param) for name in PS_RANGE_PARAMS)


def _positional(args: list[str]) -> list[str]:
    out = []
    after_dashes = False
    for arg in args:
        if arg == "--" and not after_dashes:
            after_dashes = True
        elif after_dashes or not arg.startswith("-"):
            out.append(arg)
    return out


def _ps_paths(args: list[str], values: frozenset[str] = frozenset()) -> list[str]:
    """PowerShell-style arguments: -Path values first, then positional ones.
    `values` names more parameters, in lower case, whose value is no path."""

    named, positional = [], []
    i = 0
    while i < len(args):
        arg = args[i]
        low = arg.lower()
        if low.startswith("-") and len(arg) > 1:
            param, _, attached = low.partition(":")
            if param in PS_VALUE_PARAMS or param in values:
                value = args[i][len(param) + 1 :] if attached else (
                    args[i + 1] if i + 1 < len(args) else ""
                )
                if param in PS_PATH_PARAMS and value:
                    named.append(value)
                i += 1 if attached else 2
                continue
            i += 1
            continue
        positional.append(arg)
        i += 1
    return named + positional


def _pr_options(args: list[str], value_options: dict) -> dict[str, str]:
    """The values a pull-request command's `args` name, by role ("base",
    "head", "repository"; see `PR_VALUE_OPTIONS`), the last of each winning.
    An option takes its value as the next word, after `=`, or attached to a
    short option (`-Bmain`, `-B=main`); a value is never read as an option."""

    named: dict[str, str] = {}
    i = 0
    while i < len(args):
        arg = args[i]
        i += 1
        if arg in value_options:
            name, value = arg, args[i] if i < len(args) else None
            i += 1
        elif arg.startswith("--") and "=" in arg:
            name, value = arg.split("=", 1)
        elif not arg.startswith("--") and arg[:2] in value_options and len(arg) > 2:
            name, value = arg[:2], arg[2:].removeprefix("=")  # `-Bmain` or `-B=main`
        else:
            continue
        role = value_options.get(name)
        if role and value is not None:
            named[role] = value
    return named


def _repository_path(value: str) -> str:
    """The repository path a `--repo`/`-R` value names: `owner/repo`, or
    `group/sub/repo` on GitLab, without the host or URL it may come in
    (`github.com/owner/repo`, `https://host/owner/repo.git`,
    `git@host:owner/repo.git`). A first part holding a dot, before two more
    parts, is a host: owner and group names on GitHub hold none."""

    path = value.strip().rstrip("/").removesuffix(".git")
    if "://" in path:
        path = path.split("://", 1)[1].partition("/")[2]
    elif re.match(r"[^/@:]+@[^/:]+:", path):
        path = path.partition(":")[2]
    else:
        host, _, rest = path.partition("/")
        if "." in host and "/" in rest:
            path = rest
    return path


def _forge_verb(words: list[str]) -> str | None:
    """The verb after `gh pr` or `glab mr`, given the words after the noun,
    or None when there is none. Options before it are read as their parser
    (cobra) reads options it does not know: `--x=v`, an attached short form
    (`-Rx`, `-R=x`) and `--help`/`-h` are one word; any other `--x` or `-x`
    takes the next word as its value, so `gh pr --state create list` lists.
    `--` ends the options, and no verb follows it."""

    i = 0
    while i < len(words):
        word = words[i]
        if word == "--":
            return None
        if not word.startswith("-") or word == "-":
            return word
        whole = "=" in word or word in ("--help", "-h") or (
            not word.startswith("--") and len(word) > 2)
        i += 1 if whole else 2
    return None


def _skip_options(args: list[str], takes_value: set[str]) -> list[str]:
    i = 0
    while i < len(args) and args[i].startswith("-"):
        i += 2 if args[i] in takes_value else 1
    return args[i:]


def _edits_in_place(args: list[str]) -> bool:
    for arg in args:
        if arg == "--in-place" or arg.startswith("--in-place="):
            return True
        if arg.startswith("-") and not arg.startswith("--") and "i" in arg[1:].split(".", 1)[0]:
            return True
    return False


def _in_place_files(name: str, args: list[str]) -> list[str]:
    script_given = any(a in ("-e", "-f", "--expression", "--file") or (
        a.startswith("-") and not a.startswith("--") and a[-1:] in "ef") for a in args)
    files, skip_next = [], False
    for arg in args:
        if skip_next:
            skip_next = False
            continue
        if arg in ("-e", "-f", "--expression", "--file") or (
            arg.startswith("-") and not arg.startswith("--") and arg[-1:] in "ef"
        ):
            skip_next = True
            continue
        if not arg.startswith("-"):
            files.append(arg)
    return files if script_given or name in ("perl", "ruby") else files[1:]


def _download_target(name: str, args: list[str]) -> tuple[str | None, bool]:
    """Return (output file or None, whether it writes) for a download command.

    curl writes with `-o <file>` (also at the end of a cluster such as
    `-sSLo <file>`) or `-O`; wget writes by default, to `-O <file>` when given;
    PowerShell's Invoke-WebRequest, and its `curl` and `wget` aliases, write
    with `-OutFile <file>`.
    """

    out_flag = "O" if name == "wget" else "o"
    for i, arg in enumerate(args):
        value = args[i + 1] if i + 1 < len(args) else None
        if arg.lower() == "-outfile":
            return value, True
        option, eq, attached = arg.partition("=")
        if option in ("--output", "--output-document"):
            value = attached if eq else value
            return (None, False) if value == "-" else (value, True)
        if arg.startswith("-") and arg.endswith(out_flag + "-"):
            return None, False  # `wget -qO-`: to stdout
        if arg.startswith("-") and not arg.startswith("--") and arg[1:].isalpha():
            if arg.endswith(out_flag):
                return (None, False) if value == "-" else (value, True)
            if name == "curl" and "O" in arg:
                return None, True
        if arg in ("--remote-name", "--remote-name-all"):
            return None, True
    return None, name == "wget"


def _git_subcommand(args: list[str]) -> tuple[str, list[str]]:
    index = 0
    while index < len(args) and args[index].startswith("-"):
        index += 2 if args[index] in GIT_GLOBAL_WITH_VALUE else 1
    if index >= len(args):
        return "", []
    return args[index].lower(), args[index + 1 :]


def _git_writes(sub: str, rest: list[str]) -> tuple[list[str], bool]:
    """Return (files written, whether others are written that the command does not name)."""

    if sub in GIT_UNKNOWN_TARGET_SUBCOMMANDS:
        return [], True
    if sub in ("mv", "rm"):
        return _positional(rest), False
    if sub == "restore":
        return [a for a in _positional(_drop_values(rest, {"-s", "--source"}))], False
    if sub == "checkout":
        if "--" in rest:
            return rest[rest.index("--") + 1 :], False
        if any(a in ("-b", "-B", "--orphan") for a in rest):
            return [], False
        positional = _positional(rest)
        if "--theirs" in rest or "--ours" in rest:
            return positional, False  # One side of a conflict: every positional is a path.
        # `git checkout <rev> <path>...` restores files; `git checkout <branch>` does not.
        return positional[1:], False
    if sub == "reset":
        return [], "--hard" in rest
    if sub == "stash":
        return [], bool(rest) and rest[0] in {"pop", "apply"}
    return [], False


def _git_prints_changes(sub: str, rest: list[str]) -> bool:
    """True when `git <sub> <rest>` prints changes' content: a diff or show
    without a listing-only option, a log, whatchanged, or stash show with a
    patch option, or format-patch to stdout."""

    if any(GIT_SILENT_FLAGS_RE.fullmatch(a) for a in rest):
        return False
    patch = any(GIT_PATCH_FLAGS_RE.fullmatch(a) for a in rest)
    if sub == "stash":
        return rest[:1] == ["show"] and patch
    if sub in GIT_PATCH_BY_DEFAULT:
        listing = any(a == "-s" or a.startswith(GIT_NO_PATCH_FLAGS) for a in rest)
        return patch or not listing
    if sub in ("log", "whatchanged"):
        return patch
    return sub == "format-patch" and "--stdout" in rest


def _drop_values(args: list[str], takes_value: set[str]) -> list[str]:
    out, skip = [], False
    for arg in args:
        if skip:
            skip = False
        elif arg in takes_value:
            skip = True
        else:
            out.append(arg)
    return out


# Checks -------------------------------------------------------------------------


def _runner_command(name: str, args: list[str]) -> tuple[str, str, list[str]]:
    """The command runner `name` (`uv run`, `npx`) runs with `args`, as
    `_resolve` returns one, or ("", "", []) when it runs none."""

    sub = COMMAND_RUNNERS[name]
    rest = args
    if sub:
        if not args or args[0] != sub:
            return "", "", []
        rest = args[1:]
    rest = _skip_options(rest, {"--with", "--python", "-p", "--extra", "--group",
                                 "--package", "--project", "--directory", "-e", "--env"})
    return (_bare(rest[0]), rest[0], rest[1:]) if rest else ("", "", [])


def _is_check(name: str, original: str, args: list[str]) -> bool:
    if not name:
        return False
    if name in CHECK_TOOLS:
        return True
    if name in SUBCOMMAND_CHECKS and args[:1] and args[0].lower() in SUBCOMMAND_CHECKS[name]:
        return True
    if name in SCRIPT_RUNNERS:
        rest = args[1:] if args[:1] and args[0] in ("run", "run-script") else args
        return bool(rest) and bool(CHECK_WORD_RE.fullmatch(rest[0]) or CHECK_WORD_RE.search(rest[0]))
    if name in TARGET_RUNNERS:
        return any(CHECK_WORD_RE.fullmatch(a) for a in args if not a.startswith("-"))
    if name in COMMAND_RUNNERS:
        inner, inner_original, inner_args = _runner_command(name, args)
        return _is_check(inner, inner_original, inner_args)
    if name in INTERPRETERS:
        code = _inline_code(name, args)
        if code is not None:
            # A shell's inline command line is read as one; other ad-hoc code
            # can do anything, so it is not a check.
            is_shell = name in ("pwsh", "powershell") or INLINE_CODE[name].shell
            return is_shell and analyze(code).is_check
        if "-m" in args:
            index = args.index("-m")
            return index + 1 < len(args) and args[index + 1] in CHECK_MODULES
        for flag in ("-File", "-file", "-f"):
            if flag in args and args.index(flag) + 1 < len(args):
                return _is_check_script(args[args.index(flag) + 1])
        scripts = [a for a in args if not a.startswith("-")]
        return bool(scripts) and _is_check_script(scripts[0])
    if "/" in original.replace("\\", "/") or "." in name:
        return _is_check_script(original)
    return False


def _inline_code(name: str, args: list[str]) -> str | None:
    """The code interpreter `name` is given inline, or None when it runs a
    script, a module, standard input, or nothing."""

    if name in ("pwsh", "powershell"):
        return _powershell_code(args)
    kind, code = _interpreter_program(name, args)
    return code if kind == "code" else None


def _interpreter_program(name: str, args: list[str]) -> tuple[str, str]:
    """What interpreter `name` (an `INLINE_CODE` key) runs with `args`:
    ("code", the code) for inline code, ("stdin", "") for standard input
    (`python -`, or no script named), or ("other", "") for a script, a
    module, or an interpreter it does not know. Only its own options are
    read, those before a module or script (`python -m pytest -c setup.cfg`
    runs pytest), with combined short options (`-Bc`) and options that take
    a value."""

    options = INLINE_CODE.get(name)
    if options is None:
        return "other", ""
    i = 0
    while i < len(args):
        arg = args[i]
        if arg == "-":
            return "stdin", ""
        if arg == "--" or not arg.startswith("-"):
            return "other", ""
        if arg.startswith("--"):
            key, has_value, value = arg.partition("=")
            if key in options.long_code:
                return "code", value if has_value else _word_at(args, i + 1)
            i += 2 if key in options.long_values and not has_value else 1
            continue
        for j, letter in enumerate(arg[1:], 2):
            rest = arg[j:]
            if letter in options.code:
                return "code", rest if rest and options.attached else _word_at(args, i + 1)
            if letter in options.module:
                return "other", ""
            if letter in options.values:
                i += 0 if rest else 1  # an attached value, or the next word
                break
        i += 1
    return "stdin", ""


VERSIONED_PYTHON_RE = re.compile(r"^python(?:\d+(?:\.\d+)*)?$")


def _inline_script(name: str, args: list[str],
                   stdin: tuple[str, bool] | None) -> tuple[str, str, bool] | None:
    """The language and code of a script given inline to an interpreter in
    `script_writes.LANGUAGES` (`python3.12` reads as `python`), also through
    a runner (`uv run`, `npx`), and whether the shell may have expanded it
    (see `script_writes.writes`). The code is given by an inline-code option
    (`python -c`, `node -e`, `deno eval`), which counts as expanded, or is
    `stdin`, the text its standard input gets (see `_standard_input`), when
    it runs no script (`python -`, `deno run -`). None for a script file run
    by name, a module, or another command."""

    if name in COMMAND_RUNNERS:
        name, _, args = _runner_command(name, args)
    if VERSIONED_PYTHON_RE.match(name):
        name = "python"
    language = script_writes.LANGUAGES.get(name)
    if language is None:
        return None
    if name == "deno":
        sub = args[0] if args else ""
        rest = [a for a in args[1:] if a == "-" or not a.startswith("-")]
        if sub == "eval":
            return (language, rest[0], True) if rest else None
        if sub == "run" and rest[:1] == ["-"] and stdin:
            return language, *stdin
        return None
    if name == "bun" and args[:1] == ["run"]:
        args = args[1:]
    kind, code = _interpreter_program(name, args)
    if kind == "code":
        return language, code, True
    if kind == "stdin" and stdin:
        return language, *stdin
    return None


def _standard_input(segment: "_Segment") -> tuple[str, bool] | None:
    """The text `segment`'s own heredocs or `<<<` here-strings feed its
    standard input, and whether the shell expands it: a heredoc does unless
    every delimiter is quoted (`<<'EOF'`); a here-string always may."""

    if segment.heredocs:
        return "\n".join(segment.heredocs), not all(segment.quoted_heredocs)
    if segment.here_strings:
        return "\n".join(segment.here_strings), True
    return None


# Programs that print their arguments, as a pipe into an interpreter feeds them.
ECHOES = frozenset({"echo", "write-output", "write"})


def _piped_text(segment: "_Segment") -> tuple[str, bool] | None:
    """The text a text producer pipes on, and whether the shell expands it,
    or None when `segment` is anything else: `cat` with no file, fed a
    heredoc; `echo`, `printf`, or `Write-Output` with their arguments; or a
    PowerShell string or here-string alone, which outputs itself. A word
    alone counts as such a string when it was quoted, or holds a space,
    newline, or parenthesis, which no command name does."""

    name, _, args = _resolve(segment.words)
    if name == "cat" and not _positional(args):
        return _standard_input(segment)
    if name in ECHOES:
        return " ".join(a for a in args if a not in ("-n", "-e", "-E")), True
    if name == "printf" and args:
        return " ".join(args[1:] or args), True
    if len(segment.words) == 1 and (segment.quoted_words[0]
                                    or any(c in segment.words[0] for c in " \n(")):
        return segment.words[0], True
    return None


# Writers that put new text into the files they name (`text_writes`): `tee`
# copies its input; the content cmdlets write their -Value or their input;
# `New-Item` writes text only when given a -Value.
TEXT_COPIERS = frozenset({"tee", "tee-object"})
TEXT_WRITERS = frozenset({"set-content", "sc", "add-content", "ac", "out-file"})
TEXT_CREATORS = frozenset({"new-item", "ni"})
# The content cmdlets whose second positional argument, after the path, is
# the text (`Set-Content f.txt 'x'`); `Out-File`'s is an encoding.
POSITIONAL_VALUE = frozenset({"set-content", "sc", "add-content", "ac"})
PS_TEXT_PARAMS = frozenset({"-value", "-inputobject"})
PS_PATH_NAMES = frozenset({"-path", "-literalpath", "-filepath"})
# Marks of text the shell fills in when it runs: a variable, a command
# substitution or subexpression (`$(…)`), or a backtick substitution or escape.
EXPANSION_MARKS = ("$", "`")


def _shown_lines(text: tuple[str, bool] | None) -> int | None:
    """How many lines of written text the command shows, from `text` as
    `_piped_text` gives it, or None when it shows none: no text, or text the
    shell expands that holds an expansion mark, whose result the command
    does not show. A final newline opens no line; `printf`'s `\\n` escapes
    are not expanded."""

    if text is None or (text[1] and any(mark in text[0] for mark in EXPANSION_MARKS)):
        return None
    return len(text[0].rstrip("\n").split("\n"))


def _ps_has_value(args: list[str]) -> bool:
    """Whether a PowerShell cmdlet's arguments name a `-Value` or `-InputObject`."""

    return any(a.lower().partition(":")[0] in PS_TEXT_PARAMS for a in args)


def _ps_written_lines(name: str, args: list[str], piped: tuple[str, bool] | None) -> int | None:
    """`_shown_lines` of the text PowerShell cmdlet `name` writes: its
    `-Value` or `-InputObject`; else, for `POSITIONAL_VALUE` cmdlets, the
    positional argument after the path (the first one when `-Path` names the
    path); else what is `piped` into it. A value the segment does not hold
    whole, such as `(Get-Content x)`, which ends the segment, or an `@(…)`
    array, is not shown."""

    positional: list[str] = []
    path_named = False
    i = 0
    while i < len(args):
        param, colon, attached = args[i].lower().partition(":")
        if param.startswith("-") and len(param) > 1:
            if param in PS_TEXT_PARAMS:
                value = args[i][len(param) + 1:] if colon else _word_at(args, i + 1)
                return _shown_lines((value, True)) if value.strip("@") else None
            path_named = path_named or param in PS_PATH_NAMES
            i += 2 if param in PS_VALUE_PARAMS and not colon else 1
            continue
        positional.append(args[i])
        i += 1
    at = 0 if path_named else 1
    if name in POSITIONAL_VALUE and len(positional) > at:
        return _shown_lines((positional[at], True))
    return _shown_lines(piped)


def _powershell_code(args: list[str]) -> str | None:
    """The command line `pwsh -Command` runs (its remaining words), "" for an
    -EncodedCommand, which cannot be read, or None for a script file."""

    i = 0
    while i < len(args):
        arg = args[i].lower()
        if not arg.startswith("-"):
            return None  # the script file, PowerShell's first positional
        if arg == "-c" or (len(arg) >= 4 and "-command".startswith(arg)):
            return " ".join(args[i + 1 :])
        if arg in ("-e", "-ec") or (len(arg) >= 3 and "-encodedcommand".startswith(arg)):
            return ""
        if arg in ("-f", "-file"):
            return None
        i += 2 if arg in PS_VALUE_OPTIONS else 1
    return None


def _word_at(words: list[str], index: int) -> str:
    return words[index] if index < len(words) else ""


def _is_check_script(path: str) -> bool:
    stem = path.replace("\\", "/").rsplit("/", 1)[-1].rsplit(".", 1)[0]
    return bool(CHECK_WORD_RE.search(stem))


# Commit messages ------------------------------------------------------------------

SUBSTITUTED_HEREDOC_RE = re.compile(
    r"^\$\(\s*cat\s*<<-?\s*(['\"]?)([A-Za-z_][\w.-]*)\1[ \t]*\r?\n(.*?)\r?\n[ \t]*\2[ \t]*\r?\n?\s*\)\s*$",
    re.DOTALL,
)
# Short options of `git commit` that take a value.
COMMIT_VALUE_FLAGS = "mFcCt"


def _commit_message(args: list[str], heredocs: list[str]) -> str | None:
    """Return the message a `git commit` segment carries inline, or None.

    Several `-m` options join as paragraphs, as git joins them, and a cluster
    such as `-am` counts. A heredoc fed to `-F -`, or inside
    `-m "$(cat <<'EOF' ... EOF)"`, gives its body. A message in a file, reused
    from another commit (`-c`, `-C`), or written in an editor is not in the
    command, so the answer is None.
    """

    parts: list[str] = []
    stdin = False
    i = 0
    while i < len(args):
        arg = args[i]
        nxt = args[i + 1] if i + 1 < len(args) else None
        if arg == "--":
            break
        if arg.startswith("--"):
            option, eq, value = arg.partition("=")
            if option in ("--message", "--file", "--reuse-message", "--reedit-message"):
                if not eq:
                    value, i = nxt or "", i + 1
                if option == "--message":
                    parts.append(value)
                elif option == "--file" and value == "-":
                    stdin = True
                else:
                    return None
        elif arg.startswith("-") and len(arg) > 1:
            for k, flag in enumerate(arg[1:], 1):
                if flag not in COMMIT_VALUE_FLAGS:
                    continue
                value = arg[k + 1 :]
                if not value:
                    value, i = nxt or "", i + 1
                if flag == "m":
                    parts.append(value)
                elif flag == "F" and value == "-":
                    stdin = True
                elif flag in "FcC":
                    return None
                break
        i += 1
    if stdin:
        return heredocs[0].strip("\n") if heredocs else None
    resolved = []
    for part in parts:
        match = SUBSTITUTED_HEREDOC_RE.match(part)
        if match:
            resolved.append(match.group(3))
        elif "$(" in part:
            return None  # Another command substitution: not knowable.
        else:
            resolved.append(part)
    return "\n\n".join(resolved) if resolved else None


# Package installs ---------------------------------------------------------------

_PIP_VALUES = frozenset({
    "-r", "--requirement", "-c", "--constraint", "-i", "--index-url", "--extra-index-url",
    "-f", "--find-links", "-t", "--target", "--prefix", "--root", "--python", "--platform",
    "--src", "--cache-dir",
})
# Package managers by command word: the subcommands that install or add a
# dependency or tool (spec G3), and the options that take a separate value (a
# file, folder, index, filter, or version) which is not a package. An option
# missing here leaves its value behind as a package; an `--opt=value` is one
# word and never does. Pip's `-e` is left out on purpose: its value is a local
# path (not a package) or a VCS URL (a package), which the word itself tells.
PACKAGE_MANAGERS: dict[str, tuple[tuple[tuple[str, ...], ...], frozenset[str]]] = {
    "npm": ((("install",), ("i",), ("add",)), frozenset({
        "-w", "--workspace", "--prefix", "--registry", "--tag", "--omit", "--include",
        "--cache", "--userconfig"})),
    "pnpm": ((("add",), ("install",), ("i",)), frozenset({
        "-F", "--filter", "-C", "--dir", "--registry", "--store-dir"})),
    "yarn": ((("add",), ("global", "add")), frozenset({"--cwd", "--registry", "--modules-folder"})),
    "bun": ((("add",), ("install",), ("i",)), frozenset({"--cwd", "--registry", "--backend",
                                                       "--cache-dir"})),
    "pip": ((("install",),), _PIP_VALUES),
    "pip3": ((("install",),), _PIP_VALUES),
    "uv": ((("add",), ("pip", "install"), ("tool", "install")), _PIP_VALUES | frozenset({
        "--requirements", "--constraints", "-p", "--index", "--default-index", "--directory",
        "--project", "--package", "--group", "--optional", "--extra", "--branch", "--tag",
        "--rev", "--from", "-w", "--with", "--with-requirements"})),
    "poetry": ((("add",),), frozenset({"-G", "--group", "--source", "--python", "-E", "--extras",
                                      "-C", "--directory"})),
    "pipx": ((("install",),), frozenset({"--python", "--suffix", "-i", "--index-url",
                                        "--pip-args"})),
    "conda": ((("install",),), frozenset({"--file", "-c", "--channel", "-n", "--name", "-p",
                                         "--prefix"})),
    "cargo": ((("add",), ("install",)), frozenset({
        "--path", "--branch", "--tag", "--rev", "--version", "--vers", "--root", "--features",
        "-F", "--package", "-p", "--registry", "--index", "--target", "--manifest-path",
        "--rename", "-j", "--jobs", "--profile", "--target-dir", "--config"})),
    "go": ((("get",), ("install",)), frozenset({"-C", "-modfile"})),
    "gem": ((("install",),), frozenset({"-v", "--version", "-i", "--install-dir", "-s", "--source",
                                       "-n", "--bindir"})),
    "brew": ((("install",),), frozenset()),
    "apt": ((("install",),), frozenset({"-o", "--option", "-t", "--target-release", "-c",
                                       "--config-file"})),
    "apt-get": ((("install",),), frozenset({"-o", "--option", "-t", "--target-release", "-c",
                                           "--config-file"})),
    "winget": ((("install",),), frozenset({
        "-s", "--source", "-v", "--version", "--scope", "-l", "--location", "--override",
        "--custom", "-o", "--log", "-a", "--architecture", "--locale", "-m", "--manifest",
        "--header"})),
    "choco": ((("install",),), frozenset({"--version", "-s", "--source", "--params",
                                         "--package-parameters", "--install-arguments", "--ia",
                                         "--cache-location"})),
    "scoop": ((("install",),), frozenset({"-a", "--arch"})),
}
LOCAL_PATH_RE = re.compile(r"^(?:[.~/\\]|[A-Za-z]:[\\/])")


# Installs that put a tool on the machine, not in a project, so they count
# for the Setup item wherever they run (spec R14), by command word: the
# subcommands that do, or None for every install the command makes.
GLOBAL_INSTALLS: dict[str, tuple[tuple[str, ...], ...] | None] = {
    "uv": (("tool", "install"),), "yarn": (("global", "add"),), "cargo": (("install",),),
    "go": (("install",),), "pipx": None, "gem": None, "brew": None, "apt": None,
    "apt-get": None, "winget": None, "choco": None, "scoop": None,
}
# The arguments that make an install global or per-user, whatever folder it runs in.
GLOBAL_OPTIONS = {
    "npm": frozenset({"-g", "--global", "--location=global"}),
    "pnpm": frozenset({"-g", "--global"}),
    "bun": frozenset({"-g", "--global"}),
    "pip": frozenset({"--user"}),
    "pip3": frozenset({"--user"}),
}
# The options that name the folder an install goes into, in place of the
# folder it runs in (each also in its manager's value options above).
FOLDER_OPTIONS = {
    "npm": ("--prefix",), "pnpm": ("--dir", "-C"), "yarn": ("--cwd",), "bun": ("--cwd",),
    "uv": ("--project", "--directory"), "poetry": ("-C", "--directory"), "go": ("-C",),
}


class _PackageInstall(NamedTuple):
    """A command's install of a package it names: whether it is global (or
    per-user, or run under `sudo`), so it counts wherever it runs, and the
    folder a folder option names, None when no option names one."""

    is_global: bool
    folder: str | None


def _package_install(name: str, args: list[str], elevated: bool = False) -> _PackageInstall | None:
    """The install `name args` makes when it installs or adds a package it
    names, else None, so a bare restore (`npm install`, `pip install -r
    requirements.txt`) is not one. A local path (`.`, `../lib`, `C:/pkg`) is
    not a package; a URL is. `elevated`: the command runs under `sudo`."""

    if name in ("python", "python3", "py") and args[:2] == ["-m", "pip"]:
        name, args = "pip", args[2:]
    if name not in PACKAGE_MANAGERS:
        return None
    subcommands, value_options = PACKAGE_MANAGERS[name]
    words = [a for a in _drop_values(args, value_options) if not a.startswith("-")]
    for sub in subcommands:
        if tuple(words[: len(sub)]) == sub:
            if not any("://" in w or not LOCAL_PATH_RE.match(w) for w in words[len(sub):]):
                return None
            machine = GLOBAL_INSTALLS.get(name, ())
            is_global = (elevated or machine is None or sub in machine
                         or bool(GLOBAL_OPTIONS.get(name, frozenset()) & set(args)))
            return _PackageInstall(is_global, _last_value(args, FOLDER_OPTIONS.get(name, ())))
    return None


def _last_value(args: list[str], options: tuple[str, ...]) -> str | None:
    """The value of the last of `options` in `args`, written `--opt value` or
    `--opt=value`, or None when none is given."""

    value = None
    for index, arg in enumerate(args):
        option, equals, inline = arg.partition("=")
        if option in options:
            value = inline if equals else (args[index + 1] if index + 1 < len(args) else None)
    return value
