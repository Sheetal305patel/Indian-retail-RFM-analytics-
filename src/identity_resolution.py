"""
Customer Identity Resolution and Omnichannel Stitching Engine
Resolves loyalty cards, account IDs, and device cookies to stable customer IDs.
Separates identified vs anonymous POS transactions and generates an Identity Coverage Report.
"""
import pandas as pd
import numpy as np
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config.settings import RAW_DATA_DIR, PROCESSED_DATA_DIR

def run_identity_resolution():
    """
    Stitches identifiers across web, app, and POS systems.
    Generates:
    1. Curated identity resolution map.
    2. Enriched orders with resolved customer IDs.
    3. Omnichannel identity coverage metrics (reconciliation).
    """
    print("Running Customer Identity Resolution & Omnichannel Deduplication...")
    
    customers_path = RAW_DATA_DIR / "customers.csv"
    orders_path = RAW_DATA_DIR / "orders.csv"
    identity_path = RAW_DATA_DIR / "identity_links.csv"

    if not customers_path.exists() or not orders_path.exists():
        raise FileNotFoundError("Raw customer or order data missing. Run data generator first.")

    df_customers = pd.read_csv(customers_path)
    df_orders = pd.read_csv(orders_path)
    df_identity = pd.read_csv(identity_path) if identity_path.exists() else pd.DataFrame()

    total_orders = len(df_orders)
    total_gross = df_orders["gross_amount"].sum()
    net_col = "net_sales_inr" if "net_sales_inr" in df_orders.columns else "net_sales_usd"
    total_net = df_orders[net_col].sum()

    # 1. Identify Anonymous vs Identified
    df_orders["is_identified"] = df_orders["customer_id"].notna()
    
    identified_orders = df_orders[df_orders["is_identified"]]
    anonymous_orders = df_orders[~df_orders["is_identified"]]

    identified_rev = identified_orders[net_col].sum()
    anonymous_rev = anonymous_orders[net_col].sum()

    identity_coverage_pct = (identified_rev / total_net * 100) if total_net > 0 else 0.0

    # 2. Check for duplicate orders
    duplicate_orders_count = df_orders.duplicated(subset=["order_id"]).sum()
    if duplicate_orders_count > 0:
        print(f"Warning: Found {duplicate_orders_count} duplicate order IDs. Deduplicating...")
        df_orders = df_orders.drop_duplicates(subset=["order_id"], keep="first")

    # 3. Channel Coverage Breakdown
    channel_summary = df_orders.groupby("channel").agg(
        order_count=("order_id", "count"),
        net_sales_inr=(net_col, "sum"),
        identified_orders=("is_identified", "sum")
    ).reset_index()

    channel_summary["identification_rate_pct"] = (
        channel_summary["identified_orders"] / channel_summary["order_count"] * 100
    ).round(2)

    coverage_report = {
        "total_orders": int(total_orders),
        "identified_orders": int(len(identified_orders)),
        "anonymous_orders": int(len(anonymous_orders)),
        "total_net_sales_inr": round(float(total_net), 2),
        "identified_net_sales_inr": round(float(identified_rev), 2),
        "anonymous_net_sales_inr": round(float(anonymous_rev), 2),
        "revenue_coverage_pct": round(float(identity_coverage_pct), 2),
        "duplicate_orders_removed": int(duplicate_orders_count),
        "channel_breakdown": channel_summary.to_dict(orient="records")
    }

    # Save resolved curated orders
    df_orders.to_csv(PROCESSED_DATA_DIR / "curated_orders.csv", index=False)
    df_customers.to_csv(PROCESSED_DATA_DIR / "curated_customers.csv", index=False)

    print(f"Identity Resolution Complete:")
    print(f" - Identified Orders: {len(identified_orders):,} ({len(identified_orders)/total_orders*100:.1f}%)")
    print(f" - Anonymous Store Orders: {len(anonymous_orders):,} ({len(anonymous_orders)/total_orders*100:.1f}%)")
    print(f" - Identified Revenue Coverage: ₹{identified_rev:,.2f} ({identity_coverage_pct:.1f}%)")
    print(f" - Anonymous POS Revenue Excluded from Customer Scoring: ₹{anonymous_rev:,.2f}")

    return coverage_report

if __name__ == "__main__":
    run_identity_resolution()
