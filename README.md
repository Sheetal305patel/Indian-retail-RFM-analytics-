# 🇮🇳 Indian Retail Customer Value & RFM Segmentation Engine
### Omnichannel Behavioral Analytics, Unit Economics & Predictive ML for the Indian Consumer Market

![Python 3.11](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white)

> **Author:** Sheetal Patel ([sheetalpatel8603@gmail.com](mailto:sheetalpatel8603@gmail.com))  
> **Market Focus:** 100% Indian Domestic Retail & D2C (Currency: Native ₹ INR)  
> **Industry Benchmarks:** Tata Neu / Tata Consumer Products, Reliance Retail / Ajio, Nykaa (FSN E-Commerce), Hindustan Unilever (HUL), ITC Limited

---

## 📌 Why I Built This Project

Most customer segmentation and RFM repositories on GitHub use outdated, toy datasets (like the 2010 UK Online Retail dataset) with simple dollar amounts and pure credit-card e-commerce assumptions. They completely ignore the commercial unit economics of fast-growing consumer markets like India.

In reality, running consumer analytics for companies like **Tata Neu, Reliance Ajio, or Nykaa** presents unique challenges:
1. **Cash on Delivery (COD) & RTO Logistics Bleed:** ~28% of Indian D2C orders are placed via COD, with a 20–25% **Return-to-Origin (RTO)** delivery bounce rate. Forward + reverse courier charges (₹140/order via Delhivery/Blue Dart) wipe out margins if not accounted for.
2. **UPI Dominance vs Payment Gateways:** UPI drives ~58% of digital transactions at 0% gateway fees, compared to 1.8% fees on credit/debit cards.
3. **Omnichannel Identity Fragmentation:** Consumers browse on D2C mobile apps, purchase via Quick Commerce (Blinkit/Zepto), and walk into physical retail stores (e.g., Nykaa Luxe, Reliance Smart, Westside).
4. **WhatsApp-First CRM vs Email:** In India, email marketing open rates linger below 15%, whereas WhatsApp marketing achieves 80%+ read rates—demanding strict compliance with **TRAI DND (Do Not Disturb)** regulations and India's **Digital Personal Data Protection (DPDP) Act**.

I designed and engineered this repository to provide a **complete, production-grade, end-to-end analytics platform** that models these exact commercial dynamics from scratch.

---

## 🏗️ Architecture & Data Pipeline

```
                                  OMNICHANNEL DATA SOURCES
   [ D2C Mobile App ]      [ D2C Webstore ]      [ Quick Commerce ]      [ Offline Store POS ]
            │                     │                      │                       │
            └─────────────────────┴──────────┬───────────┴───────────────────────┘
                                             ▼
                             [ Identity Resolution Engine ]
                        Cross-channel token stitching & Phone/Loyalty ID
                        (Segregates anonymous offline walk-ins: ~6% NMV)
                                             │
                                             ▼
                               [ Clean Curation & ETL ]
                     • Exclude Cancelled, Test, & Fraud orders
                     • Deduct Partial Returns & RTO Bounces
                     • Derive Net Merchandise Value (NMV) in ₹ INR
                     • Calculate Contribution Margin (CM2): Deduct COGS,
                       Gateway Fees & 3PL Reverse Logistics Penalties
                                             │
                                             ▼
                               [ Behavioral RFM Engine ]
                     • Rolling 12-Month Observation Window
                     • Percentile Quintile Scoring (1 to 5) with Tie-Breaking
                     • Assignment into 8 Commercial Lifecycle Segments
                                             │
                        ┌────────────────────┴────────────────────┐
                        ▼                                         ▼
           [ PyTorch Predictive ML ]                  [ Real-Time Stream Bus ]
     • 90-Day Neural Churn Classifier             • Event-driven SSE Order Ticker
     • Forward 12M pLTV Value Forecasting         • Dynamic RFM State Updates
     • Strategic 4-Quadrant Matrix                • Instant Segment Promotion Alerts
                        │                                         │
                        └────────────────────┬────────────────────┘
                                             ▼
                             [ Validation & Audit Engine ]
                        Automated 10-Point Acceptance Checklist
                        Reconciles Source GMV ➔ NMV with 0% Discrepancy
                                             │
                                             ▼
                             [ CRM Activation & Reporting ]
                     • Consent-filtered WhatsApp, SMS, & Email Feeds
                     • Randomized 10% Holdout Control Split Generator
                     • A/B Hypothesis Testing & Incremental Margin Lift
                     • Flask Interactive Dashboard & Customer 360
```

---

## ⚡ Key Engineering & Analytics Highlights

### 1. Robust Financial Accounting in INR (₹)
* **Gross Merchandise Value (GMV):** Total top-line order value before cancellations and returns.
* **Net Merchandise Value (NMV):**
  $$\text{NMV} = \text{GMV} - \text{Discounts} - \text{Refunds/Returns}$$
