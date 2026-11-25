#!/usr/bin/env python3
"""Read-only readiness probe. Resolve artifact and project independently."""
import argparse
import json
import re
import sys
from pathlib import Path

COORDINATORS = ("claude", "codex", "opencode", "hermes")
ARTIFACT = Path(__file__).resolve().parent.parent
# Plugin-owned capabilities that a project should not shadow with local copies.
PLUGIN_OWNED = (".agents/skills", ".agents/roles", ".claude/skills", ".claude/agents",
                ".opencode/agents", ".codex", "specs/methodology")
TEMPLATES = "templates"
SHIM_RULES = ("agentic-verify-project", "agentic-work-issue", "agentic-relay",
              "agentic-check-delegation-route", "agentic-usage-report", "agentic-usage-auto")


def permission_rules():
    """Allow rules for the project's untracked .claude/settings.local.json. Printed, never written."""
    allow = [f"Read(/{ARTIFACT}/**)"] + [f"Bash({name}:*)" for name in SHIM_RULES]
    return {"permissions": {"allow": allow}}


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


def plugin_owned_paths(root):
    """Informational only: project paths that shadow plugin-owned capabilities."""
    found = [name for name in PLUGIN_OWNED
             if (root / name).exists() or (root / name).is_symlink()]
    # A project may keep its own templates; report only the plugin's own file names.
    shipped = {item.name for item in (ARTIFACT / TEMPLATES).glob("*.md")}
    local = root / TEMPLATES
    if local.is_dir() and any((local / name).exists() for name in shipped):
        found.append(TEMPLATES)
    return found


def project_pin(root, version):
    """Informational only: the ref of the agentic-harness marketplace in the project's Claude settings."""
    ref = None
    for name in (".claude/settings.json", ".claude/settings.local.json"):
        try:
            data = json.loads((root / name).read_text(encoding="utf-8"))
            value = data["extraKnownMarketplaces"]["agentic-harness"]["source"].get("ref")
        except (OSError, ValueError, KeyError, TypeError, AttributeError):
            continue
        if isinstance(value, str) and value:
            ref = value
    if ref is None:
        return None, "absent"
    if ref == f"v{version}":
        return ref, "tag-match"
    if re.fullmatch(r"v\d+\.\d+\.\d+", ref):
        return ref, "tag-mismatch"
    return ref, "sha-or-branch"


def inventory_root(start):
    start = start.resolve(strict=True)
    if start.is_file():
        start = start.parent
    for directory in (start, *start.parents):
        if (directory / ".git").exists() or (directory / ".git").is_symlink():
            return directory
    raise ValueError("no Git project at or above this directory; select the intended project")


def inventory(project):
    root = inventory_root(project)
    if root == ARTIFACT:
        raise ValueError("select a project checkout distinct from the installed artifact")
    version = json.loads(file_under(ARTIFACT, "plugin.json").read_text(encoding="utf-8"))["version"]
    pin, pin_status = project_pin(root, version)
    return {
        "artifact_root": str(ARTIFACT),
        "artifact_version": version,
        "project_root": str(root),
        "entry_files": {name: (root / name).is_file()
                        for name in ("AGENTS.md", "CLAUDE.md", "specs/project-rules.md")},
        "plugin_owned_paths_in_project": plugin_owned_paths(root),
        "project_pin": pin,
        "pin_status": pin_status,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, default=Path.cwd())
    parser.add_argument("--coordinator", choices=COORDINATORS)
    parser.add_argument("--print-rules", action="store_true",
                        help="print the .claude/settings.local.json permission rules for this plugin and exit; writes nothing")
    parser.add_argument("--inventory", action="store_true",
                        help="read-only inventory for a project not yet adopted: needs only a Git root, no entry files")
    args = parser.parse_args()
    if args.inventory:
        try:
            print(json.dumps(inventory(args.project), sort_keys=True))
        except (OSError, ValueError, KeyError) as error:
            print(f"inventory blocked: {error}", file=sys.stderr)
            return 2
        return 0
    if args.print_rules:
        print(json.dumps(permission_rules(), indent=2))
        return 0
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
        version = json.loads(manifest.read_text(encoding="utf-8"))["version"]
        pin, pin_status = project_pin(root, version)
        print(json.dumps({
            "artifact_root": str(ARTIFACT),
            "artifact_version": version,
            "project_pin": pin,
            "pin_status": pin_status,
            "project_root": str(root),
            "project_rules": str(rules),
            "plugin_owned_paths_in_project": plugin_owned_paths(root),
            "approval_policy": str(approvals),
            "artifact_read_rule_hint": f"Read(/{ARTIFACT}/**)",
            "qa_role": str(role),
            "coordinator_config_candidate": str(config) if config else None,
        }, sort_keys=True))
    except (OSError, ValueError, KeyError) as error:
        print(f"readiness blocked: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
