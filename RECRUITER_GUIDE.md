# Recruiter & Hiring Manager Interview Guide
## Customer Value, RFM Segmentation & Predictive ML in Real-World Retail (India, US & UK)

> **Role Relevance:** Senior Data Analyst, Analytics Engineer, Commercial Data Scientist, Retention / CRM Product Manager.  
> **Business Scope:** ₹250Cr+ / \$30M+ Omnichannel Retailer operating across **India (55%)**, **United States (30%)**, and **United Kingdom (15%)**.

---

## 1. The 60-Second Executive Pitch (How to Introduce the Project)

> *"In this project, I built an end-to-end commercial customer value and retention engine for an omnichannel brand operating across India, the US, and the UK. Rather than treating customer segmentation as a toy academic exercise with synthetic clustering, I focused on real retail unit economics:*
> 1. *Handling the **Cash on Delivery (COD) Return-To-Origin (RTO)** crisis in Indian e-commerce, which typically eats 20–25% of gross orders in logistics waste.*
> 2. *Eliminating arbitrary quantile binning failures where massive clusters of one-time buyers break standard quintile scoring.*
> 3. *Deploying a **PyTorch Neural Churn Propensity model** and forward 12-month **predictive Lifetime Value (pLTV)** to classify customers into a 4-quadrant strategic matrix (e.g. Protect VIPs vs Re-engage).*
> 4. *Building a **real-time event streaming pipeline** with Server-Sent Events (SSE) that recalculates customer recency and promotes customers dynamically without batch downtime.*
> 5. *Enforcing a **10-point automated financial reconciliation audit** to guarantee that analytical totals match finance books to within \$0.05 while keeping PII strictly segregated for DPDP Act (India), GDPR (UK), and CCPA (US) compliance.*
> *This enables marketing and CRM teams to measure true incremental contribution margin using randomized holdout control groups rather than relying on vanity gross revenue."*

---

## 2. Top 5 Real-World Commercial Problems & Your Solutions

