#!/usr/bin/env python3
"""
Execute speckit workflow from steps.yaml.

Reads YAML configuration and executes opencode commands sequentially
with validation checkpoints and retry logic.
"""

import argparse
import subprocess
import sys
import traceback
from pathlib import Path
from datetime import datetime

try:
    import yaml
except ImportError:
    print("Error: PyYAML required. Run: pip install pyyaml", file=sys.stderr)
    sys.exit(1)


class WorkflowLogger:
    """Simple file logger for workflow execution."""
    
    def __init__(self, log_dir: Path):
        self.log_file = log_dir / "workflow.log"
        self._write("=" * 60)
        self._write(f"Workflow started at {datetime.now().isoformat()}")
        self._write("=" * 60)
    
    def _write(self, message: str):
        """Write a line to the log file."""
        with open(self.log_file, 'a') as f:
            f.write(message + "\n")
    
    def log_step(self, step_num: int, command: str):
        """Log step execution."""
        self._write(f"{step_num}. {command}")
    
    def log_retry(self, from_step: int, to_step: int, reason: str, attempt: int, max_retries: int):
        """Log a retry attempt."""
        self._write(f"RETRY: Step {from_step} failed, retrying from step {to_step}")
        self._write(f"REASON: {reason}")
        self._write(f"ATTEMPT: {attempt}/{max_retries}")
    
    def log_retry_exceeded(self, step: int, reason: str):
        """Log when retries are exceeded."""
        self._write(f"RETRIES EXCEEDED at step {step}")
        self._write(f"REASON: {reason}")
        self._write("WORKFLOW FAILED")
    
    def log_complete(self):
        """Log successful completion."""
        self._write("WORKFLOW COMPLETE")


class Command:
    """Represents a single workflow step."""
    
    def __init__(self, data: dict):
        self.command = data.get("command")
        self.model = data.get("model")
        self.files = data.get("files", [])
        self.retry_step_on_fail = data.get("retry_step_on_fail")


