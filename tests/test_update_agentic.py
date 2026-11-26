"""Isolated unit tests for scripts/update-agentic (stdlib only, no network, no AI quota)."""

from __future__ import annotations

import json
import runpy
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "update-agentic"
MOD = runpy.run_path(str(SCRIPT))

CommandResult = MOD["CommandResult"]
default_runner = MOD["default_runner"]
run_all = MOD["run_all"]
format_report = MOD["format_report"]
main = MOD["main"]

VALID_ORIGIN = "https://github.com/jmartinlabs/agentic-harness-plugin.git"


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

    oc_skills = home / ".config" / "opencode" / "skills"
    oc_skills.mkdir(parents=True, exist_ok=True)
    (oc_skills / "verify-project").symlink_to(skill_dir)

    hermes_skills = home / ".hermes" / "skills"
    hermes_skills.mkdir(parents=True, exist_ok=True)
    (hermes_skills / "verify-project").symlink_to(skill_dir)

    ag_parent = home / ".gemini" / "config" / "plugins"
    ag_parent.mkdir(parents=True, exist_ok=True)
    (ag_parent / "agentic").symlink_to(shared_repo)


def _write_codex_config(codex_home: Path, enabled: bool = True, version: str | None = None) -> None:
    codex_home.mkdir(parents=True, exist_ok=True)
    lines = ['[plugins."agentic@agentic-harness"]', f"enabled = {'true' if enabled else 'false'}"]
    if version is not None:
        lines.append(f'version = "{version}"')
    (codex_home / "config.toml").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _setup_codex_manifest(codex_home: Path, version: str = "1.2.0", write_config: bool = True) -> Path:
    if write_config:
        _write_codex_config(codex_home, enabled=True)
    plugin_root = codex_home / "plugins" / "cache" / "agentic-harness" / "agentic" / version
    _write_manifest(plugin_root, version, ".codex-plugin/plugin.json")
    return plugin_root


