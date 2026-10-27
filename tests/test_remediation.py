import pytest

from remediation_service import (
    RemediationError,
    apply_simulated_remediation,
)


def make_data():
    records = [
        {
            "system": "Analytics",
            "status": "Found",
            "evidence": "Customer identifier remains",
        }
    ]
    audit_log = []
    return records, audit_log


def test_remediation_rejects_missing_approval():
    records, audit_log = make_data()

    with pytest.raises(RemediationError):
        apply_simulated_remediation(
            records,
            "Analytics",
            False,
            audit_log,
        )

    assert records[0]["status"] == "Found"
    assert audit_log == []


def test_approved_remediation_updates_record_and_audit_log():
    records, audit_log = make_data()

    entry = apply_simulated_remediation(
        records,
        "Analytics",
        True,
        audit_log,
    )

    assert records[0]["status"] == "Deleted"
    assert entry["before_status"] == "Found"
    assert entry["after_status"] == "Deleted"
    assert entry["approval"] == "Approved in demo"
    assert "SIMULATED" in entry["after_evidence"]
    assert len(audit_log) == 1


def test_remediation_rejects_unknown_system():
    records, audit_log = make_data()

    with pytest.raises(RemediationError):
        apply_simulated_remediation(
            records,
            "Unknown system",
            True,
            audit_log,
        )

    assert records[0]["status"] == "Found"
    assert audit_log == []


def test_remediation_rejects_already_processed_record():
    records, audit_log = make_data()
    records[0]["status"] = "Deleted"

    with pytest.raises(RemediationError):
        apply_simulated_remediation(
            records,
            "Analytics",
            True,
            audit_log,
        )

    assert audit_log == []