* **Contribution Margin 2 (CM2):**
  $$\text{CM2} = \text{NMV} - \text{Product COGS} - \text{Gateway Fees} - \text{3PL Courier RTO Losses}$$
* **RTO Bounces:** 1,355 failed COD deliveries cleanly segregated; logistics cost burn of **₹189,700.00** subtracted directly from gross margin rather than being swept under the rug.

### 2. Empirical Percentile Tie-Breaking (No Arbitrary Binning)
In commercial retail, massive clusters of customers share identical frequency ($F=1$ purchase) or zero recent spend. Standard `pd.qcut` throws duplicate bin edge errors or splits customers with identical behavior into different tiers.
* My implementation uses **`rank(method='min', pct=True)`**:
  * Customers with $F=0$ are strictly anchored to Score 1.
  * Customers with $F=1$ receive the identical fair percentile score.
  * Spend $\le ₹0$ is anchored to Score 1.

### 3. Deep Learning Churn Classifier (PyTorch)
* Multi-layer neural network with Dropout, Batch Normalization, and Binary Cross-Entropy loss optimized via Adam.
* **Engineered Features:** Recency days, inter-purchase interval, order velocity (orders per 90 days), discount sensitivity ratio, return rate, and omnichannel breadth.
* Outputs calibrated churn probabilities (0–100%) mapped into 4 risk tiers: **Critical, High, Medium, and Low**.

### 4. Forward 12-Month Expected Lifetime Value (pLTV)
* Computes expected future 12-month net spend and contribution margin based on historical AOV, retention probability, and buying cadence.
* Categorizes customers into 4 Strategic Action Quadrants:
  1. **Protect VIPs:** High value + High churn risk (immediate concierge retention).
  2. **Nurture Champions:** High value + Low churn risk (loyalty perks, early access).
  3. **Growth & Upsell:** Low value + Low churn risk (cross-sell, basket size expansion).
  4. **Re-engage / Divest:** Low value + High churn risk (automated discount nudge or ad suppression).

### 5. Low-Latency Real-Time Streaming Engine
* Implements an in-memory streaming event bus with Server-Sent Events (SSE).
* When a customer places an order, the engine incrementally recalculates their recency, frequency, and monetary scores in sub-milliseconds without recalculating the entire batch database.
* Detects when a customer crosses segment thresholds (e.g., promoted from *Promising* $\rightarrow$ *Loyal Customers*) and dispatches real-time webhooks.

### 6. Automated 10-Point Acceptance Checklist
A built-in audit engine validates all 10 criteria specified in enterprise segmentation blueprints:
```
[PASS] CHK_01: Financial Reconciliation (Raw Net Sales strictly matches Curated Net Sales)
[PASS] CHK_02: Exclusion Integrity (Zero qualifying orders from Cancelled, Test, or Fraud)
[PASS] CHK_03: Refund Accounting (Fully refunded & RTO orders carry zero frequency weight)
[PASS] CHK_04: Temporal Bounds (Zero future transactions; zero negative recency values)
[PASS] CHK_05: Customer Deduplication (Zero duplicate IDs in customer master table)
[PASS] CHK_06: Anonymous Quantification (Anonymous store POS walk-ins tracked separately: ₹2.83M)
[PASS] CHK_07: Segment Completeness (100% of customer base mapped; 0 unassigned)
[PASS] CHK_08: RFM Summation Reconciliation (Customer RFM sum == qualifying order sales)
[PASS] CHK_09: PII Separation (Analytical tables strictly exclude email, phone, and name)
[PASS] CHK_10: Sample Reproducibility (100% calculation match across audit spot-checks)
```

---

## 📊 The 8 Actionable Lifecycle Segments

| Segment | RFM Range | Indian Retail Behavior | Prescribed Strategy |
| :--- | :---: | :--- | :--- |
| **Champions** | `555, 554, 545` | Recent, frequent, highest spenders | Early festive access (Diwali/Big Billion), Tata Neu Coins / Ajio Luxe perks. |
| **Loyal Customers** | `344, 434, 443` | Steady repeat purchasers across recent quarters | WhatsApp replenishment alerts, category cross-sell, bundle discounts. |
| **High-Value, At Risk** | `155, 244, 255` | High historical spenders drifting away ($R \ge 120\text{d}$) | Direct WhatsApp concierge win-back, high-value personalized coupon. |
| **Recent Customers** | `511, 512, 411` | First-time buyers within 60-day onboarding | Welcome onboarding drip series, 2nd-order incentive within 21 days. |
| **Promising** | `422, 523, 423` | Recent buyers with early repeat signals | Category discovery recommendations, nudge to pay via UPI (avoid COD). |
| **Need Attention** | `332, 323, 333` | Average spenders slipping past normal repurchase window | Timely replenishment reminder, "We Miss You" reactivation offer. |
| **Lapsed** | `111, 112, 121` | Inactive for >180 days | Low-cost WhatsApp/SMS test; suppress from expensive ad retargeting. |
| **One-Time / Low-History** | `211, 311` | Single purchase outside onboarding window | Check delivery experience, offer second-purchase welcome back coupon. |

