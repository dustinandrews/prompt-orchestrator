#!/usr/bin/env python3
"""Orchestrator workflow utility script.

Usage:
    python .setup/run_steps.py create-feature <description> [--short-name NAME] [--number N] [--json]
    python .setup/run_steps.py setup-plan [--json]
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path


# ── Helpers ─────────────────────────────────────────────────────────────────


def get_repo_root(start: Path | None = None) -> Path:
    start = start or Path.cwd()
    try:
        root = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, check=True, cwd=start
        ).stdout.strip()
        return Path(root).resolve()
    except subprocess.CalledProcessError:
        pass
    # Walk upward looking for markers
    for parent in [start, *start.parents]:
        if (parent / ".git").is_dir() or (parent / ".orchestrator").is_dir():
            return parent.resolve()
    print("Error: Could not determine repository root.", file=sys.stderr)
    sys.exit(1)


def has_git(cwd: Path | None = None) -> bool:
    try:
        subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, check=True, cwd=cwd or Path.cwd()
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def get_current_branch(repo_root: Path) -> str:
    feature = os.environ.get("ORCHESTRATOR_FEATURE")
    if feature:
        return feature
    if has_git(repo_root):
        try:
            return subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                capture_output=True, text=True, check=True, cwd=repo_root
            ).stdout.strip()
        except subprocess.CalledProcessError:
            pass
    specs_dir = repo_root / "specs"
    if specs_dir.is_dir():
        highest, latest = 0, ""
        for d in specs_dir.iterdir():
            if d.is_dir():
                m = re.match(r"^(\d{3})-", d.name)
                if m:
                    n = int(m.group(1))
                    if n > highest:
                        highest, latest = n, d.name
        if latest:
            return latest
    return "main"


def check_feature_branch(branch: str, git_available: bool) -> None:
    if not git_available:
        print("[orchestrator] Warning: Git not detected; skipped branch validation", file=sys.stderr)
        return
    if not re.match(r"^\d{3}-", branch):
        print(f"ERROR: Not on a feature branch. Current branch: {branch}", file=sys.stderr)
        print("Feature branches should be named like: 001-feature-name", file=sys.stderr)
        sys.exit(1)


def find_feature_dir_by_prefix(repo_root: Path, branch: str) -> Path:
    specs_dir = repo_root / "specs"
    m = re.match(r"^(\d{3})-", branch)
    if not m:
        return specs_dir / branch
    prefix = m.group(1)
    matches = sorted(d.name for d in specs_dir.glob(f"{prefix}-*") if d.is_dir())
    if not matches:
        return specs_dir / branch
    if len(matches) == 1:
        return specs_dir / matches[0]
    print(f"ERROR: Multiple spec directories found with prefix '{prefix}': {matches}", file=sys.stderr)
    print("Please ensure only one spec directory exists per numeric prefix.", file=sys.stderr)
    sys.exit(1)


def get_feature_paths(repo_root: Path) -> dict:
    branch = get_current_branch(repo_root)
    git_avail = has_git(repo_root)
    feature_dir = find_feature_dir_by_prefix(repo_root, branch)
    return {
        "REPO_ROOT": str(repo_root),
        "CURRENT_BRANCH": branch,
        "HAS_GIT": "true" if git_avail else "false",
        "FEATURE_DIR": str(feature_dir),
        "FEATURE_SPEC": str(feature_dir / "spec.md"),
        "IMPL_PLAN": str(feature_dir / "plan.md"),
        "TASKS": str(feature_dir / "tasks.md"),
        "RESEARCH": str(feature_dir / "research.md"),
        "DATA_MODEL": str(feature_dir / "data-model.md"),
        "QUICKSTART": str(feature_dir / "quickstart.md"),
        "CONTRACTS_DIR": str(feature_dir / "contracts"),
    }


def resolve_template(template_name: str, repo_root: Path) -> Path | None:
    base = repo_root / ".orchestrator" / "templates"
    candidates = [base / "overrides" / f"{template_name}.md", base / f"{template_name}.md"]
    if (base / "presets").is_dir():
        candidates.extend(sorted((base / "presets").glob(f"*/templates/{template_name}.md")))
    if (base / "extensions").is_dir():
        candidates.extend(sorted((base / "extensions").glob(f"*/templates/{template_name}.md")))
    for c in candidates:
        if c.is_file():
            return c
    return None


def clean_branch_name(name: str) -> str:
    name = name.lower()
    name = re.sub(r"[^a-z0-9]", "-", name)
    name = re.sub(r"-+", "-", name)
    return name.strip("-")


STOP_WORDS = {
    "i", "a", "an", "the", "to", "for", "of", "in", "on", "at", "by", "with",
    "from", "is", "are", "was", "were", "be", "been", "being", "have", "has",
    "had", "do", "does", "did", "will", "would", "should", "could", "can",
    "may", "might", "must", "shall", "this", "that", "these", "those", "my",
    "your", "our", "their", "want", "need", "add", "get", "set",
}


def generate_branch_name(description: str) -> str:
    lower = description.lower()
    words = re.sub(r"[^a-z0-9]", " ", lower).split()
    meaningful = []
    original_upper = {w.upper() for w in description.split()}
    for w in words:
        if not w:
            continue
        if w not in STOP_WORDS:
            if len(w) >= 3 or w.upper() in original_upper:
                meaningful.append(w)
    if meaningful:
        count = 4 if len(meaningful) == 4 else 3
        return "-".join(meaningful[:count])
    cleaned = clean_branch_name(description)
    parts = [p for p in cleaned.split("-") if p]
    return "-".join(parts[:3])


def get_highest_from_specs(specs_dir: Path) -> int:
    highest = 0
    if specs_dir.is_dir():
        for d in specs_dir.iterdir():
            if d.is_dir():
                m = re.match(r"^(\d{3})-", d.name)
                if m:
                    highest = max(highest, int(m.group(1)))
    return highest


def get_highest_from_branches(repo_root: Path) -> int:
    highest = 0
    result = subprocess.run(
        ["git", "branch", "-a"], capture_output=True, text=True, cwd=repo_root
    ).stdout
    for line in result.splitlines():
        clean = re.sub(r"^[* ]*", "", line)
        clean = re.sub(r"^remotes/[^/]*/", "", clean)
        m = re.match(r"^(\d{3})-", clean)
        if m:
            highest = max(highest, int(m.group(1)))
    return highest


# ── Subcommands ──────────────────────────────────────────────────────────────


def cmd_create_feature(args: argparse.Namespace) -> None:
    repo_root = get_repo_root()
    specs_dir = repo_root / "specs"
    specs_dir.mkdir(parents=True, exist_ok=True)

    description = args.description.strip()
    if not description:
        print("Error: Feature description cannot be empty or contain only whitespace", file=sys.stderr)
        sys.exit(1)

    if args.short_name:
        branch_suffix = clean_branch_name(args.short_name)
    else:
        branch_suffix = generate_branch_name(description)

    if args.number is not None:
        branch_number = args.number
    elif has_git(repo_root):
        subprocess.run(
            ["git", "fetch", "--all", "--prune"],
            capture_output=True, cwd=repo_root
        )
        high_branch = get_highest_from_branches(repo_root)
        high_specs = get_highest_from_specs(specs_dir)
        branch_number = max(high_branch, high_specs) + 1
    else:
        branch_number = get_highest_from_specs(specs_dir) + 1

    feature_num = f"{branch_number:03d}"
    branch_name = f"{feature_num}-{branch_suffix}"

    # GitHub branch length limit: 244 bytes
    if len(branch_name.encode("utf-8")) > 244:
        max_suffix = 239  # 244 - len(f"{feature_num}-")
        truncated = branch_suffix[:max_suffix].rstrip("-")
        print(f"[orchestrator] Warning: Branch name exceeded GitHub's 244-byte limit", file=sys.stderr)
        print(f"[orchestrator] Original: {branch_name} ({len(branch_name.encode('utf-8'))} bytes)", file=sys.stderr)
        branch_suffix = truncated
        branch_name = f"{feature_num}-{branch_suffix}"
        print(f"[orchestrator] Truncated to: {branch_name} ({len(branch_name.encode('utf-8'))} bytes)", file=sys.stderr)

    git_avail = has_git(repo_root)
    if git_avail:
        result = subprocess.run(
            ["git", "checkout", "-b", branch_name],
            capture_output=True, text=True, cwd=repo_root
        )
        if result.returncode != 0:
            existing = subprocess.run(
                ["git", "branch", "--list", branch_name],
                capture_output=True, text=True, cwd=repo_root
            ).stdout.strip()
            if existing:
                print(f"Error: Branch '{branch_name}' already exists. Use --number to specify a different number.", file=sys.stderr)
            else:
                print(f"Error: Failed to create git branch '{branch_name}'.", file=sys.stderr)
            sys.exit(1)
    else:
        print(f"[orchestrator] Warning: Git not detected; skipped branch creation for {branch_name}", file=sys.stderr)

    feature_dir = specs_dir / branch_name
    feature_dir.mkdir(parents=True, exist_ok=True)

    spec_file = feature_dir / "spec.md"
    template = resolve_template("spec-template", repo_root)
    if template and template.is_file():
        shutil.copy2(template, spec_file)
    else:
        print("Warning: Spec template not found; created empty spec file", file=sys.stderr)
        spec_file.touch()

    print(f"# To persist: export ORCHESTRATOR_FEATURE={branch_name}", file=sys.stderr)

    if args.json:
        print(json.dumps({
            "BRANCH_NAME": branch_name,
            "SPEC_FILE": str(spec_file),
            "FEATURE_NUM": feature_num,
        }))
    else:
        print(f"BRANCH_NAME: {branch_name}")
        print(f"SPEC_FILE: {spec_file}")
        print(f"FEATURE_NUM: {feature_num}")
        print(f"# To persist in your shell: export ORCHESTRATOR_FEATURE={branch_name}")


def cmd_setup_plan(args: argparse.Namespace) -> None:
    repo_root = get_repo_root()
    paths = get_feature_paths(repo_root)
    branch = paths["CURRENT_BRANCH"]
    git_avail = paths["HAS_GIT"] == "true"

    check_feature_branch(branch, git_avail)

    feature_dir = Path(paths["FEATURE_DIR"])
    feature_dir.mkdir(parents=True, exist_ok=True)

    impl_plan = Path(paths["IMPL_PLAN"])
    template = resolve_template("plan-template", repo_root)
    if template and template.is_file():
        shutil.copy2(template, impl_plan)
        print(f"Copied plan template to {impl_plan}")
    else:
        print("Warning: Plan template not found", file=sys.stderr)
        impl_plan.touch()

    if args.json:
        print(json.dumps({
            "FEATURE_SPEC": paths["FEATURE_SPEC"],
            "IMPL_PLAN": paths["IMPL_PLAN"],
            "SPECS_DIR": str(feature_dir),
            "BRANCH": branch,
            "HAS_GIT": paths["HAS_GIT"],
        }))
    else:
        print(f"FEATURE_SPEC: {paths['FEATURE_SPEC']}")
        print(f"IMPL_PLAN: {paths['IMPL_PLAN']}")
        print(f"SPECS_DIR: {feature_dir}")
        print(f"BRANCH: {branch}")
        print(f"HAS_GIT: {paths['HAS_GIT']}")


# ── CLI ─────────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(description="Orchestrator workflow utility")
    sub = parser.add_subparsers(dest="command", required=True)

    # create-feature
    cf = sub.add_parser("create-feature", help="Create a new feature branch and spec")
    cf.add_argument("description", help="Feature description")
    cf.add_argument("--short-name", help="Custom short name for the branch")
    cf.add_argument("--number", type=int, help="Branch number (auto-detected if omitted)")
    cf.add_argument("--json", action="store_true", help="Output in JSON format")
    cf.set_defaults(func=cmd_create_feature)

    # setup-plan
    sp = sub.add_parser("setup-plan", help="Set up plan directory for current feature")
    sp.add_argument("--json", action="store_true", help="Output in JSON format")
    sp.set_defaults(func=cmd_setup_plan)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
