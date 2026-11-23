"""Behavior tests for the Claude Code adapter's action, shell-write, and closeout gates.

Like `test_claude_code_adapter.py`, each test drives the adapter's single hook
entry point with hook inputs and a transcript in Claude Code's recorded shape
(see `claude_code_adapter_support.py`).
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from claude_code_adapter_support import (
    BRIEF,
    REPO_ROOT,
    ROUTER,
    SPAWN_BRIEF_PATH,
    Session,
    decision,
    git_branch_with_change,
    next_turn,
    owed,
    owed_names,
    parse,
    reason,
)

SHELL_WRITES = (
    ("Bash", "echo done > notes.txt"),
    ("Bash", "printf 'x' >> log.txt"),
    ("Bash", "make 2>&1 | tee build.log"),
    ("Bash", "sed -i 's/a/b/' src/app.py"),
    ("Bash", "sed -E -i.bak 's/a/b/' src/app.py"),
    ("Bash", "cp a.py b.py"),
    ("Bash", "mv old.py new.py"),
    ("Bash", "rm -rf build"),
    ("Bash", "cd src && rm stale.py"),
    ("Bash", "git apply fix.patch"),
    ("Bash", "git checkout -- src/app.py"),
    ("Bash", "git checkout HEAD~1 -- src/app.py"),
    ("Bash", "git checkout --theirs src/app.py"),
    ("Bash", "git checkout --ours ."),
    ("Bash", "cat <<'EOF' > src/new.py\nprint('hi')\nEOF"),
    ("PowerShell", "Set-Content -Path notes.txt -Value 'x'"),
    ("PowerShell", "'x' | Out-File notes.txt"),
    ("PowerShell", "Add-Content log.txt 'line'"),
    ("PowerShell", "Copy-Item a.py b.py"),
    ("PowerShell", "Move-Item a.py b.py"),
    ("PowerShell", "Remove-Item build -Recurse"),
    ("PowerShell", "del stale.txt"),
)

SHELL_FREE = (
    ("Bash", "git status"),
    ("Bash", "cat src/app.py"),
    ("Bash", "grep -n 'def ' src/app.py | head -5"),
    ("Bash", "uv run python -m unittest discover -s tests -v 2>&1 | tail -20"),
    ("Bash", "pytest -q 2>/dev/null"),
    ("Bash", "ls > /dev/null"),
    ("Bash", "echo 'a > b' && git diff --stat"),
    ("Bash", "sed -n '1,20p' src/app.py"),
    ("Bash", "git checkout main"),
    ("Bash", "git log --oneline -5"),
    ("PowerShell", "Get-Content notes.txt"),
    ("PowerShell", "Test-Path build 2>$null"),
)


class AdapterTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.session = Session(self.root)
        self._sessions = 0

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def fresh(self) -> Session:
        """A new session in its own folder, for subtests that need a clean start."""

        self._sessions += 1
        folder = self.root / f"s{self._sessions}"
        folder.mkdir()
        return Session(folder, session_id=f"session-{self._sessions}")

    def routed(self, route: str = "goated-route: direct", prompt: str = "Do the task.") -> Session:
        s = self.session
        s.prompt(prompt)
        s.load(ROUTER)
        s.say(route)
        return s


def hold_line(output: dict) -> str:
    return reason(output).split("\n", 1)[0]


class ShellWriteTests(AdapterTestCase):
    def test_shell_writes_meet_the_route_line_hold(self) -> None:
        for tool, command in SHELL_WRITES:
            with self.subTest(command=command):
                s = self.fresh()
                s.prompt("Tidy the build output.")
                s.load(ROUTER)
                held = s.call(tool, {"command": command})
                self.assertEqual(hold_line(held), "goated-hold: route-line | strict")
                s.say("goated-route: direct")
                self.assertEqual(decision(s.call(tool, {"command": command})), "pass")

    def test_shell_writes_meet_the_pipeline_hold(self) -> None:
        for tool, command in SHELL_WRITES:
            with self.subTest(command=command):
                s = self.fresh()
                s.prompt("Tidy the build output.")
                s.load(ROUTER)
                s.say("goated-route: standard | requires: tdd")
                held = s.call(tool, {"command": command})
                self.assertEqual(hold_line(held), "goated-hold: pipeline | strict")
                s.load("tdd")
                self.assertEqual(decision(s.call(tool, {"command": command})), "pass")

    def test_reads_test_runs_and_git_status_stay_free(self) -> None:
        for tool, command in SHELL_FREE:
            with self.subTest(command=command):
                s = self.fresh()
                s.prompt("Tidy the build output.")
                s.load(ROUTER)
                s.say("goated-route: standard | requires: tdd")
                self.assertEqual(decision(s.call(tool, {"command": command})), "pass")


def commit(message: str) -> dict:
    return {"command": f'git add -A && git commit -m "{message}"'}


class CommitHoldTests(AdapterTestCase):
    def test_commit_is_held_until_commit_message_loads_in_this_turn(self) -> None:
        s = self.routed()

        held = s.call("Bash", commit("Add CSV export"))
        self.assertEqual(hold_line(held), "goated-hold: commit | strict")
        self.assertIn("commit-message", reason(held))

        s.load("commit-message")
        s.run("git diff")
        self.assertEqual(decision(s.call("Bash", commit("Add CSV export"))), "pass")

    def test_an_unchanged_retry_never_passes(self) -> None:
        s = self.routed()

        for _ in range(3):
            self.assertEqual(decision(s.call("Bash", commit("Add CSV export"))), "deny")

    def test_a_skip_line_never_passes_the_strict_commit_hold(self) -> None:
        s = self.routed()
        s.say("goated-skip: commit-message: the message is already written and fine")

        self.assertEqual(decision(s.call("Bash", commit("Add CSV export"))), "deny")

    def test_a_load_in_an_earlier_turn_still_needs_this_turns_change_read(self) -> None:
        s = self.routed()
        s.load("commit-message")
        s.run("git diff")
        self.assertEqual(decision(s.call("Bash", commit("Add CSV export"))), "pass")

        s.prompt("Commit the follow-up too.")
        s.say("goated-route: continue")
        held = s.call("Bash", commit("Fix export rounding"))
        self.assertIn("Read the change before committing it", reason(held))
        s.run("git diff")
        self.assertEqual(decision(s.call("Bash", commit("Fix export rounding"))), "pass")

    def test_the_hold_does_not_refire_after_compliance(self) -> None:
        s = self.routed()
        s.load("commit-message")
        s.run("git diff")

        self.assertEqual(decision(s.call("Bash", commit("Add CSV export"))), "pass")
        self.assertEqual(decision(s.call("Bash", commit("Add export docs"))), "pass")

    def test_commit_forms_are_recognized(self) -> None:
        for command in (
            "git commit -m 'Add CSV export'",
            "git -C repo commit --amend --no-edit",
            "cd repo; git commit -F msg.txt",
            "git commit",
        ):
            with self.subTest(command=command):
                s = self.fresh()
                s.prompt("Commit it.")
                s.load(ROUTER)
                s.say("goated-route: direct")
                held = s.call("Bash", {"command": command})
                self.assertEqual(hold_line(held), "goated-hold: commit | strict")

    def test_mentions_of_commit_are_not_commits(self) -> None:
        s = self.routed()
        for command in ("git log -1 --format=%B", "echo 'git commit later'", "git commit-tree x"):
            with self.subTest(command=command):
                self.assertEqual(decision(s.call("Bash", {"command": command})), "pass")


class CommitMessageContentTests(AdapterTestCase):
    def loaded(self) -> Session:
        s = self.routed()
        s.load("commit-message")
        s.run("git diff")
        return s

    def test_a_message_breaking_the_contract_is_held(self) -> None:
        cases = {
            "empty subject": {"command": 'git commit -m ""'},
            "long subject": commit("Add " + "very " * 16 + "long subject"),
            "no blank line": {
                "command": "git commit -F - <<'EOF'\nAdd CSV export\nBody right under it.\nEOF"
            },
        }
        for name, command in cases.items():
            with self.subTest(case=name):
                s = self.fresh()
                s.prompt("Commit it.")
                s.load(ROUTER)
                s.say("goated-route: direct")
                s.load("commit-message")
                held = s.call("Bash", command)
                self.assertEqual(hold_line(held), "goated-hold: commit | strict")
                self.assertIn("commit-message", reason(held))

    def test_a_message_with_a_secret_shape_is_held(self) -> None:
        s = self.loaded()
        token = "ghp_" + "A1b2C3d4E5f6G7h8I9j0" * 2
        held = s.call("Bash", commit(f"Rotate token {token}"))
        self.assertEqual(decision(held), "deny")
        self.assertNotIn(token, reason(held))

    def test_well_formed_messages_pass(self) -> None:
        s = self.loaded()
        heredoc = (
            'git commit -m "$(cat <<\'EOF\'\nAdd CSV export\n\nExplain why the export'
            ' exists.\nEOF\n)"'
        )
        here_string = "git commit -m @'\nAdd CSV export\n\nWhy it exists.\n'@"
        for command in (heredoc, here_string, "git commit -m 'Add CSV export' -m 'Body.'"):
            with self.subTest(command=command):
                self.assertEqual(decision(s.call("Bash", {"command": command})), "pass")


class CommitOverrideTests(AdapterTestCase):
    def test_a_user_typed_commit_message_stands_the_hold_down(self) -> None:
        s = self.session
        s.prompt('Commit this with the message "Fix export rounding".')
        s.load(ROUTER)
        s.say("goated-route: direct")

        self.assertEqual(decision(s.call("Bash", commit("Fix export rounding"))), "pass")

    def test_a_different_message_is_still_held(self) -> None:
        s = self.session
        s.prompt('Commit this with the message "Fix export rounding".')
        s.load(ROUTER)
        s.say("goated-route: direct")

        self.assertEqual(decision(s.call("Bash", commit("Rework the exporter"))), "deny")

    def test_a_typed_commit_skip_stands_down_the_load_step(self) -> None:
        for command in (commit("Rework the exporter"), {"command": "git commit -F msg.txt"}):
            with self.subTest(command=command):
                s = self.fresh()
                s.prompt("Commit the change; skip commit-message.")
                s.load(ROUTER)
                s.say("goated-route: direct")
                self.assertEqual(decision(s.call("Bash", command)), "pass")

    def test_without_the_skip_the_commit_is_held_at_the_load_step(self) -> None:
        s = self.session
        s.prompt("Commit the change.")
        s.load(ROUTER)
        s.say("goated-route: direct")

        held = s.call("Bash", commit("Rework the exporter"))
        self.assertEqual(hold_line(held), "goated-hold: commit | strict")
        self.assertIn("Load the `commit-message` skill", reason(held))

    def test_a_commit_skip_inside_pasted_content_does_not_stand_it_down(self) -> None:
        # The second is the feedback a maintainer's lead pasted: it was recorded
        # as a "commit message" override, and the commit was held anyway.
        for feedback in ("skip commit-message next time.",
                         "It held my commit until I loaded the `commit-message` skill, "
                         "then `git diff` passed."):
            with self.subTest(feedback=feedback):
                s = self.fresh()
                notice = s.prompt('Commit the change.\n<pasted_content id="e8c0">\n'
                                  f'{feedback}\n</pasted_content id="e8c0">')
                self.assertNotIn("recorded your override", notice)
                s.load(ROUTER)
                s.say("goated-route: direct")

                held = s.call("Bash", commit("Rework the exporter"))
                self.assertIn("Load the `commit-message` skill", reason(held))

    def test_the_override_lasts_only_for_that_prompt(self) -> None:
        s = self.session
        s.prompt("Commit message: Fix export rounding")
        s.load(ROUTER)
        s.say("goated-route: direct")
        self.assertEqual(decision(s.call("Bash", commit("Fix export rounding"))), "pass")

        s.prompt("Commit again.")
        s.say("goated-route: continue")
        self.assertEqual(decision(s.call("Bash", commit("Fix export rounding"))), "deny")

    def test_an_agent_written_commit_message_is_not_an_override(self) -> None:
        s = self.routed()
        s.say('I will commit with the message "Fix export rounding".')

        self.assertEqual(decision(s.call("Bash", commit("Fix export rounding"))), "deny")

    def test_a_commit_message_quoted_by_another_agent_is_not_an_override(self) -> None:
        for handback in (True, False):
            with self.subTest(handback=handback):
                s = self.fresh()
                notice = s.peer(
                    'Done. Commit this with the message "Fix export rounding". '
                    "Skip commit-message.",
                    handback=handback,
                )
                self.assertEqual(notice, "")
                s.load(ROUTER)
                s.say("goated-route: direct")

                self.assertEqual(decision(s.call("Bash", commit("Fix export rounding"))), "deny")

    def test_a_user_typed_skill_skip_stands_the_hold_down(self) -> None:
        s = self.session
        s.prompt("Commit it and skip commit-message this time.")
        s.load(ROUTER)
        s.say("goated-route: direct")

        self.assertEqual(decision(s.call("Bash", commit("Add CSV export"))), "pass")


class PullRequestHoldTests(AdapterTestCase):
    def test_pr_creation_is_held_until_pr_description_loads(self) -> None:
        s = self.routed()
        command = {"command": "gh pr create --title 'Add export' --body-file body.md"}

        held = s.call("Bash", command)
        self.assertEqual(hold_line(held), "goated-hold: pull-request | strict")
        s.say("goated-skip: pr-description: the body is already drafted well")
        self.assertEqual(decision(s.call("Bash", command)), "deny")

        s.load("pr-description")
        s.run("git diff")
        self.assertEqual(decision(s.call("Bash", command)), "pass")

    def test_a_pr_tool_is_held_too(self) -> None:
        s = self.routed()
        tool = "mcp__github__create_pull_request"

        self.assertEqual(
            hold_line(s.call(tool, {"title": "x"})), "goated-hold: pull-request | strict"
        )
        s.load("pr-description")
        s.run("git diff")
        self.assertEqual(decision(s.call(tool, {"title": "x"})), "pass")

    def test_other_gh_commands_stay_free(self) -> None:
        s = self.routed()

        self.assertEqual(decision(s.call("Bash", {"command": "gh pr view 12"})), "pass")


REVIEW = "standards-and-spec-review"
OPEN_PR = {"command": "gh pr create --base main --title 'Add export' --body-file body.md"}


class PullRequestReviewTests(AdapterTestCase):
    """The `pr-review` gate: a large pull request needs `standards-and-spec-review`."""

    def described(self, changed_lines: int, remote_head: bool = False) -> Session:
        """A routed turn on a branch changing `changed_lines` lines against main,
        with the `pull-request` gate already passed."""

        s = self.routed()
        git_branch_with_change(s.project, changed_lines, remote_head=remote_head)
        s.load("pr-description")
        s.run("git diff main...HEAD")
        return s

    def test_a_large_pull_request_is_held_and_a_smaller_one_is_not(self) -> None:
        held = self.described(400).call("Bash", OPEN_PR)
        self.assertEqual(hold_line(held), "goated-hold: pr-review | justified-skip")
        body = reason(held).split("\n", 1)[1]
        # Beside the skill, only its skip line and the user's typed way out are backticked.
        self.assertEqual(set(re.findall(r"`([^`]+)`", body))
                         - {f"goated-skip: {REVIEW}: <reason>", f"skip {REVIEW}"},
                         {REVIEW})
        self.assertIn("400", body)

        s = self.fresh()
        s.prompt("Open the pull request.")
        s.load(ROUTER)
        s.say("goated-route: direct")
        git_branch_with_change(s.project, 399)
        s.load("pr-description")
        s.run("git diff main...HEAD")
        self.assertEqual(decision(s.call("Bash", OPEN_PR)), "pass")

    def test_the_pull_request_gate_comes_first_and_stays_strict(self) -> None:
        s = self.routed()
        git_branch_with_change(s.project, 500)

        held = s.call("Bash", OPEN_PR)
        self.assertEqual(hold_line(held), "goated-hold: pull-request | strict")
        s.load(REVIEW)
        s.say(f"goated-skip: pr-description: the body is already drafted well")
        self.assertEqual(hold_line(s.call("Bash", OPEN_PR)), "goated-hold: pull-request | strict")

    def test_loading_the_review_skill_then_reading_the_change_clears_it(self) -> None:
        # A diff read before the load counts (Ticket 092), and the pull-request gate asks for one,
        # so only a turn whose user skipped that gate's skill reaches this hold with the skill loaded.
        s = self.fresh()
        s.prompt("Open the pull request; skip pr-description.")
        s.load(ROUTER)
        s.say("goated-route: direct")
        git_branch_with_change(s.project, 450)
        s.load(REVIEW)

        held = s.call("Bash", OPEN_PR)
        self.assertEqual(hold_line(held), "goated-hold: pr-review | justified-skip")
        self.assertIn("Read the change", reason(held))
        s.run("git diff main...HEAD --stat")
        self.assertEqual(decision(s.call("Bash", OPEN_PR)), "deny")
        s.run("git diff main...HEAD")
        self.assertEqual(decision(s.call("Bash", OPEN_PR)), "pass")

    def test_a_skip_line_naming_the_review_skill_clears_it(self) -> None:
        s = self.described(450)
        s.say(f"goated-skip: {REVIEW}: generated fixtures make up the bulk of it")

        self.assertEqual(decision(s.call("Bash", OPEN_PR)), "pass")

    def test_a_typed_skip_override_clears_it(self) -> None:
        s = self.session
        s.prompt(f"Open the pull request; skip {REVIEW}.")
        s.load(ROUTER)
        s.say("goated-route: direct")
        git_branch_with_change(s.project, 450)
        s.load("pr-description")
        s.run("git diff main...HEAD")

        self.assertEqual(decision(s.call("Bash", OPEN_PR)), "pass")

    def test_without_a_base_flag_the_remote_default_branch_is_the_base(self) -> None:
        s = self.described(450, remote_head=True)

        held = s.call("Bash", {"command": "gh pr create --fill"})
        self.assertEqual(hold_line(held), "goated-hold: pr-review | justified-skip")

    def test_each_base_option_names_the_base(self) -> None:
        for command in ("gh pr create -B main --fill", "gh pr create --base=main --fill",
                        "glab mr create --target-branch main --fill", "glab mr create -b main"):
            with self.subTest(command=command):
                s = self.fresh()
                s.prompt("Open the pull request.")
                s.load(ROUTER)
                s.say("goated-route: direct")
                git_branch_with_change(s.project, 450)
                s.load("pr-description")
                s.run("git diff main...HEAD")
                held = s.call("Bash", {"command": command})
                self.assertEqual(hold_line(held), "goated-hold: pr-review | justified-skip")

    def test_a_pr_tool_is_measured_against_its_base_input(self) -> None:
        s = self.described(450)
        tool = "mcp__github__create_pull_request"

        held = s.call(tool, {"title": "x", "base": "main", "head": "feature"})
        self.assertEqual(hold_line(held), "goated-hold: pr-review | justified-skip")

    def fresh_described(self, **repo) -> Session:
        """Like `described`, in a session of its own, with `git_branch_with_change` options."""

        s = self.fresh()
        s.prompt("Open the pull request.")
        s.load(ROUTER)
        s.say("goated-route: direct")
        git_branch_with_change(s.project, repo.pop("changed_lines", 450), **repo)
        s.load("pr-description")
        s.run("git diff main...feature")
        return s

    def test_it_still_holds_once_the_pull_request_gate_passes(self) -> None:
        s = self.routed()
        git_branch_with_change(s.project, 500)

        self.assertEqual(hold_line(s.call("Bash", OPEN_PR)), "goated-hold: pull-request | strict")
        s.load("pr-description")
        s.run("git diff main...HEAD")
        self.assertEqual(hold_line(s.call("Bash", OPEN_PR)), "goated-hold: pr-review | justified-skip")

    def test_without_a_base_each_usual_default_branch_is_tried(self) -> None:
        fill = {"command": "gh pr create --fill"}
        cases = (
            ("origin/HEAD", {"remote_head": True}),
            ("origin/main", {"remote_branches": ("main",)}),
            ("origin/master", {"base": "master", "remote_branches": ("master",)}),
            ("local main", {}),
            ("local master", {"base": "master"}),
        )
        for name, repo in cases:
            with self.subTest(base=name):
                s = self.fresh_described(**repo)
                self.assertEqual(hold_line(s.call("Bash", fill)),
                                 "goated-hold: pr-review | justified-skip")

    def test_a_named_head_is_measured_instead_of_the_checked_out_branch(self) -> None:
        tool = "mcp__github__create_pull_request"
        for name, call in (
            ("pr tool", (tool, {"title": "x", "base": "main", "head": "feature"})),
            ("gh --head", ("Bash", {"command": "gh pr create --base main --head feature --fill"})),
            ("gh -H", ("Bash", {"command": "gh pr create -B main -H feature --fill"})),
            ("glab --source-branch", ("Bash", {"command": "glab mr create -b main --source-branch feature"})),
            ("remote-only head", ("Bash", {"command": "gh pr create --base main --head pushed --fill"})),
        ):
            with self.subTest(case=name):
                s = self.fresh_described(stay_on_base=True)
                if name == "remote-only head":
                    import subprocess
                    subprocess.run(["git", "update-ref", "refs/remotes/origin/pushed", "feature"],
                                   cwd=s.project, check=True)
                self.assertEqual(hold_line(s.call(*call)), "goated-hold: pr-review | justified-skip")
        # Without a head, the checked-out base is measured against itself: nothing changed.
        s = self.fresh_described(stay_on_base=True)
        self.assertEqual(decision(s.call(tool, {"title": "x", "base": "main"})), "pass")

    def test_a_pr_tool_aimed_at_another_repository_is_not_measured(self) -> None:
        tool = "mcp__github__create_pull_request"
        pr = {"title": "x", "owner": "acme", "repo": "export", "base": "main", "head": "feature"}
        for url, held in (
            ("https://github.com/acme/export.git", True),
            ("git@github.com:Acme/Export.git", True),
            ("https://github.com/other/export.git", False),
            (None, False),
        ):
            with self.subTest(origin=url):
                s = self.fresh_described(origin_url=url)
                self.assertEqual(decision(s.call(tool, pr)), "deny" if held else "pass")

    def test_a_shell_pull_request_naming_a_repository_is_measured_only_there(self) -> None:
        # Spec R7: `--repo`/`-R` aims the command as a pull_request call's
        # `repository` does, and the branches are still read beside it.
        github = "https://github.com/acme/export.git"
        gitlab = "git@gitlab.example.com:group/sub/export.git"
        branches = "--base main --head feature --fill"
        for url, command, held in (
            (github, f"gh pr create --repo acme/export {branches}", True),
            (github, f"gh pr create -R acme/export {branches}", True),
            (github, f"gh pr create --repo=Acme/Export {branches}", True),
            (github, f"gh pr create -Racme/export {branches}", True),
            (github, f"gh pr create -R=acme/export {branches}", True),
            (github, "gh pr create -R acme/export -B=main -H=feature --fill", True),
            (github, f"gh pr new -R github.com/acme/export {branches}", True),
            (github, f"gh pr create -R https://github.com/acme/export.git {branches}", True),
            (github, f"gh pr create -R git@github.com:acme/export.git {branches}", True),
            (github, f"gh pr create {branches} -R acme/export", True),
            (gitlab, "glab mr create -R gitlab.example.com/group/sub/export -b main -s feature", True),
            (gitlab, "glab mr new --repo group/sub/export --target-branch main --source-branch feature", True),
            (github, f"gh pr create --repo other/x {branches}", False),
            (github, "glab mr create -R other/x -b main -s feature", False),
            (github, f"gh pr create -R export {branches}", False),
            (None, f"gh pr create -R acme/export {branches}", False),
        ):
            with self.subTest(origin=url, command=command):
                s = self.fresh_described(origin_url=url, stay_on_base=True)
                self.assertEqual(decision(s.call("Bash", {"command": command})),
                                 "deny" if held else "pass")

    def test_options_between_the_noun_and_the_verb_still_open_a_pull_request(self) -> None:
        # Spec R13: `gh pr -R x create` opens a pull request as `gh pr create -R x` does.
        github = "https://github.com/acme/export.git"
        gitlab = "git@gitlab.example.com:group/sub/export.git"
        branches = "--base main --head feature --fill"
        for url, command, held in (
            (github, f"gh pr -R acme/export create {branches}", True),
            (github, f"gh pr --repo=acme/export create {branches}", True),
            (github, f"gh pr -Racme/export new {branches}", True),
            (github, "gh pr -B main -H feature create --fill", True),
            (gitlab, "glab mr --repo group/sub/export create -b main -s feature", True),
            (github, f"gh pr -R other/x create {branches}", False),
            (github, "glab mr --repo other/x new -b main -s feature", False),
        ):
            with self.subTest(origin=url, command=command):
                s = self.fresh_described(origin_url=url, stay_on_base=True)
                self.assertEqual(decision(s.call("Bash", {"command": command})),
                                 "deny" if held else "pass")

    def test_each_pull_request_in_a_chain_is_read_with_its_own_options(self) -> None:
        # Spec R14: a later pull request never takes an earlier one's --repo,
        # --base or --head, and each is measured on its own.
        github = "https://github.com/acme/export.git"
        for command, held in (
            ("gh pr create -R other/x --fill && gh pr create -B main -H feature --fill", True),
            ("gh pr create -B main -H feature --fill; glab mr create -R other/x", True),
            ("gh pr create -R other/x -B main -H feature --fill && gh pr create --fill", False),
            ("gh pr create -B main --fill && gh pr create -B small --fill", True),
            ("gh pr create -B small --fill && gh pr create -B main --fill", True),
            ("gh pr create -B small --fill && gh pr create -B small --fill", False),
            ("gh pr create -B main -H feature --fill && gh pr create -B small --fill", True),
        ):
            with self.subTest(command=command):
                # `small` is a branch at feature's tip, so a pull request into it is
                # empty; with no head, the checked-out branch is measured.
                s = self.fresh_described(origin_url=github, stay_on_base="-H" in command)
                subprocess.run(["git", "branch", "small", "feature"], cwd=s.project, check=True)
                self.assertEqual(decision(s.call("Bash", {"command": command})),
                                 "deny" if held else "pass")

    def test_a_held_chain_names_the_pull_request_it_measured(self) -> None:
        s = self.fresh_described()
        subprocess.run(["git", "branch", "small", "feature"], cwd=s.project, check=True)

        held = s.call("Bash", {"command": "gh pr create -B small --fill && gh pr create -B main --fill"})
        self.assertEqual(hold_line(held), "goated-hold: pr-review | justified-skip")
        self.assertIn("pull request 2 of 2 in this command, into main, has 450 changed lines",
                      reason(held))

    def test_a_branch_name_in_the_hold_is_never_backticked(self) -> None:
        # Backticks name a skill to load, so a branch's own are quoted instead.
        s = self.fresh_described()
        subprocess.run(["git", "branch", "feat`tdd`x", "feature"], cwd=s.project, check=True)

        held = s.call("Bash", {"command": "gh pr create -B 'feat`tdd`x' --fill && "
                                          "gh pr create -B main -H 'feat`tdd`x' --fill"})
        self.assertIn("into main from feat'tdd'x, has 450", reason(held))
        self.assertNotIn("`tdd`", reason(held))

    def test_one_pull_request_keeps_its_hold_text(self) -> None:
        held = self.fresh_described().call("Bash", {"command": "gh pr create -B main --fill"})
        self.assertIn("this pull request has 450 changed lines", reason(held))

    def test_other_forge_commands_open_no_pull_request(self) -> None:
        # A value that spells a verb is still a value: `-R create` names a repository.
        # Between the noun and the verb, any `--x` or `-x` takes the next word, as
        # gh's parser does, so `--draft create` gives --draft the value "create".
        for command in ("gh pr list", "gh pr -R acme/export list", "gh pr -R create list",
                        "echo gh pr create", "gh pr view create",
                        "gh pr --search new list", "gh pr -S new list",
                        "gh pr --state create list", "gh pr --json create view",
                        "gh pr --draft create", "gh pr -d create", "gh pr -- create"):
            with self.subTest(command=command):
                # Checked out on a large branch, where a pull request would be held.
                s = self.fresh_described()
                self.assertEqual(decision(s.call("Bash", {"command": command})), "pass")
        held = self.fresh_described().call("Bash", {"command": "gh pr create --fill"})
        self.assertEqual(decision(held), "deny")

    def test_option_values_are_not_read_as_options(self) -> None:
        # glab's -b is the target branch; inside --description's value it is just text.
        s = self.fresh_described(remote_head=True)
        command = {"command": 'glab mr create --description "-bump deps" --title x'}
        self.assertEqual(hold_line(s.call("Bash", command)), "goated-hold: pr-review | justified-skip")

    def test_no_hold_when_the_size_cannot_be_measured(self) -> None:
        cases = (
            # No base flag, and none of origin/HEAD, origin/main, origin/master, main, or master.
            ("no base", {"base": "trunk"}, {"command": "gh pr create --fill"}),
            # A base git would read as an option is never passed to it.
            ("option-like base", {}, {"command": "gh pr create --base=--output=x.txt --fill"}),
            ("unknown base", {}, {"command": "gh pr create --base nowhere --fill"}),
            # A head that is neither a local branch nor origin/<head> fails open.
            ("unknown head", {}, {"command": "gh pr create --base main --head someone:fork --fill"}),
        )
        for name, repo, command in cases:
            with self.subTest(case=name):
                s = self.fresh_described(**repo)
                self.assertEqual(decision(s.call("Bash", command)), "pass")
                self.assertFalse((s.project / "x.txt").exists())

    def test_outside_a_git_checkout_the_pull_request_passes(self) -> None:
        s = self.routed()
        s.load("pr-description")
        s.run("git diff main...HEAD")

        self.assertEqual(decision(s.call("Bash", OPEN_PR)), "pass")


class SpawnBriefTests(AdapterTestCase):
    def test_a_spawn_is_held_until_handoff_loads_and_its_template_is_read(self) -> None:
        s = self.routed()

        held = s.call("Agent", {"prompt": BRIEF})
        self.assertEqual(hold_line(held), "goated-hold: spawn | strict")
        s.load("handoff")
        held = s.call("Agent", {"prompt": BRIEF})
        self.assertEqual(decision(held), "deny")
        self.assertIn("spawn-brief.md", reason(held))

        s.read(SPAWN_BRIEF_PATH, success=False)
        self.assertEqual(decision(s.call("Agent", {"prompt": BRIEF})), "deny")
        s.read(SPAWN_BRIEF_PATH)
        self.assertEqual(decision(s.call("Agent", {"prompt": BRIEF})), "pass")
        self.assertEqual(decision(s.call("Agent", {"prompt": BRIEF})), "pass")

    def test_the_template_offers_checks_and_shared_with_lines_a_brief_may_leave_out(self) -> None:
        template = (REPO_ROOT / "skills" / "agent-workflows" / "handoff" / "references"
                    / "spawn-brief.md").read_text(encoding="utf-8")
        self.assertIn("- Shared with:", template)
        self.assertIn("- Checks:", template)
        self.assertNotIn("Shared with", BRIEF)
        self.assertNotIn("Checks", BRIEF)
        s = self.routed()
        s.brief_with_handoff()
        self.assertEqual(decision(s.call("Agent", {"prompt": BRIEF})), "pass")

    def test_a_brief_missing_a_required_section_is_held(self) -> None:
        s = self.routed()
        s.brief_with_handoff()
        brief = "## Goal\n\nAudit the exporter.\n\n## Scope\n\n- Work in: src/export/\n"

        held = s.call("Agent", {"prompt": brief})
        self.assertEqual(hold_line(held), "goated-hold: spawn | strict")
        self.assertIn("## Done Means", reason(held))

    def test_a_skip_line_never_passes_the_spawn_hold(self) -> None:
        s = self.routed()
        s.say("goated-skip: handoff: this is only a quick lookup agent")

        self.assertEqual(decision(s.call("Agent", {"prompt": BRIEF})), "deny")

    def test_the_implementer_prompt_counts_with_its_own_sections(self) -> None:
        s = self.routed()
        s.load("subagent-driven-development")
        s.read(
            "/opt/goated/skills/subagent-driven-development/references/implementer-prompt.md"
        )
        brief = (
            "## Task\n\nAdd export.\n\n## Ownership\n\n- src/\n\n"
            "## Required Report Format\n\n- Status\n\ngoated-skills: tdd\n"
        )

        self.assertEqual(decision(s.call("Agent", {"prompt": brief})), "pass")
        held = s.call("Agent", {"prompt": BRIEF})
        self.assertIn("## Task", reason(held))

    def test_session_spawns_without_a_brief_are_not_held(self) -> None:
        s = self.routed()
        tool = "mcp__ccd_session__start_session"

        offer = {"title": "Fix it", "initiation": "offer"}
        self.assertEqual(decision(s.call(tool, offer)), "pass")
        self.assertEqual(decision(s.call(tool, {"prompt": "do it"})), "deny")


# BRIEF without its skills line (Ticket 071).
BRIEF_BODY = BRIEF.replace("goated-skills: code-security-review\n", "")
SKILL_TEMPLATES = Path(__file__).resolve().parents[1] / "skills"
TEMPLATE_FILES = (
    "agent-workflows/handoff/references/spawn-brief.md",
    "engineering/subagent-driven-development/references/implementer-prompt.md",
    "engineering/subagent-driven-development/references/reviewer-prompt.md",
)


class SpawnSkillsLineTests(AdapterTestCase):
    """A brief names the skills the new agent reads, or none with a reason (Ticket 071)."""

    def spawn(self, brief: str, tool: str = "Agent", **extra) -> dict:
        s = self.routed()
        s.brief_with_handoff()
        return s.call(tool, {"prompt": brief, **extra})

    def test_a_line_naming_skills_passes(self) -> None:
        for line in ("goated-skills: tdd", "goated-skills: tdd, software-design-principles",
                     "`goated-skills: tdd`"):
            with self.subTest(line=line):
                self.assertEqual(decision(self.spawn(f"{BRIEF_BODY}\n{line}\n")), "pass")

    def test_namespaced_installed_names_pass(self) -> None:
        # A plugin install names its skills `namespace:skill` (GOATED_ADAPTER_SKILL_NAMESPACES).
        for line in ("goated-skills: goated:tdd", "goated-skills: anthropic-skills:pdf, tdd"):
            with self.subTest(line=line):
                self.assertEqual(decision(self.spawn(f"{BRIEF_BODY}\n{line}\n")), "pass")
        for line in ("goated-skills: goated:", "goated-skills: :tdd", "goated-skills: a:b:tdd"):
            with self.subTest(line=line):
                self.assertEqual(hold_line(self.spawn(f"{BRIEF_BODY}\n{line}\n")),
                                 "goated-hold: spawn | strict")

    def test_a_skills_line_written_as_a_list_item_passes(self) -> None:
        for line in ("- goated-skills: tdd", "* goated-skills: none: the agent only lists files"):
            with self.subTest(line=line):
                self.assertEqual(decision(self.spawn(f"{BRIEF_BODY}\n{line}\n")), "pass")
        for line in ("-goated-skills: tdd", "+ goated-skills: tdd", "**goated-skills: tdd**"):
            with self.subTest(line=line):
                held = self.spawn(f"{BRIEF_BODY}\n{line}\n")
                self.assertIn("lacks a skills line", reason(held))
                self.assertIn("not in bold", reason(held))

    def test_the_hold_names_each_problem(self) -> None:
        cases = {
            "goated-skills:": "names no skill",
            "goated-skills: none": "says none without a reason",
            "goated-skills: none: lookup only": "says none without a reason",
            "goated-skills: tdd.": 'names "tdd." in its skills line',
            "goated-skills: TDD": 'names "TDD" in its skills line',
            "goated-skills: tdd,": "an empty name",
            "Goated-Skills: tdd": "in lowercase",
            "goated-skills:tdd": "no space after",
            "goated-skills: none, tdd": "mixes none with skill names",
            "goated-skills: tdd, none": "mixes none with skill names",
        }
        for line, problem in cases.items():
            with self.subTest(line=line):
                held = self.spawn(f"{BRIEF_BODY}\n{line}\n")
                self.assertEqual(hold_line(held), "goated-hold: spawn | strict")
                self.assertIn(problem, reason(held))
                self.assertNotIn("lacks a skills line", reason(held))

    def test_a_line_naming_no_skill_is_held(self) -> None:
        for line in ("goated-skills:", "goated-skills: ", "goated-skills: TDD",
                     "goated-skills: tdd,"):
            with self.subTest(line=line):
                held = self.spawn(f"{BRIEF_BODY}\n{line}\n")
                self.assertEqual(hold_line(held), "goated-hold: spawn | strict")
                self.assertIn("goated-skills: <skill>, <skill>", reason(held))

    def test_none_with_a_reason_passes_and_none_alone_is_held(self) -> None:
        passing = "goated-skills: none: the agent only lists files"
        self.assertEqual(decision(self.spawn(f"{BRIEF_BODY}\n{passing}\n")), "pass")
        for line in ("goated-skills: none", "goated-skills: none:", "goated-skills: none: lookup only"):
            with self.subTest(line=line):
                held = self.spawn(f"{BRIEF_BODY}\n{line}\n")
                self.assertEqual(hold_line(held), "goated-hold: spawn | strict")
                self.assertIn("goated-skills: none: <reason>", reason(held))

    def test_a_brief_without_the_line_is_held_and_told_the_line(self) -> None:
        held = self.spawn(BRIEF_BODY)

        self.assertEqual(hold_line(held), "goated-hold: spawn | strict")
        self.assertIn("lacks a skills line", reason(held))
        self.assertIn("goated-skills: <skill>, <skill>", reason(held))
        self.assertIn("SKILL.md", reason(held))

    def test_a_line_in_a_code_block_or_inside_prose_does_not_count(self) -> None:
        for brief in (f"{BRIEF_BODY}\n```\ngoated-skills: tdd\n```\n",
                      f"{BRIEF_BODY}\nRead what goated-skills: tdd names.\n"):
            with self.subTest(brief=brief):
                self.assertIn("lacks a skills line", reason(self.spawn(brief)))

    def test_missing_headings_and_line_are_named_together(self) -> None:
        held = self.spawn("## Goal\n\nAudit the exporter.\n")

        self.assertIn("`## Scope`", reason(held))
        self.assertIn("lacks a skills line", reason(held))

    def test_a_card_with_a_brief_meets_the_same_check(self) -> None:
        tool = "mcp__ccd_session__start_session"
        card = {"title": "Audit", "initiation": "own_initiative"}

        held = self.spawn(BRIEF_BODY, tool=tool, **card)
        self.assertEqual(hold_line(held), "goated-hold: spawn | strict")
        self.assertIn("lacks a skills line", reason(held))
        self.assertEqual(decision(self.spawn(BRIEF, tool=tool, **card)), "pass")

    def test_each_brief_template_carries_the_line_and_the_skill_md_fallback(self) -> None:
        for name in TEMPLATE_FILES:
            with self.subTest(template=name):
                text = (SKILL_TEMPLATES / name).read_text(encoding="utf-8")
                self.assertRegex(text, r"(?m)^goated-skills: <skill>, <skill>")
                self.assertIn("SKILL.md", text)

    def test_the_spawn_brief_examples_pass_the_adapter_check(self) -> None:
        # The form is defined in handoff's spawn brief; the adapter follows it.
        text = (SKILL_TEMPLATES / TEMPLATE_FILES[0]).read_text(encoding="utf-8")
        examples = re.findall(r"`(goated-skills: (?!<)[^`]+)`", text)

        self.assertGreaterEqual(len(examples), 2)
        for example in examples:
            with self.subTest(example=example):
                self.assertEqual(decision(self.spawn(f"{BRIEF_BODY}\n{example}\n")), "pass")


def write(path: str, lines: int = 6) -> dict:
    return {"file_path": path, "content": "\n".join(f"line {n}" for n in range(lines))}


REFERENCES = "/opt/goated/skills/software-design-principles/references/"
# Six added lines that trip no design-reads signal.
PLAIN = "\n".join(f"total_{n} = {n}" for n in range(6))
# A 20-line test, the first edit of a TDD turn.
TEST_CODE = "def test_totals():\n" + "\n".join(f"    assert total_{n} == {n}" for n in range(19))


def edit(path: str, new: str, old: str = "pass") -> dict:
    return {"file_path": path, "old_string": old, "new_string": new}


def lines_of(text: str, count: int) -> str:
    """`count` lines, each `text` with its number in it."""

    return "\n".join(text.format(n=n) for n in range(count))


class DesignHoldTests(AdapterTestCase):
    def test_a_substantial_code_edit_is_held_until_design_loads(self) -> None:
        s = self.routed()

        held = s.call("Edit", edit("src/export.py", PLAIN))
        self.assertEqual(hold_line(held), "goated-hold: design | justified-skip")
        self.assertIn("`software-design-principles`", reason(held))
        self.assertEqual(decision(s.call("Edit", edit("src/export.py", PLAIN))), "deny")

        s.load("software-design-principles")
        # Ticket 089: with nothing to read, the load alone meets the gate.
        self.assertEqual(decision(s.call("Edit", edit("src/export.py", PLAIN))), "pass")
        self.assertEqual(decision(s.call("Edit", edit("src/other.py", PLAIN))), "pass")

    def test_a_skip_line_passes_the_design_hold(self) -> None:
        s = self.routed()
        self.assertEqual(decision(s.call("Write", write("src/export.py"))), "deny")

        s.say("goated-skip: software-design-principles: this is a mechanical rename only")
        self.assertEqual(decision(s.call("Write", write("src/export.py"))), "pass")

    def test_a_skip_line_with_too_short_a_reason_does_not_pass(self) -> None:
        s = self.routed()
        s.say("goated-skip: software-design-principles: mechanical")

        self.assertEqual(decision(s.call("Write", write("src/export.py"))), "deny")

    def test_small_edits_and_docs_are_not_held(self) -> None:
        s = self.routed()

        self.assertEqual(decision(s.call("Write", write("src/export.py", lines=2))), "pass")
        self.assertEqual(decision(s.call("Write", write("docs/guide.md", lines=40))), "pass")

    def test_a_test_file_edit_does_not_trigger_the_design_gate(self) -> None:
        # TDD writes the test first; the design happens in the code after it (Ticket 057).
        s = self.routed()

        self.assertEqual(decision(s.call("Edit", edit("tests/test_export.py", TEST_CODE))), "pass")
        self.assertEqual(decision(s.call("Write", write("src/export.test.ts", lines=20))), "pass")
        held = s.call("Edit", edit("src/export.py", "\n".join(f"total_{n} = {n}" for n in range(20))))
        self.assertEqual(hold_line(held), "goated-hold: design | justified-skip")

    def test_a_test_file_edit_is_not_the_turns_first_substantial_edit(self) -> None:
        s = self.routed()
        s.load("software-design-principles")
        s.read(REFERENCES + "coding.md")
        self.assertEqual(decision(s.call("Edit", edit("tests/test_export.py", TEST_CODE))), "pass")

        # The first non-test edit is still the design gate's, not the later-edit one's;
        # with the skill loaded it lands owing its reads (Ticket 118).
        landed = s.call("Edit", edit("src/export.py", "def export(rows):\n" + PLAIN))
        self.assertEqual(decision(landed), "pass")
        self.assertIn("the design gate let this write", owed(landed))

    def test_a_test_file_is_judged_by_its_path_inside_the_project(self) -> None:
        # A folder above the project named like a test folder makes nothing a test.
        s = self.session
        s.project = s.cwd = self.root / "home" / "tests" / "spec" / "myapp"
        s.project.mkdir(parents=True)
        self.routed()
        for path in ("src/export.py", str(s.project / "src" / "export.py")):
            with self.subTest(path):
                held = s.call("Edit", edit(path, TEST_CODE))
                self.assertEqual(hold_line(held), "goated-hold: design | justified-skip")
        self.assertEqual(decision(s.call("Edit", edit(str(s.project / "tests" / "test_export.py"), TEST_CODE))),
                         "pass")

    def test_which_paths_are_test_files(self) -> None:
        tests = ("tests/helpers/factory.py", "packages/api/test/load.py", "web/__tests__/load.js",
                 "spec/support/helpers.rb", "src/app/test_runner.py", "src/export_test.go",
                 "src/models/user_spec.rb", "src/export.test.ts", "src/export.spec.js")
        not_tests = ("src/spec/parser.py", "src/testing.py", "src/contest/score.py",
                     "lib/latest/load.py", "src/tests_util.py")
        for path in tests + not_tests:
            with self.subTest(path):
                self.session = self.fresh()
                s = self.routed()
                expected = "pass" if path in tests else "deny"
                self.assertEqual(decision(s.call("Edit", edit(path, TEST_CODE))), expected)

    def test_with_no_known_project_no_file_is_a_test(self) -> None:
        s = self.routed()
        held = s.call("Edit", edit("/work/tests/test_export.py", TEST_CODE), cwd="")
        self.assertEqual(hold_line(held), "goated-hold: design | justified-skip")

    def test_with_the_skill_loaded_a_test_edit_still_needs_coding(self) -> None:
        s = self.routed()
        s.load("software-design-principles")

        landed = s.call("Edit", edit("tests/test_export.py", TEST_CODE))
        self.assertEqual(decision(landed), "pass")
        self.assertEqual(owed_names(landed), {"coding.md"})
        self.assertIn("`software-design-principles/references/coding.md` (edits a test file)", owed(landed))
        s.read(REFERENCES + "coding.md")
        next_turn(s)  # So the edit would owe it again, were the read not to count.
        again = s.call("Edit", edit("tests/test_export.py", TEST_CODE))
        self.assertEqual((decision(again), owed(again)), ("pass", ""))

    def test_a_load_in_an_earlier_turn_counts(self) -> None:
        s = self.routed()
        s.load("software-design-principles")
        self.assertEqual(decision(s.call("Edit", edit("src/export.py", PLAIN))), "pass")

        s.prompt("Now the importer.")
        s.say("goated-route: continue")
        self.assertEqual(decision(s.call("Edit", edit("src/import.py", PLAIN))), "pass")


class DesignReferenceReadTests(AdapterTestCase):
    """The design hold's references, the design-reads hold, and their cooldown (Ticket 051)."""

    def designing(self, s: Session | None = None) -> Session:
        s = s or self.routed()
        s.load("software-design-principles")
        return s

    def next_turn(self, s: Session) -> None:
        next_turn(s)

    def test_an_unread_required_reference_is_owed_naming_it(self) -> None:
        s = self.designing()

        landed = s.call("Write", write("src/export.py"))
        self.assertEqual(decision(landed), "pass")
        self.assertEqual(owed_names(landed),
                         {"process.md", "complexity-and-modules.md", "readability.md"})
        self.assertIn("`software-design-principles/references/process.md` (a new code file)", owed(landed))
        s.read(REFERENCES + "process.md")
        self.next_turn(s)
        landed = s.call("Write", write("src/export.py"))
        self.assertEqual(owed_names(landed), {"complexity-and-modules.md", "readability.md"})
        s.read(REFERENCES + "complexity-and-modules.md")
        self.next_turn(s)
        landed = s.call("Write", write("src/export.py"))
        self.assertEqual(owed_names(landed), {"readability.md"})
        self.assertIn("references/readability.md` (a new code file)", owed(landed))
        s.read(REFERENCES + "readability.md")
        self.next_turn(s)
        done = s.call("Write", write("src/export.py"))
        self.assertEqual((decision(done), owed(done)), ("pass", ""))

    def test_each_signal_selects_its_reference_and_a_near_miss_does_not(self) -> None:
        cases = (
            # (name, tool, input, references it selects, near-miss tool, near-miss input)
            ("top-level definition", "Edit", edit("src/a.py", "def export(rows):\n    return rows"),
             {"process.md", "complexity-and-modules.md", "readability.md"},
             "Edit", edit("src/a.py", "    def export(self):\n        return 1")),
            ("definition kept as context", "Edit",
             edit("src/a.py", "function load() {\n  return 1", old="function load() {"),
             set(), "Edit", edit("src/a.py", "  return 2")),
            ("exported definition", "Edit", edit("src/a.ts", "export const rate = 1"),
             {"process.md", "complexity-and-modules.md", "readability.md"},
             "Edit", edit("src/a.ts", "const exported = 1")),
            ("new code file", "Write", {"file_path": "src/fresh.py", "content": "x = 1"},
             {"process.md", "complexity-and-modules.md", "readability.md"},
             "Write", {"file_path": "{project}/src/existing.py", "content": "x = 2"}),
            ("public definition", "Edit", edit("src/a.py", "class Exporter:\n    pass"),
             {"process.md", "complexity-and-modules.md", "readability.md"},
             "Edit", edit("src/a.py", "def _helper():\n    return 1")),
            ("exported, not a shell export", "Edit", edit("src/a.js", "export function load() {}"),
             {"process.md", "complexity-and-modules.md", "readability.md"},
             "Edit", edit("src/env.sh", "export RATE=1")),
            ("test file selects only coding", "Edit",
             edit("tests/test_a.py",
                  "def test_load():\n    try:\n        load()  # the cache\n    finally:\n        reset()"),
             {"coding.md"}, "Edit", edit("tests/fixtures/rows.json", '{"rate": 1}')),
            # Five code lines, so the comment selects `readability.md` (round 5, K1).
            ("comment words are not code", "Edit",
             edit("src/a.py", "# try the cache first, then raise\n# Lock the row\n# then catch it\n"
                  "# with open\nrows = load()  # Lock it\n" + lines_of("x_{n} = {n}", 4)),
             {"readability.md"}, "Edit", edit("src/a.py", "rows = load()")),
            ("docstring words are not code", "Edit",
             edit("src/a.py", '    """Raise when a Lock is held,\n    then try again,\n    catch it,\n'
                  '    and throw it.\n    """\n' + lines_of("    x_{n} = {n}", 5)),
             {"readability.md"}, "Edit", edit("src/a.py", "    rows = []")),
            ("comment", "Edit", edit("src/a.py", "rate = 1  # per second\n" + lines_of("x_{n} = {n}", 4)),
             {"readability.md"}, "Edit", edit("src/a.py", "rate = a // b")),
            ("docstring", "Edit", edit("src/a.py", '    """Return the rate."""\n' + lines_of("    x_{n} = {n}", 5)),
             {"readability.md"}, "Edit", edit("src/a.py", '    name = "rate"')),
            ("error handling", "Edit", edit("src/a.py", "try:\n    rate = 1"),
             {"errors.md"}, "Edit", edit("src/a.py", "retry = 1")),
            ("file resource", "Edit", edit("src/a.py", "    with open(path) as f:"),
             {"errors.md"}, "Edit", edit("src/a.py", "    opened = path")),
            ("test file", "Edit", edit("tests/test_export.py", lines_of("x_{n} = {n}", 5)),
             {"coding.md"}, "Edit", edit("src/contest.py", "x = 1")),
            ("concurrency", "Edit", edit("src/a.py", "guard = threading.Lock()"),
             {"concurrency.md"}, "Edit", edit("src/a.py", "clock = 1")),
            ("configuration file", "Edit", edit("config/app.yaml", lines_of("rate_{n}: {n}", 5)),
             {"decoupling.md"}, "Edit", edit("docs/app.md", "rate: 1")),
        )
        for name, tool, tool_input, selects, near_tool, near_input in cases:
            with self.subTest(name=name):
                s = self.designing(s=self.fresh_routed())
                (s.project / "src").mkdir(parents=True, exist_ok=True)
                (s.project / "src" / "existing.py").write_text("x = 0\n", encoding="utf-8")
                near_input = {
                    k: v.replace("{project}", str(s.project)) for k, v in near_input.items()
                }
                near = s.call(near_tool, near_input)
                self.assertEqual((decision(near), owed(near)), ("pass", ""))
                landed = s.call(tool, tool_input)
                # Since Ticket 118 each lands, and its notice names what it selects.
                self.assertEqual(decision(landed), "pass", reason(landed))
                self.assertEqual(owed_names(landed), selects, owed(landed))

    def test_a_definition_start_reads_its_keyword_in_code_files_only(self) -> None:
        # Ticket 106: `async` and `pub` start a definition only before a
        # definition keyword, and a configuration file defines nothing.
        defines = (
            ("src/a.rs", "pub fn run() {}"),
            ("src/a.rs", "pub(crate) struct S;"),
            ("src/a.rs", "pub(in crate::x) enum E {}"),
            ("src/a.rs", "pub async fn run() {}"),
            ("src/a.rs", "pub unsafe fn run() {}"),
            ("src/a.rs", 'pub unsafe extern "C" fn run() {}'),
            ("src/a.rs", "pub async unsafe fn run() {}"),
            ("src/a.rs", "pub unsafe trait T {}"),
            ("src/a.rs", "pub const fn run() {}"),
            ("src/a.zig", "pub var x: u8 = 1;"),
            ("src/a.zig", "pub inline fn f() void {}"),
            ("src/a.py", "async def run():"),
            ("src/a.js", "async function run() {}"),
            ("src/a.py", "class Run:"),
        )
        defines_nothing = (
            ("src/a.rs", "pub use x;"),
            ("src/a.rs", "pub(crate) use x::y;"),
            ("src/a.rs", "pub extern crate foo;"),
            ("src/a.js", "async () => run()"),
            ("src/a.py", "async_helper = 1"),
            ("src/a.py", "async"),
            ("src/a.rs", "public_rate = 1"),
            ("config/app.yaml", "class: foo"),
            ("config/app.yaml", "async: true"),
            ("config/app.toml", "pub = 1"),
        )
        for path, line in defines:
            with self.subTest(defines=line):
                landed = self.designing(s=self.fresh_routed()).call("Edit", edit(path, line))
                self.assertIn("references/process.md` (adds a public top-level definition", owed(landed))
        for path, line in defines_nothing:
            with self.subTest(defines_nothing=line):
                quiet = self.designing(s=self.fresh_routed()).call("Edit", edit(path, line))
                self.assertEqual((decision(quiet), owed(quiet)), ("pass", ""))

    def test_a_definition_is_named_past_its_keywords_and_strings(self) -> None:
        # A rename past `unsafe`, `extern "C"`, `mod`, `union` or `pub(in …)`
        # adds a definition, and the hold names it.
        renames = (
            ("pub unsafe fn a() {}", "pub unsafe fn b() {}", "b"),
            ('pub extern "C" fn a() {}', 'pub extern "C" fn b() {}', "b"),
            ("pub mod a;", "pub mod b;", "b"),
            ("pub union A {}", "pub union B {}", "B"),
            ("pub(in crate::x) fn a() {}", "pub(in crate::x) fn b() {}", "b"),
        )
        for old, new, name in renames:
            with self.subTest(new=new):
                landed = self.designing(s=self.fresh_routed()).call("Edit", edit("src/a.rs", new, old=old))
                self.assertIn(f'(adds a public top-level definition ("{name}"))', owed(landed))

    def test_a_third_code_file_selects_decoupling(self) -> None:
        s = self.designing()
        for path in ("src/a.py", "src/b.py", "src/a.py"):
            quiet = s.call("Edit", edit(path, "x = 1"))
            self.assertEqual((decision(quiet), owed(quiet)), ("pass", ""))
        landed = s.call("Edit", edit("src/c.py", PLAIN))
        self.assertEqual(decision(landed), "pass")
        self.assertEqual(owed_names(landed), {"decoupling.md"})
        self.assertIn("references/decoupling.md` (the third code file", owed(landed))

    def test_a_later_edit_owes_only_an_unread_reference_it_trips(self) -> None:
        s = self.designing()
        first = s.call("Edit", edit("src/export.py", PLAIN))
        self.assertEqual((decision(first), owed(first)), ("pass", ""))

        landed = s.call("Edit", edit("src/export.py", "try:\n    rate = 1"))
        self.assertEqual(decision(landed), "pass")
        self.assertIn("the design-reads gate let this write", owed(landed))
        self.assertEqual(owed_names(landed), {"errors.md"})
        self.assertIn("`software-design-principles/references/errors.md` (adds error handling", owed(landed))
        self.assertIn("\"export.py\"", owed(landed))
        s.read(REFERENCES + "errors.md")
        # One tripping only read references, or none, owes nothing, even in
        # a new turn, where an unread one would be owed again.
        next_turn(s)
        for text in ("try:\n    rate = 1", "except ValueError:", "rate = 2"):
            quiet = s.call("Edit", edit("src/export.py", text))
            self.assertEqual((decision(quiet), owed(quiet)), ("pass", ""))

    def test_small_edits_without_the_skill_are_not_held_for_references(self) -> None:
        s = self.routed()
        self.assertEqual(decision(s.call("Edit", edit("src/export.py", "try:\n    rate = 1"))), "pass")

    def test_a_read_counts_until_the_next_compaction(self) -> None:
        s = self.designing()
        s.read(REFERENCES + "errors.md")
        quiet = s.call("Edit", edit("src/a.py", "try:\n    x = 1"))
        self.assertEqual((decision(quiet), owed(quiet)), ("pass", ""))

        # A later turn, before any compaction: the read still counts.
        s.prompt("Now the importer.")
        s.say("goated-route: continue")
        self.designing(s=s)
        quiet = s.call("Edit", edit("src/b.py", "try:\n    x = 1"))
        self.assertEqual((decision(quiet), owed(quiet)), ("pass", ""))

        s.compact()
        s.load(ROUTER)
        s.say("goated-route: continue")
        self.designing(s=s)
        landed = s.call("Edit", edit("src/b.py", "try:\n    x = 1"))
        self.assertEqual(decision(landed), "pass")
        self.assertEqual(owed_names(landed), {"errors.md"})
        s.read(REFERENCES + "errors.md")
        next_turn(s)
        quiet = s.call("Edit", edit("src/b.py", "try:\n    x = 1"))
        self.assertEqual((decision(quiet), owed(quiet)), ("pass", ""))

    def test_a_skip_line_clears_both_holds(self) -> None:
        s = self.routed()
        s.load("software-design-principles")
        s.say("goated-skip: software-design-principles: this is a mechanical rename only")
        self.assertEqual(decision(s.call("Write", write("src/export.py"))), "pass")
        self.assertEqual(decision(s.call("Edit", edit("src/export.py", "try:\n    x = 1"))), "pass")

    def test_an_override_clears_both_holds(self) -> None:
        s = self.routed(prompt="Fix it, and skip software-design-principles.")
        self.assertEqual(decision(s.call("Write", write("src/export.py"))), "pass")
        s.load("software-design-principles")
        self.assertEqual(decision(s.call("Edit", edit("src/export.py", "try:\n    x = 1"))), "pass")

    def test_files_outside_the_project_are_not_held(self) -> None:
        s = self.designing()
        outside = str(self.root / "scratch")
        self.assertEqual(owed(s.call("Write", write(f"{outside}/probe.py", lines=40))), "")
        self.assertEqual(owed(s.call("Edit", edit(f"{outside}/probe.py", "try:\n    x = 1"))), "")
        landed = s.call("Edit", edit(f"{s.project}/src/probe.py", "try:\n    x = 1"))
        self.assertEqual(owed_names(landed), {"errors.md"})

    def test_a_typical_change_requires_five_references(self) -> None:
        # One new public function with a docstring and error handling, its caller, and a test.
        s = self.designing()
        landed = s.call("Edit", edit(
            "src/rows.py", 'def load(path):\n    """Load the rows."""\n    try:\n        return read(path)'))
        named = owed_names(landed)
        self.assertEqual(named, {"process.md", "complexity-and-modules.md", "readability.md", "errors.md"})
        for name in named:
            s.read(REFERENCES + name)
        self.assertEqual(owed(s.call("Edit", edit("src/cli.py", "rows = load(path)"))), "")
        landed = s.call("Edit", edit("tests/test_rows.py", "def test_load():\n" + lines_of("    assert load(P{n})", 4)))
        self.assertEqual(owed_names(landed), {"coding.md"})

    def test_the_third_code_file_leaves_out_test_files(self) -> None:
        s = self.designing()
        for path in ("src/a.py", "tests/test_a.py", "tests/test_b.py", "src/b.py"):
            s.read(REFERENCES + "coding.md")
            self.assertEqual(owed(s.call("Edit", edit(path, "x = 1"))), "", path)
        landed = s.call("Edit", edit("src/c.py", PLAIN))
        self.assertIn("references/decoupling.md` (the third code file", owed(landed))

    def test_lock_and_test_data_files_are_not_configuration(self) -> None:
        s = self.designing()
        s.say("goated-skip: code-security-review: lockfile regenerated with no version change")
        for path in ("package-lock.json", "pnpm-lock.yaml", "tests/fixtures/rows.json"):
            self.assertEqual(owed(s.call("Edit", edit(path, '"rate": 1'))), "", path)
        self.assertEqual(owed_names(s.call("Edit", edit("config/app.json", lines_of('"rate_{n}": {n},', 5)))),
                         {"decoupling.md"})

    def test_configuration_under_a_fixtures_folder_is_test_data(self) -> None:
        s = self.designing()
        for path in ("stack/fixtures/x.yaml", "a/fixtures/b.json", "a/__fixtures__/b.json"):
            self.assertEqual(owed(s.call("Edit", edit(path, lines_of("rate_{n}: {n}", 5)))), "", path)
        landed = s.call("Edit", edit("config/app.yaml", lines_of("rate_{n}: {n}", 5)))
        self.assertIn("references/decoupling.md` (edits a configuration file", owed(landed))

    def test_a_code_file_under_a_fixtures_folder_is_still_code(self) -> None:
        s = self.designing()
        landed = s.call("Edit", edit("fixtures/build.py", "def build():\n    return 1"))
        self.assertEqual(decision(landed), "pass")
        self.assertIn("process.md", owed_names(landed))

    def test_a_write_over_an_existing_file_counts_only_what_it_adds(self) -> None:
        s = self.designing()
        old = (
            'def export(rows):\n    """Write the rows."""\n    try:\n        save(rows)\n'
            "    except OSError:\n        raise\n"
        )
        (s.project / "src").mkdir(parents=True, exist_ok=True)
        (s.project / "src" / "export.py").write_text(old, encoding="utf-8")
        path = f"{s.project}/src/export.py"
        # A signature change, a re-indent, and the same try, except, and docstring add nothing.
        rewritten = (
            'def export(rows, sep=","):\n  """Write the rows."""\n  try:\n      save(rows)\n'
            "  except OSError:\n      raise\n"
        )
        quiet = s.call("Write", {"file_path": path, "content": rewritten})
        self.assertEqual((decision(quiet), owed(quiet)), ("pass", ""))
        landed = s.call("Write", {"file_path": path, "content": old + "\ndef publish():\n    pass\n"})
        self.assertEqual(decision(landed), "pass")
        self.assertIn('references/process.md` (adds a public top-level definition ("publish"))', owed(landed))

    def test_a_resume_keeps_reads_and_a_clear_drops_them(self) -> None:
        s = self.designing()
        s.read(REFERENCES + "errors.md")
        self.assertEqual(owed(s.call("Edit", edit("src/a.py", "try:\n    x = 1"))), "")
        s.hook("SessionStart", source="resume")
        s.prompt("Carry on.")
        s.say("goated-route: continue")
        self.designing(s=s)
        self.assertEqual(owed(s.call("Edit", edit("src/a.py", "try:\n    x = 1"))), "")

        s.hook("SessionStart", source="clear")
        s.prompt("Next task.")
        s.load(ROUTER)
        s.say("goated-route: direct")
        self.designing(s=s)
        landed = s.call("Edit", edit("src/a.py", "try:\n    x = 1"))
        self.assertEqual(owed_names(landed), {"errors.md"})

    def test_a_shell_read_of_a_reference_does_not_count(self) -> None:
        s = self.designing()
        s.run("cat " + REFERENCES + "errors.md")
        landed = s.call("Edit", edit("src/a.py", "try:\n    x = 1"))
        self.assertEqual(owed_names(landed), {"errors.md"})

    def test_a_subagents_reads_stay_in_its_own_turn(self) -> None:
        s = self.designing()
        agent = s.subagent("a9")
        agent.prompt("Add the retry.", hook=False)
        agent.load("software-design-principles")
        agent.read(REFERENCES + "errors.md")
        sub = agent.call("Edit", edit("src/a.py", "try:\n    x = 1"), agent_id="a9",
                         agent_type="general-purpose")
        self.assertEqual(decision(sub), "pass")
        landed = s.call("Edit", edit("src/b.py", "try:\n    x = 1"))
        self.assertEqual(owed_names(landed), {"errors.md"})

    def fresh_routed(self) -> Session:
        s = self.fresh()
        s.prompt("Do the task.")
        s.load(ROUTER)
        s.say("goated-route: direct")
        return s


