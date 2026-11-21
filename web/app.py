"""
Enterprise Web Application and Interactive Dashboard
Customer Value and Lifecycle Segmentation (RFM Engine)
Provides Executive View, CRM Activation View, Analyst Audit View, and Customer 360.
"""
import sqlite3
import json
from pathlib import Path
from flask import Flask, render_template, jsonify, request, send_file
import pandas as pd
import numpy as np
import sys

# Add root folder to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from config.settings import (
    PROCESSED_DATA_DIR,
    RAW_DATA_DIR,
    EXPORTS_DIR,
    REPORTS_DIR,
    DATABASE_PATH,
    SEGMENT_METADATA,
    MODEL_VERSION
)
from src.campaign_engine import export_campaign_audience
from src.pilot_measurement import simulate_and_measure_pilot
from src.streaming_pipeline import stream_engine, generate_simulated_stream_event
from src.predictive_models import train_and_score_predictive_models

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def index():
    return executive_view()

@app.route("/executive")
def executive_view():
    """Executive View: Strategic revenue share, segment matrix, identified vs anonymous."""
    rfm_path = PROCESSED_DATA_DIR / "customer_rfm.csv"
    curated_orders_path = PROCESSED_DATA_DIR / "orders_curated_clean.csv"

    if not rfm_path.exists() or not curated_orders_path.exists():
        return render_template("error.html", message="Pipeline data not found. Please run 'python cli.py run-all' first.")

    df_rfm = pd.read_csv(rfm_path)
    df_orders = pd.read_csv(curated_orders_path)

    total_customers = len(df_rfm)
    active_customers = len(df_rfm[df_rfm["qualifying_order_count"] > 0])
    
    total_sales = float(df_orders["net_sales_usd"].sum())
    identified_sales = float(df_rfm["net_sales_usd"].sum())
    anon_orders = df_orders[df_orders["customer_id"].isna()]
    anon_sales = float(anon_orders["net_sales_usd"].sum())
    coverage_pct = round((identified_sales / total_sales * 100), 1) if total_sales > 0 else 0

    total_margin = float(df_rfm["contribution_margin_usd"].sum())

    # Segment aggregations
    seg_grp = df_rfm.groupby("segment").agg(
        customer_count=("customer_id", "count"),
        net_sales=("net_sales_usd", "sum"),
        margin=("contribution_margin_usd", "sum"),
        avg_recency=("recency_days", "mean"),
        avg_orders=("qualifying_order_count", "mean")
    ).reset_index()

    seg_grp["customer_share_pct"] = (seg_grp["customer_count"] / total_customers * 100).round(1)
    seg_grp["sales_share_pct"] = (seg_grp["net_sales"] / max(1, identified_sales) * 100).round(1)
    seg_grp["margin_ratio_pct"] = (seg_grp["margin"] / seg_grp["net_sales"] * 100).fillna(0).round(1)

    # India Real-World Metrics: COD vs Prepaid RTO Analysis
    india_orders = df_orders[df_orders["country"] == "India"] if "country" in df_orders.columns else pd.DataFrame()
    india_cod_stats = {}
    if not india_orders.empty and "payment_method" in india_orders.columns:
        cod_orders = india_orders[india_orders["payment_method"] == "COD"]
        prepaid_orders = india_orders[india_orders["payment_method"] != "COD"]
        cod_rto = len(india_orders[(india_orders["payment_method"] == "COD") & (india_orders["order_status"] == "RTO")])
        cod_rto_rate = round((cod_rto / max(1, len(cod_orders)) * 100), 1)
        india_cod_stats = {
            "total_india_orders": len(india_orders),
            "cod_orders_count": len(cod_orders),
            "prepaid_orders_count": len(prepaid_orders),
            "cod_rto_count": cod_rto,
            "cod_rto_rate_pct": cod_rto_rate,
            "prepaid_return_rate_pct": round(len(prepaid_orders[prepaid_orders["order_status"] == "REFUNDED"]) / max(1, len(prepaid_orders)) * 100, 1),
            "rto_loss_avoidance_usd": round(cod_rto * 14.50, 2) # courier cost saved by converting COD to UPI
        }

    # Market Distribution
    market_stats = []
    if "country" in df_rfm.columns:
        for c_name, grp in df_rfm.groupby("country"):
            market_stats.append({
                "country": c_name,
                "customers": len(grp),
                "cust_share": round(len(grp) / total_customers * 100, 1),
                "net_sales": round(float(grp["net_sales_usd"].sum()), 2),
                "sales_share": round(float(grp["net_sales_usd"].sum()) / max(1, identified_sales) * 100, 1)
            })
        market_stats.sort(key=lambda x: x["net_sales"], reverse=True)

    segments_data = []
    for _, row in seg_grp.iterrows():
        s_name = row["segment"]
        meta = SEGMENT_METADATA.get(s_name, {})
        segments_data.append({
            "name": s_name,
            "title": meta.get("title", s_name),
            "description": meta.get("description", ""),
            "action": meta.get("action", ""),
            "color": meta.get("badge_color", "#6B7280"),
            "customer_count": int(row["customer_count"]),
            "customer_share_pct": float(row["customer_share_pct"]),
            "net_sales": round(float(row["net_sales"]), 2),
            "sales_share_pct": float(row["sales_share_pct"]),
            "margin": round(float(row["margin"]), 2),
            "margin_ratio_pct": float(row["margin_ratio_pct"]),
            "avg_recency": round(float(row["avg_recency"]), 1),
            "avg_orders": round(float(row["avg_orders"]), 1)
        })

    # Sort by net sales descending
    segments_data.sort(key=lambda x: x["net_sales"], reverse=True)

    summary_metrics = {
        "total_customers": total_customers,
        "active_customers": active_customers,
        "inactive_customers": total_customers - active_customers,
        "total_gross_sales": round(float(df_orders["gross_amount"].sum()), 2),
        "total_net_sales": round(total_sales, 2),
        "identified_net_sales": round(identified_sales, 2),
        "anonymous_net_sales": round(anon_sales, 2),
        "identity_coverage_pct": coverage_pct,
        "total_contribution_margin": round(total_margin, 2),
        "as_of_date": df_rfm["as_of_date"].iloc[0] if len(df_rfm) > 0 else "2026-11-20",
        "model_version": MODEL_VERSION
    }

    return render_template(
        "executive.html",
        metrics=summary_metrics,
        segments=segments_data,
        market_stats=market_stats,
        india_cod_stats=india_cod_stats,
        active_tab="executive"
    )

