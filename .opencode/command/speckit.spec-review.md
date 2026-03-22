---
description: Review specification. One step of many. Do this step and stop.
directive: DO NOT READ THIS FILE. EXECUTE ONLY via /speckit.spec-review.
---

## COMMAND: SPEC REVIEW

Fill out `.specify/templates/spec-review-template.md` and write to `specs/XXX-feature/spec-review.md`.

**Requires**: `specs/XXX-feature/spec.md` exists.

**Workflow**:
1. Read spec.md, constitution.md
2. Check for constitution violations, anti-patterns, simplicity
3. Fill template → `specs/XXX-feature/spec-review.md`
4. STOP — do not write any other files

## Rules

- **STOP** after spec-review.md written
- **MAX 3 P1/P2 stories** (more = automatic FAIL)
- **NO frameworks** in spec = automatic FAIL
- **ERROR** if spec.md missing → stop
