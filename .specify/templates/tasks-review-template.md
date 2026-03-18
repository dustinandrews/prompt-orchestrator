---
description: Review task list for hidden complexity and bloat
handoffs:
  - label: Fix Tasks
    agent: speckit.tasks
    prompt: Remove bloat and simplify task breakdown
---

# /speckit.tasks-review

## Purpose
Final checkpoint before implementation. Review task list for hidden complexity, unnecessary tasks, and gold plating.

## Input
- `specs/XXX-feature/tasks.md` (task list)
- `specs/XXX-feature/plan.md` (technical plan)
- `.specify/memory/constitution.md` (project constitution)

## Review Checklist

### Task Sanity
- [ ] **Task Count**: ≤10 tasks for MVP? (If >10, something's wrong)
- [ ] **Task Size**: Each fits in 1-4 hours?
- [ ] **No Premature Tasks**: No "optimize", "refactor", or "polish" before "works"
- [ ] **No Future Tasks**: No "later we can add..."

### Constitution Check
- [ ] **Test Coverage**: Every task has test criteria?
- [ ] **Library Boundary**: Tasks respect library separation?
- [ ] **CLI Focus**: Tasks build text I/O interfaces?

### Bloat Detection
- [ ] **Setup Tasks**: Minimized (not 5 tasks of "configure X")
- [ ] **Boilerplate**: Eliminated (use existing patterns)
- [ ] **Documentation**: 1 task max (code should be clear)
- [ ] **Edge Cases**: Only critical ones (80/20 rule)

## Task Categories (REJECT if wrong ratio)
- **Core Functionality**: 60-70% of tasks
- **Tests**: 20-30% of tasks
- **Setup/Config**: <10% of tasks
- **Docs/Polish**: <5% of tasks (MVP only)

## Output

Create `specs/XXX-feature/tasks-review.md`:

```markdown
# Tasks Review: [FEATURE NAME]

**Date**: [DATE]
**Reviewer**: speckit.tasks-review
**Status**: [PASS | NEEDS_REVISION | REJECT]

## Metrics
- **Total Tasks**: [N]
- **Core Tasks**: [N] ([P]%)
- **Test Tasks**: [N] ([P]%)
- **Setup Tasks**: [N] ([P]%)
- **Bloat Tasks**: [N]

## Tasks to DELETE
| Task | Reason | Action |
|------|--------|--------|
| [ID] | [Why it's bloat] | Remove |

## Tasks to SIMPLIFY
| Task | Current | Simplified |
|------|---------|------------|
| [ID] | [Complex version] | [Simple version] |

## Missing Tasks
| Task | Priority | Justification |
|------|----------|---------------|
| [Description] | [P1/P2] | [Why needed] |

## Approval
**Ready for implementation**: [YES | NO]
**If NO**: Fix issues, regenerate tasks, re-review
```

## Rules
- **DELETE MERCILESSLY**: If in doubt, cut it out
- **ONE-THIRD RULE**: MVP should be implementable in 1/3 the time of "complete" version
- **NO PERFECT**: "Works" > "Perfect" for every task
