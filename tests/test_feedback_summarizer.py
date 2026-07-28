import unittest
from pipeline.alphaevolve_search.feedback_summarizer import AlphaEvolveFeedbackSummarizer


class TestFeedbackSummarizer(unittest.TestCase):
    def setUp(self):
        self.summarizer = AlphaEvolveFeedbackSummarizer()

    def test_parse_converging_logs(self):
        logs = [
            "Generation 10/100: Best Monge-Ampere Loss = 7.500000e-01",
            "Generation 50/100: Best Monge-Ampere Loss = 2.373047e-01",
            "Generation 100/100: Best Monge-Ampere Loss = 5.631351e-02",
        ]
        res = self.summarizer.summarize_generation_logs(logs)
        self.assertEqual(res["total_generations"], 3)
        self.assertEqual(res["initial_loss"], 0.75)
        self.assertEqual(res["final_loss"], 0.05631351)
        self.assertEqual(res["recommended_action"], "CONTINUE")

    def test_plateau_detection(self):
        logs = [
            "Generation 80/100: Best Monge-Ampere Loss = 0.150000e+00",
            "Generation 90/100: Best Monge-Ampere Loss = 0.149500e+00",
            "Generation 100/100: Best Monge-Ampere Loss = 0.149200e+00",
        ]
        res = self.summarizer.summarize_generation_logs(logs)
        self.assertTrue(res["plateau_detected"])
        self.assertEqual(res["recommended_action"], "MUTATE_HYPERPARAMS")

    def test_target_loss_reached(self):
        logs = [
            "Generation 10/100: Best Monge-Ampere Loss = 1.000000e-04",
        ]
        res = self.summarizer.summarize_generation_logs(logs)
        self.assertEqual(res["recommended_action"], "TARGET_REACHED")


if __name__ == "__main__":
    unittest.main()
