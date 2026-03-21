#!/usr/bin/env python3
"""
Execute speckit workflow from steps.yaml.

Functional-style workflow executor with immutable state transitions.
"""

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Callable, Optional

try:
    import yaml
except ImportError:
    print("Error: PyYAML required. Run: pip install pyyaml", file=sys.stderr)
    sys.exit(1)


# ============================================================================
# Pure Data Structures
# ============================================================================

@dataclass(frozen=True)
class Command:
    """Immutable workflow step definition."""
    name: str
    model_alias: Optional[str]
    files: tuple = field(default_factory=tuple)
    verify: Optional[dict] = None
    verify_implementation: bool = False
    retry_step_on_fail: Optional[str] = None


@dataclass(frozen=True)
class Config:
    """Immutable workflow configuration."""
    project_name: str
    log_level: str
    message: str
    max_retries: int
    models: dict
    commands: tuple


@dataclass(frozen=True)
class StepContext:
    """Immutable execution context for a single step."""
    step_num: int
    command: Command
    retry_count: int = 0
    extra_context: tuple = field(default_factory=tuple)


@dataclass(frozen=True)
class VerificationResult:
    """Pure result of verification."""
    success: bool
    error_type: Optional[str] = None  # 'file_not_found', 'review_fail', 'implementation'
    message: Optional[str] = None


@dataclass(frozen=True)
class ExecutionResult:
    """Pure result of command execution."""
    exit_code: int
    error_msg: Optional[str] = None


@dataclass(frozen=True)
class RetryDecision:
    """Pure decision about retry behavior."""
    should_retry: bool
    target_step: Optional[int] = None
    target_command: Optional[str] = None
    new_context: tuple = field(default_factory=tuple)


# ============================================================================
# Pure Functions: Configuration Loading
# ============================================================================

def parse_models(raw_models: list) -> dict:
    """Parse model aliases from YAML structure."""
    result = {}
    for item in raw_models:
        if isinstance(item, dict):
            for alias, config in item.items():
                if isinstance(config, dict) and "model" in config:
                    result[alias] = config["model"]
    return result


def parse_command(data: dict) -> Command:
    """Parse single command from YAML dict."""
    return Command(
        name=data.get("command", ""),
        model_alias=data.get("model"),
        files=tuple(data.get("files", [])),
        verify=data.get("verify"),
        verify_implementation=data.get("verify_implementation", False),
        retry_step_on_fail=data.get("retry_step_on_fail")
    )


def load_config(yaml_path: Path) -> Config:
    """Load configuration from YAML file."""
    if not yaml_path.exists():
        raise FileNotFoundError(f"YAML file not found: {yaml_path}")

    with open(yaml_path, 'r') as f:
        data = yaml.safe_load(f)

    commands = tuple(parse_command(cmd) for cmd in data.get("commands", []))

    return Config(
        project_name=data.get("title", "Unnamed Project"),
        log_level=data.get("log_level", "INFO"),
        message=data.get("message", ""),
        max_retries=data.get("max_retries_per_validation", 3),
        models=parse_models(data.get("models", [])),
        commands=commands
    )


# ============================================================================
# Pure Functions: Path Resolution
# ============================================================================

def resolve_yaml_path(yaml_path: Optional[str] = None) -> Path:
    """Determine YAML file location based on defaults."""
    if yaml_path:
        return Path(yaml_path)

    cwd = Path.cwd()
    hidden_config = cwd / "._agents_not_allowed" / "steps.yaml"

    if hidden_config.exists():
        return hidden_config

    return Path(__file__).parent.resolve() / "steps.yaml"


def get_log_dir(yaml_path: Path) -> Path:
    """Determine log directory from YAML path."""
    return yaml_path.parent


def find_feature_dir(base_dir: Path) -> Optional[Path]:
    """Find feature directory by running check-prerequisites.sh and parsing JSON output."""
    import json
    script_path = base_dir / ".specify" / "scripts" / "bash" / "check-prerequisites.sh"

    if not script_path.exists():
        # Fallback to directory scanning if script not present
        specs_dir = base_dir / "specs"
        if not specs_dir.exists():
            return None
        for item in specs_dir.iterdir():
            if item.is_dir():
                return item
        return None

    try:
        result = subprocess.run(
            [str(script_path), "--json", "--require-tasks", "--include-tasks"],
            capture_output=True,
            text=True,
            cwd=base_dir
        )
        if result.returncode != 0:
            return None

        # Parse JSON from last line (in case of preceding output)
        lines = result.stdout.strip().split('\n')
        for line in reversed(lines):
            try:
                data = json.loads(line)
                if "FEATURE_DIR" in data:
                    return Path(data["FEATURE_DIR"])
            except json.JSONDecodeError:
                continue
        return None
    except Exception:
        return None


