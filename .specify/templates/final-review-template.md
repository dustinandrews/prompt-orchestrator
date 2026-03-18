---
description: Two-phase final review - tests first, then golden path validation
handoffs:
  - label: Fix Tests
    agent: speckit.implement
    prompt: All tests must pass before Phase 2
  - label: Fix Product
    agent: speckit.implement
    prompt: Core functionality must work on golden path
---

# /speckit.final-review

## Purpose
Two-phase final validation: First verify all tests pass, then verify core product works on the golden path. NO PARTIAL CREDIT.

## Phase 1: Test Verification

### Input
- Test results from `/speckit.implement`
- `specs/XXX-feature/tasks.md` (test tasks)

### Checklist
- [ ] **Unit Tests**: 100% of unit tests pass
- [ ] **Integration Tests**: All integration tests pass
- [ ] **Acceptance Tests**: All P1 acceptance criteria tested and passing
- [ ] **No Skipped Tests**: Zero `@skip` or `pending` tests
- [ ] **Coverage**: Core logic has test coverage

### Phase 1 Output

```markdown
# Final Review - Phase 1: Tests

**Date**: [DATE]
**Status**: [PASS | FAIL]

## Test Results
- **Total**: [N] tests
- **Passed**: [N] ([P]%)
- **Failed**: [N]
- **Skipped**: [N]

## Failed Tests (BLOCKING)
| Test | Error | Fix Required |
|------|-------|--------------|
| [Name] | [Error] | [Action] |

## Decision
**Phase 2 Allowed**: [YES | NO - fix tests first]

**If NO, fix, retest, repeat until yes.**
```

---

## Phase 2: Golden Path Validation

### Input
- Working build from Phase 1
- `specs/XXX-feature/spec.md` (P1 user stories)
- `specs/XXX-feature/spec.md` (acceptance criteria)

### Golden Path Definition
The ONE critical user journey that MUST work:
- [ ] **Entry**: User can start the journey
- [ ] **Process**: Core functionality executes
- [ ] **Exit**: User achieves goal
- [ ] **No Errors**: Clean execution, no crashes
- [ ] **Observable**: Output/result is visible/verifiable
- [ ] **Docs**: README.md exists, has usable installation steps, and at least one usage example.

### Validation Steps
1. **Execute Golden Path**: Walk through P1 user story manually
2. **Verify Output**: Result matches acceptance criteria
3. **Check Edge Cases**: Critical errors handled gracefully
4. **Time Box**: If it takes >10 min to validate, it's too complex

### Phase 2 Output

```markdown
# Final Review - Phase 2: Golden Path

**Date**: [DATE]
**Status**: [PASS | FAIL]

## Golden Path Tested
**User Story**: [P1 story name]
**Path**: [Brief description of steps taken]

## Results
- [ ] Entry point accessible: [PASS/FAIL]
- [ ] Core process executes: [PASS/FAIL]
- [ ] Expected output produced: [PASS/FAIL]
- [ ] No critical errors: [PASS/FAIL]

## Defects Found
| Step | Expected | Actual | Severity |
|------|----------|--------|----------|
| [N] | [Expected] | [Actual] | [BLOCKER/MAJOR/MINOR] |

## Decision
**Feature Complete**: [YES | NO]
**If NO**: Fix defects, re-run Phase 2 (tests already passed)

## Ship Readiness
- [ ] Code committed
- [ ] Tests passing
- [ ] Golden path validated
- [ ] Documentation minimal but sufficient

**SHIP IT**: [YES | Not yet]
```

---

## Two-Phase Rules

### Phase 1 Rules
- **ZERO TOLERANCE**: Any failing test = FAIL
- **NO EXCUSES**: "It's just a small edge case" = fix it
- **TEST OR DELETE**: Untested code must be removed

### Phase 2 Rules
- **ONE PATH ONLY**: Test the main success path, not every variant
- **WORKS > PERFECT**: Performance, polish come later
- **TIME BOX**: 10 minutes max for validation

### Exit Criteria
- **Phase 1 + Phase 2 PASS** = Feature ships
- **Either FAIL** = Back to implementation
- **NEVER** skip Phase 1 to get to Phase 2 faster
