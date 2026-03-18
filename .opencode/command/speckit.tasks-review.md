---
description: Final review of task list before implementation
handoffs:
  - label: Fix Tasks
    agent: speckit.tasks
    prompt: Remove bloat and regenerate task list
    send: true
  - label: Implement
    agent: speckit.implement
    prompt: Execute approved task list
    send: true
scripts:
  sh: scripts/bash/list-specs.sh
  ps: scripts/powershell/list-specs.ps1
---

# /speckit.tasks-review

## User Input
```
$ARGUMENTS
```

## Execution Flow

1. **Identify Target Tasks**
   - Parse $ARGUMENTS for feature name/number
   - Target: `specs/XXX-feature/tasks.md`
   - Verify plan.md exists and was reviewed

2. **Load Required Files**
   - Read `.specify/memory/constitution.md`
   - Read `specs/XXX-feature/plan.md` (verify coverage)
   - Read `specs/XXX-feature/tasks.md` (target)
   - Read `.specify/templates/tasks-review-template.md`

3. **Execute Review**

   ### Task Count Sanity
   - Total tasks: >15 = FLAG (likely bloat)
   - Core functionality tasks: Should be 60-70%
   - Test tasks: Should be 20-30%
   - Setup/config tasks: Should be <10%
   - Polish/doc tasks: Should be <5% for MVP

   ### Individual Task Review
   For each task:
   - **Size**: >4 hours? Flag as too big
   - **Premature**: "optimize", "refactor", "polish" before "works"? FLAG
   - **Future**: "later", "v2", "future enhancement"? DELETE
   - **Test Coverage**: Every core task has corresponding test task?

   ### Bloat Detection
   - **Setup Tasks**: More than 2? Consolidate or eliminate
   - **Boilerplate**: "create folder structure", "setup config"? Minimize
   - **Documentation**: >1 doc task? Excessive for MVP
   - **Edge Cases**: Non-critical edge cases taking >20% of tasks? Cut

   ### Constitution Check
   - **Test-First**: Are test tasks BEFORE implementation tasks?
   - **Library Boundary**: Do tasks respect library/module boundaries?
   - **CLI Focus**: Are I/O interface tasks prioritized?

4. **Determine Verdict**
   - **PASS**: Lean, balanced, ready to implement
   - **NEEDS_REVISION**: Remove bloat, rebalance, then regenerate
   - **REJECT**: Fundamental misalignment (rare at this stage)

5. **Generate Output**
   
   Create `specs/XXX-feature/tasks-review.md`:
   ```markdown
   # Tasks Review: [FEATURE NAME]
   
   **Date**: [DATE]
   **Reviewer**: speckit.tasks-review
   **Status**: [PASS | NEEDS_REVISION | REJECT]
   
   ## Task Distribution
   | Category | Count | Percentage | Target | Status |
   |----------|-------|------------|--------|--------|
   | Core Functionality | [N] | [P%] | 60-70% | [OK/HIGH/LOW] |
   | Tests | [N] | [P%] | 20-30% | [OK/HIGH/LOW] |
   | Setup/Config | [N] | [P%] | <10% | [OK/HIGH] |
   | Docs/Polish | [N] | [P%] | <5% | [OK/HIGH] |
   | **TOTAL** | [N] | 100% | <15 | [OK/HIGH] |
   
   ## Tasks to DELETE
   | Task ID | Task Description | Reason | Action |
   |---------|------------------|--------|--------|
   | [ID] | [Text] | [Why bloat] | Remove |
   
   ## Tasks to SIMPLIFY
   | Task ID | Current | Simplified | New Estimate |
   |---------|---------|------------|--------------|
   | [ID] | [Complex] | [Simple] | [Hours] |
   
   ## Missing Tasks
   | Description | Priority | Justification |
   |-------------|----------|---------------|
   | [Task] | [P1/P2] | [Why needed] |
   
   ## Constitution Check
   - [ ] Test tasks precede implementation tasks
   - [ ] Library boundaries respected
   - [ ] CLI/text I/O prioritized
   - [ ] No premature optimization tasks
   
   ## Decision
   **Status**: [PASS/NEEDS_REVISION/REJECT]
   **If REVISE**: Remove flagged tasks, rebalance, regenerate
   **If PASS**: Proceed to `/speckit.implement`
   ```

6. **Report Results**
   - Show task distribution pie (text)
   - List tasks to delete (with reasons)
   - If PASS: confirm ready for implementation

## Rules
- **ONE-THIRD RULE**: MVP tasks should be implementable in 1/3 time of "complete" version
- **DELETE FIRST**: Always try removing before simplifying
- **NO PERFECT TASKS**: "Works" is acceptable; "beautiful" is not a task
- **MAX 15 TASKS**: Hard limit. Forces prioritization.
