---
description: Create feature specification. One step of many. Do this step and stop.
directive: DO NOT READ THIS FILE. EXECUTE ONLY via /speckit.specify.
---

## COMMAND: SPECIFY
Convert the user spec into a formal development spec with user stories and acceptance criteria.
Fill out `.orchestrator/templates/spec-template.md` and write to `specs/XXX-feature/spec.md`.

**Workflow**:
1. Read `userspec.md` to get the feature description
2. **CHECK**: Does this project have a documented technology stack? Look for:
   - `constitution.md` with "Technology Stack" or "Technical Platform" section
   - `AGENTS.md` with tech stack details
   - `README.md` with language/framework specifications
   - Any `.specify/memory/constitution.md` or similar
3. **If tech stack is UNDOCUMENTED**: HALT immediately. Ask the user:
   > "This project does not have a documented technology stack. What language/framework should be used for this feature? Where should I document this?"
4. **If tech stack IS documented**: Proceed to next step
5. Generate a short name (2-4 words) from the description by removing stop words (the, a, an, to, for, etc.)
6. Create feature: `python .setup/run_steps.py create-feature "<description from userspec.md>" --short-name "<generated-short-name>"`
7. The command will output `BRANCH_NAME: XXX-short-name` and create `specs/XXX-short-name/spec.md`
8. Fill the template and write to the created spec file
9. STOP — do not write any other files

## Rules

- **STOP** after spec.md written
- **NO implementation details** (no frameworks, languages, databases)
- **MAX 3 [NEEDS CLARIFICATION]** markers
- **ERROR** if no description provided → stop and report
- **CRITICAL**: NEVER assume Python, TypeScript, or any tech stack. If undocumented, ASK THE USER.
