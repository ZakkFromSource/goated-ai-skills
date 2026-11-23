"""Keeps the skill-usage mod's copies of the grammar, registry and adapter texts current.

The mod's tests run inside Claude Code's plugin test kit, which has no file
system, YAML parser, or Python, so they read generated TypeScript modules:

- `marker-fixtures.ts`, the marker fixtures in `stack/fixtures/markers/lines.yaml`;
- `registry-fixture.ts`, the source registry `stack/goated-stack.yaml` with the
  references each skill declares, as a full YAML parser reads them, so the mod's
  own reader is tested against both;
- `adapter-texts.ts`, the hold reasons and the override context the Claude Code
  adapter actually produces, from driving it with synthetic sessions;
- `usage-log-session.ts`, one session driven through the adapter with the
  core's usage log on, as the rows the mod hears and as the log, so the mod's
  tests check that it counts the same from either (Ticket 082).

It also checks the one adapter fact the mod copies by hand: which file
extensions are code. This test fails when a module no longer matches its
source. Regenerate them with:

    uv run python tests/test_skill_usage_mod.py --write
"""

from __future__ import annotations

import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

from claude_code_adapter_support import BRIEF, ROUTER, Session, git_branch_with_change, parse, reason
from usage_log_session import recorded_session

REPO_ROOT = Path(__file__).resolve().parents[1]
# A whole backticked token shaped like a skill name, as the mod reads one from a hold.
BARE_BACKTICKED = re.compile(r"`([a-z0-9]+(?:-[a-z0-9]+)*)`")
MARKER_FIXTURES = REPO_ROOT / "stack" / "fixtures" / "markers" / "lines.yaml"
MOD_ROOT = REPO_ROOT / "adapters" / "claude-code" / "skill-usage"
GENERATED_MARKERS = MOD_ROOT / "tests" / "marker-fixtures.ts"
# The mod's copies of the adapter's code-file extensions and edit tools, in hooks/classify.ts.
MOD_CODE_EXTENSIONS = re.compile(r"const CODE_EXTENSIONS = new Set\(\s*'([^']*)'")
MOD_FILE_EDIT_TOOLS = re.compile(r"const FILE_EDIT_TOOLS: Record<string, string> = \{([^}]*)\}")
GENERATED_ADAPTER_TEXTS = MOD_ROOT / "tests" / "adapter-texts.ts"
REGISTRY = REPO_ROOT / "stack" / "goated-stack.yaml"
GENERATED_REGISTRY = MOD_ROOT / "tests" / "registry-fixture.ts"
GENERATED_USAGE_LOG_SESSION = MOD_ROOT / "tests" / "usage-log-session.ts"


def _module(source: str, name: str, value: object) -> str:
    header = (
        f"// Generated from {source} by\n"
        "// `uv run python tests/test_skill_usage_mod.py --write`; do not edit by hand.\n"
        "// tests/test_skill_usage_mod.py fails when this copy drifts from its source.\n"
    )
    body = json.dumps(value, indent=2, ensure_ascii=False)
    return f"{header}\nexport const {name} = {body} as const\n"


def render_marker_fixtures() -> str:
    fixtures = yaml.safe_load(MARKER_FIXTURES.read_text(encoding="utf-8"))
    return _module("stack/fixtures/markers/lines.yaml", "MARKER_FIXTURES", fixtures)


def render_registry_fixture() -> str:
    """The registry's text, and each skill's references as `enforced` (a signal) or `advisory`, file by file."""
    text = REGISTRY.read_text(encoding="utf-8")
    declared = {
        skill["name"]: {ref["file"]: "enforced" if "signal" in ref else "advisory" for ref in skill["references"]}
        for skill in yaml.safe_load(text)["skills"]
        if skill.get("references")
    }
    return _module("stack/goated-stack.yaml", "REGISTRY_FIXTURE", {"text": text, "declared": declared})


def _write(path: str, lines: int = 6) -> dict:
    """A write tool's input adding `lines` lines: six count as a substantial change."""

    return {"file_path": path, "content": "\n".join(f"line {n}" for n in range(lines))}


