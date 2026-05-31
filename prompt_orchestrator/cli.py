#!/usr/bin/env python3
"""prompt-orchestrator CLI — Multi-step LLM workflow executor.

Usage:
    prompt-orchestrator init          Scaffold workflow files into existing project
    prompt-orchestrator run [--step N] [extra...]  Execute workflow
    prompt-orchestrator new --name NAME --spec PATH  Create new project from skeleton
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path


# ── Package paths ──────────────────────────────────────────────────────────

def _package_dir() -> Path:
    """Return the directory containing this package's scaffold files."""
    return Path(__file__).resolve().parent


def _scaffold_dir() -> Path:
    return _package_dir() / "scaffold"


def _skeleton_dir() -> Path:
    return _package_dir() / "project_skeleton"


# ── Helpers ────────────────────────────────────────────────────────────────

def slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def copy_tree(src: Path, dest: Path, ignore_patterns=None):
    """Copy directory tree, skip __pycache__ and .pyc."""
    ignores = ignore_patterns or ["__pycache__", "*.pyc"]
    shutil.copytree(src, dest, ignore=shutil.ignore_patterns(*ignores), dirs_exist_ok=True)


# ── Subcommand: init ───────────────────────────────────────────────────────

def cmd_init(args):
    """Scaffold orchestrator workflow files into an existing project."""
    project_dir = Path.cwd().resolve()

    # Always scaffold .env.example (standalone file, independent of workflow)
    env_example_src = _scaffold_dir() / ".env.example"
    if env_example_src.exists():
        env_example_dst = project_dir / ".env.example"
        if not env_example_dst.exists() or args.force:
            shutil.copy2(env_example_src, env_example_dst)
            print(f"  Created: .env.example")

    # Check not already initialized
    if (project_dir / ".orchestrator").exists():
        print("Already initialized: .orchestrator/ exists")
        if not args.force:
            sys.exit(1)

    # Create .orchestrator/ from scaffold
    orchestrator_dir = project_dir / ".orchestrator"
    for sub in ["command", "templates", "memory"]:
        src = _scaffold_dir() / sub
        dst = orchestrator_dir / sub
        copy_tree(src, dst)
        print(f"  Created: {dst.relative_to(project_dir)}/")

    # Create steps.yaml in ._agents_not_allowed/ only
    hidden_dir = project_dir / "._agents_not_allowed"
    hidden_dir.mkdir(exist_ok=True)

    steps_src = _package_dir().parent / "template" / "steps.yaml"
    if not steps_src.exists():
        steps_src = _scaffold_dir().parent.parent / "template" / "steps.yaml"
    steps_dst = hidden_dir / "steps.yaml"
    if not steps_dst.exists() or args.force:
        project_name = project_dir.name
        content = steps_src.read_text().replace("{project_name}", project_name)
        steps_dst.write_text(content)
        print(f"  Created: ._agents_not_allowed/steps.yaml")

    # Copy runner
    runner_src = _package_dir() / "runner.py"
    shutil.copy2(runner_src, hidden_dir / "run_steps.py")
    print(f"  Created: ._agents_not_allowed/run_steps.py")

    # Git init if not already a repo
    if not (project_dir / ".git").exists():
        subprocess.run(["git", "init"], cwd=project_dir, capture_output=True)
        print(f"  Initialized git repo")

    # Ensure .gitignore has *.log
    gitignore = project_dir / ".gitignore"
    existing = gitignore.read_text().splitlines() if gitignore.exists() else []
    if "*.log" not in existing:
        gitignore.write_text("\n".join(existing + ["", "*.log"]) if existing else "*.log\n")
        print(f"  Added *.log to .gitignore")

    # Commit initial state
    subprocess.run(["git", "add", "-A"], cwd=project_dir, capture_output=True)
    result = subprocess.run(
        ["git", "status", "--porcelain"], cwd=project_dir, capture_output=True, text=True
    )
    if result.stdout.strip():
        subprocess.run(
            ["git", "commit", "-m", "initial commit: scaffold orchestrator workflow"],
            cwd=project_dir, capture_output=True
        )
        print(f"  Committed initial state")

    print(f"\nInitialized orchestrator in {project_dir}")
    print(f"  Run: prompt-orchestrator run")


# ── Subcommand: run ────────────────────────────────────────────────────────