class SmallEditTests(AdapterTestCase):
    """Small edits select no reference by file kind (Ticket 063): fewer than
    five added lines, the `design` gate's threshold."""

    def designing(self) -> Session:
        """A new session, routed, with the skill loaded."""

        self.session = self.fresh()
        s = self.routed()
        s.load("software-design-principles")
        return s

    def assert_requires(self, landed: dict, expected: set[str]) -> None:
        # Since Ticket 118 an edit lands at any size, owing what it selects.
        self.assertEqual(decision(landed), "pass", reason(landed))
        self.assertEqual(owed_names(landed), expected, owed(landed))

    def test_a_small_test_file_edit_requires_no_reference(self) -> None:
        for count, expected in ((1, set()), (4, set()), (5, {"coding.md"}), (20, {"coding.md"})):
            with self.subTest(lines=count):
                s = self.designing()
                held = s.call("Edit", edit("tests/test_export.py", lines_of("    assert total_{n}", count)))
                self.assert_requires(held, expected)

    def test_size_counts_every_line_the_edit_writes(self) -> None:
        # As the `design` gate counts: four lines and a trailing newline are five, context lines included.
        four = lines_of("    assert total_{n}", 4)
        for name, tool_input, expected in (
            ("four lines", edit("tests/test_export.py", four), set()),
            ("four lines and a trailing newline", edit("tests/test_export.py", four + "\n"), {"coding.md"}),
            ("one new line in five written", edit("tests/test_export.py", four + "\n    assert done", old=four),
             {"coding.md"}),
        ):
            with self.subTest(name):
                s = self.designing()
                self.assert_requires(s.call("Edit", tool_input), expected)

    def test_a_small_configuration_edit_requires_no_reference(self) -> None:
        for count, expected in ((2, set()), (4, set()), (5, {"decoupling.md"})):
            with self.subTest(lines=count):
                s = self.designing()
                self.assert_requires(s.call("Edit", edit("config/app.yaml", lines_of("rate_{n}: {n}", count))),
                                     expected)

    def test_a_small_edit_to_the_third_code_file_requires_no_reference(self) -> None:
        for count, expected in ((2, set()), (4, set()), (5, {"decoupling.md"})):
            with self.subTest(lines=count):
                s = self.designing()
                for path in ("src/a.py", "src/b.py"):
                    self.assert_requires(s.call("Edit", edit(path, "x = 1")), set())
                self.assert_requires(s.call("Edit", edit("src/c.py", lines_of("total_{n} = {n}", count))),
                                     expected)

    def test_a_small_added_comment_requires_no_reference(self) -> None:
        # With no code lines, a comment selects `readability.md` only at
        # twenty comment lines (round 5, K1).
        for count, expected in ((1, set()), (4, set()), (5, set()), (19, set()),
                                (20, {"readability.md"})):
            with self.subTest(lines=count):
                s = self.designing()
                self.assert_requires(s.call("Edit", edit("src/a.py", lines_of("# note {n} on the rate", count))),
                                     expected)

    def test_signals_from_the_added_code_apply_at_any_size(self) -> None:
        public = {"process.md", "complexity-and-modules.md", "readability.md"}
        cases = (
            # (name, input, references it selects, near-miss input)
            ("error handling", edit("src/a.py", "except ValueError:"), {"errors.md"},
             edit("src/a.py", "rate = 1")),
            ("concurrency", edit("src/a.py", "guard = threading.Lock()"), {"concurrency.md"},
             edit("src/a.py", "clock = 1")),
            ("new public function", edit("src/a.py", "def export(rows):\n    rows = list(rows)\n    return rows"),
             public, edit("src/a.py", "def _export(rows):\n    rows = list(rows)\n    return rows")),
            ("new code file", {"file_path": "src/fresh.py", "content": "x = 1"}, public,
             edit("src/other.py", "x = 1")),
        )
        for name, tool_input, selects, near in cases:
            with self.subTest(name):
                s = self.designing()
                self.assert_requires(s.call("Edit", near), set())
                landed = s.call("Write" if "content" in tool_input else "Edit", tool_input)
                self.assertIn("the design-reads gate let this write", owed(landed))
                self.assert_requires(landed, selects)

    def test_an_edit_whose_lines_cannot_be_counted_is_not_small(self) -> None:
        s = self.designing()
        # An edit that does not show its text cannot land owing its reads, so it is held.
        held = s.call("MultiEdit", {"file_path": "tests/test_export.py", "edits": ["assert total"]})
        self.assertEqual(hold_line(held), "goated-hold: design-reads | justified-skip")
        self.assertEqual(set(re.findall(r"references/([a-z-]+\.md)`", reason(held))), {"coding.md"})

        s = self.designing()
        near = {"file_path": "tests/test_export.py", "edits": [{"old_string": "a", "new_string": "b"}]}
        self.assert_requires(s.call("MultiEdit", near), set())