def _edit(path: str, new: str) -> dict:
    """An edit tool's input adding `new` in place of one line."""

    return {"file_path": path, "old_string": "pass", "new_string": new}


# A brief from the reviewer prompt, which starts a reviewer subagent.
REVIEWER_BRIEF = (
    "## Review Mode\n\nSpec review of the export change.\n\n## Review Inputs\n\n- The diff.\n\n"
    "## Required Report Format\n\n- Findings with file paths.\n\n"
    "goated-skills: standards-and-spec-review\n"
)
# Six added lines that trip no design-reads signal.
PLAIN = "\n".join(f"total_{n} = {n}" for n in range(6))


def _stop_reason(s: Session) -> str:
    """The reason the closeout gate blocks `Stop` with, or "" when it lets the turn end."""

    return parse(s.hook("Stop", stop_hook_active=False, last_assistant_message="")).get("reason", "")


def _adapter_texts() -> dict[str, str]:
    """Drive the adapter through one synthetic session per text and keep what it says.

    A hold's text is its reason, as a denied tool call or a blocked `Stop`
    carries it; the override text is the hook context the mod reads.
    """

    texts: dict[str, str] = {}
    with tempfile.TemporaryDirectory() as tmp:
        def session(name: str) -> Session:
            folder = Path(tmp) / name
            folder.mkdir()
            return Session(folder)

        def routed(name: str, route: str = "goated-route: direct") -> Session:
            s = session(name)
            s.prompt("Add CSV export.")
            s.load(ROUTER)
            s.say(route)
            return s

        first = session("router-first")
        first.prompt("Add CSV export.")
        # A command meets router-first alone; an edit meets route-line with it (Ticket 095).
        texts["routerFirst"] = reason(first.call("Bash"))

        unrouted = session("route-line")
        unrouted.prompt("Add CSV export.")
        unrouted.load(ROUTER)
        texts["routeLine"] = reason(unrouted.call("Edit"))

        piped = routed("pipeline", "goated-route: standard | requires: tdd, doc-sync")
        texts["pipeline"] = reason(piped.call("Edit"))

        # A session started from a brief also loads the orientation skill (Ticket 072).
        briefed = session("pipeline-brief")
        orientation = briefed.config.home / ".claude" / "skills" / "session-start-progressive-disclosure"
        orientation.mkdir(parents=True)
        (orientation / "SKILL.md").write_text("---\nname: x\n---\n", encoding="utf-8")
        briefed.prompt(
            "Background (from the session that started this one):\nAdd CSV export.\n\n"
            "goated-route: standard | requires: tdd",
            origin=None,
            turnOrigin="host_synthetic",
        )
        briefed.load("tdd")
        texts["pipelineBrief"] = reason(briefed.call("Edit"))

        texts["commit"] = reason(routed("commit").call("Bash", {"command": 'git commit -m "Add export"'}))
        texts["pullRequest"] = reason(
            routed("pull-request").call("Bash", {"command": 'gh pr create --title "Add export" --body "Adds it."'})
        )

        spawn = routed("spawn")
        texts["spawn"] = reason(spawn.call("Agent", {"prompt": BRIEF}))
        spawn.load("subagent-driven-development")
        texts["spawnRead"] = reason(spawn.call("Agent", {"prompt": BRIEF}))

        texts["design"] = reason(routed("design").call("Write", _write("src/export.py")))
        # A shell write's design hold says the Edit tool keeps line endings (round 7, R6).
        texts["designShellWrite"] = reason(routed("design-shell-write").call(
            "Bash", {"command": f"cat > src/export.py <<'EOF'\n{PLAIN}\nEOF"}))
        # Once the skill loads: the design hold asks for the references the edit requires
        # and no design-reads line (Ticket 089), then the design-reads hold for a later
        # edit's references. Since Ticket 118 the main agent's file edit lands owing
        # those reads, so the holds come from a subagent's edits, which keep no owed reads.
        designer = routed("design-reads")
        designed = designer.subagent("d1")
        designed.prompt("Add CSV export.", hook=False)
        designed.load("software-design-principles")
        as_agent = {"agent_id": "d1", "agent_type": "general-purpose"}
        texts["designFirstReads"] = reason(designed.call("Write", _write("src/export.py"), **as_agent))
        designed.call("Edit", _edit("src/export.py", PLAIN), **as_agent)
        texts["designReads"] = reason(designed.call(
            "Edit", _edit("src/export.py", "try:\n    rate = 1"), **as_agent))
        # The references the registry declares for a loaded skill's signals (Ticket 067): one
        # write firing a reference of each of two skills. Since Ticket 118 a file edit lands
        # owing its reads, so the hold real sessions meet is a short shell write's: here a
        # ticket copied in after a check failed twice, which fires spec-to-tickets' path
        # signal and diagnose's signal for that gate.
        referenced = routed("reference-reads")
        referenced.config.registry_path = REPO_ROOT / "stack" / "goated-stack.yaml"
        referenced.load("spec-to-tickets")
        referenced.load("diagnose")
        referenced.run("pytest -q", success=False)
        referenced.run("pytest -q", success=False)
        texts["referenceReads"] = reason(referenced.call(
            "Bash", {"command": "cp draft.md tickets/001-export.md"}))
        # A reviewer subagent's report holds the fixes until receiving-code-review loads (Ticket 070).
        intake = routed("review-intake")
        intake.load("subagent-driven-development")
        intake.read("/skills/subagent-driven-development/references/reviewer-prompt.md")
        intake.subagent("r1").prompt("Review the change.", hook=False)
        intake.spawn("r1", REVIEWER_BRIEF)
        texts["reviewIntake"] = reason(intake.call("Edit", _edit("src/export.py", "rate = 2")))
        texts["security"] = reason(routed("security").call("Write", _write("src/auth.py", lines=2)))
        # A shell write is held like a write tool's: here, to a dependency manifest.
        texts["shellWrite"] = reason(
            routed("shell-write").call("Bash", {"command": "echo requests >> requirements.txt"})
        )

        # An inline script writing a code file is held for a file edit tool (Ticket 093).
        texts["scriptedEdit"] = reason(routed("scripted-edit").call(
            "Bash", {"command": "python - <<'EOF'\nopen(\"src/export.py\", \"w\").write(text)\nEOF"}))

        failing = routed("repeated-failure")
        failing.run("pytest -q", success=False)
        failing.run("pytest -q", success=False)
        texts["repeatedFailure"] = reason(
            failing.call("Edit", {"file_path": "src/export.py", "old_string": "a", "new_string": "b"})
        )

        # One write that meets three gates: one message carries the three holds (Ticket 095).
        # It is a short shell write, since the read gates let a file edit land (Ticket 118):
        # a settings file selects a design reference, and a spec a registry one.
        joint = routed("joint")
        joint.config.registry_path = REPO_ROOT / "stack" / "goated-stack.yaml"
        joint.load("software-design-principles")
        joint.load("write-a-spec")
        joint.run("pytest -q", success=False)
        joint.run("pytest -q", success=False)
        texts["jointTestEdit"] = reason(joint.call("Bash", {
            "command": "cp a.md docs/specs/export.md && generate-settings > config/export.json"}))
        # A gate's second hold in a turn is short (Ticket 095).
        repeated = routed("security-short")
        repeated.call("Write", _write("src/auth.py", lines=2))
        texts["securityShort"] = reason(repeated.call("Write", _write("src/auth.py", lines=2)))

        closing = routed("closeout")
        closing.say("goated-skip: software-design-principles: one mechanical constant change")
        closing.call("Write", _write("src/export.py"))
        texts["closeout"] = _stop_reason(closing)
        texts["closeoutShort"] = _stop_reason(closing)

        # The other closeout items: a failed last check (Unfinished) and the design skill's red flags.
        unfinished = routed("closeout-unfinished")
        unfinished.load("software-design-principles")
        unfinished.call("Edit", _edit("src/export.py", PLAIN))
        unfinished.run("pytest -q", success=False)
        texts["closeoutUnfinished"] = _stop_reason(unfinished)

        # The Setup item alone: a package install, with no code change.
        installed = routed("closeout-setup")
        installed.run("uv add httpx")
        texts["closeoutSetup"] = _stop_reason(installed)

        contract = routed("commit-contract")
        contract.load("commit-message")
        texts["commitContract"] = reason(contract.call("Bash", {"command": f'git commit -m "{"x" * 80}"'}))

        # Holds whose step reviews or describes the change, once the skill is loaded: they ask for a change read.
        texts["commitRead"] = reason(contract.call("Bash", {"command": 'git commit -m "Add export"'}))
        described = routed("pull-request-read")
        described.load("pr-description")
        texts["pullRequestRead"] = reason(
            described.call("Bash", {"command": 'gh pr create --title "Add export" --body "Adds it."'})
        )
        # A large pull request, once the pull-request gate passes: the review hold, then its change read.
        # A change read after the last change meets the read before or after the load (Ticket 092),
        # so the read is asked for only when the user typed a skip of the pull-request gate's skill.
        large = session("pr-review")
        large.prompt("Open the pull request; skip pr-description.")
        large.load(ROUTER)
        large.say("goated-route: direct")
        git_branch_with_change(large.project, 450)
        open_pr = {"command": 'gh pr create --base main --title "Add export" --body "Adds it."'}
        texts["prReview"] = reason(large.call("Bash", open_pr))
        large.load("standards-and-spec-review")
        texts["prReviewRead"] = reason(large.call("Bash", open_pr))
        reviewed = routed("closeout-change-read")
        reviewed.load("software-design-principles")
        reviewed.load("code-security-review")
        reviewed.load("doc-sync")
        reviewed.load("verification-before-completion")  # Meets the Verification item its sensitive file raises.
        reviewed.call("Edit", _edit("src/auth.py", PLAIN))
        reviewed.run("pytest -q")
        reviewed.read("/skills/software-design-principles/references/red-flags.md")
        texts["closeoutChangeRead"] = _stop_reason(reviewed)
        # The closeout at a commit whose own hold is met (Ticket 059).
        committing = routed("closeout-commit")
        committing.say("goated-skip: software-design-principles: one mechanical constant change")
        committing.call("Write", _write("src/export.py"))
        committing.load("commit-message")
        committing.run("git diff")
        texts["closeoutCommit"] = reason(committing.call("Bash", {"command": 'git commit -m "Add export"'}))
        # The Review and Verification items alone: a turn's code change on a large branch (Ticket 069).
        reviewing = routed("closeout-review")
        git_branch_with_change(reviewing.project, 450)
        reviewing.say("goated-skip: software-design-principles: one mechanical constant change")
        reviewing.call("Write", _write("src/export.py"))
        reviewing.run("pytest -q")
        reviewing.say("goated-skip: doc-sync: internal constant with no documented behavior")
        texts["closeoutReview"] = _stop_reason(reviewing)

        headings = routed("spawn-headings")
        headings.brief_with_handoff()
        texts["spawnHeadings"] = reason(headings.call("Agent", {"prompt": "Audit the exporter."}))

        texts["securityNoExtension"] = reason(routed("security-no-extension").call("Write", _write(".env")))
        texts["conflictResolution"] = reason(routed("conflict-resolution").call("Edit", {
            "file_path": "src/app.py",
            "old_string": "<<<<<<< HEAD\nrate = 1\n=======\nrate = 2\n>>>>>>> feature\n",
            "new_string": "rate = 2\n",
        }))

        # The note after a turn's first code change, the context documents first (round 7, R11).
        noted = routed("closeout-note")
        noted.project.mkdir(parents=True, exist_ok=True)
        (noted.project / "CONTEXT.md").write_text("# Context\n", encoding="utf-8")
        small = _edit("src/export.py", "rate = 2")
        noted.call("Edit", small)
        texts["closeoutNote"] = parse(noted.hook(
            "PostToolUse", tool_name="Edit", tool_input=small, tool_use_id=noted._new_id(),
            tool_response={"filePath": "src/export.py", "success": True},
        ))["hookSpecificOutput"]["additionalContext"]

        overridden = session("override")
        context = parse(overridden.prompt("Skip routing and add CSV export."))["hookSpecificOutput"]
        texts["overrideContext"] = context["additionalContext"]
    return texts


