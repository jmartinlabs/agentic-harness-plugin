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

    def assertHarnessError(self):
        errors = check_project(self.root)
        self.assertTrue(any(e.startswith("harness-config:") for e in errors), errors)

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
        config = copy(VALID)
        self.write(config, "hermes.json")
        self.assertHarnessError()

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
        (root / "scripts" / "work-issue").unlink()
        self.assertRule(root, "shims")

    def test_agent_catalogue_drift_is_detected(self):
        names = ("methodology/issue-workflow.md", "skills/work-issue/SKILL.md", "templates/issue.md")
        for name in names:
            root = self.fixture()
            path = root / name
            path.write_text(path.read_text().replace("`hermes`", "`other`").replace("`agent:hermes`", "`agent:other`"))
            found = [e for e in self.problems(root) if e.startswith("agent-catalogue:")]
            self.assertEqual(found, [f"agent-catalogue: {name}: agent catalogue drift, missing hermes"])
        root = self.fixture()
        path = root / "scripts" / "work-issue"
        path.write_text(path.read_text().replace('DEFAULT_AGENTS = ("opencode", "hermes", "codex", "claude")',
                                                 'DEFAULT_AGENTS = ("opencode", "hermes", "codex", "claude", "newone")'))
        found = [e for e in self.problems(root) if e.startswith("agent-catalogue:")]
        self.assertEqual(len(found), 3, found)
        path.write_text(path.read_text().replace("DEFAULT_AGENTS", "OTHER_AGENTS", 1))
        self.assertRule(root, "agent-catalogue")


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
