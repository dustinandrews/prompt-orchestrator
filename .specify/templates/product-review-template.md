---
description: Golden path validation - core functionality must work
type: product
handoffs:
  - label: Fix Product
    agent: speckit.implement
    prompt: Core functionality must work on the golden path
---

# /speckit.product-review

## Purpose
Final validation: Verify core product works on the golden path. Only runs after tests pass.

## Input
- Working build (tests already passed)
- `specs/XXX-feature/spec.md` (P1 user stories)
- `specs/XXX-feature/spec.md` (acceptance criteria)

## Golden Path Definition
The ONE critical user journey that MUST work:
- [ ] **Entry**: User can start the journey
- [ ] **Process**: Core functionality executes
- [ ] **Exit**: User achieves goal
- [ ] **No Errors**: Clean execution, no crashes
- [ ] **Observable**: Output/result is visible/verifiable
- [ ] **Docs**: README.md exists, has usable installation steps, and at least one usage example.

## Validation Steps
1. **Execute Golden Path**: Walk through P1 user story manually
2. **Verify Output**: Result matches acceptance criteria
3. **Check Edge Cases**: Critical errors handled gracefully
4. **Time Box**: If it takes >10 min to validate, it's too complex

## Output

Create `specs/XXX-feature/product-review.md`:

```markdown
# Product Review: [FEATURE NAME]

**Date**: [DATE]
**Reviewer**: speckit.product-review

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

## Review Result
STATUS: [PASS | FAIL]

If FAIL: [one sentence reason for failure]
```

## Rules
- **ONE PATH ONLY**: Test the main success path, not every variant
- **WORKS > PERFECT**: Performance, polish come later
- **TIME BOX**: 10 minutes max for validation
- **SHIP IT**: PASS = Feature is complete and shippable
