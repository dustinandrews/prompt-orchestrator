# Feature Specification: Smolagents Backend Support

**Feature Branch**: `001-smolagents-backend`  
**Created**: 2026-05-31  
**Status**: Draft  
**Input**: User description: "Add a --backend smolagents option to prompt-orchestrator run that successfully completes a full spec-kit workflow using CodeAgent + HfApiModel, while keeping opencode as the default backend and changing nothing else."

## User Scenarios & Testing

### User Story 1 - Run workflow with smolagents backend (Priority: P1)

A developer wants to run a prompt-orchestrator workflow using Hugging Face's smolagents AI backend instead of the default opencode backend. They pass `--backend smolagents` and the full spec-kit workflow (specify, plan, implement, etc.) completes successfully using the smolagents agent.

**Why this priority**: This is the core feature — enabling a new backend choice for workflow execution.

**Independent Test**: Can be fully tested by running any spec-kit workflow with `--backend smolagents` and observing successful completion across all steps.

**Acceptance Scenarios**:

1. **Given** a prompt-orchestrator project, **When** the user runs `prompt-orchestrator run --backend smolagents`, **Then** the workflow executes using the smolagents backend and completes without errors
2. **Given** a prompt-orchestrator project, **When** the user runs `prompt-orchestrator run --backend smolagents specify`, **Then** the specify step produces a valid spec.md file
3. **Given** a workflow step that produces output files, **When** executed with the smolagents backend, **Then** output files are written to the expected locations

---

### User Story 2 - Default backend unchanged (Priority: P1)

A developer runs prompt-orchestrator without specifying a backend. The existing opencode backend is used with no behavior change, preserving backward compatibility.

**Why this priority**: Ensures no regression for existing users.

**Independent Test**: Can be fully tested by running `prompt-orchestrator run` (without `--backend`) and verifying identical behavior to pre-feature behavior.

**Acceptance Scenarios**:

1. **Given** a prompt-orchestrator project, **When** the user runs `prompt-orchestrator run` without `--backend`, **Then** the opencode backend is used
2. **Given** a workflow running with the default backend, **When** it executes a step, **Then** the behavior matches previous opencode-only execution

---

### User Story 3 - Workflow step verification works for both backends (Priority: P2)

A developer runs a workflow with the smolagents backend and relies on verification, retry, and hashing mechanisms to ensure correct step output.

**Why this priority**: Verification and retry logic must work regardless of backend.

**Independent Test**: Can be tested by running a step that fails verification with smolagents and confirming the retry mechanism triggers.

**Acceptance Scenarios**:

1. **Given** a workflow running with `--backend smolagents`, **When** a step produces incorrect output, **Then** the verification step catches the error and retry logic re-executes the step
2. **Given** a workflow running with `--backend smolagents`, **When** a step completes, **Then** output hashing works identically to the opencode backend

### Edge Cases

- What happens when `--backend` is set to an unrecognized value? The system should report an error and list supported backends.
- What happens when Hugging Face API credentials are missing for the smolagents backend? The system should report a clear error about missing configuration.
- How does the system handle network failures when the smolagents backend requires API access? Should retry with appropriate backoff.

## Requirements

### Functional Requirements

- **FR-001**: The system MUST accept a `--backend` CLI parameter on the `run` command
- **FR-002**: The system MUST default `--backend` to `opencode`
- **FR-003**: The system MUST route execution to the smolagents backend when `--backend smolagents` is specified
- **FR-004**: The system MUST route execution to the opencode backend when `--backend opencode` is specified (or when the flag is omitted)
- **FR-005**: The smolagents backend MUST read the same .md command files and templates as the opencode backend
- **FR-006**: The smolagents backend MUST assemble a prompt from command files that is functionally equivalent to the opencode backend's prompt
- **FR-007**: The smolagents backend MUST create a CodeAgent with HfApiModel and file read/write/search tools
- **FR-008**: The smolagents backend MUST return an ExecutionResult compatible with the existing verification and retry logic
- **FR-009**: Verification, retry, and hashing mechanisms MUST work identically for both backends
- **FR-010**: The system MUST report an error for unrecognized `--backend` values, listing supported backends

### Key Entities

- **Backend**: An execution engine for running workflow steps (e.g., opencode, smolagents). Determines how prompts are built and how agents execute commands.
- **ExecutionResult**: The result object produced by a backend after executing a workflow step, containing the output used for verification and hashing.

## Success Criteria

### Measurable Outcomes

- **SC-001**: Users can run `prompt-orchestrator run --backend smolagents specify` and produce a valid spec.md file without errors
- **SC-002**: Users can run a full 10-step spec-kit workflow (specify through implement) with `--backend smolagents` and all steps complete successfully
- **SC-003**: Running `prompt-orchestrator run` without `--backend` produces identical behavior to the pre-feature version (zero regression)
- **SC-004**: Verification passes on step output from both opencode and smolagents backends for the same inputs

## Assumptions

- Users have valid Hugging Face API credentials configured when using the smolagents backend
- The smolagents library (`smolagents`) is installed as a project dependency
- The opencode backend behavior is the baseline for correctness — smolagents output should be equivalent for the same inputs
- Network connectivity to Hugging Face API endpoints is assumed for the smolagents backend
- Existing verification, retry, and hashing logic is reusable without modification for the new backend