### Problem 1: The Indian E-Commerce COD & RTO Crisis
- **The Reality:** In India, Cash on Delivery accounts for ~25-30% of D2C orders, but carries a brutal **24% Return-To-Origin (RTO)** rate where delivery fails or is rejected at the doorstep.
- **The Pitfall:** Naive data science pipelines count all order attempts as "Frequency" and "Gross Sales", inflating the perceived value of chronic RTO buyers.
- **Your Engineering Solution:**
  - Designed an explicit transaction filter in the ETL pipeline ([`src/etl_pipeline.py`](file:///C:/Users/sheet/.gemini/antigravity/scratch/customer-rfm-segmentation/src/etl_pipeline.py)) that classifies RTO orders as non-qualifying and zeroes out their monetary contribution.
  - Built targeted CRM campaign feeds ([`src/campaign_engine.py`](file:///C:/Users/sheet/.gemini/antigravity/scratch/customer-rfm-segmentation/src/campaign_engine.py)) that incentivize high-risk COD buyers to switch to prepaid UPI with a 5% instant discount on their second purchase, immediately eliminating reverse logistics losses.

### Problem 2: Quantile Bin Splitting Failure (The "Tie Problem" in Retail)
- **The Reality:** In retail, 60–70% of customer accounts have placed exactly 1 order in the rolling 12-month window.
- **The Pitfall:** Running standard pandas `pd.qcut(df['frequency'], 5)` throws `ValueError: Bin edges must be unique` or randomly places two identical 1-order customers into different score tiers (e.g. one in Score 1 and one in Score 2).
- **Your Engineering Solution:**
  - Implemented empirical percentile ranking with minimum rank tie-handling: `rank(method='min', pct=True)` in [`src/rfm_engine.py`](file:///C:/Users/sheet/.gemini/antigravity/scratch/customer-rfm-segmentation/src/rfm_engine.py).
  - Explicitly anchored zero-order accounts to Score 1 and calibrated continuous score thresholds so customers with identical purchase history receive the exact same fair score bucket.

### Problem 3: Omnichannel Identity Attribution (Store POS vs D2C Web/App)
- **The Reality:** Offline experience stores and pop-up locations generate substantial revenue, but a significant portion of in-store checkouts are anonymous (cash or quick POS scan without loyalty phone lookup).
- **The Pitfall:** Forcing anonymous POS orders into synthetic customer profiles corrupts lifetime value distributions.
- **Your Engineering Solution:**
  - Built an Identity Resolution Engine ([`src/identity_resolution.py`](file:///C:/Users/sheet/.gemini/antigravity/scratch/customer-rfm-segmentation/src/identity_resolution.py)) that stitches known digital accounts (Web, App, Loyalty Cards, Guest cookies) while explicitly segregating anonymous in-store POS revenue ($9.79\%$ of gross sales).
  - Provided leadership with an **Identity Revenue Coverage Rate** metric ($90.21\%$) to track loyalty phone capture effectiveness across retail stores.

### Problem 4: Margin Erosion from Blind Discounting
- **The Reality:** Retailers bleed millions by blasting 20% off coupons to "Champions" and "Loyal Customers" who would have purchased anyway at full margin.
- **The Pitfall:** Evaluating campaign success by gross attributed revenue hides the reality that discount costs wiped out contribution margin.
- **Your Engineering Solution:**
  - Built an A/B Pilot Lift Simulator ([`src/pilot_measurement.py`](file:///C:/Users/sheet/.gemini/antigravity/scratch/customer-rfm-segmentation/src/pilot_measurement.py)) that enforces a randomized **10% Holdout Control Group**.
  - Measures **True Incremental Contribution Margin** (Treatment Margin minus Control Margin after product costs, variable fulfillment, and return rates) tested with two-sample statistical significance ($z$-score, $p < 0.05$).

### Problem 5: Multi-Jurisdiction Privacy by Design
- **The Reality:** Direct marketing requires strict consent under the **DPDP Act 2023 / TRAI DND (India)**, **GDPR / UK ICO (UK)**, and **CCPA / CAN-SPAM (US)**.
- **The Pitfall:** Storing contact PII (first name, phone, email) inside analytical tables creates severe data compliance exposure.
- **Your Engineering Solution:**
  - Segment tables (`customer_rfm`, `customer_predictive_rfm`) store only pseudonymous keys (`customer_id`) and behavioral scores.
  - Direct contact details are stored in a physically separate protected identity store and joined only dynamically upon campaign export after filtering for active channel opt-ins (`whatsapp_opt_in`, `email_opt_in`) and suppressing hard opt-outs.

---

## 3. High-Impact Recruiter Q&A Cheat Sheet

#### Q1: "Why did you build both an RFM engine and a PyTorch ML Churn model?"
> *"RFM is deterministic, highly explainable, and ideal for commercial teams to set rules and campaign journeys. However, RFM is backward-looking—it tells you what a customer did in the past. My PyTorch Neural Churn model is forward-looking: it incorporates behavioral velocity (e.g. inter-purchase interval acceleration, discount sensitivity, channel diversity) to predict whether a customer will churn over the next 90 days. Combining both creates our **Strategic Action Quadrant**, allowing us to identify 'Protect VIPs'—customers who currently look like Champions on historical spend but whose purchasing frequency has started decelerating."*

#### Q2: "What is the difference between Gross Merchandise Value (GMV) and Net Merchandise Sales (NMV) in your system?"
> *"GMV is the gross checkout value before accounting for commercial reality. In our pipeline:*
> $$\text{Net Sales} = \text{Gross Merchandise Sales} - \text{Discounts} - \text{Refunds/Returns} - \text{Cancelled/RTO Orders}$$
> *Furthermore, we derive **Contribution Margin 1 & 2** by deducting unit Cost of Goods Sold (COGS) and estimated shipping/reverse courier losses, because evaluating customer value on revenue alone leads to acquiring high-gross, negative-margin return abusers."*

#### Q3: "How does the real-time event streaming pipeline work?"
> *"In production e-commerce, waiting for a monthly or daily batch ETL to refresh customer status causes stale targeting—a customer who just placed an order 5 minutes ago might still receive a 'We miss you' win-back email. Our stream engine (`RealTimeStreamEngine`) listens to incoming event payloads (`ORDER_COMPLETED`, `RETURN_ISSUED`). It increments order counts, updates cumulative spend, resets recency to 0, dynamically recalculates the RFM code, slashes churn probability, and emits a live segment promotion alert (e.g. promoting a customer from Recent to Loyal). This is streamed live to the UI via Server-Sent Events (SSE)."*

---

## 4. Architecture Summary Table

| Pipeline Layer | Python Module | Key Technical Capability |
| :--- | :--- | :--- |
| **Data Generation** | [`src/data_generator.py`](file:///C:/Users/sheet/.gemini/antigravity/scratch/customer-rfm-segmentation/src/data_generator.py) | 3,500 consumers across India (INR), US (USD), UK (GBP), COD RTO modeling, Pareto distributions. |
| **Identity Stitching** | [`src/identity_resolution.py`](file:///C:/Users/sheet/.gemini/antigravity/scratch/customer-rfm-segmentation/src/identity_resolution.py) | Cross-device/card mapping, separates anonymous store POS revenue ($9.8\%$). |
| **Commercial ETL** | [`src/etl_pipeline.py`](file:///C:/Users/sheet/.gemini/antigravity/scratch/customer-rfm-segmentation/src/etl_pipeline.py) | Filters cancelled/RTO orders, enforces full refund zero-frequency, derives contribution margin. |
| **RFM Scoring** | [`src/rfm_engine.py`](file:///C:/Users/sheet/.gemini/antigravity/scratch/customer-rfm-segmentation/src/rfm_engine.py) | Robust percentile tie-handling `rank(method='min', pct=True)`, 8 lifecycle segments. |
| **Predictive ML** | [`src/predictive_models.py`](file:///C:/Users/sheet/.gemini/antigravity/scratch/customer-rfm-segmentation/src/predictive_models.py) | PyTorch Neural Net churn classifier ($P(\text{churn}) \in [0, 1]$), forward 12M pLTV forecast. |
| **Stream Engine** | [`src/streaming_pipeline.py`](file:///C:/Users/sheet/.gemini/antigravity/scratch/customer-rfm-segmentation/src/streaming_pipeline.py) | Real-time incremental online state updates with Server-Sent Events (SSE). |
| **Validation Audit** | [`src/validation.py`](file:///C:/Users/sheet/.gemini/antigravity/scratch/customer-rfm-segmentation/src/validation.py) | 10-point automated reconciliation checklist ($\Delta < \$0.05$ threshold). |
| **CRM Activation** | [`src/campaign_engine.py`](file:///C:/Users/sheet/.gemini/antigravity/scratch/customer-rfm-segmentation/src/campaign_engine.py) | WhatsApp (India) & Email (US/UK) consent filters, randomized 10% holdout splits. |
| **A/B Pilot Lift** | [`src/pilot_measurement.py`](file:///C:/Users/sheet/.gemini/antigravity/scratch/customer-rfm-segmentation/src/pilot_measurement.py) | Incremental contribution margin calculation, two-sample $z$-score hypothesis testing. |
| **Interactive UI** | [`web/app.py`](file:///C:/Users/sheet/.gemini/antigravity/scratch/customer-rfm-segmentation/web/app.py) | Full-stack Flask dashboard: Executive, Predictive ML, Stream Monitor, CRM, Audit, Customer 360. |
