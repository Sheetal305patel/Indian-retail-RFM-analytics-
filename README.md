# Customer Value and Lifecycle Segmentation (RFM Engine)
### Production-Grade Omnichannel Retail & D2C Analytics Engine — Indian Consumer Conglomerate Edition
**Benchmarked Against:** Tata Neu / Tata Consumer Products &bull; Reliance Retail / Ajio &bull; Nykaa (FSN E-Commerce) &bull; Hindustan Unilever Limited (HUL) &bull; ITC Limited

[![Python 3.11](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![Market](https://img.shields.io/badge/Market-100%25%20India%20Domestic%20(INR%20₹)-orange.svg)]()
[![Architecture](https://img.shields.io/badge/Architecture-Clean%20ETL%20%2B%20RFM%20Engine-emerald.svg)]()
[![Compliance](https://img.shields.io/badge/Compliance-DPDP%20Act%20%26%20TRAI%20DND-purple.svg)]()
[![Model Version](https://img.shields.io/badge/Model-rfm__v1.2.0-sky.svg)]()

---

## 1. Project Overview & Commercial Context

This repository provides an enterprise-ready, end-to-end customer value, predictive machine learning, and behavioral segmentation system tailored specifically to the **Indian Domestic Retail, FMCG, and E-Commerce Market**.

Unlike generic textbook examples with synthetic toy data, this project models real-world commercial realities faced by major Indian consumer conglomerates (**Tata Group / Tata Neu**, **Reliance Retail / Ajio**, **Nykaa**, **HUL**, **ITC**):

1. **100% Native INR (₹) Financial Accounting:** Models authentic Indian basket sizes (₹450 Quick Commerce FMCG to ₹4,499 Premium D2C Apparel / Beauty).
2. **Cash on Delivery (COD) vs Prepaid Unit Economics:** Realistically models India's payment landscape:
   - **58% UPI** (PhonePe, Google Pay, Paytm) with 0% gateway fees.
   - **28% COD** with an authentic **23.9% Return-to-Origin (RTO)** bounce rate.
   - **Logistics Courier Loss:** Penalizes ₹140 per bounced RTO order (forward + reverse 3PL courier charges via Delhivery/BlueDart), creating true negative contribution margins.
3. **Omnichannel Identity Resolution:** Stitches customer accounts across D2C Mobile Apps, Web, Quick Commerce (Blinkit/Zepto/Instamart), and Offline POS Stores (Reliance Smart / Nykaa Luxe / Westside).
4. **Behavioral RFM Engine with Tie Handling:** Calculates rolling 12-month Recency, Frequency, Monetary value (NMV), and Contribution Margin with percentile rank tie-handling.
5. **8 Actionable Lifecycle Segments:** Maps customers into explainable segments with defined Indian commercial action plans.
6. **Predictive ML Churn Propensity (PyTorch):** Deep neural classifier predicting 90-day churn likelihood and risk tiers (Critical, High, Medium, Low).
7. **Predictive Customer Lifetime Value (pLTV):** Forward 12-month expected spend and contribution margin estimation across 4 strategic quadrants.
8. **Real-Time Event Streaming Engine:** Low-latency event bus simulation with incremental online state updates and dynamic live segment promotions.
9. **Acceptance & Financial Audit Engine:** Automates a 10-point reconciliation checklist verifying totals against source systems.
10. **Privacy-by-Design Activation:** Complies with India's **Digital Personal Data Protection (DPDP) Act** and **TRAI DND (Do Not Disturb)** regulations. WhatsApp-first CRM activation with 10% randomized holdout control splits.
11. **Interactive Full-Stack Web Dashboard:** Full-featured visualization platform featuring Executive, Predictive ML, Live Stream, CRM, Analyst Audit, and Customer 360 views.

> 📖 **Recruiter Interview Cheat Sheet:** Check out [RECRUITER_GUIDE.md](file:///C:/Users/sheet/.gemini/antigravity/scratch/customer-rfm-segmentation/RECRUITER_GUIDE.md) for full architecture explanations, SQL queries, metric definitions, and interview Q&A.

---

## 2. System Architecture

```
customer-rfm-segmentation/
├── config/
│   └── settings.py                     # Business rules, observation window (365d), Indian market benchmarks
├── data/
│   ├── raw/                            # Ingested orders, items, customers, identity links, PII contacts
│   ├── processed/                      # Curated clean orders, customer_rfm table, SQLite database
│   ├── exports/                        # CRM campaign feeds with holdouts (WhatsApp / Email / SMS)
│   └── reports/                        # Automated validation reports & audit certificates
├── src/
│   ├── data_generator.py               # Indian retail simulator: 4,000 customers, 20,000 orders in INR (₹)
│   ├── identity_resolution.py          # Cross-channel customer stitching & anonymous POS store audit
│   ├── etl_pipeline.py                 # Order curation, RTO filtering, NMV & contribution margin derivation
│   ├── rfm_engine.py                   # R/F/M quintile scoring (1-5), tie resolution, 8 lifecycle segments
│   ├── predictive_models.py            # PyTorch Churn Propensity Classifier & forward 12M pLTV model
│   ├── streaming_pipeline.py           # Real-Time Event Bus with online state recalculations
│   ├── validation.py                   # Automated 10-point acceptance and financial reconciliation audit
│   ├── campaign_engine.py              # DPDP/TRAI-aware audience exporter with randomized holdout splits
│   └── pilot_measurement.py            # A/B test analyzer: incremental margin, conversion lift, z-scores
├── web/                                # Production interactive web application & dashboard
│   ├── app.py                          # Flask backend with SSE streaming, REST APIs & template routes
│   ├── static/css/style.css            # Dark/light executive styling
│   └── templates/
│       ├── base.html                   # Enterprise navigation layout
│       ├── executive.html              # Executive View: INR revenue share, margin %, COD vs Prepaid RTO card
│       ├── predictive.html             # Predictive ML View: Strategic Quadrants, pLTV, VIPs at Risk in INR
│       ├── streaming.html              # Real-Time Stream Monitor: Live event ticker & segment promotions
│       ├── crm_activation.html         # CRM View: WhatsApp & SMS channel eligibility, audience exporter
│       ├── analyst.html                # Analyst View: R/F/M distributions, ties, reconciliation audit
│       └── customer_lookup.html        # Customer 360: individual RFM profile, orders, and action
├── tests/                              # Comprehensive test suite (14 unit tests, ETL rules, scoring, privacy)
├── cli.py                              # Terminal CLI for automated batch pipelines
├── RECRUITER_GUIDE.md                  # Comprehensive interview cheat sheet & commercial talking points
├── RUNBOOK.md                          # Production operations runbook and incident triage SOPs
└── requirements.txt                    # Project dependencies
```

---

## 3. Commercial Transaction Rules & Accounting in INR (₹)

### Schema Definitions
- **`customers`**: `customer_id`, `identity_status` (`verified_account`, `loyalty_member`, `guest_resolved`), `first_seen_at`, `marketing_eligibility_by_channel` (`whatsapp_opt_in`, `email_opt_in`, `sms_opt_in`, `push_opt_in`), `city_tier` (`Metro`, `Tier 2`, `Tier 3`), `city_location`, `suppression_flag`.
- **`orders`**: `order_id`, `customer_id`, `order_timestamp`, `order_status`, `payment_method` (`UPI`, `COD`, `Credit_Debit_Card`, `NetBanking`), `channel`, `currency` (`INR`), `gross_amount`, `discount_amount`, `refund_amount`, `net_sales_inr`, `product_cost_inr`, `gateway_fee_inr`, `rto_courier_loss_inr`, `contribution_margin_inr`.
- **`customer_rfm`**: `customer_id`, `as_of_date`, `observation_start_date`, `last_purchase_at`, `recency_days`, `qualifying_order_count`, `net_sales_inr`, `contribution_margin_inr`, `r_score`, `f_score`, `m_score`, `rfm_code`, `segment`, `model_version`.

### Commercial Transaction Rules (Blueprint Section 5)
1. **Qualifying Order Definition:** Must be completed/delivered, non-test, non-fraud, non-RTO, associated with a valid customer ID, and placed within the rolling 12-month observation window.
2. **Returns & COD RTO Accounting:** Cancelled, test, fraud, and RTO (bounced COD) orders are excluded from frequency and net sales. Fully refunded orders have net sales = ₹0 and are excluded from purchase frequency ($F = 0$). Partially returned orders count once in frequency with reduced net sales.
3. **Net Merchandise Sales (NMV):**
   $$\text{Net Sales (INR)} = \text{Gross Merchandise Value (GMV)} - \text{Discounts} - \text{Refunds/Returns}$$
4. **Contribution Margin (CM2):**
   $$\text{Contribution Margin} = \text{Net Sales} - \text{Product COGS} - \text{Gateway Fee} - \text{3PL RTO Courier Loss}$$
5. **Anonymous Sales Quantification:** Anonymous in-store POS walk-ins are quantified (~6% of revenue) and segregated from customer-level scoring to measure identity coverage rather than forcing unlinked transactions into synthetic profiles.

---

## 4. RFM Scoring & Tie-Handling Methodology

### Scoring Logic
Metrics are computed over a rolling 365-day observation window:
- **Recency ($R$):** Days elapsed since the most recent qualifying purchase. Inverted rank: lowest days earn Score 5.
- **Frequency ($F$):** Total qualifying orders in the observation window. Score 1 to 5.
- **Monetary ($M$):** Total net merchandise spend (INR ₹) in the observation window. Score 1 to 5.

### Documented Tie Handling (Blueprint Section 6)
In retail, a large percentage of customers share identical frequency (e.g. exactly 1 purchase) or zero orders in the window. 
- Using standard `pd.qcut` results in duplicate bin edge collisions and arbitrary bin assignment.
- Our engine uses `rank(method='min', pct=True)`:
  - Customers with $F = 0$ are strictly anchored to Score 1.
  - Customers with $F = 1$ receive the exact same fair score bucket based on their empirical percentile.
  - Net sales $\le ₹0$ is strictly anchored to Score 1.

---

## 5. The 8 Commercial Lifecycle Segments (Indian Retail Edition)

| Segment | RFM Profile | Typical Behavior | Prescribed Commercial Action |
| :--- | :--- | :--- | :--- |
| **Champions** | `R: 4-5`, `F: 4-5`, `M: 4-5` | High recency, high frequency, top-tier spend | Early VIP festival access (Diwali/Big Billion), concierge service, Tata Neu Coins / Ajio Luxe benefits. |
| **Loyal Customers** | `R: 3-5`, `F: 3-5`, `M: 3-5` | Consistent repeat purchasing across recent quarters | WhatsApp replenishment triggers, bundle cross-sell, loyalty tier upgrade nudges. |
| **High-Value, At Risk** | `R: 1-2`, `F: 4-5` or `M: 4-5` | High historical spend/frequency, but recency is declining | Proactive WhatsApp outreach, bespoke win-back discount coupon, customer care survey. |
| **Recent Customers** | `R: 4-5`, `F: 1-2`, tenure $\le 60\text{d}$ | First purchase made within recent onboarding window | Welcome WhatsApp drip, product education, 2nd-order incentive within 21 days. |
| **Promising** | `R: 4-5`, `F: 2` or `M: 3-4` | Recent purchase with early signs of repeat spend | Category discovery campaigns, prepaid discount nudge (shift away from COD). |
| **Need Attention** | `R: 3`, `F: \ge 2` or `M: \ge 3` | Above-average value, but recency drifting past normal cycle | Timely replenishment reminder, tailored "We miss you" seasonal offer. |
| **Lapsed** | $F=0$ or $\text{Recency} > 180\text{d}$ | Inactive beyond standard buying cycle | Low-cost digital reactivation test; suppress from paid ads if unresponsive. |
| **One-Time / Low-History** | `R: \le 3`, `F: 1`, low spend | Single order outside onboarding window | Light-touch nurture, review delivery satisfaction, test second-purchase offer. |

---

## 6. Acceptance Criteria & 10-Point Audit Checklist

The automated audit engine (`src/validation.py`) enforces strict financial and data integrity checks:
1. `CHK_01_FINANCIAL_RECONCILIATION`: Raw net sales strictly reconciles to curated net sales ($\Delta < ₹0.05$).
2. `CHK_02_EXCLUSION_INTEGRITY`: Zero qualifying orders originate from Cancelled, Test, or Fraud transactions.
3. `CHK_03_REFUND_ACCOUNTING`: Zero qualifying frequency weight assigned to fully refunded orders.
4. `CHK_04_TEMPORAL_INTEGRITY`: Zero future transactions beyond as-of date; zero negative recency values.
5. `CHK_05_CUSTOMER_DEDUPLICATION`: Zero duplicate customer IDs in analytics master table.
6. `CHK_06_ANONYMOUS_QUANTIFICATION`: Anonymous in-store sales are quantified and segregated from customer scoring.
7. `CHK_07_SEGMENT_PLAUSIBILITY`: Zero unassigned customers; all 8 segments have active distribution.
8. `CHK_08_RFM_SUMMATION_RECONCILIATION`: Customer RFM net sales sum strictly equals qualifying order sales in window.
9. `CHK_09_PII_SEPARATION`: Zero contact PII fields (`email`, `phone`, `name`) present in analytical tables.
10. `CHK_10_SAMPLE_REPRODUCIBILITY`: 100% calculation match across randomly sampled customer order histories.

---

## 7. Quick Start & Execution Guide

### 1. Installation
```bash
cd C:\Users\sheet\.gemini\antigravity\scratch\customer-rfm-segmentation
pip install -r requirements.txt
```

### 2. Run the Full End-to-End Pipeline
Executes synthetic Indian multi-channel generation, identity resolution, ETL curation, RFM scoring, acceptance validation, audience export, and pilot lift simulation:
```bash
python cli.py run-all --as-of 2026-11-20
```

### 3. Launch Interactive Web Dashboard
```bash
python cli.py serve --port 5000
```
Navigate to `http://127.0.0.1:5000` in your browser to access:
- **Executive View (`/executive`)**: Revenue concentration in ₹ INR, COD vs Prepaid RTO penalty card, city tier distribution (Metro, Tier 2, Tier 3 Bharat).
- **Predictive ML View (`/predictive`)**: Strategic 4-quadrant scatter matrix, 90-day churn tiers, 12M pLTV forecast, VIPs at Risk table.
- **Real-Time Stream Monitor (`/streaming`)**: Live transaction ticker via Server-Sent Events (SSE), live segment promotions, and event injector.
- **CRM Activation (`/crm`)**: WhatsApp & SMS consent matrices, audience exporter with holdouts, A/B pilot simulator.
- **Analyst & Audit (`/analyst`)**: RFM histograms, tie-handling explanations, 10-point audit evidence.
- **Customer 360 (`/customer-lookup?id=IND-CUST-00001`)**: Full customer profile with RFM, churn risk %, pLTV forecast, and transaction history.

### 4. Machine Learning & Streaming CLI Commands
```bash
# Score RFM lifecycle segments
python cli.py score-rfm

# Train PyTorch churn model & calculate forward 12M pLTV
python cli.py train-ml

# Simulate real-time event streaming with dynamic segment promotions
python cli.py stream-events --events 25 --interval 0.3

# Run automated 10-point audit validation
python cli.py validate

# Run automated unit test suite (14 tests)
python -m unittest discover tests/
```
