"""Tests for run_steps.py configuration and setup.py."""
import os
import sys
import tempfile
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import yaml


def test_steps_yaml_valid():
    """Verify steps.yaml is valid YAML with expected structure."""
    config = yaml.safe_load(open(".setup/steps.yaml"))
    assert "commands" in config
    assert len(config["commands"]) >= 10  # At least 10 steps expected


def test_steps_yaml_has_required_fields():
    """Verify each command has required fields."""
    config = yaml.safe_load(open(".setup/steps.yaml"))
    for i, cmd in enumerate(config["commands"]):
        assert "command" in cmd, f"Command {i} missing 'command' field"


def test_template_structure():
    """Verify template directory structure exists."""
    template_dir = Path("template")
    assert template_dir.is_dir()
    assert (template_dir / ".specify" / "templates").is_dir()
    assert (template_dir / ".opencode" / "command").is_dir()


def test_required_template_files():
    """Verify all required template files exist."""
    required = [
        "template/.specify/templates/spec-template.md",
        "template/.opencode/command/speckit.specify.md",
    ]
    missing = [f for f in required if not Path(f).exists()]
    assert not missing, f"Missing files: {missing}"


def test_setup_script_help():
    """Verify setup.py accepts --target-dir argument."""
    import subprocess
    result = subprocess.run(
        ["python3", ".setup/setup.py", "--help"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    assert "--target-dir" in result.stdout


def test_setup_creates_valid_project():
    """Verify setup.py --target-dir creates valid project structure."""
    import subprocess
    import shutil

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create minimal spec file
        spec_path = Path(tmpdir) / "spec.md"
        spec_path.write_text("# Test\n\nA simple test spec.")

        project_dir = Path(tmpdir) / "test-project"

        result = subprocess.run(
            [
                "python3", ".setup/setup.py",
                "--project-name", "test-project",
                "--spec-path", str(spec_path),
                "--target-dir", tmpdir
            ],
            capture_output=True,
            text=True
        )

        assert result.returncode == 0, f"setup.py failed: {result.stderr}"
        assert project_dir.exists()

        # Verify key files exist
        assert (project_dir / "userspec.md").exists()
        assert (project_dir / "steps.yaml").exists()
        assert (project_dir / "._agents_not_allowed").is_dir()
        assert (project_dir / "._agents_not_allowed" / "run_steps.py").exists()
        assert (project_dir / "._agents_not_allowed" / "steps.yaml").exists()
