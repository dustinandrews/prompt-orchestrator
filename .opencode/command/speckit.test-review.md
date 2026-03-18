---
description: Phase 1 final review - all tests must pass
handoffs:
  - label: Fix Tests
    agent: speckit.implement
    prompt: Fix all failing and skipped tests
    send: true
  - label: Validate Product
    agent: speckit.product-review
    prompt: All tests passing - validate golden path
    send: true
scripts:
  sh: scripts/bash/run-tests.sh
  ps: scripts/powershell/run-tests.ps1
---

# /speckit.test-review

## User Input
```
$ARGUMENTS
```

## Purpose
Gate to product validation. Zero tolerance for failing or skipped tests. All tests MUST pass before proceeding to product review.

## Execution Flow

1. **Identify Feature**
   - Parse $ARGUMENTS for feature name/number
   - Target: `specs/XXX-feature/`

2. **Run All Tests**
   - Execute: `./scripts/bash/run-tests.sh` or equivalent
   - Capture: Total, Passed, Failed, Skipped
   - Save full test output to `specs/XXX-feature/test-results.log`

3. **Verify Coverage**
   - Unit tests: Core logic paths covered?
   - Integration tests: Component interactions tested?
   - Acceptance tests: P1 criteria verified?
   - No `@skip`, `@pending`, or TODO tests allowed

4. **Determine Verdict**
   - **PASS**: 100% tests passing, zero skipped, adequate coverage
   - **FAIL**: Any failing or skipped tests blocks progress

5. **Generate Output**
   
   Create `specs/XXX-feature/test-review.md`:
   ```markdown
   # Test Review: [FEATURE NAME]
   
   **Date**: [DATE]
   **Status**: [PASS | FAIL]
   
   ## Test Results
   - **Total**: [N] tests
   - **Passed**: [N] ([P]%)
   - **Failed**: [N]
   - **Skipped**: [N]
   
   ## Failed Tests (BLOCKING)
   | Test | Location | Error | Fix Required |
   |------|----------|-------|--------------|
   | [Name] | [File:Line] | [Error] | [Specific fix] |
   
   ## Skipped Tests (BLOCKING)
   | Test | Reason | Action |
   |------|--------|--------|
   | [Name] | [Why skipped] | [Implement or remove] |
   
   ## Coverage Analysis
   - Core logic: [%] ([status: OK/INSUFFICIENT])
   - Integration: [%] ([status: OK/INSUFFICIENT])
   - P1 paths: [Y/N]
   
   ## Decision
   **Product Review Allowed**: [YES | NO]
   **If NO**: Fix all failing/skipped tests, re-run `/speckit.test-review`
   ```

6. **Report & Handoff**
   - If **FAIL**: Display failure count, handoff to `speckit.implement` to fix
   - If **PASS**: Display "All tests passing", handoff to `speckit.product-review`

## Rules (ZERO TOLERANCE)
- **100% PASS RATE**: Any failing test = FAIL
- **ZERO SKIP**: No skipped, pending, or TODO tests allowed
- **NO EXCUSES**: "It's just an edge case" = fix it
- **COVERAGE MINIMUM**: Core logic must have test coverage
- **BLOCKING**: Cannot proceed to product-review until PASS
