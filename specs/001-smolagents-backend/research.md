# Research: Smolagents Backend Integration

## Overview

Research findings for integrating `smolagents` (Hugging Face agent framework) as an alternative execution backend for `prompt-orchestrator run`.

---

## 1. CodeAgent + Model API

### Decision
Use `smolagents.CodeAgent` with `InferenceClientModel` (previously called `HfApiModel`).

### Rationale
- `CodeAgent` generates tool calls as Python code, enabling reasoning, chaining, and dynamic composition — ideal for spec-kit workflows that require reading files, writing output, and making decisions
- `InferenceClientModel` connects to Hugging Face Inference Providers (Cerebras, Together, HF-Inference, etc.) with no additional API setup beyond `HF_TOKEN`
- The code-agent paradigm matches the opencode model of treating each step as a code-generation task

### API Surface
```python
from smolagents import CodeAgent, InferenceClientModel

model = InferenceClientModel(model_id="Qwen/Qwen3-Next-80B-A3B-Thinking")
agent = CodeAgent(tools=[...], model=model)
result = agent.run(prompt_string)
```

**Key parameters:**
- `tools`: list of `Tool` objects (file read/write/search tools)
- `model`: `Model` instance (`InferenceClientModel`, `LiteLLMModel`, etc.)
- `additional_authorized_imports`: list of module names to allow in generated code
- `max_print_outputs_length`: cap on output size

### Alternatives Considered
| Alternative | Reason Rejected |
|-------------|----------------|
| `ToolCallingAgent` | Uses JSON tool calls — less expressive for code-generation workflows |
| `LiteLLMModel` | Requires separate API keys (OpenAI, Anthropic); adds dependency surface |
| Custom subprocess agent | Would rebuild existing framework — violates Principle X |

---

## 2. File Tools (Read/Write/Search)

### Decision
Create custom `Tool` subclasses for three operations: `ReadFileTool`, `WriteFileTool`, and `SearchFilesTool`.

### Rationale
- smolagents' default toolbox includes Python interpreter, web search, and audio transcription — none of which handle filesystem operations
- Custom tools follow the standard `Tool` pattern: extend the base class, define `name`, `description`, `inputs`, `output_type`, and `forward`

### Tool Definitions

**ReadFileTool**: Reads a file from disk and returns its content as a string.
```python
class ReadFileTool(Tool):
    name = "read_file"
    description = "Read a file from the filesystem and return its contents"
    inputs = {"path": {"type": "string", "description": "Path to the file to read"}}
    output_type = "string"

    def forward(self, path: str) -> str:
        import pathlib
        return pathlib.Path(path).read_text()
```

**WriteFileTool**: Writes content to a file on disk.
```python
class WriteFileTool(Tool):
    name = "write_file"
    description = "Write content to a file on the filesystem"
    inputs = {
        "path": {"type": "string", "description": "Path to write to"},
        "content": {"type": "string", "description": "Content to write"}
    }
    output_type = "string"

    def forward(self, path: str, content: str) -> str:
        import pathlib
        pathlib.Path(path).parent.mkdir(parents=True, exist_ok=True)
        pathlib.Path(path).write_text(content)
        return f"Written to {path}"
```

**SearchFilesTool**: Searches for files matching a glob pattern.
```python
class SearchFilesTool(Tool):
    name = "search_files"
    description = "Search for files matching a glob pattern"
    inputs = {"pattern": {"type": "string", "description": "Glob pattern to match"}}
    output_type = "string"

    def forward(self, pattern: str) -> str:
        import pathlib
        results = list(pathlib.Path().glob(pattern))
        return "\n".join(str(r) for r in results)
```

---

## 3. Prompt Assembly Strategy

### Decision
Reuse the same file-reading pattern as `build_opencode_cmd()` but return a single concatenated prompt string instead of a command list.

### Rationale
- smolagents `CodeAgent.run()` takes a string prompt, not a subprocess command
- The same `.md` command files and templates are read and concatenated
- This ensures prompt equivalence between backends — the AI sees the same instructions

### Flow
1. Read each file from `cmd.files` tuple
2. Concatenate with delimiters (like opencode's `-f` concatenation)
3. Prepend base message and extra context
4. Pass the assembled prompt to `agent.run()`

---

## 4. Hugging Face Authentication

### Decision
Use `HF_TOKEN` environment variable (standard Hugging Face convention).

### Rationale
- `InferenceClientModel` automatically reads `HF_TOKEN` from environment
- No additional config UI or prompts needed
- Free HF accounts have included credits for Inference Providers
- Follows the project's `.env` pattern for secrets

---

## 5. ExecutionResult Compatibility

### Decision
Wrap `agent.run()` output in `ExecutionResult(exit_code=0)` on success, `ExecutionResult(exit_code=1, error_msg=str(e))` on exception.

### Rationale
- Existing verification, retry, and hashing logic operates on `ExecutionResult` objects
- The smolagens backend must return the same type for drop-in compatibility
- The agent's stdout output is captured but not parsed — verification uses the same file-check logic as the opencode backend

---

## 6. Project Dependencies

### Decision
Add `smolagents>=1.17.0` to `pyproject.toml` dependencies.

### Rationale
- Version 1.17.0 introduced `InferenceClientModel` as the primary HF model class
- Older versions used `HfApiModel` (still available but deprecated)
- smolagents has MIT license — compatible with project license

---

## 7. Integration Pattern

### Decision
Add a conditional branch in the main execution loop:

```python
if config.backend == "smolagents":
    prompt = build_smolagents_prompt(...)
    result = execute_smolagents(prompt)
else:
    cmd = build_opencode_cmd(...)
    result = execute_opencode(cmd)
```

### Rationale
- Minimal diff — single `if/else` replacing the existing `build_opencode_cmd`/`execute_opencode` block
- Verification, retry, hashing, and logging remain unchanged
- No refactoring of existing code paths
- K.I.S.S. compliance
