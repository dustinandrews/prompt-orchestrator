"""Tests for prompt-orchestrator — package structure, CLI, and workflow config."""
import os
import sys
import tempfile
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
import yaml


def test_steps_yaml_valid():
    """Verify steps.yaml is valid YAML with expected structure."""
    config = yaml.safe_load(open(".setup/steps.yaml"))
    assert "commands" in config
    assert len(config["commands"]) >= 10


def test_steps_yaml_has_required_fields():
    """Verify each command has required fields."""
    config = yaml.safe_load(open(".setup/steps.yaml"))
    for i, cmd in enumerate(config["commands"]):
        assert "step" in cmd, f"Step {i} missing 'step' field"
        assert ".orchestrator/command/orchestrator." in " ".join(cmd.get("files", [])), (
            f"Step {i} references non-orchestrator command file"
        )


def test_template_structure():
    """Verify template directory structure exists."""
    template_dir = Path("template")
    assert template_dir.is_dir()
    assert (template_dir / ".orchestrator" / "templates").is_dir()
    assert (template_dir / ".orchestrator" / "command").is_dir()


def test_required_template_files():
    """Verify all required template files exist."""
    required = [
        "template/.orchestrator/templates/spec-template.md",
        "template/.orchestrator/command/orchestrator.specify.md",
    ]
    missing = [f for f in required if not Path(f).exists()]
    assert not missing, f"Missing files: {missing}"


def test_package_structure():
    """Verify the installable package structure is intact."""
    pkg = Path("prompt_orchestrator")
    assert pkg.is_dir()
    assert (pkg / "__init__.py").exists()
    assert (pkg / "cli.py").exists()
    assert (pkg / "runner.py").exists()
    assert (pkg / "scaffold" / "command" / "orchestrator.specify.md").exists()
    assert (pkg / "scaffold" / "templates" / "spec-template.md").exists()
    assert (pkg / "project_skeleton" / "pyproject.toml").exists()


def test_cli_init_creates_scaffold():
    """Verify prompt-orchestrator init creates .orchestrator/ in existing project."""
    import subprocess

    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).parent.parent)

    with tempfile.TemporaryDirectory() as tmpdir:
        result = subprocess.run(
            [sys.executable, "-m", "prompt_orchestrator.cli", "init"],
            cwd=tmpdir,
            capture_output=True,
            text=True,
            env=env,
        )
        assert result.returncode == 0, f"init failed: {result.stderr}"

        project = Path(tmpdir)
        assert (project / ".orchestrator" / "command").is_dir()
        assert (project / ".orchestrator" / "templates").is_dir()
        assert (project / ".orchestrator" / "memory").is_dir()
        assert (project / "._agents_not_allowed" / "steps.yaml").exists()
        assert (project / "._agents_not_allowed" / "run_steps.py").exists()


def test_cli_new_creates_project():
    """Verify prompt-orchestrator new creates full project from skeleton."""
    import subprocess

    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).parent.parent)

    with tempfile.TemporaryDirectory() as tmpdir:
        spec_path = Path(tmpdir) / "spec.md"
        spec_path.write_text("# Test spec")

        result = subprocess.run(
            [
                sys.executable, "-m", "prompt_orchestrator.cli",
                "new",
                "--name", "test-project",
                "--spec", str(spec_path),
                "--target-dir", tmpdir,
            ],
            cwd=tmpdir,
            capture_output=True,
            text=True,
            env=env,
        )
        assert result.returncode == 0, f"new failed: {result.stderr}"

        project = Path(tmpdir) / "test-project"
        assert project.is_dir()
        assert (project / "userspec.md").exists()
        assert (project / "._agents_not_allowed" / "steps.yaml").exists()
        assert (project / "._agents_not_allowed" / "run_steps.py").exists()
        assert (project / ".orchestrator" / "command").is_dir()


