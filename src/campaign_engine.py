"""
CRM Campaign Activation and Audience Exporter
Enforces marketing eligibility, channel opt-in rules, suppression lists,
generates randomized holdout control groups, and produces privacy-safe campaign feeds.
"""
import sqlite3
import pandas as pd
import numpy as np
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config.settings import (
    RAW_DATA_DIR,
    PROCESSED_DATA_DIR,
    EXPORTS_DIR
)

def export_campaign_audience(
    segment_name: str,
    channel: str = "email",
    holdout_pct: float = 0.10,
    random_seed: int = 123
) -> pd.DataFrame:
    """
    Exports a production campaign audience file for a specific segment and channel.
    Applies:
    1. Segment filtering.
    2. Marketing consent & suppression rules (email_opt_in, suppression_flag).
    3. Randomized Holdout vs Treatment split.
    4. Controlled PII join (only first_name, email/phone required for sending).
    """
    print(f"Generating campaign audience for Segment='{segment_name}', Channel='{channel}'...")

    rfm_path = PROCESSED_DATA_DIR / "customer_rfm.csv"
    contacts_path = RAW_DATA_DIR / "customer_contacts_pii.csv"

    if not rfm_path.exists() or not contacts_path.exists():
        raise FileNotFoundError("Customer RFM or PII contact table missing.")

    df_rfm = pd.read_csv(rfm_path)
    df_contacts = pd.read_csv(contacts_path)

    # 1. Filter by Segment
    if segment_name.lower() != "all":
        df_target = df_rfm[df_rfm["segment"].str.lower() == segment_name.lower()].copy()
    else:
        df_target = df_rfm.copy()

    total_in_segment = len(df_target)

    # 2. Marketing Permissions & Suppression Rules (UK ICO / GDPR Compliance)
    # Channel opt-in requirement
    if channel.lower() == "email":
        consent_filter = df_target["email_opt_in"] == True
    elif channel.lower() == "whatsapp":
        consent_filter = df_target["whatsapp_opt_in"] == True
    elif channel.lower() == "sms":
        consent_filter = df_target["sms_opt_in"] == True
    elif channel.lower() == "push":
        consent_filter = df_target["push_opt_in"] == True
    else:
        consent_filter = True

    # Global suppression filter (opt-outs, legal hold, complaints)
    df_eligible = df_target[consent_filter & (~df_target["suppression_flag"])].copy()
    eligible_count = len(df_eligible)

    # 3. Randomized Holdout Control vs Treatment Split
    np.random.seed(random_seed)
    df_eligible["random_num"] = np.random.uniform(0, 1, size=len(df_eligible))
    df_eligible["campaign_group"] = np.where(
        df_eligible["random_num"] < holdout_pct,
        "CONTROL_HOLDOUT",
        "TREATMENT"
    )

    # 4. Controlled Activation Join with PII Contacts
    # Only export what the activation ESP/SMS engine needs
    df_joined = pd.merge(
        df_eligible,
        df_contacts[["customer_id", "first_name", "last_name", "email", "phone"]],
        on="customer_id",
        how="inner"
    )

    export_cols = [
        "customer_id", "first_name", "email" if channel == "email" else "phone",
        "segment", "rfm_code", "r_score", "f_score", "m_score",
        "recency_days", "qualifying_order_count", "campaign_group"
    ]
    df_export = df_joined[export_cols].copy()

    # Save to Exports directory
    sanitized_seg_name = segment_name.lower().replace(" ", "_").replace("/", "_")
    output_filename = f"audience_{sanitized_seg_name}_{channel}.csv"
    output_path = EXPORTS_DIR / output_filename
    df_export.to_csv(output_path, index=False)

    print(f"Audience Export Complete -> {output_filename}:")
    print(f" - Total in Segment: {total_in_segment:,}")
    print(f" - Eligible (Consented & Unsuppressed): {eligible_count:,} ({eligible_count/max(1, total_in_segment)*100:.1f}%)")
    print(f" - Treatment Group: {(df_export['campaign_group'] == 'TREATMENT').sum():,}")
    print(f" - Control Holdout Group: {(df_export['campaign_group'] == 'CONTROL_HOLDOUT').sum():,}")

    return df_export

def export_all_default_audiences():
    """Generates standard starter audiences for common lifecycle campaigns."""
    campaigns = [
        ("Champions", "email"),
        ("Loyal Customers", "email"),
        ("High-Value, At Risk", "email"),
        ("Recent Customers", "email"),
        ("Need Attention", "sms"),
        ("Lapsed", "email")
    ]
    for seg, ch in campaigns:
        try:
            export_campaign_audience(segment_name=seg, channel=ch, holdout_pct=0.10)
        except Exception as e:
            print(f"Error exporting {seg}: {e}")

if __name__ == "__main__":
    export_all_default_audiences()
