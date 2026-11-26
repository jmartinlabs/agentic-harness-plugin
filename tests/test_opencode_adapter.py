"""Tests for the packaged OpenCode global adapter (stdlib only, offline)."""
import json
import os
import runpy
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ADAPTER = ROOT / "adapters" / "opencode"
AGENTS_DIR = ADAPTER / "agents"
PLUGIN_INDEX = ADAPTER / "plugins" / "review-read" / "index.ts"
REVIEW_READ = ADAPTER / "scripts" / "review-read"

CORE = runpy.run_path(str(ROOT / "scripts" / "validate-core"))
frontmatter = CORE["frontmatter"]

EXPECTED_AGENTS = {
    "functional": "functional.md",
    "implementation": "implementation.md",
    "infrastructure": "infrastructure.md",
    "qa": "qa-review.md",
    "review": "qa-review.md",
}


class OpenCodeAdapterPackagingTests(unittest.TestCase):
    def test_expected_files_exist_and_wrapper_is_executable(self):
        self.assertTrue(AGENTS_DIR.is_dir())
        self.assertTrue(PLUGIN_INDEX.is_file())
        self.assertTrue(REVIEW_READ.is_file())
        self.assertTrue(os.access(REVIEW_READ, os.X_OK), "review-read must be executable")
        self.assertFalse((ADAPTER / "opencode.json").exists(),
                         "adapter must not ship personal/provider model config")

    def test_agents_are_thin_native_subagents_pointing_to_canonical_roles(self):
        found = sorted(p.stem for p in AGENTS_DIR.glob("*.md"))
        self.assertEqual(found, sorted(EXPECTED_AGENTS))
        for name, role_file in EXPECTED_AGENTS.items():
            path = AGENTS_DIR / f"{name}.md"
            text = path.read_text(encoding="utf-8")
            with self.subTest(agent=name):
                fields = frontmatter(path)
                self.assertEqual(fields.get("mode"), "subagent")
                self.assertTrue(fields.get("description"))
                self.assertNotIn("model", fields)
                self.assertIn(f"../../../roles/{role_file}", text)
                self.assertTrue((ROOT / "roles" / role_file).is_file())

    def test_review_and_qa_permissions_enforce_read_only_boundaries(self):
        review_text = (AGENTS_DIR / "review.md").read_text(encoding="utf-8")
        self.assertIn("action: review_query", review_text)
        self.assertIn("effect: deny", review_text)
        qa_text = (AGENTS_DIR / "qa.md").read_text(encoding="utf-8")
        self.assertIn('resource: "*.env"', qa_text)
        self.assertIn('resource: "*.env.*"', qa_text)

    def test_plugin_resolves_wrapper_relative_to_plugin_not_project(self):
        source = PLUGIN_INDEX.read_text(encoding="utf-8")
        self.assertIn("realpathSync(fileURLToPath(import.meta.url))", source)
        self.assertIn('"scripts"', source)
        self.assertIn('"review-read"', source)
        self.assertNotIn('join(directory, "scripts/review-read")', source)


class OpenCodeReviewReadRuntimeTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.project = Path(temp.name).resolve()
        (self.project / "notes.txt").write_text("hello from project\n", encoding="utf-8")
        (self.project / ".env").write_text("SECRET=1\n", encoding="utf-8")
        (self.project / ".env.example").write_text("EXAMPLE=1\n", encoding="utf-8")

    def run_wrapper(self, *args):
        return subprocess.run(
            [sys.executable, str(REVIEW_READ), *args],
            cwd=str(self.project),
            capture_output=True,
            text=True,
        )

    def test_describe_returns_valid_policy_json(self):
        proc = self.run_wrapper("describe")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        policy = json.loads(proc.stdout)
        self.assertEqual(policy["version"], 1)
        self.assertIn("git", policy)
        self.assertIn("github", policy)
        self.assertIn("file", policy)

    def test_file_read_uses_active_project_cwd_and_blocks_protected_files(self):
        ok = self.run_wrapper("file", "read", "--path", "notes.txt")
        self.assertEqual(ok.returncode, 0, ok.stderr)
        self.assertEqual(ok.stdout, "hello from project\n")

        example = self.run_wrapper("file", "read", "--path", ".env.example")
        self.assertEqual(example.returncode, 0, example.stderr)
        self.assertEqual(example.stdout, "EXAMPLE=1\n")

        secret = self.run_wrapper("file", "read", "--path", ".env")
        self.assertEqual(secret.returncode, 2)
        self.assertIn("protected", secret.stderr.lower())

        escape = self.run_wrapper("file", "read", "--path", "../escape.txt")
        self.assertEqual(escape.returncode, 2)


if __name__ == "__main__":
    unittest.main()
