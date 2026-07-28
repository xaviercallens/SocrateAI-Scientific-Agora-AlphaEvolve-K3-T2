import unittest
import numpy as np
from src.alpha_evolve.candidate import K3T2Candidate


class TestK3T2Candidate(unittest.TestCase):
    def _make_candidate(self, **kwargs):
        defaults = {
            "picard_fuchs_coefficients": np.array([1.0, -2.0, 0.5, 0.1]),
            "complex_structure_tau": complex(0.0, 1.0),
            "kahler_modulus_rho": complex(1.0, 1.0),
        }
        defaults.update(kwargs)
        return K3T2Candidate(**defaults)

    def test_creation(self):
        c = self._make_candidate()
        self.assertEqual(len(c.picard_fuchs_coefficients), 4)
        self.assertEqual(c.kodaira_fiber_type, "I_1")
        self.assertEqual(c.generation, 0)

    def test_tau2_positive_validation(self):
        with self.assertRaises(ValueError):
            self._make_candidate(complex_structure_tau=complex(0.0, -1.0))

    def test_tau2_zero_validation(self):
        with self.assertRaises(ValueError):
            self._make_candidate(complex_structure_tau=complex(0.0, 0.0))

    def test_feature_vector_round_trip(self):
        c = self._make_candidate()
        vec = c.to_feature_vector()
        self.assertEqual(len(vec), 8)  # 4 PF + τ₁ + τ₂ + ρ₁ + ρ₂
        c2 = K3T2Candidate.from_feature_vector(vec, pf_order=4)
        np.testing.assert_array_almost_equal(c2.picard_fuchs_coefficients, c.picard_fuchs_coefficients)

    def test_to_dict_from_dict_round_trip(self):
        c = self._make_candidate(generation=5, kodaira_fiber_type="IV*")
        d = c.to_dict()
        c2 = K3T2Candidate.from_dict(d)
        np.testing.assert_array_almost_equal(c2.picard_fuchs_coefficients, c.picard_fuchs_coefficients)
        self.assertEqual(c2.kodaira_fiber_type, "IV*")
        self.assertEqual(c2.generation, 5)
        self.assertEqual(c2.candidate_id, c.candidate_id)

    def test_feature_dim_property(self):
        c = self._make_candidate()
        self.assertEqual(c.feature_dim, 8)

    def test_list_input_coercion(self):
        c = K3T2Candidate(picard_fuchs_coefficients=[1.0, 2.0, 3.0])
        self.assertIsInstance(c.picard_fuchs_coefficients, np.ndarray)

    def test_auto_generated_id(self):
        c1 = self._make_candidate()
        c2 = self._make_candidate()
        self.assertNotEqual(c1.candidate_id, c2.candidate_id)

    def test_from_feature_vector_enforces_tau2(self):
        vec = np.array([1.0, 2.0, 3.0, 4.0, 0.1, -5.0, 1.0, 1.0])
        c = K3T2Candidate.from_feature_vector(vec, pf_order=4)
        self.assertGreater(c.complex_structure_tau.imag, 0)

    def test_hodge_defaults(self):
        c = self._make_candidate()
        self.assertEqual(c.hodge_numbers["h11"], 3)
        self.assertEqual(c.hodge_numbers["h21"], 19)


if __name__ == "__main__":
    unittest.main()
