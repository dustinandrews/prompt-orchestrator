---
description: Create or update project constitution. One step of many. Do this step and stop.
directive: DO NOT READ THIS FILE. EXECUTE ONLY via /speckit.constitution.
---

## COMMAND: CONSTITUTION

Fill out `.specify/templates/constitution-template.md` and write to `.specify/memory/constitution.md`.

**Workflow**:
1. Load constitution-template.md (if memory/constitution.md doesn't exist)
2. Replace placeholder tokens with concrete values
3. Propagate changes to dependent templates
4. Fill template → `.specify/memory/constitution.md`
5. STOP — do not write any other files

## Rules

- **STOP** after constitution.md written
- **Version bump** if principles changed (MAJOR/MINOR/PATCH)
- **No bracket tokens** left in final output
