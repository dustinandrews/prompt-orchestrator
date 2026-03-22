---
description: Final review - golden path validation
handoffs:
  - label: Fix Product
    agent: speckit.implement
    prompt: Golden path defects must be fixed
    send: true
scripts:
  sh: scripts/bash/start-product.sh
  ps: scripts/powershell/start-product.ps1
---

# /speckit.product-review

## User Input
```
$ARGUMENTS
```

## Purpose
Validate the core product works on the golden path. Time-boxed manual validation that the feature delivers value. Gate to shipping.

## Prerequisites
- `speckit.test-review` MUST have passed (verified by presence of test-review.md with PASS status)
- If no passing test-review found: ERROR and abort

## Execution Flow

1. **Verify Prerequisites**
   - Check `specs/XXX-feature/test-review.md` exists and shows PASS
   - If not found or FAIL: ERROR, run `/speckit.test-review` first

2. **Identify Golden Path**
   - Read `specs/XXX-feature/spec.md` for P1 user stories
   - Select ONE most critical P1 story
   - Define: Entry → Action → Expected Result

3. **Execute Golden Path (10 minute max)**
   - Start the product (if applicable)
   - Step through the user journey manually
   - Document each step's actual result
   - Stop on first blocking defect

4. **Validation Checklist**
   - [ ] **Entry**: User can start the journey
   - [ ] **Process**: Core function executes without crash
   - [ ] **Output**: Result matches acceptance criteria
   - [ ] **Errors**: Critical failures handled gracefully
   - [ ] **Observable**: Result is visible/verifiable

5. **Determine Verdict**
   - **PASS**: All checklist items verified
   - **FAIL**: Any blocking defect found

6. **Generate Output**
   
   Create `specs/XXX-feature/product-review.md`:
   ```markdown
   # Product Review: [FEATURE NAME]
   
   **Date**: [DATE]
   **Status**: [PASS | FAIL]
   
   ## Golden Path Tested
   **User Story**: [P1 story ID/name]
   **Description**: [Brief journey]
   **Test Duration**: [N] minutes
   
   ## Execution Log
   | Step | Action | Expected | Actual | Status |
   |------|--------|----------|--------|--------|
   | 1 | [Action] | [Expected] | [Actual] | [PASS/FAIL] |
   | 2 | [Action] | [Expected] | [Actual] | [PASS/FAIL] |
   | 3 | [Action] | [Expected] | [Actual] | [PASS/FAIL] |
   
   ## Defects Found
   | Step | Severity | Issue | Fix Required |
   |------|----------|-------|--------------|
   | [N] | [BLOCKER/MAJOR/MINOR] | [Description] | [Action] |
   
   ## Validation Checklist
   - [ ] Entry point accessible
   - [ ] Core process executes
   - [ ] Expected output produced
   - [ ] No critical errors
   - [ ] Observable result
   
   ## Ship Readiness
   **Feature Complete**: [YES | NO]
   **Ship Status**: [READY | NOT READY]
   ```

7. **Report & Handoff**
   - If **FAIL**: Display defects, handoff to `speckit.implement` to fix
   - If **PASS**: Display "Golden path validated", commit changes to the repo

## Rules
- **10 MINUTE MAX**: Longer = product too complex
- **ONE PATH ONLY**: Don't test variants, just main success path
- **BLOCKER = FAIL**: Any blocking defect = not ready
- **PREREQUISITE STRICT**: No test-review PASS = no product-review
- **SHIP CRITERIA**: Test PASS + Product PASS = READY