class UpdateAgenticTests(unittest.TestCase):
    def test_check_mode_is_strictly_read_only_and_never_calls_codex_plugin_list(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp) / "home"
            shared_repo = home / ".local" / "share" / "agentic-harness-plugin"
            codex_home = home / ".codex"
            _setup_shared_harnesses(home, shared_repo, version="1.2.1")
            _setup_codex_manifest(codex_home, version="1.2.1")

            commands: list[tuple[list[str], str | None]] = []

            def fake_runner(cmd, cwd, timeout):
                commands.append((list(cmd), cwd))
                if cmd[:3] == ["claude", "plugin", "list"]:
                    return CommandResult(
                        0, json.dumps([{"id": "agentic@agentic-harness", "version": "1.2.1"}])
                    )
                raise AssertionError(f"Unexpected command in --check: {cmd}")

            results = run_all(
                check_only=True,
                home=home,
                env={"AGENTIC_SHARED_REPO": str(shared_repo), "CODEX_HOME": str(codex_home)},
                runner=fake_runner,
                which=lambda name: f"/usr/bin/{name}",
            )

            by_name = {r.harness: r for r in results}
            for name in ("claude-code", "codex", "opencode", "hermes", "antigravity"):
                self.assertEqual(by_name[name].status, "installed", name)
                self.assertEqual(by_name[name].version_before, "1.2.1", name)

            # Confirm codex plugin list was never called and claude ran from home (outside any project)
            self.assertEqual(len(commands), 1)
            self.assertEqual(commands[0][0], ["claude", "plugin", "list", "--json"])
            self.assertEqual(commands[0][1], str(home))

    def test_missing_harnesses_reported_not_installed_and_never_installed(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp) / "home"
            home.mkdir()
            commands: list[list[str]] = []

            def fake_runner(cmd, cwd, timeout):
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

    def test_shared_git_repo_updated_only_once_after_verifying_branch_and_origin(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp) / "home"
            shared_repo = home / ".local" / "share" / "agentic-harness-plugin"
            _setup_shared_harnesses(home, shared_repo, version="1.2.0")

            pull_calls = 0
            sha_state = {"sha": "aaaa111"}

            def fake_runner(cmd, cwd, timeout):
                nonlocal pull_calls
                if cmd[3:6] == ["rev-parse", "--abbrev-ref", "HEAD"]:
                    return CommandResult(0, "stable\n")
                if cmd[3:6] == ["remote", "get-url", "origin"]:
                    return CommandResult(0, "git@github.com:jmartinlabs/agentic-harness-plugin.git\n")
                if cmd[3:5] == ["rev-parse", "HEAD"]:
                    return CommandResult(0, sha_state["sha"] + "\n")
                if cmd[3:7] == ["pull", "--ff-only", "origin", "stable"]:
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

    def test_shared_repo_wrong_branch_and_wrong_origin_rejected_without_pull(self):
        for case, branch_out, origin_out, expected_err in (
            ("wrong-branch", "main\n", VALID_ORIGIN + "\n", "expected branch 'stable'"),
            ("wrong-origin", "stable\n", "https://github.com/other/fork.git\n", "unexpected origin URL"),
        ):
            with self.subTest(case=case), tempfile.TemporaryDirectory() as tmp:
                home = Path(tmp) / "home"
                shared_repo = home / ".local" / "share" / "agentic-harness-plugin"
                _setup_shared_harnesses(home, shared_repo, version="1.2.0")

                def fake_runner(cmd, cwd, timeout):
                    if cmd[3:6] == ["rev-parse", "--abbrev-ref", "HEAD"]:
                        return CommandResult(0, branch_out)
                    if cmd[3:6] == ["remote", "get-url", "origin"]:
                        return CommandResult(0, origin_out)
                    if "pull" in cmd:
                        raise AssertionError("git pull must not run when branch or origin is invalid")
                    raise AssertionError(f"Unexpected command: {cmd}")

                results = run_all(
                    check_only=False,
                    home=home,
                    env={"AGENTIC_SHARED_REPO": str(shared_repo)},
                    runner=fake_runner,
                    which=lambda _name: None,
                )
                by_name = {r.harness: r for r in results}
                for name in ("opencode", "hermes", "antigravity"):
                    self.assertEqual(by_name[name].status, "error", name)
                    self.assertIn(expected_err, by_name[name].detail, name)

    def test_statuses_skipped_unverified_error_timeout_and_cwd_outside_project(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp) / "home"
            shared_repo = home / ".local" / "share" / "agentic-harness-plugin"
            codex_home = home / ".codex"
            codex_root = _setup_codex_manifest(codex_home, version="1.2.0")

            # OpenCode uses shared repo (up-to-date)
            (shared_repo / ".git").mkdir(parents=True, exist_ok=True)
            _write_manifest(shared_repo, "1.2.1", ".claude-plugin/plugin.json")
            skill_dir = shared_repo / "skills" / "verify-project"
            skill_dir.mkdir(parents=True, exist_ok=True)
            oc_skills = home / ".config" / "opencode" / "skills"
            oc_skills.mkdir(parents=True, exist_ok=True)
            (oc_skills / "verify-project").symlink_to(skill_dir)

            # Standalone non-git Antigravity install -> skipped
            ag_dir = home / ".gemini" / "config" / "plugins" / "agentic"
            _write_manifest(ag_dir, "1.2.1", ".antigravity-plugin/plugin.json")

            cwds: dict[str, list[str | None]] = {"claude": [], "codex": []}

            def fake_runner(cmd, cwd, timeout):
                if cmd[0] == "claude":
                    cwds["claude"].append(cwd)
                    if cmd[:3] == ["claude", "plugin", "list"]:
                        return CommandResult(0, json.dumps([{"id": "agentic@agentic-harness", "version": "1.2.0"}]))
                    if cmd[:4] == ["claude", "plugin", "marketplace", "update"]:
                        return CommandResult(124, "", f"command timed out after {timeout}s")
                if cmd[0] == "codex":
                    cwds["codex"].append(cwd)
                    self.assertNotEqual(cmd[:3], ["codex", "plugin", "list"])
                    if cmd[:4] == ["codex", "plugin", "marketplace", "upgrade"]:
                        _write_manifest(codex_root, "1.2.1", ".codex-plugin/plugin.json")
                        return CommandResult(0, "upgraded\n")
                if cmd[0] == "git":
                    if cmd[3:6] == ["rev-parse", "--abbrev-ref", "HEAD"]:
                        return CommandResult(0, "stable\n")
                    if cmd[3:6] == ["remote", "get-url", "origin"]:
                        return CommandResult(0, VALID_ORIGIN + "\n")
                    if cmd[3:5] == ["rev-parse", "HEAD"]:
                        return CommandResult(0, "cccc333\n")
                    if cmd[3:7] == ["pull", "--ff-only", "origin", "stable"]:
                        return CommandResult(0, "Already up to date.\n")
                raise AssertionError(f"Unexpected command: {cmd}")

            results = run_all(
                check_only=False,
                home=home,
                env={"AGENTIC_SHARED_REPO": str(shared_repo), "CODEX_HOME": str(codex_home)},
                runner=fake_runner,
                which=lambda name: f"/usr/bin/{name}",
                timeout=15,
            )

            by_name = {r.harness: r for r in results}
            self.assertEqual(by_name["claude-code"].status, "error")
            self.assertIn("timed out after 15s", by_name["claude-code"].detail)
            self.assertEqual(by_name["codex"].status, "updated")
            self.assertEqual(by_name["codex"].version_before, "1.2.0")
            self.assertEqual(by_name["codex"].version_after, "1.2.1")
            self.assertEqual(by_name["opencode"].status, "up-to-date")
            self.assertEqual(by_name["hermes"].status, "not-installed")
            self.assertEqual(by_name["antigravity"].status, "skipped")
            self.assertIn("skipped auto-reinstall", by_name["antigravity"].detail)

            self.assertTrue(cwds["claude"])
            self.assertTrue(cwds["codex"])
            self.assertTrue(all(c == str(home) for c in cwds["claude"]))
            self.assertTrue(all(c == str(home) for c in cwds["codex"]))

            report = format_report(results, check_only=False)
            self.assertIn("1.2.0 -> 1.2.1", report)
            self.assertIn("skipped", report)

    def test_unverified_version_after_update_reports_error_not_success(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp) / "home"
            codex_home = home / ".codex"
            codex_root = _setup_codex_manifest(codex_home, version="1.2.0")

            def fake_runner(cmd, cwd, timeout):
                if cmd[:4] == ["codex", "plugin", "marketplace", "upgrade"]:
                    # Corrupt manifest so post-upgrade version cannot be verified
                    (codex_root / ".codex-plugin" / "plugin.json").write_text("{}", encoding="utf-8")
                    return CommandResult(0, "ok\n")
                raise AssertionError(f"Unexpected command: {cmd}")

            results = run_all(
                check_only=False,
                home=home,
                env={"CODEX_HOME": str(codex_home)},
                runner=fake_runner,
                which=lambda name: "/usr/bin/codex" if name == "codex" else None,
            )
            by_name = {r.harness: r for r in results}
            self.assertEqual(by_name["codex"].status, "error")
            self.assertIn("could not verify version", by_name["codex"].detail)

    def test_unknown_before_version_with_valid_after_version_reports_error_not_updated(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp) / "home"
            codex_home = home / ".codex"
            _write_codex_config(codex_home, enabled=True)
            codex_root = codex_home / "plugins" / "cache" / "agentic-harness" / "agentic" / "1.2.0"
            manifest = codex_root / ".codex-plugin" / "plugin.json"
            manifest.parent.mkdir(parents=True, exist_ok=True)
            manifest.write_text(json.dumps({"name": "agentic"}), encoding="utf-8")

            def fake_runner(cmd, cwd, timeout):
                if cmd[:4] == ["codex", "plugin", "marketplace", "upgrade"]:
                    _setup_codex_manifest(codex_home, version="1.2.1", write_config=False)
                    return CommandResult(0, "ok\n")
                raise AssertionError(f"Unexpected command: {cmd}")

            results = run_all(
                check_only=False,
                home=home,
                env={"CODEX_HOME": str(codex_home)},
                runner=fake_runner,
                which=lambda name: "/usr/bin/codex" if name == "codex" else None,
            )
            by_name = {r.harness: r for r in results}
            self.assertEqual(by_name["codex"].status, "error")
            self.assertIn("before/after", by_name["codex"].detail)

    def test_codex_multi_version_cache_ignores_marketplace_and_respects_config_enabled(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp) / "home"
            codex_home = home / ".codex"

            # Coexisting cached versions (including 1.10.0 > 1.2.1 numeric SemVer) + decoy 9.9.9 in marketplaces/
            _setup_codex_manifest(codex_home, version="1.1.0", write_config=False)
            _setup_codex_manifest(codex_home, version="1.2.0", write_config=False)
            _setup_codex_manifest(codex_home, version="1.2.1", write_config=False)
            _write_manifest(
                codex_home / "marketplaces" / "agentic-harness",
                "9.9.9",
                ".codex-plugin/plugin.json",
            )

            # 1. Missing config.toml -> not-installed even though cache & marketplace exist
            res_missing = {
                r.harness: r
                for r in run_all(
                    check_only=True,
                    home=home,
                    env={"CODEX_HOME": str(codex_home)},
                    runner=lambda *_: (_ for _ in ()).throw(AssertionError("unexpected call")),
                    which=lambda name: "/usr/bin/codex" if name == "codex" else None,
                )
            }
            self.assertEqual(res_missing["codex"].status, "not-installed")

            # 2. enabled = false -> not-installed
            _write_codex_config(codex_home, enabled=False)
            res_disabled = {
                r.harness: r
                for r in run_all(
                    check_only=True,
                    home=home,
                    env={"CODEX_HOME": str(codex_home)},
                    runner=lambda *_: (_ for _ in ()).throw(AssertionError("unexpected call")),
                    which=lambda name: "/usr/bin/codex" if name == "codex" else None,
                )
            }
            self.assertEqual(res_disabled["codex"].status, "not-installed")

            # 3. enabled = true -> picks highest SemVer in cache (1.2.1), ignores marketplace 9.9.9
            _write_codex_config(codex_home, enabled=True)
            res_highest = {
                r.harness: r
                for r in run_all(
                    check_only=True,
                    home=home,
                    env={"CODEX_HOME": str(codex_home)},
                    runner=lambda *_: (_ for _ in ()).throw(AssertionError("unexpected call")),
                    which=lambda name: "/usr/bin/codex" if name == "codex" else None,
                )
            }
            self.assertEqual(res_highest["codex"].status, "installed")
            self.assertEqual(res_highest["codex"].version_before, "1.2.1")

            # 4. Numeric SemVer beats lexicographic order (1.10.0 > 1.2.1)
            _setup_codex_manifest(codex_home, version="1.10.0", write_config=False)
            res_semver = {
                r.harness: r
                for r in run_all(
                    check_only=True,
                    home=home,
                    env={"CODEX_HOME": str(codex_home)},
                    runner=lambda *_: (_ for _ in ()).throw(AssertionError("unexpected call")),
                    which=lambda name: "/usr/bin/codex" if name == "codex" else None,
                )
            }
            self.assertEqual(res_semver["codex"].version_before, "1.10.0")

            # 5. Explicit version in config.toml selects that exact cached version
            _write_codex_config(codex_home, enabled=True, version="1.2.0")
            res_pinned = {
                r.harness: r
                for r in run_all(
                    check_only=True,
                    home=home,
                    env={"CODEX_HOME": str(codex_home)},
                    runner=lambda *_: (_ for _ in ()).throw(AssertionError("unexpected call")),
                    which=lambda name: "/usr/bin/codex" if name == "codex" else None,
                )
            }
            self.assertEqual(res_pinned["codex"].status, "installed")
            self.assertEqual(res_pinned["codex"].version_before, "1.2.0")

    def test_default_runner_handles_timeout_expired(self):
        with mock.patch("subprocess.run", side_effect=subprocess.TimeoutExpired(["claude"], 5)) as mock_run:
            res = default_runner(["claude"], cwd="/tmp", timeout=5)
        self.assertEqual(mock_run.call_args.kwargs["timeout"], 5)
        self.assertEqual(res.returncode, 124)
        self.assertIn("timed out after 5s", res.stderr)

    def test_hermes_check_reports_profiles_without_plugin_skills_read_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp) / "home"
            shared_repo = home / ".local" / "share" / "agentic-harness-plugin"
            hermes_home = home / ".hermes"
            _setup_shared_harnesses(home, shared_repo, version="1.2.2")

            # CA2: profile with valid symlink to shared_repo -> should NOT be reported
            good_skills = hermes_home / "profiles" / "good-profile" / "skills"
            good_skills.mkdir(parents=True, exist_ok=True)
            (good_skills / "verify-project").symlink_to(shared_repo / "skills" / "verify-project")

            # CA4: profile with foreign homonymous work-issue (local dir, not plugin symlink) -> reported
            eng_skills = hermes_home / "profiles" / "engineering-lead" / "skills" / "work-issue"
            eng_skills.mkdir(parents=True, exist_ok=True)
            (eng_skills / "SKILL.md").write_text("# local work-issue\n", encoding="utf-8")

            # CA4 variant: profile with symlink to unrelated directory -> reported
            other_skill = Path(tmp) / "unrelated-skills" / "work-issue"
            other_skill.mkdir(parents=True, exist_ok=True)
            ext_skills = hermes_home / "profiles" / "external-link" / "skills"
            ext_skills.mkdir(parents=True, exist_ok=True)
            (ext_skills / "work-issue").symlink_to(other_skill)

            # CA3: profile without skills/ directory -> reported explicitly as missing skills/
            no_skills_prof = hermes_home / "profiles" / "no-skills-prof"
            no_skills_prof.mkdir(parents=True, exist_ok=True)
            cfg_file = no_skills_prof / "config.yaml"
            cfg_file.write_text("model: default\n", encoding="utf-8")

            # Non-directory entry under profiles/ should be ignored
            (hermes_home / "profiles" / ".DS_Store").write_text("", encoding="utf-8")

            # Hidden profile directory without skills/ -> should be reported
            hidden_prof = hermes_home / "profiles" / ".hidden-prof"
            hidden_prof.mkdir(parents=True, exist_ok=True)

            # Profile linked to ANOTHER checkout with "agentic-harness-plugin" in the path -> reported
            other_checkout_skill = Path(tmp) / "other" / "agentic-harness-plugin" / "skills" / "verify-project"
            other_checkout_skill.mkdir(parents=True, exist_ok=True)
            other_co_skills = hermes_home / "profiles" / "other-checkout" / "skills"
            other_co_skills.mkdir(parents=True, exist_ok=True)
            (other_co_skills / "verify-project").symlink_to(other_checkout_skill)

            # Symlink inside shared_repo but outside skills/ -> reported
            outside_skills = shared_repo / "roles"
            outside_skills.mkdir(parents=True, exist_ok=True)
            (outside_skills / "implementation.md").write_text("# role\n", encoding="utf-8")
            non_skill_link_dir = hermes_home / "profiles" / "non-skill-link" / "skills"
            non_skill_link_dir.mkdir(parents=True, exist_ok=True)
            (non_skill_link_dir / "implementation.md").symlink_to(outside_skills / "implementation.md")

            before_tree = sorted(str(p.relative_to(hermes_home)) for p in hermes_home.rglob("*"))

            def forbid_runner(cmd, cwd, timeout):
                raise AssertionError(f"Unexpected command in --check: {cmd}")

            results = run_all(
                check_only=True,
                home=home,
                env={"AGENTIC_SHARED_REPO": str(shared_repo), "HERMES_HOME": str(hermes_home)},
                runner=forbid_runner,
                which=lambda _name: None,
            )

            by_name = {r.harness: r for r in results}
            hermes_res = by_name["hermes"]
            self.assertEqual(hermes_res.status, "installed")
            self.assertEqual(hermes_res.version_before, "1.2.2")
            self.assertIn("profiles without shared-checkout plugin skills:", hermes_res.detail)
            self.assertIn("engineering-lead", hermes_res.detail)
            self.assertIn("external-link", hermes_res.detail)
            self.assertIn("other-checkout", hermes_res.detail)
            self.assertIn("non-skill-link", hermes_res.detail)
            self.assertIn(".hidden-prof (missing skills/)", hermes_res.detail)
            self.assertIn("no-skills-prof (missing skills/)", hermes_res.detail)
            self.assertNotIn("good-profile", hermes_res.detail)
            self.assertNotIn(".DS_Store", hermes_res.detail)

            report = format_report(results, check_only=True)
            self.assertIn("profiles without shared-checkout plugin skills:", report)
            self.assertIn("engineering-lead", report)
            self.assertIn(".hidden-prof (missing skills/)", report)
            self.assertIn("no-skills-prof (missing skills/)", report)
            self.assertNotIn("good-profile", report)

            # CA5: verify strictly read-only (no files/dirs/symlinks created, config.yaml untouched)
            after_tree = sorted(str(p.relative_to(hermes_home)) for p in hermes_home.rglob("*"))
            self.assertEqual(before_tree, after_tree)
            self.assertFalse((no_skills_prof / "skills").exists())
            self.assertEqual(cfg_file.read_text(encoding="utf-8"), "model: default\n")

    def test_hermes_absent_shared_repo_with_profiles_skips_profile_warning(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp) / "home"
            shared_repo = home / ".local" / "share" / "agentic-harness-plugin"  # does not exist
            hermes_home = home / ".hermes"
            (hermes_home / "profiles" / "engineering-lead" / "skills" / "work-issue").mkdir(parents=True)

            results = run_all(
                check_only=True,
                home=home,
                env={"AGENTIC_SHARED_REPO": str(shared_repo), "HERMES_HOME": str(hermes_home)},
                runner=lambda *_: (_ for _ in ()).throw(AssertionError("unexpected call")),
                which=lambda _name: None,
            )
            by_name = {r.harness: r for r in results}
            self.assertEqual(by_name["hermes"].status, "not-installed")
            self.assertEqual(by_name["hermes"].detail, "no agentic symlinks found")

    def test_hermes_without_profiles_preserves_existing_result_and_exit_code(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp) / "home"
            shared_repo = home / ".local" / "share" / "agentic-harness-plugin"
            hermes_home = home / ".hermes"
            _setup_shared_harnesses(home, shared_repo, version="1.2.2")

            with mock.patch.dict(
                "os.environ",
                {"HOME": str(home), "AGENTIC_SHARED_REPO": str(shared_repo), "HERMES_HOME": str(hermes_home)},
                clear=True,
            ), mock.patch.object(MOD["shutil"], "which", return_value=None):
                # Capture stdout and verify exit code 0 and unchanged detail
                results = run_all(
                    check_only=True,
                    home=home,
                    env={"AGENTIC_SHARED_REPO": str(shared_repo), "HERMES_HOME": str(hermes_home)},
                    runner=lambda *_: (_ for _ in ()).throw(AssertionError("unexpected call")),
                    which=lambda _name: None,
                )
                by_name = {r.harness: r for r in results}
                self.assertEqual(by_name["hermes"].status, "installed")
                self.assertEqual(by_name["hermes"].detail, f"shared repo: {shared_repo}")
                with mock.patch("builtins.print"):
                    exit_code = main(["--check"])
                self.assertEqual(exit_code, 0)


if __name__ == "__main__":
    unittest.main()
