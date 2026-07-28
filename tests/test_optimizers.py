import unittest
import numpy as np
from src.alpha_evolve.candidate import K3T2Candidate
from src.alpha_evolve.fitness import FitnessEvaluator
from src.alpha_evolve.optimizers import non_dominated_sort, crowding_distance, evolve_generation, run_nsga2


class TestNonDominatedSort(unittest.TestCase):
    def _make_candidate(self, fit, comp):
        c = K3T2Candidate(picard_fuchs_coefficients=np.array([1.0, 0.0, 0.0, 0.0]),
                          complex_structure_tau=complex(0, 1))
        c.surrogate_fitness = fit
        c.complexity_score = comp
        return c

    def test_single_front(self):
        pop = [self._make_candidate(0.9, 0.9), self._make_candidate(0.5, 0.5)]
        fronts = non_dominated_sort(pop)
        # Neither dominates the other → single front
        self.assertEqual(len(fronts[0]), 2)

    def test_two_fronts(self):
        a = self._make_candidate(0.9, 0.1)  # Dominates b
        b = self._make_candidate(0.5, 0.5)
        pop = [a, b]
        fronts = non_dominated_sort(pop)
        self.assertEqual(len(fronts), 2)
        self.assertIn(0, fronts[0])
        self.assertIn(1, fronts[1])

    def test_three_candidates(self):
        # In minimization space: obj = (-fit, comp)
        # a: (-0.9, 0.1) dominates both b: (-0.1, 0.9) and c: (-0.5, 0.5)
        a = self._make_candidate(0.9, 0.1)  # Best on both objectives
        b = self._make_candidate(0.1, 0.9)  # Worst on both
        c = self._make_candidate(0.5, 0.5)  # Middle
        pop = [a, b, c]
        fronts = non_dominated_sort(pop)
        # a dominates everything → front 0 = {a}
        self.assertEqual(len(fronts[0]), 1)
        self.assertIn(0, fronts[0])  # a is on front 0


class TestCrowdingDistance(unittest.TestCase):
    def _make_candidate(self, fit, comp):
        c = K3T2Candidate(picard_fuchs_coefficients=np.array([1.0, 0.0, 0.0, 0.0]),
                          complex_structure_tau=complex(0, 1))
        c.surrogate_fitness = fit
        c.complexity_score = comp
        return c

    def test_boundary_solutions_get_infinity(self):
        pop = [self._make_candidate(0.1, 0.9),
               self._make_candidate(0.5, 0.5),
               self._make_candidate(0.9, 0.1)]
        front = [0, 1, 2]
        cd = crowding_distance(pop, front)
        self.assertEqual(cd[0], float("inf"))
        self.assertEqual(cd[2], float("inf"))

    def test_small_front_all_infinity(self):
        pop = [self._make_candidate(0.5, 0.5), self._make_candidate(0.9, 0.1)]
        front = [0, 1]
        cd = crowding_distance(pop, front)
        self.assertEqual(cd[0], float("inf"))
        self.assertEqual(cd[1], float("inf"))


class TestEvolveGeneration(unittest.TestCase):
    def test_evolve_generation_returns_correct_size(self):
        pop_size = 20
        pop = []
        rng = np.random.default_rng(42)
        for _ in range(pop_size):
            c = K3T2Candidate(
                picard_fuchs_coefficients=rng.uniform(-5, 5, 4),
                complex_structure_tau=complex(rng.uniform(-0.5, 0.5), rng.uniform(0.1, 3)),
            )
            pop.append(c)

        evaluator = FitnessEvaluator()
        config = {"population_size": pop_size, "genetic_operators": {
            "crossover": {"eta_c": 20.0, "probability": 0.9},
            "mutation": {"eta_m": 20.0, "probability": 0.1},
            "kodaira_mutation": {"probability": 0.05},
        }}

        new_pop = evolve_generation(pop, evaluator, rng, config)
        self.assertEqual(len(new_pop), pop_size)


class TestRunNSGA2(unittest.TestCase):
    def test_smoke_run(self):
        rng = np.random.default_rng(42)
        pop = []
        for _ in range(20):
            c = K3T2Candidate(
                picard_fuchs_coefficients=rng.uniform(-5, 5, 4),
                complex_structure_tau=complex(rng.uniform(-0.5, 0.5), rng.uniform(0.1, 3)),
            )
            pop.append(c)

        config = {
            "population_size": 20,
            "max_generations": 5,
            "random_seed": 42,
            "genetic_operators": {
                "crossover": {"eta_c": 20.0, "probability": 0.9},
                "mutation": {"eta_m": 20.0, "probability": 0.1},
                "kodaira_mutation": {"probability": 0.05},
            },
            "logging": {"log_every_n_generations": 5},
        }

        evaluator = FitnessEvaluator()
        result = run_nsga2(pop, evaluator, config)
        self.assertEqual(result["status"], "CONVERGED")
        self.assertGreater(result["pareto_front_size"], 0)
        self.assertEqual(len(result["final_population"]), 20)


if __name__ == "__main__":
    unittest.main()
