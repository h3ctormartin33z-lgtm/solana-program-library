"""
Tests for .mergify.yml configuration changes.

PR change summary:
  - Removed: queue_rules section (had name "88888")
  - Removed: scopes section (had source.files: {})
  - Added:   priority_rules: []
"""

import os
import unittest
import yaml


CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", ".mergify.yml")


def load_config():
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)


class TestMergifyConfigParseable(unittest.TestCase):
    """The config file must be valid YAML."""

    def test_file_exists(self):
        self.assertTrue(os.path.isfile(CONFIG_PATH), ".mergify.yml not found")

    def test_yaml_is_parseable(self):
        config = load_config()
        self.assertIsNotNone(config)

    def test_yaml_parses_to_dict(self):
        config = load_config()
        self.assertIsInstance(config, dict)


class TestPriorityRulesAdded(unittest.TestCase):
    """priority_rules key was introduced by this PR as an empty list."""

    def setUp(self):
        self.config = load_config()

    def test_priority_rules_key_exists(self):
        self.assertIn("priority_rules", self.config)

    def test_priority_rules_is_list(self):
        self.assertIsInstance(self.config["priority_rules"], list)

    def test_priority_rules_is_empty(self):
        self.assertEqual(self.config["priority_rules"], [])

    def test_priority_rules_is_not_none(self):
        self.assertIsNotNone(self.config["priority_rules"])

    def test_priority_rules_is_not_dict(self):
        self.assertNotIsInstance(self.config["priority_rules"], dict)


class TestQueueRulesRemoved(unittest.TestCase):
    """queue_rules section was removed by this PR."""

    def setUp(self):
        self.config = load_config()

    def test_queue_rules_key_absent(self):
        self.assertNotIn("queue_rules", self.config)

    def test_no_queue_named_88888(self):
        # Even if queue_rules were somehow present, the "88888" entry must not exist.
        queue_rules = self.config.get("queue_rules", []) or []
        names = [r.get("name") for r in queue_rules if isinstance(r, dict)]
        self.assertNotIn("88888", names)


class TestScopesRemoved(unittest.TestCase):
    """scopes section was removed by this PR."""

    def setUp(self):
        self.config = load_config()

    def test_scopes_key_absent(self):
        self.assertNotIn("scopes", self.config)


class TestPullRequestRulesIntact(unittest.TestCase):
    """pull_request_rules section must remain intact after the PR changes."""

    def setUp(self):
        self.config = load_config()
        self.rules = self.config.get("pull_request_rules", [])

    def test_pull_request_rules_key_exists(self):
        self.assertIn("pull_request_rules", self.config)

    def test_pull_request_rules_is_list(self):
        self.assertIsInstance(self.rules, list)

    def test_pull_request_rules_not_empty(self):
        self.assertTrue(len(self.rules) > 0)

    def test_all_rules_have_name(self):
        for rule in self.rules:
            self.assertIn("name", rule, f"Rule missing 'name': {rule}")

    def test_all_rules_have_conditions(self):
        for rule in self.rules:
            self.assertIn("conditions", rule, f"Rule missing 'conditions': {rule}")

    def test_all_rules_have_actions(self):
        for rule in self.rules:
            self.assertIn("actions", rule, f"Rule missing 'actions': {rule}")

    def test_community_label_rule_present(self):
        names = [r["name"] for r in self.rules]
        self.assertIn("label changes from community", names)

    def test_automerge_squash_rule_present(self):
        names = [r["name"] for r in self.rules]
        self.assertIn("automatic merge (squash) on CI success", names)

    def test_automerge_rebase_rule_present(self):
        names = [r["name"] for r in self.rules]
        self.assertIn("automatic merge (rebase) on CI success", names)

    def test_remove_automerge_label_rule_present(self):
        names = [r["name"] for r in self.rules]
        self.assertIn("remove automerge label on CI failure", names)

    def test_remove_outdated_reviews_rule_present(self):
        names = [r["name"] for r in self.rules]
        self.assertIn("remove outdated reviews", names)


class TestTopLevelKeysOnly(unittest.TestCase):
    """The config should only contain expected top-level keys."""

    ALLOWED_KEYS = {"pull_request_rules", "priority_rules"}

    def setUp(self):
        self.config = load_config()

    def test_no_unexpected_top_level_keys(self):
        unexpected = set(self.config.keys()) - self.ALLOWED_KEYS
        self.assertEqual(
            unexpected,
            set(),
            f"Unexpected top-level keys present: {unexpected}",
        )

    def test_expected_keys_all_present(self):
        for key in self.ALLOWED_KEYS:
            self.assertIn(key, self.config, f"Expected key '{key}' not found")

    def test_exactly_two_top_level_keys(self):
        self.assertEqual(len(self.config), 2)


if __name__ == "__main__":
    unittest.main()
