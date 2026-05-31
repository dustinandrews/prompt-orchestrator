# Data Model: Smolagents Backend

## Entities

### BackendConfig
Configuration for selecting and routing to an execution backend.

| Field | Type | Description |
|-------|------|-------------|
| `backend` | `str` | Backend name: `"opencode"` or `"smolagents"`. Default: `"opencode"` |

**Validation rules:**
- MUST be one of: `"opencode"`, `"smolagents"`
- Case-sensitive matching
- Invalid values produce error listing valid options

**Relationships:**
- Passed from CLI `--backend` argument → `Config` → `run_workflow()` dispatch

---

### SmolagentsPrompt
The assembled prompt string used as input to `CodeAgent.run()`.

| Field | Type | Description |
|-------|------|-------------|
| `prompt` | `str` | Concatenated content from command .md files + templates + message + extra context |

**Relationships:**
- Built from same `cmd.files` tuple as the opencode backend
- Prefixed with `base_message` and `extra` context (same as opencode)

---

### FileTool
Custom smolagents `Tool` subclass for filesystem operations.

**Three concrete types:**
- `ReadFileTool` — reads file content by path
- `WriteFileTool` — writes content to file path (creates parent dirs)
- `SearchFilesTool` — glob-based file search

**No state required** — all operations are stateless/pure.

---

### BackendExecutionResult
Wraps CodeAgent output into the existing `ExecutionResult` dataclass.

| Field | Type | Description |
|-------|------|-------------|
| `exit_code` | `int` | 0 on success, 1 on error |
| `error_msg` | `Optional[str]` | Error message if exit_code != 0 |

**State transitions:**
1. Agent runs successfully → `ExecutionResult(exit_code=0)`
2. Agent raises exception → `ExecutionResult(exit_code=1, error_msg=str(e))`

---

## Key Relationships

```
CLI --backend flag
    │
    ▼
Config.backend ───→ run_workflow()
                        │
                        ├── "opencode": build_opencode_cmd() → execute_opencode()
                        │
                        └── "smolagents": build_smolagents_prompt() → execute_smolagents()
                                                                        │
                                                                        ├── ReadFileTool
                                                                        ├── WriteFileTool
                                                                        └── SearchFilesTool
                                                                                │
                                                                                ▼
                                                                        ExecutionResult
                                                                                │
                                                                                ▼
                                                                        verify_files()
                                                                        compute_retry_decision()
                                                                        (same as opencode path)
```
