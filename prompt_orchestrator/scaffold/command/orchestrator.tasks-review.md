---
description: Review task list. One step of many. Do this step and stop.
directive: DO NOT READ THIS FILE. EXECUTE ONLY via /speckit.tasks-review.
---

## COMMAND: TASKS REVIEW

Fill out `.specify/templates/tasks-review-template.md` and write to `specs/XXX-feature/tasks-review.md`.

**Requires**: `specs/XXX-feature/tasks.md` and `specs/XXX-feature/plan-review.md` with `STATUS: PASS`.

**Workflow**:
1. Verify plan-review.md shows PASS
2. Read tasks.md, plan.md
3. Check task distribution, bloat, constitution compliance
4. Fill template → `specs/XXX-feature/tasks-review.md`
5. STOP — do not write any other files

## Rules

- **STOP** after tasks-review.md written
- **MAX 15 tasks total**
- **Core: 60-70%, Tests: 20-30%, Setup: <10%, Polish: <5%**
- **DELETE MERCILESSLY**: if in doubt, cut it
- **ERROR** if prereqs missing or FAIL → stop
