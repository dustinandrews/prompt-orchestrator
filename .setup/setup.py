#!/usr/bin/env python3
"""
Setup script for FullAutoTemplate projects.

Creates a new project from the template, generates run.sh, and prepares
for automated speckit workflow execution.

Usage:
    python3 setup.py --project-name myproject --spec "Build a CLI tool that..."
"""

import argparse
import os
import re
import shutil
import sys
from pathlib import Path


def slugify(name: str) -> str:
    """Convert project name to directory-friendly slug."""
    return re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')


def copy_template(template_dir: Path, target_dir: Path) -> None:
    """Copy template files excluding .setup and project directories."""
    for item in template_dir.iterdir():
        if item.name in ('.setup', 'project'):
            continue
        
        dest = target_dir / item.name
        if item.is_dir():
            shutil.copytree(item, dest, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        else:
            shutil.copy2(item, dest)


def generate_run_sh(setup_dir: Path, project_dir: Path, spec: str) -> None:
    """Generate run.sh from steps.yaml template."""
    steps_yaml = setup_dir / "steps.yaml"
    yaml_to_cli = setup_dir / "yaml-to-cli.py"
    run_dir = project_dir / ".run"
    run_sh = run_dir / "run.sh"
    
    # Create .run directory
    run_dir.mkdir(exist_ok=True)
    
    # Read steps.yaml and substitute spec
    with open(steps_yaml, 'r') as f:
        yaml_content = f.read()
    
    yaml_content = yaml_content.replace('{{SPEC}}', spec)
    
    # Write temporary yaml
    temp_yaml = run_dir / "steps-temp.yaml"
    with open(temp_yaml, 'w') as f:
        f.write(yaml_content)
    
    # Generate run.sh
    import subprocess
    result = subprocess.run(
        [sys.executable, str(yaml_to_cli), str(temp_yaml)],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"Error generating run.sh: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    
    with open(run_sh, 'w') as f:
        f.write(result.stdout)
    
    # Make executable
    run_sh.chmod(0o755)
    
    # Clean up temp yaml
    temp_yaml.unlink()
    
    print(f"Generated: {run_sh}")


def main():
    parser = argparse.ArgumentParser(
        description="Setup a new FullAutoTemplate project"
    )
    parser.add_argument(
        "--project-name",
        required=True,
        help="Name of the project (will be used for directory)"
    )
    parser.add_argument(
        "--spec",
        required=True,
        help="User specification for the feature (passed to /speckit.specify)"
    )
    args = parser.parse_args()
    
    # Determine paths
    setup_dir = Path(__file__).parent.resolve()
    template_dir = setup_dir.parent
    workspace_dir = template_dir.parent
    
    project_slug = slugify(args.project_name) 
    project_dir = workspace_dir / project_slug
    
    # Check if project already exists
    if project_dir.exists():
        print(f"Error: Project directory already exists: {project_dir}", file=sys.stderr)
        sys.exit(1)
    
    # Create project directory
    project_dir.mkdir(parents=True)
    print(f"Creating project: {project_dir}")
    
    # Copy template files
    copy_template(template_dir, project_dir)
    print(f"Copied template files")
    
    # Generate run.sh
    generate_run_sh(setup_dir, project_dir, args.spec)
    
    # Copy skeleton
    skeleton_src = template_dir
    skeleton_dst = project_dir / project_slug
    if skeleton_src.exists():
        shutil.copytree(skeleton_src, skeleton_dst)
        print(f"Copied skeleton to: {skeleton_dst}")
    
    print(f"\nProject '{args.project_name}' created successfully!")
    print(f"Next steps:")
    print(f"  cd {project_dir}")
    print(f"  bash .run/run.sh")


if __name__ == "__main__":
    main()
