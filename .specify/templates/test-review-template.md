---
description: Verify all tests pass before golden path validation
handoffs:
  - label: Fix Tests
    agent: speckit.implement
    prompt: All tests must pass before proceeding to product review
---

# /speckit.test-review

## Purpose
Verify all tests pass. NO PARTIAL CREDIT. Zero tolerance for failing tests.

## Input
- Test results from `/speckit.implement`
- `specs/XXX-feature/tasks.md` (test tasks)

## Checklist
- [ ] **Unit Tests**: 100% of unit tests pass
- [ ] **Integration Tests**: All integration tests pass
- [ ] **Acceptance Tests**: All P1 acceptance criteria tested and passing
- [ ] **No Skipped Tests**: Zero `@skip` or `pending` tests
- [ ] **Coverage**: Core logic has test coverage

## Output

Create `specs/XXX-feature/test-review.md`:

```markdown
# Test Review: [FEATURE NAME]

**Date**: [DATE]
**Reviewer**: speckit.test-review

## Test Results
- **Total**: [N] tests
- **Passed**: [N] ([P]%)
- **Failed**: [N]
- **Skipped**: [N]

## Failed Tests (BLOCKING)
| Test | Error | Fix Required |
|------|-------|--------------|
| [Name] | [Error] | [Action] |

## Review Result
STATUS: [PASS | FAIL]

If FAIL: [one sentence reason for failure]
```

## Rules
- **ZERO TOLERANCE**: Any failing test = FAIL
- **NO EXCUSES**: "It's just a small edge case" = fix it
- **TEST OR DELETE**: Untested code must be removed
- **BLOCKING**: Cannot proceed to product review until PASS
