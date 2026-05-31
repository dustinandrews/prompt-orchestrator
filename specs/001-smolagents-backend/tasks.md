---

description: "Task list for smolagents backend implementation"

---

# Tasks: Smolagents Backend Support

**Input**: Design documents from `/specs/001-smolagents-backend/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/backend-interface.md, quickstart.md

**Tests**: Test tasks are included to enforce TDD per constitution Principle IV.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- This project uses `prompt_orchestrator/` as the source directory, `tests/` for tests

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and dependency management

- [x] T001 Add `smolagents>=1.17.0` to `dependencies` in `pyproject.toml`
- [x] T002 Install smolagents via `pip install smolagents` in the local venv

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: CLI flag, config changes, and thread-through — these must be complete before any user story can be implemented.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T003 [P] Add `--backend` argument to the `run` subcommand parser in `prompt_orchestrator/cli.py` with `default="opencode"` and `choices=["opencode", "smolagents"]`
- [x] T004 Add `backend: str = "opencode"` field to the `Config` dataclass in `prompt_orchestrator/runner.py`
- [x] T005 Thread `args.backend` from `cli.py` `cmd_run()` through to `runner.main()` and `run_workflow()` — pass as `backend` kwarg or extend `Config`
- [x] T006 Add backend validation in `run_workflow()`: error on unrecognized backend values (FR-010)

**Checkpoint**: Foundation ready — CLI accepts `--backend`, Config carries it, backend dispatch point exists

---

## Phase 3: User Story 1 - Run Workflow with Smolagents Backend (Priority: P1) 🎯 MVP

**Goal**: Developer can run `prompt-orchestrator run --backend smolagents` and the workflow executes using CodeAgent + InferenceClientModel.

**Independent Test**: Run `prompt-orchestrator run --backend smolagents specify` (step 1) and verify a valid spec.md is written to the feature directory.

### Tests for User Story 1 ⚠️

- [x] T007 [P] [US1] Test `build_smolagents_prompt()` reads same files as `build_opencode_cmd()` in `tests/test_run_steps.py`

### Implementation for User Story 1

- [x] T008 [US1] Implement `ReadFileTool` custom smolagents `Tool` class in new module `prompt_orchestrator/smolagents_tools.py` (file system read)
- [x] T009 [P] [US1] Implement `WriteFileTool` custom smolagents `Tool` class in `prompt_orchestrator/smolagents_tools.py` (file system write with parent dir creation)
- [x] T010 [P] [US1] Implement `SearchFilesTool` custom smolagents `Tool` class in `prompt_orchestrator/smolagents_tools.py` (glob-based file search)
- [x] T011 [US1] Implement `build_smolagents_prompt()` in `prompt_orchestrator/runner.py` — reads `cmd.files` tuple, concatenates content into single prompt string (same files as opencode)
- [x] T012 [US1] Implement `execute_smolagents()` in `prompt_orchestrator/runner.py` — creates `CodeAgent` with `InferenceClientModel` + file tools, calls `agent.run(prompt)`, wraps result in `ExecutionResult`
- [x] T013 [US1] Wire conditional dispatch in `run_workflow()`: replace `build_opencode_cmd`/`execute_opencode` block with `if config.backend == "smolagents"` branch calling `build_smolagens_prompt`/`execute_smolagens`, else existing opencode path
- [x] T014 [US1] Ensure `execute_smolagents()` uses `HF_TOKEN` from environment (research.md §4) — `InferenceClientModel` auto-reads this

**Checkpoint**: At this point, `--backend smolagents` should work end-to-end for the specify step

---

## Phase 4: User Story 2 - Default Backend Unchanged (Priority: P1)

**Goal**: Running `prompt-orchestrator run` without `--backend` uses opencode with identical behavior to pre-feature version.

**Independent Test**: Run `prompt-orchestrator run` without `--backend` flag and verify opencode is invoked (exit code matches expected, output files produced).

### Tests for User Story 2 ⚠️

- [x] T015 [P] [US2] Test that `cmd_run()` defaults `backend` to `"opencode"` when `--backend` is omitted in `tests/test_run_steps.py`
- [x] T016 [US2] Test that `run_workflow()` with `backend="opencode"` follows the existing opencode code path (no regression) in `tests/test_run_steps.py`

### Implementation for User Story 2

- [x] T017 [US2] Verify opencode dispatch path is completely unchanged when `config.backend == "opencode"` (or default) — the conditional must NOT affect opencode behavior

**Checkpoint**: Backward compatibility confirmed — opencode users see zero change

---

## Phase 5: User Story 3 - Verification Works for Both Backends (Priority: P2)

**Goal**: Verification, retry, and hashing mechanisms work identically regardless of backend choice.

**Independent Test**: Run a workflow step that fails verification with `--backend smolagents` and confirm retry logic triggers (same as opencode behavior).

### Tests for User Story 3 ⚠️

- [x] T018 [P] [US3] Test that `verify_files()` produces same result when run after smolagents vs opencode execution in `tests/test_run_steps.py`
- [x] T019 [US3] Test that `compute_retry_decision()` handles smolagens `ExecutionResult` identically to opencode's in `tests/test_run_steps.py`
- [x] T020 [US3] Test that invalid `--backend` value produces error listing valid options (FR-010) in `tests/test_run_steps.py`
- [x] T021 [US3] Test that smolagens error produces `ExecutionResult(exit_code=1, error_msg=...)` matching the opencode error contract in `tests/test_run_steps.py`

### Implementation for User Story 3

- [x] T022 [US3] Handle smolagents `ExecutionResult` in review file hash tracking — verify hashing works for smolagent-generated files (no change needed if `compute_file_hash` is backend-agnostic, which it is)

**Checkpoint**: Smolagents backend is fully integrated with verification, retry, and error handling

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T023 [P] Run `pip install -e .` to verify pyproject.toml dependency resolution works with new smolagents dependency
- [ ] T024 Run quickstart.md smoke tests: `prompt-orchestrator run --backend smolagents --step 1` (requires HF_TOKEN)
- [x] T025 Run full test suite: `python -m pytest tests/` — all existing tests must pass (SC-003)
- [ ] T026 Run full workflow smoke test: `prompt-orchestrator run --backend smolagents` (requires HF_TOKEN)
- [x] T027 Update `AGENTS.md` SPECKIT section to reference the implementation plan if needed

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup — BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - US1 (Phase 3) can start immediately after Foundational
  - US2 (Phase 4) can start in parallel with US1
  - US3 (Phase 5) depends on US1 (needs smolagents backend to exist)
- **Polish (Phase 6)**: Depends on all user stories

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational — No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational — No dependencies on other stories (verification-only story)
- **User Story 3 (P2)**: Depends on US1 — Needs smolagents backend to exist to test verification

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Tools before prompt builder
- Prompt builder before executor
- Executor before dispatch wiring

### Parallel Opportunities

- T003 and T004 can run in parallel (different files, different concerns)
- T008, T009, T010 can run in parallel (all smolagents file tools, independent)
- T015 and T016 can run in parallel (both tests, no interdependencies)
- US1 and US2 can be worked on in parallel
- T023-T025 can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch all file tool tasks together:
Task: "Implement ReadFileTool in prompt_orchestrator/smolagents_tools.py"
Task: "Implement WriteFileTool in prompt_orchestrator/smolagents_tools.py"
Task: "Implement SearchFilesTool in prompt_orchestrator/smolagents_tools.py"
```

```bash
# Then launch sequential build → execute → wire
Task: "build_smolagents_prompt() depends on file tools being available"
Task: "execute_smolagents() depends on build_smolagents_prompt()"
Task: "Wire dispatch depends on execute_smolagents()"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1 (smolagents backend)
4. **STOP and VALIDATE**: `--backend smolagents` works for specify step
5. Deploy/demo if ready

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently (smolagents works ✓)
3. Add User Story 2 → Test independently (no regression ✓)
4. Add User Story 3 → Test independently (verification works ✓)

### Parallel Team Strategy

With multiple developers:
1. Complete Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (smolagents backend)
   - Developer B: User Story 2 (backward compatibility tests)
3. Both complete, then Developer C: User Story 3 (verification cross-cutting)
4. Polish tasks can be parallelized

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- The smolagens backend is a pure addition — no existing code is modified (except adding a conditional branch)
