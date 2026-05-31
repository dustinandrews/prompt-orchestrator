# prompt-orchestrator

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

Multi-step LLM workflow executor with review gates.

## What

Runs a multi-step code generation workflow unattended, powered by [opencode](https://github.com/opencode-ai/opencode) as the AI harness:
- Specify → Review → Plan → Review → Tasks → Review → Implement → Test Review → Product Review

Each step verified before proceeding. Review files protected by hash-based tamper detection to prevent later steps from re-doing reviews.

## Quick Start

```bash
# Install
pip install -e .

# Scaffold into existing project
cd my-existing-project
prompt-orchestrator init

# Run workflow
prompt-orchestrator run
```

Or create a new project from scratch:
```bash
prompt-orchestrator new --name myproject --spec spec.md
cd myproject
prompt-orchestrator run
```

## Prerequisites

- [opencode](https://github.com/opencode-ai/opencode) - AI coding agent
- Some kind of API key or Ollama. Works with Qwen3.5 on Ollama for local inference.
- Best results with more powerful coding models like deepseek-v3.2
- Python 3.10+

## CLI Usage

```bash
prompt-orchestrator init          # Scaffold workflow files into current project
prompt-orchestrator run           # Execute workflow (from project root)
prompt-orchestrator run --step 5  # Resume from step 5
prompt-orchestrator new --name NAME --spec PATH  # Create new project from skeleton
prompt-orchestrator --help        # Full help
```

## Features

- **Automated workflow** - Multi-step process runs unattended
- **Review gates** - Each step verified before proceeding
- **Expanded commands** - 14 commands with review steps built in
- **Streamlined templates** - Simplified review templates, single STATUS field at end
- **Tamper detection** - Review files protected from modification
- **Retry logic** - Automatic retry on failure with context preservation
- **Model routing** - Use cheaper models for bulk work, premium for reviews

## Configuration

Edit `steps.yaml` in your project root to configure models and retry behavior. Configure your AI provider in opencode (see [opencode providers docs](https://opencode.ai/docs/providers)).

### Model Aliases

```yaml
models:
  - reviewer-model:
      model: moonshotai/kimi-k2.5
  - coder-model:
      model: ollama/qwen3.5:35b
```

## Advanced Usage

**Resume after interruption:**
```bash
prompt-orchestrator run --step 5
```
Resume from step 5. Useful after Ctrl-C or network failure.

**Interact with project in opencode:**
```bash
opencode --continue
```
Continue the session to manually work on the project.

## Included Constitution

The scaffold includes an opinionated constitution (`.orchestrator/memory/constitution.md`) focused on building Python CLI programs:
- **Library-first** - Extract reusable logic to libraries, keep scripts thin
- **Simplicity** - Prefer simple solutions, avoid premature abstraction
- **Test-first** - Tests validate behavior, not implementation
- **One thing at a time** - Small functions, single responsibility

The workflow enforces these principles via review gates. Plans flagged for over-engineering. Tasks flagged for wrong distribution.

## Context Management Workaround

opencode has a known issue where the `/compact` command requires an interactive terminal. If the session grows too large for the model context:

1. **Ctrl-C** to interrupt
2. Run `opencode -s` to start interactive session
3. Type `/compact` and press Enter
4. Type `/exit` to quit
5. Resume with `prompt-orchestrator run --step N` (replace N with your current step)

## Architecture

```
prompt_orchestrator/        # Installable package
├── cli.py                  # CLI entry point (init, run, new)
├── runner.py               # Workflow executor
└── scaffold/               # Files deployed to projects
    ├── command/            # Orchestrator command definitions
    ├── templates/          # Review templates
    └── memory/             # Constitution and rules

project/                    # After init
├── .orchestrator/          # Command files and templates
├── ._agents_not_allowed/   # Runner and config (hidden from agents)
├── steps.yaml              # Workflow definition
└── userspec.md             # Your specification
```

## Spec Guide

Small programs with a tight scope work best. Think Unix utils like grep or curl that do one thing well. Focus on the smallest feature set to start with.

```markdown
Write a CLI program that allows users to view web URL contents

$ get-url --help
usage:
get-url --help                                  print this message an quit
get-url <url>                                   retrieves the URL and writes the contents to SDTOUT
get-url <url> --out-file <path_to_write>        write URL contents to file as UTF-8
```

## Roadmap
- Replace OpenCode with smolagents.

## License

MIT
