"""validate-core: plugin integrity checks and the harness JSON v2 schema (ported cases)."""
import json
import runpy
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "validate-core"
CORE = runpy.run_path(str(SCRIPT))
check_project = CORE["check_project_harnesses"]

VALID = {"version": 2, "external": {
    "codex": {"enabled": True, "transport": "cli", "model": None, "effort": None,
              "tasks": {"review": "automatic", "investigate": "on_request", "develop": "disabled"}},
    "opencode": {"enabled": True, "transport": "cli", "model": None, "effort": None,
                 "tasks": {"review": "on_request", "investigate": "on_request", "develop": "disabled"}}}}


def copy(value):
    return json.loads(json.dumps(value))


class HarnessCase(unittest.TestCase):
    """Cases ported from the template's test-validator (harness-config rule only)."""

    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        (self.root / ".agents" / "harnesses").mkdir(parents=True)
        self.write(VALID)

    def write(self, config, name="claude.json"):
        text = config if isinstance(config, str) else json.dumps(config)
        (self.root / ".agents" / "harnesses" / name).write_text(text)

    def assertHarnessError(self, expected=None):
        errors = check_project(self.root)
        self.assertTrue(any(e.startswith("harness-config:") for e in errors), errors)
        if expected is not None:
            self.assertTrue(any(expected in e for e in errors), (expected, errors))

    def test_valid_file_has_no_problems(self):
        self.assertEqual(check_project(self.root), [])

    def test_a_project_without_harnesses_has_no_problems(self):
        with tempfile.TemporaryDirectory() as empty:
            self.assertEqual(check_project(empty), [])

    # ported: test_external_agents_rejects_invalid_values
    def test_rejects_invalid_values(self):
        def broken(mutate):
            config = copy(VALID)
            mutate(config)
            self.write(config)
            self.assertHarnessError()
        broken(lambda c: c.update(version=1))
        broken(lambda c: c["external"]["codex"].update(transport="mcp"))
        broken(lambda c: c["external"]["codex"]["tasks"].update(investigate="automatic"))
        broken(lambda c: c["external"]["codex"]["tasks"].update(develop="automatic"))
        broken(lambda c: c["external"]["codex"]["tasks"].update(review="sometimes"))
        broken(lambda c: c["external"]["codex"]["tasks"].update(refactor="on_request"))
        broken(lambda c: c["external"]["codex"].update(model=""))
        broken(lambda c: c["external"]["codex"].update(provider="openai"))
        self.write("{not json")
        self.assertHarnessError()

    # ported: test_external_agents_has_no_closed_client_list
    def test_has_no_closed_client_list(self):
        config = copy(VALID)
        config["external"]["newclient"] = {"enabled": False, "transport": "cli", "model": None,
                                           "effort": None, "tasks": {"review": "on_request"}}
        self.write(config)
        self.assertEqual(check_project(self.root), [])

    # ported: test_v2_harness_rejects_legacy_and_checks_all_files
    def test_rejects_legacy_and_checks_all_files(self):
        legacy = self.root / ".agents" / "external-agents.json"
        legacy.write_text("{}")
        self.assertHarnessError()
        legacy.unlink()
        self.write(VALID, "codex.json")  # Claude's standing permission cannot travel.
        self.assertHarnessError()
        self.write('{"version":2}', "codex.json")
        self.assertEqual(check_project(self.root), [])
        other = self.root / ".agents" / "harnesses"
        (other / "codex.json").rename(other / "unknown.json")
        self.assertHarnessError()

    # ported: test_v2_harness_checks_native_profiles_and_duplicate_keys
    def test_checks_native_profiles_and_duplicate_keys(self):
        config = copy(VALID)
        profiles = {
            "functional": {"standard": {"effort": "low"}, "complex": {"effort": "high"}},
            "implementation": {"standard": {"effort": "low"}, "complex": {"model": None, "effort": "high"}},
            "qa-review": {"standard": {"model": "review-model"}, "complex": {"effort": "high"}},
            "infrastructure": {"standard": {"effort": "low"}, "complex": {"effort": "high"}},
        }
        config["local"] = {"model": "example", "profiles": profiles}
        self.write(config)
        self.assertEqual(check_project(self.root), [])
        del profiles["functional"]
        del profiles["qa-review"]["complex"]
        self.write(config)
        self.assertEqual(check_project(self.root), [])
        for role, level, profile in (("review", "standard", {"effort": "low"}),
                                     ("qa-review", "urgent", {"effort": "high"}),
                                     ("implementation", "complex", {"model": None, "effort": None}),
                                     ("infrastructure", "standard", {})):
            with self.subTest(role=role, level=level):
                invalid = {**config, "local": {**config["local"], "profiles": {role: {level: profile}}}}
                self.write(invalid)
                self.assertHarnessError()
        for raw in ('{"version":2,"version":2}', "null", '{"version":2.0}'):
            with self.subTest(raw=raw):
                self.write(raw)
                self.assertHarnessError()

    # new (not in the baseline): the checker's own extra guards
    def test_nan_constants_and_symlinks_outside_the_project_are_rejected(self):
        self.write('{"version":2,"local":{"model":NaN}}')
        self.assertHarnessError()
        outside = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False)
        self.addCleanup(Path(outside.name).unlink)
        outside.write('{"version":2}')
        outside.close()
        link = self.root / ".agents" / "harnesses" / "codex.json"
        link.symlink_to(outside.name)
        self.write(VALID)
        self.assertHarnessError()

    def test_automatic_is_only_claude_to_codex_review(self):
        for name in ("hermes.json", "antigravity.json"):
            with self.subTest(name=name):
                config = copy(VALID)
                self.write(config, name)
                self.assertHarnessError()
                (self.root / ".agents" / "harnesses" / name).unlink()

    def test_antigravity_v2_harness_is_accepted(self):
        config = {
            "version": 2,
            "local": {
                "model": None,
                "effort": None,
                "profiles": {
                    "qa-review": {"standard": {"model": "flash"}, "complex": {"model": "pro"}},
                },
            },
            "external": {},
        }
        self.write(config, "antigravity.json")
        self.assertEqual(check_project(self.root), [])

    def test_cli_project_reports_the_files_and_exit_codes(self):
        ok = subprocess.run([sys.executable, str(SCRIPT), "--project", str(self.root)],
                            capture_output=True, text=True)
        self.assertEqual(ok.returncode, 0, ok.stdout)
        self.assertIn("claude.json", ok.stdout)
        self.write("{not json")
        bad = subprocess.run([sys.executable, str(SCRIPT), "--project", str(self.root)],
                             capture_output=True, text=True)
        self.assertEqual(bad.returncode, 1)
        self.assertIn("harness-config: claude.json", bad.stdout)
        missing = subprocess.run([sys.executable, str(SCRIPT), "--project", str(self.root / "nope")],
                                 capture_output=True, text=True)
        self.assertEqual(missing.returncode, 2)

    def test_t3_host_config_valid_versioned_local_and_profiles(self):
        versioned = {
            "version": 2,
            "local": {
                "provider": "antigravity",
                "model": "gemini-4-hydrogen",
                "effort": "medium",
                "profiles": {
                    "qa-review": {"provider": "opencode", "model": "alibaba-token-plan/glm-5.3", "effort": "low"},
                    "review": {"provider": "codex", "model": "gpt-6.1-terra", "effort": "low"},
                },
            },
        }
        self.write(versioned, "t3.json")
        self.assertEqual(check_project(self.root), [])

        local = {
            "version": 2,
            "local": {
                "profiles": {
                    "functional": {"provider": "antigravity", "model": "gemini-4-hydrogen"},
                    "implementation": {
                        "standard": {"provider": "antigravity", "model": "gemini-4-hydrogen", "effort": "medium"},
                        "complex": {"provider": "codex", "model": "gpt-6.1-terra", "effort": "high"},
                    },
                    "qa-review": {
                        "standard": {"provider": "opencode", "model": "alibaba-token-plan/deepseek-v4.1-flash-1017", "effort": "low"},
                        "complex": {"provider": "opencode", "model": "alibaba-token-plan/glm-5.3"},
                    },
                    "infrastructure": {"provider": "antigravity", "model": "gemini-4-hydrogen", "effort": "low"},
                    "review": {"provider": "codex", "model": "gpt-6.1-terra"},
                },
            },
        }
        self.write(local, "t3.local.json")
        self.assertEqual(check_project(self.root), [])

        for local_defaults in (
            {"provider": "antigravity", "model": "gemini-4-hydrogen"},
            {"provider": "antigravity", "model": "gemini-4-hydrogen", "effort": "medium"},
        ):
            with self.subTest(local_defaults=local_defaults):
                self.write({"version": 2, "local": local_defaults}, "t3.local.json")
                self.assertEqual(check_project(self.root), [])

    def test_t3_host_config_rejects_invalid_schemas_and_paths(self):
        base = {
            "version": 2,
            "local": {
                "provider": "antigravity",
                "model": "gemini-4-hydrogen",
                "effort": "medium",
                "profiles": {
                    "qa-review": {"provider": "opencode", "model": "alibaba-token-plan/glm-5.3", "effort": "low"},
                },
            },
        }
        invalid_cases = [
            (lambda c: c.update(version=1), "version must be integer 2"),
            (lambda c: c.update(version=2.0), "version must be integer 2"),
            (lambda c: c.update(external={}), "config: unknown field external"),
            (lambda c: c["local"].update(unknown="x"), "local: unknown field unknown"),
            (lambda c: c["local"].pop("model"), "local: provider and model are required when setting defaults"),
            (lambda c: c["local"].pop("provider"), "local: provider and model are required when setting defaults"),
            (lambda c: c.update(local={"effort": "low"}), "local: provider and model are required when setting defaults"),
            (lambda c: c.update(local={"provider": "antigravity"}), "local: provider and model are required when setting defaults"),
            (lambda c: c.update(local={"model": "gemini-4-hydrogen"}), "local: provider and model are required when setting defaults"),
            (lambda c: c["local"].update(provider="1bad"), "local.provider: must match"),
            (lambda c: c["local"].update(provider="bad provider"), "local.provider: must match"),
            (lambda c: c["local"]["profiles"].update({"unknown-role": {"provider": "codex", "model": "m"}}),
             "local.profiles: unknown field unknown-role"),
            (lambda c: c["local"]["profiles"].update({"review": {"standard": {"provider": "codex", "model": "m"}}}),
             "local.profiles.review: unknown field standard"),
            (lambda c: c["local"]["profiles"].update({"qa-review": {"provider": "opencode"}}),
             "local.profiles.qa-review: provider and model are required"),
            (lambda c: c["local"]["profiles"].update({"qa-review": {"model": "glm-5.3"}}),
             "local.profiles.qa-review: provider and model are required"),
            (lambda c: c["local"]["profiles"].update({"qa-review": {"provider": "opencode", "model": ""}}),
             "local.profiles.qa-review.model: must be null or a non-empty string"),
            (lambda c: c["local"]["profiles"].update({"qa-review": {"provider": "", "model": "glm-5.3"}}),
             "local.profiles.qa-review.provider: must match"),
            (lambda c: c["local"]["profiles"].update({"qa-review": {"urgent": {"provider": "opencode", "model": "m"}}}),
             "local.profiles.qa-review: unknown field urgent"),
        ]
        for index, (mutate, expected) in enumerate(invalid_cases):
            with self.subTest(case=index, expected=expected):
                config = copy(base)
                mutate(config)
                self.write(config, "t3.json")
                self.assertHarnessError(expected)

        outside = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False)
        self.addCleanup(Path(outside.name).unlink)
        outside.write('{"version":2}')
        outside.close()
        (self.root / ".agents" / "harnesses" / "t3.json").unlink()
        (self.root / ".agents" / "harnesses" / "t3.json").symlink_to(outside.name)
        self.assertHarnessError("invalid host file: t3.json")

    def test_cli_harness_file_validates_only_target_file(self):
        self.write("{not json", "claude.json")
        self.write({"version": 2, "local": {"provider": "antigravity", "model": "gemini-4-hydrogen"}}, "t3.json")
        ok = subprocess.run(
            [sys.executable, str(SCRIPT), "--project", str(self.root), "--harness-file", ".agents/harnesses/t3.json"],
            capture_output=True, text=True,
        )
        self.assertEqual(ok.returncode, 0, ok.stdout)
        self.assertIn("t3.json", ok.stdout)

        bad_local = {"version": 2, "local": {"profiles": {"review": {"standard": {"provider": "codex", "model": "m"}}}}}
        self.write(bad_local, "t3.local.json")
        bad = subprocess.run(
            [sys.executable, str(SCRIPT), "--project", str(self.root), "--harness-file", ".agents/harnesses/t3.local.json"],
            capture_output=True, text=True,
        )
        self.assertEqual(bad.returncode, 1)
        self.assertIn("harness-config: t3.local.json:", bad.stdout)

        missing = subprocess.run(
            [sys.executable, str(SCRIPT), "--project", str(self.root), "--harness-file", ".agents/harnesses/missing.json"],
            capture_output=True, text=True,
        )
        self.assertEqual(missing.returncode, 1)
        self.assertIn("harness-config:", missing.stdout)

        no_project = subprocess.run(
            [sys.executable, str(SCRIPT), "--harness-file", str(self.root / ".agents" / "harnesses" / "t3.json")],
            capture_output=True, text=True,
        )
        self.assertEqual(no_project.returncode, 2)
        self.assertIn("--harness-file requires --project", no_project.stderr)

        outside = tempfile.NamedTemporaryFile("w", suffix=".json", prefix="t3-", delete=False)
        self.addCleanup(Path(outside.name).unlink)
        outside.write('{"version":2}')
        outside.close()
        outside_abs = subprocess.run(
            [sys.executable, str(SCRIPT), "--project", str(self.root), "--harness-file", outside.name],
            capture_output=True, text=True,
        )
        self.assertEqual(outside_abs.returncode, 1)
        self.assertIn("harness-config: invalid coordinator filename:", outside_abs.stdout)

        outside_named_dir = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, outside_named_dir)
        outside_t3 = outside_named_dir / "t3.json"
        outside_t3.write_text('{"version":2}')
        outside_host = subprocess.run(
            [sys.executable, str(SCRIPT), "--project", str(self.root), "--harness-file", str(outside_t3)],
            capture_output=True, text=True,
        )
        self.assertEqual(outside_host.returncode, 1)
        self.assertIn("harness-config: invalid host file: t3.json", outside_host.stdout)

        (self.root / ".agents" / "harnesses" / "t3.json").unlink()
        (self.root / ".agents" / "harnesses" / "t3.json").symlink_to(outside_t3)
        symlink_escape = subprocess.run(
            [sys.executable, str(SCRIPT), "--project", str(self.root), "--harness-file", ".agents/harnesses/t3.json"],
            capture_output=True, text=True,
        )
        self.assertEqual(symlink_escape.returncode, 1)
        self.assertIn("harness-config: invalid host file: t3.json", symlink_escape.stdout)


