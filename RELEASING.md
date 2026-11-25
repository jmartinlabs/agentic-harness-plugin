# Releasing (maintainers)

## Versioning policy (SemVer)

- MAJOR: a change of skill names, of the project-path contract, of the required project files, of how the v2 harness schema is handled, or the removal of a capability.
- MINOR: a new capability, skill or tool, or a new client surface.
- PATCH: fixes and documentation.

## Procedure

1. Bump `version` in `plugin.json`, `.claude-plugin/plugin.json` and `.antigravity-plugin/plugin.json` in the same change as the content; update `CHANGELOG.md`. The Codex and Claude caches are keyed by `version`, so a new commit without a bump keeps the same cache path.
2. Merge to `main` with green CI, using a merge commit (it keeps the provenance commits). The status check `required` (an aggregate job in `.github/workflows/validate.yml` that fails unless the `pilot` and `claude-validate` jobs succeed) is the merge gate that the `main-required` ruleset names. A merge needs the owner's explicit approval.
3. Verify before tagging: `git fetch`; `git diff --stat <approved PR head> origin/main` is empty; `git rev-parse origin/main^{tree}` equals the QA'd tree; CI on the `main` SHA is green, including `required`.
4. Create an annotated tag on that exact `main` SHA and publish it: `git tag -a vX.Y.Z <main sha> -m "vX.Y.Z"`, `git push origin vX.Y.Z`, then `gh release create vX.Y.Z --verify-tag --notes-file <notes from the CHANGELOG entry>`. Tags are never moved; a mistake gets a new PATCH release. Tagging and releasing need the owner's explicit approval.
5. Post-release smoke test (tag-form pins were never run): install by tag on Claude Code (`marketplace add jmartinlabs/agentic-harness-plugin#vX.Y.Z`, then install) and on Codex (`--ref vX.Y.Z`), and run the diagnostic on each. All client evidence so far is on 0.1.0 content, so this is also the first load of the released content.

## Consumers

Pin a tag or a full sha:

- Claude Code: `claude plugin marketplace add jmartinlabs/agentic-harness-plugin#<tag-or-sha> --scope local`.
- Codex: `codex plugin marketplace add jmartinlabs/agentic-harness-plugin --ref <tag-or-full-sha>`.
- Antigravity: installs a branch only (a sha or tag URL was rejected in the tested run), so it cannot be pinned to a release; this is a limitation.

Check the pin with `agentic-verify-project`: `pin_status` is `tag-match`, `tag-mismatch`, `sha-or-branch` (not comparable) or `absent`.

## Update and rollback

- Update: bump the pin to the new tag or sha and reinstall (re-add by sha is observed, README "GitHub distribution channel"). For a marketplace that tracks a branch, `plugin update` updates only when the manifest `version` changed; at an unchanged `version` it reports "already at the latest version" (observed, README "Updating and rolling back"). The new version applies after a restart.
- Rollback: re-pin to the previous tag or sha and reinstall. Re-pinning by sha returned 0.1.1 to 0.1.0 in the observed channel flow (README, "GitHub distribution channel").
- Consequence: every release must bump `version`; consumers who need an exact revision pin a tag or a full sha.

## Compatibility with the scaffold

The scaffold pins a plugin tag. PATCH and MINOR releases are compatible with it. A MAJOR release requires a scaffold update and an adoption note.
