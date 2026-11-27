# Agent work packet (template)

> Copy into the coordinator's task context per delegate. This is NOT an agent-registration format or an instruction to create a worker when the environment cannot support it. Quick tasks use a compact packet for one bounded worker; add a field only when it applies. Corrections send only findings + acceptance criteria and reference the original packet; never repeat the full brief.

- **Packet ID and profile:** `<functional-id> · <STAGE>-<NN>` (plus `DEV-nn — <name>` for DEV); Functional | Implementation | QA | Infrastructure | bounded custom.
- **Objective and done criteria:** UNSET
- **Authorization:** approval source and date (approved spec, or draft: documentary editing only, no code); hard dependencies and whether each is satisfied.
- **Files and isolation:** files to read; files written under sole ownership; working branch or isolated checkout (or read-only); other active packets that could conflict.
- **Prohibited actions:** approvals, merge, production deployment and destructive operations; reserving Issues or writing native Issue status; delegating further. Publication (push, PR) only when the authorized scope includes it.
- **Applicable rules:** the 3–6 rules this task needs, one line each with its source link (approval gates touched, isolation, security or financial constraints, project-specific restrictions). The delegate reads this list instead of the full policies.
- **Verification:** commands and expected evidence; environment and candidate (SHA plus pending changes); where the evidence is kept (a reachable commit/diff or the existing progress/test-plan section, never a second board).
- **Return:** packet ID; status COMPLETED / PARTIAL / BLOCKED / CANCELLED; candidate and changed files; each check PASS / FAIL / UNRUN with command, environment and evidence; risks, decisions needed and next action. Questions and approvals go to the coordinator, never directly to the user.
- **Only if it applies:** selected native execution profile for the canonical role and reason; requested `provider` / `model` / `effort` and, afterwards, observed `provider` / `model` / `effort` (`FAIL` on mismatch, `UNVERIFIED` on missing metadata; self-report is not evidence); inherited context and its reason; client, version and session for an external client; shared test resources (separate ports, databases, temporary directories); who owns an operation that may need a permission; review milestones.

External clients (Codex, OpenCode) are launched by CLI under [external delegation](../methodology/dynamic-agents-external-clients.md).
