#!/usr/bin/env python3
"""
Parse opencode-seq YAML and output bash commands for manual execution.
Workaround for OpenCode bug #15150 which breaks the HTTP /command endpoint.

Usage:
    python3 yaml-to-cli.py steps.yaml
    python3 yaml-to-cli.py steps.yaml > run.sh && bash run.sh
"""

import argparse
import sys
from typing import List, Dict, Any

import yaml


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert opencode-seq YAML to bash commands"
    )
    parser.add_argument(
        "config",
        help="Path to YAML config file with commands",
    )
    args = parser.parse_args()

    # Load config
    with open(args.config, "r") as f:
        config = yaml.safe_load(f)

    global_message = config.get("message", "")
    log_level = config.get("log_level", "INFO")
    commands: List[Dict[str, Any]] = config.get("commands", [])

    if not commands:
        print("# ERROR: No commands found in config", file=sys.stderr)
        sys.exit(1)

    # Print header
    print("#!/bin/bash")
    print("# Auto-generated from YAML config")
    print("# Run with: bash run.sh")
    print()
    print("set -e  # Fail fast")
    print()

    # Map commands to their template files (only include ones that exist)
    # Standard speckit templates available:
    #   spec-template.md, spec-review-template.md
    #   plan-template.md, plan-review-template.md
    #   tasks-template.md, tasks-review-template.md
    # Note: analyze, implement, test-review, product-review don't have
    # dedicated templates - the command file provides sufficient context
    template_map = {
        "/speckit.specify": ".specify/templates/spec-template.md",
        "/speckit.spec-review": ".specify/templates/spec-review-template.md",
        "/speckit.plan": ".specify/templates/plan-template.md",
        "/speckit.plan-review": ".specify/templates/plan-review-template.md",
        "/speckit.tasks": ".specify/templates/tasks-template.md",
        "/speckit.tasks-review": ".specify/templates/tasks-review-template.md",
    }

    for idx, cmd_spec in enumerate(commands, 1):
        command_text = cmd_spec.get("command", "")
        model = cmd_spec.get("model")
        cmd_message = cmd_spec.get("message", global_message)

        if not command_text:
            print(f"# WARNING: Command {idx} missing 'command' field", file=sys.stderr)
            continue

        # Parse command and arguments
        parts = command_text.split(" ", 1)
        cmd_name = parts[0]
        cmd_args = parts[1] if len(parts) > 1 else ""

        # Append message if present
        if cmd_message:
            cmd_args = f"{cmd_args} {cmd_message}" if cmd_args else cmd_message

        print(f'echo "Step {idx}/{len(commands)} - {cmd_name[1:]}.md"')

        # Build command with file attachments
        if cmd_name.startswith("/speckit."):
            cmd_parts = ["opencode", "run", "--log-level", log_level]
            
            # Add command file
            cmd_file = f".opencode/command/{cmd_name[1:]}.md"
            cmd_parts.extend(["-f", cmd_file])
            
            # Add template file if known
            if cmd_name in template_map:
                template_file = template_map[cmd_name]
                cmd_parts.extend(["-f", template_file])
            
            # Add model
            if model:
                cmd_parts.extend(["--model", model])
            
            # Add continue flag
            if idx > 1:
                cmd_parts.append("--continue")
            
            # Add arguments as message
            if cmd_args:
                escaped_args = cmd_args.replace('"', '\\"')
                cmd_parts.append(f'"{escaped_args}"')
            
            print(" ".join(cmd_parts))
        elif cmd_name == "/compact":
            # Compact is a built-in command
            cmd_parts = ["opencode", "run", "--log-level", log_level, "--command", "compact"]
            if idx > 1:
                cmd_parts.append("--continue")
            print(" ".join(cmd_parts))
        else:
            # Other commands - pass through as-is
            escaped = command_text.replace('"', '\\"')
            cmd_parts = ["opencode", "run", "--log-level", log_level, f'"{escaped}"']
            if model:
                cmd_parts.extend(["--model", model])
            if idx > 1:
                cmd_parts.append("--continue")
            print(" ".join(cmd_parts))
        
        print()

    print("# All commands executed successfully")


if __name__ == "__main__":
    main()
