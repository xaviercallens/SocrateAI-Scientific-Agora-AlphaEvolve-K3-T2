"""
Main AlphaEvolve Evolution Runner — Entry point for multi-generational K3×T² search.
Orchestrates seed ingestion, surrogate training, NSGA-II evolution, and CMA-ES refinement.
"""

import os
import sys
import json
import yaml
import numpy as np

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.alpha_evolve.candidate import K3T2Candidate
from src.alpha_evolve.neural_surrogate import NeuralSurrogate
from src.alpha_evolve.fitness import FitnessEvaluator
from src.alpha_evolve.optimizers import run_nsga2, non_dominated_sort
from src.alpha_evolve.cma_es import CMAES
from src.integration.autoevolve_ingest import load_cooper_seeds, augment_seeds
from src.utils.mlops_logger import MLOpsLogger


def load_configs(base_dir: str = None):
    """Load evolution and threshold configs."""
    if base_dir is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    evo_path = os.path.join(base_dir, "configs", "evolution_nsga2.yaml")
    bounds_path = os.path.join(base_dir, "configs", "threshold_bounds.yaml")

    with open(evo_path, "r") as f:
        evo_cfg = yaml.safe_load(f)

    with open(bounds_path, "r") as f:
        bounds_cfg = yaml.safe_load(f)

    return evo_cfg.get("evolution", {}), bounds_cfg.get("bounds", {})


def run_evolution(config_overrides: dict = None):
    """
    Full evolution pipeline:
    1. Load configs
    2. Load/generate Generation 0 (Cooper seeds + augmentation)
    3. Train neural surrogate on synthetic data
    4. Run NSGA-II evolution
    5. [Optional] CMA-ES refinement on elite candidates
    6. Export final Pareto front
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # 1. Load configs
    evo_config, bounds = load_configs(base_dir)

    # Apply overrides
    if config_overrides:
        for k, v in config_overrides.items():
            evo_config[k] = v

    pop_size = evo_config.get("population_size", 200)
    max_gen = evo_config.get("max_generations", 500)
    pf_order = evo_config.get("picard_fuchs_order", 4)
    feature_dim = pf_order + 4  # PF coeffs + τ₁, τ₂, ρ₁, ρ₂

    print("=" * 70)
    print("  SOCRATEAI ALPHAEVOLVE K3×T² MULTI-OBJECTIVE EVOLUTION ENGINE")
    print("=" * 70)
    print(f"  Population Size: {pop_size}")
    print(f"  Max Generations: {max_gen}")
    print(f"  Picard-Fuchs Order: {pf_order}")
    print(f"  Feature Dim: {feature_dim}")
    print("=" * 70)

    # 2. Load Generation 0
    print("\n[Phase 1] Loading Cooper s7/s10/S22 seed configurations...")
    seeds = load_cooper_seeds(os.path.join(base_dir, "configs", "cooper_seeds.json"))
    print(f"  Loaded {len(seeds)} Cooper seeds.")

    n_perturbations = max(1, (pop_size - len(seeds)) // len(seeds))
    population = augment_seeds(seeds, n_perturbations=n_perturbations)[:pop_size]
    print(f"  Augmented to {len(population)} candidates.")

    # 3. Train neural surrogate
    print("\n[Phase 2] Training neural surrogate model...")
    surr_config = evo_config.get("surrogate", {})
    surrogate = NeuralSurrogate(
        feature_dim=feature_dim,
        hidden_layers=surr_config.get("hidden_layers", [128, 64, 32]),
    )
    n_synthetic = surr_config.get("synthetic_samples", 5000)
    X_train, y_train = NeuralSurrogate.generate_synthetic_training_data(
        n_samples=n_synthetic, pf_order=pf_order
    )
    train_result = surrogate.train(
        X_train, y_train,
        epochs=surr_config.get("training_epochs", 100),
        lr=surr_config.get("learning_rate", 0.001),
    )
    print(f"  Surrogate trained: final_loss={train_result['final_loss']:.6f}")

    # 4. Run NSGA-II
    print(f"\n[Phase 3] Starting NSGA-II evolution ({max_gen} generations)...")
    evaluator = FitnessEvaluator(surrogate=surrogate)

    log_config = evo_config.get("logging", {})
    logger = MLOpsLogger(
        backend=log_config.get("backend", "none"),
        project_name=log_config.get("project_name", "socrateai-k3t2-evolution"),
    )
    logger.log_hyperparameters(evo_config)

    result = run_nsga2(
        initial_population=population,
        evaluator=evaluator,
        config=evo_config,
        bounds=bounds,
        logger=logger,
    )

    pareto_front = result["pareto_front"]
    print(f"\n  NSGA-II completed: {result['pareto_front_size']} candidates on Pareto front.")

    # 5. CMA-ES refinement on elite candidates (optional)
    cma_config = evo_config.get("cma_es", {})
    elite_fraction = cma_config.get("elite_fraction", 0.01)
    n_elite = max(1, int(len(pareto_front) * elite_fraction))

    if n_elite > 0 and cma_config.get("max_iterations", 0) > 0:
        print(f"\n[Phase 4] CMA-ES refinement on top {n_elite} elite candidates...")
        elite = sorted(
            pareto_front,
            key=lambda c: -(c.surrogate_fitness or 0.0),
        )[:n_elite]

        for i, candidate in enumerate(elite):
            vec = candidate.to_feature_vector()

            def objective(x):
                c = K3T2Candidate.from_feature_vector(x, pf_order=pf_order)
                evaluator.evaluate_tier1(c)
                return -(c.surrogate_fitness or 0.0)  # Negate (CMA-ES minimizes)

            cma = CMAES(
                mean=vec,
                sigma=cma_config.get("sigma_initial", 0.3),
            )
            cma_result = cma.optimize(
                objective,
                max_iterations=cma_config.get("max_iterations", 100),
            )
            print(f"  Elite {i+1}: fitness improved to {-cma_result['best_fitness']:.6f}")

    # 6. Export results
    results_dir = os.path.join(base_dir, "results")
    os.makedirs(results_dir, exist_ok=True)
    output_path = os.path.join(results_dir, "pareto_front.json")

    pareto_data = [c.to_dict() for c in pareto_front]
    with open(output_path, "w") as f:
        json.dump({"pareto_front": pareto_data, "size": len(pareto_data)}, f, indent=2)

    print(f"\n{'=' * 70}")
    print(f"  EVOLUTION COMPLETE")
    print(f"  Pareto front exported to: {output_path}")
    print(f"  Total candidates on front: {len(pareto_front)}")
    if pareto_front:
        best = max(pareto_front, key=lambda c: c.surrogate_fitness or 0)
        print(f"  Best fitness: {best.surrogate_fitness:.6f}")
        print(f"  Best complexity: {best.complexity_score:.6f}")
    print(f"{'=' * 70}")

    logger.finish()
    return result


if __name__ == "__main__":
    # Support simple CLI overrides
    overrides = {}
    for arg in sys.argv[1:]:
        if "=" in arg:
            key, val = arg.split("=", 1)
            key = key.split(".")[-1]  # e.g. evolution.max_generations → max_generations
            try:
                overrides[key] = int(val)
            except ValueError:
                try:
                    overrides[key] = float(val)
                except ValueError:
                    overrides[key] = val

    run_evolution(config_overrides=overrides)
