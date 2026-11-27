# Epic orchestration

For multi-stream or complex work, extending [adaptive workflows](workflows.md) and [issue workflow](issue-workflow.md). GitHub Issues, sub-issues, and native `planning-statuses` are the single operational source; no external board or Project is used.

## Adaptive structure & single source

- **Structure:** Simple → single Issue; uncertainty → Parent + Analysis + DEV; complex with clear requirements → Parent + SPEC + DEV; complex with uncertainty → Parent + Analysis + SPEC + DEV.
- **Dependencies & authorization:** Create sub-issues in `Backlog` with native `blocked_by` links. Only `Todo` authorizes execution; open dependencies block start. Close each phase on acceptance/merge and the parent when the global goal is met.
- **Identifiers:** Follow [identifiers](identifiers.md) (`<id> · <STAGE>-<NN>`). Keep Issue for decisions and PR for diff, CI, QA/review, and candidate SHA without duplicating evidence.

## Delegation & gates

- **Coordinator:** Owns dependency scheduling, look-ahead, and status transitions. Delegates all technical work under [orchestrate](../skills/orchestrate/SKILL.md#procedure) with [work packets](../templates/agent-work-packet.md) and [role contracts](../roles/README.md); parallel writes require disjoint ownership and isolated checkouts.
- **Gates:** Spec approval, independent QA/review, and merge approval ([approvals](approvals.md)) remain separate, mandatory human gates. Never infer merge or `Done` from a green check.
