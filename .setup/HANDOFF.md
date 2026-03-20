# Handoff Document: OpenCode Seq Orchestrator

**Date:** 2026-03-18 16:24 PDT  
**Status:** Working bash script generator complete, v2 orchestrator spec'd but not built

---

## Quick Start (What Works Right Now)

### Generate and Run a Workflow
```bash
cd /home/nanobot/.nanobot/workspace/projects/opencode-seq
python3 yaml-to-cli.py blog-test.yaml > run.sh
bash run.sh
```

### File Locations
| File | Purpose |
|------|---------|
| `/home/nanobot/.nanobot/workspace/projects/opencode-seq/yaml-to-cli.py` | Working script generator |
| `/home/nanobot/.nanobot/workspace/projects/opencode-seq/blog-test.yaml` | Example 14-step workflow |
| `/home/nanobot/.nanobot/workspace/projects/opencode-seq/SPEC.md` | v2 orchestrator specification |
| `/home/nanobot/.nanobot/workspace/projects/opencode-seq/JOURNEY.md` | History of false paths and pivots |

---

## Critical Technical Details

### OpenCode Version & Bugs
- **Version:** 1.2.27 (installed at `/home/nanobot/.opencode/bin/opencode`)
- **Bug #15150:** `/command` endpoint and `--command` flag broken (returns "undefined is not an object")
- **Workaround:** Use `-f file.md` attachment + natural language prompt instead

### Working OpenCode Pattern
```bash
# BROKEN:
opencode run --command /speckit.specify "prompt"

# WORKING:
opencode run --log-level INFO \
  -f .opencode/command/speckit.specify.md \
  -f .specify/templates/spec-template.md \
  --model moonshot/kimi-k2-thinking \
  "Markdown blog generator: ... K.I.S.S. DO NOT ask clarifying questions."
```

### Session Management
- **Continue session:** `--continue` flag (use on steps 2-N)
- **Export session:** `opencode export [sessionID]` (for backup)
- **Fork session:** `opencode run --fork --continue` (for recovery)

---

## Model Strategy (Proven)

| Model | Use For | Cost |
|-------|---------|------|
| `moonshot/kimi-k2-thinking` | specify, product-review | Higher |
| `ollama/qwen3.5:35b` | Everything else | Local/free |
| `groq/llama-3.3-70b` | Fast bulk work | TBD (fast) |

**Constraint:** Moonshot has token quotas. Use sparingly.

---

## Speckit Template Mapping

Templates that exist:
- `.specify/templates/spec-template.md`
- `.specify/templates/spec-review-template.md`
- `.specify/templates/plan-template.md`
- `.specify/templates/plan-review-template.md`
- `.specify/templates/tasks-template.md`
- `.specify/templates/tasks-review-template.md`

Templates that DON'T exist (run without template file):
- `analyze-template.md`
- `implement-template.md`
- `test-review-template.md` (uses final-review-template - outdated)
- `product-review-template.md` (uses final-review-template - outdated)

**Note:** final-review-template.md exists but is outdated (test/product review were extracted from it).

---

## Current YAML Format

```yaml
format: json
quiet: true
log_level: INFO  # DEBUG, INFO, WARN, ERROR
message: "K.I.S.S. DO NOT ask clarifying questions. Make decisions and proceed."
commands:
  - command: "/speckit.specify Markdown blog generator: ..."
    model: "moonshot/kimi-k2-thinking"
  - command: "/speckit.spec-review"
    model: "ollama/qwen3.5:35b"
  - command: "/compact"
    model: null
  # etc...
```

---

## Known Issues

### 1. AI Recommendations Instead of Action
**Symptom:** Qwen outputs:
```
Recommended revision command:
./speckit.tasks --focus=mvp --max-tasks=15
```

**Impact:** Workflow stalls waiting for human intervention.

**Status:** Not fixed. Options:
- Post-process output, detect "Recommended", auto-retry
- Stricter prompt: "DO NOT suggest commands. MAKE CHANGES."
- Build agent that watches output and decides next step

### 2. No Checkpoint/Resume
**Symptom:** If step 12 fails, must restart from step 1.

**Workaround:** Manual session recovery:
```bash
opencode session list
opencode run --fork --continue --session <id>
```

**Spec Solution:** See SPEC.md US3 - checkpoint.json after each step.

### 3. Cost Tracking Missing
**Symptom:** No visibility into running cost.

**Spec Solution:** See SPEC.md US4 - track per-step model usage.

---

## Infrastructure Available

### Local Machine (evo-x2)
- **CPU:** NucBox EVO X2
- **Ollama:** Running with qwen3.5:35b, lfm2.5-thinking:latest
- **OpenCode:** v1.2.27, config at `~/.opencode/`
- **Projects:** `/home/nanobot/.nanobot/workspace/projects/`

### External Services
- **Moonshot API:** Working but quota-limited (~300k tokens)
- **Groq:** Available, fast (800 tokens/sec), not yet tested
- **SearXNG:** Running on port 8888 (for web search)

