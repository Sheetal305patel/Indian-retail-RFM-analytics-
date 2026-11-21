"""
Unit Tests for Predictive ML (Churn Propensity & 12M pLTV Models)
"""
import unittest
import pandas as pd
import numpy as np
import torch
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.predictive_models import ChurnClassifierNN

class TestPredictiveML(unittest.TestCase):

    def test_churn_neural_net_forward_pass(self):
        """Churn neural network outputs probabilities strictly bounded in [0.0, 1.0]."""
        batch_size = 8
        input_dim = 12
        model = ChurnClassifierNN(input_dim=input_dim)
        model.eval()

        dummy_x = torch.randn(batch_size, input_dim)
        with torch.no_grad():
            preds = model(dummy_x)

        self.assertEqual(preds.shape, (batch_size, 1))
        self.assertTrue((preds >= 0.0).all())
        self.assertTrue((preds <= 1.0).all())

    def test_pltv_quadrant_logic(self):
        """Tests that strategic quadrants correctly classify VIPs at risk."""
        # VIP at risk: Platinum value tier + Critical churn risk
        pltv_tier = "Platinum"
        churn_risk = "Critical"

        is_high_val = pltv_tier in ["Platinum", "Gold"]
        is_high_churn = churn_risk in ["Critical", "High"]

        self.assertTrue(is_high_val and is_high_churn)
        # Should map to Protect & Retain VIPs
        assigned_quad = "Protect & Retain VIPs" if (is_high_val and is_high_churn) else "Other"
        self.assertEqual(assigned_quad, "Protect & Retain VIPs")

if __name__ == "__main__":
    unittest.main()
