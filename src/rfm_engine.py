"""
Enterprise RFM Calculation and Lifecycle Segmentation Engine
Calculates Recency, Frequency, Monetary, and Contribution Margin.
Implements robust tie-breaking percentile quintile scoring (1-5) and
maps customers into 8 commercial lifecycle segments.
"""
import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config.settings import (
    PROCESSED_DATA_DIR,
    DATABASE_PATH,
    OBSERVATION_WINDOW_DAYS,
    NEW_BUYER_ONBOARDING_DAYS,
    LAPSED_DAYS_THRESHOLD,
    MODEL_VERSION
)

def compute_rfm_scores(df_metrics: pd.DataFrame) -> pd.DataFrame:
    """
    Assigns quintile scores (1 to 5) for R, F, and M with robust tie handling.
    - R: Recency (lower recency days = higher score: 5 is best)
    - F: Frequency (higher order count = higher score: 5 is best)
    - M: Monetary (higher net sales USD = higher score: 5 is best)
    
    Documented Tie-Handling Methodology:
    Because Frequency and Monetary metrics often have dense ties at low values (e.g. F=1),
    we use rank(method='min', pct=True) to ensure customers with identical metrics receive
    the exact same fair score bucket, preventing artificial bin splitting.
    """
    df = df_metrics.copy()

    # Recency Scoring: Invert rank so lowest days gets highest percentile
    # For customers with no orders in window (or very high recency), rank accordingly
    r_pct = df["recency_days"].rank(method="min", ascending=True, pct=True)
    # Since lower recency days is better:
    df["r_score"] = pd.cut(
        r_pct,
        bins=[-np.inf, 0.20, 0.40, 0.60, 0.80, np.inf],
        labels=[5, 4, 3, 2, 1]
    ).astype(int)

    # Frequency Scoring: Handle heavy cluster at 0 and 1
    # For F = 0, score is strictly 1
    # For F > 0, use percentile rank among active purchasers or business thresholds
    f_ranks = df["frequency"].rank(method="min", ascending=True, pct=True)
    df["f_score"] = pd.cut(
        f_ranks,
        bins=[-np.inf, 0.40, 0.65, 0.82, 0.93, np.inf],
        labels=[1, 2, 3, 4, 5]
    ).astype(int)
    # Ensure 0 frequency is strictly score 1
    df.loc[df["frequency"] == 0, "f_score"] = 1

    # Monetary Scoring
    m_ranks = df["monetary_usd"].rank(method="min", ascending=True, pct=True)
    df["m_score"] = pd.cut(
        m_ranks,
        bins=[-np.inf, 0.25, 0.50, 0.70, 0.88, np.inf],
        labels=[1, 2, 3, 4, 5]
    ).astype(int)
    # Ensure 0 monetary is strictly score 1
    df.loc[df["monetary_usd"] <= 0, "m_score"] = 1

    df["rfm_code"] = (
        df["r_score"].astype(str) + 
        df["f_score"].astype(str) + 
        df["m_score"].astype(str)
    )

    return df

