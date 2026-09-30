from copy import deepcopy
import json
from pathlib import Path
import unittest
from releaselens import Application, gate, impact, rollback_drill, run_suite

DATA = json.loads((Path(__file__).parents[1] / "data/release.json").read_text())


class ReleaseTests(unittest.TestCase):
    def setUp(self):
        self.config = deepcopy(DATA["versions"]["corrected"])
        self.cases = deepcopy(DATA["cases"])
        self.requirements = deepcopy(DATA["requirements"])
        self.evidence = run_suite(self.config, self.cases)
        self.rollback = rollback_drill(DATA["versions"]["baseline"], self.config)

    def assess(self):
        return gate(self.config, self.cases, self.requirements, self.evidence, self.rollback)["decision"]

    def test_corrected_ready_but_not_authorized(self):
        self.assertEqual(self.assess(), "READY_FOR_REVIEW")

    def test_bad_release_detects_three_distinct_failures(self):
        candidate = DATA["versions"]["candidate"]
        evidence = run_suite(candidate, self.cases)
        self.assertEqual([r["case_id"] for r in evidence["results"] if not r["passed"]], ["U02", "U05", "U06"])
        self.assertEqual(gate(candidate, self.cases, self.requirements, evidence, self.rollback)["decision"], "HOLD")

    def test_stale_configuration_evidence_blocked(self):
        self.config["audit_enabled"] = False
        self.assertEqual(self.assess(), "HOLD")

    def test_changed_test_suite_requires_rerun(self):
        self.cases[0]["input"]["budget"] = 200
        self.assertEqual(self.assess(), "HOLD")

    def test_missing_result_blocked(self):
        self.evidence["results"].pop()
        self.assertEqual(self.assess(), "HOLD")

    def test_duplicate_result_blocked(self):
        self.evidence["results"].append(self.evidence["results"][0])
        self.assertEqual(self.assess(), "HOLD")

    def test_uncovered_requirement_blocked(self):
        self.requirements.append({"id": "R99"})
        self.assertEqual(self.assess(), "HOLD")

    def test_wrong_traceability_blocked(self):
        self.evidence["results"][0]["requirement"] = "R99"
        self.assertEqual(self.assess(), "HOLD")

    def test_missing_and_failed_rollback_blocked(self):
        self.rollback = {}
        self.assertEqual(self.assess(), "HOLD")
        self.rollback = rollback_drill(self.config, DATA["versions"]["candidate"])
        self.rollback["records_preserved"] = False
        self.assertEqual(self.assess(), "HOLD")

    def test_empty_suite_cannot_approve(self):
        self.cases = []
        self.evidence = run_suite(self.config, [])
        self.assertEqual(self.assess(), "HOLD")

    def test_impact_includes_transitive_dependents_and_handles_cycles(self):
        expected = ["audit-review", "budget-dashboard", "operations-export", "request-workflow", "training-guide"]
        self.assertEqual(impact(["request-workflow"], DATA["dependencies"]), expected)
        self.assertEqual(impact(["a"], {"a": ["b"], "b": ["a"]}), ["a", "b"])

    def test_configuration_is_copied_and_denial_preserves_state(self):
        app = Application(self.config)
        self.config["approval_roles"].append("analyst")
        self.assertEqual(app.approve("X", "analyst", 10), {"error": "forbidden"})
        self.assertEqual(app.requests, {})
        self.assertEqual(app.audit, [])

    def test_boolean_budget_not_accepted_as_number(self):
        for value in (True, float("nan"), float("inf")):
            with self.subTest(value=value):
                self.assertEqual(Application(self.config).approve("X", "manager", value), {"error": "invalid_budget"})

    def test_rollback_restores_config_and_preserves_data(self):
        self.assertTrue(all(rollback_drill(self.config, DATA["versions"]["candidate"]).values()))


if __name__ == "__main__":
    unittest.main()
