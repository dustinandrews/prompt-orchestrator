# Tasks: Spec Directory Context Injection & Tamper Detection

**Input**: Design documents from `specs/002-spec-context-injection/`
**Prerequisites**: plan.md, spec.md, research.md

**Tests**: Not requested — manual verification per Independent Test criteria.

## Format: `[ID] [Story] Description`

- **[Story]**: Which user story this task belongs to (US1, US2)
- Include exact file paths

---

## Phase 1: User Story 1 - Agent Works in Correct Spec Directory (Priority: P1) 🎯 MVP

**Goal**: Replace the flawed `find_feature_dir()` scan with a validated read from `.specify/feature.json`, and inject the spec directory path into every step prompt.

**Independent Test**: Create a feature branch, verify the spec directory path appears in subsequent step prompts.

- [X] T001 [US1] Implement `validate_feature_context()` in `.setup/run_steps.py` — read `feature_directory` from `.specify/feature.json`, extract short name from directory name, cross-check against current git branch name (both inline, no separate helpers), abort with mismatch message. Fall back to `find_feature_dir()` if `feature.json` missing.
- [X] T002 [US1] Modify `run_workflow()` in `.setup/run_steps.py` — call `validate_feature_context()` at start, prepend `SPEC_DIR: specs/NNN-name` to every step prompt after step 1 (specify step has no directory yet).

**Checkpoint**: US1 functional — agents receive spec directory context in all prompts after the specify step.

---

## Phase 2: User Story 2 - Cross-Spec Modification Is Detected and Stopped (Priority: P1)

**Goal**: After each step, detect if any file outside the assigned spec directory was modified and abort with a clear message.

**Independent Test**: Create a file change in a non-assigned spec directory during a step, verify the workflow aborts with a descriptive message.

- [X] T003 [US2] Implement `check_spec_tampering(project_root, assigned_spec)` in `.setup/run_steps.py` — run `git diff --name-only HEAD -- specs/`, filter to paths not under `assigned_spec`, `sys.exit(1)` with message identifying affected directory and file.
- [X] T004 [US2] Integrate `check_spec_tampering()` into `run_workflow()` in `.setup/run_steps.py` — call after each successful step execution, before verification.

**Checkpoint**: Both stories functional — context injection + tamper detection working.

---

## Dependencies & Execution Order

- **US1**: No dependencies — can start immediately
- **US2**: No dependencies on US1 — both modify independent functions in `.setup/run_steps.py`
- **Implementation order**: US1 → US2 (sequential, single file)

### Within Each User Story

- Implement function, then integrate into workflow loop
- Verify independently before moving to next

---

## Implementation Strategy

### MVP (US1 + US2 together)

1. Implement US1 tasks (context injection)
2. Implement US2 tasks (tamper detection)
3. Manual verification: run a feature creation cycle end-to-end

Each story is independently testable but delivered as a single increment since both are P1 and modify the same file.

---

## Notes

- All tasks modify only `.setup/run_steps.py` — no new files, no dependencies
- Git branch reading and name extraction are inlined into `validate_feature_context()` — no separate helper functions
- Manual verification per Independent Test criteria
- Commit after each logical group
