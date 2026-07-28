"""
Genetic Operators for K3×T² Evolutionary Search.
Tensor-based mutation and crossover operators that respect mathematical
constraints of K3×T² geometries (τ₂ > 0, bounded Picard-Fuchs coefficients).
"""

import numpy as np
from typing import List, Tuple, Dict, Any
from src.alpha_evolve.candidate import K3T2Candidate


def _clip_to_bounds(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def _enforce_tau2_positive(tau: complex, min_tau2: float = 0.01) -> complex:
    """Ensures τ₂ > 0 (fundamental domain constraint)."""
    return complex(tau.real, max(tau.imag, min_tau2))


def polynomial_mutation(
    candidate: K3T2Candidate,
    rng: np.random.Generator,
    eta_m: float = 20.0,
    prob: float = 0.1,
    bounds: Dict[str, Any] = None,
) -> K3T2Candidate:
    """
    Polynomial bounded mutation (Deb & Goyal, 1996).
    Mutates Picard-Fuchs coefficients and T² moduli with polynomial distribution.
    """
    bounds = bounds or {}
    pf_bounds = bounds.get("picard_fuchs", {})
    tau_bounds = bounds.get("complex_structure_tau", {})
    rho_bounds = bounds.get("kahler_modulus_rho", {})

    pf_lo = pf_bounds.get("coefficient_min", -10.0)
    pf_hi = pf_bounds.get("coefficient_max", 10.0)

    vec = candidate.to_feature_vector().copy()
    pf_order = len(candidate.picard_fuchs_coefficients)

    for i in range(len(vec)):
        if rng.random() < prob:
            u = rng.random()
            if u < 0.5:
                delta = (2.0 * u) ** (1.0 / (eta_m + 1.0)) - 1.0
            else:
                delta = 1.0 - (2.0 * (1.0 - u)) ** (1.0 / (eta_m + 1.0))
            vec[i] += delta * (pf_hi - pf_lo) * 0.1

    # Clip Picard-Fuchs coefficients
    vec[:pf_order] = np.clip(vec[:pf_order], pf_lo, pf_hi)

    # Clip τ and ρ
    tau2_min = tau_bounds.get("tau2_min", 0.01)
    vec[pf_order + 1] = max(vec[pf_order + 1], tau2_min)
    rho2_min = rho_bounds.get("rho2_min", 0.01)
    vec[pf_order + 3] = max(vec[pf_order + 3], rho2_min)

    metadata = {
        "hodge_numbers": candidate.hodge_numbers,
        "kodaira_fiber_type": candidate.kodaira_fiber_type,
        "generation": candidate.generation + 1,
        "parent_ids": [candidate.candidate_id],
    }
    return K3T2Candidate.from_feature_vector(vec, pf_order=pf_order, metadata=metadata)


def gaussian_mutation(
    candidate: K3T2Candidate,
    rng: np.random.Generator,
    sigma: float = 0.1,
    prob: float = 0.1,
    bounds: Dict[str, Any] = None,
) -> K3T2Candidate:
    """Gaussian mutation with re-projection into fundamental domain."""
    bounds = bounds or {}
    pf_bounds = bounds.get("picard_fuchs", {})
    pf_lo = pf_bounds.get("coefficient_min", -10.0)
    pf_hi = pf_bounds.get("coefficient_max", 10.0)

    vec = candidate.to_feature_vector().copy()
    pf_order = len(candidate.picard_fuchs_coefficients)

    mask = rng.random(len(vec)) < prob
    noise = rng.normal(0, sigma, len(vec))
    vec += mask * noise

    vec[:pf_order] = np.clip(vec[:pf_order], pf_lo, pf_hi)
    tau2_min = bounds.get("complex_structure_tau", {}).get("tau2_min", 0.01)
    vec[pf_order + 1] = max(vec[pf_order + 1], tau2_min)
    rho2_min = bounds.get("kahler_modulus_rho", {}).get("rho2_min", 0.01)
    vec[pf_order + 3] = max(vec[pf_order + 3], rho2_min)

    metadata = {
        "hodge_numbers": candidate.hodge_numbers,
        "kodaira_fiber_type": candidate.kodaira_fiber_type,
        "generation": candidate.generation + 1,
        "parent_ids": [candidate.candidate_id],
    }
    return K3T2Candidate.from_feature_vector(vec, pf_order=pf_order, metadata=metadata)


def sbx_crossover(
    parent_a: K3T2Candidate,
    parent_b: K3T2Candidate,
    rng: np.random.Generator,
    eta_c: float = 20.0,
    prob: float = 0.9,
) -> Tuple[K3T2Candidate, K3T2Candidate]:
    """
    Simulated Binary Crossover (SBX) producing two offspring from two parents.
    """
    vec_a = parent_a.to_feature_vector().copy()
    vec_b = parent_b.to_feature_vector().copy()
    pf_order = len(parent_a.picard_fuchs_coefficients)

    child_a = vec_a.copy()
    child_b = vec_b.copy()

    if rng.random() < prob:
        for i in range(len(vec_a)):
            if rng.random() < 0.5:
                if abs(vec_a[i] - vec_b[i]) > 1e-14:
                    u = rng.random()
                    if u <= 0.5:
                        beta = (2.0 * u) ** (1.0 / (eta_c + 1.0))
                    else:
                        beta = (1.0 / (2.0 * (1.0 - u))) ** (1.0 / (eta_c + 1.0))
                    child_a[i] = 0.5 * ((1 + beta) * vec_a[i] + (1 - beta) * vec_b[i])
                    child_b[i] = 0.5 * ((1 - beta) * vec_a[i] + (1 + beta) * vec_b[i])

    # Enforce constraints
    child_a[pf_order + 1] = max(child_a[pf_order + 1], 0.01)
    child_b[pf_order + 1] = max(child_b[pf_order + 1], 0.01)
    child_a[pf_order + 3] = max(child_a[pf_order + 3], 0.01)
    child_b[pf_order + 3] = max(child_b[pf_order + 3], 0.01)

    gen = max(parent_a.generation, parent_b.generation) + 1
    meta_a = {
        "hodge_numbers": parent_a.hodge_numbers,
        "kodaira_fiber_type": parent_a.kodaira_fiber_type,
        "generation": gen,
        "parent_ids": [parent_a.candidate_id, parent_b.candidate_id],
    }
    meta_b = {
        "hodge_numbers": parent_b.hodge_numbers,
        "kodaira_fiber_type": parent_b.kodaira_fiber_type,
        "generation": gen,
        "parent_ids": [parent_a.candidate_id, parent_b.candidate_id],
    }

    return (
        K3T2Candidate.from_feature_vector(child_a, pf_order=pf_order, metadata=meta_a),
        K3T2Candidate.from_feature_vector(child_b, pf_order=pf_order, metadata=meta_b),
    )


def uniform_crossover(
    parent_a: K3T2Candidate,
    parent_b: K3T2Candidate,
    rng: np.random.Generator,
    swap_prob: float = 0.5,
) -> Tuple[K3T2Candidate, K3T2Candidate]:
    """Per-gene independent swap crossover."""
    vec_a = parent_a.to_feature_vector().copy()
    vec_b = parent_b.to_feature_vector().copy()
    pf_order = len(parent_a.picard_fuchs_coefficients)

    mask = rng.random(len(vec_a)) < swap_prob
    child_a = np.where(mask, vec_b, vec_a)
    child_b = np.where(mask, vec_a, vec_b)

    child_a[pf_order + 1] = max(child_a[pf_order + 1], 0.01)
    child_b[pf_order + 1] = max(child_b[pf_order + 1], 0.01)
    child_a[pf_order + 3] = max(child_a[pf_order + 3], 0.01)
    child_b[pf_order + 3] = max(child_b[pf_order + 3], 0.01)

    gen = max(parent_a.generation, parent_b.generation) + 1
    meta_a = {"generation": gen, "parent_ids": [parent_a.candidate_id, parent_b.candidate_id]}
    meta_b = {"generation": gen, "parent_ids": [parent_a.candidate_id, parent_b.candidate_id]}

    return (
        K3T2Candidate.from_feature_vector(child_a, pf_order=pf_order, metadata=meta_a),
        K3T2Candidate.from_feature_vector(child_b, pf_order=pf_order, metadata=meta_b),
    )


def kodaira_mutation(
    candidate: K3T2Candidate,
    rng: np.random.Generator,
    valid_types: List[str] = None,
    prob: float = 0.05,
) -> K3T2Candidate:
    """Categorical mutation: selects from valid Kodaira fiber types."""
    if valid_types is None:
        valid_types = ["I_1", "I_2", "II", "III", "IV", "IV*", "III*", "II*"]

    if rng.random() < prob:
        new_type = rng.choice(valid_types)
    else:
        new_type = candidate.kodaira_fiber_type

    return K3T2Candidate(
        picard_fuchs_coefficients=candidate.picard_fuchs_coefficients.copy(),
        hodge_numbers=candidate.hodge_numbers.copy(),
        kodaira_fiber_type=new_type,
        complex_structure_tau=candidate.complex_structure_tau,
        kahler_modulus_rho=candidate.kahler_modulus_rho,
        generation=candidate.generation + 1,
        parent_ids=[candidate.candidate_id],
    )
