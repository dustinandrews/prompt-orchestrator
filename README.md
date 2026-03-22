# speckit-orchestrator

Automated speckit workflow executor with review gates.

## What

Runs the [speckit](https://github.com/dustinandrews/speckit) code generation workflow unattended, powered by [opencode](https://github.com/opencode-ai/opencode) as the AI harness:
- Specify → Review → Plan → Review → Tasks → Review → Implement → Test Review → Product Review

Each step verified before proceeding. Review files protected by hash-based tamper detection to prevent later steps from re-doing reviews.

## Prerequisites

- [opencode](https://github.com/opencode-ai/opencode) - AI coding agent
- optional: [speckit](https://github.com/dustinandrews/speckit) - Coding template library
- Some kind of API key or Ollama. This will work with Qwen3.5 on Ollama.
- Best results with more powerful coding models like deepseek-v3.2
- Python 3.12+

## Quick Start

```bash
# Clone this repo
git clone https://github.com/dustinandrews/speckit-orchestrator.git
cd speckit-orchestrator

# Install dependencies
pip install pyyaml

# Configure AI provider (see [opencode docs](https://opencode.ai/docs/))

# Create new project
python3 .setup/setup.py --project-name myproject --spec "Build a CLI tool that..."

# Run workflow
cd myproject
python3 ._agents_not_allowed/run_steps.py
```

## Features

- **Automated workflow** - 14-step speckit process runs unattended
- **Review gates** - Each step verified before proceeding
- **Expanded commands** - 14 speckit commands with review steps built in (vs original 9)
- **Streamlined templates** - Simplified review templates, single STATUS field at end
- **Tamper detection** - Review files protected from modification
- **Retry logic** - Automatic retry on failure with context preservation
- **Model routing** - Use cheaper models for bulk work, premium for reviews

## Configuration

Edit `.setup/steps.yaml` to configure models and retry behavior. Configure your AI provider in opencode (see [opencode providers docs](https://opencode.ai/docs/providers)).

## Advanced Usage

**Resume after interruption:**
```bash
python3 ._agents_not_allowed/run_steps.py --step 5
```
Resume from step 5. Useful after Ctrl-C or network failure.

**Interact with project in opencode:**
```bash
opencode --continue
```
Continue the session to manually work on the project.

## Included Constitution

This repo includes an opinionated constitution (`.specify/memory/constitution.md`) focused on building Python CLI programs:
- **Library-first** - Extract reusable logic to libraries, keep scripts thin
- **Simplicity** - Prefer simple solutions, avoid premature abstraction
- **Test-first** - Tests validate behavior, not implementation
- **One thing at a time** - Small functions, single responsibility

The workflow enforces these principles via review gates. Plans flagged for over-engineering. Tasks flagged for wrong distribution.

See `.specify/memory/constitution.md` for full rules.

Caveat Emptor if you modify it. 

## Architecture

```
.setup/
├── run_steps.py     # Workflow executor
├── steps.yaml       # Step definitions
├── setup.py         # Project bootstrapper
└── ...

.specify/
├── templates/       # Review templates
└── memory/          # Constitution and rules

.opencode/
└── command/         # speckit command definitions

docs/                # Development history and documentation

._agents_not_allowed/   # Runtime files (logs, per-project steps.yaml)
    # Hidden to prevent AI agents from reading YAML and self-executing
    # Template copies here during project setup
```
├── JOURNEY.md       # Project history
├── HANDOFF.md       # Technical handoff
└── ...
```

## License

MIT
