# Production Operations Runbook: Customer RFM Segmentation
**System Version:** `rfm_v1.2.0`  
**Execution Cadence:** Monthly Batch Refresh (or Weekly for rapid CRM activation)  
**Standard Observation Window:** Rolling 365 Days (12 Months)  
**Reporting Currency:** USD (Standardized via Treasury exchange rates)

---

## 1. Routine Refresh Standard Operating Procedure (SOP)

### Prerequisites
- Confirmed ingestion of previous period's sales transactions, order returns, cancellations, and loyalty transactions.
- Updated Treasury FX exchange rate table.
- Up-to-date marketing consent suppression table (`email_opt_in`, `sms_opt_in`, `suppression_flag`).

### Step-by-Step Refresh Execution

1. **Verify Raw Data Deposits:**
   ```bash
   python -c "import os; print([f for f in os.listdir('data/raw')])"
   ```
2. **Execute Full Pipeline Refresh:**
   ```bash
   python cli.py run-all --as-of YYYY-MM-DD
   ```
3. **Verify Reconciliation & Quality Checklist:**
   ```bash
   python cli.py validate --as-of YYYY-MM-DD
   ```
   *Gate:* All 10 checks must report `PASS`. If financial discrepancy exceeds $0.05, halt promotion.
4. **Export CRM Feeds:**
   ```bash
   python cli.py export-audiences
   ```
5. **Launch Dashboard / Verification Server:**
   ```bash
   python cli.py serve --port 5000
   ```

---

## 2. Failure Triage & Incident Response

| Symptom / Alert | Probable Root Cause | Resolution SOP |
| :--- | :--- | :--- |
| **Financial Reconciliation Mismatch (`CHK_01` / `CHK_08`)** | Currency conversion drift, unlinked refunds, or untracked shipping/tax | Check `fx_rate_to_usd` in `orders.csv`. Ensure return records link to original completed order. Compare `gross - discount - refund` vs net merchandise revenue. |
| **Negative Recency or Future Order (`CHK_04`)** | Server clock drift in POS / web client or incorrect `--as-of` parameter | Audit source timestamps for UTC conversion issues. Ensure `--as-of` is >= latest transaction timestamp in dataset. |
| **Significant Segment Distribution Shift (>15% jump in Lapsed)** | Upstream data ingestion truncation or order sync failure | Confirm order intake volume for the last 30 days matches previous month. Check if POS data feed was interrupted. |
| **Ties Causing Bin Collapse (`CHK_07`)** | Spike in single-purchase customers | Engine utilizes `rank(method='min', pct=True)`. Verify that `f_score` for 0 orders is pinned to 1 and does not overflow. |
| **PII Contamination in Analytics (`CHK_09`)** | Upstream table join accidentally copied contact columns to `customer_rfm` | Run `test_validation.py`. Ensure contact details reside strictly in `customer_contacts_pii.csv` and are merged only dynamically in `campaign_engine.py`. |

---

## 3. SLA & Escalation Contacts

- **Data Engineering On-Call:** `de-team@retailcorp.internal`
- **Lead CRM & Marketing Operations:** `crm-ops@retailcorp.internal`
- **BI / Analytics Partner:** `analytics-lead@retailcorp.internal`
- **Finance Approval Lead:** `finance-reporting@retailcorp.internal`
- **Privacy & Compliance Officer:** `privacy-dpo@retailcorp.internal`
