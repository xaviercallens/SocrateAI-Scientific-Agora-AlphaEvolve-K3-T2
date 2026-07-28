import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pipeline.alphaevolve_search.cy4_metric_search import (
    load_kreuzer_skarke_data,
    evaluate_monge_ampere_loss,
    run_alphaevolve_search
)

class TestAlphaEvolveSearch(unittest.TestCase):
    def test_load_kreuzer_skarke_data(self):
        data = load_kreuzer_skarke_data("KS-X4-001")
        self.assertEqual(data["poly_id"], "KS-X4-001")
        self.assertEqual(data["h11"], 4)
        self.assertEqual(data["h31"], 22)

    def test_evaluate_monge_ampere_loss(self):
        predicted = [1.0, 2.0, 3.0]
        target = [1.0, 2.0, 3.0]
        loss = evaluate_monge_ampere_loss(predicted, target)
        self.assertAlmostEqual(loss, 0.0)

        predicted_diff = [1.5, 2.5, 3.5]
        loss_diff = evaluate_monge_ampere_loss(predicted_diff, target)
        self.assertAlmostEqual(loss_diff, 0.25)

    def test_run_alphaevolve_search(self):
        results = run_alphaevolve_search(iterations=100)
        self.assertEqual(results["status"], "SUCCESS")
        self.assertLess(results["min_loss"], 1.0)

if __name__ == '__main__':
    unittest.main()
