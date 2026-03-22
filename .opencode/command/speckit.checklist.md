---
description: Generate requirements quality checklist. One step of many. Do this step and stop.
directive: DO NOT READ THIS FILE. EXECUTE ONLY via /speckit.checklist.
---

## COMMAND: CHECKLIST

Write checklist to `specs/XXX-feature/checklists/[domain].md`.

**Requires**: `specs/XXX-feature/spec.md` exists.

**Workflow**:
1. Read spec.md, plan.md (if exists), tasks.md (if exists)
2. Clarify checklist focus (up to 3 questions, one at a time)
3. Generate "unit tests for requirements" — validate requirement quality, NOT implementation
4. Write to `specs/XXX-feature/checklists/[domain].md`
5. STOP — do not write any other files

## Rules

- **STOP** after checklist written
- **Test requirements, not code**: "Are requirements complete?" not "Does button work?"
- **MAX 5 questions** during clarification
- **Preserve existing checklists** — append only
- **ERROR** if spec.md missing → stop
