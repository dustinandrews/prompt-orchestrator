# Contributing

## Before You Start

- Open an issue first for significant changes
- For small fixes, feel free to submit a PR directly

## Development Setup

```bash
git clone https://github.com/dustinandrews/prompt-orchestrator.git
cd prompt-orchestrator
pip install -e .
```

## Testing

Run the workflow with a test spec:
```bash
prompt-orchestrator new --name test-project --spec spec.md
cd test-project && prompt-orchestrator run
```

Or with the legacy path:
```bash
python3 .setup/setup.py --project-name test-project --spec "Build a simple CLI tool"
cd test-project && python3 ._agents_not_allowed/run_steps.py
```

## Code Style

- Python: follow PEP 8
- YAML: 2-space indent
- Templates: keep minimal, document deviations in comments

## Pull Request Process

1. Fork and create a feature branch
2. Test with `prompt-orchestrator run` before submitting
3. Update docs if changing behavior
4. PRs reviewed within a few days
