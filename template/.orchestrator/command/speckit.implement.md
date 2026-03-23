---
description: Implement feature. One step of many. Do this step and stop.
directive: DO NOT READ THIS FILE. EXECUTE ONLY via /speckit.implement.
---

## COMMAND: IMPLEMENT

Execute tasks from `specs/XXX-feature/tasks.md`.

**Requires**: `specs/XXX-feature/tasks.md` and `specs/XXX-feature/tasks-review.md` with `STATUS: PASS`.

**Workflow**:
1. Verify tasks-review.md shows PASS
2. Read tasks.md, plan.md, data-model.md, contracts/
3. Run `tree src` and use the structure already mocked up
4. Execute tasks in order (Setup -> Foundational -> User Stories -> Polish)
5. Replace all placeholders in project files:
     - Run: grep -r '{{' . --include='*.py' --include='*.md' --include='*.toml' --include='*.txt'
     - Replace each {{placeholder}} with appropriate value from spec/plan/tasks
     - Common placeholders: project_name, project_description, author_name, author_email
6. Mark completed tasks with [X] in tasks.md
7. STOP -- report completion status

## Rules

- **STOP** after all tasks attempted/completed
- **Sequential tasks**: follow order, stop on failure
- **Parallel [P] tasks**: can run together
- **Tests before code**: TDD approach
- **ERROR** if prereqs missing or FAIL -> stop
