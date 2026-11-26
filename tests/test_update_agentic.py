"""Isolated unit tests for scripts/update-agentic (stdlib only, no network, no AI quota)."""

from __future__ import annotations

import json
import runpy
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "update-agentic"
MOD = runpy.run_path(str(SCRIPT))

CommandResult = MOD["CommandResult"]
run_all = MOD["run_all"]
format_report = MOD["format_report"]
main = MOD["main"]


def _write_manifest(root: Path, version: str, rel: str = ".claude-plugin/plugin.json") -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"name": "agentic", "version": version}), encoding="utf-8")


def _setup_shared_harnesses(home: Path, shared_repo: Path, version: str = "1.2.0") -> None:
    (shared_repo / ".git").mkdir(parents=True, exist_ok=True)
    _write_manifest(shared_repo, version, ".claude-plugin/plugin.json")
    _write_manifest(shared_repo, version, ".antigravity-plugin/plugin.json")
    skill_dir = shared_repo / "skills" / "verify-project"
    skill_dir.mkdir(parents=True, exist_ok=True)

    # OpenCode symlink into shared repo
    oc_skills = home / ".config" / "opencode" / "skills"
    oc_skills.mkdir(parents=True, exist_ok=True)
    (oc_skills / "verify-project").symlink_to(skill_dir)

    # Hermes symlink into shared repo
    hermes_skills = home / ".hermes" / "skills"
    hermes_skills.mkdir(parents=True, exist_ok=True)
    (hermes_skills / "verify-project").symlink_to(skill_dir)

    # Antigravity symlink into shared repo
    ag_parent = home / ".gemini" / "config" / "plugins"
    ag_parent.mkdir(parents=True, exist_ok=True)
    (ag_parent / "agentic").symlink_to(shared_repo)


