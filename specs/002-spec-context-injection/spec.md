# Feature Specification: Spec Directory Context Injection & Tamper Detection

**Feature Branch**: `004-spec-context-injection`
**Created**: 2026-06-03
**Status**: Clarified
**Input**: User description: "Inject context into each request that points to the current branch directory to keep agents on track. Detect tampering with previous specs and abort."

## Clarifications

### Session 2026-06-03

- Q: Recovery after abort? → A: Operator fixes affected documents manually and restarts from the aborted step. Auto-recovery is out of scope for now.
- Q: What directories are monitored for tamper detection? → A: Only `specs/<NNN>-<name>/` subdirectories.
- Q: What happens when spec context is missing or corrupted? → A: Abort with clear message instructing operator to re-run `/speckit.specify` or verify setup.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Agent Works in Correct Spec Directory (Priority: P1)

When a feature branch is created, the branch creation script records the current spec directory path. All subsequent workflow steps receive this path as context so agents know which directory to operate in. Agents create and modify files only within their assigned spec directory.

**Why this priority**: This is the core value of the feature - preventing cross-feature contamination is essential for workflow correctness.

**Independent Test**: Create a feature branch, then verify that the spec directory path is available as context to all subsequent workflow steps and that agent prompts reference it.

**Acceptance Scenarios**:

1. **Given** a feature branch has been created with the branch creation script, **When** any subsequent workflow step begins, **Then** the step prompt includes the spec directory path.
2. **Given** an agent receives a prompt with a spec directory path, **When** the agent performs file write operations, **Then** all writes go to paths under the assigned spec directory.

---

### User Story 2 - Cross-Spec Modification Is Detected and Stopped (Priority: P1)

When a file is modified in a spec directory that does not match the currently assigned one, the workflow detects this and aborts with a clear message identifying the affected directory and file.

**Why this priority**: Integrity of all feature specs must be preserved. Undetected cross-spec modification could silently corrupt prior work.

**Independent Test**: Create a file change in a non-assigned spec directory and verify the workflow detects it and aborts with a descriptive message.

**Acceptance Scenarios**:

1. **Given** the current feature is assigned to `specs/002-my-feature`, **When** a file in `specs/001-other-feature` is created or modified, **Then** the system detects the change and aborts the current workflow step. The operator then manually restores the affected file (e.g., via git) and restarts the workflow from the aborted step.
2. **Given** an abort due to cross-spec modification, **When** the abort message is shown, **Then** it includes the affected directory path, the modified file name, and the assigned spec directory.

---

### Edge Cases

- What happens when the spec context is missing or corrupted at the start of a workflow step? The step aborts with a message instructing the operator to re-run `/speckit.specify` or verify setup.
- What happens after a cross-spec modification abort? The operator manually restores the affected file and restarts the workflow from the aborted step. Auto-recovery is out of scope for now.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The branch creation script MUST record the spec directory path so that all subsequent workflow steps can reference it.
- **FR-002**: Every workflow step prompt (plan, tasks, implement, etc.) MUST include the assigned spec directory path as context.
- **FR-003**: The system MUST detect file modifications (create, update, delete) in `specs/<NNN>-<name>/` subdirectories that are not the currently assigned one and abort the workflow step.
- **FR-004**: Abort messages MUST identify the affected spec directory path, the modified file, and the assigned spec directory.
- **FR-005**: If the spec context (assigned spec directory) is missing or corrupted when a workflow step starts, the system MUST abort with a message instructing the operator to re-run `/speckit.specify` or verify the project setup.

### Key Entities *(include if feature involves data)*

- **Spec Directory**: A directory under `specs/` named with a numeric prefix and feature short name. Contains all artifacts for a single feature.
- **Spec Context**: The spec directory path recorded by the branch creation script and injected into subsequent workflow step prompts.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Every workflow step after branch creation receives the correct spec directory path in its prompt.
- **SC-002**: Cross-spec directory modifications are detected and abort the workflow step before any downstream step runs.
- **SC-003**: Abort messages always identify the affected directory, modified file, and assigned spec directory.

## Assumptions

- Agents operate one at a time per workflow instance, so there is a single assigned spec directory at any given moment.
- The specify step runs first and creates the spec directory; it does not receive directory context because none exists yet.
- Context is established when the branch creation script runs, which happens after the specify step creates the spec directory.
- Read-only access across spec directories (for reference) is permitted and should not trigger tamper detection.
- Auto-recovery from detected cross-spec modifications is out of scope. Recovery is manual via git operations.
