"""bin/ shims start every tool and write nothing. Stdlib only, offline."""
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
SHIMS = ("agentic-relay", "agentic-check-delegation-route",
         "agentic-usage-report", "agentic-usage-auto", "agentic-verify-project")
TOOLS = ("agent-relay", "check-delegation-route", "report-agent-usage", "auto-agent-usage",
         "verify-project.py")


class TempCase(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.tmp = Path(temp.name).resolve()

    def project(self, name):
        path = self.tmp / name
        path.mkdir()
        return path


class ShimTests(TempCase):
    def test_every_shim_is_a_small_executable_posix_sh(self):
        self.assertEqual(sorted(p.name for p in (ROOT / "bin").iterdir()), sorted(SHIMS))
        for name in SHIMS:
            path = ROOT / "bin" / name
            self.assertTrue(os.access(path, os.X_OK), name)
            lines = path.read_text(encoding="utf-8").splitlines()
            self.assertEqual(lines[0], "#!/bin/sh")
            self.assertEqual(len(lines), 3, name)
            self.assertIn("exec python3", lines[2])

    def test_help_exits_zero_and_writes_nothing(self):
        for name in SHIMS:
            project = self.project("p-" + name)
            before = sorted(project.rglob("*"))
            proc = subprocess.run([str(ROOT / "bin" / name), "--help"], cwd=str(project),
                                  capture_output=True, text=True, stdin=subprocess.DEVNULL)
            with self.subTest(shim=name):
                self.assertEqual(proc.returncode, 0, proc.stderr)
                self.assertIn("usage", (proc.stdout + proc.stderr).lower())
                self.assertEqual(before, sorted(project.rglob("*")))

    def test_a_symlinked_shim_still_finds_its_script(self):
        link = self.tmp / "linked"
        link.symlink_to(ROOT / "bin" / "agentic-relay")
        proc = subprocess.run([str(link), "--help"], cwd=str(self.tmp), capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)

    def test_each_shim_targets_a_shipped_tool(self):
        for name, tool in zip(SHIMS, TOOLS):
            with self.subTest(shim=name):
                self.assertIn(f"/../scripts/{tool}", (ROOT / "bin" / name).read_text(encoding="utf-8"))
                self.assertTrue((SCRIPTS / tool).is_file())


if __name__ == "__main__":
    unittest.main()
