"""Automated label-bound KubeArmor policy compiler (STORY-FING-04).

Translates a validated anomalous trajectory into a declarative
KubeArmorPolicy manifest bound to Kubernetes workload label selectors, so
the policy follows the workload across autoscaling and node eviction.
"""

from __future__ import annotations

from typing import Literal

import yaml

_VALID_ACTIONS = ("Block", "Post")


def compile_policy(
    workload_name: str,
    match_labels: dict[str, str],
    anomalous_trajectory: str,
    namespace: str = "default",
    action: Literal["Block", "Post"] = "Block",
) -> str:
    """Compile a KubeArmorPolicy CRD manifest as a YAML string.

    `action` is an explicit caller parameter (default "Block") rather than
    inferred from workload metadata — see docs/ARCH.md decision #3.
    """
    if action not in _VALID_ACTIONS:
        raise ValueError(f"action must be one of {_VALID_ACTIONS}, got {action!r}")
    if not match_labels:
        raise ValueError("match_labels must not be empty — an empty selector matches everything")

    policy = {
        "apiVersion": "security.kubearmor.com/v1",
        "kind": "KubeArmorPolicy",
        "metadata": {
            "name": f"fingerling-{workload_name}",
            "namespace": namespace,
            "annotations": {
                "fingerling.io/anomalous-trajectory": anomalous_trajectory,
            },
        },
        "spec": {
            "selector": {
                "matchLabels": dict(match_labels),
            },
            "process": {
                "matchPaths": [],
            },
            "action": action,
        },
    }
    return yaml.safe_dump(policy, sort_keys=False)