@app.route("/crm")
def crm_view():
    """CRM & Marketing View: Channel eligibility, audience builder, campaign downloads."""
    rfm_path = PROCESSED_DATA_DIR / "customer_rfm.csv"
    if not rfm_path.exists():
        return render_template("error.html", message="Please run the data pipeline first.")

    df_rfm = pd.read_csv(rfm_path)

    # Calculate channel eligibility per segment (including WhatsApp for India)
    has_whatsapp = "whatsapp_opt_in" in df_rfm.columns
    seg_channel = df_rfm.groupby("segment").agg(
        total_customers=("customer_id", "count"),
        whatsapp_eligible=("whatsapp_opt_in", lambda x: (x & (~df_rfm.loc[x.index, "suppression_flag"])).sum()) if has_whatsapp else ("customer_id", lambda x: 0),
        email_eligible=("email_opt_in", lambda x: (x & (~df_rfm.loc[x.index, "suppression_flag"])).sum()),
        sms_eligible=("sms_opt_in", lambda x: (x & (~df_rfm.loc[x.index, "suppression_flag"])).sum()),
        push_eligible=("push_opt_in", lambda x: (x & (~df_rfm.loc[x.index, "suppression_flag"])).sum()),
        suppressed=("suppression_flag", "sum")
    ).reset_index()

    campaign_audiences = []
    for _, row in seg_channel.iterrows():
        s_name = row["segment"]
        meta = SEGMENT_METADATA.get(s_name, {})
        campaign_audiences.append({
            "segment": s_name,
            "title": meta.get("title", s_name),
            "action": meta.get("action", ""),
            "color": meta.get("badge_color", "#6B7280"),
            "total": int(row["total_customers"]),
            "whatsapp_count": int(row["whatsapp_eligible"]),
            "email_count": int(row["email_eligible"]),
            "sms_count": int(row["sms_eligible"]),
            "push_count": int(row["push_eligible"]),
            "suppressed_count": int(row["suppressed"])
        })

    # Available exported files
    exported_files = [f.name for f in EXPORTS_DIR.glob("*.csv")]

    return render_template(
        "crm_activation.html",
        audiences=campaign_audiences,
        exported_files=exported_files,
        active_tab="crm"
    )

