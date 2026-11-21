"""
Unit Tests for RFM Metric Calculations, Scoring, and Segment Assignment
"""
import unittest
import pandas as pd
import numpy as np
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.rfm_engine import compute_rfm_scores, assign_lifecycle_segment

class TestRFMEngine(unittest.TestCase):

    def test_scoring_monotonicity_and_bounds(self):
        """Scores must strictly be within 1 and 5."""
        test_df = pd.DataFrame({
            "customer_id": [f"C{i}" for i in range(10)],
            "recency_days": [5, 20, 45, 60, 90, 120, 180, 240, 300, 360],
            "frequency": [10, 8, 5, 4, 3, 2, 1, 1, 0, 0],
            "monetary_usd": [1200, 850, 500, 350, 200, 150, 60, 40, 0, 0]
        })

        scored = compute_rfm_scores(test_df)

        self.assertTrue(scored["r_score"].between(1, 5).all())
        self.assertTrue(scored["f_score"].between(1, 5).all())
        self.assertTrue(scored["m_score"].between(1, 5).all())

        # Best customer should receive highest R, F, M
        best_cust = scored.iloc[0]
        self.assertEqual(best_cust["r_score"], 5)
        self.assertEqual(best_cust["f_score"], 5)
        self.assertEqual(best_cust["m_score"], 5)

        # Inactive customer with 0 freq should receive F=1, M=1
        zero_cust = scored.iloc[-1]
        self.assertEqual(zero_cust["f_score"], 1)
        self.assertEqual(zero_cust["m_score"], 1)

    def test_segment_assignment_champions(self):
        """Top tier metrics must map to Champions."""
        row = pd.Series({
            "r_score": 5, "f_score": 5, "m_score": 5,
            "frequency": 12, "recency_days": 10,
            "days_since_first_purchase": 250
        })
        seg = assign_lifecycle_segment(row)
        self.assertEqual(seg, "Champions")

    def test_segment_assignment_high_value_at_risk(self):
        """High historical spend but low recency must map to High-Value, At Risk."""
        row = pd.Series({
            "r_score": 1, "f_score": 4, "m_score": 5,
            "frequency": 8, "recency_days": 210,
            "days_since_first_purchase": 400
        })
        seg = assign_lifecycle_segment(row)
        self.assertEqual(seg, "High-Value, At Risk")

    def test_segment_assignment_new_buyer(self):
        """Customer with recent purchase in onboarding window (<=60 days) maps to Recent Customers."""
        row = pd.Series({
            "r_score": 5, "f_score": 1, "m_score": 2,
            "frequency": 1, "recency_days": 12,
            "days_since_first_purchase": 25 # inside 60-day onboarding window
        })
        seg = assign_lifecycle_segment(row)
        self.assertEqual(seg, "Recent Customers")

    def test_segment_assignment_lapsed(self):
        """Inactive customer with zero orders in window maps to Lapsed."""
        row = pd.Series({
            "r_score": 1, "f_score": 1, "m_score": 1,
            "frequency": 0, "recency_days": 320,
            "days_since_first_purchase": 450
        })
        seg = assign_lifecycle_segment(row)
        self.assertEqual(seg, "Lapsed")

if __name__ == "__main__":
    unittest.main()
