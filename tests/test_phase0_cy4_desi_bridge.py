import unittest
import numpy as np
from pipeline.alphaevolve_search.cy4_metric_search import (
    generate_mutated_cy4_weights,
    crossover_cy4_weights,
    tier1_fast_surrogate_filter,
    load_kreuzer_skarke_data,
)
from pipeline.alphaevolve_search.mock_symbolic_gatekeeper import (
    mock_topological_gatekeeper,
    filter_population_tier2,
)
from pipeline.antigravity_compute.cobaya_tpu_dispatcher import (
    cy4_to_dark_energy_phenotype,
    evaluate_desi_bao_likelihood,
    evaluate_tier3_tpu_batch,
    TARGET_W0,
    TARGET_OMEGA_M,
)
from scripts.run_phase0_cy4_desi_mvp import run_phase0_calibration_bridge


class TestPhase0CY4DESIBridge(unittest.TestCase):
    def test_load_kreuzer_skarke_data(self):
        data = load_kreuzer_skarke_data("KS-X4-001")
        self.assertEqual(data["poly_id"], "KS-X4-001")
        self.assertEqual(len(data["weights"]), 6)
        self.assertEqual(data["degree"], 8)

    def test_generate_mutated_cy4_weights(self):
        rng = np.random.default_rng(42)
        initial = [1, 1, 1, 1, 2, 2]
        mutated = generate_mutated_cy4_weights(initial, rng, mutation_rate=1.0)
        self.assertEqual(len(mutated), 6)
        self.assertTrue(all(w >= 1 for w in mutated))

    def test_crossover_cy4_weights(self):
        rng = np.random.default_rng(42)
        p1 = [1, 1, 1, 1, 2, 2]
        p2 = [2, 2, 2, 2, 1, 1]
        child = crossover_cy4_weights(p1, p2, rng)
        self.assertEqual(len(child), 6)
        for i, val in enumerate(child):
            self.assertIn(val, [p1[i], p2[i]])

    def test_tier1_fast_surrogate_filter(self):
        candidates = [
            [1, 1, 1, 1, 2, 2],
            [1, 1, 1, 1, 1, 10],  # Singular (max_w > d/2)
            [2, 2, 2, 2, 2, 2],
            [1, 2, 1, 2, 1, 2],
            [1, 1, 1, 1, 1, 20],  # Extremely singular
        ]
        survivors, stats = tier1_fast_surrogate_filter(candidates, cull_fraction=0.60)
        self.assertLess(len(survivors), len(candidates))
        self.assertGreaterEqual(stats["cull_percentage"], 40.0)

    def test_tier2_mock_symbolic_gatekeeper_valid(self):
        valid, reason, meta = mock_topological_gatekeeper([1, 1, 1, 1, 2, 2])
        self.assertTrue(valid)
        self.assertEqual(reason, "PASSED_SYMBOLIC_GATEKEEPER")
        self.assertEqual(meta["penalty"], 0.0)

    def test_tier2_mock_symbolic_gatekeeper_odd_degree(self):
        valid, reason, meta = mock_topological_gatekeeper([1, 1, 1, 1, 1, 2])  # sum = 7 (odd)
        self.assertFalse(valid)
        self.assertIn("ODD_DEGREE", reason)
        self.assertEqual(meta["penalty"], float("inf"))

    def test_tier2_mock_symbolic_gatekeeper_singular(self):
        valid, reason, meta = mock_topological_gatekeeper([1, 1, 1, 1, 2, 10])  # sum=16 (even), max_w=10 > d/2=8
        self.assertFalse(valid)
        self.assertIn("SINGULAR_HYPERSURFACE", reason)

    def test_filter_population_tier2(self):
        pop = [
            [1, 1, 1, 1, 2, 2],  # Valid
            [1, 1, 1, 1, 1, 2],  # Odd sum
            [2, 2, 2, 2, 2, 2],  # Valid
        ]
        passed, stats = filter_population_tier2(pop)
        self.assertEqual(len(passed), 2)
        self.assertEqual(stats["failed_count"], 1)

    def test_cy4_to_dark_energy_phenotype(self):
        weights = [1, 1, 1, 1, 2, 2]
        pheno = cy4_to_dark_energy_phenotype(weights)
        self.assertIn("w0", pheno)
        self.assertIn("omega_m", pheno)
        self.assertIn("h0", pheno)

    def test_evaluate_desi_bao_likelihood(self):
        pheno = {"w0": -1.00, "omega_m": 0.30, "h0": 67.4}
        likelihood = evaluate_desi_bao_likelihood(pheno)
        self.assertAlmostEqual(likelihood["chi2"], 0.0, places=5)
        self.assertAlmostEqual(likelihood["fitness"], 1.0, places=5)

    def test_evaluate_tier3_tpu_batch(self):
        candidates = [[1, 1, 1, 1, 2, 2], [2, 2, 2, 2, 2, 2]]
        results = evaluate_tier3_tpu_batch(candidates, tpu_eval_delay_per_candidate=0.0)
        self.assertEqual(len(results), 2)
        self.assertIn("chi2", results[0])
        self.assertLessEqual(results[0]["chi2"], results[1]["chi2"])  # Sorted best first

    def test_run_phase0_calibration_bridge_execution(self):
        result = run_phase0_calibration_bridge(n_generations=5, population_size=20, seed=42)
        self.assertEqual(result["status"], "CONVERGED")
        self.assertEqual(result["generations_completed"], 5)
        self.assertGreater(result["tpu_reduction_efficacy_pct"], 50.0)
        self.assertIn("best_candidate", result)

        # Check elitism (monotonic non-increasing chi2)
        gen_logs = result["generation_logs"]
        best_chi2_history = [log["best_chi2"] for log in gen_logs]
        for i in range(1, len(best_chi2_history)):
            self.assertLessEqual(
                best_chi2_history[i],
                best_chi2_history[i - 1] + 1e-9,
                f"Elitism failure at gen {i+1}: chi2 regressed from {best_chi2_history[i-1]} to {best_chi2_history[i]}",
            )

        # Check strict gatekeeper conditioning (if tier2_passed == 0, tier3_tpu_calls must be 0)
        for log in gen_logs:
            if log["tier2_passed"] == 0:
                self.assertEqual(log["tier3_tpu_calls"], 0)

        # Check execution timing (> 0.01 seconds for 5 generations)
        self.assertGreater(result["elapsed_seconds"], 0.01)


if __name__ == "__main__":
    unittest.main()

