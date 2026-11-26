# Hermes Agent global adapter

Minimal, native adapter for using the `agentic` plugin with **Hermes Agent** at user scope (per-user, per-`HERMES_HOME` profile) without duplicating any skills, roles, or methodology.

Hermes reads skills natively, so this adapter provides only global installation/update instructions and a placeholder `model_map` delegation example. It does not create a second coordinator, modify project files, or override [approvals](../../methodology/approvals.md).

## What is reused from the plugin

| Plugin asset | Role in Hermes |
| --- | --- |
| `skills/*/SKILL.md` (e.g. [orchestrate](../../skills/orchestrate/SKILL.md)) | Invoked natively as `/orchestrate`, `/work-issue`, `/task`, `/dev`, `/spec`, `/tweak`, `/handoff`, `/relay`, `/verify-project`, etc. |
| [roles](../../roles/README.md) | Canonical role contracts passed inside bounded delegation packets. |
| [methodology](../../methodology/dynamic-agents.md) | Shared workflow, delegation, and [approval](../../methodology/approvals.md) rules. |
| `scripts/` | Run directly via `python3 <plugin-root>/scripts/<tool>` (including `verify-project.py` and `check-delegation-route`). |

Project-owned files (`AGENTS.md`, `specs/`, `.agents/harnesses/`) remain in each project repository.

## Global per-user install

Clone the plugin once at user scope tracking the `stable` channel, then symlink its `skills/*` directories into your Hermes profile's skills directory (`${HERMES_HOME:-$HOME/.hermes}/skills`):

```sh
PLUGIN_ROOT="${XDG_DATA_HOME:-$HOME/.local/share}/agentic-harness-plugin"
HERMES_SKILLS="${HERMES_HOME:-$HOME/.hermes}/skills"

git clone --branch stable https://github.com/jmartinlabs/agentic-harness-plugin.git "$PLUGIN_ROOT"
mkdir -p "$HERMES_SKILLS"
for skill in "$PLUGIN_ROOT"/skills/*; do
  ln -sfn "$skill" "$HERMES_SKILLS/$(basename "$skill")"
done
```

Start a new Hermes session **from the target project's repository root**:

```sh
cd /path/to/your-project
hermes
```

Verify readiness with `/verify-project` or:

```sh
python3 "$PLUGIN_ROOT/scripts/verify-project.py" --coordinator hermes
```

### Update

```sh
PLUGIN_ROOT="${XDG_DATA_HOME:-$HOME/.local/share}/agentic-harness-plugin"
HERMES_SKILLS="${HERMES_HOME:-$HOME/.hermes}/skills"

git -C "$PLUGIN_ROOT" fetch origin
git -C "$PLUGIN_ROOT" checkout stable
git -C "$PLUGIN_ROOT" pull --ff-only
for skill in "$PLUGIN_ROOT"/skills/*; do
  ln -sfn "$skill" "$HERMES_SKILLS/$(basename "$skill")"
done
```

Start a new Hermes session so updated skills are loaded.

### Roll back

```sh
PLUGIN_ROOT="${XDG_DATA_HOME:-$HOME/.local/share}/agentic-harness-plugin"
git -C "$PLUGIN_ROOT" fetch --tags origin
git -C "$PLUGIN_ROOT" checkout v1.1.0   # replace with the previous published tag
```

Re-run the symlink loop if the skill set changed, then start a new Hermes session.

### Uninstall

Remove the symlinks pointing into `$PLUGIN_ROOT/skills/` from `${HERMES_HOME:-$HOME/.hermes}/skills` and delete `$PLUGIN_ROOT`. Project repositories are untouched.

## Session rules and boundaries

- **Always launch from the project root**: Hermes injects `AGENTS.md` from the current working directory. Starting in a subdirectory drops project rules.
- **Restart after policy edits**: changes to `AGENTS.md` or profile configuration take effect only in a new session.
- **No `--yolo` or `approvals.mode: off`**: shell command approvals are not semantic approvals; follow [methodology/approvals.md](../../methodology/approvals.md).
- **Per-profile scope**: `HERMES_HOME` isolates profiles. Repeat the symlink step for each profile that should load the plugin.

## Role-based delegation (`model_map`)

Hermes configures native delegate routes manually in the user's profile via `delegation.backend: model_map` (it does not use `.agents/harnesses/<coordinator>.json` to generate routes).

See [model_map.example.yaml](model_map.example.yaml) for the minimal structure aligning `model_map` options with the plugin's canonical roles (`implementation`, `functional`, `review`, `qa`, `infrastructure`) plus a `worker` default.

Key rules when using `model_map`:

- `options` **must be a YAML list** (`- name: ...`), never a mapping; Hermes ignores a mapping and leaves `option` unexposed.
- Replace `<connected-provider>` and `<verified-model>` manually with providers already connected in your profile. This adapter never writes profile configuration or credentials.
- Restart the Hermes session after editing the profile so `delegate_task` exposes the updated options.
- Keep `goal` short and place detailed instructions in `context` to avoid upstream dropping of the per-task `option` parameter.
- Verify the effective route after delegation with:

```sh
python3 "$PLUGIN_ROOT/scripts/check-delegation-route" \
  --profile <profile> \
  --delegation <id> \
  --expect-label <option> \
  --expect-provider <provider> \
  --expect-model <model>
```
