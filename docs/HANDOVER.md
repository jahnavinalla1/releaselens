# Training and support handover

## User quick guide

- A manager approves a service request only after the required positive budget is supplied.
- An analyst must receive a permission denial and no new approved record.
- The canonical downstream status is `approved`. A visually similar label can still break an integration.
- Every successful approval should be traceable in the audit history. If it is missing, report the request reference and environment through the approved channel.

These are fictional application rules used for the exercise, not instructions for an employer's systems.

## Trainer demonstration

Show U01 and U02 side by side, then show U05 and U06 on the candidate and corrected versions. Ask: “Why is a successful manager click not enough to approve this release?” Expected answer: it does not establish correct permissions, downstream compatibility or audit behavior.

## Support diagnosis

| Symptom | First check | Escalation / evidence |
|---|---|---|
| Analyst can approve | Candidate approval_roles | Application owner; U02 output; D01 |
| Approved request absent from export | Canonical status contract | Integration owner; U05 output; D02 |
| Approval has no history | Audit configuration | Application/audit owner; U06 output; D03 |
| Gate holds despite passing screenshots | Configuration/suite fingerprints and case completeness | Test coordinator; fresh machine-readable report |
| Configuration rollback appears successful but data differs | Actual data reconciliation and writes during deployment | Change lead; avoid repeated uncontrolled rollback |

## Handover checklist template

The following items require real owners in a deployed system: application version/environment, approved configuration, dependency owners, open defects, test-evidence location, training update, support contacts, escalation coverage, backup/rollback procedure, monitoring period and approval record. They are intentionally not marked complete by the lab.
