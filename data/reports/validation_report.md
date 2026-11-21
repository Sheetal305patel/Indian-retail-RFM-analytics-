# Acceptance & Data Quality Audit Report
**Status:** `[PASSED]` (10/10 Checks Passed)  
**As-Of Date:** 2026-11-20 | **Model Version:** rfm_v3.0_india_enterprise  
**Audit Timestamp:** 2026-11-21 19:12:40

---

### Executive Reconciliation Summary
- **Total Ingested Raw Orders:** 20,000
- **Total Raw Net Sales:** $46,653,440.25 USD
- **Identified Qualifying Orders (12-Mo Window):** 14,967
- **Customer RFM Net Sales Base:** $40,603,905.40 USD
- **Anonymous Store Sales (Excluded from RFM):** $2,835,873.90 USD (6.08% of sales)

---

### Acceptance Criteria Checklist

| Check ID | Requirement | Result | Expected | Actual |
| :--- | :--- | :---: | :--- | :--- |
| `CHK_01_FINANCIAL_RECONCILIATION` | Raw Source vs Curated Net Sales Reconciliation | [PASS] | ₹46,653,440.25 | ₹46,653,440.25 |
| `CHK_02_EXCLUSION_INTEGRITY` | Cancelled, Fraud, and Test Order Exclusion | [PASS] | 0 qualifying orders from excluded categories | 0 qualifying orders |
| `CHK_03_REFUND_ACCOUNTING` | Full Refund Zero-Frequency Enforcement | [PASS] | 0 qualifying orders among fully refunded transactions | 0 qualifying orders |
| `CHK_04_TEMPORAL_INTEGRITY` | Temporal Bounds and Non-Negative Recency | [PASS] | 0 future orders and 0 negative recency records | 0 future orders, 0 negative recencies |
| `CHK_05_CUSTOMER_DEDUPLICATION` | Customer Master Table Uniqueness | [PASS] | 0 duplicate customer_id records | 0 duplicate customer records |
| `CHK_06_ANONYMOUS_QUANTIFICATION` | Anonymous Store Sales Quantification | [PASS] | Quantified and segregated from customer profiles | ₹2,835,873.90 (6.08% of total net sales) |
| `CHK_07_SEGMENT_PLAUSIBILITY` | Lifecycle Segment Completeness | [PASS] | 0 unassigned customers and plausible distribution | 0 unassigned, 8 active segments |
| `CHK_08_RFM_SUMMATION_RECONCILIATION` | RFM Customer Total vs Qualifying Orders Reconciliation | [PASS] | ₹40,603,905.40 | ₹40,603,905.40 |
| `CHK_09_PII_SEPARATION` | Analytical Table PII Isolation (Privacy by Design) | [PASS] | 0 PII contact attributes in customer_rfm | 0 PII fields detected ([]) |
| `CHK_10_SAMPLE_REPRODUCIBILITY` | Sample Customer Metric Audit & Reproducibility | [PASS] | 100% calculation match across sampled customer records | 100% match |

---
*Report generated automatically by customer-rfm-segmentation audit engine.*
