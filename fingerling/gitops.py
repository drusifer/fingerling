"""Automated workload-bound GitOps delivery pipeline (STORY-FING-09..11)."""

from __future__ import annotations

import os
import subprocess


def _run_git(args: list[str], cwd: str) -> str:
    """Helper to run git commands safely via subprocess."""
    res = subprocess.run(["git"] + args, cwd=cwd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(
            f"Git command failed: git {' '.join(args)}\nStdout: {res.stdout}\nStderr: {res.stderr}"
        )
    return res.stdout


def initialize_repo(repo_path: str, default_branch: str = "main") -> None:
    """Scaffold and initialize a local Git repository workspace."""
    os.makedirs(repo_path, exist_ok=True)
    if not os.path.exists(os.path.join(repo_path, ".git")):
        _run_git(["init", "-b", default_branch], cwd=repo_path)

    # Check and set user.name locally if not configured globally
    try:
        _run_git(["config", "user.name"], cwd=repo_path)
    except RuntimeError:
        _run_git(["config", "user.name", "Fingerling Bot"], cwd=repo_path)

    # Check and set user.email locally if not configured globally
    try:
        _run_git(["config", "user.email"], cwd=repo_path)
    except RuntimeError:
        _run_git(["config", "user.email", "bot@fingerling.io"], cwd=repo_path)

    # Make initial commit
    readme_path = os.path.join(repo_path, "README.md")
    if not os.path.exists(readme_path):
        with open(readme_path, "w") as f:
            f.write("# Fingerling GitOps Workspace\n")
        _run_git(["add", "README.md"], cwd=repo_path)
        _run_git(["commit", "-m", "Initial commit"], cwd=repo_path)


def commit_policy(
    repo_path: str,
    policy_yaml: str,
    workload_name: str,
    branch_name: str,
    gpg_sign: bool = False,
    gpg_key_id: str | None = None,
) -> None:
    """Checkout a branch and commit the compiled policy manifest."""
    try:
        _run_git(["checkout", "-b", branch_name], cwd=repo_path)
    except RuntimeError:
        _run_git(["checkout", branch_name], cwd=repo_path)

    policies_dir = os.path.join(repo_path, "policies")
    os.makedirs(policies_dir, exist_ok=True)
    policy_file = os.path.join(policies_dir, f"fingerling-{workload_name}.yaml")
    with open(policy_file, "w") as f:
        f.write(policy_yaml)

    _run_git(["add", f"policies/fingerling-{workload_name}.yaml"], cwd=repo_path)

    if gpg_key_id:
        _run_git(["config", "user.signingkey", gpg_key_id], cwd=repo_path)

    commit_args = ["commit"]
    if gpg_sign:
        commit_args.append("-S")
    commit_args.extend(["-m", f"Add policy for {workload_name} workload"])

    _run_git(commit_args, cwd=repo_path)


def auto_merge_policy(
    repo_path: str, branch_name: str, target_branch: str = "main"
) -> None:
    """Merge the hotfix branch back to the target deployment branch."""
    # Check out target branch
    _run_git(["checkout", target_branch], cwd=repo_path)

    # Merge hotfix branch
    try:
        _run_git(
            ["merge", "--no-ff", branch_name, "-m", f"Auto-merge policy update branch {branch_name}"],
            cwd=repo_path,
        )
    except RuntimeError as e:
        raise RuntimeError(f"Merge conflict or failure on auto-merge: {e}")

    # Clean up the hotfix branch
    try:
        _run_git(["branch", "-d", branch_name], cwd=repo_path)
    except RuntimeError:
        _run_git(["branch", "-D", branch_name], cwd=repo_path)