class SecurityHoldTests(AdapterTestCase):
    def test_a_sensitive_path_is_held_until_security_review_loads(self) -> None:
        s = self.routed()
        edit = {"file_path": "src/auth/login.py", "old_string": "a", "new_string": "b"}

        held = s.call("Edit", edit)
        self.assertEqual(hold_line(held), "goated-hold: security | justified-skip")
        self.assertIn("auth", reason(held))
        self.assertEqual(decision(s.call("Edit", edit)), "deny")
        s.load("code-security-review")
        self.assertEqual(decision(s.call("Edit", edit)), "pass")

    def test_a_skip_line_passes_the_security_hold(self) -> None:
        s = self.routed()
        s.say("goated-skip: code-security-review: only a comment typo in the file")

        edit = {"file_path": "package.json", "old_string": "a", "new_string": "b"}
        self.assertEqual(decision(s.call("Edit", edit)), "pass")

    def test_ordinary_paths_and_docs_are_not_held(self) -> None:
        s = self.routed()
        for path in ("src/export.py", "docs/auth.md"):
            with self.subTest(path=path):
                edit = {"file_path": path, "old_string": "a", "new_string": "b"}
                self.assertEqual(decision(s.call("Edit", edit)), "pass")


def git_bash(path: str) -> str:
    """A Windows path as Git Bash writes it: `C:\\x` is `/c/x`."""

    path = path.replace("\\", "/")
    return "/" + path[0].lower() + path[2:]


class OutOfProjectTests(AdapterTestCase):
    """The design and security gates, and the closeout, count only project files (AC11).

    `self.outside` is an absolute folder beside the project, not inside it.
    """

    def setUp(self) -> None:
        super().setUp()
        self.outside = str(self.root / "scratch")
        self.inside = str(self.session.project)

    def changed_by(self, command: str, tool: str = "Bash") -> dict:
        """Run `command` in a fresh session, with `{inside}` as its project folder,
        and return what the closeout says."""

        s = self.fresh()
        s.prompt("Tidy it.")
        s.load(ROUTER)
        s.say("goated-route: direct")
        command = command.replace("{inside}", str(s.project))
        self.assertEqual(decision(s.run(command, tool=tool)), "pass")
        return stop(s)

    def test_a_large_code_write_outside_the_project_skips_the_design_gate(self) -> None:
        s = self.routed()

        outside = s.call("Write", write(f"{self.outside}/probe.py", lines=40))
        self.assertEqual(decision(outside), "pass")
        inside = s.call("Write", write(f"{self.inside}/src/probe.py", lines=40))
        self.assertEqual(hold_line(inside), "goated-hold: design | justified-skip")

    def test_a_sensitive_write_outside_the_project_skips_the_security_gate(self) -> None:
        s = self.routed()
        edit = {"file_path": f"{self.outside}/.env", "old_string": "a", "new_string": "b"}
        self.assertEqual(decision(s.call("Edit", edit)), "pass")
        edit = {"file_path": f"{self.inside}/.env", "old_string": "a", "new_string": "b"}
        self.assertEqual(hold_line(s.call("Edit", edit)), "goated-hold: security | justified-skip")

    def test_a_cd_through_dot_dot_is_read_as_cd_reads_it(self) -> None:
        """Ticket 058 review: `cd` drops `..` from the folder's text (bash's
        default `cd -L`) before any mount is reached, so `cd /tmp/../c/proj`
        is in `/c/proj`, not beside the temp folder. Near misses: a `..` that
        lands back under `/tmp`, and one that climbs out of the project."""

        for template, inside in (
            ("cd /tmp/..{project} && echo 'print(1)' > x.py", True),
            ("cd '/tmp/..{project}' && echo 'print(1)' > x.py", True),
            ("cd /tmp && cd '..{project}' && echo 'print(1)' > x.py", True),
            ("cd /c/..{project} && echo 'print(1)' > x.py", True),
            ("cd {project}/sub/.. && echo 'print(1)' > x.py", True),
            ("cd /tmp/scratch/.. && echo 'print(1)' > x.py", False),
            ("cd {project}/.. && echo 'print(1)' > x.py", False),
        ):
            with self.subTest(command=template):
                s = self.fresh()
                s.prompt("Tidy it.")
                s.load(ROUTER)
                s.say("goated-route: direct")
                project = str(s.project)
                project = git_bash(project) if os.name == "nt" else Path(project).as_posix()
                s.run(template.replace("{project}", project))
                self.assertEqual("- Proof:" in stop(s).get("reason", ""), inside)

    def test_a_rooted_path_with_no_drive_is_outside_only_off_windows(self) -> None:
        """On Windows, `/etc/x` may be under Git Bash's install folder, a user's
        mount, or a folder on any drive, so it is not certainly outside."""

        s = self.routed()
        edit = {"file_path": "/etc/scratch/auth/login.py", "old_string": "a", "new_string": "b"}
        if os.name == "nt":
            self.assertEqual(hold_line(s.call("Edit", edit)),
                             "goated-hold: security | justified-skip")
        else:
            self.assertEqual(decision(s.call("Edit", edit)), "pass")

    def test_a_git_bash_tmp_write_is_not_a_project_change(self) -> None:
        """Ticket 058 (spec R10): Git Bash mounts `/tmp` on the temp folder, so a
        scratch write there raises no Proof or Docs item. The near miss, the
        project's own file named in Git Bash form, still does."""

        for command in (
            "echo 'print(1)' > /tmp/x.py",
            "cat > /tmp/claude/scratchpad/probe.py <<'EOF'\nprint(1)\nEOF",
            "cd /tmp/claude/scratchpad && echo 'print(1)' > probe.py",
        ):
            with self.subTest(command=command):
                self.assertEqual(self.changed_by(command), {})
        inside = "echo 'print(1)' > {inside}/x.py"
        if os.name == "nt":
            inside = "echo 'print(1)' > {git_bash}/x.py"
        s = self.fresh()
        s.prompt("Tidy it.")
        s.load(ROUTER)
        s.say("goated-route: direct")
        s.run(inside.replace("{inside}", str(s.project))
              .replace("{git_bash}", git_bash(str(s.project))))
        held = stop(s)
        self.assertIn("- Proof:", held.get("reason", ""))
        self.assertIn("- Docs:", held.get("reason", ""))

    @unittest.skipUnless(os.name == "nt", "Git Bash mounts exist only on Windows")
    def test_tmp_is_inside_when_the_temp_folder_is_not_certain(self) -> None:
        """`/tmp` is read through `TMP` and `TEMP`; when neither is set, or
        either is not an absolute Windows path, where `/tmp` is cannot be
        said, so it is inside."""

        from unittest import mock

        good = tempfile.gettempdir()
        for tmp, temp in ((None, None), ("/tmp", None), (None, "relative\\temp"),
                          ("%LOCALAPPDATA%\\Temp", good), (good, "/tmp")):
            with self.subTest(tmp=tmp, temp=temp):
                environment = {k: v for k, v in os.environ.items() if k not in ("TMP", "TEMP")}
                environment.update({k: v for k, v in (("TMP", tmp), ("TEMP", temp)) if v})
                with mock.patch.dict(os.environ, environment, clear=True):
                    held = self.changed_by("echo 'print(1)' > /tmp/x.py")
                self.assertIn("- Proof:", held.get("reason", ""))

    @unittest.skipUnless(os.name == "nt", "8.3 short names exist only on Windows")
    def test_tmp_matches_a_temp_folder_named_by_its_short_name(self) -> None:
        """The session's scratchpad sits under a `TEMP` such as
        `C:\\Users\\LONGNA~1\\AppData\\Local\\Temp`; `/tmp` reads the same folder."""

        import ctypes
        from unittest import mock

        buffer = ctypes.create_unicode_buffer(32768)
        if not ctypes.windll.kernel32.GetShortPathNameW(tempfile.gettempdir(), buffer, 32768):
            self.skipTest("no short name for the temp folder")
        with mock.patch.dict(os.environ, {"TMP": buffer.value, "TEMP": buffer.value}):
            self.assertEqual(self.changed_by("echo 'print(1)' > /tmp/x.py"), {})

    def test_a_shell_write_after_a_cd_outside_skips_the_security_gate(self) -> None:
        s = self.routed()

        outside = s.run(f'cd "{self.outside}" && echo KEY=1 > .env')
        self.assertEqual(decision(outside), "pass")
        inside = s.run("cd config && echo KEY=1 > .env")
        self.assertEqual(hold_line(inside), "goated-hold: security | justified-skip")

    def test_a_move_after_a_cd_outside_is_not_a_project_change(self) -> None:
        for tool, command in (
            ("Bash", f'cd "{self.outside}" && mv a.py b.py'),
            ("Bash", f'cd -- "{self.outside}" && mv a.py b.py'),
            ("Bash", "cd ~/.claude/hooks && mv a.ps1 b.ps1"),
            ("Bash", "cd ./src && cd ../.. && mv a.py b.py"),
            ("Bash", f'cd "{self.outside}" && cd ../elsewhere && mv a.py b.py'),
            ("PowerShell", f"Set-Location -Path '{self.outside}' && Move-Item a.py b.py"),
            ("PowerShell", f"Set-Location '{self.outside}' && Move-Item a.py b.py"),
            ("Bash", "cd /tmp/scratch && mv a.py b.py"),
            # The maintainer's scratch merge clone (ticket 058).
            ("Bash", f'cd "{self.outside}/merge26" && git checkout --theirs src/adapter-texts.ts'),
        ):
            with self.subTest(command=command):
                self.assertEqual(self.changed_by(command, tool), {})

    def test_a_scratch_write_under_the_temp_folder_is_outside(self) -> None:
        s = self.routed()
        scratch = Path(tempfile.gettempdir()) / "goated-scratch-043" / "probe.py"

        self.assertEqual(decision(s.call("Write", write(str(scratch), lines=40))), "pass")
        self.assertEqual(decision(s.call("Write", write(scratch.as_posix(), lines=40))), "pass")

    def test_a_move_after_a_cd_inside_is_a_project_change(self) -> None:
        # The ticket's criterion: `cd sub` is not followed (`CDPATH` may move
        # it elsewhere), so its folder is unknown and the move counts as inside.
        for tool, command in (
            ("Bash", "cd sub && mv a.py b.py"),
            ("Bash", "cd ./sub && mv a.py b.py"),
            ("Bash", f'pushd "{self.outside}" && mv a.py b.py && popd'),
            ("Bash", 'cd "{inside}/sub" && mv a.py b.py'),
            ("Bash", f'cd "{self.outside}" && cd "{{inside}}" && mv a.py b.py'),
            ("PowerShell", "Set-Location sub; Move-Item a.py b.py"),
        ):
            with self.subTest(command=command):
                held = self.changed_by(command, tool)
                self.assertEqual(closeout_line(held), "goated-hold: closeout | justified-skip")

    def assert_security_held(self, s: Session, command: str, held: bool = True) -> None:
        with self.subTest(command=command):
            output = s.run(command)
            if held:
                self.assertEqual(hold_line(output), "goated-hold: security | justified-skip")
            else:
                self.assertEqual(decision(output), "pass")

    def test_a_cd_that_does_not_carry_over_leaves_the_target_inside(self) -> None:
        s = self.routed()
        for command in (
            f'(cd "{self.outside}") ; echo K=1 > .env',
            f'cd "{self.outside}" || echo K=1 > .env',
            f'cd "{self.outside}" | true; echo K=1 > .env',
            f'true | cd "{self.outside}"; echo K=1 > .env',
            f'here=$(cd "{self.outside}" && pwd); echo K=1 > .env',
        ):
            self.assert_security_held(s, command)
        self.assert_security_held(s, f'cd "{self.outside}" && echo K=1 > .env', held=False)

    def test_only_a_leading_and_chain_of_cds_is_followed(self) -> None:
        """A `cd` outside a leading `&&` chain makes the folder unknown for the
        rest of the command, so relative targets after it count as inside."""

        s = self.routed()
        for command in (
            # An unknown folder stays unknown, even after a later `cd`.
            'cd "$X" && cd ../.. && echo K=1 > .env',
            f'cd "$X" && cd "{self.outside}" && echo K=1 > .env',
            f'(cd x) ; cd "{self.outside}"; echo K=1 > .env',
            # A `cd` that may fail or never run.
            "cd /tmp/nope; echo K=1 > .env",
            "cd /tmp/nope\necho K=1 > .env",
            "test -d /tmp/nope && cd /tmp/nope; echo K=1 > .env",
            "if cd /tmp/nope; then :; fi; echo K=1 > .env",
            "if true; then cd /tmp; fi; echo K=1 > .env",
            "case x in y) cd /tmp;; esac; echo K=1 > .env",
            "false || cd /tmp && echo K=1 > .env",
            # Brace groups.
            "{ cd /tmp; } | cat; echo K=1 > .env",
            "{ cd /tmp; } & echo K=1 > .env",
            "{ cd /tmp; } || true; echo K=1 > .env",
            "{ cd /tmp; } && echo K=1 > .env",
            # Bash's previous and current folders, and a glob.
            "cd /tmp && cd ~- && echo K=1 > .env",
            "cd /tmp && cd ~+ && echo K=1 > .env",
            "cd /tm* && echo K=1 > .env",
        ):
            self.assert_security_held(s, command)
        for command in (
            "Set-Location C:/nope; Set-Content .env x",
            "Set-Location /tmp | Out-Null; Set-Content .env x",
            "Start-Job { Set-Location /tmp }; Set-Content .env x",
        ):
            with self.subTest(command=command):
                held = s.run(command, tool="PowerShell")
                self.assertEqual(hold_line(held), "goated-hold: security | justified-skip")
        # Near misses: a leading `&&` chain is followed.
        self.assert_security_held(s, f'cd "{self.outside}" && cd ./sub && echo K=1 > .env',
                                  held=False)

    def test_only_a_plain_cd_to_a_plain_path_is_followed(self) -> None:
        s = self.routed()
        out = self.outside
        for command in (
            f'! cd "{out}" && echo K=1 > .env',
            f'pushd "{out}" && echo K=1 > .env',
            f'pushd -n "{out}" && echo K=1 > .env',
            f'cd "{out}" && pushd +1 && echo K=1 > .env',
            f'cd "{out}" && cd -1 && echo K=1 > .env',
            f'cd -P "{out}" && echo K=1 > .env',
            f'cd "{out}" "{out}" && echo K=1 > .env',
            # A bare relative name may resolve against CDPATH.
            f'cd "{out}" && cd deep/../.. && echo K=1 > .env',
            f'cd "{out}" && cd sub && echo K=1 > .env',
        ):
            self.assert_security_held(s, command)
        for command in (
            f"Push-Location -StackName '{out}' . && Set-Content .env x",
            f"Push-Location '{out}' && Set-Content .env x",
            f"Set-Location -StackName '{out}' && Set-Content .env x",
            f"Set-Location '{out}' -WhatIf && Set-Content .env x",
            f"Set-Location -Path '{out}' -LiteralPath x && Set-Content .env x",
        ):
            with self.subTest(command=command):
                held = s.run(command, tool="PowerShell")
                self.assertEqual(hold_line(held), "goated-hold: security | justified-skip")

    def test_a_link_into_the_project_is_inside(self) -> None:
        self.session.project.mkdir(parents=True)
        link = self.root / "link-to-project"
        try:
            if os.name == "nt":
                import _winapi

                _winapi.CreateJunction(str(self.session.project), str(link))
            else:
                os.symlink(self.session.project, link, target_is_directory=True)
        except OSError as exc:
            self.skipTest(f"cannot make a folder link here: {exc}")
        try:
            s = self.routed()
            edit = {"file_path": f"{link}/.env", "old_string": "a", "new_string": "b"}

            self.assertEqual(hold_line(s.call("Edit", edit)),
                             "goated-hold: security | justified-skip")
            self.assert_security_held(s, f'echo K=1 > "{link}/.env"')
            self.assert_security_held(s, f'cd "{link}" && echo K=1 > .env')
            self.assert_security_held(s, f'cd "{self.outside}" && echo K=1 > .env', held=False)
        finally:
            # Remove the link itself, so cleaning up the folder never follows it.
            os.rmdir(link) if os.name == "nt" else os.unlink(link)

    def test_a_home_path_is_read_with_the_home_variable_too(self) -> None:
        from unittest import mock

        s = self.routed()
        edit = {"file_path": "~/.env", "old_string": "a", "new_string": "b"}
        with mock.patch.dict(os.environ, {"HOME": self.inside}):
            self.assertEqual(hold_line(s.call("Edit", edit)),
                             "goated-hold: security | justified-skip")
        with mock.patch.dict(os.environ, {"HOME": self.outside}):
            self.assertEqual(decision(s.call("Edit", edit)), "pass")

    @unittest.skipUnless(os.name == "nt", "Windows drops trailing dots and spaces")
    def test_a_folder_name_ending_in_a_dot_or_space_counts_as_inside(self) -> None:
        s = self.routed()
        for path in (f"{self.inside}.../sub/../.env", f"{self.inside}./.env",
                     f"{self.inside} /.env", f"{self.outside}./x/.env"):
            with self.subTest(path=path):
                edit = {"file_path": path, "old_string": "a", "new_string": "b"}
                self.assertEqual(hold_line(s.call("Edit", edit)),
                                 "goated-hold: security | justified-skip")

    @unittest.skipUnless(os.name == "nt", "Git Bash mounts exist only on Windows")
    def test_git_bash_mounts_count_as_inside(self) -> None:
        s = self.routed()
        under_temp = os.path.relpath(self.inside, tempfile.gettempdir()).replace("\\", "/")

        self.assert_security_held(s, f"echo K=1 > /tmp/{under_temp}/.env")
        self.assert_security_held(s, f"cd /tmp && echo K=1 > {under_temp}/.env")
        self.assert_security_held(s, "echo K=1 > /etc/.env")
        # A one-letter top folder whose drive does not exist is not certainly a drive.
        missing = next((d for d in "QJKLMNOX" if not os.path.exists(f"{d}:\\")), None)
        if missing:
            self.assert_security_held(s, f"echo K=1 > /{missing.lower()}/.env")

    def test_device_network_and_unexpanded_paths_count_as_inside(self) -> None:
        s = self.routed()
        native = self.inside.replace("/", "\\")
        posix = self.inside.replace("\\", "/")
        for path in (f"\\\\?\\{native}\\.env", f"//?/{posix}/.env", f"\\\\.\\{native}\\.env",
                     "\\\\server\\share\\.env", "//server/share/.env", "~other/.env",
                     "~-/.env", "$HOME/.env", "%USERPROFILE%/.env"):
            with self.subTest(path=path):
                edit = {"file_path": path, "old_string": "a", "new_string": "b"}
                self.assertEqual(hold_line(s.call("Edit", edit)),
                                 "goated-hold: security | justified-skip")
                self.assert_security_held(s, f"echo K=1 > '{path}'")

    @unittest.skipUnless(os.name == "nt", "Git Bash drive paths exist only on Windows")
    def test_git_bash_drive_paths_are_read_as_windows_paths(self) -> None:
        s = self.routed()
        inside, outside = git_bash(self.inside), git_bash(self.outside)
        self.assert_security_held(s, f"echo K=1 > {inside}/.env")
        self.assert_security_held(s, f"echo K=1 > {inside.upper()}/.env")
        self.assert_security_held(s, f"cd {inside} && echo K=1 > .env")
        self.assert_security_held(s, f"echo K=1 > {outside}/.env", held=False)
        self.assert_security_held(s, f"cd {outside} && echo K=1 > .env", held=False)
        edit = {"file_path": f"{inside}/.env", "old_string": "a", "new_string": "b"}
        self.assertEqual(hold_line(s.call("Edit", edit)), "goated-hold: security | justified-skip")
        edit = {"file_path": f"{outside}/.env", "old_string": "a", "new_string": "b"}
        self.assertEqual(decision(s.call("Edit", edit)), "pass")

    @unittest.skipUnless(os.name == "nt", "Git Bash drive paths exist only on Windows")
    def test_a_project_folder_in_git_bash_form_is_read_as_a_windows_path(self) -> None:
        for setting in ("cwd", "project_dir"):
            with self.subTest(setting=setting):
                s = self.fresh()
                s.project.mkdir(parents=True)
                if setting == "cwd":
                    s.cwd = git_bash(str(s.project))
                else:
                    s.config.project_dir = git_bash(str(s.project))
                s.prompt("Tidy it.")
                s.load(ROUTER)
                s.say("goated-route: direct")
                for path in (f"{s.project}/.env", ".env"):
                    edit = {"file_path": path, "old_string": "a", "new_string": "b"}
                    self.assertEqual(hold_line(s.call("Edit", edit)),
                                     "goated-hold: security | justified-skip")
                edit = {"file_path": f"{self.outside}/.env", "old_string": "a", "new_string": "b"}
                self.assertEqual(decision(s.call("Edit", edit)), "pass")

    @unittest.skipUnless(os.name == "nt", "drive letters exist only on Windows")
    def test_a_one_letter_top_folder_may_be_a_folder_not_a_drive(self) -> None:
        from goated_core.actions import _in_project, find_project

        project = find_project("C:\\w\\proj")
        self.assertTrue(_in_project("/w/proj/.env", project))
        self.assertTrue(_in_project("/c/w/proj/.env", project))
        self.assertFalse(_in_project("/c/other-043/.env", project))

    @unittest.skipUnless(os.name == "nt", "8.3 short names exist only on Windows")
    def test_a_short_and_a_long_name_for_the_project_match(self) -> None:
        import ctypes

        buffer = ctypes.create_unicode_buffer(32768)
        short = buffer.value if ctypes.windll.kernel32.GetShortPathNameW(
            str(self.root), buffer, len(buffer)) else ""
        long = buffer.value if ctypes.windll.kernel32.GetLongPathNameW(
            str(self.root), buffer, len(buffer)) else ""
        if not short or not long or short.lower() == long.lower():
            self.skipTest("this folder has no distinct 8.3 short name")
        other = long if str(self.root).lower() == short.lower() else short
        s = self.routed()
        project = self.session.project.relative_to(self.root).as_posix()
        edit = {"file_path": f"{other}/{project}/.env", "old_string": "a", "new_string": "b"}
        self.assertEqual(hold_line(s.call("Edit", edit)), "goated-hold: security | justified-skip")
        edit = {"file_path": f"{other}/scratch/.env", "old_string": "a", "new_string": "b"}
        self.assertEqual(decision(s.call("Edit", edit)), "pass")

    def test_the_project_dir_setting_beats_a_session_folder_below_it(self) -> None:
        s = self.routed()
        s.config.project_dir = self.inside
        s.cwd = self.session.project / "adapters"
        ci = {"file_path": f"{self.inside}/.github/workflows/ci.yml", "old_string": "a",
              "new_string": "b"}

        self.assertEqual(hold_line(s.call("Edit", ci)), "goated-hold: security | justified-skip")
        held = s.call("Write", write(f"{self.inside}/tools/build.py", lines=40))
        self.assertEqual(hold_line(held), "goated-hold: design | justified-skip")
        # Relative paths still start from the session's folder.
        self.assert_security_held(s, "echo K=1 > ../.env")
        self.assert_security_held(s, "echo K=1 > ../../.env", held=False)

    def test_the_git_top_level_is_the_project_when_no_setting_names_one(self) -> None:
        s = self.routed()
        (self.session.project / ".git").mkdir(parents=True)
        (self.session.project / "adapters").mkdir()
        s.cwd = self.session.project / "adapters"
        manifest = {"file_path": f"{self.inside}/pyproject.toml", "old_string": "a",
                    "new_string": "b"}

        self.assertEqual(hold_line(s.call("Edit", manifest)), "goated-hold: security | justified-skip")
        outside = {"file_path": f"{self.outside}/pyproject.toml", "old_string": "a",
                   "new_string": "b"}
        self.assertEqual(decision(s.call("Edit", outside)), "pass")

    def test_with_no_setting_or_git_folder_the_session_folder_is_the_project(self) -> None:
        s = self.routed()
        s.cwd = self.session.project / "adapters"
        manifest = {"file_path": f"{self.inside}/pyproject.toml", "old_string": "a",
                    "new_string": "b"}

        self.assertEqual(decision(s.call("Edit", manifest)), "pass")
        manifest["file_path"] = f"{self.inside}/adapters/pyproject.toml"
        self.assertEqual(hold_line(s.call("Edit", manifest)), "goated-hold: security | justified-skip")

    def test_an_unresolvable_cd_leaves_the_target_inside(self) -> None:
        for tool, command in (
            ("Bash", 'cd "$dir" && mv a.py b.py'),
            ("Bash", f'cd "{self.outside}" && cd "$dir" && mv a.py b.py'),
            ("Bash", "cd - && mv a.py b.py"),
            ("Bash", "cd && mv a.py b.py"),
            ("Bash", f'pushd "{self.outside}" && popd && mv a.py b.py'),
            ("PowerShell", "Set-Location $env:TEMP; Move-Item a.py b.py"),
        ):
            with self.subTest(command=command):
                held = self.changed_by(command, tool)
                self.assertEqual(closeout_line(held), "goated-hold: closeout | justified-skip")


