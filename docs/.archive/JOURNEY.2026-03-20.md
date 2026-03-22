# Journey: Building the OpenCode Seq Orchestrator

*A chronological record of false paths, pivots, and working solutions.*

**Date:** 2026-03-18  
**Goal:** Automate speckit workflow execution via OpenCode CLI  
**Outcome:** Working bash script generator with file-attachment workaround

---
## Phase 0: Fine tuning Spec Kit process
**Spec Kit problems**
- Out of the box, models tend to over-engineer with spec kit. 
- Without human intervention they end up with an unruly mess by the end.
- Even without human review, person still has to feed in the commands as each on finishes

**Fixing the process**
- After several human assisted runs, patterns emerged
- Between steps the AI needs to review the last step and aggressively trim the fat
- Built new /speckit steps to review each step.
```
/speckit.specify
/speckit.spec-review
/speckit.plan
/speckit.plan-review
/speckit.tasks
/speckit.analyze
/speckit.tasks-review
/speckit.implement
/speckit.test-review
/speckit.product-review
```
  - Test review ensures all tests are working
  - Product review ensures golden path functions

With a working process in hand all we had to do was automate opencode to just run them in order. Should be easy, right?

## Phase 1: The Dream (HTTP API Automation)

**Initial Approach:** Build a Python orchestrator that talks to OpenCode's HTTP API

Created `runner.py` that:
- Creates sessions via `POST /session`
- Sends commands via `POST /session/{id}/command`

**False Path #1: Direct HTTP API**
- Discovered OpenCode bug #15150: `/command` endpoint returns `undefined is not an object (evaluating 'command3.agent')`
- Bug affects versions 1.2.14-1.2.27 (confirmed unfixed)

**Pivot #1:** Route through `/message` endpoint instead
- Changed payload structure to use `parts: [{type: "text", text: "/speckit.specify ..."}]`
- Returns empty response (fire-and-forget, no LLM output)

**False Path #2: /tui/execute-command**
- Tried `/tui/execute-command` endpoint
- Returns boolean `true`, not the LLM response
- Also fire-and-forget

---

## Phase 2: The CLI Discovery

**Pivot #2:** Abandon HTTP API entirely, use `opencode run` CLI

Discovered working pattern:
```bash
opencode run -f .opencode/command/speckit.specify.md \
             -f .specify/templates/spec-template.md \
             --model moonshot/kimi-k2-thinking \
             "Markdown blog generator: ..."
```

**Key Insight:** The `-f` (file attachment) flag works around the `--command` bug by attaching speckit prompt files as context, then passing the actual prompt as natural language.

**Why this works:**
- OpenCode reads the attached `.md` files
- The command file contains the speckit instructions
- The template file contains the output format
- Natural language prompt provides the specific task

---

## Phase 3: YAML-to-CLI Generator

**Created:** `yaml-to-cli.py` - converts workflow YAML to bash script

**Features added:**
1. Template mapping (speckit command → template file)
2. Model routing per command
3. `--continue` flag for session persistence
4. Step numbering with echo statements
5. Log level support

**False Path #3: Missing Templates**
- Tried to attach `analyze-template.md` - doesn't exist
- Tried to attach `implement-template.md` - doesn't exist
- Tried to use `final-review-template.md` for test/product review - outdated

**Fix:** Only map templates that exist; run other commands with just the command file.

---

## Phase 4: Model Routing Strategy

**Decision:** Use different models for different phases

| Phase | Model | Reason |
|-------|-------|--------|
| specify | moonshot/kimi | High-quality specification writing |
| spec-review | ollama/qwen3.5:35b | Cheap bulk analysis |
| plan | ollama/qwen3.5:35b | Cheap bulk generation |
| plan-review | ollama/qwen3.5:35b | Cheap bulk analysis |
| tasks | ollama/qwen3.5:35b | Cheap bulk generation |
| analyze | ollama/qwen3.5:35b | Cheap bulk analysis |
| tasks-review | ollama/qwen3.5:35b | Cheap bulk analysis |
| implement | ollama/qwen3.5:35b | Cheap bulk coding |
| test-review | ollama/qwen3.5:35b | Cheap validation |
| product-review | moonshot/kimi | High-quality final review |

**Cost Control:** Moonshot only for high-value steps (specification and final review).

---

## Phase 5: The Recommendation Problem

**Issue:** Qwen sometimes outputs:
```
Recommended revision command:
./speckit.tasks --focus=mvp --max-tasks=15
```

Instead of making the changes directly.

**Impact:** Workflow stalls waiting for human intervention.

**Potential Solutions (Not Yet Implemented):**
1. Post-process output to detect recommendations, auto-retry with "MAKE THE CHANGES"
2. Use stricter prompt: "DO NOT suggest commands. DO NOT ask questions. MAKE CHANGES."
3. Build agent that watches output and decides next step

**Current Workaround:** Manual intervention when detected.

---

## Phase 6: Session Recovery

**Issue:** Test run failed at step 13/14 due to missing `--continue` flag in old script.

**Recovery Process:**
1. Load session: `opencode session list`
2. Fork session: `opencode run --fork --continue`
3. Re-run recommended command

