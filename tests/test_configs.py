import unittest
import os
import yaml


class TestConfigs(unittest.TestCase):
    def _get_config_dir(self):
        return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "configs")

    def test_evolution_nsga2_loads(self):
        path = os.path.join(self._get_config_dir(), "evolution_nsga2.yaml")
        with open(path) as f:
            cfg = yaml.safe_load(f)
        self.assertIn("evolution", cfg)
        self.assertEqual(cfg["evolution"]["algorithm"], "NSGA-II")

    def test_evolution_has_required_keys(self):
        path = os.path.join(self._get_config_dir(), "evolution_nsga2.yaml")
        with open(path) as f:
            cfg = yaml.safe_load(f)["evolution"]
        for key in ["population_size", "max_generations", "random_seed", "genetic_operators"]:
            self.assertIn(key, cfg)

    def test_threshold_bounds_loads(self):
        path = os.path.join(self._get_config_dir(), "threshold_bounds.yaml")
        with open(path) as f:
            cfg = yaml.safe_load(f)
        self.assertIn("bounds", cfg)
        self.assertIn("picard_fuchs", cfg["bounds"])

    def test_tau2_min_positive(self):
        path = os.path.join(self._get_config_dir(), "threshold_bounds.yaml")
        with open(path) as f:
            cfg = yaml.safe_load(f)
        tau2_min = cfg["bounds"]["complex_structure_tau"]["tau2_min"]
        self.assertGreater(tau2_min, 0)


if __name__ == "__main__":
    unittest.main()