MERGE_CONFLICT = (
    "Auto-merging src/app.py\n"
    "CONFLICT (content): Merge conflict in src/app.py\n"
    "Automatic merge failed; fix conflicts and then commit the result."
)
REBASE_CONFLICT = (
    "Auto-merging src/app.py\n"
    "CONFLICT (content): Merge conflict in src/app.py\n"
    "error: could not apply 1a2b3c4... Add export\n"
    "hint: Resolve all conflicts manually, mark them as resolved with\n"
    'hint: "git add/rm <conflicted_files>", then run "git rebase --continue".'
)
REVERT_CONFLICT = (
    "Auto-merging src/app.py\n"
    "CONFLICT (content): Merge conflict in src/app.py\n"
    "error: could not revert 1a2b3c4... Add export\n"
    "hint: After resolving the conflicts, mark them with"
)
STASH_CONFLICT = (
    "Auto-merging src/app.py\n"
    "CONFLICT (content): Merge conflict in src/app.py\n"
    "On branch main\n"
    "The stash entry is kept in case you need it again."
)
CONFLICT_HOLD = "goated-hold: conflict-resolution | justified-skip"
# A Read of a conflicted file, with the line numbers the Read tool adds.
CONFLICTED_READ = (
    "     1\t<<<<<<< HEAD\n     2\trate = 1\n     3\t=======\n     4\trate = 2\n"
    "     5\t>>>>>>> feature\n"
)
CONFLICT_EDIT = {
    "file_path": "src/app.py",
    "old_string": "<<<<<<< HEAD\nrate = 1\n=======\nrate = 2\n>>>>>>> feature\n",
    "new_string": "rate = 2\n",
}


class ConflictResolutionHoldTests(AdapterTestCase):
    """G1: a write while a conflict is open in the turn needs `resolving-merge-conflicts`."""

    def test_an_edit_of_conflict_markers_is_held(self) -> None:
        s = self.routed()

        held = s.call("Edit", CONFLICT_EDIT)
        self.assertEqual(hold_line(held), "goated-hold: conflict-resolution | justified-skip")
        loads = set(re.findall(r"`([a-z0-9-]+)`", reason(held)))
        self.assertEqual(loads, {"resolving-merge-conflicts"})
        self.assertEqual(decision(s.call("Edit", CONFLICT_EDIT)), "deny")

    def test_an_edit_of_conflict_markers_outside_the_project_is_held(self) -> None:
        # A worktree may sit outside the project folder; its conflict is still a conflict.
        s = self.routed()
        edit = dict(CONFLICT_EDIT, file_path=str(self.root / "worktree" / "src" / "app.py"))

        held = s.call("Edit", edit)
        self.assertEqual(hold_line(held), "goated-hold: conflict-resolution | justified-skip")

    def test_a_multiedit_of_conflict_markers_is_held(self) -> None:
        s = self.routed()
        edit = {"file_path": "src/app.py", "edits": [
            {"old_string": "a", "new_string": "b"},
            {"old_string": CONFLICT_EDIT["old_string"], "new_string": "rate = 2\n"},
        ]}
        self.assertEqual(hold_line(s.call("MultiEdit", edit)),
                         "goated-hold: conflict-resolution | justified-skip")

    def test_markers_mentioned_mid_line_are_not_held(self) -> None:
        s = self.routed()
        for old in ("Git writes <<<<<<< and >>>>>>> around a conflict.",
                    "Title\n=======\n", "a\n"):
            with self.subTest(old=old):
                edit = {"file_path": "notes.md", "old_string": old, "new_string": "x"}
                self.assertEqual(decision(s.call("Edit", edit)), "pass")

    def test_a_write_after_a_conflicting_git_result_is_held(self) -> None:
        cases = (
            ("git merge feature", MERGE_CONFLICT),
            ("git pull origin main", MERGE_CONFLICT),
            ("git rebase main", REBASE_CONFLICT),
            ("git pull --rebase", REBASE_CONFLICT),
            ("git cherry-pick 1a2b3c4", REBASE_CONFLICT),
            ("git revert 1a2b3c4", REVERT_CONFLICT),
        )
        for command, output in cases:
            with self.subTest(command=command):
                s = self.fresh()
                s.prompt("Bring the branch up to date.")
                s.load(ROUTER)
                s.say("goated-route: direct")
                s.run(command, success=False, output=output)

                edit = {"file_path": "notes.md", "old_string": "a", "new_string": "b"}
                self.assertEqual(hold_line(s.call("Edit", edit)),
                                 "goated-hold: conflict-resolution | justified-skip")
                self.assertEqual(hold_line(s.call("Write", write("notes.md", 1))),
                                 "goated-hold: conflict-resolution | justified-skip")
                self.assertEqual(hold_line(s.call("Bash", {"command": "echo x > notes.md"})),
                                 "goated-hold: conflict-resolution | justified-skip")
                self.assertEqual(decision(s.call("Bash", {"command": "git status"})), "pass")

    def test_near_misses_after_git_are_not_held(self) -> None:
        cases = (
            ("git merge feature", "Updating 1a2b3c4..5d6e7f8\nFast-forward\n src/app.py | 2 +-"),
            ("git stash pop", STASH_CONFLICT),
            ("git stash apply", STASH_CONFLICT),
            ("grep -rn 'Automatic merge failed' docs", "docs/x.md:3:" + MERGE_CONFLICT),
        )
        for command, output in cases:
            with self.subTest(command=command):
                s = self.fresh()
                s.prompt("Bring the branch up to date.")
                s.load(ROUTER)
                s.say("goated-route: direct")
                s.run(command, output=output)

                edit = {"file_path": "notes.md", "old_string": "a", "new_string": "b"}
                self.assertEqual(decision(s.call("Edit", edit)), "pass")

    def test_a_conflict_in_an_earlier_turn_does_not_hold_a_later_write(self) -> None:
        s = self.routed()
        s.run("git merge feature", success=False, output=MERGE_CONFLICT)
        s.prompt("Now update the notes.")
        s.say("goated-route: continue")

        edit = {"file_path": "notes.md", "old_string": "a", "new_string": "b"}
        self.assertEqual(decision(s.call("Edit", edit)), "pass")

    def test_loading_the_skill_clears_the_hold(self) -> None:
        s = self.routed()
        self.assertEqual(decision(s.call("Edit", CONFLICT_EDIT)), "deny")

        s.load("resolving-merge-conflicts")
        self.assertEqual(decision(s.call("Edit", CONFLICT_EDIT)), "pass")

    def test_a_skip_line_clears_the_hold(self) -> None:
        s = self.routed()
        s.run("git merge feature", success=False, output=MERGE_CONFLICT)
        s.say("goated-skip: resolving-merge-conflicts: the conflict is in a generated lockfile")

        self.assertEqual(decision(s.call("Edit", CONFLICT_EDIT)), "pass")

    def test_a_typed_override_clears_the_hold(self) -> None:
        s = self.routed(prompt="Fix the conflict; skip resolving-merge-conflicts.")

        self.assertEqual(decision(s.call("Edit", CONFLICT_EDIT)), "pass")

    def conflicted(self, prompt: str = "Bring the branch up to date.") -> Session:
        """A fresh routed session whose turn has a conflicting `git merge`."""

        s = self.fresh()
        s.prompt(prompt)
        s.load(ROUTER)
        s.say("goated-route: direct")
        s.run("git merge feature", success=False, output=MERGE_CONFLICT)
        return s

    def test_checking_out_one_side_after_a_conflict_is_held(self) -> None:
        for command in ("git checkout --theirs src/app.py", "git checkout --ours .",
                        "git -C repo checkout --theirs -- src/app.py"):
            with self.subTest(command=command):
                s = self.conflicted()
                self.assertEqual(hold_line(s.call("Bash", {"command": command})), CONFLICT_HOLD)

    def test_powershell_and_git_dash_c_are_read_like_bash(self) -> None:
        s = self.fresh()
        s.prompt("Bring the branch up to date.")
        s.load(ROUTER)
        s.say("goated-route: direct")
        s.run("git -C repo merge feature", tool="PowerShell", success=False, output=MERGE_CONFLICT)

        held = s.call("PowerShell", {"command": "Set-Content -Path notes.txt -Value 'x'"})
        self.assertEqual(hold_line(held), CONFLICT_HOLD)

    def test_a_write_to_a_file_read_with_markers_is_held(self) -> None:
        s = self.routed()
        s.read("src/app.py", content=CONFLICTED_READ)

        self.assertEqual(hold_line(s.call("Write", write("src/app.py", 1))), CONFLICT_HOLD)
        # Old text spanning only the separator and one side, in that file.
        partial = {"file_path": "src/app.py", "old_string": "=======\nrate = 2\n", "new_string": ""}
        self.assertEqual(hold_line(s.call("Edit", partial)), CONFLICT_HOLD)
        self.assertEqual(decision(s.call("Write", write("src/other.py", 1))), "pass")

    def test_a_lone_separator_is_not_a_conflict(self) -> None:
        s = self.routed()
        s.read("docs/guide.rst", content="     1\tSection\n     2\t=======\n")

        self.assertEqual(decision(s.call("Write", write("docs/guide.rst", 1))), "pass")
        edit = {"file_path": "notes.md", "old_string": "=======\nrate = 2\n", "new_string": ""}
        self.assertEqual(decision(s.call("Edit", edit)), "pass")

    def test_label_less_markers_with_crlf_are_held(self) -> None:
        s = self.routed()
        edit = {"file_path": "src/app.py", "old_string": "x\r\n=======\r\ny\r\n>>>>>>>\r\n",
                "new_string": "y\r\n"}
        self.assertEqual(hold_line(s.call("Edit", edit)), CONFLICT_HOLD)

    def test_an_abort_continue_or_commit_ends_the_conflict(self) -> None:
        for command in ("git merge --abort", "git rebase --abort", "git cherry-pick --abort",
                        "git revert --abort", "git rebase --continue", "git cherry-pick --continue",
                        'git commit -m "Merge feature"'):
            with self.subTest(command=command):
                s = self.conflicted('Merge it. Commit message: "Merge feature"')
                s.read("src/app.py", content=CONFLICTED_READ)
                s.run(command)

                edit = {"file_path": "notes.md", "old_string": "a", "new_string": "b"}
                self.assertEqual(decision(s.call("Edit", edit)), "pass")
                self.assertEqual(decision(s.call("Write", write("src/app.py", 1))), "pass")

    def test_a_failed_continue_leaves_the_conflict_open(self) -> None:
        s = self.conflicted()
        s.run("git rebase --continue", success=False,
              output="error: you must edit all merge conflicts and then\nmark them as resolved")

        edit = {"file_path": "notes.md", "old_string": "a", "new_string": "b"}
        self.assertEqual(hold_line(s.call("Edit", edit)), CONFLICT_HOLD)

    def test_a_new_conflict_after_an_abort_reopens_it(self) -> None:
        s = self.conflicted()
        s.run("git merge --abort")
        s.run("git rebase main", success=False, output=REBASE_CONFLICT)

        edit = {"file_path": "notes.md", "old_string": "a", "new_string": "b"}
        self.assertEqual(hold_line(s.call("Edit", edit)), CONFLICT_HOLD)

    def test_a_skip_line_clears_the_marker_path(self) -> None:
        s = self.routed()
        s.say("goated-skip: resolving-merge-conflicts: the markers are a test fixture's text")

        self.assertEqual(decision(s.call("Edit", CONFLICT_EDIT)), "pass")

    def test_a_load_or_an_override_clears_the_after_git_path(self) -> None:
        edit = {"file_path": "notes.md", "old_string": "a", "new_string": "b"}
        loaded = self.conflicted()
        loaded.load("resolving-merge-conflicts")
        self.assertEqual(decision(loaded.call("Edit", edit)), "pass")

        overridden = self.conflicted("Merge it and skip resolving-merge-conflicts.")
        self.assertEqual(decision(overridden.call("Edit", edit)), "pass")

    def test_a_finished_commit_call_ends_the_conflict(self) -> None:
        # R10: a commit tool's finished call ends it, as a shell `git commit` does.
        s = self.conflicted('Merge it. Commit message: "Merge feature"')
        s.read("src/app.py", content=CONFLICTED_READ)
        committed = s.call("mcp__git__git_commit", {"message": "Merge feature"})
        self.assertEqual(decision(committed), "pass")

        edit = {"file_path": "notes.md", "old_string": "a", "new_string": "b"}
        self.assertEqual(decision(s.call("Edit", edit)), "pass")
        self.assertEqual(decision(s.call("Write", write("src/app.py", 1))), "pass")

    def test_a_held_or_failed_commit_call_ends_nothing(self) -> None:
        edit = {"file_path": "notes.md", "old_string": "a", "new_string": "b"}
        held = self.conflicted()  # No message given, so the commit gate holds the call.
        self.assertEqual(decision(held.call("mcp__git__git_commit", {"message": "Merge feature"})),
                         "deny")
        self.assertEqual(hold_line(held.call("Edit", edit)), CONFLICT_HOLD)

        failed = self.conflicted('Merge it. Commit message: "Merge feature"')
        failed.call("mcp__git__git_commit", {"message": "Merge feature"}, failed=True,
                    result="error: committing is not possible because you have unmerged files")
        self.assertEqual(hold_line(failed.call("Edit", edit)), CONFLICT_HOLD)

    def test_a_plain_read_showing_markers_opens_the_conflict_for_its_files(self) -> None:
        # R10, decision G: per file, as a file read.
        shown = "<<<<<<< HEAD\nrate = 1\n=======\nrate = 2\n>>>>>>> feature\n"
        cases = (
            ("Bash", "cat src/app.py"),
            ("Bash", "head -n 20 src/app.py"),
            ("Bash", "tail -n 20 src/app.py"),
            ("Bash", "cat -n src/app.py | head -n 40"),
            ("PowerShell", "Get-Content src/app.py"),
            ("PowerShell", "Get-Content -Path src/app.py -TotalCount 20"),
            ("PowerShell", "type src/app.py"),
            ("PowerShell", "gc src/app.py"),
        )
        for tool, command in cases:
            with self.subTest(command=command):
                s = self.routed()
                s.run(command, tool=tool, output=shown)

                self.assertEqual(hold_line(s.call("Write", write("src/app.py", 1))),
                                 CONFLICT_HOLD)
                self.assertEqual(decision(s.call("Write", write("src/other.py", 1))), "pass")

    def test_a_command_naming_several_files_opens_the_conflict_for_each(self) -> None:
        s = self.routed()
        s.run("cat src/app.py src/b.py", output="<<<<<<< HEAD\nrate = 1\n=======\n>>>>>>> x\n")

        self.assertEqual(hold_line(s.call("Write", write("src/app.py", 1))), CONFLICT_HOLD)
        self.assertEqual(hold_line(s.call("Write", write("src/b.py", 1))), CONFLICT_HOLD)

    def test_a_plain_read_without_markers_opens_nothing(self) -> None:
        cases = (
            ("cat src/app.py", "rate = 2\n", True),
            ("cat src/app.py", "rate = 2\nGit writes <<<<<<< around a conflict.\n", True),
            ("cat src/app.py", "<<<<<<< HEAD\n", False),  # The read failed.
            ("grep -n rate src/app.py", "<<<<<<< HEAD\n", True),  # Not a file printer.
        )
        for command, output, success in cases:
            with self.subTest(command=command, output=output):
                s = self.routed()
                s.run(command, output=output, success=success)

                self.assertEqual(decision(s.call("Write", write("src/app.py", 1))), "pass")

    def test_a_git_diff_showing_markers_opens_the_conflict_for_those_paths(self) -> None:
        combined = (
            "diff --cc src/app.py\n"
            "index 1a2b3c4,5d6e7f8..0000000\n"
            "--- a/src/app.py\n"
            "+++ b/src/app.py\n"
            "@@@ -1,1 -1,1 +1,5 @@@\n"
            "++<<<<<<< HEAD\n"
            " +rate = 1\n"
            "++=======\n"
            "+ rate = 2\n"
            "++>>>>>>> feature\n"
            "diff --cc src/clean.py\n"
            "index 1a2b3c4,5d6e7f8..0000000\n"
            "--- a/src/clean.py\n"
            "+++ b/src/clean.py\n"
            "@@@ -1,1 -1,1 +1,1 @@@\n"
            "- limit = 1\n"
            " -limit = 2\n"
            "++limit = 3\n"
        )
        two_way = (
            "diff --git a/src/app.py b/src/app.py\n"
            "index 1a2b3c4..5d6e7f8 100644\n"
            "--- a/src/app.py\n"
            "+++ b/src/app.py\n"
            "@@ -1 +1,5 @@\n"
            "-rate = 1\n"
            "+<<<<<<< HEAD\n"
            "+rate = 1\n"
            "+=======\n"
            "+rate = 2\n"
            "+>>>>>>> feature\n"
        )
        for command, output in (("git diff", combined), ("git diff HEAD", two_way)):
            with self.subTest(command=command):
                s = self.routed()
                s.run(command, output=output)

                self.assertEqual(hold_line(s.call("Write", write("src/app.py", 1))),
                                 CONFLICT_HOLD)
                self.assertEqual(decision(s.call("Write", write("src/clean.py", 1))), "pass")

    def test_a_git_diff_names_a_quoted_file_as_written(self) -> None:
        # Git quotes a name with a space or a non-ASCII byte, escaping each
        # such byte in octal: `"b/caf\303\251.py"` is `café.py`.
        hunk = "@@ -1 +1,3 @@\n+<<<<<<< HEAD\n+rate = 1\n+>>>>>>> feature\n"
        cases = (
            ('diff --git "a/sp ace.py" "b/sp ace.py"\n--- "a/sp ace.py"\n+++ "b/sp ace.py"\n',
             "sp ace.py"),
            ('diff --git "a/caf\\303\\251.py" "b/caf\\303\\251.py"\n', "café.py"),
            ('diff --cc "say \\"hi\\".py"\n--- a/x\n+++ "b/say \\"hi\\".py"\n', 'say "hi".py'),
        )
        for header, name in cases:
            with self.subTest(name=name):
                s = self.routed()
                s.run("git diff", output=header + hunk)

                self.assertEqual(hold_line(s.call("Write", write(name, 1))), CONFLICT_HOLD)

    def test_a_git_diff_removing_or_mentioning_markers_opens_nothing(self) -> None:
        output = (
            "diff --git a/src/app.py b/src/app.py\n"
            "--- a/src/app.py\n"
            "+++ b/src/app.py\n"
            "@@ -1,5 +1 @@\n"
            "-<<<<<<< HEAD\n"
            "-rate = 1\n"
            "->>>>>>> feature\n"
            "+rate = 2 # was <<<<<<< once\n"
        )
        s = self.routed()
        s.run("git diff", output=output)

        self.assertEqual(decision(s.call("Write", write("src/app.py", 1))), "pass")

    def test_a_commit_drops_the_files_a_shell_read_showed(self) -> None:
        s = self.routed(prompt='Fix it. Commit message: "Merge feature"')
        s.run("cat src/app.py", output="<<<<<<< HEAD\nrate = 1\n>>>>>>> feature\n")
        s.run('git commit -am "Merge feature"')

        self.assertEqual(decision(s.call("Write", write("src/app.py", 1))), "pass")

    def test_the_commit_gate_still_fires_once_the_conflict_gate_clears(self) -> None:
        s = self.conflicted()
        s.load("resolving-merge-conflicts")
        self.assertEqual(decision(s.call("Edit", CONFLICT_EDIT)), "pass")

        held = s.call("Bash", {"command": 'git add src/app.py && git commit -m "Merge feature"'})
        self.assertEqual(hold_line(held), "goated-hold: commit | strict")


CHECK = "uv run python -m unittest discover -s tests"
FIX = {"file_path": "src/export.py", "old_string": "a", "new_string": "b"}
TEST_EDIT = {"file_path": "tests/test_export.py", "old_string": "a", "new_string": "b"}
# Each runner's summary of a failed run with `n` failed or errored tests, as
# the runner prints it.
RUNNER_SUMMARIES = {
    "pytest": lambda n: f"FAILED tests/test_export.py::test_round\n{n} failed, 2 passed in 0.31s",
    "pytest-errors": lambda n: (
        f"===== {n - 1} failed, 4 passed, 1 error in 1.02s =====" if n > 1
        else "===== 4 passed, 1 error in 1.02s ====="
    ),
    "unittest": lambda n: f"Ran 9 tests in 0.004s\n\nFAILED (failures={n})",
    "unittest-errors": lambda n: (
        f"Ran 9 tests in 0.004s\n\nFAILED (failures={n - 1}, errors=1)" if n > 1
        else "Ran 9 tests in 0.004s\n\nFAILED (errors=1)"
    ),
    "jest": lambda n: (
        "Test Suites: 1 failed, 1 total\n"
        f"Tests:       {n} failed, 4 passed, {n + 4} total"
    ),
    "cargo": lambda n: f"test result: FAILED. 4 passed; {n} failed; 0 ignored; 0 measured",
}
RUNNER_OUTPUT = Path(__file__).parent / "fixtures" / "claude_code_adapter" / "runner-output"


def sample(name: str) -> str:
    """Runner output as the runner printed it (Ticket 057): pytest 9.2 and
    unittest on Python 3.14, machine paths neutralized; jest in its
    documented format."""

    return (RUNNER_OUTPUT / f"{name}.txt").read_text(encoding="utf-8")


# Runs that failed only because a test module could not import a module.
IMPORT_ERRORS = ("pytest-imp", "unittest-imp", "jest-imp")
# Runs that show an import or load error but are real failures: a real test
# failure beside the import error, a broken module under test, or a test
# that prints import-error text.
COUNTED_FAILURES = (
    "pytest-mixed", "pytest-syntax", "pytest-name", "pytest-printed",
    "unittest-mixed", "unittest-syntax", "unittest-printed",
    "jest-mixed", "jest-broken", "jest-printed",
)
# A Python traceback ending in a missing module, with no runner's own line.
BARE_IMPORT_FAILURE = (
    "Traceback (most recent call last):\n"
    "  File \"/repo/scripts/check.py\", line 2, in <module>\n"
    "    import exporter\n"
    "ModuleNotFoundError: No module named 'exporter'"
)