def cmd_run(args):
    """Execute orchestrator workflow."""
    project_dir = Path.cwd().resolve()

    # Find steps.yaml — prefer ._agents_not_allowed/, then project root
    yaml_path = project_dir / "._agents_not_allowed" / "steps.yaml"
    if not yaml_path.exists():
        yaml_path = project_dir / "steps.yaml"
    if not yaml_path.exists():
        print("ERROR: steps.yaml not found. Run 'prompt-orchestrator init' first.", file=sys.stderr)
        sys.exit(1)

    # Require .env in project root (check before announcing run)
    dotenv = project_dir / ".env"
    if not dotenv.exists():
        example = project_dir / ".env.example"
        if example.exists():
            print(f"ERROR: copy {example} to {dotenv} and configure with needed API keys.", file=sys.stderr)
        else:
            print(f"ERROR: create {dotenv} with your API keys.", file=sys.stderr)
        sys.exit(1)

    print(f"  Running [{yaml_path}]")


    # Import and run
    sys.path.insert(0, str(_package_dir()))
    from prompt_orchestrator.runner import main as runner_main

    # Build args for runner
    runner_args = ["--config", str(yaml_path)]
    if args.step:
        runner_args.extend(["--step", str(args.step)])
    runner_args.extend(args.extra)

    sys.argv = ["run_steps.py"] + runner_args
    runner_main()


# ── Subcommand: new ────────────────────────────────────────────────────────

def cmd_new(args):
    """Create a new project from skeleton with orchestrator scaffold."""
    project_name = args.name
    spec_path = Path(args.spec)
    target = Path(args.target_dir or Path.cwd()).resolve()

    if not spec_path.exists():
        print(f"ERROR: Spec file not found: {spec_path}", file=sys.stderr)
        sys.exit(1)

    project_slug = slugify(project_name)
    project_dir = target / project_slug

    if project_dir.exists():
        print(f"ERROR: Directory already exists: {project_dir}", file=sys.stderr)
        sys.exit(1)

    project_dir.mkdir(parents=True)

    # Copy skeleton
    copy_tree(_skeleton_dir(), project_dir)

    # Replace placeholders in skeleton files
    for pattern in ["*.py", "*.toml", "*.md", "*.txt", "*.cfg", "*.ini"]:
        for f in project_dir.rglob(pattern):
            if f.is_file():
                content = f.read_text()
                content = content.replace("{{project_name}}", project_slug)
                content = content.replace("{{project_description}}", f"{project_name} project")
                content = content.replace("{{author_name}}", os.environ.get("USER", "developer"))
                content = content.replace("{{author_email}}", f"{os.environ.get('USER', 'dev')}@example.com")
                f.write_text(content)

    # Initialize orchestrator in the new project
    os.chdir(str(project_dir))
    class FakeArgs:
        force = False
    cmd_init(FakeArgs())

    # Copy user spec
    shutil.copy2(spec_path, project_dir / "userspec.md")
    print(f"  Created: userspec.md")

    print(f"\nProject '{project_name}' created: {project_dir}")
    print(f"  cd {project_dir}")
    print(f"  prompt-orchestrator run")


# ── Main CLI ───────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Multi-step LLM workflow executor with review gates",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--version", action="version", version="prompt-orchestrator 0.2.0")

    sub = parser.add_subparsers(dest="command", required=True)

    # init
    init_p = sub.add_parser("init", help="Scaffold workflow files into existing project")
    init_p.add_argument("--force", "-f", action="store_true", help="Overwrite existing files")

    # run
    run_p = sub.add_parser("run", help="Execute orchestrator workflow")
    run_p.add_argument("--step", "-s", type=int, default=None, metavar="N", help="Start at step N")
    run_p.add_argument("extra", nargs="*", help="Additional context for step N")

    # new
    new_p = sub.add_parser("new", help="Create new project from skeleton")
    new_p.add_argument("--name", required=True, help="Project name")
    new_p.add_argument("--spec", required=True, help="Path to specification file")
    new_p.add_argument("--target-dir", help="Target directory (default: current dir)")

    args = parser.parse_args()

    if args.command == "init":
        cmd_init(args)
    elif args.command == "run":
        cmd_run(args)
    elif args.command == "new":
        cmd_new(args)


if __name__ == "__main__":
    main()
