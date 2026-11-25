#!/usr/bin/env python3
"""Read-only readiness probe. Resolve artifact and project independently."""
import argparse
import json
import sys
from pathlib import Path

COORDINATORS = ("claude", "codex", "opencode", "hermes")
ARTIFACT = Path(__file__).resolve().parent.parent
# Plugin-owned capabilities that a project should not shadow with local copies.
PLUGIN_OWNED = (".agents/skills", ".agents/roles", ".claude/skills", ".claude/agents",
                ".opencode/agents", "specs/methodology")


def project_root(start):
    start = start.resolve(strict=True)
    if start.is_file():
        start = start.parent
    directories = (start, *start.parents)
    boundary = next(
        (directory for directory in directories
         if (directory / ".git").exists() or (directory / ".git").is_symlink()),
        None,
    )
    # A Git boundary takes precedence over nested entry files. A source-only
    # fixture can opt in with an entry pair even without a Git directory.
    candidates = (boundary,) if boundary is not None else directories
    entries = ("AGENTS.md", "CLAUDE.md")
    for directory in candidates:
        if all((directory / entry).is_file() for entry in entries):
            for entry in entries:
                file_under(directory, entry)
            return directory
    raise ValueError("no project with AGENTS.md and CLAUDE.md in this checkout; select the intended project")


def file_under(root, relative):
    path = root / relative
    if not path.resolve().is_relative_to(root):
        raise ValueError(f"{path}: points outside its root")
    if not path.is_file():
        raise ValueError(f"{path}: absent or not a regular file")
    try:
        path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        raise ValueError(f"{path}: unreadable ({error})") from error
    return path


def common_copies(root):
    """Informational only: project paths that shadow plugin-owned capabilities."""
    return [name for name in PLUGIN_OWNED
            if (root / name).exists() or (root / name).is_symlink()]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, default=Path.cwd())
    parser.add_argument("--coordinator", choices=COORDINATORS)
    args = parser.parse_args()
    try:
        root = project_root(args.project)
        if root == ARTIFACT:
            raise ValueError("select a project checkout distinct from the installed artifact")
        rules = file_under(root, "specs/project-rules.md")
        approvals = file_under(ARTIFACT, "methodology/approvals.md")
        role = file_under(ARTIFACT, "roles/qa-review.md")
        manifest = file_under(ARTIFACT, "plugin.json")
        config = None
        if args.coordinator:
            relative = f".agents/harnesses/{args.coordinator}.json"
            path = root / relative
            if path.exists() or path.is_symlink():
                config = file_under(root, relative)
        print(json.dumps({
            "artifact_root": str(ARTIFACT),
            "artifact_version": json.loads(manifest.read_text(encoding="utf-8"))["version"],
            "project_root": str(root),
            "project_rules": str(rules),
            "common_copies_in_project": common_copies(root),
            "approval_policy": str(approvals),
            "qa_role": str(role),
            "coordinator_config_candidate": str(config) if config else None,
        }, sort_keys=True))
    except (OSError, ValueError, KeyError) as error:
        print(f"readiness blocked: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
