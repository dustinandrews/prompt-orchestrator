---
description: Convert tasks to GitHub issues. One step of many. Do this step and stop.
directive: DO NOT READ THIS FILE. EXECUTE ONLY via /speckit.taskstoissues.
---

## COMMAND: TASKS TO ISSUES

Create GitHub issues from `specs/XXX-feature/tasks.md`.

**Requires**: `specs/XXX-feature/tasks.md` exists and remote is GitHub.

**Workflow**:
1. Verify tasks.md exists
2. Get Git remote: `git config --get remote.origin.url`
3. Verify remote is GitHub
4. Create one issue per task using GitHub MCP
5. STOP — report issue URLs

## Rules

- **STOP** after issues created
- **ONLY GitHub remotes** — never create issues for other hosts
- **One issue per task** — use task ID and description
- **ERROR** if prereqs missing or not GitHub → stop