class PluginCase(unittest.TestCase):
    def fixture(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name) / "plugin"
        shutil.copytree(ROOT, root, ignore=shutil.ignore_patterns(".git", "__pycache__"))
        return root

    def problems(self, root):
        return CORE["validate_plugin"](root)

    def test_the_real_plugin_validates(self):
        self.assertEqual(self.problems(ROOT), [])
        proc = subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stdout)

    def assertRule(self, root, rule):
        found = self.problems(root)
        self.assertTrue(any(e.startswith(rule + ":") for e in found), (rule, found))

    def test_manifest_drift_is_detected(self):
        root = self.fixture()
        path = root / ".antigravity-plugin" / "plugin.json"
        data = json.loads(path.read_text())
        data["version"] = "9.9.9"
        path.write_text(json.dumps(data))
        self.assertRule(root, "manifest")

    def test_marketplace_name_must_be_shared_across_versions(self):
        for relative in (".claude-plugin/marketplace.json", ".agents/plugins/marketplace.json"):
            with self.subTest(path=relative):
                root = self.fixture()
                path = root / relative
                data = json.loads(path.read_text())
                data["name"] = "agentic-harness-1-1-0"
                path.write_text(json.dumps(data))
                self.assertRule(root, "manifest")

    def test_provenance_hash_and_unlisted_file_are_detected(self):
        root = self.fixture()
        (root / "roles" / "qa-review.md").write_text("changed\n")
        self.assertRule(root, "provenance")
        root = self.fixture()
        (root / "templates" / "extra.md").write_text("new\n")
        self.assertRule(root, "provenance")

    def test_hook_over_budget_is_detected(self):
        root = self.fixture()
        with (root / "skills" / "orchestrate" / "SKILL.md").open("a") as stream:
            stream.write("x" * 9000)
        self.assertRule(root, "hook")

    def test_frontmatter_problems_are_detected(self):
        root = self.fixture()
        path = root / "agents" / "qa-review.md"
        path.write_text(path.read_text().replace("model: inherit", "model: opus"))
        self.assertRule(root, "frontmatter")
        root = self.fixture()
        path = root / "skills" / "dev" / "SKILL.md"
        path.write_text(path.read_text().replace("name: dev", "name: other", 1))
        self.assertRule(root, "frontmatter")

    def test_broken_link_and_anchor_are_detected(self):
        root = self.fixture()
        with (root / "README.md").open("a") as stream:
            stream.write("\n[x](methodology/nope.md)\n[y](methodology/approvals.md#no-such-heading)\n")
        found = self.problems(root)
        self.assertTrue(any("nope.md" in e for e in found), found)
        self.assertTrue(any("no such heading" in e for e in found), found)

    def test_missing_shim_or_exec_bit_is_detected(self):
        root = self.fixture()
        (root / "bin" / "agentic-relay").chmod(0o644)
        self.assertRule(root, "shims")
        root = self.fixture()
        (root / "scripts" / "agent-relay").unlink()
        self.assertRule(root, "shims")

    def test_agent_catalogue_drift_is_detected(self):
        names = ("methodology/issue-workflow.md", "skills/work-issue/SKILL.md", "templates/issue.md")
        for name in names:
            root = self.fixture()
            path = root / name
            path.write_text(path.read_text().replace("`hermes`", "`other`").replace("`agent:hermes`", "`agent:other`"))
            found = [e for e in self.problems(root) if e.startswith("agent-catalogue:")]
            self.assertEqual(found, [f"agent-catalogue: {name}: agent catalogue drift, missing hermes"])

    def test_secret_scan_detects_tokens_and_keys(self):
        root = self.fixture()
        (root / "README.md").write_text("token = ghp_1234567890abcdefghij123456\n", encoding="utf-8")
        self.assertRule(root, "secrets")

    def test_neutrality_scan_detects_local_user_paths(self):
        root = self.fixture()
        (root / "README.md").write_text("see /Users/alice/projects/foo\n", encoding="utf-8")
        self.assertRule(root, "neutrality")

    def test_git_diff_check_detects_whitespace_errors(self):
        root = self.fixture()
        subprocess.run(["git", "init", "-q"], cwd=root, check=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=root, check=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=root, check=True)
        subprocess.run(["git", "add", "README.md"], cwd=root, check=True)
        subprocess.run(["git", "commit", "-q", "-m", "init"], cwd=root, check=True)
        (root / "README.md").write_text("trailing whitespace   \n", encoding="utf-8")
        self.assertRule(root, "git-diff")

    def test_required_phrases_drift_is_detected(self):
        root = self.fixture()
        path = root / "roles" / "implementation.md"
        path.write_text(path.read_text(encoding="utf-8").replace("$task", "$other"), encoding="utf-8")
        self.assertRule(root, "required-phrases")


