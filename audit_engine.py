from typing import Any


def audit_customer(records: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Audit synthetic customer records from multiple systems.
    This function inspects evidence; it does not delete data.
    """
    if not records:
        return {
            "overall_status": "INCONCLUSIVE",
            "systems_checked": 0,
            "findings": [],
        }

    findings = []

    for record in records:
        status = record.get("status", "Unknown")
        system = record.get("system", "Unknown system")
        evidence = record.get("evidence", "No evidence supplied")

        if status == "Found":
            finding = {
                "system": system,
                "severity": "High",
                "result": "Residual data found",
                "evidence": evidence,
                "recommended_action": (
                    "Inspect the matching record and prepare "
                    "a deletion request for human approval."
                ),
            }
        elif status in ("Unknown", "Retained"):
            finding = {
                "system": system,
                "severity": "Medium",
                "result": "Verification required",
                "evidence": evidence,
                "recommended_action": (
                    "Check system logs, retention rules, and "
                    "deletion evidence."
                ),
            }
        elif status == "Deleted":
            finding = {
                "system": system,
                "severity": "Low",
                "result": "Deletion evidence reported",
                "evidence": evidence,
                "recommended_action": (
                    "Retain the evidence and verify the "
                    "system's deletion confirmation."
                ),
            }
        else:
            finding = {
                "system": system,
                "severity": "Medium",
                "result": "Unrecognized status",
                "evidence": evidence,
                "recommended_action": (
                    "Investigate the record before deciding "
                    "whether deletion is complete."
                ),
            }

        findings.append(finding)

    if any(item["result"] == "Residual data found" for item in findings):
        overall_status = "INCOMPLETE"
    elif any(item["result"] != "Deletion evidence reported" for item in findings):
        overall_status = "INCONCLUSIVE"
    else:
        overall_status = "VERIFICATION REQUIRED"

    return {
        "overall_status": overall_status,
        "systems_checked": len(findings),
        "findings": findings,
    }