import streamlit as st
import pandas as pd
from datetime import datetime, timezone
from remediation_service import (
    RemediationError,
    apply_simulated_remediation,
)

from audit_engine import audit_customer
from identity_matcher import find_identifier_matches


# -------------------------------
# Page configuration
# -------------------------------
st.set_page_config(
    page_title="EraseProof AI",
    page_icon="ðŸ›¡ï¸",
    layout="wide",
)

st.title("ðŸ›¡ï¸ EraseProof AI")
st.caption("Evidence-driven customer data deletion verification")

st.warning(
    "Synthetic demo data only. This prototype does not access "
    "real customer systems or delete records."
)


# -------------------------------
# Initialize session data
# -------------------------------
if "reset_demo" in st.query_params:
    st.session_state.pop("audit_records", None)
    st.session_state.pop("remediation_log", None)
    st.query_params.clear()

if "audit_records" not in st.session_state:
    st.session_state.audit_records = [
        {
            "system": "CRM",
            "status": "Deleted",
            "evidence": "Deletion event recorded",
            "identifiers": {
                "email": ["demo.user@example.com"],
                "customer_id": ["CUST-001"],
            },
        },
        {
            "system": "Analytics",
            "status": "Found",
            "evidence": "Customer identifier remains",
            "identifiers": {
                "email": ["DEMO.USER@example.com"],
            },
        },
        {
            "system": "Data Warehouse",
            "status": "Deleted",
            "evidence": "Tombstone record found",
            "identifiers": {
                "customer_id": ["CUST-001"],
            },
        },
        {
            "system": "Cache",
            "status": "Unknown",
            "evidence": "Cache expiration not verified",
            "identifiers": {
                "email": ["demo.user@example.com"],
            },
        },
        {
            "system": "Backup",
            "status": "Retained",
            "evidence": "Retention policy requires review",
            "identifiers": {
                "customer_id": ["CUST-001"],
            },
        },
    ]

if "remediation_log" not in st.session_state:
    st.session_state.remediation_log = []


target_identifiers = {
    "email": ["demo.user@example.com"],
    "customer_id": ["CUST-001"],
}

records = st.session_state.audit_records


# -------------------------------
# Customer deletion audit
# -------------------------------
st.subheader("Customer deletion audit")

customer_reference = st.selectbox(
    "Select synthetic customer",
    ["DEMO-CUSTOMER-001"],
)

st.write("Customer reference:", customer_reference)

if st.button("Run deletion audit", type="primary"):
    report = audit_customer(records)

    matches = find_identifier_matches(
        target_identifiers,
        records,
    )

    st.subheader("Overall result")

    if report["overall_status"] == "INCOMPLETE":
        st.error("Audit result: INCOMPLETE")
    elif report["overall_status"] == "INCONCLUSIVE":
        st.warning("Audit result: INCONCLUSIVE")
    else:
        st.info(f'Audit result: {report["overall_status"]}')

    col1, col2, col3 = st.columns(3)

    col1.metric("Systems checked", report["systems_checked"])

    residual_count = sum(
        item["result"] == "Residual data found"
        for item in report["findings"]
    )

    review_count = sum(
        item["result"] == "Verification required"
        for item in report["findings"]
    )

    col2.metric("Residual findings", residual_count)
    col3.metric("Systems needing review", review_count)

    st.subheader("System-by-system findings")

    findings_df = pd.DataFrame(report["findings"])
    st.table(findings_df)

    st.subheader("Cross-system identity matches")

    st.caption(
        "These are normalized identifier matches, not proof that "
        "a record belongs to the customer."
    )

    if matches:
        match_rows = []

        for match in matches:
            match_rows.append({
                "System": match["system"],
                "Audit status": match["status"],
                "Matched identifiers": ", ".join(
                    f'{item["type"]}: {item["value"]}'
                    for item in match["matched_on"]
                ),
                "Evidence": match["evidence"],
            })

        st.table(pd.DataFrame(match_rows))
    else:
        st.info("No matching identifiers found.")

    st.subheader("Recommended next actions")

    for finding in report["findings"]:
        with st.expander(
            f'{finding["system"]} â€” {finding["result"]}'
        ):
            st.write("**Evidence:**", finding["evidence"])
            st.write("**Severity:**", finding["severity"])
            st.write(
                "**Recommended action:**",
                finding["recommended_action"],
            )

    st.download_button(
        "Download audit report (CSV)",
        data=findings_df.to_csv(index=False).encode("utf-8"),
        file_name="eraseproof_audit_report.csv",
        mime="text/csv",
    )


# -------------------------------
# Safe remediation simulator
# -------------------------------
st.divider()
st.header("ðŸ§° Safe Remediation Simulator")

st.info(
    "Simulation only. No real customer systems or records are changed. "
    "Approval updates synthetic demo data in this session."
)

residual_records = [
    record
    for record in st.session_state.audit_records
    if record.get("status") == "Found"
]

if residual_records:
    selected_system = st.selectbox(
        "Select a system with residual data",
        [record["system"] for record in residual_records],
        key="remediation_system",
    )

    selected_record = next(
        record
        for record in residual_records
        if record["system"] == selected_system
    )

    st.subheader("1. Review proposed remediation")

    st.write("**System:**", selected_record["system"])
    st.write("**Current status:**", selected_record["status"])
    st.write("**Current evidence:**", selected_record["evidence"])

    st.write(
        "**Proposed action:** Simulate remediation of the residual "
        "finding after human approval."
    )

    st.warning(
        "Changing a demo status is not proof of actual deletion. "
        "Independent verification would be required in a real system."
    )

    approval = st.checkbox(
        "I reviewed the evidence and approve this demo simulation.",
        key="approve_remediation",
    )


    if st.button(
        "Approve and simulate remediation",
        type="primary",
        key="apply_remediation",
    ):
        if not approval:
            st.error("Please check the approval box first.")
        else:
            try:
                apply_simulated_remediation(
                    records=st.session_state.audit_records,
                    system=selected_system,
                    approved=approval,
                    audit_log=st.session_state.remediation_log,
                )

                st.success(
                    "Simulation recorded. No real customer system was changed."
                )

                st.rerun()

            except RemediationError as exc:
                st.error(str(exc))

else:
    st.success(
        "No records currently have status Found in the synthetic dataset."
    )


# -------------------------------
# Remediation audit trail
# -------------------------------
if st.session_state.remediation_log:
    st.subheader("2. Remediation audit trail")

    log_df = pd.DataFrame(st.session_state.remediation_log)

    st.table(log_df)

    st.download_button(
        "Download remediation audit trail",
        data=log_df.to_csv(index=False).encode("utf-8"),
        file_name="eraseproof_remediation_audit_trail.csv",
        mime="text/csv",
    )

st.caption(
    "The remediation log is temporary session data, not an immutable "
    "or tamper-proof production audit log."
)

st.divider()

st.caption(
    "EraseProof AI prototype | Synthetic data only | "
    "Human review required before remediation"
)