### Python Environment
- **Location:** nanobot venv
- **Key packages:** yaml, requests, youtube-transcript-api
- **Path:** `/home/nanobot/nanobot/`

---

## What's Built vs Spec'd

### Built (Working)
- ✅ yaml-to-cli.py - bash script generator
- ✅ File attachment workaround for --command bug
- ✅ Template mapping for existing templates
- ✅ Model routing per command
- ✅ --continue flag for session persistence
- ✅ log_level support

### Spec'd (Not Built)
- ⏳ Recommendation detection & auto-retry
- ⏳ Checkpoint/resume (checkpoint.json)
- ⏳ Session export at workflow start
- ⏳ Cost tracking per step
- ⏳ Real-time progress with timing
- ⏳ Agent-based step decider

---

## Test Project

**Location:** `/home/nanobot/.nanobot/workspace/projects/BlogTest/`

**Status:** In-progress speckit run (may be abandoned/rescued)

**What was being built:** Markdown blog generator
- Single command: `mdblog build ./posts ./output`
- Dark theme via CSS
- Static HTML output

---

## Key Assumptions

1. **OpenCode bug #15150 won't be fixed soon** - Workaround is permanent
2. **Speckit templates won't change** - Hardcoded paths in yaml-to-cli.py
3. **Ollama/qwen3.5:35b is "good enough"** for bulk work
4. **Moonshot is for high-value steps only** - cost control critical
5. **File-based approach is viable** - no need for Redis/DB

---

## Next Steps (Pick One)

1. **Fix yaml-to-cli.py** - Add recommendation detection + auto-retry
2. **Build orchestrator.py** - Full spec from SPEC.md
3. **Test Groq models** - Replace qwen with groq for speed
4. **Test lfm2.5-thinking** - See if it's viable for implement step
5. **Run BlogTest to completion** - Validate end-to-end workflow

---

## Emergency Contacts (Metaphorical)

- **OpenCode bugs:** GitHub issues #15150, #9733
- **Speckit templates:** Check `.specify/templates/` directory
- **Model quotas:** Moonshot dashboard (if suspended, use Ollama only)

---

## Update: FullAutoTemplate (2026-03-19)

**Location:** `/home/nanobot/.nanobot/workspace/projects/FullAutoTemplate/`

**New Workflow:**
```bash
cd FullAutoTemplate/.setup
python3 setup.py --project-name myapp --spec "Build a tool that..."
cd ../myapp
bash .run/run.sh
```

**Key Files:**
- `.setup/setup.py` - Project generator
- `.setup/steps.yaml` - Generic workflow template
- `project/` - Skeleton scaffold (src/, tests/, pyproject.toml)
- `.specify/memory/constitution.md` - Updated with venv/path rules

**Template Updates:**
- `test-review-template.md` - Now populated
- `product-review-template.md` - Created
- `speckit.implement.md` - References skeleton structure

**Cost Validation:**
- Qwen (Ollama/local): $0
- Kimi (landing): $0.60
- Full cycle: **$0.60** vs **$2.50** Kimi-only

**Active Test Project:**
- **opencode-runner** at `/home/nanobot/.nanobot/workspace/projects/opencode-runner/`
- Python-based workflow executor (replacing bash script generation)
- Being built with Qwen via new template workflow

**Status:** Template system functional. Next: Test opencode-runner completion.

--

## Update: FullAutoTemplate
### Completed test
- **opencode-runner** at `/home/nanobot/.nanobot/workspace/projects/opencode-runner/`
- Ran 100% un-attended and ended up with a python file that looks correct but is untested
- Agents didn't follow the directory pattern
- May need to adjust the templates -OR- make the working dir the {projectname} dir

### Root Cause Identified (2026-03-19)
**Template Discovery Failure:** Skeleton in `project/` folder was invisible to agents - opencode ran from root, agents never saw scaffold files. Created their own structure instead.

**Solution Direction:**
- Option A: Change working directory to `{projectname}/` before opencode execution
- Option B: Flatten template structure (move skeleton to root)
- Option C: Explicitly pass skeleton files via `-f` attachments

### YAML-First Refactor (2026-03-19)
**Simplification:** Beefed up `steps.yaml` with richer metadata, stubbed minimal `run_steps.py` executor.

**Principle:** One source of truth (YAML), dumb executor, no middle logic.

### Next steps

1. **Complete run_steps.py program**
   - Implement YAML reader
   - Execute opencode commands via subprocess
   - ensure --continue flag across steps
   - implement the validation logic
   - Add checkpoint/resume capability (later)

2. **Re-examine setup.py program**
   - It's messy - needs cleanup
   - Mods to remove extra directory may not work properly
   - Rip out bash script generation (deprecated by run_steps.py)
   - Focus: clean project scaffolding only

3. **Validate working directory fix**
   - Test Option A (cd to project dir before opencode)
   - Verify agents see skeleton files in context