@app.route("/analyst")
def analyst_view():
    """Analyst View: Metric distributions, score histograms, tie behavior, financial audit report."""
    rfm_path = PROCESSED_DATA_DIR / "customer_rfm.csv"
    report_path = REPORTS_DIR / "validation_report.json"

    if not rfm_path.exists():
        return render_template("error.html", message="Pipeline data not found.")

    df_rfm = pd.read_csv(rfm_path)

    validation_report = {}
    if report_path.exists():
        with open(report_path, "r") as f:
            validation_report = json.load(f)

    # Score distributions (R, F, M 1-5 counts)
    r_dist = df_rfm["r_score"].value_counts().sort_index().to_dict()
    f_dist = df_rfm["f_score"].value_counts().sort_index().to_dict()
    m_dist = df_rfm["m_score"].value_counts().sort_index().to_dict()

    # Recency & Frequency statistics
    rfm_stats = {
        "recency_min": int(df_rfm["recency_days"].min()),
        "recency_median": int(df_rfm["recency_days"].median()),
        "recency_max": int(df_rfm["recency_days"].max()),
        "freq_min": int(df_rfm["qualifying_order_count"].min()),
        "freq_median": int(df_rfm["qualifying_order_count"].median()),
        "freq_max": int(df_rfm["qualifying_order_count"].max()),
        "monetary_min": round(float(df_rfm["net_sales_usd"].min()), 2),
        "monetary_median": round(float(df_rfm["net_sales_usd"].median()), 2),
        "monetary_max": round(float(df_rfm["net_sales_usd"].max()), 2),
        "zero_freq_count": int((df_rfm["qualifying_order_count"] == 0).sum()),
        "one_freq_count": int((df_rfm["qualifying_order_count"] == 1).sum())
    }

    return render_template(
        "analyst.html",
        r_dist=r_dist,
        f_dist=f_dist,
        m_dist=m_dist,
        stats=rfm_stats,
        report=validation_report,
        active_tab="analyst"
    )

@app.route("/predictive")
def predictive_view():
    """Predictive ML View: Churn propensity, 12M pLTV forecast, Strategic Quadrants."""
    pred_path = PROCESSED_DATA_DIR / "customer_predictive_rfm.csv"
    if not pred_path.exists():
        # Train and score if not generated
        train_and_score_predictive_models()

    df_pred = pd.read_csv(pred_path)

    total_custs = len(df_pred)
    avg_churn_prob = round(float(df_pred["churn_probability"].mean() * 100), 1)
    critical_churn_count = int((df_pred["churn_risk_tier"] == "Critical").sum())
    high_churn_count = int((df_pred["churn_risk_tier"] == "High").sum())
    total_predicted_spend = round(float(df_pred["predicted_12m_net_sales"].sum()), 2)
    total_predicted_margin = round(float(df_pred["predicted_12m_margin"].sum()), 2)

    # Churn Risk Tier counts
    churn_tier_counts = df_pred["churn_risk_tier"].value_counts().to_dict()
    # Value Tier counts
    value_tier_counts = df_pred["pltv_value_tier"].value_counts().to_dict()
    # Strategic Quadrant counts
    quadrant_counts = df_pred["strategic_quadrant"].value_counts().to_dict()

    # High-Value VIPs at Risk (Platinum or Gold + Critical or High Churn Risk)
    vips_at_risk_df = df_pred[
        (df_pred["pltv_value_tier"].isin(["Platinum", "Gold"])) &
        (df_pred["churn_risk_tier"].isin(["Critical", "High"]))
    ].sort_values("predicted_12m_net_sales", ascending=False).head(15)

    vips_at_risk = vips_at_risk_df.to_dict(orient="records")
    vips_at_risk_revenue = round(float(vips_at_risk_df["predicted_12m_net_sales"].sum()), 2)

    # Quadrant Scatter Plot sample (sample 150 customers for snappy rendering)
    scatter_sample = df_pred.sample(n=min(180, len(df_pred)), random_state=42)[[
        "customer_id", "segment", "churn_probability_pct", "predicted_12m_net_sales",
        "pltv_value_tier", "strategic_quadrant"
    ]].to_dict(orient="records")

    metrics = {
        "total_customers": total_custs,
        "avg_churn_prob": avg_churn_prob,
        "critical_churn_count": critical_churn_count,
        "high_churn_count": high_churn_count,
        "total_predicted_spend": total_predicted_spend,
        "total_predicted_margin": total_predicted_margin,
        "vips_at_risk_count": len(vips_at_risk_df),
        "vips_at_risk_revenue": vips_at_risk_revenue
    }

    return render_template(
        "predictive.html",
        metrics=metrics,
        churn_tiers=churn_tier_counts,
        value_tiers=value_tier_counts,
        quadrants=quadrant_counts,
        vips_at_risk=vips_at_risk,
        scatter_sample=scatter_sample,
        active_tab="predictive"
    )

@app.route("/streaming")
def streaming_view():
    """Real-time live event streaming monitor & simulation cockpit."""
    return render_template(
        "streaming.html",
        stats={
            "events_processed": stream_engine.events_processed,
            "live_revenue_added": round(stream_engine.live_revenue_added, 2),
            "transitions_count": len(stream_engine.segment_transitions)
        },
        transitions=stream_engine.segment_transitions[-15:],
        active_tab="streaming"
    )