def test_setup_script_help():
    """Verify old setup.py still works."""
    import subprocess
    result = subprocess.run(
        ["python3", ".setup/setup.py", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "--target-dir" in result.stdout


def test_setup_creates_valid_project():
    """Verify old setup.py creates valid project structure."""
    import subprocess
    import shutil

    with tempfile.TemporaryDirectory() as tmpdir:
        spec_path = Path(tmpdir) / "spec.md"
        spec_path.write_text("# Test\n\nA simple test spec.")

        project_dir = Path(tmpdir) / "test-project"

        result = subprocess.run(
            [
                "python3", ".setup/setup.py",
                "--project-name", "test-project",
                "--spec-path", str(spec_path),
                "--target-dir", tmpdir,
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, f"setup.py failed: {result.stderr}"
        assert project_dir.exists()
        assert (project_dir / "userspec.md").exists()
        assert (project_dir / "steps.yaml").exists()
        assert (project_dir / "._agents_not_allowed").is_dir()
        assert (project_dir / "._agents_not_allowed" / "run_steps.py").exists()
        assert (project_dir / "._agents_not_allowed" / "steps.yaml").exists()


def test_config_has_backend_field():
    """Verify Config dataclass accepts backend field with default opencode."""
    from prompt_orchestrator.runner import Config

    config = Config(
        project_name="test",
        debug=False,
        message="",
        max_retries=3,
        models={},
        commands=(),
    )
    assert config.backend == "opencode"

    config_smol = Config(
        project_name="test",
        debug=False,
        message="",
        max_retries=3,
        models={},
        commands=(),
        backend="smolagents",
    )
    assert config_smol.backend == "smolagents"


def test_cli_parser_accepts_backend_flag():
    """Verify CLI parser accepts --backend flag with correct choices."""
    import subprocess

    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).parent.parent)

    result = subprocess.run(
        [sys.executable, "-m", "prompt_orchestrator.cli", "run", "--help"],
        capture_output=True,
        text=True,
        env=env,
    )
    assert result.returncode == 0
    assert "--backend" in result.stdout
    assert "opencode" in result.stdout
    assert "smolagents" in result.stdout


def test_build_smolagents_prompt_reads_files():
    """Verify build_smolagents_prompt reads the same files as build_opencode_cmd."""
    from prompt_orchestrator.runner import build_smolagents_prompt

    with tempfile.TemporaryDirectory() as tmpdir:
        f1 = Path(tmpdir) / "cmd.md"
        f1.write_text("# Command\nDo something.")
        f2 = Path(tmpdir) / "template.md"
        f2.write_text("# Template\nUse this.")

        prompt = build_smolagents_prompt(
            command="specify",
            model=None,
            files=(str(f1), str(f2)),
            debug=False,
            base_message="Base msg",
            extra=("extra1",),
        )

        assert "Base msg" in prompt
        assert "extra1" in prompt
        assert "Do something." in prompt
        assert "Use this." in prompt


def test_invalid_backend_error():
    """Verify invalid backend value is rejected."""
    from prompt_orchestrator.runner import Config, run_workflow
    import io

    config = Config(
        project_name="test",
        debug=False,
        message="",
        max_retries=3,
        models={},
        commands=(),
        backend="invalid",
    )

    # run_workflow should exit on invalid backend
    with tempfile.TemporaryDirectory() as tmpdir:
        log_file = Path(tmpdir) / "test.log"
        log_file.write_text("")

        # Capture stderr
        old_stderr = sys.stderr
        sys.stderr = io.StringIO()
        try:
            with pytest.raises(SystemExit) as exc_info:
                run_workflow(config, log_file)
            assert exc_info.value.code == 1
        finally:
            sys.stderr = old_stderr


def test_smolagents_tools_exist():
    """Verify smolagents file tools are importable and have correct attributes."""
    from prompt_orchestrator.smolagents_tools import ReadFileTool, WriteFileTool, SearchFilesTool

    read_tool = ReadFileTool()
    assert read_tool.name == "read_file"

    write_tool = WriteFileTool()
    assert write_tool.name == "write_file"

    search_tool = SearchFilesTool()
    assert search_tool.name == "search_files"


def test_smolagents_tools_functional():
    """Verify smolagents file tools perform actual filesystem operations."""
    from prompt_orchestrator.smolagents_tools import ReadFileTool, WriteFileTool, SearchFilesTool

    with tempfile.TemporaryDirectory() as tmpdir:
        # Test WriteFileTool
        write_tool = WriteFileTool()
        result = write_tool.forward(path=str(Path(tmpdir) / "subdir" / "test.txt"), content="hello")
        assert "Written to" in result
        assert (Path(tmpdir) / "subdir" / "test.txt").read_text() == "hello"

        # Test ReadFileTool
        read_tool = ReadFileTool()
        content = read_tool.forward(path=str(Path(tmpdir) / "subdir" / "test.txt"))
        assert content == "hello"

        # Test SearchFilesTool
        search_tool = SearchFilesTool()
        old_cwd = os.getcwd()
        try:
            os.chdir(tmpdir)
            results = search_tool.forward(pattern="**/*.txt")
            assert "test.txt" in results
        finally:
            os.chdir(old_cwd)
