# FullAutoTemplate - Technical Handoff

**Project:** FullAutoTemplate - Reusable template for bootstrapping code generators  
**Location:** `/home/nanobot/.nanobot/workspace/projects/FullAutoTemplate/`  
**Last Updated:** 2026-03-20  
**Status:** ACTIVE - System refactor complete, ready for next test

---

## Quick Reference

```bash
# Create new project from template
python3 .setup/setup.py --project-name myproject --spec "Build a CLI tool that..."

# Run workflow
cd myproject
python3 ._agents_not_allowed/run_steps.py

# Check logs
cat ._agents_not_allowed/workflow_*.log
```

---

## System Overview

**Purpose:** Automate speckit workflow execution without human intervention between steps.

**Architecture:**
1. **steps.yaml** - Single source of truth for workflow
2. **run_steps.py** - Executes commands, handles verification, manages retries
3. **._agents_not_allowed/** - Per-project config and logs (hidden to discourage agent modification)

**Key Principle:** Command runs → Verification checks → Retry if needed → Continue

---

## Workflow Steps (14 Total)

| Step | Command | Model | Verification |
|------|---------|-------|--------------|
| 1 | /speckit.specify | reviewer-model | spec.md exists |
| 2 | /speckit.spec-review | coder-model | spec-review.md PASS |
| 3 | /compact | coder-model | - |
| 4 | /speckit.plan | coder-model | plan.md exists |
| 5 | /speckit.plan-review | coder-model | plan-review.md PASS |
| 6 | /compact | coder-model | - |
| 7 | /speckit.tasks | coder-model | tasks.md exists |
| 8 | /speckit.analyze | coder-model | - |
| 9 | /speckit.tasks-review | coder-model | tasks-review.md PASS |
| 10 | /compact | coder-model | - |
| 11 | /speckit.implement | coder-model | No placeholders in src/ |
| 12 | /compact | coder-model | - |
| 13 | /speckit.test-review | coder-model | test-review.md PASS |
| 14 | /speckit.product-review | reviewer-model | product-review.md PASS |

---

## YAML Configuration

### Model Aliases
```yaml
models:
  - reviewer-model:
      model: "moonshotai/kimi-k2-turbo-preview"
  - coder-model:
      model: "ollama/qwen3.5:35b"
```

### Verification Patterns

**File existence check (e.g., spec.md):**
```yaml
- command: "/speckit.specify"
  verify:
    files:
      - "spec.md"
    retry_step_on_file_not_found: "/speckit.specify"
```

**Review validation (PASS/FAIL parsing):**
```yaml
- command: "/speckit.spec-review"
  verify:
    files:
      - "spec-review.md"
    retry_step_on_fail: "/speckit.spec-review"
    retry_step_on_file_not_found: "/speckit.spec-review"
```

**Implementation validation (placeholder scan):**
```yaml
- command: "/speckit.implement"
  verify_implementation: true
  retry_step_on_fail: "/speckit.implement"
```

---

## Retry Behavior

### Three Failure Types

1. **Command fails** (non-zero exit)
   - Retry same command
   - Max 3 attempts

2. **File not found** (verification)
   - Use `retry_step_on_file_not_found`
   - Usually same command (cheap regeneration)

3. **Review FAILED / Placeholders found**
   - Use `retry_step_on_fail`
   - Usually upstream step (expensive rebuild)

### Retry Context
On retry, agent receives:
```
VALIDATION ERROR: {reason}
```

Plus the review file attached via `-f` flag if applicable.

---

## File Structure

```
FullAutoTemplate/
├── .setup/
│   ├── setup.py              # Creates new projects
│   ├── run_steps.py          # Workflow executor
│   └── steps.yaml            # Master workflow config
│
├── .specify/
│   ├── templates/            # All speckit templates
│   │   ├── spec-template.md
│   │   ├── spec-review-template.md
│   │   ├── plan-template.md
│   │   ├── plan-review-template.md
│   │   ├── tasks-template.md
│   │   ├── tasks-review-template.md
│   │   ├── test-review-template.md
│   │   └── product-review-template.md
│   └── memory/
│       └── constitution.md   # 11 principles
│
├── .opencode/
│   └── command/              # Speckit command definitions
│       ├── speckit.specify.md
│       ├── speckit.spec-review.md
│       ├── speckit.plan.md
│       ├── speckit.plan-review.md
│       ├── speckit.tasks.md
│       ├── speckit.analyze.md
│       ├── speckit.tasks-review.md
│       ├── speckit.implement.md
│       ├── speckit.test-review.md
│       ├── speckit.product-review.md
│       └── compact.md
│
├── project/                  # Skeleton scaffold (copied to new projects)
│   ├── src/
│   ├── tests/
│   ├── pyproject.toml
│   ├── README.md
│   └── requirements.txt
│
└── .specs/                   # Test specs
    └── PythonSnakeGame.md
```

---

## Current Implementation Details

### run_steps.py Key Classes

**WorkflowLogger:**
- Timestamped log files: `workflow_YYYYMMDD_HHMMSS.log`
- Tracks step execution, retries, failures

**Command:**
```python
class Command:
    command: str              # The speckit command
    model: str                # Model alias (reviewer-model, coder-model)
    files: List[str]          # Files to attach via -f
    verify: Dict              # File verification config
    verify_implementation: bool  # Scan src/ for placeholders
```

**OpenCodeExecutor:**
- Loads YAML, resolves model aliases
- Executes commands via `opencode run` subprocess
- Runs verification after successful commands
- Handles retry logic with per-step counters

### Verification Functions

**verify_files(files):**
- Checks file exists in `specs/{feature-dir}/`
- If `-review.md` file: parses STATUS: PASS/FAIL
- Returns (success, error_message)

**verify_implementation():**
- Scans `src/` and `tests/` directories
- Looks for placeholder patterns: `# TODO`, `# FIXME`, `# Implement`, etc.
- Returns (success, error_message)

---

## Known Limitations

1. **Model hallucination:** Qwen sometimes outputs "Recommended command:" instead of making changes
2. **Context limits:** Long specs can fill Qwen context window
3. **No checkpoint/resume:** Must restart from specific step if interrupted
4. **Single feature directory:** Finds first subdir in `specs/`, not configurable

---

## Recent Changes (2026-03-20)

### Compacted Verification System
**Before:** 23 steps (9 separate verification steps)  
**After:** 14 steps (verification integrated into commands)

**Benefits:**
- 39% fewer steps
- File-not-found retries are cheap (same command, not upstream)
- Cleaner YAML structure
- No magic `-*-verify-*-` command prefixes

### Timestamped Logs
- Log files now include timestamp: `workflow_20260320_181132.log`
- Prevents overwriting previous run logs

### Null Model Error
- `model: null` now raises `ValueError` (was unpredictable)
- All steps must specify valid model alias

---

## Next Steps / TODO

1. **Test with Qwen:** Run snake game test to validate compacted system
2. **Cost tracking:** Add token/cost logging per step
3. **Session persistence:** Support `--continue` for opencode session reuse
4. **Recommendation detection:** Auto-retry when Qwen suggests commands instead of executing

---

## Files Modified Today

- `.setup/steps.yaml` - Compacted to 14 steps with inline verification
- `.setup/run_steps.py` - Updated Command class, verification logic, retry handling
- `.setup/JOURNEY.md` - Added Phase 11 documentation
- `.setup/HANDOFF.md` - This file

---

## Contact / Context

**For AI assistants:** Read this file first when picking up this project. Check `._agents_not_allowed/workflow_*.log` for recent activity.

**Key constraint:** Files in `._agents_not_allowed/` are hands-off unless explicitly asked to modify.