def render_adapter_texts() -> str:
    return _module(
        "the Claude Code adapter's output (goated_adapter), driven with synthetic sessions",
        "ADAPTER_TEXTS",
        _adapter_texts(),
    )


def render_usage_log_session() -> str:
    return _module(
        "one synthetic Claude Code session driven through the adapter with the core's usage "
        "log on (tests/usage_log_session.py)",
        "USAGE_LOG_SESSION",
        recorded_session(),
    )


GENERATED = {
    GENERATED_MARKERS: render_marker_fixtures,
    GENERATED_ADAPTER_TEXTS: render_adapter_texts,
    GENERATED_REGISTRY: render_registry_fixture,
    GENERATED_USAGE_LOG_SESSION: render_usage_log_session,
}


class SkillUsageModFixtureTests(unittest.TestCase):
    def test_generated_modules_match_their_sources(self) -> None:
        for path, render in GENERATED.items():
            with self.subTest(path=path.name):
                self.assertTrue(path.is_file(), f"missing {path.relative_to(REPO_ROOT)}")
                self.assertEqual(
                    path.read_text(encoding="utf-8"),
                    render(),
                    f"{path.name} is stale; run `uv run python tests/test_skill_usage_mod.py --write`",
                )

    def test_adapter_texts_are_the_holds_and_notice_the_mod_reads(self) -> None:
        texts = _adapter_texts()
        self.assertTrue(texts["routerFirst"].startswith("goated-hold: router-first | strict\n"))
        self.assertTrue(texts["routeLine"].startswith("goated-hold: route-line | strict\n"))
        self.assertTrue(texts["pipeline"].startswith("goated-hold: pipeline | strict\n"))
        self.assertTrue(texts["pipelineBrief"].startswith("goated-hold: pipeline | strict\n"))
        self.assertIn("A session started from a brief loads `session-start-progressive-disclosure`", texts["pipelineBrief"])
        self.assertNotIn("The current route requires", texts["pipelineBrief"])
        self.assertNotIn("started from a brief", texts["pipeline"])
        self.assertIn('recorded your override for this prompt: "Skip routing"', texts["overrideContext"])
        gates = {
            "commit": "commit | strict",
            "pullRequest": "pull-request | strict",
            "prReview": "pr-review | justified-skip",
            "prReviewRead": "pr-review | justified-skip",
            "spawn": "spawn | strict",
            "spawnRead": "spawn | strict",
            "design": "design | justified-skip",
            "designShellWrite": "design | justified-skip",
            "designFirstReads": "design | justified-skip",
            "designReads": "design-reads | justified-skip",
            "referenceReads": "reference-reads | justified-skip",
            "reviewIntake": "review-intake | justified-skip",
            "security": "security | justified-skip",
            "shellWrite": "security | justified-skip",
            "repeatedFailure": "repeated-failure | justified-skip",
            "scriptedEdit": "scripted-edit | justified-skip",
            "closeout": "closeout | justified-skip",
            "closeoutUnfinished": "closeout | justified-skip",
            "closeoutSetup": "closeout | justified-skip",
            "closeoutCommit": "closeout | justified-skip",
            "closeoutReview": "closeout | justified-skip",
            "commitContract": "commit | strict",
            "spawnHeadings": "spawn | strict",
            "securityNoExtension": "security | justified-skip",
            "conflictResolution": "conflict-resolution | justified-skip",
            "jointTestEdit": "design-reads | justified-skip",
            "securityShort": "security | justified-skip",
            "closeoutShort": "closeout | justified-skip",
        }
        # A joint message keeps each hold's own line, in the order the gates fire (Ticket 095).
        self.assertEqual(re.findall(r"^goated-hold: (\S+) \|", texts["jointTestEdit"], re.MULTILINE),
                         ["design-reads", "reference-reads", "repeated-failure"])
        self.assertIn("Still unmet", texts["securityShort"])
        self.assertIn("Still unmet", texts["closeoutShort"])
        for key, line in gates.items():
            with self.subTest(key=key):
                self.assertTrue(texts[key].startswith(f"goated-hold: {line}\n"), texts[key])
        self.assertIn("- Unfinished:", texts["closeoutUnfinished"])
        self.assertIn("- Design:", texts["closeoutUnfinished"])
        self.assertIn("- Setup:", texts["closeoutSetup"])
        # Round 7: the line-ending sentence on script and shell writes (R6), the commit's
        # read in an earlier message (R10), and the context documents first (R11).
        line_endings = "The Edit tool keeps a file's line endings, so CRLF is no reason"
        for key in ("scriptedEdit", "designShellWrite"):
            with self.subTest(key=key):
                self.assertIn(line_endings, texts[key])
        self.assertNotIn(line_endings, texts["design"])
        for key in ("commit", "commitRead", "commitContract"):
            with self.subTest(key=key):
                self.assertIn("Make that read in an earlier message than the commit", texts[key])
        self.assertNotIn("earlier message", texts["pullRequestRead"])
        self.assertTrue(texts["closeoutNote"].startswith(
            "GOATED Claude Code adapter: This project's own context documents"), texts["closeoutNote"])
        self.assertIn("`CONTEXT.md`.\nThis turn changed code", texts["closeoutNote"])
        # Ticket 089: no hold asks for a design-reads line or a citation; the near miss,
        # the design hold's references, is still asked for.
        for key, text in texts.items():
            with self.subTest(key=key):
                self.assertNotIn("design-reads line", text)
                self.assertNotIn("goated-design-reads", text)
                self.assertNotIn("file#id", text)
        self.assertIn("references/process.md", texts["designFirstReads"])
        self.assertIn("Before committing in this turn", texts["closeoutCommit"])
        self.assertIn("- Proof:", texts["closeoutCommit"])
        self.assertIn("- Review:", texts["closeoutReview"])
        self.assertIn("- Verification:", texts["closeoutReview"])

    def test_holds_a_line_can_clear_name_the_call_fields_and_the_user_way_out(self) -> None:
        # A route or skip line in reply text is recorded only after the hook returns, and Claude
        # Code may store it as a narration summary that drops it (README "Known Limits"), so the
        # hint points to a tool call's description or a Skill call's args, then to the user's way out.
        # The full hint comes once per turn; a later such hold in the turn gives one sentence that
        # keeps the way out. The generator drives these keys as later holds in their turn.
        texts = _adapter_texts()
        later_in_turn = {"designReads", "prReviewRead", "securityShort"}
        ways_out = {
            "routeLine": "skip routing",
            "pipeline": "skip routing",
            "pipelineBrief": "skip routing",
            "design": "skip software-design-principles",
            "designFirstReads": "skip software-design-principles",
            "designReads": "skip software-design-principles",
            "referenceReads": "skip <skill>",
            "reviewIntake": "skip receiving-code-review",
            "security": "skip code-security-review",
            "shellWrite": "skip code-security-review",
            "securityNoExtension": "skip code-security-review",
            "conflictResolution": "skip resolving-merge-conflicts",
            "repeatedFailure": "skip diagnose",
            "scriptedEdit": "skip software-design-principles",
            "prReview": "skip standards-and-spec-review",
            "prReviewRead": "skip standards-and-spec-review",
            "securityShort": "skip code-security-review",
        }
        for key, way_out in ways_out.items():
            with self.subTest(key=key):
                if key in later_in_turn:
                    self.assertNotIn("may not be seen", texts[key])
                    self.assertIn("in a shell or agent call's description or a Skill call's args", texts[key])
                else:
                    self.assertIn("may not be seen", texts[key])
                    self.assertIn("description field of a shell or agent call, or in a Skill call's args", texts[key])
                self.assertIn(f"`{way_out}`", texts[key])

    def test_each_hold_and_closeout_item_opens_with_its_clearing_action(self) -> None:
        # Round 6, R11: the action first, conditions and caveats after. A hold line, a closeout
        # item's `- <Label>:`, the closeout's opening line, and a short form's
        # `Still unmet: <what>.` are labels the contract fixes, so the action follows them.
        imperatives = {"Load", "Read", "Write", "Run", "Fix", "Add", "Name", "Make", "Put", "End"}
        for key, text in _adapter_texts().items():
            if not text.startswith("goated-hold: "):
                continue
            for block in re.split(r"\n\n(?=goated-hold: )", text):
                hold_line, body = block.split("\n", 1)
                if " closeout " in hold_line:
                    openings = [line.split(": ", 1)[1] for line in body.splitlines()
                                if line.startswith("- ")]
                else:
                    openings = [re.sub(r"^Still unmet: .*?\. (?=[A-Z])", "", body)]
                for opening in openings:
                    with self.subTest(key=key, opening=opening[:60]):
                        self.assertIn(opening.split()[0].capitalize().rstrip(","), imperatives)

    def test_holds_backtick_only_skill_names(self) -> None:
        # The mod reads every bare backticked name in a hold as a skill it asks for (README "Hold messages"),
        # so a backticked file name, such as a security hold's `credentials`, would read as a phantom skill.
        registry = yaml.safe_load((REPO_ROOT / "stack" / "goated-stack.yaml").read_text(encoding="utf-8"))
        skills = {entry["name"] for entry in registry["skills"]}
        for key, text in _adapter_texts().items():
            if not text.startswith("goated-hold: "):
                continue
            with self.subTest(key=key):
                names = set(BARE_BACKTICKED.findall(text.split("\n", 1)[1]))
                self.assertEqual(names - skills, set(), text)

    def test_a_security_hold_on_a_file_named_like_a_word_names_no_extra_skill(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            s = Session(Path(tmp))
            s.prompt("Add CSV export.")
            s.load(ROUTER)
            s.say("goated-route: direct")
            held = reason(s.call("Write", _write("src/credentials")))
        self.assertTrue(held.startswith("goated-hold: security | justified-skip\n"), held)
        self.assertEqual(set(BARE_BACKTICKED.findall(held)), {"code-security-review"})

    def test_mod_counts_the_same_files_as_code_as_the_adapter(self) -> None:
        # The mod times reference reads against code changes, which it must judge as the adapter does.
        from goated_core.actions import CODE_EXTENSIONS
        from goated_adapter.translation import FILE_WRITE_TOOLS

        source = (MOD_ROOT / "hooks" / "classify.ts").read_text(encoding="utf-8")
        found = MOD_CODE_EXTENSIONS.search(source)
        self.assertIsNotNone(found, "hooks/classify.ts no longer declares CODE_EXTENSIONS as this test reads it")
        self.assertEqual(set(found.group(1).split()), set(CODE_EXTENSIONS))
        tools = MOD_FILE_EDIT_TOOLS.search(source)
        self.assertIsNotNone(tools, "hooks/classify.ts no longer declares FILE_EDIT_TOOLS as this test reads it")
        self.assertEqual(dict(re.findall(r"(\w+): '([^']+)'", tools.group(1))), FILE_WRITE_TOOLS)

    def test_mod_manifest_names_its_type_contract(self) -> None:
        manifest = json.loads((MOD_ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["name"], "skill-usage")
        self.assertTrue((MOD_ROOT / manifest["types"]).is_file())


if __name__ == "__main__":
    if "--write" in sys.argv:
        for path, render in GENERATED.items():
            path.write_text(render(), encoding="utf-8", newline="\n")
            print(f"wrote {path.relative_to(REPO_ROOT)}")
    else:
        unittest.main()
