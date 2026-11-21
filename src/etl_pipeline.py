"""
Enterprise ETL and Commercial Order Curation Pipeline
Applies strict transaction and metric accounting rules:
- Filters qualifying orders (completed/fulfilled, non-test, non-fraud, identified).
- Subtracts refunds and returns from net merchandise sales.
- Handles partial returns (count = 1 in frequency) vs full returns (count = 0 in frequency).
- Derives contribution margin.
- Enforces rolling observation window cutoff.
"""
import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config.settings import (
    RAW_DATA_DIR,
    PROCESSED_DATA_DIR,
    DATABASE_PATH,
    QUALIFYING_STATUSES,
    EXCLUDED_STATUSES,
    OBSERVATION_WINDOW_DAYS,
    MODEL_VERSION
)

def run_etl_pipeline(as_of_date: str = "2026-11-20"):
    """
    Executes commercial curation rules and outputs analytical tables.
    """
    print(f"Executing ETL Pipeline as of {as_of_date}...")
    as_of_dt = datetime.strptime(as_of_date, "%Y-%m-%d")
    window_start_dt = as_of_dt - timedelta(days=OBSERVATION_WINDOW_DAYS)

    orders_path = PROCESSED_DATA_DIR / "curated_orders.csv"
    order_items_path = RAW_DATA_DIR / "order_items.csv"
    customers_path = PROCESSED_DATA_DIR / "curated_customers.csv"

    if not orders_path.exists():
        # Fallback to raw if identity resolution not run
        orders_path = RAW_DATA_DIR / "orders.csv"

    df_orders = pd.read_csv(orders_path)
    df_order_items = pd.read_csv(order_items_path)
    df_customers = pd.read_csv(customers_path)

    # Convert order_timestamp to datetime
    df_orders["order_dt"] = pd.to_datetime(df_orders["order_timestamp"])

    # 1. Total Source Reconciliation Baseline
    total_raw_orders = len(df_orders)
    total_raw_gross = df_orders["gross_amount"].sum()
    net_col = "net_sales_inr" if "net_sales_inr" in df_orders.columns else "net_sales_usd"
    margin_col = "contribution_margin_inr" if "contribution_margin_inr" in df_orders.columns else "contribution_margin_usd"
    cost_col = "product_cost_inr" if "product_cost_inr" in df_orders.columns else "product_cost_usd"
    total_raw_net = df_orders[net_col].sum()

    # 2. Apply Qualifying Logic and Exclusion Rules
    # Rule 1: Exclude cancelled, test, fraud, and RTO (failed COD delivery)
    df_orders["is_excluded_status"] = df_orders["order_status"].isin(EXCLUDED_STATUSES)
    
    # Rule 2: Must have a known customer_id
    df_orders["has_customer_id"] = df_orders["customer_id"].notna()

    # Rule 3: Within observation window
    df_orders["in_observation_window"] = (df_orders["order_dt"] >= window_start_dt) & (df_orders["order_dt"] <= as_of_dt)

    # Rule 4: Handling full returns and RTO deliveries
    # Fully refunded or RTO orders are excluded from qualifying purchase frequency
    df_orders["is_fully_refunded"] = (df_orders["order_status"].isin(["REFUNDED", "RTO"])) | (df_orders[net_col] <= 0)

    # Qualifying order definition:
    # Status in QUALIFYING_STATUSES, not excluded, has customer_id, in window, not fully refunded
    df_orders["is_qualifying_order"] = (
        df_orders["order_status"].isin(QUALIFYING_STATUSES) &
        df_orders["has_customer_id"] &
        df_orders["in_observation_window"] &
        (~df_orders["is_fully_refunded"]) &
        (df_orders[net_col] > 0)
    )

    # Standardize column names for cross-module compatibility
    df_orders["net_sales_inr"] = df_orders[net_col]
    df_orders["contribution_margin_inr"] = df_orders[margin_col]
    df_orders["product_cost_inr"] = df_orders[cost_col] if cost_col in df_orders.columns else 0.0

    # Ensure aliases for cross-module compatibility
    df_orders["net_sales_usd"] = df_orders["net_sales_inr"]
    df_orders["contribution_margin_usd"] = df_orders["contribution_margin_inr"]
    df_orders["product_cost_usd"] = df_orders["product_cost_inr"]

    # Save Curated Orders Table
    export_cols = [
        "order_id", "customer_id", "order_timestamp", "order_status", "channel",
        "currency", "gross_amount", "discount_amount", "refund_amount",
        "net_sales_amount", "net_sales_inr", "contribution_margin_inr", "product_cost_inr",
        "net_sales_usd", "contribution_margin_usd", "product_cost_usd",
        "is_qualifying_order", "in_observation_window", "has_customer_id"
    ]
    if "payment_method" in df_orders.columns:
        export_cols.append("payment_method")
    if "city_tier" in df_orders.columns:
        export_cols.append("city_tier")

    curated_orders_export = df_orders[export_cols]
    curated_orders_export.to_csv(PROCESSED_DATA_DIR / "orders_curated_clean.csv", index=False)

    # 3. Save to SQLite Database
    conn = sqlite3.connect(DATABASE_PATH)
    curated_orders_export.to_sql("orders", conn, if_exists="replace", index=False)
    df_customers.to_sql("customers", conn, if_exists="replace", index=False)
    df_order_items.to_sql("order_items", conn, if_exists="replace", index=False)
    conn.close()

    qualifying_orders = df_orders[df_orders["is_qualifying_order"]]

    print("ETL Pipeline Execution Complete:")
    print(f" - Raw Orders Ingested: {total_raw_orders:,}")
    print(f" - Qualifying Orders in 12-Month Window: {len(qualifying_orders):,} ({len(qualifying_orders)/total_raw_orders*100:.1f}%)")
    print(f" - Excluded Orders (Cancelled/Test/Fraud/RTO): {df_orders['is_excluded_status'].sum():,}")
    print(f" - Fully Refunded / RTO Bounced Orders: {df_orders['is_fully_refunded'].sum():,}")
    print(f" - Anonymous Store Orders Excluded: {(~df_orders['has_customer_id']).sum():,}")
    print(f" - Orders Outside Observation Window: {(~df_orders['in_observation_window']).sum():,}")
    print(f" - Total Curated Qualifying Net Sales: ₹{qualifying_orders['net_sales_inr'].sum():,.2f}")

    return {
        "as_of_date": as_of_date,
        "window_start_date": window_start_dt.strftime("%Y-%m-%d"),
        "total_raw_orders": int(total_raw_orders),
        "qualifying_orders_count": int(len(qualifying_orders)),
        "qualifying_net_sales_inr": round(float(qualifying_orders["net_sales_inr"].sum()), 2),
        "qualifying_margin_inr": round(float(qualifying_orders["contribution_margin_inr"].sum()), 2)
    }

if __name__ == "__main__":
    run_etl_pipeline()
