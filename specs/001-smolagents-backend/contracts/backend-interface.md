# Backend Interface Contract

## Contract: Backend Execution

The backend system defines a contract between the workflow runner and execution engines.

### Contract ID
`backend-execution-v1`

### Provider
`prompt_orchestrator.runner` (the `run_workflow()` function)

### Consumer
Any execution backend (opencode, smolagents, future backends)

---

## Input Contract

### Build Phase

**Signature:**
```
build_<backend>_cmd(command: str, model: Optional[str], files: tuple,
                    debug: bool, base_message: str, extra: tuple,
                    use_continue: bool) -> list | str
```

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `command` | `str` | yes | Step name (e.g., "specify") |
| `model` | `Optional[str]` | no | Model identifier (e.g., "ollama/qwen3.5:35b") |
| `files` | `tuple` | yes | File paths to command .md files and templates |
| `debug` | `bool` | yes | Whether debug mode is enabled |
| `base_message` | `str` | yes | Base instruction message from config |
| `extra` | `tuple` | yes | Additional context strings (e.g., error context on retry) |
| `use_continue` | `bool` | yes | Whether this is a continuation (not first step) |

**Returns:**
- opencode backend: `list[str]` — subprocess command array
- smolagents backend: `str` — assembled prompt string

---

### Execute Phase

**Signature:**
```
execute_<backend>(input: list | str) -> ExecutionResult
```

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `input` | `list[str] | str` | yes | Command list (opencode) or prompt string (smolagents) |

**Returns:**
```python
@dataclass(frozen=True)
class ExecutionResult:
    exit_code: int       # 0 = success, 1 = failure
    error_msg: Optional[str]  # Error message if failed
```

---

## Output Contract

### Success
- `ExecutionResult(exit_code=0)` — step executed, output files may exist on disk

### Failure
- `ExecutionResult(exit_code=1, error_msg="...")` — step failed, verification should check for partial output

---

## Guarantees

1. **Same files read**: smolagents backend reads the exact same `cmd.files` tuple as opencode backend
2. **Same verification**: Both backends' output is verified by the same `verify_files()` function
3. **Same retry/decision**: Both backends use `compute_retry_decision()` with same max_retries
4. **Same hashing**: Review file hash tracking is backend-agnostic

---

## Versioning

Current contract version: `1.0`  
Change process: Any new backend must implement both `build_` and `execute_` functions matching this contract.
