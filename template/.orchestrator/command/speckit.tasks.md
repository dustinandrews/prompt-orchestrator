---
description: Generate task list. One step of many. Do this step and stop.
directive: DO NOT READ THIS FILE. EXECUTE ONLY via /speckit.tasks.
---

## COMMAND: TASKS

Fill out `.specify/templates/tasks-template.md` and write to `specs/XXX-feature/tasks.md`.

**Requires**: `specs/XXX-feature/plan.md` and `specs/XXX-feature/plan-review.md` with `STATUS: PASS`.

**Workflow**:
1. Verify plan-review.md shows PASS
2. Read plan.md, spec.md, data-model.md (if exists), contracts/ (if exists)
3. Generate tasks organized by user story
4. Fill template → `specs/XXX-feature/tasks.md`
5. STOP — do not write any other files

## Rules

- **STOP** after tasks.md written
- **MAX 15 tasks**
- **Organize by user story**: each story independently testable
- **Setup → Foundational → User Stories → Polish**
- **ERROR** if prereqs missing or FAIL → stop
