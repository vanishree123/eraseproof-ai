from audit_engine import audit_customer


def test_residual_data_is_incomplete():
    records = [
        {
            "system": "Analytics",
            "status": "Found",
            "evidence": "Synthetic record remains",
        }
    ]

    result = audit_customer(records)

    assert result["overall_status"] == "INCOMPLETE"


def test_unknown_status_requires_review():
    records = [
        {
            "system": "Cache",
            "status": "Unknown",
            "evidence": "Expiration not verified",
        }
    ]

    result = audit_customer(records)

    assert result["overall_status"] == "INCONCLUSIVE"


def test_all_deleted_evidence_is_not_called_verified():
    records = [
        {
            "system": "CRM",
            "status": "Deleted",
            "evidence": "Deletion event recorded",
        }
    ]

    result = audit_customer(records)

    assert result["overall_status"] == "VERIFICATION REQUIRED"


def test_empty_records_are_inconclusive():
    result = audit_customer([])

    assert result["overall_status"] == "INCONCLUSIVE"