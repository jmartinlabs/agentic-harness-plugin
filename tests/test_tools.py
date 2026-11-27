"""Ported tools read project data from the working directory, never from the tool's own directory.
Stdlib only, offline."""
import json
import os
import runpy
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
SESSION = "11111111-1111-1111-1111-111111111111"
TURN = "33333333-3333-3333-3333-333333333333"


def git(*args, cwd):
    subprocess.run(["git", *args], cwd=str(cwd), check=True, capture_output=True)


class TempCase(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.tmp = Path(temp.name).resolve()

    def project(self, name):
        path = self.tmp / name
        path.mkdir()
        return path


class RelayAndUsageProjectData(TempCase):
    def test_agent_relay_takes_the_repository_from_the_working_directory(self):
        api = runpy.run_path(str(SCRIPTS / "agent-relay"))
        repo = self.project("repo")
        git("init", "-q", cwd=repo)
        plain = self.project("plain")
        old = Path.cwd()
        try:
            os.chdir(repo)
            self.assertEqual(Path(api["repo_root"]()).resolve(), repo)
            os.chdir(plain)
            with self.assertRaises(Exception):
                api["repo_root"]()
        finally:
            os.chdir(old)
        self.assertNotIn("__file__", (SCRIPTS / "agent-relay").read_text(encoding="utf-8"))

    def write_session(self, logs):
        logs.mkdir()
        record = {"type": "token_usage_record", "payload": {
            "session_id": SESSION, "thread_id": SESSION, "root_turn_id": TURN, "turn_id": TURN,
            "response_id": "r1", "usage": {"input_tokens": 100, "cached_input_tokens": 80,
                                           "output_tokens": 10}}}
        (logs / "rollout.jsonl").write_text(json.dumps(record) + "\n")

    def test_usage_report_names_the_output_after_the_working_directory(self):
        project = self.project("projx")
        home = self.tmp / "home"
        logs = self.tmp / "logs"
        self.write_session(logs)
        before = sorted(p.name for p in ROOT.iterdir())
        proc = subprocess.run([sys.executable, str(SCRIPTS / "report-agent-usage"), "--session", SESSION,
                               "--sessions-dir", str(logs)], cwd=str(project), capture_output=True,
                              text=True, env={**os.environ, "CODEX_HOME": str(home)})
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(len(list((home / "usage-reports" / "projx").rglob("usage.md"))), 1)
        self.assertEqual(before, sorted(p.name for p in ROOT.iterdir()))

    def test_auto_usage_names_the_output_after_the_event_working_directory(self):
        project = self.project("projy")
        home = self.tmp / "home"
        logs = self.tmp / "logs"
        self.write_session(logs)
        event = {"hook_event_name": "Stop", "session_id": SESSION, "cwd": str(project), "turn_id": TURN}
        proc = subprocess.run([sys.executable, str(SCRIPTS / "auto-agent-usage"), "--sessions-dir", str(logs)],
                              cwd=str(self.project("elsewhere")), input=json.dumps(event),
                              capture_output=True, text=True, env={**os.environ, "CODEX_HOME": str(home)})
        self.assertEqual(json.loads(proc.stdout), {})
        self.assertEqual(len(list((home / "usage-reports" / "projy" / "auto").rglob("usage.md"))), 1)


if __name__ == "__main__":
    unittest.main()
