---
description: Review specification for constitution compliance and simplicity
handoffs:
  - label: Clarify Issues
    agent: speckit.clarify
    prompt: Address review findings before planning
---

# /speckit.spec-review

## Purpose
Review the feature specification for compliance with project constitution and identify over-engineering before planning begins.

## Input
- `specs/XXX-feature/spec.md` (current specification)
- `.specify/memory/constitution.md` (project constitution)

## Review Checklist

### Constitution Compliance
- [ ] **Principle Alignment**: Does the spec violate any core principles?
- [ ] **Library-First**: Can this feature start as a standalone, testable library?
- [ ] **CLI Interface**: Is the user interaction model text-based and simple?
- [ ] **Test-First**: Are acceptance criteria defined before implementation?
- [ ] **YAGNI**: Are there requirements that anticipate future needs?

### Anti-Patterns (REJECT if found)
- [ ] **Gold Plating**: Requirements that "would be nice" but aren't essential
- [ ] **Premature Abstraction**: Generic frameworks when specific solution works
- [ ] **Scope Creep**: Features beyond the stated problem scope
- [ ] **Tech Speculation**: Assuming specific libraries/frameworks needed

### Simplicity Review
- [ ] Can this be solved with 3 or fewer user stories?
- [ ] Are success criteria measurable without implementation details?
- [ ] Are there [NEEDS CLARIFICATION] markers that hide complexity?

## Output

Create `specs/XXX-feature/spec-review.md`:

```markdown
# Specification Review: [FEATURE NAME]

**Date**: [DATE]
**Reviewer**: speckit.spec-review

## Findings

### Defects Found
1. **[SEVERITY]**: [Description of issue] → **Fix**: [Required change]

### Constitution Violations
1. **[PRINCIPLE]**: [How spec violates] → **Fix**: [Required change]

## Review Result
STATUS: [PASS | FAIL]

If FAIL: [one sentence reason for failure]
```

## Rules
- **BE RUTHLESS**: Reject specs with >3 P2/P3 stories (bloat indicator)
- **NO MERCY**: Any "framework" or "platform" language = REJECT
- **FIX NOW**: All defects must be addressed before planning
- **EMPOWERMENT**: You are authorized and required to cut or punt out of scope work. E.G. Feature Foo is out of scope for this iteration. First on deck for next sprint.
