"""Tests for STORY-FING-09..11: Automated GitOps Delivery Pipeline."""

from __future__ import annotations

import os
import tempfile
import unittest

from fingerling.gitops import initialize_repo, _run_git


class GitOpsScaffoldingTests(unittest.TestCase):
    def test_initialize_repo_creates_git_workspace(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_path = os.path.join(tmp, "gitops-repo")
            initialize_repo(repo_path, default_branch="main")

            self.assertTrue(os.path.exists(os.path.join(repo_path, ".git")))
            self.assertTrue(os.path.exists(os.path.join(repo_path, "README.md")))

            # Verify commit is made
            log = _run_git(["log", "--oneline"], cwd=repo_path)
            self.assertIn("Initial commit", log)
            
            # Verify user name/email are set locally
            name = _run_git(["config", "user.name"], cwd=repo_path).strip()
            email = _run_git(["config", "user.email"], cwd=repo_path).strip()
            self.assertTrue(len(name) > 0)
            self.assertTrue(len(email) > 0)

    def test_commit_policy_creates_branch_and_policy_file(self) -> None:
        from fingerling.gitops import commit_policy

        with tempfile.TemporaryDirectory() as tmp:
            repo_path = os.path.join(tmp, "gitops-repo")
            initialize_repo(repo_path, default_branch="main")

            policy_content = "apiVersion: security.kubearmor.com/v1\nkind: KubeArmorPolicy"
            commit_policy(
                repo_path=repo_path,
                policy_yaml=policy_content,
                workload_name="nginx-service",
                branch_name="fingerling-hotfix-nginx",
                gpg_sign=False,
            )

            # Verify branch is checked out
            branch = _run_git(["branch", "--show-current"], cwd=repo_path).strip()
            self.assertEqual(branch, "fingerling-hotfix-nginx")

            # Verify file exists and has correct content
            policy_file_path = os.path.join(repo_path, "policies", "fingerling-nginx-service.yaml")
            self.assertTrue(os.path.exists(policy_file_path))
            with open(policy_file_path) as f:
                content = f.read()
            self.assertEqual(content, policy_content)

            # Verify commit is in git log
            log = _run_git(["log", "-n", "1", "--oneline"], cwd=repo_path)
            self.assertIn("Add policy for nginx-service workload", log)

    def test_commit_policy_gpg_sign_fails_gracefully_when_key_invalid(self) -> None:
        from fingerling.gitops import commit_policy

        with tempfile.TemporaryDirectory() as tmp:
            repo_path = os.path.join(tmp, "gitops-repo")
            initialize_repo(repo_path, default_branch="main")

            policy_content = "apiVersion: security.kubearmor.com/v1\nkind: KubeArmorPolicy"
            with self.assertRaises(RuntimeError):
                commit_policy(
                    repo_path=repo_path,
                    policy_yaml=policy_content,
                    workload_name="nginx-service",
                    branch_name="fingerling-hotfix-nginx",
                    gpg_sign=True,
                    gpg_key_id="invalid-gpg-key-id-12345",
                )

    def test_auto_merge_policy_success_and_cleanup(self) -> None:
        from fingerling.gitops import commit_policy, auto_merge_policy

        with tempfile.TemporaryDirectory() as tmp:
            repo_path = os.path.join(tmp, "gitops-repo")
            initialize_repo(repo_path, default_branch="main")

            policy_content = "apiVersion: security.kubearmor.com/v1\nkind: KubeArmorPolicy"
            branch_name = "fingerling-hotfix-nginx"
            commit_policy(
                repo_path=repo_path,
                policy_yaml=policy_content,
                workload_name="nginx-service",
                branch_name=branch_name,
                gpg_sign=False,
            )

            # Switch back to main via auto-merge
            auto_merge_policy(repo_path, branch_name, target_branch="main")

            # Verify current branch is main
            branch = _run_git(["branch", "--show-current"], cwd=repo_path).strip()
            self.assertEqual(branch, "main")

            # Verify file exists on main branch
            policy_file_path = os.path.join(repo_path, "policies", "fingerling-nginx-service.yaml")
            self.assertTrue(os.path.exists(policy_file_path))

            # Verify branch is deleted
            branches = _run_git(["branch"], cwd=repo_path)
            self.assertNotIn(branch_name, branches)

    def test_auto_merge_policy_raises_on_invalid_branch(self) -> None:
        from fingerling.gitops import auto_merge_policy

        with tempfile.TemporaryDirectory() as tmp:
            repo_path = os.path.join(tmp, "gitops-repo")
            initialize_repo(repo_path, default_branch="main")

            with self.assertRaises(RuntimeError):
                auto_merge_policy(repo_path, "non-existent-branch", target_branch="main")


if __name__ == "__main__":
    unittest.main()
