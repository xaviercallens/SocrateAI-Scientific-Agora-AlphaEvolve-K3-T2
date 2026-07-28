import unittest
import numpy as np
from src.alpha_evolve.cma_es import CMAES


class TestCMAES(unittest.TestCase):
    def test_sphere_function_convergence(self):
        """CMA-ES should optimize the sphere function (sum of squares) to near zero."""
        mean = np.array([5.0, 5.0, 5.0])
        cma = CMAES(mean=mean, sigma=1.0)
        result = cma.optimize(
            objective_fn=lambda x: np.sum(x ** 2),
            max_iterations=100,
            rng=np.random.default_rng(42),
        )
        self.assertLess(result["best_fitness"], 0.1)

    def test_rosenbrock_convergence(self):
        """CMA-ES on 2D Rosenbrock should converge near (1,1)."""
        mean = np.array([0.0, 0.0])
        cma = CMAES(mean=mean, sigma=0.5)

        def rosenbrock(x):
            return (1 - x[0]) ** 2 + 100 * (x[1] - x[0] ** 2) ** 2

        result = cma.optimize(rosenbrock, max_iterations=200, rng=np.random.default_rng(42))
        self.assertLess(result["best_fitness"], 1.0)

    def test_ask_returns_correct_shape(self):
        mean = np.array([0.0, 0.0, 0.0])
        cma = CMAES(mean=mean, sigma=0.5)
        solutions = cma.ask(rng=np.random.default_rng(42))
        self.assertEqual(solutions.shape[1], 3)
        self.assertEqual(solutions.shape[0], cma.lam)

    def test_tell_updates_mean(self):
        mean = np.array([5.0, 5.0])
        cma = CMAES(mean=mean, sigma=1.0)
        rng = np.random.default_rng(42)
        solutions = cma.ask(rng)
        fitnesses = np.array([np.sum(s ** 2) for s in solutions])
        cma.tell(solutions, fitnesses)
        # Mean should move towards origin
        self.assertLess(np.linalg.norm(cma.mean), np.linalg.norm(mean))

    def test_fitness_history_recorded(self):
        mean = np.array([3.0, 3.0])
        cma = CMAES(mean=mean, sigma=1.0)
        result = cma.optimize(lambda x: np.sum(x ** 2), max_iterations=10, rng=np.random.default_rng(42))
        self.assertEqual(len(result["fitness_history"]), result["iterations"])


if __name__ == "__main__":
    unittest.main()