class RepeatedFailureTests(AdapterTestCase):
    """The same check failing twice in a turn holds the next write until `diagnose`."""

    def failed_twice(self, command: str = CHECK, other: str | None = None) -> Session:
        s = self.routed()
        s.run(command, success=False)
        s.call("Edit", FIX)
        s.run(other or command, success=False)
        return s

    def test_the_same_check_failing_twice_holds_the_next_write(self) -> None:
        s = self.failed_twice()

        held = s.call("Edit", FIX)
        self.assertEqual(hold_line(held), "goated-hold: repeated-failure | justified-skip")
        self.assertIn(CHECK, reason(held))
        names = set(re.findall(r"`([a-z0-9]+(?:-[a-z0-9]+)*)`", reason(held)))
        self.assertEqual(names, {"diagnose"})
        self.assertEqual(decision(s.call("Edit", FIX)), "deny")
        self.assertEqual(decision(s.call("Bash", {"command": "echo x > src/notes.txt"})), "deny")

    def test_a_write_outside_the_project_is_held_too(self) -> None:
        # Unlike design and security, the gate is about the failing check, not the file.
        s = self.failed_twice()
        outside = dict(FIX, file_path=str(self.root / "scratch" / "export.py"))

        held = s.call("Edit", outside)
        self.assertEqual(hold_line(held), "goated-hold: repeated-failure | justified-skip")

    def test_rerunning_the_check_and_reading_stay_free(self) -> None:
        s = self.failed_twice()

        self.assertEqual(decision(s.run(CHECK, success=False)), "pass")
        self.assertEqual(decision(s.run(f"{CHECK} > test-output.txt", success=False)), "pass")
        self.assertEqual(decision(s.call("Bash", {"command": "cat src/export.py"})), "pass")

    def test_a_write_chained_with_the_check_is_held(self) -> None:
        for command in (
            f"sed -i 's/a/b/' src/export.py && {CHECK}",
            f"cat > src/export.py <<'EOF'\nprint('x')\nEOF\n{CHECK}",
            f"{CHECK} | tee test-output.txt",
        ):
            with self.subTest(command=command):
                self.session = self.fresh()
                s = self.failed_twice()
                self.assertEqual(decision(s.call("Bash", {"command": command})), "deny")

    def test_a_piped_check_fails_by_what_it_prints(self) -> None:
        for output in (
            "FAILED tests/test_export.py::test_round\n1 failed, 3 passed in 0.2s",
            "Ran 4 tests in 0.1s\n\nFAILED (failures=1)",
            "src/export.ts(3,1): error TS2304: Cannot find name 'x'.",
            "npm ERR! Test failed.",
            "Tests:       1 failed, 4 passed, 5 total",
        ):
            with self.subTest(output=output):
                self.session = self.fresh()
                s = self.routed()
                # The pipe's exit code is the filter's, so the run records as a success.
                s.run("pytest -q 2>&1 | tail -20", output=output)
                s.run("pytest -q 2>&1 | tail -40", output=output)
                held = s.call("Edit", FIX)
                self.assertEqual(hold_line(held), "goated-hold: repeated-failure | justified-skip")
                self.assertIn('"pytest -q"', reason(held))

    def test_a_piped_check_that_prints_no_failure_is_a_pass(self) -> None:
        s = self.routed()
        s.run("pytest -q 2>&1 | tail -20", output="1 failed, 3 passed in 0.2s")
        s.run("pytest -q 2>&1 | tail -20", output="4 passed in 0.2s")
        s.run("pytest -q 2>&1 | tail -20", output="1 failed, 3 passed in 0.2s")

        self.assertEqual(decision(s.call("Edit", FIX)), "pass")

    def test_powershell_checks_and_writes_count(self) -> None:
        s = self.routed()
        command = "uv run pytest -q | Select-Object -Last 20"
        s.run(command, tool="PowerShell", output="2 failed, 1 passed in 0.3s")
        s.run(command, tool="PowerShell", output="2 failed, 1 passed in 0.3s")

        write = {"command": "Set-Content -Path src/export.py -Value 'x'"}
        self.assertEqual(decision(s.call("PowerShell", write)), "deny")

    def test_a_held_check_is_not_a_failure(self) -> None:
        s = self.session
        s.prompt("Fix the exporter.")
        self.assertEqual(decision(s.run(f"echo x > out.txt; {CHECK}")), "deny")
        self.assertEqual(decision(s.run(f"echo x > out.txt; {CHECK}")), "deny")
        s.load(ROUTER)
        s.say("goated-route: direct")

        self.assertEqual(decision(s.call("Edit", FIX)), "pass")

    def test_a_refused_or_interrupted_check_is_not_a_failure(self) -> None:
        for text in (
            "The user doesn't want to proceed with this tool use. The tool use was rejected.",
            "Permission for this action was denied by the Claude Code auto mode classifier.",
            "Permission for this command was denied by a built-in Claude Code safety check.",
            "PreToolUse:Bash hook error: blocked by another hook",
            "[Request interrupted by user for tool use]",
        ):
            with self.subTest(text=text):
                self.session = self.fresh()
                s = self.routed()
                s.run(CHECK, success=False, output=text)
                s.run(CHECK, success=False, output=text)
                self.assertEqual(decision(s.call("Edit", FIX)), "pass")

    def test_a_pass_between_failures_resets_the_count(self) -> None:
        s = self.routed()
        s.run(CHECK, success=False)
        s.run(CHECK)
        s.run(CHECK, success=False)
        self.assertEqual(decision(s.call("Edit", FIX)), "pass", "fail, pass, fail")

        s.run(CHECK, success=False)
        self.assertEqual(decision(s.call("Edit", FIX)), "deny", "then a second failure in a row")

    def test_an_import_error_run_does_not_count(self) -> None:
        for name in IMPORT_ERRORS:
            with self.subTest(name):
                self.session = self.fresh()
                s = self.routed()
                s.run(CHECK, success=False, output=sample(name))
                s.run(CHECK, success=False)
                self.assertEqual(decision(s.call("Edit", FIX)), "pass")

    def test_a_run_with_a_real_failure_beside_the_load_error_counts(self) -> None:
        # Mixed runs, broken modules under test, and tests printing import text.
        for name in COUNTED_FAILURES:
            with self.subTest(name):
                self.session = self.fresh()
                s = self.routed()
                s.run(CHECK, success=False, output=sample(name))
                s.run(CHECK, success=False)
                held = s.call("Edit", FIX)
                self.assertEqual(hold_line(held), "goated-hold: repeated-failure | justified-skip")

    def test_a_bare_import_traceback_counts(self) -> None:
        # No runner says a test module failed to import, so it is a real failure.
        s = self.routed()
        s.run(CHECK, success=False, output=BARE_IMPORT_FAILURE)
        s.run(CHECK, success=False, output=BARE_IMPORT_FAILURE)
        held = s.call("Edit", FIX)
        self.assertEqual(hold_line(held), "goated-hold: repeated-failure | justified-skip")

    def test_an_import_error_run_does_not_reset_the_count(self) -> None:
        for name in IMPORT_ERRORS:
            with self.subTest(name):
                self.session = self.fresh()
                s = self.routed()
                s.run(CHECK, success=False)
                s.run(CHECK, success=False, output=sample(name))
                s.run(CHECK, success=False)
                held = s.call("Edit", FIX)
                self.assertEqual(hold_line(held), "goated-hold: repeated-failure | justified-skip")

    def test_a_piped_import_error_run_is_judged_the_same_way(self) -> None:
        piped = "pytest -q 2>&1 | tail -20"
        failure = "FAILED tests/test_export.py::test_round\n1 failed, 3 passed in 0.2s"
        s = self.routed()
        # The pipe's exit code is the filter's, so these runs record as successes.
        s.run(piped, output=sample("pytest-imp"))
        s.run(piped, output=failure)
        self.assertEqual(decision(s.call("Edit", FIX)), "pass", "import error, then a failure")

        s.run(piped, output=sample("pytest-imp"))
        s.run(piped, output=failure)
        held = s.call("Edit", FIX)
        self.assertEqual(hold_line(held), "goated-hold: repeated-failure | justified-skip",
                         "the import error between two failures does not reset the count")

    def test_a_truncated_import_error_run_does_not_reset_the_count(self) -> None:
        # `| head -8` keeps only the collection header and prints no failure sign.
        s = self.routed()
        s.run("pytest -q 2>&1 | head -8", output=sample("pytest-imp-head8"))
        s.run("pytest -q 2>&1 | head -8", output=sample("pytest-imp-head8"))
        self.assertEqual(decision(s.call("Edit", FIX)), "pass", "neither run is a failure")

        s.run("pytest -q", success=False)
        s.run("pytest -q 2>&1 | head -8", output=sample("pytest-imp-head8"))
        s.run("pytest -q", success=False)
        held = s.call("Edit", FIX)
        self.assertEqual(hold_line(held), "goated-hold: repeated-failure | justified-skip")

    def test_a_truncated_collection_error_is_a_failure(self) -> None:
        header = "\n".join(sample("pytest-syntax").splitlines()[:8])
        s = self.routed()
        s.run("pytest -q 2>&1 | head -8", output=header)
        s.run("pytest -q 2>&1 | head -8", output=header)
        held = s.call("Edit", FIX)
        self.assertEqual(hold_line(held), "goated-hold: repeated-failure | justified-skip")

    def test_another_check_passing_does_not_reset_the_count(self) -> None:
        s = self.routed()
        s.run(CHECK, success=False)
        s.run("uv run ruff check .")
        s.run(CHECK, success=False)

        self.assertEqual(decision(s.call("Edit", FIX)), "deny")

    def test_whitespace_alone_does_not_make_a_different_command(self) -> None:
        s = self.failed_twice("pytest -q", other="pytest   -q ")

        self.assertEqual(decision(s.call("Edit", FIX)), "deny")

    def test_near_misses_are_not_held(self) -> None:
        once = self.routed()
        once.run(CHECK, success=False)
        self.assertEqual(decision(once.call("Edit", FIX)), "pass", "one failure")

        for first, second in (
            (CHECK, "uv run ruff check ."),
            ("pytest tests/", "pytest tests/test_export.py -k rounding"),
            ("ls missing", "ls missing"),  # not a check
        ):
            with self.subTest(first=first, second=second):
                self.session = self.fresh()
                s = self.failed_twice(first, other=second)
                self.assertEqual(decision(s.call("Edit", FIX)), "pass")

    def test_passing_runs_are_not_failures(self) -> None:
        s = self.routed()
        s.run(CHECK, success=False)
        s.run(CHECK)
        self.assertEqual(decision(s.call("Edit", FIX)), "pass")

    def test_failures_in_an_earlier_turn_do_not_count(self) -> None:
        s = self.failed_twice()
        s.prompt("Carry on.")
        s.say("goated-route: continue")
        s.run(CHECK, success=False)

        self.assertEqual(decision(s.call("Edit", FIX)), "pass")

    def test_loading_diagnose_clears_it(self) -> None:
        s = self.failed_twice()
        self.assertEqual(decision(s.call("Edit", FIX)), "deny")

        s.load("diagnose")
        self.assertEqual(decision(s.call("Edit", FIX)), "pass")

    def test_a_skip_line_clears_it(self) -> None:
        s = self.failed_twice()
        self.assertEqual(decision(s.call("Edit", FIX)), "deny")

        s.say("goated-skip: diagnose: the failure is a known typo I just introduced")
        self.assertEqual(decision(s.call("Edit", FIX)), "pass")

    def test_the_first_run_after_a_test_edit_does_not_count(self) -> None:
        # Spec R1: in TDD the first run after writing a test is meant to fail.
        s = self.routed()
        s.call("Edit", TEST_EDIT)
        s.run(CHECK, success=False)
        s.call("Edit", FIX)
        s.run(CHECK, success=False)
        self.assertEqual(decision(s.call("Edit", FIX)), "pass", "red, then one counted failure")

        s.run(CHECK, success=False)
        held = s.call("Edit", FIX)
        self.assertEqual(hold_line(held), "goated-hold: repeated-failure | justified-skip",
                         "a second counted failure holds")

    def test_the_red_run_does_not_reset_the_count(self) -> None:
        s = self.routed()
        s.run(CHECK, success=False)
        s.call("Edit", TEST_EDIT)
        s.run(CHECK, success=False)
        self.assertEqual(decision(s.call("Edit", FIX)), "pass", "the red run is not counted")

        s.run(CHECK, success=False)
        held = s.call("Edit", FIX)
        self.assertEqual(hold_line(held), "goated-hold: repeated-failure | justified-skip",
                         "the failure before the red run still counts")

    def test_a_shell_write_to_a_test_file_excuses_the_next_run(self) -> None:
        s = self.routed()
        s.run(CHECK, success=False)
        s.run("echo 'def test_x(): assert 0' >> tests/test_export.py")
        s.run(CHECK, success=False)

        self.assertEqual(decision(s.call("Edit", FIX)), "pass")

    def test_only_the_first_run_after_a_test_edit_is_excused(self) -> None:
        # Near miss: the excuse is used once, by the first run after the test edit.
        s = self.routed()
        s.call("Edit", TEST_EDIT)
        s.run(CHECK, success=False)
        s.run(CHECK, success=False)
        s.run(CHECK, success=False)
        held = s.call("Edit", FIX)
        self.assertEqual(hold_line(held), "goated-hold: repeated-failure | justified-skip")

    def test_a_held_or_failed_test_edit_excuses_nothing(self) -> None:
        for how in ("failed", "held"):
            with self.subTest(how=how):
                self.session = s = self.fresh()
                s.prompt("Fix the exporter.")
                if how == "failed":
                    s.load(ROUTER)
                    s.say("goated-route: direct")
                    s.call("Edit", TEST_EDIT, result="String to replace not found in file.",
                           failed=True)
                else:
                    # Held by the route-line gate, so the edit never ran.
                    self.assertEqual(decision(s.call("Edit", TEST_EDIT)), "deny")
                    s.load(ROUTER)
                    s.say("goated-route: direct")
                s.run(CHECK, success=False)
                s.run(CHECK, success=False)
                held = s.call("Edit", FIX)
                self.assertEqual(hold_line(held),
                                 "goated-hold: repeated-failure | justified-skip")

    def test_runs_with_fewer_failures_do_not_count(self) -> None:
        # Spec R1: 5, 3, 1 failures is progress; 3 and 3 is not.
        for runner, summary in RUNNER_SUMMARIES.items():
            with self.subTest(runner=runner):
                self.session = s = self.fresh()
                s.prompt("Fix the exporter.")
                s.load(ROUTER)
                s.say("goated-route: direct")
                for failures in (5, 3, 1):
                    s.run(CHECK, success=False, output=summary(failures))
                    self.assertEqual(decision(s.call("Edit", FIX)), "pass", failures)

                s.run(CHECK, success=False, output=summary(1))
                held = s.call("Edit", FIX)
                self.assertEqual(hold_line(held),
                                 "goated-hold: repeated-failure | justified-skip", "1 then 1")

    def test_runs_with_the_same_failures_hold(self) -> None:
        for runner, summary in RUNNER_SUMMARIES.items():
            with self.subTest(runner=runner):
                self.session = s = self.fresh()
                s.prompt("Fix the exporter.")
                s.load(ROUTER)
                s.say("goated-route: direct")
                s.run(CHECK, success=False, output=summary(3))
                s.run(CHECK, success=False, output=summary(3))
                held = s.call("Edit", FIX)
                self.assertEqual(hold_line(held),
                                 "goated-hold: repeated-failure | justified-skip")

    def test_a_run_whose_count_cannot_be_read_counts(self) -> None:
        for first, second in (
            ("Exit code 1\nfailed", "Exit code 1\nfailed"),
            (RUNNER_SUMMARIES["pytest"](5), "Exit code 1\nfailed"),
            ("Exit code 1\nfailed", RUNNER_SUMMARIES["pytest"](1)),
            # Two runners' summaries in one run: which count is the check's is unknown.
            (RUNNER_SUMMARIES["pytest"](5),
             RUNNER_SUMMARIES["pytest"](1) + "\n" + RUNNER_SUMMARIES["jest"](1)),
        ):
            with self.subTest(first=first, second=second):
                self.session = s = self.fresh()
                s.prompt("Fix the exporter.")
                s.load(ROUTER)
                s.say("goated-route: direct")
                s.run(CHECK, success=False, output=first)
                s.run(CHECK, success=False, output=second)
                held = s.call("Edit", FIX)
                self.assertEqual(hold_line(held),
                                 "goated-hold: repeated-failure | justified-skip")

    def test_a_cd_to_the_session_folder_is_the_same_check(self) -> None:
        # Spec R2: `cd <folder> && pytest -q` is `pytest -q` run from that folder.
        for spell in (str, lambda p: p.as_posix(), lambda p: p.as_posix() + "/"):
            with self.subTest(spell=spell(Path("x/y"))):
                self.session = s = self.fresh()
                folder = spell(s.cwd)
                s.prompt("Fix the exporter.")
                s.load(ROUTER)
                s.say("goated-route: direct")
                s.run(f'cd "{folder}" && pytest -q', success=False)
                s.run("pytest -q", success=False)
                held = s.call("Edit", FIX)
                self.assertEqual(hold_line(held),
                                 "goated-hold: repeated-failure | justified-skip")
                self.assertIn('the check "pytest -q" has failed', reason(held))

    def test_the_hold_shows_the_check_without_its_cd(self) -> None:
        folder = "build/" + "a-very-long-folder-name/" * 4
        for cd in (f'cd "{folder}" && ', f"cd {folder}; ", f"cd '{folder}' &&"):
            with self.subTest(cd=cd):
                self.session = s = self.fresh()
                s.prompt("Fix the exporter.")
                s.load(ROUTER)
                s.say("goated-route: direct")
                s.run(f"{cd}pytest -q", success=False)
                s.run(f'cd "{folder}" && pytest -q', success=False)
                held = s.call("Edit", FIX)
                self.assertEqual(hold_line(held),
                                 "goated-hold: repeated-failure | justified-skip")
                self.assertIn('the check "pytest -q" has failed', reason(held))

    def test_checks_run_from_different_folders_are_different_checks(self) -> None:
        # Near miss: the cd's folder stays part of the check, and so do its counts.
        s = self.routed()
        s.run("cd pkg_a && pytest -q", success=False, output="5 failed in 0.1s")
        s.run("cd pkg_b && pytest -q", success=False, output="1 failed in 0.1s")
        self.assertEqual(decision(s.call("Edit", FIX)), "pass", "a, then b")
        s.run("pytest -q", success=False)
        self.assertEqual(decision(s.call("Edit", FIX)), "pass", "a, b, then the session folder")

        s.run("cd pkg_a && pytest -q", success=False, output="5 failed in 0.1s")
        held = s.call("Edit", FIX)
        self.assertEqual(hold_line(held), "goated-hold: repeated-failure | justified-skip",
                         "a failed twice with 5 failures, b's 1 between them aside")

    def test_a_crash_after_failures_is_not_progress(self) -> None:
        # A run that could not load its tests reports fewer failures, but shows no progress.
        for before, crash in (
            ("Tests:       3 failed, 2 passed, 5 total", sample("jest-broken")),
            ("Tests:       3 failed, 2 passed, 5 total",
             "Test Suites: 1 failed, 1 total\nTests:       0 total"),
            ("5 failed, 2 passed in 0.31s", sample("pytest-syntax")),
            ("5 failed, 2 passed in 0.31s",
             "!!! Interrupted: 1 error during collection !!!\n1 error in 0.05s"),
            ("Ran 9 tests in 0.004s\n\nFAILED (failures=3)", sample("unittest-syntax")),
        ):
            with self.subTest(crash=crash[-40:]):
                self.session = s = self.fresh()
                s.prompt("Fix the exporter.")
                s.load(ROUTER)
                s.say("goated-route: direct")
                s.run(CHECK, success=False, output=before)
                s.run(CHECK, success=False, output=crash)
                held = s.call("Edit", FIX)
                self.assertEqual(hold_line(held),
                                 "goated-hold: repeated-failure | justified-skip")

    def test_only_a_pytest_summary_line_is_read_as_one(self) -> None:
        # Near miss: "3 files in 2 dirs" is not a second summary that makes the count unreadable.
        s = self.routed()
        s.run(CHECK, success=False, output="3 failed, 2 passed in 0.31s")
        s.run(CHECK, success=False, output="3 files in 2 dirs\n1 failed, 4 passed in 0.31s")

        self.assertEqual(decision(s.call("Edit", FIX)), "pass")

    def test_a_cd_within_the_command_still_makes_another_check(self) -> None:
        # Near miss: only a leading cd joined by && or ; is dropped.
        for first, second in (
            ("pytest -q && cd docs", "pytest -q"),
            ("cd tests || pytest -q", "pytest -q"),
            ("cd tests && pytest -q", "cd tests && pytest -q -k export"),
        ):
            with self.subTest(first=first, second=second):
                self.session = s = self.fresh()
                s.prompt("Fix the exporter.")
                s.load(ROUTER)
                s.say("goated-route: direct")
                s.run(first, success=False)
                s.run(second, success=False)
                self.assertEqual(decision(s.call("Edit", FIX)), "pass")

    def test_a_typed_skip_diagnose_override_clears_it(self) -> None:
        s = self.session
        s.prompt("Fix the exporter; skip diagnose this time.")
        s.load(ROUTER)
        s.say("goated-route: direct")
        s.run(CHECK, success=False)
        s.run(CHECK, success=False)

        self.assertEqual(decision(s.call("Edit", FIX)), "pass")


class SubagentActionTests(AdapterTestCase):
    """Inside a subagent, action gates apply and routing gates do not (spec R9)."""

    def setUp(self) -> None:
        super().setUp()
        self.session.prompt("Delegate the export work.")
        self.agent = self.session.subagent("a7")

    def sub_call(self, tool: str, tool_input: dict) -> dict:
        return self.agent.call(tool, tool_input, agent_id="a7", agent_type="general-purpose")

    def test_routing_gates_do_not_apply_but_action_gates_do(self) -> None:
        a = self.agent
        a.prompt("Implement the export. Skip routing and skip commit-message.", hook=False)

        self.assertEqual(decision(self.sub_call("Edit", {"file_path": "notes.md"})), "pass")
        self.assertEqual(
            hold_line(self.sub_call("Bash", commit("Add export"))),
            "goated-hold: commit | strict",
        )
        self.assertEqual(
            hold_line(self.sub_call("Write", write("src/export.py"))),
            "goated-hold: design | justified-skip",
        )

    def test_a_subagent_load_clears_its_own_hold(self) -> None:
        a = self.agent
        a.prompt("Implement the export.", hook=False)
        a.load("commit-message")
        a._tool_result(a._tool_use("Bash", {"command": "git diff --cached"}), "ok")

        self.assertEqual(decision(self.sub_call("Bash", commit("Add export"))), "pass")

    def test_a_check_failing_twice_in_a_subagent_holds_its_write(self) -> None:
        a = self.agent
        a.prompt("Implement the export.", hook=False)
        for _ in range(2):
            a._tool_result(a._tool_use("Bash", {"command": "pytest -q"}), "Exit code 1\n1 failed",
                           is_error=True)

        held = self.sub_call("Edit", {"file_path": "src/export.py", "old_string": "a",
                                      "new_string": "b"})
        self.assertEqual(hold_line(held), "goated-hold: repeated-failure | justified-skip")

    def test_a_parent_load_does_not_clear_a_subagent_hold(self) -> None:
        self.session.load("commit-message")
        self.agent.prompt("Implement the export.", hook=False)

        self.assertEqual(decision(self.sub_call("Bash", commit("Add export"))), "deny")

    def test_a_missing_subagent_transcript_fails_open(self) -> None:
        output = parse(self.session.hook(
            "PreToolUse", tool_name="Bash", tool_input=commit("Add export"),
            tool_use_id="toolu_x", agent_id="unknown9", agent_type="general-purpose",
        ))
        self.assertEqual(decision(output), "pass")
        self.assertIn("allowed without checks", output.get("systemMessage", ""))


def stop(s: Session, final: str = "") -> dict:
    return parse(s.hook("Stop", stop_hook_active=False, last_assistant_message=final))


def closeout_line(output: dict) -> str:
    return str(output.get("reason", "")).split("\n", 1)[0] if output.get("decision") else ""


