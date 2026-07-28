import unittest
import numpy as np
from src.alpha_evolve.candidate import K3T2Candidate
from src.alpha_evolve.genetic_operators import (
    polynomial_mutation, gaussian_mutation, sbx_crossover,
    uniform_crossover, kodaira_mutation,
)


class TestGeneticOperators(unittest.TestCase):
    def _make_candidate(self, pf=None, tau=None):
        return K3T2Candidate(
            picard_fuchs_coefficients=np.array(pf or [1.0, -2.0, 0.5, 0.1]),
            complex_structure_tau=tau or complex(0.0, 1.5),
            kahler_modulus_rho=complex(1.0, 1.0),
        )

    def test_polynomial_mutation_produces_child(self):
        rng = np.random.default_rng(42)
        parent = self._make_candidate()
        child = polynomial_mutation(parent, rng, prob=1.0)
        self.assertIsInstance(child, K3T2Candidate)
        self.assertEqual(child.generation, parent.generation + 1)

    def test_polynomial_mutation_preserves_tau2(self):
        rng = np.random.default_rng(42)
        parent = self._make_candidate(tau=complex(0.0, 0.05))
        child = polynomial_mutation(parent, rng, prob=1.0)
        self.assertGreater(child.complex_structure_tau.imag, 0)

    def test_gaussian_mutation_produces_child(self):
        rng = np.random.default_rng(42)
        parent = self._make_candidate()
        child = gaussian_mutation(parent, rng, sigma=0.5, prob=1.0)
        self.assertIsInstance(child, K3T2Candidate)

    def test_gaussian_mutation_clips_bounds(self):
        rng = np.random.default_rng(42)
        parent = self._make_candidate(pf=[9.9, 9.9, 9.9, 9.9])
        child = gaussian_mutation(parent, rng, sigma=5.0, prob=1.0,
                                   bounds={"picard_fuchs": {"coefficient_min": -10, "coefficient_max": 10}})
        for val in child.picard_fuchs_coefficients:
            self.assertGreaterEqual(val, -10.0)
            self.assertLessEqual(val, 10.0)

    def test_sbx_crossover_produces_two_children(self):
        rng = np.random.default_rng(42)
        a = self._make_candidate(pf=[1.0, 2.0, 3.0, 4.0])
        b = self._make_candidate(pf=[5.0, 6.0, 7.0, 8.0])
        c1, c2 = sbx_crossover(a, b, rng)
        self.assertIsInstance(c1, K3T2Candidate)
        self.assertIsInstance(c2, K3T2Candidate)
        self.assertEqual(len(c1.parent_ids), 2)

    def test_sbx_crossover_preserves_tau2(self):
        rng = np.random.default_rng(42)
        a = self._make_candidate(tau=complex(0.0, 0.1))
        b = self._make_candidate(tau=complex(0.0, 0.2))
        c1, c2 = sbx_crossover(a, b, rng)
        self.assertGreater(c1.complex_structure_tau.imag, 0)
        self.assertGreater(c2.complex_structure_tau.imag, 0)

    def test_uniform_crossover_produces_two_children(self):
        rng = np.random.default_rng(42)
        a = self._make_candidate(pf=[1.0, 2.0, 3.0, 4.0])
        b = self._make_candidate(pf=[5.0, 6.0, 7.0, 8.0])
        c1, c2 = uniform_crossover(a, b, rng)
        self.assertIsInstance(c1, K3T2Candidate)
        self.assertIsInstance(c2, K3T2Candidate)

    def test_kodaira_mutation_changes_type(self):
        rng = np.random.default_rng(42)
        parent = self._make_candidate()
        child = kodaira_mutation(parent, rng, prob=1.0)
        self.assertIn(child.kodaira_fiber_type, ["I_1", "I_2", "II", "III", "IV", "IV*", "III*", "II*"])

    def test_kodaira_mutation_preserves_coefficients(self):
        rng = np.random.default_rng(42)
        parent = self._make_candidate()
        child = kodaira_mutation(parent, rng, prob=1.0)
        np.testing.assert_array_almost_equal(child.picard_fuchs_coefficients, parent.picard_fuchs_coefficients)

    def test_deterministic_with_seed(self):
        parent = self._make_candidate()
        c1 = polynomial_mutation(parent, np.random.default_rng(123), prob=1.0)
        c2 = polynomial_mutation(parent, np.random.default_rng(123), prob=1.0)
        np.testing.assert_array_almost_equal(
            c1.picard_fuchs_coefficients, c2.picard_fuchs_coefficients
        )


if __name__ == "__main__":
    unittest.main()
