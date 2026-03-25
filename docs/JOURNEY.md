# Journey: Building FullAutoTemplate

*A chronological record of false paths, pivots, and working solutions.*

**Date:** 2026-03-21  
**Goal:** Automate speckit workflow execution with guardrails  
**Outcome:** Functional Python orchestrator with verification and retry logic

---

## Historical Summary (Phases 0-8)

See `.archive/JOURNEY.2026-03-20.md` for detailed accounts of:

- **Phase 0-1:** Spec kit refinement, HTTP API attempts (OpenCode bug #15150)
- **Phase 2-3:** CLI discovery, YAML-to-CLI bash generator
- **Phase 4:** Model routing strategy (Kimi for spec/review, Qwen for bulk)
- **Phase 5-6:** Recommendation problem, session recovery patterns
- **Phase 7:** FullAutoTemplate creation (skeleton scaffold + setup script)
- **Phase 8:** Template discovery failure (directory context matters)

**Key Lesson from History:** Pre-structure beats post-fix. Skeleton prevents whole categories of errors.

---

## Phase 9: YAML-First Simplification (2026-03-19)

**Insight:** Reviewing broken code revealed unnecessary complexity.
**Insight:** Qwen3.5 still promising with guard rails and reviews

**Decision:** Beef up YAML file with richer metadata, simplify runner logic.

**Changes Made:**
1. Updated `steps.yaml` with explicit fields per step (template paths, validation hooks)
2. Stubbed `run_steps.py` as minimal executor - just reads YAML and executes

**Goal:** One source of truth (YAML), dumb executor (Python), no logic in between.

---

## Phase 10: Review Validation & Retry System (2026-03-20)

**Problem:** Reviews could FAIL but workflow would continue. No automated retry mechanism.

**Solution Built:**

### 1. Standardized Review Templates
All review templates now include PASS/FAIL marker:
```markdown
## Review Result
STATUS: [PASS | FAIL]

If FAIL: [one sentence reason]
```

### 2. Enhanced Validation Steps
Added `-*-verify-*-` checkpoints after every review:
- Check review file exists
- Parse STATUS: PASS/FAIL marker
- Extract failure reason
- Trigger retry if FAIL

### 3. Retry Logic with Context
```yaml
max_retries_per_validation: 3

commands:
  - command: "-*-verify-*-"
    files:
      - "test-review.md"
    retry_step_on_fail: "/speckit.implement"
```

**Behavior:**
1. Verify step reads review file
2. If STATUS: FAIL → find retry_step_on_fail target
3. Re-run target step with error context and review file attached
4. Track retry count per validation step
5. Max retries exceeded → bail with full traceback

### 4. File Logger
`workflow.log` in `._agents_not_allowed/` tracks execution, retries, failures.

### 5. GPT-OSS-20B Test Results

**Test:** Snake game with GPT-OSS-20B (replacing Qwen for speed)

**Result:** System worked perfectly, model failed spectacularly

**What Worked:**
- ✅ 23-step workflow executed unattended
- ✅ Verify-implementation detected placeholder
- ✅ Retry triggered automatically
- ✅ Max retries exceeded, clean bail

**What Failed:**
- ❌ GPT-OSS-20B output placeholders instead of code
- ❌ Even with 3 retries + error context, kept outputting stubs
- ❌ Might work with a higher temperature, but command line opencode doesn't support that.

**Verdict:** GPT-OSS-20B unsuitable for implement step. Retry system validated.

---

## Phase 11: Compacted Verification System (2026-03-20)

**Problem:** 23 steps (9 were just verification). Wasteful rebuilds when review file missing.

**Solution:** Integrate verification into commands that need it.

### New YAML Structure
```yaml
commands:
  - command: "/speckit.spec-review"
    model: coder-model
    files: [...]
    verify:
      files:
        - "spec-review.md"
      retry_step_on_fail: "/speckit.spec-review"
      retry_step_on_file_not_found: "/speckit.spec-review"

  - command: "/speckit.implement"
    model: coder-model
    files: [...]
    verify_implementation: true
    retry_step_on_fail: "/speckit.implement"
```

### Key Changes

1. **Removed separate `-*-verify-*-` steps** - 14 steps instead of 23 (39% reduction)

2. **Two retry paths:**
   - `retry_step_on_file_not_found` - File doesn't exist (cheap: rerun same command)
   - `retry_step_on_fail` - Review FAILED or implementation has placeholders (expensive: go back and fix)

3. **Verification runs after command succeeds:**
   ```
   Execute command → Verify output → Handle failure → Continue
   ```

4. **Simpler runner logic:**
   - No magic command prefixes
   - `Command` class parses `verify` and `verify_implementation` attributes
   - Main loop handles all retry logic uniformly

### Timestamped Logs
Log files now include timestamp: `workflow_20260320_181132.log`

---

## Phase 12: Functional Refactor (2026-03-21)

**Goal:** Cleaner architecture using functional programming principles

### Changes Made

**Before:** Class-based `OpenCodeExecutor` with mutable state scattered throughout

**After:** Pure functions with immutable data structures, maybe overkill, but much nicer than the mess from before

```python
@dataclass(frozen=True)
class Command:
    name: str
    model_alias: Optional[str]
    files: tuple
    verify: Optional[dict]
    verify_implementation: bool
```

**Pure Functions:**
- `load_config()` - Returns immutable `Config`
- `verify_files()` - Returns `VerificationResult`
- `compute_retry_decision()` - Returns `RetryDecision`
- `find_feature_dir()` - Returns `Optional[Path]`

**I/O Isolation:**
- `write_log()`, `create_logger()` - File operations
- `execute_opencode()` - Subprocess execution
- All side effects in dedicated section

### Enhanced Verification Output

```
======= VERIFYING =======
Feature directory: specs/001-console-snake-game
Files to verify: ['spec.md']
  spec.md: FOUND
  spec-review.md: FOUND
    Review status: PASS
======= PASS =======
```

### Feature Directory Selection

- Finds highest numbered directory (e.g., `001-alpha`, `002-beta` → `002-beta`)
- Ignores non-numbered directories
- Re-checks after each command execution

---

## Current Status

**System:** Functional Python orchestrator (~650 lines)  
**Architecture:** Pure functions + immutable data + isolated I/O  
**Verification:** Detailed output with FOUND/NOT FOUND and PASS/FAIL  
**Retry Logic:** Per-target-step counters with context preservation  

**Ready for:** End-to-end testing with snake game

---

## Lessons Learned

1. **Bugs happen:** OpenCode is new (1.2.27), has 5000+ open issues
2. **Workarounds work:** File attachment bypasses broken `--command`
3. **Cost matters:** Routing cheap models to bulk work saves 10x
4. **Rescue is hard:** Restarting clean often beats debugging partial runs
5. **Meta is the point:** We built automation for building automation
6. **Functional > OOP in small scripts:** Immutable data prevents whole classes of bugs in small scripts.
7. **Visibility matters:** Clear verification output saves debugging time

---

## Tools That Work

- `opencode run -f cmd.md -f template.md --model X "prompt"` ✅
- `python3 run_steps.py` ✅ (functional refactor)
- `python3 setup.py --project-name foo --spec "..."` ✅
- Session recovery via `--continue` ✅
- Verification with detailed output ✅

## Tools That Don't Work

- `opencode run --command /speckit.specify` ❌ (bug #15150)
- HTTP API `/session/{id}/command` ❌ (same bug)
- GPT-OSS-20B for implement step ❌ (placeholders instead of code)

---

## What's Next

1. **End-to-end test:** Validate with snake game
2. **Cost tracking:** Token/cost per step logging
3. **Multi-feature support:** Queue multiple feature directories
4. **Parallel/Queue execution:** Run independent features concurrently or in a queue. Queue for local agents that might slow each other down with parallel runs.

---

## Phase 13: Tamper Detection + Template Cleanup (2026-03-22)

### Bug: Review File Tampering

**Problem:** Model modified plan-review.md (changed FAIL to PASS) during /speckit.tasks step.

**Evidence:**
```
Step 5/10 - /speckit.tasks
M specs/001-snake-game/plan-review.md
```

**Root Cause:** Review file modified by downstream step after verification passed.

### Fix Applied: Hash-based Tamper Detection

Added to `run_steps.py`:
- Track MD5 hash of each review file at verification time
- Before each step, compare current hash to stored hash
- Fail with integrity violation if file changed

```python
# Store hash after verification
state['verified_review_hashes'][step_num] = {filename: hash}

# Check before next step
if current_hash != stored_hash:
    print("[ERROR] Review file modified by downstream step!")
    sys.exit(1)
```

### Fix Applied: Template Cleanup

Removed confusing `**Status**: [PASS | FAIL]` placeholders from review templates. Only `STATUS: [PASS | FAIL]` at the end remains as actual output field.

### Other Fixes Applied

1. **--continue logic:** Fixed hardcoded flag. Now only omitted on first step.
2. **--debug flag:** Removed. Not valid in current OpenCode CLI. User confirmed via docs.

### Current Test Run (Snake Game)

Retry mechanism working - model received FAIL context and is regenerating plan:
```
[CONTEXT] Adding extra info: VALIDATION ERROR: plan-review.md: FAIL - Review marked as FAIL
Executing: /speckit.plan
```

**Status:** In progress, monitoring for tamper detection.

---

## Phase 14: Refactor & GitHub (2026-03-22)

### Project Renamed
- speckit-orchestrator -> prompt-orchestrator
- Better reflects purpose: orchestrating LLM workflows

### Field Rename
- `command: "/speckit.xxx"` -> `step: "xxx"`
- Cleaner, no misleading /speckit prefix
- References updated in all YAML files

### Directory Consolidation
- Moved `.opencode/command/` and `.specify/templates/` to `.orchestrator/`
- Single location for all prompt files
- Updated paths in steps.yaml

### Bug: Retry Counter Regression
- Bug introduced during Phase 13 functional refactor
- Counter tracked `target_step` instead of failing `step_num`
- Fixed with clear comment explaining the logic
- Verified with snake4 end-to-end test

### GitHub Launch
- Repository created and pushed
- https://github.com/dustinandrews/prompt-orchestrator

### Lessons
1. Functional refactors can introduce subtle regressions
2. End-to-end testing catches what unit tests miss
3. Framework validated, model limitations exposed

### Next
- steps-basic.yaml / steps-full.yaml split
- Break up implement step for Qwen compatibility

---

## Phase 15: Context Management Workaround (2026-03-22)

### Problem: Session Context Exhaustion

**Issue:** opencode commands (`/compact`) cannot be invoked from CLI due to opencode bug. Auto-compact triggers at 95% context, which is too late for smaller models like Qwen 3.5.

**Current workaround:**
1. Ctrl-C to interrupt run_steps.py
2. `opencode -s` (start interactive session)
3. `/compact` (manual compaction)
4. `/exit` (quit session)
5. `run_steps.py --step N` (resume at current step)

### Research Findings

- opencode is archived, moved to [Crush](https://github.com/charmbracelet/crush)
- Crush has no non-interactive mode (TUI-only)
- opencode schema doesn't include configurable compact threshold
- No CLI way to invoke `/compact` without interactive terminal

### Documentation Added

- README.md: Context Management Workaround section
- JOURNEY.md: This entry
- HANDOFF.md: Known Limitations section updated

### Next
- File bug report with opencode/Crush for configurable compact threshold
- Consider switching to different AI harness tool
- Break up implement step to reduce context requirements