---

## 🖥️ Interactive Web Dashboard

The project includes a web dashboard built with Flask, Tailwind CSS, and Chart.js:

* **Executive View (`/executive`):** Net revenue in ₹ INR, profit contribution margin, COD vs Prepaid breakdown, RTO courier loss tracker, and Metro vs Tier 2 vs Tier 3 Bharat volume.
* **Predictive ML Cockpit (`/predictive`):** Interactive 4-quadrant scatter chart, churn risk breakdown, and table of high-value VIPs requiring immediate retention.
* **Live Event Stream (`/streaming`):** Real-time event ticker with live revenue counter, SSE connection, and simulated event injector.
* **CRM Activation Hub (`/crm`):** Channel eligibility counts (WhatsApp, SMS, Email), production audience file exporter with 10% holdouts, and A/B campaign lift simulator with two-proportion z-tests.
* **Analyst & Audit Room (`/analyst`):** Recency, Frequency, and Monetary distribution histograms, tie-breaking documentation, and live 10-point audit checklist.
* **Customer 360 Lookup (`/customer-lookup?id=IND-CUST-00001`):** Complete behavioral card, RFM scores, churn risk %, forward pLTV spend, and transaction ledger.

---

## 🚀 Quickstart & How to Run

### 1. Prerequisites & Setup
Clone the repository and install dependencies:
```bash
# Clone the repository
git clone https://github.com/Sheetal305patel/Indian-retail-RFM-analytics-.git
cd Indian-retail-RFM-analytics-

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate      # On Windows
# source venv/bin/activate  # On Linux/macOS

# Install dependencies
pip install -r requirements.txt
```

### 2. Run the Complete Data & ML Pipeline
Execute the end-to-end pipeline (generates 20,000 transactions, runs identity resolution, curates orders, calculates RFM, trains PyTorch models, executes validation audit, and exports audiences):
```bash
python cli.py run-all
```

### 3. Launch the Interactive Web Dashboard
```bash
python cli.py serve --port 5000
```
Open **`http://127.0.0.1:5000`** in your browser to view the application.

### 4. CLI Power Commands
```bash
# Score RFM segments and view distribution table
python cli.py score-rfm

# Train the PyTorch neural churn classifier & calculate pLTV
python cli.py train-ml

# Simulate real-time streaming order events with dynamic transitions
python cli.py stream-events --events 20 --interval 0.3

# Run the automated 10-point audit reconciliation
python cli.py validate

# Run the complete test suite (14 unit tests)
python -m unittest discover tests/
```

---

## 📂 Repository Structure

```
├── config/
│   └── settings.py              # Business thresholds, observation windows, payment dynamics
├── src/
│   ├── data_generator.py        # Indian consumer data generator (4k users, 20k orders in ₹ INR)
│   ├── identity_resolution.py   # Cross-channel customer stitching & anonymous POS audit
│   ├── etl_pipeline.py          # Data curation, RTO handling, NMV & CM2 derivation
│   ├── rfm_engine.py            # R/F/M quintile scoring (1-5), tie resolution, 8 segments
│   ├── predictive_models.py     # PyTorch Neural Churn Classifier & forward 12M pLTV
│   ├── streaming_pipeline.py    # In-memory real-time event bus with online state updates
│   ├── validation.py            # Automated 10-point financial reconciliation audit
│   ├── campaign_engine.py       # DPDP/TRAI-aware audience exporter with holdouts
│   └── pilot_measurement.py     # A/B test analyzer: incremental margin, conversion lift
├── web/
│   ├── app.py                   # Flask backend with SSE streaming & REST endpoints
│   ├── static/css/style.css     # Dark-mode styling
│   └── templates/               # 7 responsive Tailwind CSS dashboard templates
├── tests/                       # 14 unit tests covering ETL, scoring, ML, and validation
├── cli.py                       # CLI interface powered by Click and Rich
├── RECRUITER_GUIDE.md           # Interview cheat sheet & technical talking points
├── RUNBOOK.md                   # Operations runbook & production triage SOPs
└── requirements.txt             # PyTorch, Pandas, Flask, Click, Rich, etc.
```

---

## 🧪 Unit Tests

The test suite covers ETL curation rules, zero-frequency full refund enforcement, percentile tie handling, privacy PII separation, streaming state transitions, and neural network output shapes:

```bash
python -m unittest discover tests/
```
```
..............
----------------------------------------------------------------------
Ran 14 tests in 0.087s

OK
```

---

## 👤 Author & Contact

**Sheetal Patel**  
* **Email:** [sheetalpatel8603@gmail.com](mailto:sheetalpatel8603@gmail.com)  
* **GitHub:** [@Sheetal305patel](https://github.com/Sheetal305patel)  
* **LinkedIn:** [Sheetal Patel](https://www.linkedin.com/) *(Add your LinkedIn URL)*

---

*⭐ If you find this project insightful, feel free to star the repository!*