@app.route("/customer-lookup")
def customer_lookup():
    """Customer 360: Search individual customer history, RFM attributes, ML churn & pLTV."""
    cust_id = request.args.get("id", "").strip().upper()
    customer_data = None
    orders_data = []

    pred_path = PROCESSED_DATA_DIR / "customer_predictive_rfm.csv"
    rfm_path = PROCESSED_DATA_DIR / "customer_rfm.csv"
    orders_path = PROCESSED_DATA_DIR / "orders_curated_clean.csv"
    contacts_path = RAW_DATA_DIR / "customer_contacts_pii.csv"

    # Prefer predictive table if exists
    target_rfm_path = pred_path if pred_path.exists() else rfm_path

    if cust_id and target_rfm_path.exists():
        df_rfm = pd.read_csv(target_rfm_path)
        c_row = df_rfm[df_rfm["customer_id"] == cust_id]
        if not c_row.empty:
            customer_data = c_row.iloc[0].to_dict()
            meta = SEGMENT_METADATA.get(customer_data["segment"], {})
            customer_data["segment_title"] = meta.get("title", customer_data["segment"])
            customer_data["segment_action"] = meta.get("action", "")
            customer_data["badge_color"] = meta.get("badge_color", "#6B7280")

            if contacts_path.exists():
                df_contacts = pd.read_csv(contacts_path)
                contact_row = df_contacts[df_contacts["customer_id"] == cust_id]
                if not contact_row.empty:
                    customer_data.update(contact_row.iloc[0].to_dict())

            if orders_path.exists():
                df_orders = pd.read_csv(orders_path)
                c_orders = df_orders[df_orders["customer_id"] == cust_id].sort_values("order_timestamp", ascending=False)
                orders_data = c_orders.head(15).to_dict(orient="records")

    return render_template(
        "customer_lookup.html",
        search_id=cust_id,
        customer=customer_data,
        orders=orders_data,
        active_tab="lookup"
    )

# Real-time Streaming API Endpoints
@app.route("/api/stream/inject", methods=["POST"])
def api_stream_inject():
    """Manually injects or auto-generates an order completed event into the stream engine."""
    data = request.get_json() or {}
    if not data or "customer_id" not in data:
        data = generate_simulated_stream_event()
    result = stream_engine.process_order_event(data)
    return jsonify(result)

@app.route("/api/stream/events")
def api_stream_events():
    """Server-Sent Events (SSE) live event ticker feed."""
    from flask import Response
    def event_stream():
        # Emit an event every 1.5 seconds
        for _ in range(30):
            evt = generate_simulated_stream_event()
            processed = stream_engine.process_order_event(evt)
            yield f"data: {json.dumps(processed)}\n\n"
            time.sleep(1.2)
    return Response(event_stream(), mimetype="text/event-stream")

# API Endpoints
@app.route("/api/summary")
def api_summary():
    rfm_path = PROCESSED_DATA_DIR / "customer_rfm.csv"
    if not rfm_path.exists():
        return jsonify({"error": "No data"}), 404
    df_rfm = pd.read_csv(rfm_path)
    return jsonify({
        "total_customers": len(df_rfm),
        "total_net_sales": float(df_rfm["net_sales_usd"].sum()),
        "total_margin": float(df_rfm["contribution_margin_usd"].sum()),
        "segments": df_rfm["segment"].value_counts().to_dict()
    })

@app.route("/api/export-audience", methods=["POST"])
def api_export_audience():
    data = request.get_json() or {}
    segment = data.get("segment", "Champions")
    channel = data.get("channel", "email")
    holdout = float(data.get("holdout", 0.10))
    try:
        df_exp = export_campaign_audience(segment_name=segment, channel=channel, holdout_pct=holdout)
        sanitized = segment.lower().replace(" ", "_").replace("/", "_")
        filename = f"audience_{sanitized}_{channel}.csv"
        return jsonify({
            "status": "success",
            "filename": filename,
            "total_records": len(df_exp),
            "treatment_count": int((df_exp["campaign_group"] == "TREATMENT").sum()),
            "control_count": int((df_exp["campaign_group"] == "CONTROL_HOLDOUT").sum())
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route("/api/download-audience/<filename>")
def api_download_audience(filename):
    file_path = EXPORTS_DIR / filename
    if file_path.exists():
        return send_file(file_path, as_attachment=True)
    return jsonify({"error": "File not found"}), 404

@app.route("/api/simulate-pilot", methods=["POST"])
def api_simulate_pilot():
    data = request.get_json() or {}
    audience_file = data.get("audience_file", "audience_high-value,_at_risk_email.csv")
    campaign_name = data.get("campaign_name", "VIP Win-Back Campaign")
    try:
        res = simulate_and_measure_pilot(audience_file=audience_file, campaign_name=campaign_name)
        return jsonify({"status": "success", "result": res})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
