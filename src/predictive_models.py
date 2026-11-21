"""
Predictive Machine Learning Engine: Churn Propensity & Customer Lifetime Value (pLTV)
Builds feature engineering pipelines, PyTorch-powered churn probability classifier,
and forward 12-month Net Revenue & Margin pLTV estimation.
"""
import sqlite3
import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Ensure project root in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config.settings import (
    PROCESSED_DATA_DIR,
    RAW_DATA_DIR,
    DATABASE_PATH,
    MODEL_VERSION
)

# Set random seeds for reproducibility
torch.manual_seed(42)
np.random.seed(42)

class ChurnClassifierNN(nn.Module):
    """Deep learning neural classifier for customer churn probability estimation."""
    def __init__(self, input_dim: int):
        super(ChurnClassifierNN, self).__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, 32),
            nn.BatchNorm1d(32),
            nn.ReLU(),
            nn.Dropout(0.25),
            nn.Linear(32, 16),
            nn.ReLU(),
            nn.Linear(16, 1),
            nn.Sigmoid()
        )

    def forward(self, x):
        return self.net(x)

def extract_predictive_features(as_of_date: str = "2026-11-20") -> pd.DataFrame:
    """
    Constructs high-signal behavioral features:
    - Recency days & days since first purchase
    - Order velocity & inter-purchase interval
    - Average Order Value (AOV) & Monetary trend
    - Return rate & discount sensitivity
    - Multi-channel cross-shopping diversity
    """
    orders_path = PROCESSED_DATA_DIR / "orders_curated_clean.csv"
    rfm_path = PROCESSED_DATA_DIR / "customer_rfm.csv"

    if not orders_path.exists() or not rfm_path.exists():
        raise FileNotFoundError("Curated orders or customer RFM table missing. Run ETL first.")

    df_orders = pd.read_csv(orders_path)
    df_rfm = pd.read_csv(rfm_path)

    as_of_dt = datetime.strptime(as_of_date, "%Y-%m-%d")
    df_orders["order_dt"] = pd.to_datetime(df_orders["order_timestamp"])

    # Filter to identified customers with completed orders
    ident_orders = df_orders[
        (df_orders["customer_id"].notna()) &
        (df_orders["order_status"].isin(["COMPLETED", "FULFILLED", "SHIPPED", "DELIVERED"]))
    ].copy()

    cost_col = "product_cost_usd" if "product_cost_usd" in ident_orders.columns else ("product_cost_inr" if "product_cost_inr" in ident_orders.columns else "gross_amount")

    # Calculate customer level behavioral feature aggregates
    order_features = ident_orders.groupby("customer_id").agg(
        gross_spend_usd=("gross_amount", "sum"),
        discount_usd=("discount_amount", "sum"),
        refund_usd=("refund_amount", "sum"),
        net_spend_usd=("net_sales_usd", "sum"),
        cost_usd=(cost_col, "sum"),
        margin_usd=("contribution_margin_usd", "sum"),
        total_transactions=("order_id", "count"),
        channels_used=("channel", lambda x: x.nunique()),
        earliest_order=("order_dt", "min"),
        latest_order=("order_dt", "max")
    ).reset_index()

    # Derived ratios
    order_features["discount_sensitivity"] = np.where(
        order_features["gross_spend_usd"] > 0,
        order_features["discount_usd"] / order_features["gross_spend_usd"],
        0.0
    ).round(4)

    order_features["return_rate"] = np.where(
        order_features["gross_spend_usd"] > 0,
        order_features["refund_usd"] / order_features["gross_spend_usd"],
        0.0
    ).round(4)

    order_features["average_order_value"] = np.where(
        order_features["total_transactions"] > 0,
        order_features["net_spend_usd"] / order_features["total_transactions"],
        0.0
    ).round(2)

    # Average days between orders
    def calc_interpurchase_interval(row):
        tx_count = row["total_transactions"]
        if tx_count <= 1:
            return 180.0 # default prior for single-order customers
        span_days = max(1, (row["latest_order"] - row["earliest_order"]).days)
        return round(span_days / (tx_count - 1), 1)

    order_features["avg_days_between_orders"] = order_features.apply(calc_interpurchase_interval, axis=1)

    # Merge with RFM base table
    df_feat = pd.merge(df_rfm, order_features, on="customer_id", how="left")

    # Impute missing features for customers with zero recent orders
    df_feat["gross_spend_usd"] = df_feat["gross_spend_usd"].fillna(0.0)
    df_feat["discount_sensitivity"] = df_feat["discount_sensitivity"].fillna(0.0)
    df_feat["return_rate"] = df_feat["return_rate"].fillna(0.0)
    df_feat["average_order_value"] = df_feat["average_order_value"].fillna(0.0)
    df_feat["avg_days_between_orders"] = df_feat["avg_days_between_orders"].fillna(240.0)
    df_feat["channels_used"] = df_feat["channels_used"].fillna(1).astype(int)

    # Order velocity: orders per 90-day cycle
    df_feat["order_velocity_90d"] = np.where(
        df_feat["recency_days"] > 0,
        (df_feat["qualifying_order_count"] / np.maximum(df_feat["recency_days"], 30)) * 90,
        0.0
    ).round(2)

    # Ground-truth churn proxy for training:
    # A customer is defined as churned if recency_days > 180 or frequency in window == 0
    # or last purchase was > 2x their average inter-purchase interval
    is_churned = (
        (df_feat["recency_days"] > 180) |
        (df_feat["qualifying_order_count"] == 0) |
        (df_feat["recency_days"] > (df_feat["avg_days_between_orders"] * 2.2))
    ).astype(float)

    # Add realistic label noise for machine learning generalization
    noise = np.random.binomial(1, 0.05, size=len(df_feat))
    df_feat["target_churn"] = np.abs(is_churned - noise)

    return df_feat

