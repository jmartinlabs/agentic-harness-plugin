"""Static checks for the moved plugin assets (stdlib only, no network, no client)."""
import hashlib
import json
import os
import re
import runpy
import subprocess
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASELINE = "e9a46160753c5e61f7d3291da9e6a0299f840aa0"
HOOK_PRINT_BUDGET = 8704
ASSET_DIRS = ("skills", "methodology", "roles", "agents", "templates")
CLASSES = {"copy", "link-rewrite", "path-reword", "deliberate-delta"}


def plugin_markdown():
    return [path for path in sorted(ROOT.rglob("*.md"))
            if path.relative_to(ROOT).parts[0] not in (".git", "tests")]


CORE = runpy.run_path(str(ROOT / "scripts" / "validate-core"))
prose_lines = CORE["prose_lines"]
slugs = CORE["slugs"]
frontmatter = CORE["frontmatter"]
git_blob_sha = CORE["git_blob_sha"]


def provenance_rows():
    return CORE["provenance_rows"](ROOT)


class LinkTests(unittest.TestCase):
    def test_relative_links_and_anchors_resolve_inside_plugin(self):
        files = plugin_markdown()
        self.assertGreater(len(files), 30)
        checked = 0
        for path in files:
            for number, line in prose_lines(path.read_text(encoding="utf-8")):
                for target in re.findall(r"\]\(([^)\s]+)\)", line):
                    if re.match(r"^[a-z][a-z0-9+.-]*:", target):
                        continue
                    name, _, anchor = target.partition("#")
                    destination = path if not name else (path.parent / name).resolve()
                    where = f"{path.relative_to(ROOT)}:{number}: {target}"
                    self.assertTrue(destination.is_relative_to(ROOT), f"{where} leaves the plugin")
                    self.assertTrue(destination.exists(), f"{where} does not exist")
                    if anchor:
                        self.assertTrue(destination.is_file() and destination.suffix == ".md", where)
                        self.assertIn(anchor, slugs(destination), f"{where}: no such heading")
                    checked += 1
        self.assertGreater(checked, 50)


class ProvenanceTests(unittest.TestCase):
    def test_every_moved_file_is_listed_and_hashes_match(self):
        rows = provenance_rows()
        self.assertGreaterEqual(len(rows), 39)
        listed = {row[2] for row in rows}
        self.assertEqual(len(listed), len(rows), "duplicate destination")
        for source, blob, destination, digest, klass in rows:
            with self.subTest(destination=destination):
                self.assertIn(klass, CLASSES)
                self.assertRegex(blob, r"^[0-9a-f]{40}$")
                data = (ROOT / destination).read_bytes()
                self.assertEqual(hashlib.sha256(data).hexdigest(), digest)
                if klass == "copy":
                    self.assertEqual(git_blob_sha(data), blob)
        for directory in ASSET_DIRS:
            for path in (ROOT / directory).rglob("*"):
                relative = path.relative_to(ROOT).as_posix()
                if path.is_file() and relative != "skills/verify-project/SKILL.md":
                    self.assertIn(relative, listed, f"{relative} is not in PROVENANCE.md")

    def test_copy_files_equal_template_baseline_when_available(self):
        template = os.environ.get("AGENTIC_TEMPLATE_CHECKOUT")
        if not template:
            self.skipTest("AGENTIC_TEMPLATE_CHECKOUT not set; template baseline not compared")
        probe = subprocess.run(["git", "-C", template, "cat-file", "-e", f"{BASELINE}^{{commit}}"],
                               capture_output=True)
        if probe.returncode != 0:
            self.skipTest(f"{template} has no commit {BASELINE}; template baseline not compared")
        for source, _, destination, _, klass in provenance_rows():
            if klass != "copy":
                continue
            with self.subTest(destination=destination):
                original = subprocess.run(["git", "-C", template, "show", f"{BASELINE}:{source}"],
                                          capture_output=True, check=True).stdout
                self.assertEqual((ROOT / destination).read_bytes(), original)


# (file, exact text) -> expected occurrences. A new occurrence fails until justified here.
PATH_PATTERN = re.compile(
    r"\.agents/skills|\.agents/roles|\.claude/skills|\.claude/agents|specs/methodology"
    r"|(?<![\w.])\.codex(?!\w)|(?<![\w.])\.opencode/|scripts/")
