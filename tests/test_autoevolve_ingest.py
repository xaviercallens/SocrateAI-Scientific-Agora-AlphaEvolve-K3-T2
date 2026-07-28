import unittest
import os
from src.integration.autoevolve_ingest import load_cooper_seeds, augment_seeds


class TestAutoevolveIngest(unittest.TestCase):
    def _get_seeds_path(self):
        return os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "configs", "cooper_seeds.json"
        )

    def test_load_cooper_seeds(self):
        seeds = load_cooper_seeds(self._get_seeds_path())
        self.assertEqual(len(seeds), 3)

    def test_seed_names_present(self):
        seeds = load_cooper_seeds(self._get_seeds_path())
        types = [s.kodaira_fiber_type for s in seeds]
        self.assertIn("I_1", types)
        self.assertIn("II", types)
        self.assertIn("IV*", types)

    def test_seeds_have_generation_zero(self):
        seeds = load_cooper_seeds(self._get_seeds_path())
        for s in seeds:
            self.assertEqual(s.generation, 0)

    def test_seeds_tau2_positive(self):
        seeds = load_cooper_seeds(self._get_seeds_path())
        for s in seeds:
            self.assertGreater(s.complex_structure_tau.imag, 0)

    def test_augment_seeds_count(self):
        seeds = load_cooper_seeds(self._get_seeds_path())
        augmented = augment_seeds(seeds, n_perturbations=10)
        # 3 originals + 3 * 10 perturbations = 33
        self.assertEqual(len(augmented), 33)

    def test_augmented_tau2_positive(self):
        seeds = load_cooper_seeds(self._get_seeds_path())
        augmented = augment_seeds(seeds, n_perturbations=5)
        for c in augmented:
            self.assertGreater(c.complex_structure_tau.imag, 0)


if __name__ == "__main__":
    unittest.main()