class UpdateAgenticTests(unittest.TestCase):
    def test_check_mode_is_strictly_read_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp) / "home"
            shared_repo = home / ".local" / "share" / "agentic-harness-plugin"
            _setup_shared_harnesses(home, shared_repo, version="1.2.1")

            commands: list[list[str]] = []

            def fake_runner(cmd):
                commands.append(list(cmd))
                if cmd[:3] == ["claude", "plugin", "list"]:
                    return CommandResult(
                        0,
                        json.dumps([{"id": "agentic@agentic-harness", "version": "1.2.1"}]),
                    )
                if cmd[:3] == ["codex", "plugin", "list"]:
                    return CommandResult(0, "agentic@agentic-harness  1.2.1\n")
                raise AssertionError(f"Unexpected mutating or unknown command in --check: {cmd}")

            results = run_all(
                check_only=True,
                home=home,
                env={"AGENTIC_SHARED_REPO": str(shared_repo)},
                runner=fake_runner,
                which=lambda name: f"/usr/bin/{name}",
            )

            by_name = {r.harness: r for r in results}
            for name in ("claude-code", "codex", "opencode", "hermes", "antigravity"):
                self.assertEqual(by_name[name].status, "installed", name)
                self.assertEqual(by_name[name].version_before, "1.2.1", name)

            # Verify no mutating commands were invoked
            for cmd in commands:
                self.assertNotIn("update", cmd)
                self.assertNotIn("upgrade", cmd)
                self.assertNotIn("pull", cmd)
                self.assertNotIn("install", cmd)

    def test_missing_harnesses_reported_not_installed_and_never_installed(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp) / "home"
            home.mkdir()
            commands: list[list[str]] = []

            def fake_runner(cmd):
                commands.append(list(cmd))
                return CommandResult(1, "", "should not be called")

            results = run_all(
                check_only=False,
                home=home,
                env={},
                runner=fake_runner,
                which=lambda _name: None,
            )

            self.assertEqual(commands, [])
            for res in results:
                self.assertEqual(res.status, "not-installed", res.harness)

    def test_shared_git_repo_updated_only_once_across_multiple_harnesses(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp) / "home"
            shared_repo = home / ".local" / "share" / "agentic-harness-plugin"
            _setup_shared_harnesses(home, shared_repo, version="1.2.0")

            pull_calls = 0
            sha_state = {"sha": "aaaa111"}

            def fake_runner(cmd):
                nonlocal pull_calls
                if cmd[:2] == ["git", "-C"] and cmd[3:5] == ["rev-parse", "HEAD"]:
                    return CommandResult(0, sha_state["sha"] + "\n")
                if cmd[:2] == ["git", "-C"] and cmd[3:7] == ["pull", "--ff-only", "origin", "stable"]:
                    pull_calls += 1
                    sha_state["sha"] = "bbbb222"
                    _write_manifest(shared_repo, "1.2.1", ".claude-plugin/plugin.json")
                    _write_manifest(shared_repo, "1.2.1", ".antigravity-plugin/plugin.json")
                    return CommandResult(0, "Updating aaaa111..bbbb222\n")
                raise AssertionError(f"Unexpected command: {cmd}")

            results = run_all(
                check_only=False,
                home=home,
                env={"AGENTIC_SHARED_REPO": str(shared_repo)},
                runner=fake_runner,
                which=lambda _name: None,
            )

            self.assertEqual(pull_calls, 1)
            by_name = {r.harness: r for r in results}
            for name in ("opencode", "hermes", "antigravity"):
                self.assertEqual(by_name[name].status, "updated", name)
                self.assertEqual(by_name[name].version_before, "1.2.0", name)
                self.assertEqual(by_name[name].version_after, "1.2.1", name)
            self.assertEqual(by_name["claude-code"].status, "not-installed")
            self.assertEqual(by_name["codex"].status, "not-installed")

    def test_distinguishes_updated_up_to_date_not_installed_and_error_with_fault_isolation(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp) / "home"
            shared_repo = home / ".local" / "share" / "agentic-harness-plugin"
            (shared_repo / ".git").mkdir(parents=True, exist_ok=True)
            _write_manifest(shared_repo, "1.2.1", ".claude-plugin/plugin.json")
            skill_dir = shared_repo / "skills" / "verify-project"
            skill_dir.mkdir(parents=True, exist_ok=True)
            oc_skills = home / ".config" / "opencode" / "skills"
            oc_skills.mkdir(parents=True, exist_ok=True)
            (oc_skills / "verify-project").symlink_to(skill_dir)

            # Standalone non-git Antigravity install
            ag_dir = home / ".gemini" / "config" / "plugins" / "agentic"
            _write_manifest(ag_dir, "1.2.1", ".antigravity-plugin/plugin.json")

            codex_list_calls = 0

            def fake_runner(cmd):
                nonlocal codex_list_calls
                # Claude Code fails during marketplace update
                if cmd[:3] == ["claude", "plugin", "list"]:
                    return CommandResult(0, json.dumps([{"id": "agentic@agentic-harness", "version": "1.2.0"}]))
                if cmd[:4] == ["claude", "plugin", "marketplace", "update"]:
                    return CommandResult(1, "", "network timeout")

                # Codex updates from 1.2.0 -> 1.2.1
                if cmd[:3] == ["codex", "plugin", "list"]:
                    codex_list_calls += 1
                    ver = "1.2.0" if codex_list_calls == 1 else "1.2.1"
                    return CommandResult(0, f"agentic@agentic-harness  {ver}\n")
                if cmd[:4] == ["codex", "plugin", "marketplace", "upgrade"]:
                    return CommandResult(0, "upgraded agentic-harness\n")

                # Shared repo (OpenCode) is already up-to-date
                if cmd[:2] == ["git", "-C"] and cmd[3:5] == ["rev-parse", "HEAD"]:
                    return CommandResult(0, "cccc333\n")
                if cmd[:2] == ["git", "-C"] and cmd[3:7] == ["pull", "--ff-only", "origin", "stable"]:
                    return CommandResult(0, "Already up to date.\n")

                raise AssertionError(f"Unexpected command: {cmd}")

            results = run_all(
                check_only=False,
                home=home,
                env={"AGENTIC_SHARED_REPO": str(shared_repo)},
                runner=fake_runner,
                which=lambda name: f"/usr/bin/{name}",
            )

            by_name = {r.harness: r for r in results}
            self.assertEqual(by_name["claude-code"].status, "error")
            self.assertIn("network timeout", by_name["claude-code"].detail)
            self.assertEqual(by_name["codex"].status, "updated")
            self.assertEqual(by_name["codex"].version_before, "1.2.0")
            self.assertEqual(by_name["codex"].version_after, "1.2.1")
            self.assertEqual(by_name["opencode"].status, "up-to-date")
            self.assertEqual(by_name["hermes"].status, "not-installed")
            self.assertEqual(by_name["antigravity"].status, "up-to-date")
            self.assertIn("skipped auto-reinstall", by_name["antigravity"].detail)

            report = format_report(results, check_only=False)
            self.assertIn("1.2.0 -> 1.2.1", report)
            self.assertIn("error", report)
            self.assertIn("not-installed", report)
            self.assertIn("up-to-date", report)


if __name__ == "__main__":
    unittest.main()
