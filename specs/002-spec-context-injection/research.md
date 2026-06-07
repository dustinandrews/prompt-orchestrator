# Research: Spec Directory Context Injection & Tamper Detection

## Decision 1: Context Storage Mechanism

**Decision**: Use existing `.specify/feature.json` — it already persists `feature_directory` after `/speckit.specify`.

**Rationale**: No new file or mechanism needed. The existing `run_steps.py` already has `find_feature_dir()` but it scans `specs/` for the highest-numbered directory (the root cause of agent confusion). Instead, read the persisted path from `feature.json`.

**Alternatives Considered**:
- Environment variable: Fragile, doesn't persist across `opencode` invocations
- Git branch name convention: Already available but `feature.json` is more explicit and independent from branch naming

## Decision 2: Context Injection into Step Prompts

**Decision**: Modify `run_steps.py` to prepend the spec directory path to the step message for every command after the `specify` step.

**Rationale**: The `build_opencode_cmd()` function already supports `extra_context` for retries. Adding the spec directory to the base message of every step is a minimal change. The step prompts (`.orchestrator/command/orchestrator.*.md`) can reference `{SPEC_DIR}`; the context gets added via `extra_context` or as part of `config.message`.

**Implementation approach**:
1. In `run_workflow()`, read `feature_directory` from `.specify/feature.json`
2. Prepend `"SPEC_DIR: specs/NNN-name"` to the base message for all steps after step 1 (specify creates the directory)

**Alternatives Considered**:
- Modifying all `.orchestrator/command/*.md` files to include a template variable: More intrusive, harder to maintain
- Adding a separate context file: Extra complexity, no benefit over message injection

## Decision 3: Tamper Detection Mechanism

**Decision**: Before each step, record `git ls-tree` state of all `specs/` directories. After the step completes, diff against the recorded state. If any file outside the assigned spec directory was modified, abort.

**Rationale**: Git-based detection is zero-config (git is already required), works on any platform, and provides precise file-level diffs. No watchers, daemons, or filesystem hooks needed.

**Implementation approach**:
1. `PRE` hook: `git ls-tree -r HEAD --name-only specs/` → store in memory
2. `POST` check: `git diff --name-only HEAD` → filter to specs/ paths
3. For each changed file not under the assigned spec directory → abort

**Alternatives Considered**:
- `inotify`/file watchers: Over-engineered, platform-specific
- Python `os.walk` check: Less reliable (misses renames, can't diff as accurately)
- Pre-commit hook: Only catches git commits, not general file writes during agent execution

## Dependency Analysis

No new external dependencies. The implementation uses:
- `json` (Python stdlib) — already available
- `subprocess` for git commands (Python stdlib) — already used
- `pathlib` (Python stdlib) — already used
