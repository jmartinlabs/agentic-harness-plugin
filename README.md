# Agentic Harness plugin

The `agentic` plugin supplies shared skills, roles, methodology, templates and tools from one marketplace, `agentic-harness`. Each project keeps its own rules (`specs/project-rules.md`), v2 harness configuration (`.agents/harnesses/<coordinator>.json`) and application files.

- **Current stable release:** [latest stable release](https://github.com/jmartinlabs/agentic-harness-plugin/releases/latest) (tracking the `stable` channel).
- **Requirements:** Python 3.10+ for hooks, readiness diagnostics and CLI tools.

---

## Quick start

Install once per client at user scope. All commands below track the `stable` channel.

### Claude Code

```sh
claude plugin marketplace add https://github.com/jmartinlabs/agentic-harness-plugin.git#stable --scope user
claude plugin install agentic@agentic-harness --scope user
```

If Claude Code denies reads to plugin files, find `installPath` with `claude plugin list --json` and run:

```sh
python3 "<installPath>/scripts/verify-project.py" --print-rules
```

Add the printed `Read(//<installPath>/**)` and needed `Bash(agentic-*:*)` entries to the project's untracked `.claude/settings.local.json` (or user settings). Refresh the `Read` rule after an update.

### Codex CLI

```sh
codex plugin marketplace add https://github.com/jmartinlabs/agentic-harness-plugin.git --ref stable
codex plugin add agentic@agentic-harness
```

Review and trust the plugin's hooks in Codex with `/hooks` (and re-review after updates or rollbacks).

### Antigravity

```sh
antigravity plugin install https://github.com/jmartinlabs/agentic-harness-plugin/tree/stable
```

Antigravity installs globally under `$HOME/.gemini/config/plugins/agentic` from a Git branch (not a commit SHA). It loads `.antigravity-plugin/plugin.json` and the 13 skills as bare names (e.g. `verify-project`, `orchestrate`); it skips `agents/*.md` and `hooks/hooks.json`.

### OpenCode

Clone `stable` once per user and symlink the OpenCode adapter and each shared skill directory into `~/.config/opencode/` (symlinking individual skill directories preserves any existing skills in `~/.config/opencode/skills/`):

```sh
git clone --branch stable https://github.com/jmartinlabs/agentic-harness-plugin.git ~/.local/share/agentic-harness-plugin
mkdir -p ~/.config/opencode/agents ~/.config/opencode/plugins ~/.config/opencode/skills
for agent in ~/.local/share/agentic-harness-plugin/adapters/opencode/agents/*.md; do
  ln -sfn "$agent" ~/.config/opencode/agents/"$(basename "$agent")"
done
ln -sfn ~/.local/share/agentic-harness-plugin/adapters/opencode/plugins/review-read ~/.config/opencode/plugins/review-read
for skill in ~/.local/share/agentic-harness-plugin/skills/*; do
  ln -sfn "$skill" ~/.config/opencode/skills/"$(basename "$skill")"
done
```

### Hermes Agent

Hermes loads skills natively at user scope. Clone `stable` once per user and symlink `skills/*` into `${HERMES_HOME:-$HOME/.hermes}/skills` (no files are copied into projects), and always start `hermes` from the project root. `scripts/update-agentic --check` also inspects `${HERMES_HOME:-$HOME/.hermes}/profiles/*/` in read-only mode (when the shared checkout exists) and warns about profiles whose `skills/` directory is missing or has no symlink to a top-level skill directory inside `<shared-repo>/skills` (if the profile's `skills/` directory itself is a symlink to `<shared-repo>/skills`, the profile is considered covered). A single valid symlink to a top-level skill directory marks a profile as covered: partial symlink sets are not flagged, and copied (non-symlinked) skills are reported as missing shared-checkout plugin skills; `update-agentic` never creates or repairs profile links. See [adapters/hermes/README.md](adapters/hermes/README.md) for full install, update, rollback and optional `model_map` role-routing instructions.

---

## Update and roll back

### Update

To check or update all installed clients in one step (without installing missing clients or starting AI sessions), run `scripts/update-agentic`:

```sh
# Read-only status and version check across all supported clients
python3 <plugin-root>/scripts/update-agentic --check

# Update all installed clients
python3 <plugin-root>/scripts/update-agentic
```

Optional global symlink on `PATH`:

```sh
ln -sfn <plugin-root>/scripts/update-agentic ~/.local/bin/update-agentic
```

If Codex has multiple cached versions without a pinned version in `config.toml`, `update-agentic` selects the highest SemVer cached version as the estimated active installation.

Or run the command for your individual client and start a new session. Updates apply to all projects in that client profile.

```sh
# Claude Code
claude plugin marketplace update agentic-harness
claude plugin update agentic@agentic-harness --scope user

# Codex CLI
codex plugin marketplace upgrade agentic-harness

# Antigravity
antigravity plugin uninstall agentic
antigravity plugin install https://github.com/jmartinlabs/agentic-harness-plugin/tree/stable

# OpenCode
git -C ~/.local/share/agentic-harness-plugin pull --ff-only origin stable
```

### Roll back

Run uninstall/removal commands **outside any project**, then reinstall replacing `stable` with a previous published tag (e.g. `v1.2.0` or `v1.0.0`). Use the same procedure with `stable` to return to the stable channel.

```sh
# Claude Code
claude plugin uninstall agentic@agentic-harness --scope user
claude plugin marketplace remove agentic-harness

# Codex CLI
codex plugin remove agentic@agentic-harness
codex plugin marketplace remove agentic-harness

# Antigravity
antigravity plugin uninstall agentic

# OpenCode
git -C ~/.local/share/agentic-harness-plugin fetch --tags
git -C ~/.local/share/agentic-harness-plugin checkout v1.2.0
```

> **Migrating an older installation:** If `agentic-harness` was registered from another source or ref, uninstall and remove the marketplace outside any project, remove old Agentic marketplace/enablement entries from project settings (preserving unrelated settings and `.agents/harnesses/`), and reinstall using `stable`.

---

## Onboarding and skills

### Project setup

- **New project:** Run `verify-project` (or `agentic:verify-project`), then `init-project`.
- **Existing project:** Run `adopt-project` (supports a read-only inventory before entry files exist).
- **Per-project files:** Each project owns its `AGENTS.md`, `CLAUDE.md`, `specs/project-rules.md` and `.agents/harnesses/<coordinator>.json` (v2 harness config).
- **Validate v2 config:** Run `python3 <plugin-root>/scripts/validate-core --project <project-dir>`.

### The 13 skills

| Category | Skills |
| --- | --- |
| Onboarding & readiness | `verify-project`, `init-project`, `adopt-project`, `bootstrap` |
| Delivery & orchestration | `orchestrate`, `task`, `tweak`, `spec`, `dev`, `roadmap`, `handoff` |
| Issue & multi-agent coordination | `work-issue`, `relay` |

### Package contents

- `skills/`, `methodology/`, `roles/`, `templates/` — canonical shared assets (see [PROVENANCE.md](PROVENANCE.md) for upstream baseline and hashes).
- `agents/` — Claude Code role agents (`functional`, `implementation`, `infrastructure`, `qa-review`).
- `adapters/opencode/`, `adapters/hermes/` — global per-user adapters for OpenCode and Hermes.
- `hooks/` — `SessionStart` version banner (`Agentic Harness X.Y.Z`) and Codex usage hooks.
- `scripts/`, `bin/` — CLI tools (`verify-project.py`, `validate-core`, `agent-relay`, `check-delegation-route`, `report-agent-usage`, `auto-agent-usage`). In Claude Code, `bin/agentic-*` shims are on `PATH` while enabled; elsewhere run `python3 <plugin-root>/scripts/<tool>`.

---

## Usage reporting

- **Manual report:** Run `agentic-usage-report --session <UUID>` (Claude Code) or `python3 <plugin-root>/scripts/report-agent-usage --session <UUID>` from the project root to inspect local agent usage summaries.
- **Automatic capture:** `auto-agent-usage` (`agentic-usage-auto` in Claude Code) is wired to Codex `Stop`, `SubagentStop` and `SessionEnd` hooks in `hooks/codex.json` and can be invoked directly from the project root.

---

## Local validation

```sh
python3 -m unittest discover -s tests -v
```

---

## Current limitations

- **No guaranteed per-project version pins:** User-scope installation applies one plugin version across all projects in a client profile ([#2](https://github.com/jmartinlabs/agentic-harness-plugin/issues/2)).
- **Explicit global install required:** Global per-user installation replaces automatic project-level detection; an enabled-but-uninstalled plugin fails open ([#3](https://github.com/jmartinlabs/agentic-harness-plugin/issues/3)).
- **Deferred live client verification:** End-to-end live client checks (including OpenCode, Hermes, interactive permission prompts and published-tag smoke checks) are deferred due to quota.
- **Client-specific behavior:**
  - **Antigravity:** Installs from a branch tip (no tag/SHA pin) and loads only the 13 skills as bare names (skips `agents/` and `hooks/`).
  - **Claude Code:** Running `uninstall` or `marketplace remove` inside a project can clear `.claude/settings.json` plugin entries; plugin file reads require `Read(//<installPath>/**)` refreshed after updates.
  - **Enforcement:** Hooks and skill instructions are guidance, not hard sandbox enforcement.

## References and history

Historical experiments, increment logs and design decisions live in their original issues rather than this README:

- Architecture & distribution spec: [agent-project-template#77](https://github.com/jmartinlabs/agent-project-template/issues/77) ([stable channel amendment](https://github.com/jmartinlabs/agent-project-template/issues/77#issuecomment-7174900762))
- Plugin issues & evidence: [#2](https://github.com/jmartinlabs/agentic-harness-plugin/issues/2), [#3](https://github.com/jmartinlabs/agentic-harness-plugin/issues/3), [#4](https://github.com/jmartinlabs/agentic-harness-plugin/issues/4), [#5](https://github.com/jmartinlabs/agentic-harness-plugin/issues/5), [#6](https://github.com/jmartinlabs/agentic-harness-plugin/issues/6), [#7](https://github.com/jmartinlabs/agentic-harness-plugin/issues/7), [#8](https://github.com/jmartinlabs/agentic-harness-plugin/issues/8), [#22](https://github.com/jmartinlabs/agentic-harness-plugin/issues/22)
- File provenance: [PROVENANCE.md](PROVENANCE.md)
