#!/usr/bin/env python3
"""Report the version of the artifact that started this session."""
import json
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
claude = sys.argv[1:] == ["--claude"]
manifest = ".claude-plugin/plugin.json" if claude else ".codex-plugin/plugin.json"
version = json.loads((root / manifest).read_text(encoding="utf-8"))["version"]
result = {"systemMessage": f"Agentic Harness {version}"}
if claude:
    result["hookSpecificOutput"] = {
        "hookEventName": "SessionStart",
        "additionalContext": (root / "skills/orchestrate/SKILL.md").read_text(encoding="utf-8"),
    }
print(json.dumps(result))
