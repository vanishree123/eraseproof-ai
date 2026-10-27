from identity_matcher import find_identifier_matches


def test_matches_email_alias_case_insensitively():
    targets = {
        "email": ["demo.user@example.com"],
    }

    records = [
        {
            "system": "Analytics",
            "identifiers": {
                "email": [" DEMO.USER@EXAMPLE.COM "],
            },
        }
    ]

    matches = find_identifier_matches(targets, records)

    assert len(matches) == 1
    assert matches[0]["system"] == "Analytics"


def test_matches_internal_customer_id():
    targets = {
        "customer_id": ["CUST-001"],
    }

    records = [
        {
            "system": "Warehouse",
            "identifiers": {
                "customer_id": ["cust-001"],
            },
        }
    ]

    assert len(find_identifier_matches(targets, records)) == 1


def test_does_not_match_different_identifier_types():
    targets = {
        "email": ["12345"],
    }

    records = [
        {
            "system": "CRM",
            "identifiers": {
                "customer_id": ["12345"],
            },
        }
    ]

    assert find_identifier_matches(targets, records) == []


def test_unrelated_customer_is_not_matched():
    targets = {
        "email": ["demo.user@example.com"],
    }

    records = [
        {
            "system": "CRM",
            "identifiers": {
                "email": ["other.user@example.com"],
            },
        }
    ]

    assert find_identifier_matches(targets, records) == []