ALLOWED_PATHS = {
    # The tools ship in scripts/ since this increment; the verbatim methodology text keeps the template path.
    ("methodology/document-ownership.md", "scripts/"): 1,
    ("methodology/issue-workflow.md", "scripts/"): 3,
    ("skills/relay/GITHUB_API.md", "scripts/"): 2,
    ("skills/work-issue/SKILL.md", "scripts/"): 2,
    ("skills/relay/SKILL.md", "scripts/"): 1,
    # adopt-project runs the plugin's own scripts/verify-project.py to list plugin-owned copies in the project.
    ("skills/adopt-project/SKILL.md", "scripts/"): 2,
    # The plugin's own validator (validate-core) named in the v2 schema sentence (deliberate delta).
    ("methodology/dynamic-agents.md", "scripts/"): 1,
    # Derived-project CI path families and examples of a project's own harness (project-owned).
    ("methodology/ci-policy.md", "scripts/"): 3,
    ("methodology/ci-policy.md", "specs/methodology"): 1,
    # Reworded sentence naming a template-only document that is not part of the plugin.
    ("methodology/document-ownership.md", "specs/methodology"): 1,
}


class PathTests(unittest.TestCase):
    def test_plugin_owned_paths_are_not_used_as_project_paths(self):
        found = Counter()
        for directory in ("skills", "methodology", "roles", "agents"):
            for path in sorted((ROOT / directory).rglob("*.md")):
                relative = path.relative_to(ROOT).as_posix()
                if relative == "skills/verify-project/SKILL.md":
                    continue
                for match in PATH_PATTERN.findall(path.read_text(encoding="utf-8")):
                    found[(relative, match)] += 1
        self.assertEqual(dict(found), ALLOWED_PATHS)


class HookTests(unittest.TestCase):
    def test_hook_prints_one_plugin_file_within_budget(self):
        config = json.loads((ROOT / "hooks/hooks.json").read_text(encoding="utf-8"))
        self.assertEqual(list(config), ["hooks"])
        self.assertEqual(list(config["hooks"]), ["SessionStart"])
        (group,) = config["hooks"]["SessionStart"]
        (hook,) = group["hooks"]
        self.assertEqual(hook["type"], "command")
        match = re.fullmatch(r'cat "\$\{CLAUDE_PLUGIN_ROOT\}/(skills/orchestrate/SKILL\.md)" 2>/dev/null \|\| true',
                             hook["command"])
        self.assertIsNotNone(match, hook["command"])
        printed = ROOT / match.group(1)
        self.assertTrue(printed.is_file())
        self.assertLessEqual(printed.stat().st_size, HOOK_PRINT_BUDGET)


class FrontmatterTests(unittest.TestCase):
    def test_skills_name_matches_directory_and_description_present(self):
        skills = sorted((ROOT / "skills").glob("*/SKILL.md"))
        self.assertEqual(len(skills), 13)
        for path in skills:
            with self.subTest(skill=path.parent.name):
                fields = frontmatter(path)
                self.assertEqual(fields.get("name"), path.parent.name)
                self.assertTrue(fields.get("description"))

    def test_agents_carry_no_hooks_permissions_or_mcp_and_use_plugin_role_path(self):
        agents = sorted((ROOT / "agents").glob("*.md"))
        self.assertEqual([path.stem for path in agents],
                         ["functional", "implementation", "infrastructure", "qa-review"])
        for path in agents:
            with self.subTest(agent=path.stem):
                fields = frontmatter(path)
                self.assertEqual(fields.get("name"), path.stem)
                self.assertTrue(fields.get("description"))
                self.assertEqual(fields.get("model"), "inherit")
                for forbidden in ("hooks", "permissionMode", "mcpServers"):
                    self.assertNotIn(forbidden, fields)
                self.assertIn(f"${{CLAUDE_PLUGIN_ROOT}}/roles/{path.stem}.md", path.read_text(encoding="utf-8"))
                self.assertTrue((ROOT / "roles" / f"{path.stem}.md").is_file())


if __name__ == "__main__":
    unittest.main()
