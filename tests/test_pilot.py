import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIXTURES = ROOT / "tests/fixtures"


class PilotTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.sandbox = Path(temp.name).resolve()
        self.bundle = self.sandbox / "installed"
        self.bundle.mkdir()
        for name in ("scripts", "methodology", "roles", "skills"):
            shutil.copytree(ROOT / name, self.bundle / name)
        shutil.copyfile(ROOT / "plugin.json", self.bundle / "plugin.json")
        self.projects = self.sandbox / "projects"
        shutil.copytree(FIXTURES, self.projects)

    def invoke(self, cwd, *arguments):
        return subprocess.run(
            [sys.executable, str(self.bundle / "scripts/verify-project.py"), *arguments],
            cwd=cwd, capture_output=True, text=True, check=False,
        )

    def test_manifest_identity_and_portable_skill(self):
        manifests = [json.loads((ROOT / path).read_text()) for path in (
            "plugin.json", ".claude-plugin/plugin.json", ".antigravity-plugin/plugin.json",
        )]
        self.assertEqual({item["name"] for item in manifests}, {"agentic"})
        self.assertEqual(len({item["version"] for item in manifests}), 1)
        for manifest in manifests:
            self.assertRegex(manifest["version"], r"^\d+\.\d+\.\d+$")
            self.assertTrue(manifest["description"].strip())
        self.assertEqual(manifests[0]["$schema"], "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json")
        self.assertTrue(manifests[1]["author"]["name"].strip())
        self.assertEqual(manifests[2]["$schema"], "https://antigravity.google/schemas/v1/plugin.json")
        self.assertTrue(manifests[2]["displayName"].strip())
        self.assertTrue((self.bundle / "skills/verify-project/SKILL.md").is_file())

    def test_marketplaces_target_the_same_packaged_root(self):
        claude = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text())
        codex = json.loads((ROOT / ".agents/plugins/marketplace.json").read_text())
        self.assertEqual(codex["plugins"][0]["source"]["source"], "local")
        for market, source in ((claude, claude["plugins"][0]["source"]),
                               (codex, codex["plugins"][0]["source"]["path"])):
            self.assertEqual([entry["name"] for entry in market["plugins"]], ["agentic"])
            self.assertEqual((ROOT / source).resolve(), ROOT)

    def test_readiness_uses_different_roots_and_single_config_candidate(self):
        a, b = self.projects / "a", self.projects / "b"
        subdirectory = a / "src" / "nested"
        subdirectory.mkdir(parents=True)
        for cwd, coordinator, project in ((a, "claude", a), (subdirectory, "claude", a), (b, "codex", b)):
            with self.subTest(cwd=cwd):
                result = self.invoke(cwd, "--coordinator", coordinator)
                self.assertEqual(result.returncode, 0, result.stderr)
                report = json.loads(result.stdout)
                self.assertEqual(report["project_root"], str(project))
                self.assertEqual(report["artifact_root"], str(self.bundle))
                self.assertEqual(report["project_rules"], str(project / "specs/project-rules.md"))
                self.assertEqual(report["approval_policy"], str(self.bundle / "methodology/approvals.md"))
                self.assertEqual(report["qa_role"], str(self.bundle / "roles/qa-review.md"))
                self.assertEqual(
                    report["coordinator_config_candidate"],
                    str(project / ".agents/harnesses" / f"{coordinator}.json"),
                )
        result = self.invoke(a, "--coordinator", "codex")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIsNone(json.loads(result.stdout)["coordinator_config_candidate"])

    def test_explicit_missing_rules_and_unrelated_project(self):
        a = self.projects / "a"
        (a / "specs/project-rules.md").unlink()
        result = self.invoke(self.sandbox, "--project", str(a))
        self.assertEqual(result.returncode, 2)
        self.assertIn("project-rules.md: absent", result.stderr)
        result = self.invoke(self.projects / "unrelated")
        self.assertEqual(result.returncode, 2)
        self.assertIn("no project", result.stderr)

    def test_git_root_precedes_nested_entries_and_rejects_escaped_entry(self):
        a = self.projects / "a"
        (a / ".git").mkdir()
        nested = a / "nested"
        (nested / "specs").mkdir(parents=True)
        for entry in ("AGENTS.md", "CLAUDE.md", "specs/project-rules.md"):
            (nested / entry).write_text("Nested decoy", encoding="utf-8")
        result = self.invoke(nested)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["project_root"], str(a))
        (a / "AGENTS.md").unlink()
        (a / "AGENTS.md").symlink_to(self.projects / "b" / "AGENTS.md")
        result = self.invoke(nested)
        self.assertEqual(result.returncode, 2)
        self.assertIn("AGENTS.md: points outside", result.stderr)

    def test_outside_rules_and_nested_checkout_do_not_cross_roots(self):
        a = self.projects / "a"
        nested = a / "nested-checkout"
        (nested / ".git").mkdir(parents=True)
        self.assertEqual(self.invoke(nested).returncode, 2)
        rules = a / "specs/project-rules.md"
        rules.unlink()
        rules.symlink_to(self.projects / "b" / "specs/project-rules.md")
        result = self.invoke(a)
        self.assertEqual(result.returncode, 2)
        self.assertIn("outside its root", result.stderr)


if __name__ == "__main__":
    unittest.main()
