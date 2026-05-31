---
description: Create implementation plan. One step of many. Do this step and stop.
directive: DO NOT READ THIS FILE. EXECUTE ONLY via /speckit.plan.
---

## COMMAND: PLAN

Fill out `.specify/templates/plan-template.md` and write to `specs/XXX-feature/plan.md`.

**Requires**: `specs/XXX-feature/spec-review.md` exists with `STATUS: PASS`.

**Workflow**:
1. Verify spec-review.md shows PASS
2. Run `.specify/scripts/bash/setup-plan.sh --json`
3. Read spec.md, constitution.md
4. Fill template → `specs/XXX-feature/plan.md`
5. STOP — do not write any other files

## Rules

- **STOP** after plan.md written
- **Library-first**: prefer standalone modules over frameworks
- **NO premature optimization**
- **MAX 15 tasks**
- **ERROR** if spec-review missing or shows FAIL → stop