**Lesson:** Checkpoint/resume is critical for long workflows (14 steps × 2-5 min = 30-70 min total).

**Spec Addition:** Orchestrator should export session data at start and support `--resume` flag.

---

## Current Working System

**Input:** `blog-test.yaml`
```yaml
format: json
quiet: true
log_level: INFO
message: "K.I.S.S. DO NOT ask clarifying questions. Make decisions and proceed."
commands:
  - command: "/speckit.specify Markdown blog generator: ..."
    model: "moonshot/kimi-k2-thinking"
  - command: "/speckit.spec-review"
    model: "ollama/qwen3.5:35b"
  # ... 12 more steps
```

**Generation:**
```bash
python3 yaml-to-cli.py blog-test.yaml > run.sh
```

**Output Excerpt:**
```bash
echo "Step 1/14 - speckit.specify.md"
opencode run --log-level INFO \
  -f .opencode/command/speckit.specify.md \
  -f .specify/templates/spec-template.md \
  --model moonshot/kimi-k2-thinking \
  "Markdown blog generator: ... K.I.S.S. DO NOT ask clarifying questions."
```

**Execution:**
```bash
bash run.sh
```

---

## Key Architectural Decisions

### 1. File Attachment Over Commands
- **Why:** `--command` flag broken in OpenCode
- **How:** Attach prompt files, pass task as natural language
- **Trade-off:** More verbose commands, but reliable

### 2. Bash Generation Over Direct Execution
- **Why:** User can review/edit before running
- **How:** Generate run.sh, user runs manually
- **Trade-off:** Less "magic", more transparent

### 3. Template Mapping
- **Why:** Not all speckit commands have templates
- **How:** Dictionary lookup, skip if missing
- **Trade-off:** Some commands run with less context

### 4. Model Per Command
- **Why:** Cost optimization
- **How:** YAML specifies model per step
- **Trade-off:** More complex config, but cheaper runs

---

## What's Next (Spec V2)

1. **Recommendation Detection:** Auto-retry when AI suggests commands
2. **Checkpoint/Resume:** Save progress after each step
3. **Session Export:** Backup at workflow start
4. **Cost Tracking:** Running token/cost estimate
5. **Progress Visibility:** Real-time step timing

---

## Lessons Learned

1. **Bugs happen:** OpenCode is new (1.2.27), has 5000+ open issues
2. **Workarounds work:** File attachment bypasses broken `--command`
3. **Cost matters:** Routing cheap models to bulk work saves 10x
4. **Rescue is hard:** Restarting clean often beats debugging partial runs
5. **Meta is the point:** We built automation for building automation

---

## Tools That Work

- `opencode run -f cmd.md -f template.md --model X "prompt"` ✅
- `python3 yaml-to-cli.py blog-test.yaml` ✅
- `bash run.sh` ✅
- Session recovery via fork/continue ✅

## Tools That Don't Work

