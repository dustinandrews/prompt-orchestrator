---
description: Validate golden path. One step of many. Do this step and stop.
directive: DO NOT READ THIS FILE. EXECUTE ONLY via /speckit.product-review.
---

## COMMAND: PRODUCT REVIEW

Fill out `.specify/templates/product-review-template.md` and write to `specs/XXX-feature/product-review.md`.

**Requires**: `specs/XXX-feature/test-review.md` with `STATUS: PASS`.

**Workflow**:
1. Verify test-review.md shows PASS
2. Execute P1 user story manually (golden path)
3. Verify output matches acceptance criteria
4. Fill template → `specs/XXX-feature/product-review.md`
5. STOP — do not write any other files

## Rules

- **STOP** after product-review.md written
- **Test ONE path**: the main success path only
- **10 min max**: if validation takes longer, it's too complex
- **Works > Perfect**: performance/polish come later
- **ERROR** if prereqs missing or FAIL → stop