class OpenCodeExecutor:
    """Executes opencode workflow from YAML configuration."""
    
    def __init__(self, yaml_path: str = None, start_step: int = 1, step_n_extra: list = None):
        # Default: look for ._agents_not_allowed/steps.yaml in CWD
        if yaml_path is None:
            cwd = Path.cwd()
            hidden_config = cwd / "._agents_not_allowed" / "steps.yaml"
            if hidden_config.exists():
                self.yaml_path = hidden_config
                self.log_dir = cwd / "._agents_not_allowed"
            else:
                # Fall back to same directory as script
                script_dir = Path(__file__).parent.resolve()
                self.yaml_path = script_dir / "steps.yaml"
                self.log_dir = script_dir
        else:
            self.yaml_path = Path(yaml_path)
            self.log_dir = self.yaml_path.parent
        
        # Initialize logger
        self.logger = WorkflowLogger(self.log_dir)
        
        self.project_name = "Unnamed Project"
        self.log_level = "INFO"
        self.message = ""
        self.models = {}  # alias -> actual model string
        self.commands = []
        self.start_step = start_step
        self.start_step_override = start_step if start_step > 1 else None
        self.step_n_extra = step_n_extra or []
        self.max_retries_per_validation = 3
        self.retry_counters = {}  # validation_step_index -> retry_count
        
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
        self.max_retries_per_validation = data.get("max_retries_per_validation", 3)
        
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
        print(f"Max retries per validation: {self.max_retries_per_validation}")
    
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
    
    def verify_files(self, files: list) -> tuple:
        """Verify required files exist in feature directory. Returns (success, error_msg)."""
        if not files:
            return True, None
        
        feature_dir = self._get_feature_dir()
        if not feature_dir:
            return False, "No feature directory found in specs/"
        
        missing = []
        for file_path in files:
            # Only check in feature directory - root is wrong
            if not (feature_dir / file_path).exists():
                missing.append(f"{feature_dir}/{file_path}")
        
        if missing:
            return False, f"Missing required files: {', '.join(missing)}"
        
        print(f"Verified files in {feature_dir}: {files}")
        return True, None
    
    def verify_implementation(self) -> tuple:
        """Check that implementation files exist and don't contain placeholders. Returns (success, error_msg)."""
        impl_dirs = ["src", "tests"]
        found_placeholder = False
        placeholder_files = []
        
        for dir_name in impl_dirs:
            dir_path = Path(dir_name)
            if not dir_path.exists():
                return False, f"Implementation directory missing: {dir_name}"
            
            for file_path in dir_path.rglob("*"):
                if file_path.is_file() and file_path.suffix in ('.py', '.toml', '.md'):
                    try:
                        content = file_path.read_text()
                        if '{{' in content and '}}' in content:
                            print(f"ERROR: Placeholders found in {file_path}")
                            placeholder_files.append(str(file_path))
                            found_placeholder = True
                    except Exception:
                        pass
        
        if found_placeholder:
            return False, f"Placeholders found in: {', '.join(placeholder_files)}"
        
        print("Implementation verified: no placeholders found")
        return True, None
    
    def find_retry_step(self, current_index: int, target_command: str) -> int:
        """Find the index of the first matching command going backwards."""
        for i in range(current_index - 1, -1, -1):
            if self.commands[i].command == target_command:
                return i + 1  # Return 1-indexed step number
        return None
    
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
        """Execute all commands in sequence with retry support."""
        i = self.start_step
        
        while i <= len(self.commands):
            cmd = self.commands[i - 1]  # 0-indexed access
            
            print(f"\n{'='*60}")
            print(f"Step {i}/{len(self.commands)} - {cmd.command}")
            print(f"{'='*60}")
            
            # Log step execution
            self.logger.log_step(i, cmd.command)
            
            exit_code = 0
            error_msg = None
            is_verify = cmd.command.startswith("-*-verify-*-")
            
            # Determine if we should pass extra context (only for step N when --step specified)
            step_n_context = None
            if self.start_step_override is not None and i == self.start_step_override and self.step_n_extra:
                step_n_context = self.step_n_extra
                print(f"  [CONTEXT] Adding extra info: {' '.join(self.step_n_extra)}")
            
            try:
                if cmd.command.startswith("-*-verify-*-implementation"):
                    success, error_msg = self.verify_implementation()
                    if not success:
                        exit_code = 1
                elif is_verify:
                    success, error_msg = self.verify_files(cmd.files)
                    if not success:
                        exit_code = 1
                else:
                    resolved_model = self._resolve_model(cmd.model)
                    exit_code = self.execute_command(
                        cmd.command, 
                        model=resolved_model, 
                        files=cmd.files,
                        extra=step_n_context
                    )
            except Exception as e:
                exit_code = 1
                error_msg = str(e)
                print(f"ERROR: {error_msg}")
            
            if exit_code != 0:
                # Check if this is a verify step with retry configured
                if is_verify and cmd.retry_step_on_fail:
                    # Get or initialize retry counter for this validation step
                    retry_count = self.retry_counters.get(i, 0)
                    
                    if retry_count < self.max_retries_per_validation:
                        # Find the step to retry
                        retry_step = self.find_retry_step(i, cmd.retry_step_on_fail)
                        
                        if retry_step:
                            retry_count += 1
                            self.retry_counters[i] = retry_count
                            
                            print(f"\n[RETRY] Validation failed: {error_msg}")
                            print(f"[RETRY] Attempt {retry_count}/{self.max_retries_per_validation}")
                            print(f"[RETRY] Re-running step {retry_step}: {cmd.retry_step_on_fail}")
                            print(f"[RETRY] With context: {error_msg}")
                            
                            # Log the retry
                            self.logger.log_retry(i, retry_step, error_msg, retry_count, self.max_retries_per_validation)
                            
                            # Set up context for retry step
                            self.step_n_extra = [f"VALIDATION ERROR: {error_msg}"]
                            self.start_step_override = retry_step
                            
                            # Jump back to retry step
                            i = retry_step
                            continue
                        else:
                            print(f"\n[RETRY] ERROR: Could not find step '{cmd.retry_step_on_fail}' to retry")
                    else:
                        print(f"\n[RETRY] Max retries ({self.max_retries_per_validation}) exceeded for validation step {i}")
                        self.logger.log_retry_exceeded(i, error_msg)
                
                # If we get here, either no retry configured or max retries exceeded
                print(f"\n[FAIL] Step {i} failed with no more retries available")
                print(f"\nFull traceback:")
                traceback.print_exc()
                sys.exit(1)
            
            # Clear retry context after successful step
            if i == self.start_step_override:
                self.step_n_extra = []
                self.start_step_override = None
            
            # Move to next step
            i += 1
        
        self.logger.log_complete()
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
