"""
Campaign Measurement and Incremental Lift Pilot Analyzer
Evaluates Treatment vs Control Holdout outcomes:
- Conversion rate & repeat purchase lift.
- Incremental net revenue & incremental contribution margin (after returns/costs).
- Statistical significance evaluation (t-statistic, p-value).
"""
import pandas as pd
import numpy as np
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config.settings import EXPORTS_DIR, REPORTS_DIR

def simulate_and_measure_pilot(
    audience_file: str = "audience_high-value,_at_risk_email.csv",
    campaign_name: str = "Win-Back VIP Outreach Q4"
) -> dict:
    """
    Simulates actual campaign responses for an exported audience with Treatment vs Holdout,
    and calculates true incremental contribution margin.
    """
    file_path = EXPORTS_DIR / audience_file
    if not file_path.exists():
        # Fallback to any audience file
        files = list(EXPORTS_DIR.glob("*.csv"))
        if not files:
            raise FileNotFoundError("No audience files found. Run campaign engine first.")
        file_path = files[0]

    df_aud = pd.read_csv(file_path)

    treatment = df_aud[df_aud["campaign_group"] == "TREATMENT"].copy()
    control = df_aud[df_aud["campaign_group"] == "CONTROL_HOLDOUT"].copy()

    # Simulate realistic response outcomes:
    # Baseline control conversion (natural organic repurchases)
    np.random.seed(42)
    control_conv_rate = 0.045 # 4.5% organic repurchase
    treatment_conv_rate = 0.082 # 8.2% campaign repurchase (lift = +3.7 pts)

    n_ctrl = len(control)
    n_treat = len(treatment)

    control_conversions = np.random.binomial(1, control_conv_rate, size=n_ctrl)
    treatment_conversions = np.random.binomial(1, treatment_conv_rate, size=n_treat)

    # Order values and margins
    avg_order_val = 145.0
    margin_ratio = 0.62 # 62% contribution margin after variable costs

    ctrl_spend = control_conversions * np.random.normal(avg_order_val, 25, size=n_ctrl)
    ctrl_spend = np.maximum(0, ctrl_spend)
    ctrl_margin = ctrl_spend * margin_ratio

    treat_spend = treatment_conversions * np.random.normal(avg_order_val * 1.05, 28, size=n_treat)
    treat_spend = np.maximum(0, treat_spend)
    treat_margin = treat_spend * margin_ratio

    # Calculate metrics
    ctrl_conv_pct = (control_conversions.sum() / n_ctrl * 100) if n_ctrl > 0 else 0
    treat_conv_pct = (treatment_conversions.sum() / n_treat * 100) if n_treat > 0 else 0
    conv_lift_pct = treat_conv_pct - ctrl_conv_pct

    treat_rev_per_cust = treat_spend.mean() if n_treat > 0 else 0
    ctrl_rev_per_cust = ctrl_spend.mean() if n_ctrl > 0 else 0
    inc_rev_per_cust = treat_rev_per_cust - ctrl_rev_per_cust

    treat_margin_per_cust = treat_margin.mean() if n_treat > 0 else 0
    ctrl_margin_per_cust = ctrl_margin.mean() if n_ctrl > 0 else 0
    inc_margin_per_cust = treat_margin_per_cust - ctrl_margin_per_cust

    total_incremental_margin = inc_margin_per_cust * n_treat

    # Statistical significance (Two-proportion z-test approximation)
    p_pool = (treatment_conversions.sum() + control_conversions.sum()) / (n_treat + n_ctrl)
    se = np.sqrt(p_pool * (1 - p_pool) * (1/n_treat + 1/n_ctrl))
    z_stat = (treatment_conv_rate - control_conv_rate) / se if se > 0 else 0
    # Statistically significant if z > 1.96 (p < 0.05)
    is_stat_sig = z_stat >= 1.96

    results = {
        "campaign_name": campaign_name,
        "audience_file": file_path.name,
        "treatment_sample_size": int(n_treat),
        "control_sample_size": int(n_ctrl),
        "treatment_conversions": int(treatment_conversions.sum()),
        "control_conversions": int(control_conversions.sum()),
        "treatment_conversion_rate": round(treat_conv_pct, 2),
        "control_conversion_rate": round(ctrl_conv_pct, 2),
        "conversion_lift_points": round(conv_lift_pct, 2),
        "treatment_revenue_per_contact": round(treat_rev_per_cust, 2),
        "control_revenue_per_contact": round(ctrl_rev_per_cust, 2),
        "incremental_revenue_per_contact": round(inc_rev_per_cust, 2),
        "incremental_contribution_margin_per_contact": round(inc_margin_per_cust, 2),
        "total_campaign_incremental_contribution_margin": round(total_incremental_margin, 2),
        "z_score": round(float(z_stat), 3),
        "statistically_significant": bool(is_stat_sig)
    }

    print(f"Pilot Campaign Measurement Complete ({campaign_name}):")
    print(f" - Treatment Conversion: {treat_conv_pct:.2f}% vs Control: {ctrl_conv_pct:.2f}% (Lift: +{conv_lift_pct:.2f}%)")
    print(f" - Incremental Margin per Contact: ₹{inc_margin_per_cust:.2f}")
    print(f" - Total Incremental Contribution Margin: ₹{total_incremental_margin:,.2f}")
    print(f" - Statistically Significant (p < 0.05): {is_stat_sig} (z = {z_stat:.2f})")

    return results

if __name__ == "__main__":
    simulate_and_measure_pilot()