class CloseoutTests(AdapterTestCase):
    def changed(self, path: str = "src/export.py") -> Session:
        s = self.routed()
        s.say("goated-skip: software-design-principles: one mechanical constant change")
        self.assertEqual(decision(s.call("Write", write(path))), "pass")
        return s

    def test_a_turn_without_code_changes_ends_freely(self) -> None:
        s = self.routed()
        s.call("Write", write("docs/guide.md"))
        s.run("cat src/export.py")

        self.assertEqual(stop(s), {})

    def test_a_code_change_needs_fresh_proof_and_a_retry_never_passes(self) -> None:
        s = self.changed()

        for _ in range(2):
            held = stop(s)
            self.assertEqual(closeout_line(held), "goated-hold: closeout | justified-skip")
            self.assertIn("Proof", held["reason"])

        s.run("uv run python -m unittest discover -s tests")
        held = stop(s)
        self.assertNotIn("Proof", held["reason"])
        self.assertIn("doc-sync", held["reason"])

        s.load("doc-sync")
        s.run("git diff")
        self.assertEqual(stop(s), {})

    def test_check_commands_count_as_proof_and_reads_do_not(self) -> None:
        for command, is_proof in (
            ("uv run python scripts/validate_skills.py", True),
            ("npm run build", True),
            ("cargo test", True),
            ("cat tests/test_export.py", False),
            ("git diff --check", False),
        ):
            with self.subTest(command=command):
                s = self.fresh()
                s.prompt("Bump it.")
                s.load(ROUTER)
                s.say("goated-route: direct")
                s.load("doc-sync")
                s.run("sed -i 's/1/2/' src/export.py")
                s.run(command)
                held = stop(s)
                self.assertEqual("Proof" not in held.get("reason", ""), is_proof)

    def test_a_check_later_in_the_same_command_proves_its_write(self) -> None:
        for command, is_proof in (
            ("cp a.py src/a.py && python -m pytest", True),
            ("cp a.py src/a.py; npm test", True),
            ("cp a.py src/a.py\npytest -q", True),
            ("cp a.py src/a.py && pytest -q > out.txt", True),
            ("cp a.py src/a.py && python -m pytest -p no:cacheprovider -c setup.cfg", True),
            ("cp a.py src/a.py && pytest -q && cp b.py src/b.py", False),
            ("python -m pytest && cp a.py src/a.py", False),
            ("pytest -q && cp a.py src/a.py && git status", False),
            ("cp a.py src/a.py || pytest -q", False),
            ("cp a.py src/a.py & pytest -q", False),
            ("cp a.py src/a.py | pytest -q", False),
            ("cp a.py src/a.py && python -c \"print('tests pass')\"", False),
            ("cp a.py src/a.py && node -e \"console.log('check')\"", False),
            # A .NET write the command cannot place, after the check.
            ("cp a.py src/a.py; pytest; [System.IO.File]::WriteAllText('src/b.py','x')", False),
            # A check in another branch or body, or after the command may have stopped.
            ("if [ -f x ]; then cp a.py src/a.py; else pytest; fi", False),
            ("if [ -f x ]; then cp a.py src/a.py; fi; pytest", False),
            ("f() { cp a.py src/a.py; }; pytest", False),
            ("cp a.py src/a.py && exit 0; pytest", False),
            ("! cp a.py src/a.py && pytest", False),
            ("if [ -f x ]; then echo; fi; cp a.py src/a.py && pytest", True),
            # A backgrounded check.
            ("cp a.py src/a.py && pytest -q &", False),
            ("cp a.py src/a.py && pytest & wait", False),
            ("cp a.py src/a.py && pytest || true", True),
            # A non-code write after the check, such as its log.
            ("cp a.py src/a.py && pytest 2>&1 | tee log.txt", True),
            ("cp a.py src/a.py && pytest && echo x > notes.md", True),
            ("cp a.py src/a.py && pytest && echo x > src/b.py", False),
            # Inline code, by combined or valued options.
            ("cp a.py src/a.py && python -Bc 'import tests'", False),
            ("cp a.py src/a.py && python -W ignore -c 'print(1)' -m pytest", False),
            ("cp a.py src/a.py && python -W ignore -m pytest", True),
            ("cp a.py src/a.py && node -pe '\"tests\"'", False),
            ("cp a.py src/a.py && perl -le 'print \"tests\"'", False),
            ("cp a.py src/a.py && perl -I tests -e 'print 1'", False),
            ("cp a.py src/a.py && ruby -ne 'puts \"check\"'", False),
            # A shell's inline string is read as a command line.
            ("cp a.py src/a.py && bash -c 'npm test'", True),
            ("cp a.py src/a.py && bash -lc 'echo tests ok'", False),
            ("cp a.py src/a.py && sh -c 'echo check'", False),
            ("cp a.py src/a.py && pwsh -NoProfile -Command npm test", True),
            ("cp a.py src/a.py && pwsh -c 'Write-Output tests'", False),
        ):
            with self.subTest(command=command):
                s = self.routed()
                s.load("doc-sync")
                s.run(command)
                s.run("git diff")
                held = stop(s)
                self.assertEqual("Proof" not in held.get("reason", ""), is_proof)

    def test_a_dotnet_write_after_a_powershell_check_is_not_proved(self) -> None:
        for command, is_proof in (
            ("Copy-Item a.py src/a.py; Invoke-Pester; [IO.File]::Copy('a','src/b.py')", False),
            ("Copy-Item a.py src/a.py; Invoke-Pester", True),
        ):
            with self.subTest(command=command):
                s = self.routed()
                s.load("doc-sync")
                s.run(command, tool="PowerShell")
                s.run("git diff")
                held = stop(s)
                self.assertEqual("Proof" not in held.get("reason", ""), is_proof)

    def test_dotnet_write_text_held_as_data_is_not_a_change(self) -> None:
        """Ticket 058's scratch-file closeout, reproduced from the maintainer's
        session: probe commands for the adapter held `.NET` write text as data,
        in a heredoc written to a scratch file and in a `python -c` string. Each
        read as an unnamed write, which counts as project code wherever it runs,
        so the turn got Proof and Docs items. Text only a text tool is given is
        data; text an interpreter or `git` is given still counts, since those can
        start PowerShell, and so does any text in a command that runs PowerShell."""

        native = str(self.root / "scratch")
        scratch = (self.root / "scratch").as_posix()
        if os.name == "nt":
            scratch = git_bash(scratch)
        dotnet = "[System.IO.File]::WriteAllText('src/b.py','x')"
        for tool, command, changes in (
            ("Bash", f"cd {scratch}/merge27/adapters/claude-code && uv run --project ../.. "
                     f"python -c \"\ncases = {{\n \\\"cp a.py src/a.py; pytest; {dotnet}\\\": "
                     f"False,\n}}\nprint(cases)\n\"", True),
            ("Bash", f"cat > {scratch}/probe.py <<'EOF'\ncases = [\"{dotnet}\"]\nEOF", False),
            # A quoted delimiter: the shell expands nothing in the body.
            ("Bash", f"cat > {scratch}/probe.py <<'EOF'\ncases = [\"x=$(pwd); {dotnet}\"]\nEOF",
             False),
            ("Bash", f"cat > {scratch}/probe.py <<EOF\ncases = [\"x=$(pwd); {dotnet}\"]\nEOF",
             True),
            ("Bash", f"python3 -c \"text = '{dotnet}'\"", True),
            ("Bash", f"echo \"{dotnet}\" | grep -c IO", False),
            ("Bash", f"echo \"{dotnet}\" 2>&1 | tail -20 | sort | head -3", False),
            # In the PowerShell tool, .NET text counts wherever it is (058 review).
            ("PowerShell", f"Write-Output \"{dotnet}\" | Select-Object -First 1", True),
            ("Bash", f"git log -S \"{dotnet}\"", True),
            ("PowerShell", f"Write-Output \"{dotnet}\"", True),
            ("PowerShell", f"$p = '{native}\\w12.ps1'; Write-Output \"{dotnet}\" > $p; & $p", True),
            ("PowerShell", f"Write-Output \"{dotnet}\" > {native}\\w13.txt; "
                           f"Get-Content {native}\\w13.txt | Invoke-Expression", True),
            ("PowerShell", f"Write-Output \"{dotnet}\" > {native}\\w14.txt; "
                           f"Invoke-Expression (Get-Content -Raw {native}\\w14.txt)", True),
            # Bash near misses: the same text to a non-script file stays data,
            # unless the command names `iex`, `Invoke-Expression`, or PowerShell.
            ("Bash", f"echo \"{dotnet}\" > {scratch}/w13.txt; cat {scratch}/w13.txt", False),
            ("Bash", f"echo \"{dotnet}\" > {scratch}/w14.txt && wc -l {scratch}/w14.txt", False),
            ("Bash", f"echo \"{dotnet}\" > {scratch}/w13.txt; "
                     f"pwsh -c 'Get-Content {scratch}/w13.txt | iex'", True),
            ("Bash", f"echo \"{dotnet}\" > {scratch}/w14.txt; "
                     f"cat {scratch}/w14.txt | Invoke-Expression", True),
            ("Bash", f"echo \"{dotnet}\" > {scratch}/w14.txt; cat {scratch}/w14.txt | iex", True),
            # Near misses: PowerShell runs each of these.
            ("Bash", f"cp a.py b.py; {dotnet}", True),
            ("Bash", f"pwsh -NoProfile -Command \"{dotnet}\"", True),
            ("Bash", f"bash -c \"pwsh -c '{dotnet}'\"", True),
            ("Bash", f"echo \"$(pwsh -c '{dotnet}')\"", True),
            ("Bash", f"cat <<EOF\n`pwsh -c \"{dotnet}\"`\nEOF", True),
            # Data piped on into a program that may run it.
            ("Bash", f"cat <<'EOF' | pwsh -NoProfile -Command -\n{dotnet}\nEOF", True),
            ("Bash", f"echo \"{dotnet}\" | grep IO | pwsh -Command -", True),
            ("PowerShell", f"Write-Output \"{dotnet}\" | Invoke-Expression", True),
            ("PowerShell", dotnet, True),
            ("PowerShell", f"$null = {dotnet}", True),
            ("PowerShell", f"Write-Output ({dotnet})", True),
            ("PowerShell", f"Write-Output \"$({dotnet})\"", True),
            ("PowerShell", f"if ($true) {{ {dotnet} }}", True),
            # Data a later command runs as PowerShell, or a launcher may hand on.
            ("Bash", f"cat > {scratch}/w.ps1 <<'EOF'\n{dotnet}\nEOF\n"
                     f"pwsh -NoProfile -File {scratch}/w.ps1", True),
            ("Bash", f"echo \"{dotnet}\" > {scratch}/w.ps1 && pwsh -File {scratch}/w.ps1", True),
            ("Bash", f"echo \"{dotnet}\" | tee {scratch}/w.ps1; pwsh {scratch}/w.ps1", True),
            ("Bash", f"echo \"{dotnet}\" > {scratch}/w.ps1 && powershell.exe {scratch}/w.ps1",
             True),
            ("Bash", "python -c \"import subprocess; subprocess.run(['pwsh', '-c', "
                     f"\\\"{dotnet}\\\"])\"", True),
            ("Bash", "git -c alias.w='!pwsh -c \"[System.IO.File]::Delete(1)\"' w", True),
            ("Bash", f"uv run node -e \"x = '{dotnet}'\"", True),
            # A PowerShell script file the text is written into, wherever it is,
            # counts: a later call may run it (ticket 058 review, N2).
            ("Bash", f"cat > {scratch}/w2.ps1 <<'EOF'\n{dotnet}\nEOF", True),
            ("Bash", f"echo \"{dotnet}\" | tee {scratch}/w.psm1", True),
            ("PowerShell", f"Write-Output \"{dotnet}\" > {native}\\w5.ps1", True),
            ("PowerShell", f"Write-Output \"{dotnet}\" >> {native}\\W5.PSD1", True),
            # The PowerShell tool runs a script with `&` or `.` (N1).
            ("PowerShell", f"Write-Output \"{dotnet}\" > {native}\\w3.ps1; & {native}\\w3.ps1",
             True),
            ("PowerShell", f"Write-Output \"{dotnet}\"; . {native}\\run.ps1", True),
            ("PowerShell", f"Write-Output \"{dotnet}\"; & '{native}\\run.ps1'", True),
            # Near misses: the text written to a file that is not a script.
            ("Bash", f"cat > {scratch}/w.ps1.txt <<'EOF'\n{dotnet}\nEOF", False),
            ("PowerShell", f"Write-Output \"{dotnet}\" > {native}\\notes.txt", True),
            ("Bash", f"echo \"{dotnet}\" > {scratch}/notes.txt", False),
            ("Bash", f"echo \"{dotnet}\" | tee {scratch}/log.txt", False),
        ):
            with self.subTest(command=command):
                s = self.fresh()
                s.prompt("Probe it.")
                s.load(ROUTER)
                s.say("goated-route: direct")
                s.say("goated-skip: commit-message: probe commit in a scratch clone")
                s.run(command, tool=tool)
                reason_text = stop(s).get("reason", "")
                self.assertEqual("- Proof:" in reason_text, changes)
                self.assertEqual("- Docs:" in reason_text, changes)

    def test_a_failing_same_command_check_needs_a_handoff(self) -> None:
        s = self.changed()
        s.load("doc-sync")
        s.run("cp a.py src/a.py && pytest -q", success=False)
        s.run("git diff")

        held = stop(s)
        self.assertNotIn("Proof", held["reason"])
        self.assertIn("handoff", held["reason"])

    def test_inline_interpreter_code_is_not_a_check(self) -> None:
        s = self.changed()
        s.load("doc-sync")
        s.run("python -c \"import tests; print('check passed')\"")
        s.run("git diff")

        self.assertIn("Proof", stop(s)["reason"])

    def test_loading_verification_alone_is_not_proof(self) -> None:
        s = self.changed()
        s.load("doc-sync")
        s.load("verification-before-completion")

        self.assertIn("Proof", stop(s)["reason"])

    def test_proof_before_the_last_change_is_not_fresh(self) -> None:
        s = self.changed()
        s.run("pytest -q")
        s.call("Edit", {"file_path": "src/export.py", "old_string": "a", "new_string": "b"})
        s.load("doc-sync")

        self.assertIn("Proof", stop(s)["reason"])

    def test_skip_lines_pass_every_closeout_item(self) -> None:
        s = self.changed()
        final = (
            "Done.\n\ngoated-skip: verification-before-completion: no test harness exists here\n"
            "goated-skip: doc-sync: internal constant with no documented behavior"
        )

        self.assertEqual(stop(s, final), {})

    def test_a_skip_line_already_in_the_transcript_counts(self) -> None:
        s = self.changed()
        s.run("pytest -q")
        s.say("goated-skip: doc-sync: internal constant with no documented behavior")

        self.assertEqual(stop(s), {})

    def test_a_failing_last_check_needs_a_handoff(self) -> None:
        s = self.changed()
        s.run("pytest -q", success=False)
        s.load("doc-sync")
        s.run("git diff")

        held = stop(s)
        self.assertIn("handoff", held["reason"])
        s.load("handoff")
        self.assertEqual(stop(s), {})

    def test_test_only_changes_do_not_need_doc_sync(self) -> None:
        s = self.changed("tests/test_export.py")
        s.run("pytest -q")

        self.assertEqual(stop(s), {})

    def test_a_test_change_written_beside_a_doc_does_not_need_doc_sync(self) -> None:
        s = self.routed()
        s.run("sed -i 's/1/2/' tests/test_export.py notes.md")
        s.run("pytest -q")

        self.assertEqual(stop(s), {})

    def test_a_held_edit_is_not_a_change(self) -> None:
        s = self.routed()
        self.assertEqual(decision(s.call("Write", write("src/export.py"))), "deny")

        self.assertEqual(stop(s), {})

    def test_a_shell_write_to_code_is_a_change(self) -> None:
        s = self.routed()
        s.run("sed -i 's/1/2/' src/export.py")

        self.assertIn("Proof", stop(s)["reason"])

    def test_applied_design_needs_the_red_flags_read_after_the_last_change(self) -> None:
        s = self.routed()
        s.load("software-design-principles")
        red_flags = "/opt/goated/skills/software-design-principles/references/red-flags.md"
        s.read(red_flags)
        s.call("Edit", edit("src/export.py", PLAIN))
        s.run("pytest -q")
        s.load("doc-sync")

        held = stop(s)
        self.assertIn("red-flags.md", held["reason"])
        s.read(red_flags)
        s.run("git diff")
        self.assertEqual(stop(s), {})

    def test_a_user_typed_skill_skip_stands_its_item_down(self) -> None:
        s = self.session
        s.prompt("Bump the constant, and skip doc-sync.")
        s.load(ROUTER)
        s.say("goated-route: direct")
        s.say("goated-skip: software-design-principles: one mechanical constant change")
        s.call("Write", write("src/export.py"))
        s.run("pytest -q")

        self.assertEqual(stop(s), {})

    def test_the_closeout_does_not_carry_into_the_next_turn(self) -> None:
        s = self.changed()
        self.assertTrue(stop(s))

        s.prompt("Thanks. What does the exporter do?")
        self.assertEqual(stop(s), {})


SECURITY_SKIP = "goated-skip: code-security-review: a local env value, no trust boundary"


class SetupCloseoutTests(AdapterTestCase):
    """The closeout's Setup item: a package install or an env or settings file
    write needs `setup-scribe`, or a skip line naming it."""

    def installed(self, command: str = "uv add httpx") -> Session:
        s = self.routed()
        self.assertEqual(decision(s.run(command)), "pass")
        return s

    def test_a_named_package_install_needs_setup_scribe(self) -> None:
        for tool, command in (
            ("Bash", "uv add httpx"),
            ("Bash", "npm install --save-dev typescript"),
            ("Bash", "npm i -g pnpm"),
            ("Bash", "pnpm add zod"),
            ("Bash", "yarn add react"),
            ("Bash", "pip install requests==2.32.0"),
            ("Bash", "python -m pip install --upgrade ruff"),
            ("Bash", "uv pip install rich"),
            ("Bash", "uv tool install ruff"),
            ("Bash", "cargo add serde"),
            ("Bash", "go get example.com/mod@v1.2.0"),
            ("Bash", "brew install jq"),
            ("Bash", "sudo apt-get install -y ripgrep"),
            ("Bash", "cd web && npm install lodash"),
            ("Bash", "npm i -f lodash"),
            ("Bash", "cargo install -f ripgrep"),
            ("Bash", "brew install -f jq"),
            ("Bash", "npm install --workspace=app lodash"),
            ("Bash", "pnpm add --filter web zod"),
            ("Bash", "yarn global add pnpm"),
            ("Bash", "pip install -e git+https://example.com/org/pkg.git#egg=pkg"),
            ("Bash", "cargo install --git https://example.com/org/tool.git"),
            ("Bash", "npm install foo || true"),
            ("PowerShell", "winget install --id Git.Git -e"),
            ("PowerShell", "choco install nodejs -y"),
        ):
            with self.subTest(command=command):
                s = self.fresh()
                s.prompt("Add the dependency.")
                s.load(ROUTER)
                s.say("goated-route: direct")
                s.call(tool, {"command": command})
                held = stop(s)
                self.assertEqual(closeout_line(held), "goated-hold: closeout | justified-skip")
                self.assertIn("- Setup:", held["reason"])
                self.assertIn("`setup-scribe`", held["reason"])

    def test_writing_an_env_or_settings_file_needs_setup_scribe(self) -> None:
        for tool, target in (
            ("Write", ".env.local"),
            ("Write", ".env"),
            ("Edit", "web/.env.example"),
            ("Write", ".claude/settings.local.json"),
            ("Write", ".vscode/settings.json"),
            ("Bash", "echo API_URL=http://localhost >> .env.local"),
            # Unplaced: `cd sub` may go anywhere through CDPATH, so it counts as inside.
            ("Bash", "cd sub && echo '{}' > .claude/settings.json"),
        ):
            with self.subTest(target=target):
                s = self.fresh()
                s.prompt("Configure it.")
                s.load(ROUTER)
                s.say("goated-route: direct")
                s.say(SECURITY_SKIP)
                if tool == "Bash":
                    s.run(target)
                else:
                    field = {"Write": "content", "Edit": "new_string"}[tool]
                    s.call(tool, {"file_path": target, field: "X=1", "old_string": "X=0"})
                held = stop(s)
                self.assertEqual(closeout_line(held), "goated-hold: closeout | justified-skip")
                self.assertIn("- Setup:", held["reason"])

    def test_comments_alone_in_an_example_env_file_do_not_count(self) -> None:
        """Round 7, R9: adding, removing or editing comment lines in
        `.env.example`, `.env.sample` or `.env.template` records no setup.
        Near misses: a setting line there, a whole-file write, and a comment
        in `.env` itself."""

        for path, old, new, counts in (
            (".env.example", "# The API's address.", "# The API's address, with no slash.", False),
            ("web/.env.sample", "API_URL=", "# Where the API runs.\nAPI_URL=", False),
            (".env.template", "  # Old note\nKEY=", "KEY=", False),
            (".ENV.EXAMPLE", "KEY=1\n# a", "KEY=1\n\n# b", False),
            (".env.example", "# The API's address.", "# The API's address.\nAPI_URL=", True),
            (".env.example", "KEY=1", "KEY=2", True),
            (".env.example", "# KEY=1", "KEY=1", True),
            (".env", "# The API's address.", "# The API's address, with no slash.", True),
            (".env.local", "# a", "# b", True),
            (".env.example", None, "# The API's address.", True),
        ):
            with self.subTest(path=path, new=new):
                s = self.fresh()
                s.prompt("Document the setting.")
                s.load(ROUTER)
                s.say("goated-route: direct")
                s.say(SECURITY_SKIP)
                if old is None:
                    s.call("Write", {"file_path": path, "content": new})
                else:
                    s.call("Edit", {"file_path": path, "old_string": old, "new_string": new})
                self.assertEqual("- Setup:" in stop(s).get("reason", ""), counts)

    def test_a_settings_file_outside_the_project_does_not_count(self) -> None:
        """Ticket 058 (spec R9): a scratch live-check folder's settings are not
        the project's setup. The near miss, the same file in the project, counts."""

        scratch = self.root / "scratch" / ".claude" / "settings.json"
        for tool, target, counts in (
            ("Write", str(scratch), False),
            ("Write", scratch.as_posix(), False),
            ("Write", "..\\shared\\.claude\\settings.json", False),
            ("Bash", f"echo '{{}}' > '{scratch}'", False),
            ("Bash", f"cd '{scratch.parent}' && echo '{{}}' > settings.json", False),
            ("Write", ".claude/settings.json", True),
            ("Write", "{inside}/.claude/settings.json", True),
            ("Bash", "cd ./.claude && echo '{}' > settings.json", True),
        ):
            with self.subTest(target=target):
                s = self.fresh()
                s.prompt("Configure it.")
                s.load(ROUTER)
                s.say("goated-route: direct")
                s.say(SECURITY_SKIP)
                target = target.replace("{inside}", str(s.project))
                if tool == "Bash":
                    s.run(target)
                else:
                    s.call(tool, {"file_path": target, "content": "{}"})
                reason_text = stop(s).get("reason", "")
                if counts:
                    self.assertIn("- Setup:", reason_text)
                else:
                    self.assertNotIn("Setup", reason_text)

    def test_near_misses_end_freely(self) -> None:
        for tool, command in (
            ("Bash", "npm install"),
            ("Bash", "npm ci"),
            ("Bash", "pnpm install --frozen-lockfile"),
            ("Bash", "pip install -r requirements.txt"),
            ("Bash", "pip install -e ."),
            ("Bash", "pip install -e ../lib"),
            ("Bash", "pnpm install --filter web"),
            ("Bash", "pnpm install -F web"),
            ("Bash", "npm install --workspace app"),
            ("Bash", "npm install -w app"),
            ("Bash", "npm install --prefix web"),
            ("Bash", "uv pip install -r requirements.txt --python 3.12"),
            ("Bash", "uv pip install -p 3.12 -r requirements.txt"),
            ("Bash", "pip install --index-url https://example.com/simple -r requirements.txt"),
            ("Bash", "pip install --target vendor -r requirements.txt"),
            ("Bash", "conda install --file requirements.txt"),
            ("Bash", "npm install --registry https://example.com/npm"),
            ("Bash", "uv sync"),
            ("Bash", "cargo build"),
            ("Bash", "npm run build"),
            ("Bash", "cat .env.local"),
            ("Bash", "grep -n install README.md"),
            ("Bash", "echo 'pip install x' > notes.md"),
            ("PowerShell", "Get-Content .vscode/settings.json"),
        ):
            with self.subTest(command=command):
                s = self.fresh()
                s.prompt("Check it.")
                s.load(ROUTER)
                s.say("goated-route: direct")
                s.call(tool, {"command": command})
                self.assertNotIn("Setup", stop(s).get("reason", ""))

    def setup_raised(self, tool: str, command: str) -> bool:
        s = self.fresh()
        s.prompt("Try the tool.")
        s.load(ROUTER)
        s.say("goated-route: direct")
        s.call(tool, {"command": command.replace("{project}", str(s.project))})
        return "- Setup:" in stop(s).get("reason", "")

    def test_a_local_install_in_a_folder_outside_the_project_does_not_count(self) -> None:
        # Spec R14. The scratch folder sits beside every session's project folder.
        outside = str(self.root / "scratch")
        for tool, command in (
            ("Bash", f'cd "{outside}" && pip install requests'),
            ("Bash", f'cd "{outside}" && npm install lodash'),
            ("Bash", f'cd "{outside}" && uv add httpx'),
            ("Bash", f'cd "{outside}" && cargo add serde'),
            ("Bash", f'cd "{outside}" && go get example.com/mod@v1.2.0'),
            ("PowerShell", f"Set-Location '{outside}' && pip install requests"),
        ):
            with self.subTest(command=command):
                self.assertFalse(self.setup_raised(tool, command))

    def test_a_global_install_counts_wherever_it_runs(self) -> None:
        outside = str(self.root / "scratch")
        for tool, command in (
            ("Bash", "uv tool install ruff"),
            ("Bash", "npm install -g pnpm"),
            ("Bash", "npm i --global pnpm"),
            ("Bash", "npm i -g typescript"),
            ("Bash", "npm install --location=global typescript"),
            ("Bash", "bun add -g typescript"),
            ("Bash", "bun add --global typescript"),
            ("Bash", "pip install --user requests"),
            ("Bash", "python -m pip install --user requests"),
            ("Bash", "sudo pip install requests"),
            ("Bash", "sudo npm install lodash"),
            ("Bash", "pnpm add -g zx"),
            ("Bash", "yarn global add pnpm"),
            ("Bash", "pipx install black"),
            ("Bash", "cargo install ripgrep"),
            ("Bash", "go install example.com/cmd/tool@latest"),
            ("Bash", "gem install bundler"),
            ("Bash", "brew install jq"),
            ("Bash", "apt install jq"),
            ("Bash", "sudo apt-get install -y ripgrep"),
            ("PowerShell", "winget install --id Git.Git -e"),
            ("PowerShell", "choco install nodejs -y"),
            ("PowerShell", "scoop install git"),
        ):
            with self.subTest(command=command):
                change = "Set-Location" if tool == "PowerShell" else "cd"
                self.assertTrue(self.setup_raised(tool, f'{change} "{outside}" && {command}'))

    def test_a_folder_option_decides_where_an_install_runs(self) -> None:
        outside = str(self.root / "scratch")
        for command, raised in (
            (f'cd "{outside}" && npm install --prefix "{{project}}" left-pad', True),
            (f'cd "{outside}" && npm --prefix "{{project}}" install left-pad', True),
            (f'cd "{outside}" && npm install --prefix="{{project}}" left-pad', True),
            (f'cd "{outside}" && uv add --project "{{project}}" httpx', True),
            (f'cd "{outside}" && pnpm --dir "{{project}}" add left-pad', True),
            (f'cd "{outside}" && yarn --cwd "{{project}}" add left-pad', True),
            # Near misses: the option points outside, from inside the project.
            (f'npm install --prefix "{outside}" left-pad', False),
            (f'uv add --project "{outside}" httpx', False),
            # A relative value after a cd outside stays outside.
            (f'cd "{outside}" && npm install --prefix ./tool left-pad', False),
        ):
            with self.subTest(command=command):
                self.assertEqual(self.setup_raised("Bash", command), raised)

    def test_an_install_in_the_project_or_an_unknown_folder_counts(self) -> None:
        outside = str(self.root / "scratch")
        for command in (
            "pip install requests",
            "npm install lodash",
            "cd src && pip install requests",  # A bare name may go through CDPATH: unknown.
            'cd "$TMPDIR" && pip install requests',
            f'cd "{outside}"; pip install requests',
            f'cd "{outside}" && cd "{{project}}" && pip install requests',
        ):
            with self.subTest(command=command):
                self.assertTrue(self.setup_raised("Bash", command))

    def test_settings_named_files_elsewhere_and_code_edits_end_without_setup(self) -> None:
        s = self.routed()
        s.say("goated-skip: software-design-principles: one mechanical constant change")
        s.call("Write", write("src/settings.json"))
        s.call("Write", write("docs/env.md"))
        s.call("Write", write("src/export.py"))
        s.run("pytest -q")
        s.load("doc-sync")
        s.run("git diff")

        self.assertEqual(stop(s), {})

    def test_a_failed_install_is_not_a_setup_change(self) -> None:
        s = self.routed()
        s.run("uv add no-such-package-xyz", success=False)

        self.assertEqual(stop(s), {})

    def test_loading_setup_scribe_clears_it(self) -> None:
        s = self.installed()
        s.load("setup-scribe")

        self.assertEqual(stop(s), {})

    def test_setup_scribe_loaded_before_the_install_still_clears_it(self) -> None:
        s = self.routed()
        s.load("setup-scribe")
        s.run("uv add httpx")

        self.assertEqual(stop(s), {})

    def test_a_skip_line_clears_it(self) -> None:
        s = self.installed()

        self.assertEqual(
            stop(s, "Added.\n\ngoated-skip: setup-scribe: the lockfile already records it"), {}
        )

    def test_a_typed_skip_override_clears_it(self) -> None:
        s = self.session
        s.prompt("Add httpx, and skip setup-scribe.")
        s.load(ROUTER)
        s.say("goated-route: direct")
        s.run("uv add httpx")

        self.assertEqual(stop(s), {})

    def test_it_sits_beside_the_code_items(self) -> None:
        s = self.installed()
        s.say("goated-skip: software-design-principles: one mechanical constant change")
        s.call("Write", write("src/export.py"))

        held = stop(s)
        self.assertEqual(closeout_line(held), "goated-hold: closeout | justified-skip")
        for item in ("- Proof:", "- Docs:", "- Setup:"):
            self.assertIn(item, held["reason"])

    def subagent_install(self, agent_id: str, *after: str) -> Session:
        """A turn whose subagent ran `uv add httpx`, then each of `after`: a
        skill to load, or a skip line to say."""

        s = self.routed()
        s.brief_with_handoff()
        agent = s.subagent(agent_id)
        agent.prompt("Add httpx.", hook=False)
        agent.run("uv add httpx")
        for step in after:
            if step.startswith("goated-skip:"):
                agent.say(step)
            else:
                agent.load(step)
        self.assertEqual(decision(s.spawn(agent_id, BRIEF)), "pass")
        return s

    def test_a_subagent_install_needs_setup_scribe(self) -> None:
        s = self.subagent_install("c1")

        held = stop(s)
        self.assertEqual(closeout_line(held), "goated-hold: closeout | justified-skip")
        self.assertIn("- Setup:", held["reason"])
        s.load("setup-scribe")
        self.assertEqual(stop(s), {})

    def test_a_subagents_own_load_meets_its_install(self) -> None:
        self.assertEqual(stop(self.subagent_install("c2", "setup-scribe")), {})

    def test_a_subagents_own_skip_line_meets_its_install(self) -> None:
        s = self.subagent_install("c3", "goated-skip: setup-scribe: the lockfile already records it")

        self.assertEqual(stop(s), {})

    def test_a_subagents_load_does_not_meet_the_parents_own_install(self) -> None:
        s = self.subagent_install("c4", "setup-scribe")
        s.run("brew install jq")

        self.assertIn("- Setup:", stop(s)["reason"])

    def test_the_header_names_setup_when_only_the_setup_item_is_left(self) -> None:
        s = self.routed()
        s.load("code-security-review")
        s.load("verification-before-completion")  # A sensitive file needs verification (Ticket 069).
        s.call("Edit", {"file_path": ".env.local", "old_string": "A=1", "new_string": "A=2"})
        s.run("git diff .env.local")

        held = stop(s)
        self.assertIn("which changed setup:", held["reason"])
        self.assertNotIn("- Security:", held["reason"])

    def test_it_does_not_carry_into_the_next_turn(self) -> None:
        s = self.installed()
        self.assertTrue(stop(s))

        s.prompt("Thanks. What else is left?")
        self.assertEqual(stop(s), {})


RED_FLAGS = "/opt/goated/skills/software-design-principles/references/red-flags.md"
DIFF = "git diff"


