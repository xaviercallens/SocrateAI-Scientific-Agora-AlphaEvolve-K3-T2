import unittest
from core.tier_classifier import TierClassifier


class TestTierClassifier(unittest.TestCase):
    def setUp(self):
        self.classifier = TierClassifier()

    def test_low_tier_classification(self):
        directives = [
            ("Check job queue status", "ROUTE_TASK"),
            ("Aggregate status reports from TPU cluster", "AGGREGATE_STATUS"),
            ("Pre-validate dispatch before running grid", "PRE_VALIDATE_DISPATCH"),
            ("Summarize logs from generation search", "SUMMARIZE_LOGS"),
            ("Format results for BigQuery", "FORMAT_RESULTS"),
            ("Health check endpoint", "HEALTH_CHECK"),
        ]
        for text, expected_action in directives:
            res = self.classifier.classify(text)
            self.assertEqual(res["classified_action"], expected_action)
            self.assertGreaterEqual(res["confidence"], 0.7)

    def test_mid_tier_classification(self):
        directives = [
            ("Analyze loss trajectory for Monge-Ampere residual", "ANALYZE_LOSS_TRAJECTORY"),
            ("Diagnose failure in node 1", "ERROR_RECOVERY"),
            ("Cross-validate results against Kreuzer-Skarke", "CROSS_VALIDATION"),
            ("Recommend parameter grid refinement", "PARAMETER_RECOMMENDATION"),
        ]
        for text, expected_action in directives:
            res = self.classifier.classify(text)
            self.assertEqual(res["classified_action"], expected_action)

    def test_high_tier_classification(self):
        directives = [
            ("Evaluate if this is a novel topology", "NOVEL_TOPOLOGY_EVALUATION"),
            ("Draft publication analysis for journal paper", "PUBLICATION_ANALYSIS"),
            ("Cross-stream synthesis of Stream 2 and Stream 3", "CROSS_STREAM_SYNTHESIS"),
        ]
        for text, expected_action in directives:
            res = self.classifier.classify(text)
            self.assertEqual(res["classified_action"], expected_action)

    def test_low_confidence_escalate(self):
        res = self.classifier.classify("some ambiguous text")
        self.assertTrue(res["escalate"])


if __name__ == "__main__":
    unittest.main()
