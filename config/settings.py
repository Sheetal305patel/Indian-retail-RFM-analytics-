"""
Configuration & Commercial Settings
Indian Consumer Market Segmentation & Value Optimization Engine
Modeled after Leading Indian Consumer Conglomerates (Tata Neu/Tata Consumer, Reliance Retail/Ajio, Nykaa, HUL, ITC)
"""
import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
EXPORTS_DIR = DATA_DIR / "exports"
REPORTS_DIR = DATA_DIR / "reports"
DATABASE_PATH = PROCESSED_DATA_DIR / "segmentation.db"

for d in [RAW_DATA_DIR, PROCESSED_DATA_DIR, EXPORTS_DIR, REPORTS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# Model & Engine Metadata
MODEL_VERSION = "rfm_v3.0_india_enterprise"
REPORTING_CURRENCY = "INR"
CURRENCY_SYMBOL = "₹"

# Reference Conglomerates & Retail Giants in Scope
REFERENCE_BENCHMARKS = [
    "Tata Consumer Products & Tata Neu (Omnichannel Super-App)",
    "Reliance Retail (Ajio / Trends / JioMart Omnichannel)",
    "Nykaa / FSN E-Commerce (Beauty & Fashion Lifestyle)",
    "Hindustan Unilever Limited (D2C Brands & Shikhar Platform)",
    "ITC Limited (Personal Care, Apparel & Foods Direct)"
]

# Geographic City Tiers in India
INDIAN_CITY_TIERS = {
    "Tier 1 - Metro": [
        "Bengaluru (Karnataka)",
        "Delhi NCR (Delhi / Gurugram / Noida)",
        "Mumbai MMR (Mumbai / Thane / Navi Mumbai)",
        "Hyderabad (Telangana)",
        "Chennai (Tamil Nadu)",
        "Kolkata (West Bengal)",
        "Pune (Maharashtra)"
    ],
    "Tier 2 - Emerging Hubs": [
        "Ahmedabad (Gujarat)",
        "Jaipur (Rajasthan)",
        "Chandigarh Tricity (Punjab / Haryana)",
        "Lucknow (Uttar Pradesh)",
        "Indore (Madhya Pradesh)",
        "Kochi (Kerala)",
        "Coimbatore (Tamil Nadu)",
        "Surat (Gujarat)",
        "Nagpur (Maharashtra)"
    ],
    "Tier 3 - Bharat Growth Belt": [
        "Patna (Bihar)",
        "Bhopal (Madhya Pradesh)",
        "Bhubaneswar (Odisha)",
        "Ranchi (Jharkhand)",
        "Vadodara (Gujarat)",
        "Varanasi (Uttar Pradesh)",
        "Rest of India (Semi-Urban & Rural Hubs)"
    ]
}

# Payment Dynamics in Indian E-Commerce
PAYMENT_METHODS = {
    "UPI": {
        "share": 0.58,              # 58% UPI dominance (PhonePe, GPay, Paytm)
        "rto_failure_rate": 0.025,  # 2.5% return rate (Prepaid high commitment)
        "gateway_fee_pct": 0.00     # 0% MDR on UPI (P2M subsidies)
    },
    "COD": {
        "share": 0.28,              # 28% Cash on Delivery
        "rto_failure_rate": 0.25,   # 25% Return-To-Origin (Customer refusal at doorstep)
        "reverse_logistics_loss_inr": 140.0 # Average forward + reverse courier loss per RTO (Delhivery / BlueDart)
    },
    "Cards": {
        "share": 0.10,              # 10% Credit/Debit Cards & Cardless EMI
        "rto_failure_rate": 0.035,
        "gateway_fee_pct": 0.018    # 1.8% gateway MDR
    },
    "NetBanking_Wallets": {
        "share": 0.04,              # 4% NetBanking & Prepaid Wallets
        "rto_failure_rate": 0.020,
        "gateway_fee_pct": 0.015
    }
}

# Omnichannel Sales Channels
VALID_CHANNELS = {
    "d2c_app": "Mobile Application (iOS / Android Native)",
    "d2c_web": "Direct-to-Consumer Website",
    "pos_store_identified": "Exclusive Brand Store / Offline Outlet (Phone Lookup)",
    "pos_store_anonymous": "Offline Store Walk-in (Anonymous Cash / POS)",
    "quick_commerce": "Quick Commerce Partner (Blinkit / Zepto / Instamart)"
}

# Observation Window & Lifecycle Thresholds (Days)
OBSERVATION_WINDOW_DAYS = 365       # Rolling 12-month window for RFM
NEW_BUYER_ONBOARDING_DAYS = 60      # Customer first seen within last 60 days
LAPSED_DAYS_THRESHOLD = 180         # No purchase in > 180 days is considered lapsed / at-risk
CHAMPION_RECENCY_MAX = 60           # Must have bought in the last 60 days
LOYAL_RECENCY_MAX = 90              # Must have bought in the last 90 days

# Transaction & Order Rules
QUALIFYING_STATUSES = {"COMPLETED", "FULFILLED", "SHIPPED", "DELIVERED"}
EXCLUDED_STATUSES = {"CANCELLED", "TEST", "FRAUD", "RTO"}

# Segment Definitions and Business Action Guidance
SEGMENT_METADATA = {
    "Champions": {
        "title": "Champions / Elite Advocates",
        "description": "Top-tier recency, high purchase frequency, and highest cumulative spend (INR). Brand loyalists.",
        "action": "Early access to festive drops (Diwali / Big Billion Days), VIP concierge care, zero-friction pre-orders, personal loyalty perks.",
        "badge_color": "#10B981"  # Emerald Green
    },
    "Loyal Customers": {
        "title": "Loyal Customers",
        "description": "Consistent repeat purchasers across recent months with high net margin contribution.",
        "action": "Automated WhatsApp replenishment triggers, multi-category bundles, loyalty tier upgrade nudges.",
        "badge_color": "#3B82F6"  # Blue
    },
    "High-Value, At Risk": {
        "title": "High-Value, At Risk",
        "description": "Historically large INR spenders or repeat buyers whose recency has drifted past 120-180 days.",
        "action": "High-touch WhatsApp outreach, bespoke win-back offers, direct customer care survey to diagnose churn reason.",
        "badge_color": "#F59E0B"  # Amber
    },
    "Recent Customers": {
        "title": "Recent Customers (New Buyers)",
        "description": "First-time purchasers within the onboarding window (<=60 days). Highest risk of one-and-done dropoff.",
        "action": "Interactive WhatsApp welcome journey, product education, 10% instant discount on 2nd order via UPI to eliminate COD.",
        "badge_color": "#06B6D4"  # Cyan
    },
    "Promising": {
        "title": "Promising (Emerging Value)",
        "description": "Recent buyers with emerging repeat orders or above-average basket sizes. Growth candidates.",
        "action": "Cross-category discovery campaigns, festive bundle incentives, loyalty tier enrollment.",
        "badge_color": "#8B5CF6"  # Purple
    },
    "Need Attention": {
        "title": "Need Attention",
        "description": "Above-average historical value, but recency is drifting beyond category buying cycle.",
        "action": "Timely WhatsApp replenishment reminder, festive seasonal discount nudge, personalized product recommendations.",
        "badge_color": "#EC4899"  # Pink
    },
    "Lapsed": {
        "title": "Lapsed / Churned",
        "description": "No purchase activity for over 180 days. Significant drop in brand engagement.",
        "action": "Low-cost WhatsApp reactivation drip; suppress from expensive Performance Max / Meta ad retargeting to preserve CAC.",
        "badge_color": "#EF4444"  # Red
    },
    "One-Time / Low-History": {
        "title": "One-Time / Low-History",
        "description": "Single low-spend order outside onboarding window, no repeat signal.",
        "action": "Light-touch nurture, delivery satisfaction check, survey preferences, test second-purchase prepaid voucher.",
        "badge_color": "#6B7280"  # Gray
    }
}