class ChangeReadTests(AdapterTestCase):
    """Holds whose step reviews or describes the change need a change read (spec R7, AC10)."""

    def designed(self) -> Session:
        """A turn that applied design, changed code, proved it, and read the red flags after."""

        s = self.routed()
        s.load("software-design-principles")
        s.call("Edit", edit("src/export.py", PLAIN))
        s.run("pytest -q")
        s.say("goated-skip: doc-sync: internal constant with no documented behavior")
        s.read(RED_FLAGS)
        return s

    def test_a_red_flags_read_alone_does_not_clear_the_design_item(self) -> None:
        s = self.designed()

        held = stop(s)
        self.assertEqual(closeout_line(held), "goated-hold: closeout | justified-skip")
        self.assertIn("- Design:", held["reason"])
        s.run(DIFF)
        self.assertEqual(stop(s), {})

    def test_a_change_read_before_the_red_flags_read_does_not_count(self) -> None:
        s = self.routed()
        s.load("software-design-principles")
        s.call("Edit", edit("src/export.py", PLAIN))
        s.run("pytest -q")
        s.say("goated-skip: doc-sync: internal constant with no documented behavior")
        s.run(DIFF)
        s.read(RED_FLAGS)

        self.assertIn("- Design:", stop(s)["reason"])

    def test_a_change_read_before_the_last_change_does_not_count(self) -> None:
        s = self.routed()
        s.say("goated-skip: software-design-principles: one mechanical constant change")
        s.load("doc-sync")
        s.call("Write", write("src/export.py"))
        s.run(DIFF)
        s.call("Edit", {"file_path": "src/export.py", "old_string": "a", "new_string": "b"})
        s.run("pytest -q")

        self.assertIn("- Docs:", stop(s)["reason"])
        s.read("src/export.py")
        self.assertEqual(stop(s), {})

    def test_listings_do_not_count_and_a_read_of_a_changed_file_does(self) -> None:
        for tool, command, counts in (
            ("Bash", "git diff --stat", False),
            ("Bash", "git diff --name-only HEAD", False),
            ("Bash", "git diff --name-status", False),
            ("Bash", "git diff --quiet", False),
            ("Bash", "git show --stat HEAD", False),
            ("Bash", "git log --oneline -3", False),
            ("Bash", "git status", False),
            ("Bash", "git diff > change.patch", False),
            ("Read", "src/other.py", False),
            ("Bash", "git diff", True),
            ("Bash", "git --no-pager diff --cached -- src/export.py", True),
            ("Bash", "git diff --stat -p", True),
            ("Bash", "git show HEAD", True),
            ("Bash", "git log -p -1", True),
            ("Bash", "git diff --output=change.patch", False),
            ("Bash", "git diff --output-indicator-new=+", True),
            ("Bash", "git log --patch-with-stat -1", True),
            ("Bash", "git log -U3 -1", True),
            ("Bash", "git log --unified=5 -1", True),
            ("Bash", "git whatchanged -p -1", True),
            ("Bash", "git whatchanged -1", False),
            ("Bash", "gh pr diff 12", True),
            ("Bash", "gh pr view 12", False),
            ("Bash", "glab mr diff", True),
            ("Bash", "git diff 2>err.txt", True),
            ("Bash", "git diff 1>out.txt", False),
            ("PowerShell", "git diff HEAD | Select-Object -First 200", True),
            ("Read", "src/export.py", True),
        ):
            with self.subTest(command=command):
                s = self.fresh()
                s.prompt("Bump it.")
                s.load(ROUTER)
                s.say("goated-route: direct")
                s.say("goated-skip: software-design-principles: one mechanical constant change")
                s.load("doc-sync")
                s.call("Write", write("src/export.py"))
                s.run("pytest -q")
                if tool == "Read":
                    s.read(command)
                else:
                    s.run(command, tool=tool)
                self.assertEqual(stop(s) == {}, counts)

    def test_a_loaded_docs_item_needs_a_change_read(self) -> None:
        s = self.routed()
        s.say("goated-skip: software-design-principles: one mechanical constant change")
        s.call("Write", write("src/export.py"))
        s.run("pytest -q")
        s.load("doc-sync")

        held = stop(s)
        self.assertIn("- Docs:", held["reason"])
        self.assertNotIn("`doc-sync`", held["reason"])  # Loaded: offered only as a skip line.
        s.run(DIFF)
        self.assertEqual(stop(s), {})

    def sensitive(self) -> Session:
        s = self.routed()
        s.load("code-security-review")
        s.load("verification-before-completion")  # A sensitive file needs verification (Ticket 069).
        s.say("goated-skip: software-design-principles: one mechanical constant change")
        s.say("goated-skip: doc-sync: internal constant with no documented behavior")
        s.call("Write", write("src/auth.py"))
        s.run("pytest -q")
        return s

    def test_a_loaded_security_review_needs_a_change_read(self) -> None:
        s = self.sensitive()

        held = stop(s)
        self.assertIn("- Security:", held["reason"])
        self.assertIn("auth", held["reason"])
        s.read("src/auth.py")
        self.assertEqual(stop(s), {})

    def test_a_sensitive_file_that_is_not_code_needs_it_too(self) -> None:
        s = self.routed()
        s.load("code-security-review")
        s.load("verification-before-completion")  # A sensitive file needs verification (Ticket 069).
        s.call("Edit", {"file_path": "config/secrets.yaml", "old_string": "A=1", "new_string": "A=2"})

        self.assertIn("- Security:", stop(s)["reason"])
        s.run("git diff config/secrets.yaml")
        self.assertEqual(stop(s), {})

    def test_a_security_skip_needs_no_change_read(self) -> None:
        s = self.routed()
        s.load("verification-before-completion")  # A sensitive file needs verification (Ticket 069).
        s.say("goated-skip: code-security-review: renames a local variable only")
        s.say("goated-skip: software-design-principles: one mechanical constant change")
        s.say("goated-skip: doc-sync: internal constant with no documented behavior")
        s.call("Write", write("src/auth.py"))
        s.run("pytest -q")

        self.assertEqual(stop(s), {})

    def test_a_skip_line_clears_a_loaded_items_change_read(self) -> None:
        s = self.sensitive()
        final = "goated-skip: code-security-review: reviewed the auth change in full earlier"

        self.assertEqual(stop(s, final), {})

    def test_a_user_typed_skip_clears_the_items(self) -> None:
        s = self.session
        s.prompt("Bump the constant, and skip doc-sync.")
        s.load(ROUTER)
        s.say("goated-route: direct")
        s.say("goated-skip: software-design-principles: one mechanical constant change")
        s.call("Write", write("src/export.py"))
        s.run("pytest -q")

        self.assertEqual(stop(s), {})

    def test_the_commit_hold_needs_a_change_read(self) -> None:
        s = self.routed()
        s.load("commit-message")

        held = s.call("Bash", commit("Add CSV export"))
        self.assertEqual(hold_line(held), "goated-hold: commit | strict")
        self.assertNotIn("`", reason(held).split("\n", 1)[1])
        s.run("git diff --cached --stat")
        self.assertEqual(decision(s.call("Bash", commit("Add CSV export"))), "deny")
        s.run("git diff --cached")
        self.assertEqual(decision(s.call("Bash", commit("Add CSV export"))), "pass")

    def test_a_commit_needs_the_change_read_after_the_last_change(self) -> None:
        s = self.routed()
        s.say("goated-skip: software-design-principles: one mechanical constant change")
        s.say("goated-skip: verification-before-completion: no test suite covers this file")
        s.say("goated-skip: doc-sync: internal constant with no documented behavior")
        s.load("commit-message")
        s.run(DIFF)
        s.call("Write", write("src/export.py"))

        self.assertEqual(decision(s.call("Bash", commit("Add CSV export"))), "deny")
        s.read("src/export.py")
        self.assertEqual(decision(s.call("Bash", commit("Add CSV export"))), "pass")

    def test_a_message_less_commit_needs_a_change_read_too(self) -> None:
        s = self.routed()
        s.load("commit-message")

        self.assertEqual(decision(s.call("Bash", {"command": "git commit -F msg.txt"})), "deny")
        s.run("git show")
        self.assertEqual(decision(s.call("Bash", {"command": "git commit -F msg.txt"})), "pass")

    def test_user_typed_commit_overrides_need_no_change_read(self) -> None:
        for prompt in ('Commit this with the message "Fix export rounding".',
                       "Commit it and skip commit-message this time."):
            with self.subTest(prompt=prompt):
                s = self.fresh()
                s.prompt(prompt)
                s.load(ROUTER)
                s.say("goated-route: direct")
                self.assertEqual(decision(s.call("Bash", commit("Fix export rounding"))), "pass")

    def test_the_pull_request_hold_needs_a_change_read_after_the_load(self) -> None:
        s = self.routed()
        command = {"command": "gh pr create --title 'Add export' --body-file body.md"}
        s.load("pr-description")

        held = s.call("Bash", command)
        self.assertEqual(hold_line(held), "goated-hold: pull-request | strict")
        self.assertNotIn("`", reason(held).split("\n", 1)[1])
        s.run("git diff main...HEAD --name-only")
        self.assertEqual(decision(s.call("Bash", command)), "deny")
        s.run("git diff main...HEAD")
        self.assertEqual(decision(s.call("Bash", command)), "pass")
        self.assertEqual(decision(s.call("mcp__github__create_pull_request", {"title": "x"})), "pass")

    def test_the_pull_request_text_says_a_chained_or_parallel_read_does_not_count(self) -> None:
        s = self.routed()
        s.load("pr-description")

        text = reason(s.call("Bash", {"command": "gh pr create --title x --body y"}))
        self.assertIn("chained", text)
        self.assertIn("parallel", text)

    def test_a_turn_that_changed_nothing_is_told_a_diff_is_the_way(self) -> None:
        s = self.routed()
        s.load("commit-message")

        text = reason(s.call("Bash", commit("Add CSV export")))
        self.assertIn("changed no file", text)
        self.assertNotIn("Read a file you changed", text)

    def test_mcp_commit_and_pr_tools_pass_when_the_turn_changed_no_project_file(self) -> None:
        # Outside a git checkout no diff can run and no changed file exists to Read, so a strict hold
        # with no exit would be a dead end; the change is in the tool's own input.
        for tool, tool_input, skill in (
            ("mcp__github__push_files", {"message": "Add export", "files": []}, "commit-message"),
            ("mcp__github__create_or_update_file", {"message": "Add export", "path": "a.py"},
             "commit-message"),
            ("mcp__github__create_pull_request", {"title": "x"}, "pr-description"),
        ):
            with self.subTest(tool=tool):
                s = self.fresh()
                s.prompt("Push it.")
                s.load(ROUTER)
                s.say("goated-route: direct")
                s.load(skill)
                self.assertEqual(decision(s.call(tool, tool_input)), "pass")
                s.say("goated-skip: software-design-principles: one mechanical constant change")
                s.say("goated-skip: verification-before-completion: no test suite covers this file")
                s.say("goated-skip: doc-sync: internal constant with no documented behavior")
                s.call("Write", write("src/export.py"))
                self.assertEqual(decision(s.call(tool, tool_input)), "deny")
                s.read("src/export.py")
                self.assertEqual(decision(s.call(tool, tool_input)), "pass")

    def test_a_non_code_change_needs_a_read_but_one_after_a_read_keeps_it(self) -> None:
        # A doc change after a change read keeps the commit's read (Ticket 120, R5);
        # a turn whose only change is a doc still needs one.
        s = self.routed()
        s.load("commit-message")
        s.call("Edit", {"file_path": "README.md", "old_string": "a", "new_string": "b"})

        self.assertEqual(decision(s.call("Bash", commit("Update the readme"))), "deny")
        s.read("README.md")
        s.call("Edit", {"file_path": "README.md", "old_string": "b", "new_string": "c"})
        self.assertEqual(decision(s.call("Bash", commit("Update the readme"))), "pass")

    def test_the_security_item_counts_from_the_last_sensitive_change(self) -> None:
        s = self.routed()
        s.load("code-security-review")
        s.load("verification-before-completion")  # A sensitive file needs verification (Ticket 069).
        s.call("Edit", {"file_path": "config/secrets.yaml", "old_string": "A=1", "new_string": "A=2"})
        s.read("config/secrets.yaml")
        s.say("goated-skip: software-design-principles: one mechanical constant change")
        s.call("Write", write("src/util.py"))
        s.run("pytest -q")
        s.say("goated-skip: doc-sync: internal constant with no documented behavior")

        self.assertEqual(stop(s), {})

    def test_a_subagents_changes_count_for_the_commit_hold(self) -> None:
        s = self.routed()
        s.say("goated-skip: verification-before-completion: no test suite covers this file")
        s.say("goated-skip: doc-sync: internal constant with no documented behavior")
        s.load("commit-message")
        s.run(DIFF)
        s.brief_with_handoff()
        agent = s.subagent("c1")
        agent.prompt("Implement it.", hook=False)
        agent.call("Edit", {"file_path": "src/app.py", "old_string": "a", "new_string": "b"},
                   agent_id="c1", agent_type="general-purpose")
        self.assertEqual(decision(s.spawn("c1", BRIEF)), "pass")

        self.assertEqual(decision(s.call("Bash", commit("Add export"))), "deny")
        s.read("src/app.py")
        self.assertEqual(decision(s.call("Bash", commit("Add export"))), "pass")


class HoldFormatTests(AdapterTestCase):
    """Every hold's first line follows the format the skill-usage mod parses."""

    FORMAT = re.compile(
        r"^goated-hold: (router-first|route-line|pipeline|commit|pull-request|pr-review|spawn"
        r"|design|security|conflict-resolution|repeated-failure|closeout) \| (strict|justified-skip)$"
    )

    def test_every_hold_message_starts_with_the_documented_line(self) -> None:
        s = self.session
        s.prompt("Do the task.")
        lines = [hold_line(s.call("Bash"))]
        s.load(ROUTER)
        lines.append(hold_line(s.call("Edit")))
        s.say("goated-route: standard | requires: tdd")
        lines.append(hold_line(s.call("Edit")))
        s.load("tdd")
        lines.append(hold_line(s.call("Bash", commit("Add export"))))
        lines.append(hold_line(s.call("Bash", {"command": "gh pr create"})))
        lines.append(hold_line(s.call("Agent", {"prompt": BRIEF})))
        lines.append(hold_line(s.call("Write", write("src/export.py"))))
        lines.append(hold_line(s.call("Edit", {"file_path": ".env", "new_string": "x"})))
        s.say("goated-skip: software-design-principles: one mechanical constant change")
        s.call("Write", write("src/export.py"))
        lines.append(closeout_line(stop(s)))

        self.assertEqual(len(set(lines)), 9)
        for line in lines:
            self.assertRegex(line, self.FORMAT)


class ReviewRegressionTests(AdapterTestCase):
    """Regression tests for the independent review of ticket 031."""

    LONG = "A" * 80

    def loaded(self, prompt: str = "Do the task.") -> Session:
        s = self.routed(prompt=prompt)
        s.load("commit-message")
        s.run("git diff")
        return s

    def held_line(self, tool: str, command: str, setup=None) -> str:
        s = self.fresh()
        s.prompt("Do the task.")
        s.load(ROUTER)
        s.say("goated-route: direct")
        if setup:
            setup(s)
        return hold_line(s.call(tool, {"command": command}))

    # Item 1: the message is read from the commit's own segment.
    def test_a_chained_commit_message_is_checked_and_matched(self) -> None:
        for command in (
            f'python -m pytest -q && git commit -m "{self.LONG}"',
            f'grep -m1 x a; git commit -m "{self.LONG}"',
        ):
            with self.subTest(command=command):
                line = self.held_line("Bash", command, lambda s: s.load("commit-message"))
                self.assertEqual(line, "goated-hold: commit | strict")

        s = self.session
        s.prompt('Commit with the message "Fix export rounding".')
        s.load(ROUTER)
        s.say("goated-route: direct")
        command = 'python -m pytest -q && git commit -m "Fix export rounding"'
        self.assertEqual(decision(s.call("Bash", {"command": command})), "pass")

    # Item 2: combined short flags carry the message.
    def test_combined_short_flags_carry_the_message(self) -> None:
        for flags in ("-am", "-sm"):
            with self.subTest(flags=flags):
                command = f'git commit {flags} "{self.LONG}"'
                line = self.held_line("Bash", command, lambda s: s.load("commit-message"))
                self.assertEqual(line, "goated-hold: commit | strict")

        s = self.session
        s.prompt('Commit with the message "Fix export rounding".')
        s.load(ROUTER)
        s.say("goated-route: direct")
        command = 'git commit -am "Fix export rounding"'
        self.assertEqual(decision(s.call("Bash", {"command": command})), "pass")

    # Item 3: dependency manifests ending in .txt are sensitive, by edit or shell.
    def test_requirements_files_meet_the_security_hold(self) -> None:
        s = self.routed()
        for path in ("requirements.txt", "requirements-dev.txt"):
            with self.subTest(path=path):
                edit = {"file_path": path, "old_string": "a", "new_string": "b"}
                self.assertEqual(hold_line(s.call("Edit", edit)), "goated-hold: security | justified-skip")
        held = s.call("Bash", {"command": "echo requests >> requirements.txt"})
        self.assertEqual(hold_line(held), "goated-hold: security | justified-skip")

    # Item 4: only write targets inside the project count as changed code.
    def test_only_written_project_code_counts_for_closeout(self) -> None:
        for command in ("python scripts/report.py > report.txt",
                        'cp src/app.py "{outside}/app_backup.py"'):
            with self.subTest(command=command):
                s = self.fresh()
                command = command.replace("{outside}", str(s.root / "backup"))
                s.prompt("Report.")
                s.load(ROUTER)
                s.say("goated-route: direct")
                s.run(command)
                self.assertEqual(stop(s), {})

    def test_a_check_that_tees_its_log_is_proof_not_a_change(self) -> None:
        s = self.changed_app()
        s.run("python -m pytest tests/test_app.py 2>&1 | tee test.log")

        self.assertEqual(stop(s), {})

    def test_an_edit_outside_the_project_is_not_a_change(self) -> None:
        s = self.routed()
        s.say("goated-skip: software-design-principles: throwaway scratch script only")
        s.call("Write", write(str(s.root / "scratch" / "probe.py")))

        self.assertEqual(stop(s), {})

    def changed_app(self) -> Session:
        s = self.routed()
        s.call("Edit", {"file_path": str(s.project / "src" / "app.py"),
                        "old_string": "a", "new_string": "b"})
        s.load("doc-sync")
        s.run("git diff")
        return s

    # Item 5: proof is a check command, not any command naming "test" or "build".
    def test_commands_that_only_mention_checks_are_not_proof(self) -> None:
        for command in ("rm -rf build", "uv sync --extra test", "mkdir tests"):
            with self.subTest(command=command):
                s = self.fresh()
                s.prompt("Bump it.")
                s.load(ROUTER)
                s.say("goated-route: direct")
                s.call("Edit", {"file_path": "src/app.py", "old_string": "a", "new_string": "b"})
                s.load("doc-sync")
                s.run(command)
                self.assertIn("Proof", stop(s).get("reason", ""))

    # Item 6: common spellings of commit and PR commands are still held.
    def test_common_command_spellings_meet_the_strict_holds(self) -> None:
        commits = (
            ("Bash", 'git \\\n  commit -m "Add export"'),
            ("PowerShell", 'git `\n  commit -m "Add export"'),
            ("Bash", '"git" commit -m "Add export"'),
            ("PowerShell", '& "C:\\Program Files\\Git\\cmd\\git.exe" commit -m "Add export"'),
            ("Bash", 'timeout 60 git commit -m "Add export"'),
            ("Bash", 'nice git commit -m "Add export"'),
            ("PowerShell", 'cmd /c git commit -m "Add export"'),
            ("Bash", 'sudo -u bob git commit -m "Add export"'),
        )
        for tool, command in commits:
            with self.subTest(command=command):
                self.assertEqual(self.held_line(tool, command), "goated-hold: commit | strict")
        for command in ("gh pr new --fill", "gh \\\n  pr create --fill", "gh -R o/r pr create"):
            with self.subTest(command=command):
                self.assertEqual(
                    self.held_line("Bash", command), "goated-hold: pull-request | strict"
                )

    def test_a_continued_shell_write_meets_the_route_line_hold(self) -> None:
        s = self.session
        s.prompt("Apply it.")
        s.load(ROUTER)

        held = s.call("Bash", {"command": "git \\\n  apply fix.patch"})
        self.assertEqual(hold_line(held), "goated-hold: route-line | strict")

    # Item 7: more write commands.
    def test_more_write_commands_meet_the_route_line_hold(self) -> None:
        for tool, command in (
            ("PowerShell", "'x' | sc notes.txt"),
            ("PowerShell", "ac log.txt 'line'"),
            ("PowerShell", "clc log.txt"),
            ("PowerShell", "Get-Process | Export-Csv procs.csv"),
            ("Bash", "curl -o src/vendor.py https://example.invalid/x.py"),
            ("Bash", "curl -sSLo src/vendor.py https://example.invalid/x.py"),
            ("Bash", "wget https://example.invalid/x.tar.gz"),
            ("Bash", "patch -p1 < fix.patch"),
            ("Bash", "git checkout HEAD~1 src/app.py"),
        ):
            with self.subTest(command=command):
                s = self.fresh()
                s.prompt("Do it.")
                s.load(ROUTER)
                held = s.call(tool, {"command": command})
                self.assertEqual(hold_line(held), "goated-hold: route-line | strict")

    # Item 8: comparisons, comments, and mentions are not writes or actions.
    def test_comparisons_comments_and_mentions_stay_free(self) -> None:
        for command in (
            '[[ "$a" > "$b" ]] && echo yes',
            "echo $((2 > 1))",
            "ls # list > files",
            "echo gh pr create",
            "git commit --dry-run",
            "curl -s https://example.invalid/x | head",
        ):
            with self.subTest(command=command):
                s = self.fresh()
                s.prompt("Look.")
                s.load(ROUTER)
                self.assertEqual(decision(s.call("Bash", {"command": command})), "pass")

    # Item 9: sensitive words must stand alone in the path.
    def test_security_words_must_stand_alone_in_the_path(self) -> None:
        s = self.routed()
        for path, held in (
            ("src/tokenizer.py", False),
            ("src/author.py", False),
            ("src/api_token.py", True),
            ("src/userAuth.ts", True),
            ("src/auth/views.py", True),
            # `session` counts only beside another auth word (round 7, R5).
            ("src/runtime/session.py", False),
            ("src/sessions.py", False),
            ("src/auth/session.py", True),
            ("src/login_session.py", True),
        ):
            with self.subTest(path=path):
                edit = {"file_path": path, "old_string": "a", "new_string": "b"}
                self.assertEqual(decision(s.call("Edit", edit)) == "deny", held)

    # Item 10: `-F -` reads the heredoc fed to the commit itself.
    def test_the_commit_reads_its_own_heredoc(self) -> None:
        s = self.loaded()
        command = (
            "cat <<'EOF' > notes.md\nshort\nEOF\ngit commit -F - <<'EOF'\n"
            + "B" * 90 + "\nEOF"
        )
        self.assertEqual(hold_line(s.call("Bash", {"command": command})), "goated-hold: commit | strict")

    def test_a_commit_body_ending_lines_in_backticks_is_read_whole(self) -> None:
        s = self.loaded()
        command = (
            'git commit -m "$(cat <<\'EOF\'\nUpdate `gates.py`\n\nExplain `x`\nand `y`\nEOF\n)"'
        )
        self.assertEqual(decision(s.call("Bash", {"command": command})), "pass")

    # Item 11: code a subagent changed counts toward the parent's closeout.
    def test_subagent_code_changes_need_the_parents_closeout(self) -> None:
        s = self.routed()
        s.brief_with_handoff()
        agent = s.subagent("b1")
        agent.prompt("Implement it.", hook=False)
        agent.call("Edit", {"file_path": "src/app.py", "old_string": "a", "new_string": "b"},
                   agent_id="b1", agent_type="general-purpose")
        self.assertEqual(decision(s.spawn("b1", BRIEF)), "pass")

        held = stop(s)
        self.assertIn("Proof", held["reason"])
        self.assertIn("doc-sync", held["reason"])
        s.run("pytest -q")
        s.load("doc-sync")
        s.run("git diff")
        self.assertIn("- Verification: load `verification-before-completion` and follow it, since a subagent "
                      "changed code", stop(s)["reason"])  # Ticket 069.
        s.load("verification-before-completion")
        self.assertEqual(stop(s), {})

    def test_a_subagent_that_ran_its_own_check_proved_its_change(self) -> None:
        s = self.routed()
        s.brief_with_handoff()
        agent = s.subagent("b2")
        agent.prompt("Implement it.", hook=False)
        agent.call("Edit", {"file_path": "src/app.py", "old_string": "a", "new_string": "b"},
                   agent_id="b2", agent_type="general-purpose")
        agent.run("pytest -q")
        s.spawn("b2", BRIEF)

        held = stop(s)
        self.assertNotIn("Proof", held["reason"])
        self.assertIn("doc-sync", held["reason"])

    def test_a_subagents_same_command_check_proved_its_change(self) -> None:
        s = self.routed()
        s.brief_with_handoff()
        agent = s.subagent("b2")
        agent.prompt("Implement it.", hook=False)
        agent.run("cp a.py src/app.py && pytest -q")
        s.spawn("b2", BRIEF)

        held = stop(s)
        self.assertNotIn("Proof", held["reason"])
        self.assertIn("doc-sync", held["reason"])

    def test_a_subagents_background_write_and_check_proves_nothing(self) -> None:
        # Ticket 116: a background call is no check, in a later call or the same one.
        s = self.routed()
        s.brief_with_handoff()
        agent = s.subagent("b3")
        agent.prompt("Implement it.", hook=False)
        agent.call("Bash", {"command": "cp a.py src/app.py && pytest -q", "run_in_background": True},
                   agent_id="b3", agent_type="general-purpose")
        s.spawn("b3", BRIEF)

        self.assertIn("- Proof:", stop(s)["reason"])

    def test_a_subagents_comment_only_edit_after_its_check_keeps_the_proof(self) -> None:
        s = self.routed()
        s.brief_with_handoff()
        agent = s.subagent("b4")
        agent.prompt("Implement it.", hook=False)
        agent.call("Edit", {"file_path": "src/app.py", "old_string": "a", "new_string": "b"},
                   agent_id="b4", agent_type="general-purpose")
        agent.run("pytest -q")
        agent.call("Edit", {"file_path": "src/app.py", "old_string": "# old note",
                            "new_string": "# new note"},
                   agent_id="b4", agent_type="general-purpose")
        s.spawn("b4", BRIEF)

        held = stop(s)
        self.assertNotIn("Proof", held["reason"])
        self.assertIn("doc-sync", held["reason"])

    # Item 12: the older spawn tool name and MCP commit tools.
    def test_the_task_spawn_tool_is_held(self) -> None:
        s = self.routed()

        self.assertEqual(hold_line(s.call("Task", {"prompt": BRIEF})), "goated-hold: spawn | strict")
        s.brief_with_handoff()
        self.assertEqual(decision(s.call("Task", {"prompt": BRIEF})), "pass")

    def test_mcp_tools_that_commit_meet_the_commit_hold(self) -> None:
        s = self.routed()
        tool = "mcp__github__push_files"

        held = s.call(tool, {"message": "Add export", "files": []})
        self.assertEqual(hold_line(held), "goated-hold: commit | strict")
        s.load("commit-message")
        s.run("git diff")
        self.assertEqual(decision(s.call(tool, {"message": self.LONG, "files": []})), "deny")
        self.assertEqual(decision(s.call(tool, {"message": "Add export", "files": []})), "pass")


class InteractiveRecordingTests(AdapterTestCase):
    """In an interactive session Claude Code records the assistant message
    holding a call only after PreToolUse returns, so the hook judges the call
    from its input alone. Headless runs often record it first; both orders
    must give the same answers."""

    def gate_lines(self, record_before_hook: bool) -> list[str]:
        s = self.fresh()
        s.record_before_hook = record_before_hook
        s.prompt("Do the task.")
        lines = [hold_line(s.call("Bash"))]
        s.load(ROUTER)
        lines.append(hold_line(s.call("Edit")))
        s.say("goated-route: standard | requires: tdd")
        lines.append(hold_line(s.call("Edit")))
        s.load("tdd")
        lines.append(hold_line(s.call("Bash", commit("Add export"))))
        lines.append(hold_line(s.call("Bash", {"command": "gh pr create --fill"})))
        lines.append(hold_line(s.call("Agent", {"prompt": BRIEF})))
        lines.append(hold_line(s.call("Write", write("src/export.py"))))
        lines.append(hold_line(s.call("Edit", {"file_path": ".env", "new_string": "x"})))
        s.say("goated-skip: software-design-principles: one mechanical constant change")
        self.assertEqual(decision(s.call("Write", write("src/export.py"))), "pass")
        lines.append(closeout_line(stop(s)))
        return lines

    def test_every_gate_holds_a_call_the_transcript_does_not_show_yet(self) -> None:
        lines = self.gate_lines(record_before_hook=False)

        self.assertEqual(lines, [
            "goated-hold: router-first | strict",
            "goated-hold: route-line | strict",
            "goated-hold: pipeline | strict",
            "goated-hold: commit | strict",
            "goated-hold: pull-request | strict",
            "goated-hold: spawn | strict",
            "goated-hold: design | justified-skip",
            "goated-hold: security | justified-skip",
            "goated-hold: closeout | justified-skip",
        ])
        self.assertEqual(lines, self.gate_lines(record_before_hook=True))

    def test_parallel_calls_recorded_after_both_hooks_are_each_judged(self) -> None:
        s = self.routed()

        commit_out, design_out = s.parallel([
            ("Bash", commit("Add export")),
            ("Write", write("src/export.py")),
        ])
        self.assertEqual(hold_line(commit_out), "goated-hold: commit | strict")
        self.assertEqual(hold_line(design_out), "goated-hold: design | justified-skip")
        for output in (commit_out, design_out):
            self.assertNotIn("systemMessage", output)

    def test_a_sibling_load_in_the_same_message_does_not_count(self) -> None:
        s = self.routed()

        _, held = s.parallel([
            ("Skill", {"skill": "commit-message"}),
            ("Bash", commit("Add export")),
        ])
        self.assertEqual(hold_line(held), "goated-hold: commit | strict")

    def test_a_subagent_call_not_yet_recorded_is_judged(self) -> None:
        self.session.prompt("Delegate it.")
        agent = self.session.subagent("c1")
        agent.prompt("Implement it.", hook=False)

        held = agent.call("Bash", commit("Add export"), agent_id="c1", agent_type="general-purpose")
        self.assertEqual(hold_line(held), "goated-hold: commit | strict")

    def test_a_stop_without_its_prompt_recorded_fails_open(self) -> None:
        s = self.routed()
        s.call("Edit", {"file_path": "src/app.py", "old_string": "a", "new_string": "b"})

        output = parse(s.hook("Stop", stop_hook_active=False, prompt_id="prompt-not-recorded"))
        self.assertNotIn("decision", output)
        self.assertIn("allowed without checks", output.get("systemMessage", ""))


