---
description: Review technical plan for over-engineering and constitution compliance
handoffs:
  - label: Revise Plan
    agent: speckit.plan
    prompt: Fix over-engineering issues identified in review
---

# /speckit.plan-review

## Purpose
Review the technical implementation plan for over-engineering, unnecessary complexity, and constitution compliance BEFORE tasks are created.

## Input
- `specs/XXX-feature/plan.md` (technical plan)
- `.specify/memory/constitution.md` (project constitution)
- `specs/XXX-feature/spec.md` (original specification)

## Review Checklist

### Constitution Compliance
- [ ] **Library-First**: Plan shows standalone library with clear boundaries?
- [ ] **CLI Interface**: Plan uses stdin/stdout, not complex APIs?
- [ ] **Test-First**: Testing strategy defined before implementation tasks?
- [ ] **Simplicity**: No unnecessary dependencies or frameworks?

### Over-Engineering Detection
- [ ] **Framework Avoidance**: No "we'll build a framework for..."
- [ ] **Database Minimalism**: SQLite/local files preferred over external DBs
- [ ] **API Simplicity**: REST/text preferred over GraphQL/gRPC/complex protocols
- [ ] **Single Purpose**: Each component does ONE thing well

### Task Breakdown Review
- [ ] Are tasks <4 hours each? (If not, split them)
- [ ] Can any tasks be deleted? (YAGNI check)
- [ ] Are dependencies minimal and explicit?
- [ ] Is there a "make it work" phase before "make it nice"?

## RED FLAGS (Immediate REJECT)
1. **Microservices**: For features that don't need them
2. **Message Queues**: When function calls suffice
3. **Caching Layers**: Before performance is measured
4. **Config Systems**: When env vars work
5. **Generic Abstractions**: "Plugin system", "driver interface", etc.

## Output

Create `specs/XXX-feature/plan-review.md`:

```markdown
# Plan Review: [FEATURE NAME]

**Date**: [DATE]
**Reviewer**: speckit.plan-review
**Status**: [PASS | NEEDS_REVISION | REJECT]

## Complexity Score
- **Tasks**: [N] 
- **Estimated Hours**: [N]
- **Dependencies**: [N external | N internal]
- **VERDICT**: [ACCEPTABLE | TOO_COMPLEX]

## Findings

### Over-Engineering Detected
1. **[COMPONENT]**: [Complex solution] → **Simplify**: [Simple solution]

### Constitution Violations
1. **[PRINCIPLE]**: [Violation] → **Fix**: [Required change]

### Task Issues
1. **Task [N]**: [Issue] → **Fix**: [Simplification]

## Required Changes
- [ ] [Specific change with justification]

## Approval
**Approved for tasks**: [YES | NO - revise first]

**If NO**: Fix issues, regenerate, re-review
```

## Rules
- **K.I.S.S.**: If you can't explain the plan in 5 bullets, it's too complex
- **NO FRAMEWORKS**: Libraries only, no "we'll build a..."
- **MEASURE FIRST**: No optimization without profiling data
