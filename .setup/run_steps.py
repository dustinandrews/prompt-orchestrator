#!/usr/bin/env python3
"""
Execute speckit workflow from steps.yaml.

Reads YAML configuration and executes opencode commands sequentially
with validation checkpoints.
"""

import os
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
    
    def __init__(self, yaml_path: str = "steps.yaml"):
        self.yaml_path = Path(yaml_path)
        self.project_name = "Unnamed Project"
        self.log_level = "INFO"
        self.message = ""
        self.commands = []
        
        self._load_yaml()
    
    def _load_yaml(self) -> None:
        """Load and parse steps.yaml."""
        if not self.yaml_path.exists():
            raise FileNotFoundError(f"YAML file not found: {self.yaml_path}")
        
        with open(self.yaml_path, 'r') as f:
            data = yaml.safe_load(f)
        
        self.project_name = data.get("title", "Unnamed Project")
        self.log_level = data.get("log_level", "INFO")
        self.message = data.get("message", "")
        self.commands = [Command(cmd) for cmd in data.get("commands", [])]
        
        print(f"Loaded {len(self.commands)} commands for: {self.project_name}")
    
    def verify_files(self, files: list) -> None:
        """Verify required files exist."""
        if not files:
            return
        
        missing = []
        for file_path in files:
            if not Path(file_path).exists():
                missing.append(file_path)
        
        if missing:
            raise FileNotFoundError(f"Missing required files: {', '.join(missing)}")
        
        print(f"Verified files: {files}")
    
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
    
    def execute_command(self, command: str, model: str = None, files: list = None) -> int:
        """Execute a single opencode command."""
        files = files or []
        
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
        cmd.append(full_message)
        
        print(f"  Command: {' '.join(cmd[:10])}...")  # Truncate for display
        
        # Execute
        result = subprocess.run(cmd, capture_output=False, text=True)
        return result.returncode
    
    def run(self) -> None:
        """Execute all commands in sequence."""
        for i, cmd in enumerate(self.commands, 1):
            print(f"\n{'='*60}")
            print(f"Step {i}/{len(self.commands)}")
            print(f"{'='*60}")
            
            if cmd.command.startswith("-*-verify-*-implementation"):
                self.verify_implementation()
            elif cmd.command.startswith("-*-verify-*-"):
                self.verify_files(cmd.files)
            else:
                exit_code = self.execute_command(
                    cmd.command, 
                    model=cmd.model, 
                    files=cmd.files
                )
                if exit_code != 0:
                    print(f"ERROR: Command failed with exit code {exit_code}")
                    sys.exit(exit_code)
        
        print(f"\n{'='*60}")
        print("Workflow complete!")


if __name__ == "__main__":
    executor = OpenCodeExecutor()
    executor.run()
