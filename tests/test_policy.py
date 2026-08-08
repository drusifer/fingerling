"""Tests for STORY-FING-04: automated label-bound KubeArmor policy compiler."""

import unittest

import yaml

from fingerling.policy import compile_policy


class CompilePolicyTests(unittest.TestCase):
    def test_output_is_valid_yaml_matching_kubearmor_schema_shape(self):
        # Verification Task: generated YAML matches standard KubeArmor schema without
        # formatting errors.
        manifest_text = compile_policy(
            workload_name="checkout-backend",
            match_labels={"app": "checkout-backend"},
            anomalous_trajectory="fp_a,fp_b,fp_c",
        )

        manifest = yaml.safe_load(manifest_text)

        self.assertEqual(manifest["apiVersion"], "security.kubearmor.com/v1")
        self.assertEqual(manifest["kind"], "KubeArmorPolicy")
        self.assertIn("metadata", manifest)
        self.assertIn("spec", manifest)
        self.assertIn("selector", manifest["spec"])
        self.assertIn("action", manifest["spec"])

    def test_maps_match_labels_to_target_workload(self):
        # Verification Task: matchLabels correctly maps to target workload id
        # (app: checkout-backend).
        manifest_text = compile_policy(
            workload_name="checkout-backend",
            match_labels={"app": "checkout-backend"},
            anomalous_trajectory="fp_a,fp_b,fp_c",
        )

        manifest = yaml.safe_load(manifest_text)

        self.assertEqual(
            manifest["spec"]["selector"]["matchLabels"], {"app": "checkout-backend"}
        )

    def test_action_defaults_to_block(self):
        manifest_text = compile_policy(
            workload_name="w", match_labels={"app": "w"}, anomalous_trajectory="fp_x"
        )
        manifest = yaml.safe_load(manifest_text)
        self.assertEqual(manifest["spec"]["action"], "Block")

    def test_action_can_be_explicitly_set_to_post(self):
        manifest_text = compile_policy(
            workload_name="w",
            match_labels={"app": "w"},
            anomalous_trajectory="fp_x",
            action="Post",
        )
        manifest = yaml.safe_load(manifest_text)
        self.assertEqual(manifest["spec"]["action"], "Post")

    def test_invalid_action_raises(self):
        with self.assertRaises(ValueError):
            compile_policy(
                workload_name="w",
                match_labels={"app": "w"},
                anomalous_trajectory="fp_x",
                action="Allow",
            )

    def test_empty_match_labels_rejected(self):
        with self.assertRaises(ValueError):
            compile_policy(workload_name="w", match_labels={}, anomalous_trajectory="fp_x")

    def test_namespace_defaults_and_is_overridable(self):
        default_manifest = yaml.safe_load(
            compile_policy(workload_name="w", match_labels={"app": "w"}, anomalous_trajectory="x")
        )
        self.assertEqual(default_manifest["metadata"]["namespace"], "default")

        custom_manifest = yaml.safe_load(
            compile_policy(
                workload_name="w",
                match_labels={"app": "w"},
                anomalous_trajectory="x",
                namespace="checkout",
            )
        )
        self.assertEqual(custom_manifest["metadata"]["namespace"], "checkout")

    def test_block_pattern_omitted_by_default(self):
        # STORY-FING-22: matchPattern absent unless block_pattern is explicitly passed —
        # existing callers/tests must see no schema change.
        manifest = yaml.safe_load(
            compile_policy(workload_name="w", match_labels={"app": "w"}, anomalous_trajectory="x")
        )
        self.assertNotIn("matchPattern", manifest["spec"]["process"])

    def test_block_pattern_adds_match_pattern_field(self):
        # STORY-FING-22: comprehensive ';'-content block, additive to matchPaths.
        manifest = yaml.safe_load(
            compile_policy(
                workload_name="w",
                match_labels={"app": "w"},
                anomalous_trajectory="x",
                block_pattern=";",
            )
        )
        self.assertEqual(manifest["spec"]["process"]["matchPattern"], ";")
        self.assertEqual(manifest["spec"]["process"]["matchPaths"], [])

    def test_accepts_tuple_trajectory(self):
        # Verification Task: anomalous_trajectory accepts tuple and joins with commas
        manifest_text = compile_policy(
            workload_name="w",
            match_labels={"app": "w"},
            anomalous_trajectory=("fp_a", "fp_b"),
        )
        manifest = yaml.safe_load(manifest_text)
        self.assertEqual(
            manifest["metadata"]["annotations"]["fingerling.io/anomalous-trajectory"],
            "fp_a,fp_b",
        )


if __name__ == "__main__":
    unittest.main()

