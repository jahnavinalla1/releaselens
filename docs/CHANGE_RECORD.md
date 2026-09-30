# Simulated change RL-001

**Requested change:** evaluate an administrative request-workflow upgrade. **Environment:** local synthetic lab. **Owner:** portfolio analyst role. **Approvals:** none obtained; example record only.

## Defect register

| Defect | Reproduction | Expected / actual | Proposed severity | Resolution in corrected configuration |
|---|---|---|---|---|
| D01 | U02, analyst approval with budget 100 | Denied / allowed with record written | High: permission regression | Remove analyst from approval roles |
| D02 | U05, manager approval | `approved` / `accepted` | High: downstream contract break | Restore canonical `approved` status |
| D03 | U06, successful approval | One audit entry / zero | High: missing decision history | Enable approval auditing |

Severity is proposed for this fictional administrative workflow. D01's persistence test also verifies that denial has no side effects. D02 checks the interface contract locally; it does not prove a vendor export works. D03 checks an audit event exists; the lab does not provide immutable or regulatory-grade auditing.

## Decision record

The candidate is **HOLD** because U02, U05 and U06 fail. The baseline and corrected configurations pass six of six cases and the rollback drill, so they are **READY_FOR_REVIEW**. Exact output is in `results/report.json`. No release has been approved or deployed.

Do not accept screenshots from another configuration as evidence. The gate ties results to hashes of the configuration and test catalog. Adding a requirement without coverage, omitting a case, duplicating a result, changing traceability or providing a failed rollback check also holds the release.

## Rollback rehearsal

Executed locally: create an existing approved request and audit entry; snapshot baseline configuration; install candidate; restore baseline; verify configuration equality, record preservation, audit preservation and a new approval smoke test.

Limit: no requests are processed while the bad candidate is installed. A production rollback must also address writes created under defective rules, schema compatibility, backup restoration and integration replay. A successful configuration rollback alone cannot undo those business effects.

## Proposed operational change sequence

1. Confirm scope and vendor compatibility; baseline configuration/data and downstream contracts.
2. Execute approved nonproduction tests and record build/configuration identifiers.
3. Resolve defects, rerun impacted and regression cases, rehearse the actual rollback procedure.
4. Obtain business and technical approval; schedule the agreed window and communicate support coverage.
5. Deploy through the organization's controlled process; perform smoke tests and monitor agreed indicators.
6. Trigger rollback for any critical approval, export or audit failure; preserve incident evidence and notify owners.
7. Close only after business validation, documentation updates and support handover.

No timing/SLA is invented here. Owners must establish actual monitoring thresholds, observation period and decision authority.

## Example stakeholder update — draft only

“The candidate failed three critical acceptance cases affecting approval permissions, status compatibility and audit history. The corrected configuration passes the local catalog and rollback rehearsal. The recommendation is to keep the candidate on hold and submit corrected evidence for business and integration-owner review.”