def train_and_score_predictive_models(as_of_date: str = "2026-11-20") -> pd.DataFrame:
    """
    Trains PyTorch churn propensity neural network and calculates forward 12-Month pLTV.
    """
    print(f"Training ML Predictive Models (Churn Propensity & pLTV) as of {as_of_date}...")
    df_data = extract_predictive_features(as_of_date=as_of_date)

    feature_cols = [
        "recency_days",
        "qualifying_order_count",
        "net_sales_usd",
        "average_order_value",
        "avg_days_between_orders",
        "order_velocity_90d",
        "discount_sensitivity",
        "return_rate",
        "channels_used",
        "r_score",
        "f_score",
        "m_score"
    ]

    X_raw = df_data[feature_cols].values.astype(np.float32)
    y_raw = df_data["target_churn"].values.astype(np.float32).reshape(-1, 1)

    # Z-Score Feature Standardization
    means = np.mean(X_raw, axis=0)
    stds = np.std(X_raw, axis=0) + 1e-7
    X_scaled = (X_raw - means) / stds

    # PyTorch Tensors
    X_tensor = torch.tensor(X_scaled, dtype=torch.float32)
    y_tensor = torch.tensor(y_raw, dtype=torch.float32)

    # Initialize Model, Optimizer, Loss
    model = ChurnClassifierNN(input_dim=len(feature_cols))
    criterion = nn.BCELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.015, weight_decay=1e-4)

    # Train for 75 epochs
    model.train()
    for epoch in range(75):
        optimizer.zero_grad()
        preds = model(X_tensor)
        loss = criterion(preds, y_tensor)
        loss.backward()
        optimizer.step()

    # Predict Probabilities
    model.eval()
    with torch.no_grad():
        churn_probs = model(X_tensor).numpy().flatten()

    df_data["churn_probability"] = np.round(churn_probs, 4)
    df_data["churn_probability_pct"] = np.round(churn_probs * 100, 1)

    # Churn Risk Tier Assignment
    conditions_churn = [
        df_data["churn_probability"] >= 0.75,
        df_data["churn_probability"] >= 0.50,
        df_data["churn_probability"] >= 0.25
    ]
    choices_churn = ["Critical", "High", "Medium"]
    df_data["churn_risk_tier"] = np.select(conditions_churn, choices_churn, default="Low")

    # -------------------------------------------------------------
    # 2. Predictive Customer Lifetime Value (pLTV 12-Month Model)
    # -------------------------------------------------------------
    # Formula: pLTV = Expected Orders (12M) * Expected AOV * Margin Ratio * (1 - Churn Probability)
    # Expected Orders = max(1, current_frequency) * retention_factor
    retention_factor = (1.0 - df_data["churn_probability"]).clip(0.05, 0.98)
    
    # Baseline expected frequency next 12M
    exp_freq_12m = np.maximum(
        0.5,
        df_data["qualifying_order_count"] * (0.85 + 0.3 * (df_data["r_score"] / 5.0))
    ) * retention_factor

    # Expected AOV next 12M
    overall_aov_median = df_data[df_data["average_order_value"] > 0]["average_order_value"].median()
    exp_aov_12m = np.where(
        df_data["average_order_value"] > 0,
        df_data["average_order_value"] * (0.95 + 0.1 * (df_data["m_score"] / 5.0)),
        overall_aov_median
    )

    # Typical Contribution Margin Ratio in retail (~60%)
    margin_ratio = np.where(
        df_data["net_sales_usd"] > 0,
        (df_data["contribution_margin_usd"] / df_data["net_sales_usd"]).clip(0.35, 0.85),
        0.60
    )

    # 12-Month Predicted Net Sales & Margin
    predicted_net_sales = np.round(exp_freq_12m * exp_aov_12m, 2)
    predicted_margin = np.round(predicted_net_sales * margin_ratio, 2)

    df_data["predicted_12m_net_sales"] = predicted_net_sales
    df_data["predicted_12m_margin"] = predicted_margin

    # pLTV Value Tiers (Percentile based)
    pltv_ranks = df_data["predicted_12m_net_sales"].rank(pct=True)
    df_data["pltv_value_tier"] = pd.cut(
        pltv_ranks,
        bins=[-np.inf, 0.50, 0.80, 0.95, np.inf],
        labels=["Bronze", "Silver", "Gold", "Platinum"]
    ).astype(str)

    # Strategic Action Quadrant:
    # Quadrant 1: Protect & Retain VIPs (High Value + High/Critical Churn Risk)
    # Quadrant 2: Nurture Champions (High Value + Low/Med Churn Risk)
    # Quadrant 3: Re-engage or Divest (Low Value + High/Critical Churn Risk)
    # Quadrant 4: Growth Upsell (Low Value + Low/Med Churn Risk)
    is_high_value = df_data["pltv_value_tier"].isin(["Platinum", "Gold"])
    is_high_churn = df_data["churn_risk_tier"].isin(["Critical", "High"])

    def assign_quadrant(row):
        h_val = row["pltv_value_tier"] in ["Platinum", "Gold"]
        h_churn = row["churn_risk_tier"] in ["Critical", "High"]
        if h_val and h_churn:
            return "Protect & Retain VIPs"
        elif h_val and not h_churn:
            return "Nurture Champions"
        elif not h_val and h_churn:
            return "Re-engage or Divest"
        else:
            return "Growth & Upsell"

    df_data["strategic_quadrant"] = df_data.apply(assign_quadrant, axis=1)

    # Save to CSV and SQLite Database
    export_cols = [
        "customer_id", "country", "segment", "rfm_code", "r_score", "f_score", "m_score",
        "recency_days", "qualifying_order_count", "net_sales_usd", "contribution_margin_usd",
        "average_order_value", "avg_days_between_orders", "order_velocity_90d",
        "discount_sensitivity", "return_rate", "channels_used",
        "churn_probability", "churn_probability_pct", "churn_risk_tier",
        "predicted_12m_net_sales", "predicted_12m_margin", "pltv_value_tier", "strategic_quadrant",
        "whatsapp_opt_in", "email_opt_in", "sms_opt_in", "push_opt_in", "suppression_flag", "as_of_date"
    ]
    df_scored = df_data[export_cols].copy()

    output_csv = PROCESSED_DATA_DIR / "customer_predictive_rfm.csv"
    df_scored.to_csv(output_csv, index=False)

    conn = sqlite3.connect(DATABASE_PATH)
    df_scored.to_sql("customer_predictive_rfm", conn, if_exists="replace", index=False)
    conn.close()

    # Feature Importance (Linear Weights proxy)
    first_layer_weights = model.net[0].weight.data.abs().mean(dim=0).numpy()
    feat_importance = dict(zip(feature_cols, np.round(first_layer_weights, 4).tolist()))
    feat_importance = dict(sorted(feat_importance.items(), key=lambda item: item[1], reverse=True))

    print(f"ML Model Training & Scoring Complete:")
    print(f" - Scored Customers: {len(df_scored):,}")
    print(f" - Churn Risk Tiers: {df_scored['churn_risk_tier'].value_counts().to_dict()}")
    print(f" - Value Tiers: {df_scored['pltv_value_tier'].value_counts().to_dict()}")
    print(f" - Total Predicted 12M Spend: ₹{df_scored['predicted_12m_net_sales'].sum():,.2f}")
    print(f" - Top Churn Risk Drivers: {list(feat_importance.keys())[:4]}")

    return {
        "df_scored": df_scored,
        "feature_importance": feat_importance,
        "total_predicted_12m_revenue": round(float(df_scored["predicted_12m_net_sales"].sum()), 2),
        "total_predicted_12m_margin": round(float(df_scored["predicted_12m_margin"].sum()), 2),
        "vips_at_risk_count": int(((df_scored["pltv_value_tier"].isin(["Platinum", "Gold"])) & (df_scored["churn_risk_tier"].isin(["Critical", "High"]))).sum())
    }

if __name__ == "__main__":
    train_and_score_predictive_models()
