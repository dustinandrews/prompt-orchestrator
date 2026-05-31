---
description: Create feature specification. One step of many. Do this step and stop.
directive: DO NOT READ THIS FILE. EXECUTE ONLY via /speckit.specify.
---

## COMMAND: SPECIFY
Convert the user spec into a formal development spec with user stories and acceptance criteria.
Fill out `.specify/templates/spec-template.md` and write to `specs/XXX-feature/spec.md`.

**Workflow**:
1. Parse feature description from $ARGUMENTS
2. Create branch: `.specify/scripts/bash/create-new-feature.sh "$ARGUMENTS" --json --short-name "short-name"`
3. Fill template → `specs/XXX-feature/spec.md`
4. STOP — do not write any other files

## Rules

- **STOP** after spec.md written
- **NO implementation details** (no frameworks, languages, databases)
- **MAX 3 [NEEDS CLARIFICATION]** markers
- **ERROR** if no description provided → stop and report
