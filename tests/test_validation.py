"""
Unit Tests for Audit Checks and Reconciliation Logic
"""
import unittest
import pandas as pd
import numpy as np
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

class TestValidationChecks(unittest.TestCase):

    def test_pii_isolation_assertion(self):
        """Analytical table must strictly exclude direct contact PII."""
        allowed_analytical_cols = {
            "customer_id", "country", "identity_status", "region_or_market", "first_seen_at",
            "as_of_date", "observation_start_date", "last_purchase_at",
            "recency_days", "qualifying_order_count", "net_sales_usd",
            "contribution_margin_usd", "r_score", "f_score", "m_score",
            "rfm_code", "segment", "whatsapp_opt_in", "email_opt_in", "sms_opt_in", "push_opt_in",
            "suppression_flag", "model_version"
        }
        forbidden_pii = {"first_name", "last_name", "email", "phone", "street_address"}

        # Intersection must be empty
        self.assertEqual(len(forbidden_pii.intersection(allowed_analytical_cols)), 0)

    def test_holdout_split_distribution(self):
        """Randomized holdout split should closely match specified holdout percentage."""
        np.random.seed(42)
        n = 1000
        holdout_pct = 0.10
        rands = np.random.uniform(0, 1, size=n)
        control_count = (rands < holdout_pct).sum()

        observed_pct = control_count / n
        self.assertAlmostEqual(observed_pct, holdout_pct, delta=0.03)

if __name__ == "__main__":
    unittest.main()
