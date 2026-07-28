"""
CMA-ES (Covariance Matrix Adaptation Evolution Strategy) for fine-tuning
continuous T² torus moduli (τ, ρ) of elite K3×T² candidates.
Based on Hansen & Ostermeier (2001).
"""

import numpy as np
from typing import Callable, Dict, Any, Optional


class CMAES:
    """
    CMA-ES optimizer for continuous parameter refinement.
    Adapts the covariance matrix of a multivariate Gaussian to match the local
    fitness landscape, enabling efficient search in continuous moduli spaces.
    """

    def __init__(
        self,
        mean: np.ndarray,
        sigma: float = 0.3,
        population_size: Optional[int] = None,
    ):
        self.dim = len(mean)
        self.mean = mean.astype(np.float64).copy()
        self.sigma = sigma

        # Population size (default: 4 + floor(3 * ln(n)))
        self.lam = population_size or (4 + int(3 * np.log(self.dim)))
        self.mu = self.lam // 2

        # Recombination weights (log-linear)
        raw_weights = np.log(self.mu + 0.5) - np.log(np.arange(1, self.mu + 1))
        self.weights = raw_weights / np.sum(raw_weights)
        self.mu_eff = 1.0 / np.sum(self.weights ** 2)

        # Step-size control parameters
        self.cs = (self.mu_eff + 2.0) / (self.dim + self.mu_eff + 5.0)
        self.ds = 1.0 + 2.0 * max(0, np.sqrt((self.mu_eff - 1.0) / (self.dim + 1.0)) - 1.0) + self.cs
        self.chi_n = np.sqrt(self.dim) * (1.0 - 1.0 / (4.0 * self.dim) + 1.0 / (21.0 * self.dim ** 2))

        # Covariance matrix adaptation parameters
        self.cc = (4.0 + self.mu_eff / self.dim) / (self.dim + 4.0 + 2.0 * self.mu_eff / self.dim)
        self.c1 = 2.0 / ((self.dim + 1.3) ** 2 + self.mu_eff)
        self.cmu = min(
            1.0 - self.c1,
            2.0 * (self.mu_eff - 2.0 + 1.0 / self.mu_eff) / ((self.dim + 2.0) ** 2 + self.mu_eff),
        )

        # Evolution paths
        self.ps = np.zeros(self.dim)
        self.pc = np.zeros(self.dim)

        # Covariance matrix and its decomposition
        self.C = np.eye(self.dim)
        self.invsqrtC = np.eye(self.dim)
        self.eigeneval = 0
        self.generation = 0

    def _update_eigensystem(self):
        """Update eigendecomposition of covariance matrix."""
        self.C = np.triu(self.C) + np.triu(self.C, 1).T
        # Guard against NaN/inf in covariance matrix
        if not np.all(np.isfinite(self.C)):
            self.C = np.eye(self.dim)
        try:
            D, B = np.linalg.eigh(self.C)
        except np.linalg.LinAlgError:
            self.C = np.eye(self.dim)
            D, B = np.linalg.eigh(self.C)
        D = np.sqrt(np.maximum(D, 1e-20))
        self.invsqrtC = B @ np.diag(1.0 / D) @ B.T

    def ask(self, rng: Optional[np.random.Generator] = None) -> np.ndarray:
        """
        Sample new candidate solutions from the current distribution.
        Returns: (lam, dim) array of solutions
        """
        if rng is None:
            rng = np.random.default_rng()

        solutions = np.zeros((self.lam, self.dim))
        for k in range(self.lam):
            z = rng.standard_normal(self.dim)
            solutions[k] = self.mean + self.sigma * (self.C @ z if self.dim <= 10 else z)

        return solutions

    def tell(self, solutions: np.ndarray, fitnesses: np.ndarray):
        """
        Update distribution parameters based on evaluated solutions.
        solutions: (lam, dim), fitnesses: (lam,) — lower fitness is better.
        """
        # Sort by fitness (ascending = best first)
        order = np.argsort(fitnesses)
        solutions = solutions[order]

        # Recombine: weighted mean of mu best solutions
        old_mean = self.mean.copy()
        self.mean = np.sum(self.weights[:, None] * solutions[: self.mu], axis=0)

        # Update evolution paths
        mean_diff = self.mean - old_mean
        self.ps = (1 - self.cs) * self.ps + np.sqrt(
            self.cs * (2 - self.cs) * self.mu_eff
        ) * (self.invsqrtC @ mean_diff) / self.sigma

        hs = (
            np.linalg.norm(self.ps)
            / np.sqrt(1 - (1 - self.cs) ** (2 * (self.generation + 1)))
            < (1.4 + 2.0 / (self.dim + 1)) * self.chi_n
        )

        self.pc = (1 - self.cc) * self.pc + hs * np.sqrt(
            self.cc * (2 - self.cc) * self.mu_eff
        ) * mean_diff / self.sigma

        # Update covariance matrix
        artmp = (solutions[: self.mu] - old_mean) / self.sigma
        self.C = (
            (1 - self.c1 - self.cmu) * self.C
            + self.c1 * (np.outer(self.pc, self.pc) + (1 - hs) * self.cc * (2 - self.cc) * self.C)
            + self.cmu * (self.weights[:, None] * artmp).T @ artmp
        )

        # Update step size (clamp to prevent overflow)
        exponent = (self.cs / self.ds) * (np.linalg.norm(self.ps) / self.chi_n - 1)
        exponent = np.clip(exponent, -20, 20)
        self.sigma *= np.exp(exponent)
        self.sigma = np.clip(self.sigma, 1e-20, 1e10)

        # Update eigensystem periodically
        self.eigeneval += 1
        if self.eigeneval >= self.lam / (self.c1 + self.cmu) / self.dim / 10:
            self._update_eigensystem()
            self.eigeneval = 0

        self.generation += 1

    def optimize(
        self,
        objective_fn: Callable[[np.ndarray], float],
        max_iterations: int = 100,
        sigma_threshold: float = 1e-10,
        rng: Optional[np.random.Generator] = None,
    ) -> Dict[str, Any]:
        """
        Run CMA-ES optimization loop.
        Returns dict with best solution, fitness, and convergence info.
        """
        if rng is None:
            rng = np.random.default_rng(42)

        best_solution = self.mean.copy()
        best_fitness = float("inf")
        fitness_history = []

        for iteration in range(max_iterations):
            solutions = self.ask(rng)
            fitnesses = np.array([objective_fn(s) for s in solutions])

            self.tell(solutions, fitnesses)

            gen_best_idx = np.argmin(fitnesses)
            if fitnesses[gen_best_idx] < best_fitness:
                best_fitness = fitnesses[gen_best_idx]
                best_solution = solutions[gen_best_idx].copy()

            fitness_history.append(best_fitness)

            # Convergence check
            if self.sigma < sigma_threshold:
                break

        return {
            "best_solution": best_solution,
            "best_fitness": best_fitness,
            "iterations": iteration + 1,
            "converged": self.sigma < sigma_threshold,
            "final_sigma": self.sigma,
            "fitness_history": fitness_history,
        }
