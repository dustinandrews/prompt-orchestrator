# FullAutoTemplate - Technical Handoff

**Project:** FullAutoTemplate - Reusable template for bootstrapping code generators  
**Location:** `/home/nanobot/.nanobot/workspace/projects/FullAutoTemplate/`  
**Last Updated:** 2026-03-21  
**Status:** ACTIVE - Functional refactor complete, verification output enhanced

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

### Model Aliases - subject to change, but these are the base case
```yaml
models:
  - reviewer-model:
      model: "moonshotai/kimi-k2.5"
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
│   ├── steps.yaml            # Master workflow config
│   ├── HANDOFF.md            # This file
│   ├── JOURNEY.md            # Development history
│   ├── TODO.md               # Open questions
│   ├── WHYANDWHAT.md         # Public rationale
│   ├── WORKSTYLE.md          # Working constraints
│   └── .archive/             # Archived versions
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

### run_steps.py Architecture

**Functional Style:**
- Pure functions for configuration loading, verification, retry logic
- Immutable data structures (`@dataclass(frozen=True)`)
- Side effects isolated to I/O section
- Explicit state management in main loop

**Key Data Structures:**
```python
@dataclass(frozen=True)
class Command:
    name: str
    model_alias: Optional[str]
    files: tuple
    verify: Optional[dict]
    verify_implementation: bool
    retry_step_on_fail: Optional[str]
```

**Verification Output Format:**
```
======= VERIFYING =======
Feature directory: /path/to/specs/001-feature
Files to verify: ['spec.md']
  spec.md: FOUND
  spec-review.md: FOUND
    Review status: PASS
======= PASS =======
```

### Verification Functions

**verify_files(feature_dir, files):**
- Checks file exists in `specs/{feature-dir}/`
- If `-review.md` file: parses STATUS: PASS/FAIL
- Returns `VerificationResult` with detailed output

**verify_implementation(base_dir):**
- Scans `src/` and `tests/` directories
- Looks for placeholder patterns: `{{ }}` (Jinja-style)
- Returns `VerificationResult` with file list if found

### Feature Directory Selection

**find_feature_dir(base_dir):**
- Finds highest numbered directory in `specs/`
- Ignores non-numbered directories
- Example: `001-alpha`, `002-beta` → returns `002-beta`

---

## Known Limitations

1. **Model hallucination:** Qwen sometimes outputs "Recommended command:" instead of making changes
2. **Context limits:** Long specs can fill Qwen context window
3. **No checkpoint/resume:** Must restart from specific step if interrupted - feature recorded for later.
4. **Single feature workflow:** One feature directory per workflow run
5. **No verbose/debug flag:** Current OpenCode CLI does not support --debug or --log-level flags.

---

## Recent Changes (2026-03-21)

### Functional Refactor
- Converted from class-based to functional architecture
- Immutable data structures throughout
- Pure functions for business logic
- Side effects isolated to explicit I/O section

### Enhanced Verification Output
- Clear section headers (`======= VERIFYING =======`)
- Per-file FOUND/NOT FOUND status
- Review PASS/FAIL status for review files
- Consistent PASS/FAIL summary

### Feature Directory Logic
- Now selects highest numbered directory (for multi-feature projects)
- Ignores non-numbered directories
- Re-checks after each command (for newly created specs)

---

## Recent Changes (2026-03-22)

### Removed Non-existent CLI Flags
- `--debug` and `--log-level` flags removed from `run_steps.py`. Not valid in current OpenCode CLI.

### Review File Tamper Detection
- Added MD5 hash tracking for review files
- Fails workflow if review file modified by downstream step

### GitHub Prep Status (2026-03-22)

**Completed:**
- README.md ✅
- .gitignore ✅
- pyproject.toml ✅
- LICENSE (MIT) ✅
- Log cleanup ✅
- Backup cleanup ✅
- Git history verified ✅
- CONTRIBUTING.md ✅
- --target-dir option for setup.py ✅

**Pending:**
- .github/ CI workflow ⏳

---

## Historical Context

See `.archive/HANDOFF.2026-03-20.md` for full development history including:
- HTTP API false starts (OpenCode bug #15150)
- YAML-to-CLI generator evolution
- Model routing strategy development
- Retry system architecture decisions

---

## Next Steps / TODO

1. **Test end-to-end:** Run snake game test to validate refactored system
2. **Cost tracking:** Add token/cost logging per step
3. **Session persistence:** Support `--continue` for opencode session reuse [complete]
4. **Recommendation detection:** Auto-retry when Qwen suggests commands instead of executing

---

## Contact / Context

**For AI assistants:** Read this file first when picking up this project. Check `._agents_not_allowed/workflow_*.log` for recent activity.

**Key constraint:** Files in `._agents_not_allowed/` are hands-off unless explicitly asked to modify. Meant to keep opencode runner agents from getting confused by the contents.
