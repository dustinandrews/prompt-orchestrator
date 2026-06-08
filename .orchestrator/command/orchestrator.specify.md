---
description: Create feature specification. One step of many. Do this step and stop.
directive: DO NOT READ THIS FILE. EXECUTE ONLY via /speckit.specify.
---

## COMMAND: SPECIFY
Convert the user spec into a formal development spec with user stories and acceptance criteria.
Fill out `.orchestrator/templates/spec-template.md` and write to `specs/XXX-feature/spec.md`.

**Workflow**:
1. Read `userspec.md` to get the feature description
2. Generate a short name (2-4 words) from the description by removing stop words (the, a, an, to, for, etc.)
3. Create feature: `python .setup/run_steps.py create-feature "<description from userspec.md>" --short-name "<generated-short-name>"`
4. The command will output `BRANCH_NAME: XXX-short-name` and create `specs/XXX-short-name/spec.md`
5. Fill the template and write to the created spec file
6. STOP — do not write any other files

## Rules

- **STOP** after spec.md written
- **NO implementation details** (no frameworks, languages, databases)
- **MAX 3 [NEEDS CLARIFICATION]** markers
- **ERROR** if no description provided → stop and report
