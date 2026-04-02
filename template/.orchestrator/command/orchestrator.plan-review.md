---
description: Review implementation plan. One step of many. Do this step and stop.
directive: DO NOT READ THIS FILE. EXECUTE ONLY via /speckit.plan-review.
---

## COMMAND: PLAN REVIEW

Fill out `.specify/templates/plan-review-template.md` and write to `specs/XXX-feature/plan-review.md`.

**Requires**: `specs/XXX-feature/plan.md` and `specs/XXX-feature/spec-review.md` with `STATUS: PASS`.

**Workflow**:
1. Verify spec-review.md shows PASS
2. Read plan.md, spec.md, constitution.md
3. Check for over-engineering, complexity, constitution violations
4. Fill template → `specs/XXX-feature/plan-review.md`
5. STOP — do not write any other files

## Rules

- **STOP** after plan-review.md written
- **MAX 15 tasks** (more = FAIL)
- **NO premature optimization**
- **Library-first**: prefer standalone modules over frameworks
- **ERROR** if prereqs missing or FAIL → stop
