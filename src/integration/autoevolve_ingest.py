"""
Generation 0 Seed Ingestion Module.
Imports Cooper s7/s10/S22 configurations from config and augments
them with Gaussian perturbations to initialize a diverse population.
"""

import json
import os
import numpy as np
from typing import List, Optional
from src.alpha_evolve.candidate import K3T2Candidate


def load_cooper_seeds(
    source: str = None,
) -> List[K3T2Candidate]:
    """
    Load pre-validated Cooper s7/s10/S22 configurations as K3T2Candidate instances.
    """
    if source is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        source = os.path.join(base_dir, "configs", "cooper_seeds.json")

    with open(source, "r", encoding="utf-8") as f:
        data = json.load(f)

    seeds = []
    for entry in data["seeds"]:
        tau = complex(entry["complex_structure_tau"][0], entry["complex_structure_tau"][1])
        rho = complex(entry["kahler_modulus_rho"][0], entry["kahler_modulus_rho"][1])
        candidate = K3T2Candidate(
            picard_fuchs_coefficients=np.array(entry["picard_fuchs_coefficients"], dtype=np.float64),
            hodge_numbers=entry.get("hodge_numbers", {"h11": 3, "h21": 19, "h22": 156}),
            kodaira_fiber_type=entry.get("kodaira_fiber_type", "I_1"),
            complex_structure_tau=tau,
            kahler_modulus_rho=rho,
            generation=0,
            parent_ids=[],
        )
        seeds.append(candidate)

    return seeds


def augment_seeds(
    seeds: List[K3T2Candidate],
    n_perturbations: int = 50,
    sigma: float = 0.1,
    rng: Optional[np.random.Generator] = None,
) -> List[K3T2Candidate]:
    """
    Generate Gaussian perturbations around each seed to initialize a diverse population.
    Returns: original seeds + (n_perturbations * len(seeds)) perturbed candidates.
    """
    if rng is None:
        rng = np.random.default_rng(42)

    augmented = list(seeds)  # Start with originals

    for seed in seeds:
        vec = seed.to_feature_vector()
        pf_order = len(seed.picard_fuchs_coefficients)

        for _ in range(n_perturbations):
            noise = rng.normal(0, sigma, len(vec))
            perturbed_vec = vec + noise

            # Enforce constraints
            perturbed_vec[:pf_order] = np.clip(perturbed_vec[:pf_order], -10.0, 10.0)
            perturbed_vec[pf_order + 1] = max(perturbed_vec[pf_order + 1], 0.01)  # τ₂ > 0
            perturbed_vec[pf_order + 3] = max(perturbed_vec[pf_order + 3], 0.01)  # ρ₂ > 0

            metadata = {
                "hodge_numbers": seed.hodge_numbers.copy(),
                "kodaira_fiber_type": seed.kodaira_fiber_type,
                "generation": 0,
                "parent_ids": [seed.candidate_id],
            }
            child = K3T2Candidate.from_feature_vector(perturbed_vec, pf_order=pf_order, metadata=metadata)
            augmented.append(child)

    return augmented
