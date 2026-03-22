---
description: Run tests and review. One step of many. Do this step and stop.
directive: DO NOT READ THIS FILE. EXECUTE ONLY via /speckit.test-review.
---

## COMMAND: TEST REVIEW

Fill out `.specify/templates/test-review-template.md` and write to `specs/XXX-feature/test-review.md`.

**Requires**: `specs/XXX-feature/tasks.md` and `specs/XXX-feature/tasks-review.md` with `STATUS: PASS`.

**Workflow**:
1. Verify tasks-review.md shows PASS
2. Run all tests: `./.specify/scripts/bash/run-tests.sh`
3. Verify 100% pass, zero skipped, adequate coverage
4. Fill template → `specs/XXX-feature/test-review.md`
5. STOP — do not write any other files

## Rules

- **STOP** after test-review.md written
- **100% PASS RATE**: any failing test = FAIL
- **ZERO SKIP**: no skipped/pending tests allowed
- **ERROR** if prereqs missing or FAIL → stop