# ============================================================================
# Pure Functions: Verification Logic
# ============================================================================

def check_review_status(content: str) -> VerificationResult:
    """Parse review content for PASS/FAIL marker."""
    match = re.search(r'^STATUS:\s*(PASS|FAIL)', content, re.MULTILINE | re.IGNORECASE)

    if not match:
        return VerificationResult(
            success=False,
            error_type="review_fail",
            message="No STATUS marker found (expected 'STATUS: PASS' or 'STATUS: FAIL')"
        )

    status = match.group(1).upper()

    if status == "PASS":
        return VerificationResult(success=True)

    reason_match = re.search(r'^If FAIL:\s*(.+)$', content, re.MULTILINE | re.IGNORECASE)
    reason = reason_match.group(1) if reason_match else "Review marked as FAIL"

    return VerificationResult(
        success=False,
        error_type="review_fail",
        message=f"FAIL - {reason}"
    )


def verify_file_exists(feature_dir: Path, file_path: str) -> VerificationResult:
    """Check if single file exists in feature directory."""
    full_path = feature_dir / file_path
    if not full_path.exists():
        return VerificationResult(
            success=False,
            error_type="file_not_found",
            message=f"Missing: {feature_dir}/{file_path}"
        )

    if file_path.endswith('-review.md'):
        try:
            content = full_path.read_text()
            result = check_review_status(content)
            if not result.success:
                return VerificationResult(
                    success=False,
                    error_type="review_fail",
                    message=f"{file_path}: {result.message}"
                )
        except Exception as e:
            return VerificationResult(
                success=False,
                error_type="review_fail",
                message=f"{file_path}: Error reading - {e}"
            )

    return VerificationResult(success=True)


def verify_files(feature_dir: Optional[Path], files: tuple) -> VerificationResult:
    """Verify all required files exist and pass review checks."""
    if not files:
        return VerificationResult(success=True)

    if not feature_dir:
        return VerificationResult(
            success=False,
            error_type="file_not_found",
            message="No feature directory found in specs/"
        )

    for file_path in files:
        result = verify_file_exists(feature_dir, file_path)
        if not result.success:
            return result

    return VerificationResult(success=True)


def has_placeholders(content: str) -> bool:
    """Check if content contains placeholder markers."""
    return '{{' in content and '}}' in content


def scan_directory_for_placeholders(dir_path: Path) -> list:
    """Recursively scan directory for files with placeholders."""
    found = []
    if not dir_path.exists():
        return found

    for file_path in dir_path.rglob("*"):
        if file_path.is_file() and file_path.suffix in ('.py', '.toml', '.md'):
            try:
                content = file_path.read_text()
                if has_placeholders(content):
                    found.append(str(file_path))
            except Exception:
                pass
    return found


def verify_implementation(base_dir: Path) -> VerificationResult:
    """Check implementation directories for placeholders."""
    impl_dirs = ["src", "tests"]
    all_placeholders = []

    for dir_name in impl_dirs:
        dir_path = base_dir / dir_name
        if not dir_path.exists():
            return VerificationResult(
                success=False,
                error_type="implementation",
                message=f"Directory missing: {dir_name}"
            )
        placeholders = scan_directory_for_placeholders(dir_path)
        all_placeholders.extend(placeholders)

    if all_placeholders:
        return VerificationResult(
            success=False,
            error_type="implementation",
            message=f"Placeholders found in: {', '.join(all_placeholders)}"
        )

    return VerificationResult(success=True)


# ============================================================================
# Pure Functions: Retry Logic
# ============================================================================

def find_step_index(commands: tuple, target_command: str, current_index: int) -> Optional[int]:
    """Find 1-indexed step number for command, searching backwards from current."""
    for i in range(current_index - 1, -1, -1):
        if commands[i].name == target_command:
            return i + 1
    return None


