---
description: Review technical plan for over-engineering and constitution compliance
handoffs:
  - label: Revise Plan
    agent: speckit.plan
    prompt: Fix over-engineering and complexity issues
    send: true
  - label: Create Tasks
    agent: speckit.tasks
    prompt: Generate tasks from approved plan
    send: true
scripts:
  sh: scripts/bash/list-specs.sh
  ps: scripts/powershell/list-specs.ps1
---

# /speckit.plan-review

## User Input
```
$ARGUMENTS
```

## Execution Flow

1. **Identify Target Plan**
   - Parse $ARGUMENTS for feature name/number
   - Target: `specs/XXX-feature/plan.md`
   - Must exist before review can proceed

2. **Load Required Files**
   - Read `.specify/memory/constitution.md`
   - Read `specs/XXX-feature/spec.md` (verify alignment)
   - Read `specs/XXX-feature/plan.md` (target)
   - Read `.specify/templates/plan-review-template.md`

3. **Execute Review**

   ### Architecture Review
   - **Library-First**: Is the component standalone with clear boundaries?
   - **CLI Interface**: Text I/O or complex API?
   - **Dependencies**: External DBs, message queues, caching layers?

   ### Over-Engineering Detection (REJECT flags)
   | Pattern | Indicator | Verdict |
   |---------|-----------|---------|
   | Microservices | "service mesh", "distributed" | REJECT |
   | Message Queues | "queue", "pub/sub", "async" when sync works | REJECT |
   | Caching | "cache layer", "Redis" before measurement | REJECT |
   | Config Systems | "config management" vs env vars | REJECT |
   | Generic Frameworks | "plugin system", "driver interface" | REJECT |

   ### Task Breakdown Review
   - Count total tasks: >15 = bloated
   - Check task size: >4 hours = too big, split it
   - Verify "make it work" comes before "make it nice"
   - Ensure setup tasks are minimal (<10%)

   ### Alignment Check
   - Does plan address all P1 stories from spec?
   - Are there plan items NOT in spec? (Scope creep)
   - Do success criteria have implementation paths?

4. **Determine Verdict**
   - **PASS**: Lean, aligned, constitution-compliant
   - **NEEDS_REVISION**: Fixable bloat/complexity
   - **REJECT**: Fundamental architecture violations

5. **Generate Output**
   
   Create `specs/XXX-feature/plan-review.md`:
   ```markdown
   # Plan Review: [FEATURE NAME]
   
   **Date**: [DATE]
   **Reviewer**: speckit.plan-review
   **Status**: [PASS | NEEDS_REVISION | REJECT]
   
   ## Complexity Metrics
   - **Total Tasks**: [N] ([status: OK/TOO_MANY])
   - **Estimated Hours**: [N] ([status: OK/TOO_LONG])
   - **External Dependencies**: [N] ([status: OK/TOO_MANY])
   - **Internal Dependencies**: [N] ([status: OK/COMPLEX])
   
   ## Over-Engineering Detected
   | Component | Violation | Simplification |
   |-----------|-----------|----------------|
   | [Name] | [Complex solution] | [Simple solution] |
   
   ## Constitution Compliance
   | Principle | Status | Notes |
   |-----------|--------|-------|
   | Library-First | [PASS/FAIL] | [Notes] |
   | CLI Interface | [PASS/FAIL] | [Notes] |
   | Test-First | [PASS/FAIL] | [Notes] |
   | Simplicity | [PASS/FAIL] | [Notes] |
   
   ## Alignment with Spec
   | P1 Story | Covered | Notes |
   |----------|---------|-------|
   | [Story] | [Y/N] | [Gap if N] |
   
   ## Decision
   **Status**: [PASS/NEEDS_REVISION/REJECT]
   **If REJECT**: [Why and what to change]
   **If NEEDS_REVISION**: [List specific changes]
   ```

6. **Report Results**
   - Display verdict with complexity score
   - If FAIL: list what to delete/simplify
   - If PASS: ready for `/speckit.tasks`

## Rules
- **K.I.S.S.**: If plan needs >10 bullets to explain, it's too complex
- **NO OPTIMIZATION**: No "scalable", "high-performance", "optimized" without metrics
- **DELETE > REDUCE**: Better to remove a feature than complicate it
- **TASK COUNT MAX 15**: More tasks = hidden complexity
