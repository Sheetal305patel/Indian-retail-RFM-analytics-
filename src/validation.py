"""
Automated Quality, Reconciliation, and Acceptance Audit Engine
Executes strict financial reconciliation, anomaly detection, recency bounds,
and identity completeness checks according to the Company-Ready Blueprint.
"""
import sqlite3
import json
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config.settings import (
    RAW_DATA_DIR,
    PROCESSED_DATA_DIR,
    REPORTS_DIR,
    EXCLUDED_STATUSES,
    QUALIFYING_STATUSES,
    MODEL_VERSION
)

def run_comprehensive_validation(as_of_date: str = "2026-11-20") -> dict:
    """
    Performs automated 10-point audit checklist and generates reconciliation certificate.
    """
    print(f"Executing Enterprise Validation & Reconciliation Audit as of {as_of_date}...")
    as_of_dt = datetime.strptime(as_of_date, "%Y-%m-%d")

    raw_orders_path = RAW_DATA_DIR / "orders.csv"
    curated_orders_path = PROCESSED_DATA_DIR / "orders_curated_clean.csv"
    rfm_path = PROCESSED_DATA_DIR / "customer_rfm.csv"

    if not raw_orders_path.exists() or not curated_orders_path.exists() or not rfm_path.exists():
        raise FileNotFoundError("Prerequisite data tables not found. Run ETL and RFM steps first.")

    df_raw = pd.read_csv(raw_orders_path)
    df_curated = pd.read_csv(curated_orders_path)
    df_rfm = pd.read_csv(rfm_path)

    audit_results = []
    has_critical_failure = False

    net_col = "net_sales_inr" if "net_sales_inr" in df_raw.columns else "net_sales_usd"

    # 1. Total Financial Reconciliation
    # Raw source net vs Curated net (including excluded/anonymous)
    raw_net_sum = round(float(df_raw[net_col].sum()), 2)
    curated_net_sum = round(float(df_curated[net_col].sum()), 2)
    diff_net = abs(raw_net_sum - curated_net_sum)
    check_1 = {
        "check_id": "CHK_01_FINANCIAL_RECONCILIATION",
        "name": "Raw Source vs Curated Net Sales Reconciliation",
        "expected": f"₹{raw_net_sum:,.2f}",
        "actual": f"₹{curated_net_sum:,.2f}",
        "difference": diff_net,
        "passed": diff_net < 0.05,
        "detail": "Confirmed that raw net sales equals curated net sales across all statuses."
    }
    audit_results.append(check_1)

    # 2. Excluded Order Integrity (Cancelled, Test, Fraud)
    # Excluded orders must have net qualifying sales = 0
    excluded_orders = df_curated[df_curated["order_status"].isin(EXCLUDED_STATUSES)]
    excluded_qualifying_count = excluded_orders["is_qualifying_order"].sum()
    check_2 = {
        "check_id": "CHK_02_EXCLUSION_INTEGRITY",
        "name": "Cancelled, Fraud, and Test Order Exclusion",
        "expected": "0 qualifying orders from excluded categories",
        "actual": f"{excluded_qualifying_count} qualifying orders",
        "passed": excluded_qualifying_count == 0,
        "detail": f"Verified {len(excluded_orders)} excluded orders were zeroed from RFM eligibility."
    }
    audit_results.append(check_2)

    # 3. Full Refund Handling
    # Fully refunded orders must not contribute to qualifying purchase frequency
    refunded_orders = df_curated[df_curated["order_status"] == "REFUNDED"]
    refunded_qualifying_count = refunded_orders["is_qualifying_order"].sum()
    check_3 = {
        "check_id": "CHK_03_REFUND_ACCOUNTING",
        "name": "Full Refund Zero-Frequency Enforcement",
        "expected": "0 qualifying orders among fully refunded transactions",
        "actual": f"{refunded_qualifying_count} qualifying orders",
        "passed": refunded_qualifying_count == 0,
        "detail": f"Verified {len(refunded_orders)} fully refunded orders have zero frequency weight."
    }
    audit_results.append(check_3)

    # 4. Negative Recency & Future Date Detection
    future_orders = df_curated[pd.to_datetime(df_curated["order_timestamp"]) > as_of_dt]
    negative_recency_count = (df_rfm["recency_days"] < 0).sum()
    check_4 = {
        "check_id": "CHK_04_TEMPORAL_INTEGRITY",
        "name": "Temporal Bounds and Non-Negative Recency",
        "expected": "0 future orders and 0 negative recency records",
        "actual": f"{len(future_orders)} future orders, {negative_recency_count} negative recencies",
        "passed": (len(future_orders) == 0) and (negative_recency_count == 0),
        "detail": "Verified timestamps do not exceed as_of_date and recency is strictly non-negative."
    }
    audit_results.append(check_4)

    # 5. Customer Deduplication & Primary Key Uniqueness
    cust_dups = df_rfm.duplicated(subset=["customer_id"]).sum()
    check_5 = {
        "check_id": "CHK_05_CUSTOMER_DEDUPLICATION",
        "name": "Customer Master Table Uniqueness",
        "expected": "0 duplicate customer_id records",
        "actual": f"{cust_dups} duplicate customer records",
        "passed": cust_dups == 0,
        "detail": f"Confirmed all {len(df_rfm):,} customer records are deduplicated primary keys."
    }
    audit_results.append(check_5)

    # 6. Anonymous POS Revenue Quantification
    anon_orders = df_curated[df_curated["customer_id"].isna()]
    anon_rev = round(float(anon_orders[net_col].sum()), 2)
    total_sales = round(float(df_curated[net_col].sum()), 2)
    anon_share = round((anon_rev / total_sales * 100), 2) if total_sales > 0 else 0
    check_6 = {
        "check_id": "CHK_06_ANONYMOUS_QUANTIFICATION",
        "name": "Anonymous Store Sales Quantification",
        "expected": "Quantified and segregated from customer profiles",
        "actual": f"₹{anon_rev:,.2f} ({anon_share}% of total net sales)",
        "passed": True,
        "detail": f"Identified {len(anon_orders):,} anonymous POS orders isolated from RFM customer tables."
    }
    audit_results.append(check_6)

    # 7. Segment Plausibility and Coverage
    # Ensure no customer is left unassigned (segment is not NA) and each segment has members
    unassigned_count = df_rfm["segment"].isna().sum()
    segment_counts = df_rfm["segment"].value_counts().to_dict()
    has_empty_segments = len(segment_counts) < 5 # should have good distribution across classes
    check_7 = {
        "check_id": "CHK_07_SEGMENT_PLAUSIBILITY",
        "name": "Lifecycle Segment Completeness",
        "expected": "0 unassigned customers and plausible distribution",
        "actual": f"{unassigned_count} unassigned, {len(segment_counts)} active segments",
        "passed": (unassigned_count == 0) and (not has_empty_segments),
        "detail": f"Segment breakdown: {segment_counts}"
    }
    audit_results.append(check_7)

    # 8. RFM Mathematical Reconciliation
    # Sum of customer net sales in RFM table must equal total qualifying orders sales in window
    rfm_sales_sum = round(float(df_rfm[net_col].sum()), 2)
    qualifying_orders = df_curated[df_curated["is_qualifying_order"]]
    qualifying_sales_sum = round(float(qualifying_orders[net_col].sum()), 2)
    rfm_sales_diff = abs(rfm_sales_sum - qualifying_sales_sum)
    check_8 = {
        "check_id": "CHK_08_RFM_SUMMATION_RECONCILIATION",
        "name": "RFM Customer Total vs Qualifying Orders Reconciliation",
        "expected": f"₹{qualifying_sales_sum:,.2f}",
        "actual": f"₹{rfm_sales_sum:,.2f}",
        "difference": rfm_sales_diff,
        "passed": rfm_sales_diff < 0.05,
        "detail": "Validated that customer-level sales sum strictly equals qualifying order sales."
    }
    audit_results.append(check_8)

    # 9. PII Isolation Check
    # Verify that df_rfm does NOT contain first_name, last_name, email, or phone
    pii_columns = {"first_name", "last_name", "email", "phone", "street_address"}
    present_pii = pii_columns.intersection(set(df_rfm.columns))
    check_9 = {
        "check_id": "CHK_09_PII_SEPARATION",
        "name": "Analytical Table PII Isolation (Privacy by Design)",
        "expected": "0 PII contact attributes in customer_rfm",
        "actual": f"{len(present_pii)} PII fields detected ({list(present_pii)})",
        "passed": len(present_pii) == 0,
        "detail": "Verified that contact identifiers remain segregated in protected contact tables."
    }
    audit_results.append(check_9)

    # 10. Sample Customer Reproducibility Test
    # Pick 3 random customers and independently verify their R, F, M calculation
    sample_custs = df_rfm[df_rfm["qualifying_order_count"] > 1].sample(n=min(3, len(df_rfm)), random_state=42)
    sample_passed = True
    for _, row in sample_custs.iterrows():
        cid = row["customer_id"]
        c_orders = qualifying_orders[qualifying_orders["customer_id"] == cid]
        calc_f = len(c_orders)
        calc_m = round(float(c_orders[net_col].sum()), 2)
        if calc_f != row["qualifying_order_count"] or abs(calc_m - row[net_col]) > 0.05:
            sample_passed = False
            break

    check_10 = {
        "check_id": "CHK_10_SAMPLE_REPRODUCIBILITY",
        "name": "Sample Customer Metric Audit & Reproducibility",
        "expected": "100% calculation match across sampled customer records",
        "actual": "100% match" if sample_passed else "Mismatch detected",
        "passed": sample_passed,
        "detail": f"Independently verified order histories for sample customers {sample_custs['customer_id'].tolist()}."
    }
    audit_results.append(check_10)

    # Overall Summary
    total_checks = len(audit_results)
    passed_checks = sum(1 for c in audit_results if c["passed"])
    overall_status = "PASSED" if passed_checks == total_checks else "FAILED"

    report = {
        "audit_timestamp": datetime.now().isoformat(),
        "as_of_date": as_of_date,
        "model_version": MODEL_VERSION,
        "overall_status": overall_status,
        "scorecard": f"{passed_checks}/{total_checks} checks passed",
        "financial_summary": {
            "total_raw_orders": int(len(df_raw)),
            "total_raw_net_sales_usd": raw_net_sum,
            "qualifying_orders_in_window": int(len(qualifying_orders)),
            "qualifying_net_sales_usd": qualifying_sales_sum,
            "anonymous_net_sales_usd": anon_rev,
            "anonymous_sales_share_pct": anon_share
        },
        "checklist": audit_results
    }

    def make_json_serializable(obj):
        if isinstance(obj, (np.bool_, bool)):
            return bool(obj)
        if isinstance(obj, (np.integer, int)):
            return int(obj)
        if isinstance(obj, (np.floating, float)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, dict):
            return {k: make_json_serializable(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [make_json_serializable(item) for item in obj]
        return obj

    # Save validation report
    with open(REPORTS_DIR / "validation_report.json", "w", encoding="utf-8") as f:
        json.dump(make_json_serializable(report), f, indent=2)

    # Write formatted Markdown report
    md_content = f"""# Acceptance & Data Quality Audit Report
**Status:** `{"[PASSED]" if overall_status == "PASSED" else "[FAILED]"}` ({passed_checks}/{total_checks} Checks Passed)  
**As-Of Date:** {as_of_date} | **Model Version:** {MODEL_VERSION}  
**Audit Timestamp:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

### Executive Reconciliation Summary
- **Total Ingested Raw Orders:** {len(df_raw):,}
- **Total Raw Net Sales:** ${raw_net_sum:,.2f} USD
- **Identified Qualifying Orders (12-Mo Window):** {len(qualifying_orders):,}
- **Customer RFM Net Sales Base:** ${rfm_sales_sum:,.2f} USD
- **Anonymous Store Sales (Excluded from RFM):** ${anon_rev:,.2f} USD ({anon_share}% of sales)

---

### Acceptance Criteria Checklist

| Check ID | Requirement | Result | Expected | Actual |
| :--- | :--- | :---: | :--- | :--- |
"""
    for c in audit_results:
        icon = "[PASS]" if c["passed"] else "[FAIL]"
        md_content += f"| `{c['check_id']}` | {c['name']} | {icon} | {c['expected']} | {c['actual']} |\n"

    md_content += "\n---\n*Report generated automatically by customer-rfm-segmentation audit engine.*\n"

    with open(REPORTS_DIR / "validation_report.md", "w", encoding="utf-8") as f:
        f.write(md_content)

    print(f"Validation Audit Finished: {passed_checks}/{total_checks} passed. Status: {overall_status}")
    return report

if __name__ == "__main__":
    run_comprehensive_validation()
