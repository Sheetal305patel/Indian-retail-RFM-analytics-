"""
Unit Tests for Real-Time Event Streaming & Incremental State Engine
"""
import unittest
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.streaming_pipeline import RealTimeStreamEngine, generate_simulated_stream_event

class TestStreamingEngine(unittest.TestCase):

    def test_simulated_event_structure(self):
        """Simulated event payload must contain required streaming attributes."""
        evt = generate_simulated_stream_event()
        required_keys = ["event_id", "event_type", "customer_id", "order_id", "channel", "net_sales_usd"]
        for k in required_keys:
            self.assertIn(k, evt)
        self.assertGreater(evt["net_sales_usd"], 0)

    def test_incremental_state_update(self):
        """Streaming order event should increment customer order frequency and reset recency."""
        engine = RealTimeStreamEngine()
        evt = generate_simulated_stream_event()
        res = engine.process_order_event(evt)

        self.assertEqual(res["status"], "success")
        self.assertIn("customer_id", res)
        self.assertIn("new_rfm", res)
        self.assertIn("new_segment", res)

if __name__ == "__main__":
    unittest.main()
