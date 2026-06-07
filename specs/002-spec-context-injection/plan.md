# Implementation Plan: Spec Directory Context Injection & Tamper Detection

**Branch**: `004-spec-context-injection` | **Date**: 2026-06-03 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `specs/002-spec-context-injection/spec.md`

## Summary

Three additive changes to `run_steps.py`: (1) replace `find_feature_dir()` (which scans specs/ for the highest-numbered directory — the root cause of agent confusion) with a direct read from `.specify/feature.json` and a cross check with `git branch`; (2) prepend `SPEC_DIR: <path>` to every step prompt after the specify step; (3) run `git diff --name-only HEAD -- specs/` after each step — if any file outside the assigned spec dir was modified, abort. No new files, no new dependencies.

## Technical Context

**Language/Version**: Python 3.11+, bash  
**Primary Dependencies**: None new — uses existing git, Python stdlib, speckit scripts  
**Storage**: `.specify/feature.json` (already persists `feature_directory`)  
**Testing**: pytest (existing project testing pattern)  
**Target Platform**: Linux (dev environment)  
**Project Type**: Workflow scripts / internal tooling (modifies existing orchestration)  
**Performance Goals**: N/A — step overhead is negligible  
**Constraints**: Must integrate with existing `run_steps.py`/`steps.yaml` workflow and existing speckit extension scripts  
**Scale/Scope**: Single repo, single team

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

All gates pass. Key principle checks:
- **I. Lean Development** — 4 FRs, no new deps, solves real agent confusion
- **IV. Test-First** — detection mechanism tests deferred to tasks
- **IX. MVP-Focus** — spec was trimmed, plan is 3 additive changes to one file
- **X. Battle-Tested** — uses git diff (battle-tested) for detection
- **XI. K.I.S.S** — no daemons, no watchers, one file modified

**Result**: No constitution violations.

## Project Structure

### Documentation

```text
specs/002-spec-context-injection/
├── plan.md              # This file
├── research.md          # Phase 0 — technology choices validated
└── tasks.md             # (created by /speckit.tasks)
```

### Source Code

The only file modified is `.setup/run_steps.py` — three additive changes:

| # | Change | What it does |
|---|--------|-------------|
| 1 | `validate_feature_context()` | Reads `feature_directory` from `.specify/feature.json`. Extracts short name (e.g., `spec-context-injection`) from the path and cross-checks it against the current git branch name. If they don't match, aborts with a message showing the mismatch. Falls back to existing `find_feature_dir()` if `feature.json` missing (backward compat). |
| 2 | Inject `SPEC_DIR` in `run_workflow()` | Prepends `SPEC_DIR: specs/NNN-name` to `config.message` for every step after step 1 (specify step creates the directory, so step 1 has no context yet). |
| 3 | `check_spec_tampering()` | Runs `git diff --name-only HEAD -- specs/` after the step completes. If any changed path doesn't start with the assigned spec dir, logs the file and calls `sys.exit(1)`. |

The only data involved is the `feature_directory` string already persisted in `.specify/feature.json`. No new config files, no bash scripts, no prompt template modifications.

## Complexity Tracking

No constitution violations — table omitted.
