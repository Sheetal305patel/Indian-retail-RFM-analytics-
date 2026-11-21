# 🇮🇳 Indian Retail Customer Value & RFM Segmentation Engine
### Omnichannel Behavioral Analytics, Unit Economics & Predictive Machine Learning for the Indian Consumer Market

![Python 3.11](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python&logoColor=white)
![PyTorch](https://img.shields.io/badge/PyTorch-Deep%20Learning-EE4C2C?style=flat-square&logo=pytorch&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-Web%20Dashboard-000000?style=flat-square&logo=flask&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-Modern%20UI-38B2AC?style=flat-square&logo=tailwind-css&logoColor=white)
![Audit Status](https://img.shields.io/badge/10--Point%20Audit-100%25%20Passed-10b981?style=flat-square)
![Tests](https://img.shields.io/badge/Unit%20Tests-14%2F14%20Passed-10b981?style=flat-square)

> **Author:** Sheetal Patel &bull; [GitHub (@Sheetal305patel)](https://github.com/Sheetal305patel) &bull; [Email](mailto:sheetalpatel8603@gmail.com)  
> **Market Focus:** 100% Indian Domestic Retail & D2C &bull; **Currency:** Indian Rupee (₹ INR)  
> **Industry Benchmarks:** Tata Neu / Tata Consumer Products &bull; Reliance Retail / Ajio &bull; Nykaa (FSN E-Commerce) &bull; Hindustan Unilever (HUL) &bull; ITC Limited

---

## ⚡ Executive Summary: At a Glance

| Metric | Production Dataset Result | Commercial Context |
| :--- | :--- | :--- |
| **Analyzed Customers** | **4,000** Consumers | Metro (45%), Tier 2 (35%), Tier 3 Bharat (20%) |
| **Ingested Orders** | **20,000** Transactions | D2C App (48%), D2C Web (28%), POS Store (18%), Quick Commerce (6%) |
| **Gross Value (GMV)** | **₹60,615,657.00** | Top-line merchandise demand before returns and cancellations |
| **Net Sales (NMV)** | **₹46,653,440.25** | $\text{GMV} - \text{Discounts} - \text{Customer Refunds}$ |
| **COD RTO Bounced** | **1,355 orders (23.9% of COD)** | **₹189,700.00** logistics cost burn deducted from gross margins |
| **Payment Breakdown** | **UPI: 58%** (0% fee) &bull; **COD: 28%** | Credit/Debit Cards: 10% (1.8% fee) &bull; NetBanking: 4% |
| **ML Churn Accuracy** | **PyTorch Neural Classifier** | 90-day churn likelihood + forward 12M pLTV forecasting |
| **Audit Verification** | **10 / 10 Checks Passed** | Automated financial reconciliation with 0% discrepancy |

---

## 📖 Table of Contents
- [Why I Built This Project](#-why-i-built-this-project)
- [Architecture & System Flow](#-architecture--system-flow)
- [Commercial Unit Economics in ₹ INR](#-commercial-unit-economics-in--inr)
- [RFM Methodology & Empirical Tie-Breaking](#-rfm-methodology--empirical-tie-breaking)
- [Predictive ML: Churn Propensity & pLTV](#-predictive-ml-churn-propensity--pltv)
- [The 8 Lifecycle Segments](#-the-8-lifecycle-segments)
- [Interactive Dashboard Tour](#-interactive-dashboard-tour)
- [Automated 10-Point Acceptance Audit](#-automated-10-point-acceptance-audit)
- [Quickstart: Run in 3 Steps](#-quickstart-run-in-3-steps)
- [Testing & Code Quality](#-testing--code-quality)
- [Author & Contact](#-author--contact)

---

## 🎯 Why I Built This Project

Most customer segmentation projects online use textbook datasets (such as the 2010 UK Online Retail dataset) with generic dollar amounts, simple credit-card checkouts, and zero returns logic. They completely fail to reflect the commercial unit economics of high-growth retail markets like India.

When building analytics for consumer giants like **Tata Neu, Reliance Ajio, or Nykaa**, four real-world factors make or break profitability:

1. **Cash on Delivery (COD) Logistics Loss:** Cash on Delivery accounts for ~28% of Indian D2C orders and carries an authentic **20–25% Return-to-Origin (RTO)** bounce rate. Forward + reverse courier charges (~₹140/order via Delhivery/Blue Dart) create true negative margins on bounced packages.
2. **Zero-Fee UPI vs Gateway Costs:** UPI drives ~58% of digital checkouts at 0% processing fee, whereas Cards charge ~1.8%.
3. **Omnichannel Identity Resolution:** Modern Indian consumers browse on D2C apps, order daily groceries via Quick Commerce (Blinkit/Zepto), and shop at physical offline stores (Reliance Smart, Nykaa Luxe, Westside).
4. **WhatsApp-First Marketing:** With Indian email open rates below 15% and WhatsApp read rates above 80%, CRM activation must be WhatsApp-first while strictly adhering to India's **Digital Personal Data Protection (DPDP) Act** and **TRAI DND** regulations.

I engineered this project to provide a **reproducible, enterprise-grade analytics engine** that solves these real commercial problems.

---

## 🏗️ Architecture & System Flow

<details open>
<summary><b>Click to expand / collapse Architecture Diagram</b></summary>

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                             OMNICHANNEL DATA INGESTION                            │
│    D2C Mobile App (48%)  •  D2C Webstore (28%)  •  Quick Commerce (6%)  •  POS (18%) │
└────────────────────────────────────────┬─────────────────────────────────────────┘
                                         ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│                         IDENTITY RESOLUTION ENGINE                                │
│   • Phone Number & Loyalty ID Graph Stitching across web, app, and store POS     │
│   • Quantifies & segregates anonymous store walk-ins (~6% of total revenue)      │
└────────────────────────────────────────┬─────────────────────────────────────────┘
                                         ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│                           CURATION & ETL PIPELINE                                │
│   • Filters Cancelled, Test, and Fraudulent orders                               │
│   • Enforces Zero-Frequency weight on full refunds and RTO bounces               │
│   • Net Merchandise Value: NMV = Gross Sales - Discounts - Refunds               │
│   • Contribution Margin (CM2): Deducts COGS, Gateway Fees, & 3PL Courier Losses  │
└────────────────────────────────────────┬─────────────────────────────────────────┘
                                         ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│                        BEHAVIORAL RFM SCORING ENGINE                             │
│   • Rolling 365-Day Observation Window                                           │
│   • Percentile Quantiles (1 to 5) with Empirical Tie-Breaking (No arbitrary bin) │
│   • Assignment into 8 Commercial Lifecycle Segments                              │
└───────────────────┬──────────────────────────────────────────┬───────────────────┘
                    ▼                                          ▼
┌──────────────────────────────────────┐   ┌───────────────────────────────────────┐
│     PYTORCH PREDICTIVE ML ENGINE     │   │      REAL-TIME STREAMING BUS          │
│ • 90-Day Neural Churn Classifier     │   │ • Sub-millisecond incremental state   │
│ • Forward 12M pLTV Forecasting       │   │ • Dynamic RFM & live segment updates  │
│ • Strategic 4-Quadrant Action Matrix │   │ • Server-Sent Events (SSE) Web Ticker │
└───────────────────┬──────────────────┘   └───────────────────┬───────────────────┘
                    └─────────────────────┬────────────────────┘
                                          ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│                     VALIDATION & 10-POINT FINANCIAL AUDIT                        │
│   • Reconciles Source GMV ➔ Curated NMV with 0% discrepancy                      │
│   • Enforces PII Isolation: Analytical tables strictly exclude direct contacts   │
└────────────────────────────────────────┬─────────────────────────────────────────┘
                                         ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│                      CRM ACTIVATION & INTERACTIVE DASHBOARD                      │
│   • WhatsApp / SMS / Email feeds with randomized 10% holdout control groups      │
│   • A/B Pilot Lift Simulator with two-proportion z-tests and incremental margin  │
│   • Flask Interactive Dashboard: Executive, ML, Stream, CRM, Audit, Customer 360 │
└──────────────────────────────────────────────────────────────────────────────────┘
```
</details>

---

## 💰 Commercial Unit Economics in ₹ INR

Unlike textbook setups that only track top-line revenue, this pipeline computes three distinct profit tiers:

```
Gross Merchandise Value (GMV): ₹60,615,657.00
  ├── Promotional Discounts:   - ₹6,245,190.40
  └── Customer Refunds:        - ₹7,717,026.35
      ═════════════════════════════════════════════════
      = Net Merchandise Value (NMV): ₹46,653,440.25
        ├── Product COGS:           - ₹22,393,651.30
        ├── Payment Gateway Fees:   - ₹261,259.20  (0% UPI, 1.8% Cards)
        └── 3PL RTO Courier Losses: - ₹189,700.00  (₹140 loss on 1,355 bounced COD orders)
            ═════════════════════════════════════════════════
            = Contribution Margin 2 (CM2): ₹23,808,829.75 (51.0% Margin Ratio)
```

> **Why this matters in interviews:** Many data analysts mistakenly give frequency credit to bounced COD orders or ignore reverse logistics costs. Our engine explicitly segregates RTO bounces from active buyer frequency and penalizes the courier burn against contribution margin.

---

## 📐 RFM Methodology & Empirical Tie-Breaking

Standard `pd.qcut` fails in retail because huge numbers of customers share identical frequency (e.g. exactly 1 purchase) or zero recent spend, causing bin-edge collision errors or arbitrary bin splitting.

Our scoring engine solves this using **`rank(method='min', pct=True)`**:

```python
# Recency (R): Inverted rank so fewest days since last purchase earns Score 5
r_pct = df["recency_days"].rank(method="min", ascending=True, pct=True)
df["r_score"] = pd.cut(r_pct, bins=[-np.inf, 0.20, 0.40, 0.60, 0.80, np.inf], labels=[5, 4, 3, 2, 1])

# Frequency (F): Inactive customers (F=0) anchored to 1; one-time buyers share fair percentile
df["f_score"] = pd.cut(f_ranks, bins=[-np.inf, 0.40, 0.65, 0.82, 0.93, np.inf], labels=[1, 2, 3, 4, 5])
df.loc[df["frequency"] == 0, "f_score"] = 1

# Monetary (M): Spend <= 0 strictly anchored to Score 1
df["m_score"] = pd.cut(m_ranks, bins=[-np.inf, 0.25, 0.50, 0.70, 0.88, np.inf], labels=[1, 2, 3, 4, 5])
df.loc[df["monetary_inr"] <= 0, "m_score"] = 1
```

---

## 🤖 Predictive ML: Churn Propensity & pLTV

Moving beyond historical RFM, the platform integrates two predictive machine learning models:

### 1. PyTorch Deep Neural Churn Classifier
* **Architecture:** 3-layer Feedforward Net (Linear $\rightarrow$ BatchNorm $\rightarrow$ ReLU $\rightarrow$ Dropout(0.2) $\rightarrow$ Sigmoid) trained via BCE Loss and Adam optimizer.
* **Engineered Features:** Recency days, order velocity (orders per 90-day cycle), average inter-purchase interval, discount sensitivity ratio, return rate, and channel diversity.
* **Output:** Predicts 90-day churn probability (0–100%) mapped to risk tiers: **Critical (>70%)**, **High (50–70%)**, **Medium (30–50%)**, and **Low (<30%)**.

### 2. Forward 12-Month Customer Lifetime Value (pLTV)
* Forecasts expected 12-month net spend and contribution margin based on retention probability, historical AOV, and repurchase cadence.
* Maps every customer into the **Strategic 4-Quadrant Action Matrix**:

```
      ▲ High
      │   [ PROTECT & RETAIN VIPs ]          [ NURTURE CHAMPIONS ]
      │   High Spend + High Churn Risk       High Spend + Low Churn Risk
      │   ➜ Concierge Win-back, Direct Call  ➜ Early VIP Access, Loyalty Multipliers
pLTV  │─────────────────────────────────────────────────────────────────────────────
Spend │   [ RE-ENGAGE OR DIVEST ]            [ GROWTH & UPSELL ]
      │   Low Spend + High Churn Risk        Low Spend + Low Churn Risk
      │   ➜ Low-cost SMS, Suppress Paid Ads  ➜ Cross-sell, Category Discovery
      ▼ Low
         Low ◄───────────────────────────────► High
                         90-Day Churn Risk
```

---

## 👥 The 8 Lifecycle Segments

| Segment | RFM Code Range | Share | Typical Profile | Commercial Action Plan |
| :--- | :---: | :---: | :--- | :--- |
| **🏆 Champions** | `555, 554, 545` | 16.4% | Highest spenders, recent & frequent | Exclusive festival early access (Diwali/Big Billion), Tata Neu Coins / Ajio Luxe benefits. |
| **⭐ Loyal Customers** | `344, 434, 443` | 12.6% | Consistent repeat buyers across quarters | WhatsApp replenishment alerts, category cross-sell, bundle incentives. |
| **🚨 High-Value, At Risk** | `155, 244, 255` | 1.2% | High historical spenders slipping away ($R > 120\text{d}$) | Proactive WhatsApp outreach, bespoke win-back coupon, priority care survey. |
| **🌱 Recent Customers** | `511, 512, 411` | 6.9% | First-time buyers within 60-day onboarding | Welcome drip series, product guide, 2nd-order incentive within 21 days. |
| **🚀 Promising** | `422, 523, 423` | 7.0% | Recent buyers with early repeat signals | Category discovery recommendations, nudge to pay via UPI (to avoid COD). |
| **⚠️ Need Attention** | `332, 323, 333` | 6.2% | Value buyers drifting past average reorder cycle | Timely replenishment reminder, tailored "We Miss You" offer. |
| **💤 Lapsed** | `111, 112, 121` | 45.2% | Inactive for >180 days | Low-cost digital reactivation test; suppress from expensive paid ad audiences. |
| **🏷️ One-Time / Low-History** | `211, 311` | 4.6% | Single order outside onboarding window | Light-touch nurture, delivery satisfaction check, 2nd purchase coupon. |

---

## 🖥️ Interactive Dashboard Tour

The repository includes a web dashboard built with **Flask**, **Tailwind CSS**, and **Chart.js**:

| View Name | Route | What It Delivers |
| :--- | :--- | :--- |
| **Executive View** | `/executive` | Net revenue in ₹ INR, margin ratio, COD vs Prepaid breakdown, RTO courier loss card, and Metro vs Tier 2 vs Tier 3 distribution. |
| **Predictive ML** | `/predictive` | Interactive 4-quadrant scatter matrix, 90-day churn risk tiers, forward 12M pLTV forecast, and VIPs at Risk table. |
| **Live Stream** | `/streaming` | Real-time SSE order ticker, dynamic RFM score transitions, live segment promotion alerts, and manual event injector. |
| **CRM Activation** | `/crm` | WhatsApp and SMS channel eligibility tables, audience exporter with 10% holdout splits, and A/B pilot lift simulator with z-tests. |
| **Analyst Audit** | `/analyst` | R, F, and M distribution histograms, documented percentile tie rules, and automated 10-point audit checklist. |
| **Customer 360** | `/customer-lookup?id=IND-CUST-00001` | Customer profile card, behavioral RFM score, churn risk %, pLTV forecast, and 15-order transaction ledger. |

---

## ✅ Automated 10-Point Acceptance Audit

Built directly into `src/validation.py` to ensure complete accounting and data integrity:

```
[PASS] CHK_01: Financial Reconciliation (Raw Net Sales strictly equals Curated Net Sales: ₹46.65M)
[PASS] CHK_02: Exclusion Integrity (Zero qualifying orders from Cancelled, Test, or Fraud)
[PASS] CHK_03: Refund Accounting (Zero frequency weight assigned to fully refunded & RTO orders)
[PASS] CHK_04: Temporal Integrity (Zero future orders; zero negative recency values)
[PASS] CHK_05: Customer Deduplication (Zero duplicate IDs in customer master table)
[PASS] CHK_06: Anonymous Quantification (Anonymous store POS walk-ins tracked: ₹2,835,873.90)
[PASS] CHK_07: Segment Completeness (100% of customer base assigned across all 8 segments)
[PASS] CHK_08: RFM Summation Reconciliation (Customer RFM sales sum strictly equals curated sales)
[PASS] CHK_09: PII Separation (Analytical tables strictly exclude email, phone, and name)
[PASS] CHK_10: Sample Reproducibility (100% calculation match across audit spot-checks)
```

---

## 🚀 Quickstart: Run in 3 Steps

### Step 1: Clone & Setup Environment
```bash
git clone https://github.com/Sheetal305patel/Indian-retail-RFM-analytics-.git
cd Indian-retail-RFM-analytics-

# Create virtual environment
python -m venv venv
venv\Scripts\activate      # On Windows
# source venv/bin/activate  # On macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Execute the End-to-End Pipeline
Generates 20,000 Indian transactions, runs identity resolution, curates orders, calculates RFM, trains PyTorch models, executes validation audit, and exports audiences:
```bash
python cli.py run-all
```

### Step 3: Launch the Interactive Web Dashboard
```bash
python cli.py serve --port 5000
```
Open **`http://127.0.0.1:5000`** in your browser to explore the dashboard.

---

## 🛠️ CLI Power Commands

```bash
# Score RFM segments and view terminal table
python cli.py score-rfm

# Train PyTorch neural churn classifier & pLTV model
python cli.py train-ml

# Simulate real-time streaming order events
python cli.py stream-events --events 15 --interval 0.3

# Run automated 10-point audit reconciliation
python cli.py validate

# Run unit tests
python -m unittest discover tests/
```

---

## 🧪 Testing & Code Quality

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

## 📂 Repository Structure

```
├── config/
│   └── settings.py              # Business rules, observation window (365d), Indian benchmarks
├── src/
│   ├── data_generator.py        # 4,000 users, 20,000 orders in ₹ INR across Metro/Tier 2/Tier 3
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
│   ├── static/css/style.css     # Dark-mode executive styling
│   └── templates/               # 7 responsive Tailwind CSS dashboard templates
├── tests/                       # 14 unit tests covering ETL, scoring, ML, and validation
├── cli.py                       # CLI interface powered by Click and Rich
├── RECRUITER_GUIDE.md           # Interview cheat sheet & technical talking points
├── RUNBOOK.md                   # Operations runbook & production triage SOPs
└── requirements.txt             # PyTorch, Pandas, Flask, Click, Rich, etc.
```

---

## 👤 Author & Contact

**Sheetal Patel**  
* **GitHub:** [@Sheetal305patel](https://github.com/Sheetal305patel)  
* **Email:** [sheetalpatel8603@gmail.com](mailto:sheetalpatel8603@gmail.com)  
* **Project Repository:** [Indian-retail-RFM-analytics-](https://github.com/Sheetal305patel/Indian-retail-RFM-analytics-)

---

*⭐ If you find this project insightful, feel free to star the repository!*
