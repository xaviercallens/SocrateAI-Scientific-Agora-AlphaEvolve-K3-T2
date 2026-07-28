import unittest
from core.agent_kit_orchestrator import SocrateAICoordinator, initialize_socrateai_coordinator


class TestOrchestratorMultiModel(unittest.TestCase):
    def setUp(self):
        self.coordinator = SocrateAICoordinator()

    def test_dispatch_directive_low_tier(self):
        res = self.coordinator.dispatch_directive("Check TPU node status and aggregate reports")
        self.assertEqual(res["status"], "SUCCESS")
        self.assertEqual(res["final_tier"], "T-Low")
        self.assertEqual(res["result"]["model_name"], "gemini-2.0-flash-lite")

    def test_dispatch_directive_high_tier(self):
        res = self.coordinator.dispatch_directive("Evaluate if this is a novel topology for paper publication")
        self.assertEqual(res["status"], "SUCCESS")
        self.assertEqual(res["final_tier"], "T-High")
        self.assertEqual(res["result"]["model_name"], "gemini-1.5-ultra")

    def test_backward_compatibility_initializer(self):
        agent = initialize_socrateai_coordinator()
        self.assertIsNotNone(agent)


if __name__ == "__main__":
    unittest.main()