def assign_lifecycle_segment(row: pd.Series) -> str:
    """
    Maps RFM codes and lifecycle attributes into 8 commercial segments:
    1. Champions / Best Customers
    2. Loyal Customers
    3. High-Value, At Risk
    4. Recent Customers (New Buyers)
    5. Promising
    6. Need Attention
    7. Lapsed
    8. One-Time / Low-History
    """
    r = row["r_score"]
    f = row["f_score"]
    m = row["m_score"]
    freq = row["frequency"]
    recency = row["recency_days"]
    days_since_first = row["days_since_first_purchase"]

    # 1. Zero orders in observation window or severe inactivity
    if freq == 0 or recency > LAPSED_DAYS_THRESHOLD:
        # Check if historically high value before lapsing
        if m >= 4 or f >= 4:
            return "High-Value, At Risk"
        return "Lapsed"

    # 2. Champions / Best Customers: Top tier across R, F, and M
    if r in [4, 5] and f in [4, 5] and m in [4, 5]:
        return "Champions"

    # 3. High-Value, At Risk: Strong historical spend/frequency, but recency is slipping
    if r in [1, 2] and (m in [4, 5] or f in [4, 5]):
        return "High-Value, At Risk"

    # 4. Recent Customers (New Buyers): First purchase is within onboarding window
    if days_since_first <= NEW_BUYER_ONBOARDING_DAYS and freq <= 2 and r in [4, 5]:
        return "Recent Customers"

    # 5. Loyal Customers: Consistent repeat shoppers with good recency
    if r in [3, 4, 5] and f in [3, 4, 5]:
        return "Loyal Customers"

    # 6. Promising: Recent buyers with emerging repeat or above-average spend
    if r in [4, 5] and (freq == 2 or m in [3, 4]):
        return "Promising"

    # 7. Need Attention: Above average value, but recency is becoming borderline
    if r == 3 and (f >= 2 or m >= 3):
        return "Need Attention"

    # 8. One-Time / Low-History: Single order, low spend, not in onboarding window
    if freq == 1:
        return "One-Time / Low-History"

    # Default fallback for active remaining accounts
    if r >= 3:
        return "Promising"
    else:
        return "Need Attention"