def compute_retry_decision(
    context: StepContext,
    exec_result: ExecutionResult,
    verify_result: VerificationResult,
    config: Config,
    commands: tuple
) -> RetryDecision:
    """Pure function: determine retry strategy based on results."""

    # No failure - no retry
    if exec_result.exit_code == 0 and verify_result.success:
        return RetryDecision(should_retry=False)

    # Check retry limits
    if context.retry_count >= config.max_retries:
        return RetryDecision(should_retry=False)

    current_idx = context.step_num - 1
    cmd = context.command

    # Command execution failed - retry same step
    if exec_result.exit_code != 0:
        return RetryDecision(
            should_retry=True,
            target_step=context.step_num,
            target_command=cmd.name,
            new_context=(f"VALIDATION ERROR: {exec_result.error_msg or 'Command failed'}",)
        )

    # File not found - retry same step or configured fallback
    if verify_result.error_type == "file_not_found":
        target_step = context.step_num
        target_name = cmd.name

        if cmd.verify and cmd.verify.get("retry_step_on_file_not_found"):
            found = find_step_index(commands, cmd.verify["retry_step_on_file_not_found"], current_idx)
            if found:
                target_step = found
                target_name = cmd.verify["retry_step_on_file_not_found"]

        return RetryDecision(
            should_retry=True,
            target_step=target_step,
            target_command=target_name,
            new_context=(f"VALIDATION ERROR: {verify_result.message}",)
        )

    # Review or implementation failure - use configured retry step
    if verify_result.error_type in ("review_fail", "implementation"):
        retry_target = None

        if cmd.verify and cmd.verify.get("retry_step_on_fail"):
            retry_target = cmd.verify["retry_step_on_fail"]
        elif cmd.retry_step_on_fail:
            retry_target = cmd.retry_step_on_fail

        if retry_target:
            found = find_step_index(commands, retry_target, current_idx)
            if found:
                return RetryDecision(
                    should_retry=True,
                    target_step=found,
                    target_command=retry_target,
                    new_context=(f"VALIDATION ERROR: {verify_result.message}",)
                )

    # No valid retry target found
    return RetryDecision(should_retry=False)


# ============================================================================
# I/O Functions: Side Effects Isolated
# ============================================================================

def write_log(log_file: Path, message: str) -> None:
    """Append message to log file."""
    with open(log_file, 'a') as f:
        f.write(message + "\n")