class IndependentCoverage(PluginCase):
    """Direct checks of the shared helpers' effects, without the test_plugin helpers."""

    def test_link_checker_catches_a_broken_relative_link_in_a_copy(self):
        root = self.fixture()
        (root / "roles" / "README.md").write_text("[gone](missing-file.md)\n", encoding="utf-8")
        errors = CORE["check_links"](root.resolve())
        self.assertTrue(any("missing-file.md" in e for e in errors), errors)
        self.assertEqual(CORE["check_links"](ROOT), [])

    def test_provenance_mismatch_is_detected_after_modifying_a_copied_file(self):
        root = self.fixture()
        self.assertEqual(CORE["check_provenance"](root.resolve()), [])
        path = root / "methodology" / "approvals.md"
        path.write_bytes(path.read_bytes() + b"\nextra\n")
        errors = CORE["check_provenance"](root.resolve())
        self.assertTrue(any("methodology/approvals.md" in e and "sha256" in e for e in errors), errors)

    def test_hook_budget_exceeded_is_detected(self):
        root = self.fixture()
        self.assertEqual(CORE["check_hook"](root.resolve()), [])
        with (root / "skills" / "orchestrate" / "SKILL.md").open("a") as stream:
            stream.write("y" * (CORE["HOOK_PRINT_BUDGET"] + 1))
        errors = CORE["check_hook"](root.resolve())
        self.assertTrue(any("budget" in e for e in errors), errors)


if __name__ == "__main__":
    unittest.main()
