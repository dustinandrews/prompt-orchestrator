# Implementation Plan: Smolagents Backend Support

**Branch**: `001-smolagents-backend` | **Date**: 2026-05-31 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-smolagents-backend/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command.

**Artifacts generated**:
- [research.md](research.md) — Phase 0 research (CodeAgent API, file tools, auth, integration pattern)
- [data-model.md](data-model.md) — BackendConfig, SmolagentsPrompt, FileTool entities and relationships
- [contracts/backend-interface.md](contracts/backend-interface.md) — Backend execution contract
- [quickstart.md](quickstart.md) — Implementation guide with modified file list and smoke test commands

## Summary

Add a `--backend smolagents` flag to `prompt-orchestrator run` that routes execution through a `CodeAgent + HfApiModel` from the `smolagents` library, while keeping `opencode` as the default backend. The smolagents backend reads the same `.md` command files and templates, assembles them into a prompt, executes via a CodeAgent with file read/write/search tools, and returns an `ExecutionResult` compatible with the existing verification, retry, and hashing logic.

## Technical Context

**Language/Version**: Python >=3.11  
**Primary Dependencies**: pyyaml>=6.0, smolagents (new)  
**Storage**: filesystem — specs/, .orchestrator/command/, .orchestrator/templates/  
**Testing**: pytest  
**Target Platform**: CLI / Linux  
**Project Type**: CLI tool (library with CLI entry points)  
**Performance Goals**: N/A — developer tool, not performance-sensitive  
**Constraints**: opencode remains default; zero backward-compatibility regression for existing users  
**Scale/Scope**: Single developer; no concurrent-access concerns  

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Assessment | Status |
|-----------|-----------|--------|
| **I. Lean Development** | Adding a second backend (smolagents) justifies the backend abstraction that was previously single-use-only. The constitution states _"Do not add generic interfaces unless a second concrete variant exists"_ (I-13) — this feature creates that second variant. The implementation is minimal: one CLI flag, one conditional branch, one new module. No overengineering. | PASS |
| **III. CLI Interface** | `--backend` flag follows stdin/args → stdout, errors → stderr protocol. | PASS |
| **IV. Test-First** | Tests for new backend must be written before implementation. | PASS (requires enforcement) |
| **VII. Python Stack** | Uses existing Python >=3.11. Adds smolagents as a dependency, which aligns with "battle-tested over build-from-scratch" (Principle X). | PASS |
| **IX. MVP-Focus** | Spec explicitly starts with just the `specify` step for validation, then expands to full 10-step workflow. | PASS |
| **X. Battle-Tested** | Uses smolagents library rather than building a new agent framework from scratch. | PASS |
| **XI. K.I.S.S.** | Conditional `if backend == "smolagents"` path is the simplest possible integration. | PASS |
| **XII. One Thing** | Single feature: add alternate backend. No scope creep. | PASS |

**Post-Design Re-check** (after Phase 0+1):

| Principle | Re-assessment | Status |
|-----------|--------------|--------|
| **I. Lean Development** | Design creates 3 small Tool subclasses (read/write/search) + 2 functions. No factory pattern, no abstract backend registry, no plugin system. The conditional `if/else` is the simplest possible dispatch. No dead code. | PASS |
| **IV. Test-First** | Tests for `build_smolagents_prompt` and `execute_smolagents` must be written before code. Recommend existing `test_run_steps.py` pattern. | PASS (enforce in implementation) |
| **VII. Python Stack** | smolagents >=1.17.0 added as dependency. Uses `InferenceClientModel` which depends on `huggingface-hub` — already battle-tested. | PASS |
| **IX. MVP-Focus** | Phase 1 design is intentionally minimal: specify-step-only validation first, then expand to full workflow. `research.md` documents this explicitly. | PASS |
| **XI. K.I.S.S.** | Design is 3 files: `cli.py` (+1 flag), `runner.py` (+2 functions), `pyproject.toml` (+1 dep). No new modules, no refactoring of existing code. | PASS |

**Result**: All gates PASS. No violations to track.

## Project Structure

### Documentation (this feature)

```text
specs/001-smolagents-backend/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
prompt_orchestrator/
├── __init__.py
├── cli.py               # Add --backend flag to argparse
├── runner.py            # Add backend dispatch, build_smolagents_prompt(), execute_smolagents()
├── scaffold/            # Unchanged
└── project_skeleton/    # Unchanged

tests/
├── __init__.py
└── test_run_steps.py    # Add smolagents backend tests
```

**Structure Decision**: Single project — no new packages or submodules. All changes go into `runner.py` (new functions) and `cli.py` (new argparse flag). This minimizes diff and complexity.

## Complexity Tracking

No constitution violations to justify.
