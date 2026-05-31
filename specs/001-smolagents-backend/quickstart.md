# Quickstart: Smolagents Backend Implementation

## Files to Modify

### 1. `pyproject.toml` — Add dependency
```toml
dependencies = [
    "pyyaml>=6.0",
    "smolagents>=1.17.0",
]
```

### 2. `prompt_orchestrator/cli.py` — Add `--backend` flag
In `cmd_run()` parser, add:
```python
run_p.add_argument("--backend", default="opencode", choices=["opencode", "smolagents"],
                   help="Execution backend (default: opencode)")
```
Pass `args.backend` through to `runner.main()` or `run_workflow()`.

### 3. `prompt_orchestrator/runner.py` — New functions + dispatch

**New functions:**

```python
def build_smolagents_prompt(command, model, files, debug, base_message, extra, use_continue=True) -> str:
    """Assemble prompt from command files — returns string for CodeAgent.run()."""

def execute_smolagents(prompt: str) -> ExecutionResult:
    """Create CodeAgent with HfApiModel + file tools and execute prompt."""
```

**Modified dispatch in `run_workflow()`:**

Replace:
```python
opencode_cmd = build_opencode_cmd(...)
exec_result = execute_opencode(opencode_cmd)
```

With:
```python
if config.backend == "smolagents":
    prompt = build_smolagents_prompt(...)
    exec_result = execute_smolagents(prompt)
else:
    cmd = build_opencode_cmd(...)
    exec_result = execute_opencode(cmd)
```

## Implementation Order

1. **Add dependency** — `pip install smolagents`, bump `pyproject.toml`
2. **Add argparse flag** — `--backend` in CLI, thread to `Config`
3. **Write `build_smolagents_prompt()`** — reads same files as opencode, returns string
4. **Write `execute_smolagents()`** — `CodeAgent` + `InferenceClientModel` + file tools
5. **Wire dispatch** — conditional `if/else` in main loop

## Smoke Test

```bash
# Specify step only (cheapest validation)
prompt-orchestrator run --backend smolagents --step 1

# Full workflow
prompt-orchestrator run --backend smolagents
```

## Configuration

Set `HF_TOKEN` in `.env` for Hugging Face Inference Providers:
```env
HF_TOKEN=hf_...
```

## Rollback

Remove `--backend` flag and revert `pyproject.toml` to restore original behavior. All changes are additive — no existing functionality is modified.
