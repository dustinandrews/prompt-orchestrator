---
description: Review specification for constitution compliance and over-engineering
handoffs:
  - label: Clarify Issues
    agent: speckit.clarify
    prompt: Address specification review findings before planning
    send: true
  - label: Revise Spec
    agent: speckit.specify
    prompt: Fix constitution violations and over-engineering
    send: true
scripts:
  sh: scripts/bash/list-specs.sh
  ps: scripts/powershell/list-specs.ps1
---

# /speckit.spec-review

## User Input
```
$ARGUMENTS
```

## Execution Flow

1. **Identify Target Spec**
   - If $ARGUMENTS contains feature name/number: use that spec
   - Else: list available specs in `specs/` and ask user
   - Target: `specs/XXX-feature/spec.md`

2. **Load Required Files**
   - Read `.specify/memory/constitution.md` (project principles)
   - Read target `specs/XXX-feature/spec.md`
   - Read `.specify/templates/spec-review-template.md` (output format)

3. **Execute Review**

   ### Constitution Compliance Check
   For each principle in constitution.md:
   - Does spec violate this principle?
   - Quote specific text that violates
   - Recommend fix

   ### Anti-Pattern Scan (REJECT if found)
   - **Gold Plating**: Look for "would be nice", "could add", "future"
   - **Premature Abstraction**: "framework", "platform", "generic"
   - **Scope Creep**: Features not in original problem statement
   - **Tech Speculation**: Named libraries/frameworks in spec

   ### Simplicity Check
   - Count user stories: >3 P1/P2? Flag as bloated
   - Check for [NEEDS CLARIFICATION]: >3 markers? Flag as unclear
   - Verify acceptance criteria are testable without implementation details

4. **Determine Verdict**
   - **PASS**: No violations, ≤3 stories, clear criteria
   - **NEEDS_REVISION**: Fixable issues found
   - **REJECT**: Fundamental over-engineering (frameworks, >5 stories, etc.)

5. **Generate Output**
   
   Create `specs/XXX-feature/spec-review.md` using template format:
   ```markdown
   # Specification Review: [FEATURE NAME]
   
   **Date**: [DATE]
   **Reviewer**: speckit.spec-review
   **Status**: [PASS | FAIL]
   
   ## Constitution Compliance
   | Principle | Status | Issue | Fix |
   |-----------|--------|-------|-----|
   | [Name] | STATUS: [PASS | FAIL] | [Quote violation] | [Action] |
   
   ## Anti-Patterns Found
   | Pattern | Severity | Location | Fix |
   |---------|----------|----------|-----|
   | [Name] | [BLOCKER/WARNING] | [Quote] | [Action] |
   
   ## Simplicity Score
   - User Stories: [N] ([status])
   - Clarifications Needed: [N] ([status])
   - Testable Criteria: [Y/N]
   
   ## Decision
   **Status**: [PASS | FAIL]
   **Next Step**: [Action with handoff]
   ```

6. **Report Results**
   - Display verdict and key findings
   - If REJECT: explain why, require full revision
   - If NEEDS_REVISION: list specific fixes needed
   - If PASS: ready for `/speckit.plan`

## Rules (VIOLATE = WRONG)
- **MAX 3 STORIES**: More than 3 P1/P2 stories = automatic REJECT
- **NO FRAMEWORKS**: Any "build a framework" language = REJECT
- **NO FUTURE TENSE**: "Will support", "can be extended" = Gold plating
- **FIX BEFORE PROCEED**: NEVER handoff to plan with violations present
