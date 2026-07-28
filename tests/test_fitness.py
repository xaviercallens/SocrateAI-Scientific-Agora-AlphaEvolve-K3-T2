import unittest
import numpy as np
from src.alpha_evolve.candidate import K3T2Candidate
from src.alpha_evolve.fitness import FitnessEvaluator


class TestFitnessEvaluator(unittest.TestCase):
    def _make_candidate(self, pf=None, tau=None):
        return K3T2Candidate(
            picard_fuchs_coefficients=np.array(pf or [1.0, -2.0, 0.5, 0.1]),
            complex_structure_tau=tau or complex(0.0, 1.5),
        )

    def setUp(self):
        self.evaluator = FitnessEvaluator()

    def test_evaluate_complexity_range(self):
        c = self._make_candidate()
        score = self.evaluator.evaluate_complexity(c)
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)

    def test_high_complexity_candidate(self):
        c = self._make_candidate(pf=[9.0, 9.0, 9.0, 9.0])
        score = self.evaluator.evaluate_complexity(c)
        self.assertGreater(score, 0.8)

    def test_low_complexity_candidate(self):
        c = self._make_candidate(pf=[0.1, 0.0, 0.0, 0.0])
        score = self.evaluator.evaluate_complexity(c)
        self.assertLess(score, 0.1)

    def test_evaluate_tier1_sets_fitness(self):
        c = self._make_candidate()
        result = self.evaluator.evaluate_tier1(c)
        self.assertIsNotNone(result.surrogate_fitness)
        self.assertIsNotNone(result.complexity_score)

    def test_evaluate_tier2_stub(self):
        c = self._make_candidate()
        result = self.evaluator.evaluate_tier2(c)
        self.assertIsNone(result.lean_swampland_valid)

    def test_evaluate_tier3_stub(self):
        c = self._make_candidate()
        result = self.evaluator.evaluate_tier3(c)
        self.assertIsNone(result.empirical_chi2)

    def test_evaluate_population_batch(self):
        candidates = [self._make_candidate(pf=[float(i), 0.0, 0.0, 0.0]) for i in range(10)]
        results = self.evaluator.evaluate_population(candidates)
        self.assertEqual(len(results), 10)
        for c in results:
            self.assertIsNotNone(c.surrogate_fitness)

    def test_dominates_true(self):
        a = self._make_candidate()
        a.surrogate_fitness = 0.9
        a.complexity_score = 0.1
        b = self._make_candidate()
        b.surrogate_fitness = 0.5
        b.complexity_score = 0.5
        self.assertTrue(FitnessEvaluator.dominates(a, b))

    def test_dominates_false_neither(self):
        a = self._make_candidate()
        a.surrogate_fitness = 0.9
        a.complexity_score = 0.9
        b = self._make_candidate()
        b.surrogate_fitness = 0.5
        b.complexity_score = 0.1
        self.assertFalse(FitnessEvaluator.dominates(a, b))

    def test_dominates_false_equal(self):
        a = self._make_candidate()
        a.surrogate_fitness = 0.5
        a.complexity_score = 0.5
        b = self._make_candidate()
        b.surrogate_fitness = 0.5
        b.complexity_score = 0.5
        self.assertFalse(FitnessEvaluator.dominates(a, b))


if __name__ == "__main__":
    unittest.main()