def calculate_rfm_table(as_of_date: str = "2026-11-20") -> pd.DataFrame:
    """
    Computes end-to-end customer RFM table with historical retention.
    """
    print(f"Calculating RFM and Lifecycle Segments as of {as_of_date}...")
    as_of_dt = datetime.strptime(as_of_date, "%Y-%m-%d")
    window_start_dt = as_of_dt - timedelta(days=OBSERVATION_WINDOW_DAYS)

    orders_path = PROCESSED_DATA_DIR / "orders_curated_clean.csv"
    customers_path = PROCESSED_DATA_DIR / "curated_customers.csv"

    if not orders_path.exists():
        raise FileNotFoundError("Curated orders table not found. Run ETL pipeline first.")

    df_orders = pd.read_csv(orders_path)
    df_customers = pd.read_csv(customers_path)

    df_orders["order_dt"] = pd.to_datetime(df_orders["order_timestamp"])

    net_col = "net_sales_inr" if "net_sales_inr" in df_orders.columns else "net_sales_usd"
    margin_col = "contribution_margin_inr" if "contribution_margin_inr" in df_orders.columns else "contribution_margin_usd"

    # Historical first and last order timestamps across all completed orders
    historical_orders = df_orders[
        (df_orders["customer_id"].notna()) & 
        (df_orders["order_status"].isin(["COMPLETED", "FULFILLED", "SHIPPED", "DELIVERED"])) &
        (df_orders[net_col] > 0)
    ]

    cust_history = historical_orders.groupby("customer_id").agg(
        first_ever_order=("order_dt", "min"),
        last_ever_order=("order_dt", "max"),
        lifetime_order_count=("order_id", "count"),
        lifetime_net_sales_inr=(net_col, "sum")
    ).reset_index()

    # Qualifying orders strictly within the 12-month observation window
    window_qualifying = df_orders[df_orders["is_qualifying_order"]].copy()

    cust_window = window_qualifying.groupby("customer_id").agg(
        last_purchase_at=("order_dt", "max"),
        qualifying_order_count=("order_id", "count"),
        net_sales_inr=(net_col, "sum"),
        contribution_margin_inr=(margin_col, "sum")
    ).reset_index()

    # Merge with full customer master table so historical/inactive customers never disappear!
    df_rfm = pd.merge(df_customers, cust_history, on="customer_id", how="left")
    df_rfm = pd.merge(df_rfm, cust_window, on="customer_id", how="left")

    # Fill NA for metrics for customers with zero orders in observation window
    df_rfm["qualifying_order_count"] = df_rfm["qualifying_order_count"].fillna(0).astype(int)
    df_rfm["net_sales_inr"] = df_rfm["net_sales_inr"].fillna(0.0).round(2)
    df_rfm["contribution_margin_inr"] = df_rfm["contribution_margin_inr"].fillna(0.0).round(2)
    # Ensure aliases for cross-module compatibility
    df_rfm["net_sales_usd"] = df_rfm["net_sales_inr"]
    df_rfm["contribution_margin_usd"] = df_rfm["contribution_margin_inr"]

    # Recency Calculation:
    # If last purchase in window exists, use that.
    # Otherwise, if historical last order exists, use that (reflecting true inactivity).
    # If customer never bought, recency = 999
    def compute_recency_days(row):
        if pd.notna(row["last_purchase_at"]):
            ref_dt = pd.to_datetime(row["last_purchase_at"])
        elif pd.notna(row["last_ever_order"]):
            ref_dt = pd.to_datetime(row["last_ever_order"])
        else:
            return 999
        return max(0, (as_of_dt - ref_dt).days)

    df_rfm["recency_days"] = df_rfm.apply(compute_recency_days, axis=1)

    # Days since first purchase
    def compute_days_since_first(row):
        if pd.notna(row["first_ever_order"]):
            return max(0, (as_of_dt - pd.to_datetime(row["first_ever_order"])).days)
        first_seen = pd.to_datetime(row["first_seen_at"])
        return max(0, (as_of_dt - first_seen).days)

    df_rfm["days_since_first_purchase"] = df_rfm.apply(compute_days_since_first, axis=1)

    # Standardize column naming for scoring
    df_rfm["frequency"] = df_rfm["qualifying_order_count"]
    df_rfm["monetary_usd"] = df_rfm["net_sales_inr"]

    # Assign Scores 1-5
    df_scored = compute_rfm_scores(df_rfm)

    # Assign Segments
    df_scored["segment"] = df_scored.apply(assign_lifecycle_segment, axis=1)

    # Add Audit & Version Metadata
    df_scored["as_of_date"] = as_of_date
    df_scored["observation_start_date"] = window_start_dt.strftime("%Y-%m-%d")
    df_scored["model_version"] = MODEL_VERSION

    # Preserve region / city_tier
    if "city_tier" in df_scored.columns:
        df_scored["region_or_market"] = df_scored["city_tier"]

    # Analytical table columns
    final_cols = [
        "customer_id", "country", "identity_status", "region_or_market", "first_seen_at",
        "as_of_date", "observation_start_date", "last_purchase_at",
        "recency_days", "qualifying_order_count", "net_sales_inr", "contribution_margin_inr",
        "net_sales_usd", "contribution_margin_usd",
        "r_score", "f_score", "m_score", "rfm_code", "segment",
        "whatsapp_opt_in", "email_opt_in", "sms_opt_in", "push_opt_in", "suppression_flag",
        "model_version"
    ]
    df_final = df_scored[final_cols]

    # Save to CSV and SQLite
    df_final.to_csv(PROCESSED_DATA_DIR / "customer_rfm.csv", index=False)

    conn = sqlite3.connect(DATABASE_PATH)
    df_final.to_sql("customer_rfm", conn, if_exists="replace", index=False)
    conn.close()

    segment_counts = df_final["segment"].value_counts()
    print("RFM Calculation & Lifecycle Segmentation Complete:")
    print(f"Total Evaluated Customers: {len(df_final):,}")
    print("Segment Breakdown:")
    for seg, cnt in segment_counts.items():
        pct = (cnt / len(df_final)) * 100
        rev = df_final[df_final["segment"] == seg]["net_sales_usd"].sum()
        print(f" - {seg:25s}: {cnt:5d} ({pct:5.1f}%) | Net Sales: ₹{rev:10,.2f}")

    return df_final

if __name__ == "__main__":
    calculate_rfm_table()
