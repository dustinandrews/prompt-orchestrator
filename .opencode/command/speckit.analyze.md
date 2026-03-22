---
description: Analyze cross-artifact consistency. One step of many. Do this step and stop.
directive: DO NOT READ THIS FILE. EXECUTE ONLY via /speckit.analyze.
---

## COMMAND: ANALYZE

Read-only analysis. Output report to console only.

**Requires**: `specs/XXX-feature/tasks.md` exists.

**Workflow**:
1. Verify tasks.md exists
2. Read spec.md, plan.md, tasks.md, constitution.md
3. Check for: duplications, ambiguities, underspecification, constitution violations, coverage gaps, inconsistencies
4. Output analysis report to console
5. STOP — do NOT modify any files

## Rules

- **STOP** after report output
- **READ ONLY** — never modify files
- **MAX 50 findings** — summarize overflow
- **Constitution violations = CRITICAL**
- **ERROR** if prereqs missing → stop