def create_logger(log_dir: Path) -> Path:
    """Initialize log file and return path."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"workflow_{timestamp}.log"
    write_log(log_file, "=" * 60)
    write_log(log_file, f"Workflow started at {datetime.now().isoformat()}")
    write_log(log_file, "=" * 60)
    return log_file


def log_step(log_file: Path, step_num: int, command: str) -> None:
    """Log step execution to file."""
    write_log(log_file, f"{step_num}. {command}")


def log_retry(log_file: Path, from_step: int, to_step: int, reason: str, attempt: int, max_retries: int) -> None:
    """Log retry attempt to file."""
    write_log(log_file, f"RETRY: Step {from_step} failed, retrying from step {to_step}")
    write_log(log_file, f"REASON: {reason}")
    write_log(log_file, f"ATTEMPT: {attempt}/{max_retries}")


def log_failure(log_file: Path, step: int, reason: str) -> None:
    """Log final failure to file."""
    write_log(log_file, f"RETRIES EXCEEDED at step {step}")
    write_log(log_file, f"REASON: {reason}")
    write_log(log_file, "WORKFLOW FAILED")


def log_complete(log_file: Path) -> None:
    """Log successful completion."""
    write_log(log_file, "WORKFLOW COMPLETE")


def build_opencode_cmd(
    command: str,
    model: Optional[str],
    files: tuple,
    log_level: str,
    base_message: str,
    extra: tuple
) -> list:
    """Construct opencode command list."""
    cmd = ["opencode", "run", "--continue", "--log-level", log_level]

    for file_path in files:
        cmd.extend(["-f", file_path])

    if model:
        cmd.extend(["--model", model])

    full_message = command
    if base_message:
        full_message = f"{command} {base_message}"
    if extra:
        full_message = f"{full_message} {' '.join(extra)}"
    cmd.append(full_message)

    return cmd


def execute_opencode(cmd: list) -> ExecutionResult:
    """Execute opencode command and return pure result."""
    try:
        result = subprocess.run(cmd, capture_output=False, text=True)
        return ExecutionResult(exit_code=result.returncode)
    except Exception as e:
        return ExecutionResult(exit_code=1, error_msg=str(e))


# ============================================================================
# Main Execution Loop
# ============================================================================

def run_workflow(
    config: Config,
    log_file: Path,
    start_step: int = 1,
    step_n_extra: Optional[list] = None
) -> None:
    """Execute workflow with functional state management."""

    state = {
        'current_step': start_step,
        'retry_counters': {},
        'start_step_override': start_step if start_step > 1 else None,
        'step_n_extra': tuple(step_n_extra) if step_n_extra else ()
    }

    project_root = log_file.parent.parent  # Go up from ._agents_not_allowed/
    feature_dir = find_feature_dir(project_root)

    print(f"Loaded {len(config.commands)} commands for: {config.project_name}")
    print(f"Defined models: {list(config.models.keys())}")
    print(f"Max retries per validation: {config.max_retries}")

    if start_step > 1:
        print(f"\nStarting at step {start_step}")

    while state['current_step'] <= len(config.commands):
        step_num = state['current_step']
        cmd = config.commands[step_num - 1]

        print(f"\n{'='*60}")
        print(f"Step {step_num}/{len(config.commands)} - {cmd.name}")
        print(f"{'='*60}")

        log_step(log_file, step_num, cmd.name)

        # Determine extra context for this step
        extra = ()
        if state['start_step_override'] == step_num and state['step_n_extra']:
            extra = state['step_n_extra']
            print(f"  [CONTEXT] Adding extra info: {' '.join(extra)}")

        # Build and execute command
        model = config.models.get(cmd.model_alias, cmd.model_alias) if cmd.model_alias else None
        if model is None and cmd.model_alias is not None:
            raise ValueError(f"Model cannot be null for command: {cmd.name}")

        opencode_cmd = build_opencode_cmd(
            cmd.name, model, cmd.files, config.log_level, config.message, extra
        )

        print(f"Executing: {cmd.name}")
        if model:
            print(f"  Model: {model}")
        print(f"  Command: {' '.join(opencode_cmd[:10])}...")

        exec_result = execute_opencode(opencode_cmd)

        # Run verification if configured
        verify_result = VerificationResult(success=True)

        if exec_result.exit_code == 0 and cmd.verify_implementation:
            verify_result = verify_implementation(project_root)

        if exec_result.exit_code == 0 and cmd.verify and verify_result.success:
            files_to_check = tuple(cmd.verify.get("files", []))
            verify_result = verify_files(feature_dir, files_to_check)

        # Compute retry decision
        context = StepContext(
            step_num=step_num,
            command=cmd,
            retry_count=state['retry_counters'].get(step_num, 0),
            extra_context=extra
        )

        decision = compute_retry_decision(context, exec_result, verify_result, config, config.commands)

        if decision.should_retry:
            # Update retry counter for the target step (the one we're jumping to)
            target_retry_count = state['retry_counters'].get(decision.target_step, 0) + 1
            state['retry_counters'][decision.target_step] = target_retry_count

            print(f"\n[RETRY] {verify_result.message or exec_result.error_msg}")
            print(f"[RETRY] Attempt {target_retry_count}/{config.max_retries} for step {decision.target_step}")
            print(f"[RETRY] Re-running step {decision.target_step}: {decision.target_command}")

            log_retry(
                log_file, step_num, decision.target_step,
                verify_result.message or exec_result.error_msg or "Command failed",
                target_retry_count, config.max_retries
            )

            # Set up retry state
            state['step_n_extra'] = decision.new_context
            state['start_step_override'] = decision.target_step
            state['current_step'] = decision.target_step
            continue

        # Check if we should fail
        if exec_result.exit_code != 0 or not verify_result.success:
            print(f"\n[RETRY] Max retries ({config.max_retries}) exceeded for step {step_num}")
            log_failure(log_file, step_num, verify_result.message or exec_result.error_msg)
            print(f"\n[FAIL] Step {step_num} failed with no more retries available")
            sys.exit(1)

        # Clear context after successful step
        if step_num == state['start_step_override']:
            state['step_n_extra'] = ()
            state['start_step_override'] = None

        # Advance to next step
        state['current_step'] += 1

    log_complete(log_file)
    print(f"\n{'='*60}")
    print("Workflow complete!")


# ============================================================================
# CLI Entry Point
# ============================================================================

def validate_start_step(start_step: int, num_commands: int) -> None:
    """Validate start step is within valid range."""
    if start_step < 1 or start_step > num_commands:
        print(f"ERROR: Step {start_step} out of range (1-{num_commands})", file=sys.stderr)
        sys.exit(1)


def main():
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

    yaml_path = resolve_yaml_path()
    config = load_config(yaml_path)
    validate_start_step(args.step, len(config.commands))

    log_dir = get_log_dir(yaml_path)
    log_file = create_logger(log_dir)

    step_n_extra = args.extra if args.step > 1 else None

    run_workflow(config, log_file, start_step=args.step, step_n_extra=step_n_extra)


if __name__ == "__main__":
    main()
