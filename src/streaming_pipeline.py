"""
Real-Time Event Streaming & Incremental State Engine
Simulates live event streaming (Kafka/PubSub style) with incremental online
state updates, dynamic RFM re-scoring, real-time segment transitions, and alert dispatching.
"""
import sqlite3
import json
import random
import time
from datetime import datetime
from pathlib import Path
import pandas as pd
import numpy as np
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config.settings import (
    PROCESSED_DATA_DIR,
    DATABASE_PATH,
    SEGMENT_METADATA
)
from src.rfm_engine import assign_lifecycle_segment

class RealTimeStreamEngine:
    """
    Manages in-memory and SQLite incremental customer state updates
    triggered by incoming event stream payloads.
    """
    def __init__(self):
        self.db_path = DATABASE_PATH
        self.events_processed = 0
        self.live_revenue_added = 0.0
        self.segment_transitions = []
        self.alert_feed = []

    def load_customer_profile(self, customer_id: str) -> dict:
        """Loads live customer record from SQLite database."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        # Check predictive table first, then customer_rfm
        cur.execute("SELECT * FROM customer_predictive_rfm WHERE customer_id = ?", (customer_id,))
        row = cur.fetchone()
        if not row:
            cur.execute("SELECT * FROM customer_rfm WHERE customer_id = ?", (customer_id,))
            row = cur.fetchone()
        conn.close()

        if row:
            return dict(row)
        return None

    def process_order_event(self, event: dict) -> dict:
        """
        Incrementally processes an incoming live order completed event.
        - Updates frequency, net sales, margin.
        - Resets recency to 0.
        - Re-evaluates RFM code and segment in real-time.
        - Dispatches alerts if segment upgraded or VIP status reached.
        """
        cust_id = event["customer_id"]
        order_amt = float(event.get("net_sales_usd", 120.0))
        margin_amt = float(event.get("contribution_margin_usd", order_amt * 0.62))
        event_time = event.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        profile = self.load_customer_profile(cust_id)
        if not profile:
            return {"status": "error", "message": f"Customer {cust_id} not found"}

        old_segment = profile["segment"]
        old_freq = int(profile["qualifying_order_count"])
        old_sales = float(profile["net_sales_usd"])
        old_margin = float(profile.get("contribution_margin_usd", 0.0))

        # Incremental Online State Update
        new_freq = old_freq + 1
        new_sales = round(old_sales + order_amt, 2)
        new_margin = round(old_margin + margin_amt, 2)
        new_recency = 0 # fresh purchase just completed

        # Dynamic Real-time R, F, M scoring updates
        new_r = 5 # 0 days recency guarantees top Score 5
        
        # Frequency score upgrade
        if new_freq >= 6:
            new_f = 5
        elif new_freq >= 4:
            new_f = 4
        elif new_freq >= 2:
            new_f = 3
        else:
            new_f = 2

        # Monetary score upgrade
        if new_sales >= 1500:
            new_m = 5
        elif new_sales >= 800:
            new_m = 4
        elif new_sales >= 350:
            new_m = 3
        elif new_sales >= 100:
            new_m = 2
        else:
            new_m = 1

        new_rfm_code = f"{new_r}{new_f}{new_m}"

        # Dynamic Segment Re-assignment
        mock_row = pd.Series({
            "r_score": new_r,
            "f_score": new_f,
            "m_score": new_m,
            "frequency": new_freq,
            "recency_days": new_recency,
            "days_since_first_purchase": profile.get("days_since_first_purchase", 120)
        })
        new_segment = assign_lifecycle_segment(mock_row)

        # Real-time Churn Probability reduction
        old_churn = float(profile.get("churn_probability", 0.45))
        new_churn = max(0.04, round(old_churn * 0.40, 4)) # buying immediately slashes churn risk!
        new_churn_pct = round(new_churn * 100, 1)
        new_churn_tier = "Critical" if new_churn >= 0.75 else ("High" if new_churn >= 0.50 else ("Medium" if new_churn >= 0.25 else "Low"))

        # Persist incremental state to SQLite database
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        # Update customer_rfm
        cur.execute("""
            UPDATE customer_rfm
            SET qualifying_order_count = ?, net_sales_usd = ?, contribution_margin_usd = ?,
                recency_days = ?, last_purchase_at = ?, r_score = ?, f_score = ?, m_score = ?,
                rfm_code = ?, segment = ?
            WHERE customer_id = ?
        """, (new_freq, new_sales, new_margin, new_recency, event_time, new_r, new_f, new_m, new_rfm_code, new_segment, cust_id))

        # Update customer_predictive_rfm if table exists
        cur.execute("""
            UPDATE customer_predictive_rfm
            SET qualifying_order_count = ?, net_sales_usd = ?, contribution_margin_usd = ?,
                recency_days = ?, r_score = ?, f_score = ?, m_score = ?,
                rfm_code = ?, segment = ?, churn_probability = ?, churn_probability_pct = ?, churn_risk_tier = ?
            WHERE customer_id = ?
        """, (new_freq, new_sales, new_margin, new_recency, new_r, new_f, new_m, new_rfm_code, new_segment, new_churn, new_churn_pct, new_churn_tier, cust_id))

        conn.commit()
        conn.close()

        # Update engine counters
        self.events_processed += 1
        self.live_revenue_added += order_amt

        transition_occurred = old_segment != new_segment
        transition_info = None

        if transition_occurred:
            transition_info = {
                "customer_id": cust_id,
                "timestamp": event_time,
                "from_segment": old_segment,
                "to_segment": new_segment,
                "reason": f"New order of ${order_amt:.2f} triggered RFM code {old_profile_rfm(profile)} -> {new_rfm_code}"
            }
            self.segment_transitions.append(transition_info)

            # Alert dispatch
            alert = {
                "type": "SEGMENT_TRANSITION",
                "severity": "SUCCESS" if new_segment in ["Champions", "Loyal Customers", "Promising"] else "INFO",
                "message": f"🚀 Customer {cust_id} promoted from '{old_segment}' to '{new_segment}'!",
                "timestamp": event_time
            }
            self.alert_feed.append(alert)

        return {
            "status": "success",
            "customer_id": cust_id,
            "order_id": event.get("order_id", f"ORD-LIVE-{int(time.time()*1000)}"),
            "amount": order_amt,
            "margin": margin_amt,
            "old_rfm": old_profile_rfm(profile),
            "new_rfm": new_rfm_code,
            "old_segment": old_segment,
            "new_segment": new_segment,
            "segment_transition": transition_occurred,
            "old_churn_prob": old_churn,
            "new_churn_prob": new_churn,
            "timestamp": event_time
        }

def old_profile_rfm(profile: dict) -> str:
    return profile.get("rfm_code", f"{profile.get('r_score', 1)}{profile.get('f_score', 1)}{profile.get('m_score', 1)}")

def generate_simulated_stream_event() -> dict:
    """Generates a realistic live retail event for streaming."""
    conn = sqlite3.connect(DATABASE_PATH)
    cur = conn.cursor()
    # Pick a random customer from active database
    cur.execute("SELECT customer_id FROM customer_rfm ORDER BY RANDOM() LIMIT 1")
    row = cur.fetchone()
    conn.close()

    cust_id = row[0] if row else "IND-CUST-00042"
    channels = ["d2c_app", "d2c_web", "pos_store_identified", "quick_commerce"]
    order_val = round(float(np.random.gamma(shape=3.5, scale=420.0)), 2)
    order_val = max(499.0, min(order_val, 8999.0)) # Realistic Indian AOV range (₹499 to ₹8,999)

    event_id = f"EVT-IND-{int(time.time()*1000)}"
    order_id = f"IND-ORD-STREAM-{int(time.time()*1000)%100000}"

    return {
        "event_id": event_id,
        "event_type": "ORDER_COMPLETED",
        "customer_id": cust_id,
        "order_id": order_id,
        "channel": random.choice(channels),
        "payment_method": random.choice(["UPI", "UPI", "UPI", "Cards", "NetBanking"]),
        "currency": "INR",
        "gross_amount": round(order_val * 1.15, 2),
        "discount_amount": round(order_val * 0.15, 2),
        "net_sales_inr": order_val,
        "net_sales_usd": order_val,
        "contribution_margin_inr": round(order_val * 0.62, 2),
        "contribution_margin_usd": round(order_val * 0.62, 2),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

# Global Stream Engine Instance
stream_engine = RealTimeStreamEngine()

if __name__ == "__main__":
    print("Testing Indian real-time stream engine with 5 simulated events...")
    for i in range(5):
        evt = generate_simulated_stream_event()
        res = stream_engine.process_order_event(evt)
        print(f"Event {i+1}: {res['customer_id']} -> ₹{res['amount']} | RFM: {res['old_rfm']} -> {res['new_rfm']} | Segment: {res['old_segment']} -> {res['new_segment']}")
        time.sleep(0.3)