class SkillSkipPhraseTests(AdapterTestCase):
    """`skip <name>` is an override only when `<name>` is a skill."""

    def test_skip_followed_by_an_ordinary_word_is_not_an_override(self) -> None:
        from claude_code_adapter_support import parse_overrides

        for prompt in (
            "If it does not apply, decline it with a goated-skip line instead of loading the skill.",
            "Skip the first two lines of the log.",
            "skip line 3",
        ):
            with self.subTest(prompt=prompt):
                self.assertEqual(parse_overrides(prompt)["skills"], [])

    def test_a_prompt_naming_no_skill_records_no_override(self) -> None:
        s = self.session
        notice = s.prompt("Decline it with a goated-skip line instead of loading the skill.")

        self.assertEqual(notice, "")

    def test_installed_skills_decide_which_names_count(self) -> None:
        skill = self.session.config.home / ".claude" / "skills" / "my-review"
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_text("# My Review\n", encoding="utf-8")
        s = self.session

        self.assertIn("Skip my-review", s.prompt("Skip my-review this time."))
        # With skills found, a GOATED name that is not installed does not count.
        self.assertEqual(s.prompt("Skip tdd this time."), "")

    def test_the_fallback_list_matches_the_registry(self) -> None:
        import yaml
        from claude_code_adapter_support import REPO_ROOT
        from goated_core.overrides import GOATED_SKILLS

        registry = yaml.safe_load(
            (REPO_ROOT / "stack" / "goated-stack.yaml").read_text(encoding="utf-8")
        )
        self.assertEqual(GOATED_SKILLS, {skill["name"] for skill in registry["skills"]})


DESIGN_SKILL_SOURCE = (
    Path(__file__).resolve().parents[1] / "skills" / "engineering" / "software-design-principles"
)
DOC_SKIP = "goated-skip: doc-sync: internal constant with no documented behavior"
# Claude Code's result text for a Write that replaced a file on disk.
WRITE_UPDATED = "The file {path} has been updated successfully."


class DesignRedFlagsItemTests(AdapterTestCase):
    """The closeout's Design item: the red flags and a change read (Tickets 052, 059).
    Its citations item is gone (Ticket 089)."""

    def designing(self) -> Session:
        s = self.routed()
        s.load("software-design-principles")
        s.read(REFERENCES + "errors.md")
        s.call("Edit", edit("src/export.py", PLAIN))
        s.run("pytest -q")
        s.say(DOC_SKIP)
        return s

    def test_the_red_flags_and_change_read_items(self) -> None:
        s = self.designing()

        held = stop(s)
        self.assertIn(
            "- Design: read `software-design-principles/references/red-flags.md` whole with the Read tool",
            held["reason"],
        )
        self.assertNotIn("file#id", held["reason"])
        s.read(RED_FLAGS)
        # The item's second ask is new to the turn, so it comes in full (Ticket 095).
        self.assertIn("- Design: read the change itself after reading the red flags and after your "
                      "last code change, and scan it", stop(s)["reason"])
        s.run(DIFF)
        self.assertEqual(stop(s), {})

    def test_a_skip_line_stands_the_item_down(self) -> None:
        s = self.designing()
        s.say("goated-skip: software-design-principles: one mechanical constant change")

        self.assertEqual(stop(s), {})

    def test_the_red_flags_item_asks_the_question_and_no_hold_needs_an_answer(self) -> None:
        question = "Name one input that would break this change, and say what happens."
        red_flags = (DESIGN_SKILL_SOURCE / "references" / "red-flags.md").read_text(encoding="utf-8")
        self.assertTrue(red_flags.rstrip().endswith(question), red_flags[-300:])

        s = self.designing()
        item = next(line for line in stop(s)["reason"].split("\n") if "red-flags.md" in line)
        self.assertIn(question, item)
        s.read(RED_FLAGS)
        item = next(line for line in stop(s)["reason"].split("\n") if "red flags" in line)
        self.assertIn(question, item)
        # No answer is checked: the change read alone meets the item, while the
        # near miss above, the red flags read with no change read, did not.
        s.run(DIFF)
        self.assertEqual(stop(s), {})

    def test_red_flags_declares_only_ids_the_section_index_lists(self) -> None:
        skill = (DESIGN_SKILL_SOURCE / "SKILL.md").read_text(encoding="utf-8")
        row = next(line for line in skill.splitlines()
                   if line.startswith("| [") and "(references/red-flags.md)" in line)
        red_flags = (DESIGN_SKILL_SOURCE / "references" / "red-flags.md").read_text(encoding="utf-8")
        declared = set(re.findall(r"<!-- id: #([a-z-]+) -->", red_flags))

        self.assertEqual(declared, set(re.findall(r"`#([a-z-]+)`", row.split("|")[-2])))
        self.assertEqual(declared, {"red-flags"})


class RestoreLimitTests(AdapterTestCase):
    """A restore command counts as a change whatever it restores (Ticket 061)."""

    def test_a_restore_after_the_check_asks_for_proof_and_a_rerun_answers_it(self) -> None:
        s = self.routed()
        s.call("Edit", edit("src/export.py", PLAIN))
        s.run("pytest -q")
        s.say(DOC_SKIP)
        self.assertEqual(stop(s), {})

        s.run("git checkout -- src/export.py")
        self.assertIn("- Proof:", stop(s)["reason"])
        s.run("pytest -q")
        self.assertEqual(stop(s), {})

    def test_known_limits_names_the_restore_case(self) -> None:
        readme = (Path(__file__).resolve().parents[1] / "adapters" / "claude-code"
                  / "README.md").read_text(encoding="utf-8")
        limits = readme.split("\n## Known Limits\n", 1)[1].split("\n## ", 1)[0]
        other = readme.replace(limits, "")

        self.assertRegex(limits, r"restore[^.]*counts as a change whatever it restores")
        # The near miss: the note lives in Known Limits, not elsewhere.
        self.assertNotRegex(other, r"counts as a change whatever it restores")


CLOSEOUT_HOLD = "goated-hold: closeout | justified-skip"
PROOF_SKIP = "goated-skip: verification-before-completion: no test suite covers this file"
DESIGN_SKIP = "goated-skip: software-design-principles: one mechanical constant change"
# Every design reference a design-reads line can require, read so no design-reads hold applies.
REFERENCE_FILES = ("process.md", "complexity-and-modules.md", "decoupling.md", "readability.md",
                   "errors.md", "coding.md", "concurrency.md", "differences.md")
# Edits whose added and removed text is only comments or docstrings (Ticket 059).
COMMENT_EDITS = (
    {"file_path": "src/export.py", "old_string": "total_0 = 0", "new_string": "total_0 = 0  # the first"},
    {"file_path": "src/export.py", "old_string": '"""Old doc."""\ntotal_1 = 1',
     "new_string": '"""New doc, longer."""\ntotal_1 = 1'},
    {"file_path": "src/export.py", "edits": [
        {"old_string": "# old note", "new_string": "# new note"},
        {"old_string": "total_2 = 2  # two", "new_string": "total_2 = 2  # still two"},
    ]},
)


class ChangeReadOrderTests(AdapterTestCase):
    """A change read counts after the last change, before or after the skill load (Ticket 059)."""

    def test_a_diff_read_before_the_commit_message_load_passes_the_commit(self) -> None:
        s = self.routed()
        s.call("Edit", {"file_path": "README.md", "old_string": "a", "new_string": "b"})
        s.run(DIFF)
        s.load("commit-message")

        self.assertEqual(decision(s.call("Bash", commit("Update the readme"))), "pass")

    def test_a_change_after_the_read_still_needs_a_new_read_for_the_commit(self) -> None:
        s = self.routed()
        s.say(PROOF_SKIP)
        s.say(DOC_SKIP)
        s.call("Edit", {"file_path": "src/export.py", "old_string": "a = 1", "new_string": "a = 2"})
        s.run(DIFF)
        s.load("commit-message")
        s.call("Edit", {"file_path": "src/export.py", "old_string": "a = 2", "new_string": "a = 3"})

        held = s.call("Bash", commit("Update the export"))
        self.assertEqual(hold_line(held), "goated-hold: commit | strict")
        self.assertNotIn("after loading", reason(held))
        s.read("src/export.py")
        self.assertEqual(decision(s.call("Bash", commit("Update the export"))), "pass")

    def test_a_diff_read_before_the_pr_description_load_passes_the_pull_request(self) -> None:
        s = self.routed()
        command = {"command": "gh pr create --title 'Update readme' --body-file body.md"}
        s.call("Edit", {"file_path": "README.md", "old_string": "a", "new_string": "b"})
        s.run(DIFF)
        s.load("pr-description")

        self.assertEqual(decision(s.call("Bash", command)), "pass")
        s.call("Edit", {"file_path": "README.md", "old_string": "b", "new_string": "c"})
        self.assertEqual(hold_line(s.call("Bash", command)), "goated-hold: pull-request | strict")

    def test_a_diff_read_before_the_doc_sync_load_meets_the_docs_item(self) -> None:
        s = self.routed()
        s.say(DESIGN_SKIP)
        s.call("Write", write("src/export.py"))
        s.run("pytest -q")
        s.run(DIFF)
        s.load("doc-sync")

        self.assertEqual(stop(s), {})

    def test_a_code_change_after_the_read_reopens_the_docs_item(self) -> None:
        s = self.routed()
        s.say(DESIGN_SKIP)
        s.call("Write", write("src/export.py"))
        s.run(DIFF)
        s.load("doc-sync")
        s.call("Edit", {"file_path": "src/export.py", "old_string": "a", "new_string": "b"})
        s.run("pytest -q")

        held = stop(s)
        self.assertIn("- Docs:", held["reason"])
        self.assertNotIn("after loading", held["reason"])


class CommentOnlyEditTests(AdapterTestCase):
    """A comment-only edit does not reopen the Design item (Ticket 059) and keeps the proof
    (Ticket 116); Docs still counts it."""

    def designed(self) -> Session:
        """A turn that met every closeout item, the Design item's red flags and change read included."""

        s = self.routed()
        s.load("software-design-principles")
        s.read(REFERENCES + "readability.md")  # The design gates require it for a comment.
        s.call("Edit", edit("src/export.py", PLAIN))
        s.run("pytest -q")
        s.say(DOC_SKIP)
        s.read(RED_FLAGS)
        s.run(DIFF)
        self.assertEqual(stop(s), {})
        return s

    def test_a_comment_only_edit_does_not_reopen_the_design_item(self) -> None:
        for change in COMMENT_EDITS:
            with self.subTest(change=change):
                self.session = self.fresh()
                s = self.designed()
                tool = "Edit" if "old_string" in change else "MultiEdit"
                self.assertEqual(decision(s.call(tool, change)), "pass")
                s.run("pytest -q")
                self.assertEqual(stop(s), {})

    def test_an_edit_that_also_changes_code_reopens_it(self) -> None:
        s = self.designed()
        s.call("Edit", {"file_path": "src/export.py", "old_string": "total_0 = 0",
                        "new_string": "total_0 = 10  # the first"})
        s.run("pytest -q")

        self.assertIn("- Design:", stop(s)["reason"])

    def test_code_changes_that_look_like_comments_reopen_it(self) -> None:
        # Review of Ticket 059: each of these changes code, or text the comment rules cannot
        # read for certain, so each counts as a change and reopens the Design item.
        for path, old, new in (
            ("src/export.py", "x = a // 2", "x = a // 3"),  # Floor division, not a comment.
            ("src/export.py", 'label = "a # b"', 'label = "a # c"'),
            ("src/export.py", 'label = "a  # b"', 'label = "a  # c"'),
            ("src/lib.c", "#define MAX 1", "#define MAX 2"),
            ("src/lib.c", "#include <a.h>", "#include <b.h>"),
            ("src/lib.rs", "#[derive(Debug)]", "#[derive(Debug, Clone)]"),
            ("src/export.py", "*rest,", "*other,"),
            ("src/lib.c", "*rest,", "*other,"),
            ("src/lib.c", "/* a */ f(1);", "/* a */ f(2);"),
            ("src/export.py", '"""\ntotal = 1', '"""\ntotal = 2'),
            ("src/export.py", 'text = """\n# one', 'text = """\n# two'),
            ("src/app.js", "const s = `a\n// one", "const s = `a\n// two"),
            ("src/notes.lua", "-- one", "-- two"),  # A language with no known comment syntax.
        ):
            with self.subTest(path=path, old=old):
                self.session = self.fresh()
                s = self.designed()
                for name in REFERENCE_FILES:  # No design-reads hold, so every edit applies.
                    s.read(REFERENCES + name)
                self.assertEqual(decision(s.call("Edit", {"file_path": path, "old_string": old,
                                                          "new_string": new})), "pass")
                s.run("pytest -q")
                self.assertIn("- Design:", stop(s)["reason"])

    def test_comment_changes_in_c_family_files_do_not_reopen_it(self) -> None:
        for path, old, new in (
            ("src/lib.c", "f(1);  // one", "f(1);  // two"),
            ("src/lib.rs", "/// Old doc.\nfn f() {}", "/// New doc.\nfn f() {}"),
            ("src/app.js", "/* old\n * note */\nf(1);", "/* new\n * note */\nf(1);"),
        ):
            with self.subTest(path=path):
                self.session = self.fresh()
                s = self.designed()
                for name in REFERENCE_FILES:
                    s.read(REFERENCES + name)
                s.call("Edit", {"file_path": path, "old_string": old, "new_string": new})
                s.run("pytest -q")
                self.assertEqual(stop(s), {})

    def test_an_indentation_change_beside_a_comment_reopens_it(self) -> None:
        # Indentation is code in Python, so the comment rules do not read it as a comment change.
        s = self.designed()
        s.call("Edit", {"file_path": "src/export.py", "old_string": "total_0 = 0",
                        "new_string": "    total_0 = 0  # the first"})
        s.run("pytest -q")

        self.assertIn("- Design:", stop(s)["reason"])

    def test_a_comment_only_write_that_replaces_the_files_code_reopens_it(self) -> None:
        s = self.designed()
        s.call("Write", {"file_path": "src/export.py", "content": "# Nothing here yet.\n"})
        s.run("pytest -q")

        self.assertIn("- Design:", stop(s)["reason"])

    def checked(self) -> Session:
        """A turn that changed a code line and passed a check, with Docs and Design skipped."""

        s = self.routed()
        s.say(DESIGN_SKIP)
        s.say(DOC_SKIP)
        s.call("Edit", edit("src/export.py", PLAIN))
        s.run("pytest -q")
        self.assertEqual(stop(s), {})
        return s

    def test_a_comment_only_edit_after_a_passing_check_keeps_the_proof(self) -> None:
        # Ticket 116 (N1): comments do not run, so a comment-only edit of any size is proved.
        long_docstring = ('    """Return the export total.\n\n'
                          + lines_of("    Line {n} of the explanation.", 30) + '\n    """')
        changes = (*COMMENT_EDITS, {"file_path": "src/export.py",
                                    "old_string": '    """Old doc."""\n    return total',
                                    "new_string": long_docstring + "\n    return total"})
        for change in changes:
            with self.subTest(change=change):
                self.session = self.fresh()
                s = self.checked()
                s.call("Edit", change)
                self.assertEqual(stop(s), {})

    def test_a_comment_only_edit_with_no_check_in_the_turn_needs_no_proof(self) -> None:
        s = self.routed()
        s.say(DESIGN_SKIP)
        s.say(DOC_SKIP)
        s.call("Edit", COMMENT_EDITS[0])

        self.assertEqual(stop(s), {})

    def test_near_miss_an_edit_changing_one_code_line_after_the_check_needs_proof(self) -> None:
        s = self.checked()
        s.call("Edit", {"file_path": "src/export.py", "old_string": "total_0 = 0",
                        "new_string": "total_0 = 1  # the first"})

        self.assertIn("- Proof:", stop(s)["reason"])

    def test_near_miss_an_edit_that_opens_or_closes_a_block_needs_proof(self) -> None:
        # The code after a fragment that leaves a block open is commented out, and the reverse.
        changes = (
            ("src/export.ts", "/* note */", "/* note"),
            ("src/export.ts", "/* note", "/* note */"),
            ("src/export.py", "# a", '"""a'),
            ("src/export.py", '"""a', "# a"),
        )
        for path, old, new in changes:
            with self.subTest(old=old, new=new):
                self.session = self.fresh()
                s = self.checked()
                s.call("Edit", {"file_path": path, "old_string": old, "new_string": new})
                self.assertIn("- Proof:", stop(s)["reason"])

    def test_a_docstring_left_open_on_both_sides_keeps_the_proof(self) -> None:
        s = self.checked()
        s.call("Edit", {"file_path": "src/export.py", "old_string": '    """Return x.',
                        "new_string": '    """Return x, capped.'})

        self.assertEqual(stop(s), {})

    def test_near_miss_an_edit_of_a_directive_comment_needs_proof(self) -> None:
        # Comments that change what a tool does are code (DIRECTIVE_PREFIXES).
        changes = (
            ("src/export.py", "# a note", "# type: ignore"),
            ("src/export.py", "total_0 = 0", "total_0 = 0  # noqa: E501"),
            ("src/export.py", "# a note", "# pragma: no cover"),
            ("src/export.py", "# a note", "# pylint: disable=unused-import"),
            ("src/export.py", "# a note", "#!/usr/bin/env python3"),
            ("src/export.py", '    """Return x."""', '    """Return x.\n\n    >>> total()\n    3\n    """'),
            ("src/export.ts", "// a note", "// @ts-ignore"),
            ("src/export.ts", "/* a note */", "/* eslint-disable */"),
            ("src/export.ts", "// a note", '/// <reference path="types.d.ts" />'),
            ("src/export.go", "// a note", "//go:generate stringer"),
            ("src/export.go", "// a note", "// +build linux"),
        )
        for path, old, new in changes:
            with self.subTest(new=new):
                self.session = self.fresh()
                s = self.checked()
                s.call("Edit", {"file_path": path, "old_string": old, "new_string": new})
                self.assertIn("- Proof:", stop(s)["reason"])

    def test_near_miss_a_comment_edit_of_a_file_without_known_comments_needs_proof(self) -> None:
        s = self.checked()
        s.call("Edit", {"file_path": "src/export.lua", "old_string": "-- old",
                        "new_string": "-- new"})

        self.assertIn("- Proof:", stop(s)["reason"])

    def test_a_failed_check_before_a_comment_only_edit_still_asks_for_a_handoff(self) -> None:
        s = self.routed()
        s.say(DESIGN_SKIP)
        s.say(DOC_SKIP)
        s.call("Edit", edit("src/export.py", PLAIN))
        s.run("pytest -q", success=False)
        s.call("Edit", COMMENT_EDITS[0])

        held = stop(s)["reason"]
        self.assertIn("- Unfinished:", held)
        self.assertNotIn("- Proof:", held)

    def test_docs_still_needs_a_change_read_after_a_comment_only_edit(self) -> None:
        s = self.routed()
        s.say(DESIGN_SKIP)
        s.load("doc-sync")
        s.call("Edit", edit("src/export.py", PLAIN))
        s.run(DIFF)
        s.call("Edit", COMMENT_EDITS[0])
        s.run("pytest -q")

        self.assertIn("- Docs:", stop(s)["reason"])
        s.run(DIFF)
        self.assertEqual(stop(s), {})


class BackgroundCheckTests(AdapterTestCase):
    """A check launched in the background is not a check (Ticket 116, O1)."""

    def changed(self) -> Session:
        """A turn that changed code, with Docs and Design skipped: only Proof is left."""

        s = self.routed()
        s.say(DESIGN_SKIP)
        s.say(DOC_SKIP)
        s.call("Write", write("src/export.py"))
        return s

    def background(self, s: Session, command: str = "pytest -q") -> None:
        s.call("Bash", {"command": command, "run_in_background": True})

    def test_a_background_check_does_not_meet_proof_at_the_turns_end(self) -> None:
        s = self.changed()
        self.background(s)

        self.assertIn("- Proof:", stop(s)["reason"])

    def test_a_background_check_does_not_meet_proof_at_a_commit(self) -> None:
        s = self.changed()
        s.load("commit-message")
        s.run(DIFF)
        self.background(s)

        held = s.call("Bash", commit("Add CSV export"))
        self.assertEqual(hold_line(held), CLOSEOUT_HOLD)
        self.assertIn("- Proof:", reason(held))

    def test_near_miss_the_same_check_in_the_foreground_meets_proof(self) -> None:
        s = self.changed()
        s.load("commit-message")
        s.run(DIFF)
        s.run("pytest -q")

        self.assertEqual(decision(s.call("Bash", commit("Add CSV export"))), "pass")
        self.assertEqual(stop(s), {})

    def test_a_check_sent_to_the_background_inside_its_command_still_does_not(self) -> None:
        s = self.changed()
        s.run("cp a.py src/export.py && pytest -q &")

        self.assertIn("- Proof:", stop(s)["reason"])

    def test_a_check_sent_to_the_background_as_its_own_call_does_not_meet_proof(self) -> None:
        s = self.changed()
        s.run("pytest -q &")

        self.assertIn("- Proof:", stop(s)["reason"])

    def test_a_background_call_that_writes_and_checks_does_not_prove_itself(self) -> None:
        s = self.routed()
        s.say(DESIGN_SKIP)
        s.say(DOC_SKIP)
        s.call("Bash", {"command": "cp a.py src/export.py && pytest -q",
                        "run_in_background": True})

        self.assertIn("- Proof:", stop(s)["reason"])

    def test_a_failed_background_check_is_not_read(self) -> None:
        s = self.changed()
        s.call("Bash", {"command": "pytest -q", "run_in_background": True},
               result="Exit code 1\nfailed", failed=True)

        held = stop(s)["reason"]
        self.assertIn("- Proof:", held)
        self.assertNotIn("- Unfinished:", held)

    def test_the_wait_skip_line_clears_proof_while_a_background_check_runs(self) -> None:
        s = self.changed()
        self.background(s)
        s.say("goated-skip: verification-before-completion: the background pytest run")

        self.assertEqual(stop(s), {})

    def test_the_proof_text_names_waiting_on_the_user_and_on_a_background_check(self) -> None:
        s = self.changed()

        held = stop(s)["reason"]
        proof = next(line for line in held.splitlines() if line.startswith("- Proof:"))
        self.assertIn("on the user", proof)
        self.assertIn("on a check running in the background", proof)
        self.assertIn("in the foreground", proof)
        self.assertIn("`goated-skip: verification-before-completion: <what it waits for>`", proof)


class CloseoutAtCommitTests(AdapterTestCase):
    """A commit whose own hold is met is held while closeout items are unmet (Ticket 059)."""

    def changed(self) -> Session:
        """A turn that changed code, loaded commit-message, and read the change: only closeout is left."""

        s = self.routed()
        s.say(DESIGN_SKIP)
        s.call("Write", write("src/export.py"))
        s.load("commit-message")
        s.run(DIFF)
        return s

    def test_a_commit_with_unmet_items_is_held_with_the_closeout_line(self) -> None:
        s = self.changed()

        held = s.call("Bash", commit("Add CSV export"))
        self.assertEqual(hold_line(held), CLOSEOUT_HOLD)
        text = reason(held)
        self.assertIn("- Proof:", text)
        self.assertIn("- Docs:", text)
        self.assertIn("Before committing", text)
        self.assertIn("chained", text)

    def test_meeting_the_items_lets_the_commit_through_and_stop_passes(self) -> None:
        s = self.changed()
        self.assertEqual(hold_line(s.call("Bash", commit("Add CSV export"))), CLOSEOUT_HOLD)

        s.run("pytest -q")
        held = s.call("Bash", commit("Add CSV export"))
        self.assertIn("- Docs:", reason(held))
        self.assertNotIn("- Proof:", reason(held))
        s.say(DOC_SKIP)
        self.assertEqual(decision(s.call("Bash", commit("Add CSV export"))), "pass")
        self.assertEqual(stop(s), {})

    def test_skip_lines_let_the_commit_through(self) -> None:
        s = self.changed()
        s.say(PROOF_SKIP)
        s.say(DOC_SKIP)

        self.assertEqual(decision(s.call("Bash", commit("Add CSV export"))), "pass")
        self.assertEqual(stop(s), {})

    def test_a_commit_tool_is_held_too(self) -> None:
        s = self.changed()
        tool_input = {"message": "Add CSV export", "files": []}

        self.assertEqual(hold_line(s.call("mcp__github__push_files", tool_input)), CLOSEOUT_HOLD)
        s.say(PROOF_SKIP)
        s.say(DOC_SKIP)
        self.assertEqual(decision(s.call("mcp__github__push_files", tool_input)), "pass")

    def test_an_unmet_commit_hold_comes_first_with_the_closeout_beside_it(self) -> None:
        # One held commit names everything it needs (Ticket 120, R4), and the
        # closeout beside it leaves the commit hold's text word for word as it
        # is when the closeout is met.
        bare = self.fresh()
        bare.prompt("Do the task.")
        bare.load(ROUTER)
        bare.say("goated-route: direct")
        bare.say(DESIGN_SKIP)
        bare.call("Write", write("src/export.py"))
        bare.say(PROOF_SKIP)
        bare.say(DOC_SKIP)
        expected = reason(bare.call("Bash", commit("Add CSV export")))
        self.assertTrue(expected.startswith("goated-hold: commit | strict\n"))
        self.assertNotIn(CLOSEOUT_HOLD, expected)

        s = self.routed()
        s.say(DESIGN_SKIP)
        s.call("Write", write("src/export.py"))
        held = reason(s.call("Bash", commit("Add CSV export")))
        commit_part, closeout = held.split(f"\n\n{CLOSEOUT_HOLD}\n", 1)
        self.assertEqual(commit_part, expected)
        self.assertIn("- Proof:", closeout)
        s.load("commit-message")
        s.run(DIFF)
        self.assertEqual(hold_line(s.call("Bash", commit("Add CSV export"))), CLOSEOUT_HOLD)

    def test_a_commit_in_a_turn_with_no_unmet_item_passes(self) -> None:
        s = self.routed()
        s.call("Edit", {"file_path": "README.md", "old_string": "a", "new_string": "b"})
        s.load("commit-message")
        s.read("README.md")

        self.assertEqual(decision(s.call("Bash", commit("Update the readme"))), "pass")

    def test_a_turn_that_never_commits_is_held_at_stop_as_before(self) -> None:
        s = self.routed()
        s.say(DESIGN_SKIP)
        s.call("Write", write("src/export.py"))

        held = stop(s)
        self.assertEqual(closeout_line(held), CLOSEOUT_HOLD)
        self.assertIn("Before finishing this turn, which changed code:", held["reason"])
        self.assertIn("- Proof:", held["reason"])
        s.run("pytest -q")
        s.say(DOC_SKIP)
        self.assertEqual(stop(s), {})

    def test_a_setup_item_holds_the_commit_too(self) -> None:
        s = self.routed()
        s.run("uv add httpx")
        s.load("commit-message")
        s.run(DIFF)

        held = s.call("Bash", commit("Add httpx"))
        self.assertEqual(hold_line(held), CLOSEOUT_HOLD)
        self.assertIn("- Setup:", reason(held))
        s.load("setup-scribe")
        self.assertEqual(decision(s.call("Bash", commit("Add httpx"))), "pass")

    def test_a_subagent_unread_at_commit_is_left_out_with_a_warning(self) -> None:
        s = self.routed()
        s.brief_with_handoff()
        self.assertEqual(decision(s.spawn("gone1", BRIEF)), "pass")  # Its transcript is never written.
        s.load("commit-message")
        s.run(DIFF)

        output = s.call("Bash", commit("Add export"))
        self.assertEqual(decision(output), "pass")
        self.assertIn("could not read the transcript of subagent gone1", output.get("systemMessage", ""))
        self.assertNotIn("subagent", s.call("Bash", {"command": "git status"}).get("systemMessage", ""))

    def subagent_changed(self) -> Session:
        """A subagent that changed code and may commit it, with no proof or docs."""

        s = self.routed()
        s.brief_with_handoff()
        agent = s.subagent("k1")
        agent.prompt("Implement it and commit.", hook=False)
        agent.call("Edit", {"file_path": "src/app.py", "old_string": "a", "new_string": "b"},
                   agent_id="k1", agent_type="general-purpose")
        agent.load("commit-message")
        agent.run("git diff")
        return agent

    def test_a_subagents_commit_meets_the_closeout_of_its_own_turn(self) -> None:
        """Ticket 098: judged from the subagent's own turn, with no override."""

        agent = self.subagent_changed()
        held = agent.call("Bash", commit("Add export"), agent_id="k1", agent_type="general-purpose")
        self.assertEqual(hold_line(held), CLOSEOUT_HOLD)
        self.assertIn("- Proof:", reason(held))
        self.assertIn("- Docs:", reason(held))
        self.assertNotIn("- Review:", reason(held))

    def test_a_subagent_that_proved_and_documented_its_change_commits_freely(self) -> None:
        agent = self.subagent_changed()
        agent.run("pytest -q")
        agent.load("doc-sync")
        agent.run("git diff")

        held = agent.call("Bash", commit("Add export"), agent_id="k1", agent_type="general-purpose")
        self.assertEqual(decision(held), "pass")
