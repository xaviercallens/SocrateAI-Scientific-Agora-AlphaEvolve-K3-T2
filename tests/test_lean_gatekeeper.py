import unittest
from src.integration.lean_client import LeanOracleClient, _simulated_lean_verify
from src.alpha_evolve.lean_gatekeeper import tier2_lean_gatekeeper


class TestLeanGatekeeper(unittest.TestCase):
    def test_simulated_lean_verify_pass(self):
        cand = {
            "candidate_id": "cand_001",
            "picard_number": 16,
            "moduli_stabilization": 0.42,
            "complex_structure": [1.0, 1.0, 2.0, 2.0],
        }
        res = _simulated_lean_verify(cand)
        self.assertTrue(res["passed_swampland"])
        self.assertTrue(res["uv_complete"])
        self.assertEqual(res["penalty_score"], 0.0)
        self.assertIn("Distance and dS conjectures satisfied", res["formal_reason"])

    def test_simulated_lean_verify_fail_unstable(self):
        cand = {
            "candidate_id": "cand_002",
            "picard_number": 16,
            "moduli_stabilization": -0.1,  # Unstable
            "complex_structure": [1.0, 1.0, 2.0, 2.0],
        }
        res = _simulated_lean_verify(cand)
        self.assertFalse(res["passed_swampland"])
        self.assertFalse(res["uv_complete"])
        self.assertEqual(res["penalty_score"], 9999.9)

    def test_simulated_lean_verify_fail_picard(self):
        cand = {
            "candidate_id": "cand_003",
            "picard_number": 25,  # Exceeds max picard of 20
            "moduli_stabilization": 0.5,
            "complex_structure": [1.0, 1.0, 2.0, 2.0],
        }
        res = _simulated_lean_verify(cand)
        self.assertFalse(res["passed_swampland"])

    def test_lean_oracle_client_batch(self):
        with LeanOracleClient() as client:
            candidates = [
                {"candidate_id": "c1", "picard_number": 10, "moduli_stabilization": 0.5, "complex_structure": [1, 2]},
                {"candidate_id": "c2", "picard_number": 22, "moduli_stabilization": 0.5, "complex_structure": [1, 2]},
            ]
            results = client.batch_evaluate(candidates)
            self.assertEqual(len(results), 2)
            self.assertTrue(results[0]["passed_swampland"])
            self.assertFalse(results[1]["passed_swampland"])

    def test_tier2_lean_gatekeeper_filtering(self):
        tier1_survivors = [
            {"candidate_id": "c1", "picard_number": 12, "moduli_stabilization": 0.5, "weights": [1, 1, 2, 2]},
            {"candidate_id": "c2", "picard_number": 22, "moduli_stabilization": 0.5, "weights": [1, 1, 2, 2]},  # Fails picard
            {"candidate_id": "c3", "picard_number": 15, "moduli_stabilization": -0.2, "weights": [1, 1, 2, 2]}, # Fails stability
        ]
        proven, stats = tier2_lean_gatekeeper(tier1_survivors)
        self.assertEqual(len(proven), 1)
        self.assertEqual(proven[0]["candidate_id"], "c1")
        self.assertEqual(stats["input_count"], 3)
        self.assertEqual(stats["passed_count"], 1)
        self.assertEqual(stats["failed_count"], 2)


if __name__ == "__main__":
    unittest.main()
