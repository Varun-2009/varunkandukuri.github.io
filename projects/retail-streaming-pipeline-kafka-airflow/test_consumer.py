import tempfile
import unittest
from pathlib import Path

from consumer import persist, valid


class PipelineTest(unittest.TestCase):
    def test_validation_and_deduplication(self):
        event = {"event_id": "1", "event_time": "2026-01-01T00:00:00Z", "store_id": "S001", "product_id": "milk-a2", "quantity": 2, "unit_price": 4.5}
        self.assertTrue(valid(event))
        with tempfile.TemporaryDirectory() as tmp:
            accepted, rejected = persist([event, event, {"bad": True}], Path(tmp) / "retail.db")
        self.assertEqual((accepted, rejected), (1, 1))


if __name__ == "__main__":
    unittest.main()

