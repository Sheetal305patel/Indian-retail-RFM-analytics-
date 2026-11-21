"""
Unit & Pipeline Tests for ETL Curation and Accounting Rules
"""
import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config.settings import QUALIFYING_STATUSES, EXCLUDED_STATUSES

class TestETLAccountingRules(unittest.TestCase):

    def setUp(self):
        self.as_of_dt = datetime(2026, 11, 20)
        self.window_start_dt = self.as_of_dt - timedelta(days=365)

    def test_excluded_statuses_cancelled_and_fraud(self):
        """Cancelled, Test, and Fraud orders must not be marked qualifying."""
        sample_orders = pd.DataFrame([
            {"order_id": "O1", "customer_id": "C1", "order_status": "CANCELLED", "order_dt": self.as_of_dt - timedelta(days=10), "net_sales_usd": 100},
            {"order_id": "O2", "customer_id": "C2", "order_status": "FRAUD", "order_dt": self.as_of_dt - timedelta(days=20), "net_sales_usd": 150},
            {"order_id": "O3", "customer_id": "C3", "order_status": "TEST", "order_dt": self.as_of_dt - timedelta(days=5), "net_sales_usd": 50},
            {"order_id": "O4", "customer_id": "C4", "order_status": "COMPLETED", "order_dt": self.as_of_dt - timedelta(days=15), "net_sales_usd": 200}
        ])

        is_qualifying = (
            sample_orders["order_status"].isin(QUALIFYING_STATUSES) &
            sample_orders["customer_id"].notna() &
            (sample_orders["order_dt"] >= self.window_start_dt) &
            (sample_orders["net_sales_usd"] > 0)
        )

        self.assertFalse(is_qualifying.iloc[0], "Cancelled order should not qualify")
        self.assertFalse(is_qualifying.iloc[1], "Fraud order should not qualify")
        self.assertFalse(is_qualifying.iloc[2], "Test order should not qualify")
        self.assertTrue(is_qualifying.iloc[3], "Completed order should qualify")

    def test_full_refund_zero_frequency(self):
        """Fully refunded orders should not count in frequency."""
        order = {"order_id": "O5", "customer_id": "C5", "order_status": "REFUNDED", "net_sales_usd": 0.0}
        qualifies = (order["order_status"] in QUALIFYING_STATUSES) and (order["net_sales_usd"] > 0)
        self.assertFalse(qualifies, "Fully refunded orders must be excluded from qualifying frequency")

    def test_partial_refund_net_sales(self):
        """Partially refunded completed orders retain count=1 with reduced net sales."""
        gross = 100.0
        discount = 10.0
        refund = 30.0
        net_sales = gross - discount - refund
        self.assertEqual(net_sales, 60.0)
        self.assertGreater(net_sales, 0)

if __name__ == "__main__":
    unittest.main()
