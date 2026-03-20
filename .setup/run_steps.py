#!/usr/bin/env python3
"""
Execute speckit workflow from steps.yaml.

Reads YAML configuration and executes opencode commands sequentially
with validation checkpoints.
"""

import argparse
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("Error: PyYAML required. Run: pip install pyyaml", file=sys.stderr)
    sys.exit(1)


class Command:
    """Represents a single workflow step."""
    
    def __init__(self, data: dict):
        self.command = data.get("command")
        self.model = data.get("model")
        self.files = data.get("files", [])


class OpenCodeExecutor:
    """Executes opencode workflow from YAML configuration."""
    
    def __init__(self, yaml_path: str = None, start_step: int = 1, step_n_extra: list = None):
        # Default to steps.yaml in same directory as this script
        if yaml_path is None:
            script_dir = Path(__file__).parent.resolve()
            self.yaml_path = script_dir / "steps.yaml"
        else:
            self.yaml_path = Path(yaml_path)
        
        self.project_name = "Unnamed Project"
        self.log_level = "INFO"
        self.message = ""
        self.models = {}  # alias -> actual model string
        self.commands = []
        self.start_step = start_step
        self.start_step_override = start_step if start_step > 1 else None
        self.step_n_extra = step_n_extra or []
        
        self._load_yaml()
        self._validate_start_step()
    
    def _load_yaml(self) -> None:
        """Load and parse steps.yaml."""
        if not self.yaml_path.exists():
            raise FileNotFoundError(f"YAML file not found: {self.yaml_path}")
        
        with open(self.yaml_path, 'r') as f:
            data = yaml.safe_load(f)
        
        self.project_name = data.get("title", "Unnamed Project")
        self.log_level = data.get("log_level", "INFO")
        self.message = data.get("message", "")
        
        # Parse models section: list of dicts like [{"alias": {"model": "value"}}]
        raw_models = data.get("models", [])
        for item in raw_models:
            if isinstance(item, dict):
                for alias, config in item.items():
                    if isinstance(config, dict) and "model" in config:
                        self.models[alias] = config["model"]
        
        self.commands = [Command(cmd) for cmd in data.get("commands", [])]
        
        print(f"Loaded {len(self.commands)} commands for: {self.project_name}")
        print(f"Defined models: {list(self.models.keys())}")
    
    def _validate_start_step(self) -> None:
        """Validate start step is in range."""
        if self.start_step < 1 or self.start_step > len(self.commands):
            print(f"ERROR: Step {self.start_step} out of range (1-{len(self.commands)})", file=sys.stderr)
            sys.exit(1)
        
        if self.start_step > 1:
            print(f"\nStarting at step {self.start_step}")
    
    def _resolve_model(self, model_ref: str) -> str:
        """Resolve model alias to actual model string, or return as-is if not found."""
        if model_ref is None:
            return None
        return self.models.get(model_ref, model_ref)
    
    def _get_feature_dir(self) -> Path:
        """Find the speckit feature directory (e.g., specs/001-feature-name)."""
        specs_dir = Path("specs")
        if not specs_dir.exists():
            return None
        
        # Find first subdirectory in specs/
        for item in specs_dir.iterdir():
            if item.is_dir():
                return item
        
        return None
    
    def verify_files(self, files: list) -> None:
        """Verify required files exist in feature directory."""
        if not files:
            return
        
        feature_dir = self._get_feature_dir()
        if not feature_dir:
            raise FileNotFoundError("No feature directory found in specs/")
        
        missing = []
        for file_path in files:
            # Only check in feature directory - root is wrong
            if not (feature_dir / file_path).exists():
                missing.append(f"{feature_dir}/{file_path}")
        
        if missing:
            raise FileNotFoundError(f"Missing required files: {', '.join(missing)}")
        
        print(f"Verified files in {feature_dir}: {files}")
    
    def verify_implementation(self) -> None:
        """Check that implementation files exist and don't contain placeholders."""
        impl_dirs = ["src", "tests"]
        found_placeholder = False
        
        for dir_name in impl_dirs:
            dir_path = Path(dir_name)
            if not dir_path.exists():
                raise FileNotFoundError(f"Implementation directory missing: {dir_name}")
            
            for file_path in dir_path.rglob("*"):
                if file_path.is_file() and file_path.suffix in ('.py', '.toml', '.md'):
                    try:
                        content = file_path.read_text()
                        if '{{' in content and '}}' in content:
                            print(f"ERROR: Placeholders found in {file_path}")
                            found_placeholder = True
                    except Exception:
                        pass
        
        if found_placeholder:
            raise ValueError("Implementation files contain unfilled placeholders")
        
        print("Implementation verified: no placeholders found")
    
    def execute_command(self, command: str, model: str = None, files: list = None, extra: list = None) -> int:
        """Execute a single opencode command."""
        files = files or []
        extra = extra or []
        
        print(f"Executing: {command}")
        if model:
            print(f"  Model: {model}")
        
        # Build opencode command
        cmd = ["opencode", "run", "--log-level", self.log_level]
        
        for file_path in files:
            cmd.extend(["-f", file_path])
        
        if model:
            cmd.extend(["--model", model])
        
        # Add message as final argument
        full_message = f"{command}"
        if self.message:
            full_message = f"{command} {self.message}"
        if extra:
            full_message = f"{full_message} {' '.join(extra)}"
        cmd.append(full_message)
        
        print(f"  Command: {' '.join(cmd[:10])}...")  # Truncate for display
        
        # Execute
        result = subprocess.run(cmd, capture_output=False, text=True)
        return result.returncode
    
    def run(self) -> None:
        """Execute all commands in sequence."""
        for i, cmd in enumerate(self.commands, 1):
            # Skip steps before start_step
            if i < self.start_step:
                print(f"\nSkipping step {i}: {cmd.command}")
                continue
            
            print(f"\n{'='*60}")
            print(f"Step {i}/{len(self.commands)}")
            print(f"{'='*60}")
            
            exit_code = 0
            
            # Determine if we should pass extra context (only for step N when --step specified)
            step_n_context = None
            if self.start_step_override is not None and i == self.start_step_override and self.step_n_extra:
                step_n_context = self.step_n_extra
                print(f"  [CONTEXT] Adding extra info: {' '.join(self.step_n_extra)}")
            
            if cmd.command.startswith("-*-verify-*-implementation"):
                self.verify_implementation()
            elif cmd.command.startswith("-*-verify-*-"):
                self.verify_files(cmd.files)
            else:
                resolved_model = self._resolve_model(cmd.model)
                exit_code = self.execute_command(
                    cmd.command, 
                    model=resolved_model, 
                    files=cmd.files,
                    extra=step_n_context
                )
            
            if exit_code != 0:
                print(f"ERROR: Command failed with exit code {exit_code}")
                sys.exit(exit_code)
        
        print(f"\n{'='*60}")
        print("Workflow complete!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Execute speckit workflow from steps.yaml",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_steps.py                      # Start from step 1
  python run_steps.py --step 5             # Start at step 5
  python run_steps.py -s 5 "error in line 42"  # Step 5 with context, then normal
        """
    )
    parser.add_argument(
        "-s", "--step",
        type=int,
        default=1,
        metavar="N",
        help="Start at step N (1-indexed, default: 1)"
    )
    parser.add_argument(
        "extra",
        nargs="*",
        help="Additional context for step N only (e.g., error message)"
    )
    
    args = parser.parse_args()
    
    # Only use extra args if --step was specified (and not default 1)
    step_n_extra = args.extra if args.step > 1 else None
    
    executor = OpenCodeExecutor(start_step=args.step, step_n_extra=step_n_extra)
    executor.run()
