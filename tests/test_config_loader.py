import unittest
import os
from core.config_loader import load_gemini_config


class TestConfigLoader(unittest.TestCase):
    def test_load_default_config(self):
        cfg = load_gemini_config()
        self.assertIn("gemini_model_config", cfg)
        inner = cfg["gemini_model_config"]
        self.assertIn("tiers", inner)
        self.assertIn("low", inner["tiers"])
        self.assertIn("mid", inner["tiers"])
        self.assertIn("high", inner["tiers"])

    def test_env_override_budget(self):
        os.environ["SOCRATEAI_GEMINI_COST_MANAGEMENT_MONTHLY_BUDGET_USD"] = "250.0"
        try:
            cfg = load_gemini_config()
            budget = cfg["gemini_model_config"]["cost_management"]["monthly_budget_usd"]
            self.assertEqual(budget, 250.0)
        finally:
            del os.environ["SOCRATEAI_GEMINI_COST_MANAGEMENT_MONTHLY_BUDGET_USD"]


if __name__ == "__main__":
    unittest.main()
