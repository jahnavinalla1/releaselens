"""Executable research application release assessment; Python 3.10+, no dependencies."""
import argparse
from copy import deepcopy
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


class Application:
    """Small research service-request workflow; roles are fixtures, not authentication."""
    def __init__(self, config):
        self.config = deepcopy(config)
        self.requests = {}
        self.audit = []

    def approve(self, request_id, role, budget):
        if role not in self.config["approval_roles"]:
            return {"error": "forbidden"}
        if type(budget) not in (int, float) or not math.isfinite(budget) or budget <= 0:
            return {"error": "invalid_budget"}
        record = {"request_id": request_id, "status": self.config["approved_status"], "budget": budget}
        self.requests[request_id] = record
        if self.config["audit_enabled"]:
            self.audit.append({"action": "approve", "request_id": request_id, "actor_role": role})
        return record

    def install(self, config):
        self.config = deepcopy(config)


def execute_case(config, case):
    app = Application(config)
    response = app.approve(**case["input"])
    actual = {key: response.get(key) for key in case["expected"]}
    passed = actual == case["expected"]
    if "expected_audits" in case:
        passed = passed and len(app.audit) == case["expected_audits"]
    if "expected_records" in case:
        passed = passed and len(app.requests) == case["expected_records"]
    return {"case_id": case["id"], "requirement": case["requirement"],
            "passed": passed, "expected": case["expected"], "actual": actual,
            "audit_count": len(app.audit), "record_count": len(app.requests)}


def run_suite(config, cases):
    return {"config_digest": digest(config), "suite_digest": digest(cases),
            "results": [execute_case(config, case) for case in cases]}


def rollback_drill(baseline, candidate):
    app = Application(baseline)
    app.approve("DEMO-EXISTING", "manager", 100)
    snapshot = deepcopy(app.config)
    saved_records, saved_audit = deepcopy(app.requests), deepcopy(app.audit)
    app.install(candidate)
    app.install(snapshot)
    return {"config_restored": app.config == baseline,
            "records_preserved": app.requests == saved_records,
            "audit_preserved": app.audit == saved_audit,
            "post_rollback_smoke": app.approve("DEMO-NEW", "manager", 200).get("status") == "approved"}


def gate(config, cases, requirements, evidence, rollback):
    """Fail closed for stale, incomplete, duplicate or failed execution evidence."""
    reasons = []
    if evidence.get("config_digest") != digest(config):
        reasons.append("Evidence does not match candidate configuration")
    if evidence.get("suite_digest") != digest(cases):
        reasons.append("Evidence does not match current test suite")
    required_ids = {c["id"] for c in cases}
    results = evidence.get("results", [])
    observed_ids = [r["case_id"] for r in results]
    if not required_ids or len(required_ids) != len(cases):
        reasons.append("Test catalog is empty or has duplicate IDs")
    if set(observed_ids) != required_ids or len(observed_ids) != len(required_ids):
        reasons.append("Execution evidence is incomplete or duplicated")
    required_requirements = {r["id"] for r in requirements}
    if not required_requirements or not required_requirements.issubset({c["requirement"] for c in cases}):
        reasons.append("Requirements lack test coverage")
    catalog = {c["id"]: c for c in cases}
    if any(r.get("requirement") != catalog.get(r["case_id"], {}).get("requirement") for r in results):
        reasons.append("Requirement traceability mismatch")
    if any(r.get("passed") is not True for r in results):
        reasons.append("One or more regression tests failed")
    rollback_checks = {"config_restored", "records_preserved", "audit_preserved", "post_rollback_smoke"}
    if set(rollback) != rollback_checks or any(rollback[k] is not True for k in rollback_checks):
        reasons.append("Rollback drill is missing or failed")
    return {"decision": "HOLD" if reasons else "READY_FOR_REVIEW", "reasons": reasons,
            "human_approval": "Not obtained; simulated technical evidence only"}


def impact(changed, dependencies):
    affected = set(changed)
    while True:
        extended = affected | {node for node, parents in dependencies.items() if affected.intersection(parents)}
        if extended == affected:
            return sorted(affected)
        affected = extended


def demo(output):
    scenario = json.loads((ROOT / "data/release.json").read_text())
    cases, requirements = scenario["cases"], scenario["requirements"]
    baseline = scenario["versions"]["baseline"]
    report = {"simulation": True, "impact": impact(["request-workflow"], scenario["dependencies"]), "releases": {}}
    for name, config in scenario["versions"].items():
        evidence = run_suite(config, cases)
        rollback = rollback_drill(baseline, config)
        report["releases"][name] = {"evidence": evidence, "rollback": rollback,
                                  "gate": gate(config, cases, requirements, evidence, rollback)}
    output.mkdir(parents=True, exist_ok=True)
    (output / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    lines = ["# ReleaseLens — executed release assessment", "", "Synthetic research service-request workflow.", "",
             "| Configuration | Tests passed | Decision |", "|---|---:|---|"]
    for name, result in report["releases"].items():
        count = sum(r["passed"] for r in result["evidence"]["results"])
        lines.append(f"| {name} | {count}/{len(cases)} | {result['gate']['decision']} |")
    lines += ["", "READY_FOR_REVIEW is a technical recommendation, not release authorization.", "",
              "Impacted components: " + ", ".join(report["impact"]), "",
              "Rollback drill restores configuration and preserves records and audit entries in memory.",
              "It does not test database schema migrations, infrastructure, downtime or vendor behavior."]
    (output / "RESULTS.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "results")
    demo(parser.parse_args().output)
