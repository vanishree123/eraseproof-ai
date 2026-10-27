from datetime import datetime, timezone


class RemediationError(Exception):
    """Raised when a remediation request is invalid."""


def apply_simulated_remediation(
    records,
    system,
    approved,
    audit_log,
):
    """Apply an approved change to synthetic demo data only."""

    if not approved:
        raise RemediationError(
            "Human approval is required."
        )

    matches = [
        record
        for record in records
        if record.get("system") == system
        and record.get("status") == "Found"
    ]

    if len(matches) != 1:
        raise RemediationError(
            "Expected exactly one residual record for this system."
        )

    record = matches[0]

    before_status = record["status"]
    before_evidence = record.get("evidence", "")

    after_evidence = (
        "SIMULATED remediation only; independent verification "
        "is still required."
    )

    audit_entry = {
        "timestamp_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "system": system,
        "action": "Simulated remediation",
        "before_status": before_status,
        "after_status": "Deleted",
        "before_evidence": before_evidence,
        "after_evidence": after_evidence,
        "approval": "Approved in demo",
    }

    # Change synthetic data only after validation.
    record["status"] = "Deleted"
    record["evidence"] = after_evidence
    audit_log.append(audit_entry)

    return audit_entry