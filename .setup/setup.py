#!/usr/bin/env python3
"""
Setup script for speckit-orchestrator projects.

Creates a new project from the template and prepares skeleton.

Usage:
    python3 .setup/setup.py --project-name myproject --spec-path ./my-spec.md
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path


def slugify(name: str) -> str:
    """Convert project name to directory-friendly slug."""
    return re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')


def get_template_dir() -> Path:
    """Get template directory."""
    return Path(__file__).parent.resolve().parent / "template"

def get_setup_dir() -> Path:
    """Get .setup directory."""
    return Path(__file__).parent.resolve()

def copy_template_files(template_dir: Path, target_dir: Path) -> None:
    """Copy template files to new project."""
    for item in template_dir.iterdir():
        if item.name in ('__pycache__', '.git'):
            continue
        
        dest = target_dir / item.name
        if item.is_dir():
            shutil.copytree(item, dest, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        else:
            shutil.copy2(item, dest)


def copy_spec_file(project_dir: Path, spec_path: str) -> None:
    """Copy user spec file into project as userspec.md."""
    src = Path(spec_path)
    if not src.exists():
        print(f"Error: Spec file not found: {spec_path}", file=sys.stderr)
        sys.exit(1)
    
    dest = project_dir / "userspec.md"
    shutil.copy2(src, dest)
    print(f"Copied spec: {dest}")


def main():
    parser = argparse.ArgumentParser(
        description="Setup a new speckit-orchestrator project"
    )
    parser.add_argument(
        "--project-name",
        required=True,
        help="Name of the project (will be used for directory)"
    )
    parser.add_argument(
        "--spec-path",
        required=True,
        help="Path to user specification markdown file"
    )
    args = parser.parse_args()
    
    setup_dir = get_setup_dir()
    template_dir = get_template_dir()
    workspace_dir = setup_dir.parent.parent
    
    project_slug = slugify(args.project_name)
    project_dir = workspace_dir / project_slug
    
    if project_dir.exists():
        print(f"Error: Project directory already exists: {project_dir}", file=sys.stderr)
        sys.exit(1)
    
    project_dir.mkdir(parents=True)
    print(f"Creating project: {project_dir}")
    
    copy_template_files(template_dir, project_dir)
    print(f"Copied template files")
    
    copy_spec_file(project_dir, args.spec_path)
    
    # Initialize git repo for new project
    subprocess.run(["git", "init"], cwd=project_dir, capture_output=True)
    print(f"Initialized git repo: {project_dir}")
    
    setup_dir_str = str(setup_dir)
    print(f"\nProject '{args.project_name}' created successfully!")
    print(f"Next steps:")
    print(f"  cd {project_dir}")
    print(f"  python3 {setup_dir_str}/run_steps.py")


if __name__ == "__main__":
    main()