- `opencode run --command /speckit.specify` ❌ (bug #15150)
- HTTP API `/session/{id}/command` ❌ (same bug)
- `/tui/execute-command` ❌ (fire-and-forget, no output)

---

## Phase 7: FullAutoTemplate (2026-03-19)

**Goal:** Create reusable template for new projects with skeleton structure

**Problem Solved:** Qwen was creating malformed project structures, installing to global Python, using /tmp

**Solution:** Pre-defined skeleton + setup script

### Created Structure

**FullAutoTemplate/**:
```
.specify/templates/     # All review templates
.opencode/command/      # Speckit commands
.specify/memory/constitution.md  # Updated principles
project/                # Skeleton scaffold
├── src/
│   ├── __init__.py
│   ├── main.py
│   └── cli.py
├── tests/
│   ├── test_main.py
│   └── test_cli.py
├── pyproject.toml
├── README.md
└── requirements.txt
.setup/                 # Orchestration
├── setup.py           # Creates projects
├── steps.yaml         # Generic workflow
└── yaml-to-cli.py     # Script generator
```

### Workflow Change

Old: Manual copy, manual spec, run bash script
New: `python3 setup.py --project-name foo --spec "..."`

Setup handles:
1. Copy template (minus .setup/ and project/)
2. Generate run.sh from steps.yaml with spec substituted
3. Copy skeleton to {project_name}/

### Constitution Updates

Added to Principle VI:
- "Activate local venv before any pip install. Global pip is forbidden."
- "Use project-relative paths only. Never write to /tmp."

### Template Updates

- **test-review-template.md** - Created (was empty)
- **product-review-template.md** - Created (was missing)
- **speckit.implement.md** - Added note: "Project skeleton exists, fill existing files"

### First Complete Cycle

BlogTest finished successfully:
- Qwen: Spec → Tasks → Implement (free, local)
- Kimi: Landed product review ($0.60)
- **Total cost: $0.60** vs $2.50 for Kimi-only
- **Savings: 4:1**

Qwen limit: Package-level debugging (context fills, loses thread)
Kimi value: Landing messy implementations

### Current Test

**opencode-runner**: Python program to replace bash script generation
- Reads YAML workflow
- Executes opencode commands via subprocess
- Captures output, handles --continue, logs progress
- Being built with Qwen via FullAutoTemplate workflow

### New Lesson

Pre-structure beats post-fix. Skeleton prevents whole categories of errors.


--
- Ran full suite with the mission to create an upgraded running script. 
- Script just replaces old bash script, but was created unattended mostly by qwen3.5

## Phase 8: Template Discovery Failure (2026-03-19)

**Problem:** opencode-runner experiment failed - code produced but non-functional, template ignored.

**Root Cause:** Template embedded in `project/` folder but opencode ran from root directory. Agents never "saw" the skeleton files and flailed.

**Evidence:**
- Project created `src/opencode_runner/` in wrong location
- No use of pre-existing scaffold files
- Agents created their own structure from scratch

**Lesson:** Directory context matters. If agents don't see files in their working directory, they assume they don't exist.

**Next Hypothesis:** Change working directory to `{projectname}/` before running opencode, OR flatten template structure.

---

## Phase 9: YAML-First Simplification (2026-03-19)

**Insight:** Reviewing the broken code revealed unnecessary complexity.
**Insight:** Qwen3.5 still looks promising with guard rails and reviews

**Decision:** Beef up YAML file with richer metadata, simplify runner logic.

**Changes Made:**
1. Updated `steps.yaml` with explicit fields per step (template paths, validation hooks, timeout values)
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

Templates updated:
- `spec-review-template.md` ✅
- `plan-review-template.md` ✅
- `tasks-review-template.md` ✅
- `test-review-template.md` (new) ✅
- `product-review-template.md` (new) ✅

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
3. Re-run target step with:
   - Error context: "VALIDATION ERROR: {reason}"
   - Review file attached via `-f` flag
4. Track retry count per validation step
5. Max retries exceeded → bail with full traceback

### 4. File Logger
`workflow.log` in `._agents_not_allowed/` tracks:
```
1. /speckit.specify
...
15. -*-*-verify-*-
RETRY: Step 15 failed, retrying from step 14
REASON: Placeholders found in src/snake.py
ATTEMPT: 1/3
14. /speckit.implement
...
```

### 5. GPT-OSS-20B Test Results

**Test:** Snake game with GPT-OSS-20B (replacing Qwen for speed)

**Result:** System worked perfectly, model failed spectacularly

**What Worked:**
- ✅ 23-step workflow executed unattended
- ✅ Verify-implementation detected placeholder: `#Impliment game here.`
- ✅ Retry triggered automatically
- ✅ Review file attached to retry context
- ✅ Max retries exceeded, clean bail

**What Failed:**
- ❌ GPT-OSS-20B output placeholders instead of code
- ❌ Even with 3 retries + error context, kept outputting stubs
- ❌ "Fast but lazy" - 30+ min saved vs Qwen, but useless output

**Verdict:** GPT-OSS-20B unsuitable for implement step. Retry system validated.

### Architecture Validated

The retry loop design works:
1. Validation detects failure
2. Retry with context
3. Either fixes or exhausts retries
4. Clear logging of entire flow

**23 steps now** (was 18):
- Each review followed by verify
- Each verify can retry upstream step
- No manual intervention needed

---

## Phase 11: Compacted Verification System (2026-03-20)

**Problem:** 23 steps (9 were just verification). Wasteful rebuilds when review file missing (would retry upstream step instead of just regenerating the file).

**Solution:** Integrate verification into commands that need it

### New YAML Structure
```yaml
commands:
  - command: "/speckit.spec-review"
    model: coder-model
    files: [...]
    verify:
      files:
        - "spec-review.md"
      retry_step_on_fail: "/speckit.spec-review"        # Review FAILED
      retry_step_on_file_not_found: "/speckit.spec-review"  # File missing

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

### Efficiency Gains

**Before:**
- File missing → Verify step fails → Retry upstream step (wasteful rebuild)
- 23 steps, complex step ordering

**After:**
- File missing → Retry same command (cheap regeneration)
- Review FAILED → Retry upstream step (correct behavior)
- 14 steps, each self-contained

### Runner Changes

**Command class:**
```python
class Command:
    def __init__(self, data: dict):
        self.command = data.get("command")
        self.model = data.get("model")
        self.files = data.get("files", [])
        self.verify = data.get("verify")                    # New
        self.verify_implementation = data.get("verify_implementation", False)  # New
```

**Main loop pattern:**
```python
# Execute command
exit_code = self.execute_command(cmd.command, ...)

# Run verification if configured
if exit_code == 0 and cmd.verify_implementation:
    success, error = self.verify_implementation()
    
if exit_code == 0 and cmd.verify:
    success, error = self.verify_files(cmd.verify["files"])

# Handle failures with appropriate retry target
if file_not_found:
    retry_step = cmd.verify.get("retry_step_on_file_not_found", i)
elif review_failed:
    retry_step = cmd.verify.get("retry_step_on_fail")
```

### Timestamped Logs

Log files now include timestamp:
- `workflow_20260320_181132.log` instead of `workflow.log`
- Prevents overwriting previous runs

---
