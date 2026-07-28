import unittest
from core.agent_kit_orchestrator import SocrateAICoordinator
from pipeline.alphaevolve_search.feedback_summarizer import AlphaEvolveFeedbackSummarizer
from pipeline.antigravity_compute.dispatch_pre_validator import TPUDispatchPreValidator


class TestGeminiTieredE2E(unittest.TestCase):
    def setUp(self):
        self.coordinator = SocrateAICoordinator()
        self.summarizer = AlphaEvolveFeedbackSummarizer()
        self.pre_validator = TPUDispatchPreValidator()

    def test_scenario_1_simple_routing(self):
        res = self.coordinator.dispatch_directive("Check AlphaEvolve job status")
        self.assertEqual(res["status"], "SUCCESS")
        self.assertEqual(res["final_tier"], "T-Low")

    def test_scenario_2_loss_analysis(self):
        res = self.coordinator.dispatch_directive("Analyze Monge-Ampere loss trajectory")
        self.assertEqual(res["status"], "SUCCESS")
        self.assertEqual(res["final_tier"], "T-Mid")

    def test_scenario_3_novel_topology(self):
        res = self.coordinator.dispatch_directive("Evaluate if this topology is publishable")
        self.assertEqual(res["status"], "SUCCESS")
        self.assertEqual(res["final_tier"], "T-High")

    def test_scenario_4_full_pipeline_flow(self):
        # 1. Pre-validate dispatch
        val_res = self.pre_validator.validate_dispatch()
        self.assertTrue(val_res["dispatch_allowed"])

        # 2. Process logs with Flash summarizer
        logs = [
            "Generation 10/100: Best Monge-Ampere Loss = 7.500000e-01",
            "Generation 100/100: Best Monge-Ampere Loss = 5.631351e-02",
        ]
        sum_res = self.summarizer.summarize_generation_logs(logs)
        self.assertEqual(sum_res["recommended_action"], "CONTINUE")

        # 3. Route directive
        coord_res = self.coordinator.dispatch_directive("Summarize logs and pre-validate TPU dispatch")
        self.assertEqual(coord_res["status"], "SUCCESS")
        self.assertEqual(coord_res["final_tier"], "T-Low")


if __name__ == "__main__":
    unittest.main()
