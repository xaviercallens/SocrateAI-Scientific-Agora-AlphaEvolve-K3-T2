"""
Multi-Objective Fitness Evaluator for K3×T² candidates.
Coordinates Tier 1 surrogate evaluation and Objective B complexity penalty.
Tier 2 (Lean) and Tier 3 (GPU) are defined as interface stubs for Phase 3.
"""

import numpy as np
from typing import List, Optional
from src.alpha_evolve.candidate import K3T2Candidate
from src.alpha_evolve.neural_surrogate import NeuralSurrogate


class FitnessEvaluator:
    """
    Multi-objective fitness evaluator using Pareto dominance.
    Objective A: Maximize empirical fit (surrogate prediction or Tier 3 chi-squared)
    Objective B: Minimize Picard-Fuchs complexity
    """

    def __init__(self, surrogate: Optional[NeuralSurrogate] = None):
        self.surrogate = surrogate

    def evaluate_complexity(self, candidate: K3T2Candidate) -> float:
        """
        Objective B: Normalized L1 norm of Picard-Fuchs coefficients.
        Range: [0, 1] where 0 = simplest, 1 = most complex.
        """
        pf = candidate.picard_fuchs_coefficients
        l1_norm = np.sum(np.abs(pf))
        order = len(pf)
        # Normalize: max possible L1 with coefficients in [-10, 10] is order * 10
        max_l1 = order * 10.0
        return min(l1_norm / max_l1, 1.0)

    def evaluate_tier1(self, candidate: K3T2Candidate) -> K3T2Candidate:
        """
        Tier 1: Neural surrogate prediction + complexity scoring.
        """
        # Surrogate fitness (Objective A proxy)
        if self.surrogate is not None:
            fitness = float(self.surrogate.predict([candidate])[0])
        else:
            # Fallback: analytic approximation
            pf = candidate.picard_fuchs_coefficients
            tau2 = candidate.complex_structure_tau.imag
            tau1 = abs(candidate.complex_structure_tau.real)
            pf_complexity = np.sum(np.abs(pf))
            fitness = (tau2 / (1.0 + tau1)) / (1.0 + pf_complexity)
            fitness = min(max(fitness, 0.0), 1.0)

        candidate.surrogate_fitness = fitness
        candidate.complexity_score = self.evaluate_complexity(candidate)
        return candidate

    def evaluate_tier2(self, candidate: K3T2Candidate) -> K3T2Candidate:
        """Tier 2 stub: Lean 4 Swampland check (Phase 3 implementation)."""
        candidate.lean_swampland_valid = None  # Not yet implemented
        return candidate

    def evaluate_tier3(self, candidate: K3T2Candidate) -> K3T2Candidate:
        """Tier 3 stub: GPU empirical evaluation (Phase 3 implementation)."""
        candidate.empirical_chi2 = None  # Not yet implemented
        return candidate

    def evaluate_population(self, candidates: List[K3T2Candidate]) -> List[K3T2Candidate]:
        """Batch Tier 1 evaluation for an entire population."""
        if self.surrogate is not None:
            X = np.array([c.to_feature_vector() for c in candidates])
            predictions = self.surrogate.predict_batch(X).flatten()
            for c, pred in zip(candidates, predictions):
                c.surrogate_fitness = float(pred)
                c.complexity_score = self.evaluate_complexity(c)
        else:
            for c in candidates:
                self.evaluate_tier1(c)
        return candidates

    @staticmethod
    def dominates(a: K3T2Candidate, b: K3T2Candidate) -> bool:
        """
        Pareto dominance: a dominates b if:
        - a is >= b on ALL objectives, AND
        - a is strictly > b on AT LEAST ONE objective
        
        Objective A (surrogate_fitness): MAXIMIZE → higher is better
        Objective B (complexity_score):  MINIMIZE → lower is better
        """
        fit_a = a.surrogate_fitness if a.surrogate_fitness is not None else 0.0
        fit_b = b.surrogate_fitness if b.surrogate_fitness is not None else 0.0
        comp_a = a.complexity_score if a.complexity_score is not None else 1.0
        comp_b = b.complexity_score if b.complexity_score is not None else 1.0

        # a is at least as good on both objectives
        at_least_as_good = (fit_a >= fit_b) and (comp_a <= comp_b)
        # a is strictly better on at least one
        strictly_better = (fit_a > fit_b) or (comp_a < comp_b)

        return at_least_as_good and strictly_better
