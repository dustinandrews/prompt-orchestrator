---
description: Clarify specification ambiguities. One step of many. Do this step and stop.
directive: DO NOT READ THIS FILE. EXECUTE ONLY via /speckit.clarify.
---

## COMMAND: CLARIFY

Update `specs/XXX-feature/spec.md` with answers to clarification questions.

**Requires**: `specs/XXX-feature/spec.md` exists.

**Workflow**:
1. Read spec.md
2. Identify up to 5 ambiguities requiring clarification
3. Ask ONE question at a time, wait for answer
4. Update spec.md with resolved answers
5. STOP after all questions answered or user says "done"

## Rules

- **STOP** after all questions answered or user terminates
- **MAX 5 questions** total
- **One question at a time** — wait for answer before next
- **NO tech stack questions** unless absence blocks clarity
- **ERROR** if spec.md missing → stop
