"""
K3T2Candidate Dataclass — Atomic unit for K3×T² evolutionary geometry search.
Represents a single candidate geometry configuration with Picard-Fuchs coefficients,
T² torus moduli, fitness scores, and lineage tracking.
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from uuid import uuid4


@dataclass
class K3T2Candidate:
    """
    Represents a single K3×T² geometry configuration in the evolutionary search.
    
    K3 Surface Parameters:
        picard_fuchs_coefficients: ODE coefficients of shape (pf_order,)
        hodge_numbers: {h11, h21, h22}
        kodaira_fiber_type: Kodaira classification string
    
    T² Torus Moduli:
        complex_structure_tau: τ = τ₁ + iτ₂ with τ₂ > 0
        kahler_modulus_rho: Kähler area/shape parameter
    
    Fitness Scores (populated after evaluation):
        surrogate_fitness: Tier 1 ML prediction (0–1, higher is better)
        lean_swampland_valid: Tier 2 formal pass/fail
        empirical_chi2: Tier 3 ground-truth chi-squared
        complexity_score: Objective B (lower is better)
    """

    # K3 Surface Parameters
    picard_fuchs_coefficients: np.ndarray
    hodge_numbers: Dict[str, int] = field(default_factory=lambda: {"h11": 3, "h21": 19, "h22": 156})
    kodaira_fiber_type: str = "I_1"

    # T² Torus Moduli
    complex_structure_tau: complex = complex(0.0, 1.0)
    kahler_modulus_rho: complex = complex(1.0, 1.0)

    # Fitness Scores
    surrogate_fitness: Optional[float] = None
    lean_swampland_valid: Optional[bool] = None
    empirical_chi2: Optional[float] = None
    complexity_score: Optional[float] = None

    # Lineage Tracking
    generation: int = 0
    parent_ids: List[str] = field(default_factory=list)
    candidate_id: str = field(default_factory=lambda: str(uuid4()))

    def __post_init__(self):
        if isinstance(self.picard_fuchs_coefficients, list):
            self.picard_fuchs_coefficients = np.array(self.picard_fuchs_coefficients, dtype=np.float64)
        if self.complex_structure_tau.imag <= 0:
            raise ValueError(
                f"complex_structure_tau must have positive imaginary part (τ₂ > 0), "
                f"got τ₂ = {self.complex_structure_tau.imag}"
            )

    @property
    def feature_dim(self) -> int:
        """Total dimensionality of the flattened feature vector."""
        return len(self.picard_fuchs_coefficients) + 4  # +4 for τ₁, τ₂, ρ₁, ρ₂

    def to_feature_vector(self) -> np.ndarray:
        """Flattens candidate into a 1D float array for the neural surrogate."""
        tau_parts = np.array([self.complex_structure_tau.real, self.complex_structure_tau.imag])
        rho_parts = np.array([self.kahler_modulus_rho.real, self.kahler_modulus_rho.imag])
        return np.concatenate([self.picard_fuchs_coefficients, tau_parts, rho_parts])

    @classmethod
    def from_feature_vector(
        cls,
        vec: np.ndarray,
        pf_order: int = 4,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> "K3T2Candidate":
        """Reconstructs candidate from feature vector + optional metadata."""
        metadata = metadata or {}
        pf_coeffs = vec[:pf_order]
        tau = complex(vec[pf_order], max(vec[pf_order + 1], 1e-6))  # Enforce τ₂ > 0
        rho = complex(vec[pf_order + 2], max(vec[pf_order + 3], 1e-6))

        return cls(
            picard_fuchs_coefficients=pf_coeffs,
            hodge_numbers=metadata.get("hodge_numbers", {"h11": 3, "h21": 19, "h22": 156}),
            kodaira_fiber_type=metadata.get("kodaira_fiber_type", "I_1"),
            complex_structure_tau=tau,
            kahler_modulus_rho=rho,
            generation=metadata.get("generation", 0),
            parent_ids=metadata.get("parent_ids", []),
            candidate_id=metadata.get("candidate_id", str(uuid4())),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serializes to JSON-compatible dictionary."""
        return {
            "picard_fuchs_coefficients": self.picard_fuchs_coefficients.tolist(),
            "hodge_numbers": self.hodge_numbers,
            "kodaira_fiber_type": self.kodaira_fiber_type,
            "complex_structure_tau": [self.complex_structure_tau.real, self.complex_structure_tau.imag],
            "kahler_modulus_rho": [self.kahler_modulus_rho.real, self.kahler_modulus_rho.imag],
            "surrogate_fitness": self.surrogate_fitness,
            "lean_swampland_valid": self.lean_swampland_valid,
            "empirical_chi2": self.empirical_chi2,
            "complexity_score": self.complexity_score,
            "generation": self.generation,
            "parent_ids": self.parent_ids,
            "candidate_id": self.candidate_id,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "K3T2Candidate":
        """Deserializes from dictionary."""
        tau = complex(d["complex_structure_tau"][0], d["complex_structure_tau"][1])
        rho = complex(d["kahler_modulus_rho"][0], d["kahler_modulus_rho"][1])
        cand = cls(
            picard_fuchs_coefficients=np.array(d["picard_fuchs_coefficients"], dtype=np.float64),
            hodge_numbers=d.get("hodge_numbers", {"h11": 3, "h21": 19, "h22": 156}),
            kodaira_fiber_type=d.get("kodaira_fiber_type", "I_1"),
            complex_structure_tau=tau,
            kahler_modulus_rho=rho,
            generation=d.get("generation", 0),
            parent_ids=d.get("parent_ids", []),
            candidate_id=d.get("candidate_id", str(uuid4())),
        )
        cand.surrogate_fitness = d.get("surrogate_fitness")
        cand.lean_swampland_valid = d.get("lean_swampland_valid")
        cand.empirical_chi2 = d.get("empirical_chi2")
        cand.complexity_score = d.get("complexity_score")
        return cand
