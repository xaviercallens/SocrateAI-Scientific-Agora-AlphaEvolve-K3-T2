"""
NSGA-II Multi-Objective Optimizer for K3×T² Evolutionary Geometry Search.
Implements non-dominated sorting, crowding distance, tournament selection,
and the full generational loop.
"""

import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from src.alpha_evolve.candidate import K3T2Candidate
from src.alpha_evolve.fitness import FitnessEvaluator
from src.alpha_evolve.genetic_operators import (
    polynomial_mutation,
    sbx_crossover,
    kodaira_mutation,
)


def _get_objectives(c: K3T2Candidate) -> Tuple[float, float]:
    """Returns (objective_a, objective_b) — both to be MINIMIZED for NSGA-II.
    Objective A: maximize fitness → minimize negative fitness
    Objective B: minimize complexity
    """
    fit = c.surrogate_fitness if c.surrogate_fitness is not None else 0.0
    comp = c.complexity_score if c.complexity_score is not None else 1.0
    return (-fit, comp)  # Negate fitness so NSGA-II minimizes both


def non_dominated_sort(population: List[K3T2Candidate]) -> List[List[int]]:
    """
    Fast non-dominated sort (Deb et al., 2002).
    Returns list of fronts, where each front is a list of indices into population.
    """
    n = len(population)
    domination_count = [0] * n
    dominated_set: List[List[int]] = [[] for _ in range(n)]
    fronts: List[List[int]] = [[]]

    objs = [_get_objectives(c) for c in population]

    for p in range(n):
        for q in range(n):
            if p == q:
                continue
            # p dominates q if p <= q on all objectives and p < q on at least one
            p_dom_q = all(objs[p][k] <= objs[q][k] for k in range(2)) and \
                      any(objs[p][k] < objs[q][k] for k in range(2))
            q_dom_p = all(objs[q][k] <= objs[p][k] for k in range(2)) and \
                      any(objs[q][k] < objs[p][k] for k in range(2))

            if p_dom_q:
                dominated_set[p].append(q)
            elif q_dom_p:
                domination_count[p] += 1

        if domination_count[p] == 0:
            fronts[0].append(p)

    i = 0
    while i < len(fronts) and fronts[i]:
        next_front = []
        for p in fronts[i]:
            for q in dominated_set[p]:
                domination_count[q] -= 1
                if domination_count[q] == 0:
                    next_front.append(q)
        i += 1
        if next_front:
            fronts.append(next_front)

    return [f for f in fronts if f]


def crowding_distance(population: List[K3T2Candidate], front: List[int]) -> Dict[int, float]:
    """
    Calculates crowding distance for individuals in a front.
    Boundary solutions receive infinity.
    """
    n = len(front)
    if n <= 2:
        return {idx: float("inf") for idx in front}

    distances = {idx: 0.0 for idx in front}
    objs = {idx: _get_objectives(population[idx]) for idx in front}

    for m in range(2):  # Two objectives
        sorted_front = sorted(front, key=lambda idx: objs[idx][m])
        distances[sorted_front[0]] = float("inf")
        distances[sorted_front[-1]] = float("inf")

        obj_min = objs[sorted_front[0]][m]
        obj_max = objs[sorted_front[-1]][m]
        obj_range = obj_max - obj_min

        if obj_range < 1e-14:
            continue

        for i in range(1, n - 1):
            distances[sorted_front[i]] += (
                objs[sorted_front[i + 1]][m] - objs[sorted_front[i - 1]][m]
            ) / obj_range

    return distances


def tournament_selection(
    population: List[K3T2Candidate],
    ranks: Dict[int, int],
    crowding: Dict[int, float],
    rng: np.random.Generator,
    k: int = 2,
) -> int:
    """Binary tournament selection using (rank, crowding distance) comparison."""
    competitors = rng.choice(len(population), size=k, replace=False)

    best = competitors[0]
    for c in competitors[1:]:
        c_rank = ranks.get(c, float("inf"))
        b_rank = ranks.get(best, float("inf"))
        if c_rank < b_rank:
            best = c
        elif c_rank == b_rank:
            if crowding.get(c, 0) > crowding.get(best, 0):
                best = c
    return best


def evolve_generation(
    population: List[K3T2Candidate],
    evaluator: FitnessEvaluator,
    rng: np.random.Generator,
    config: Dict[str, Any],
    bounds: Dict[str, Any] = None,
) -> List[K3T2Candidate]:
    """
    Execute one full NSGA-II generation cycle:
    1. Evaluate fitness
    2. Non-dominated sort
    3. Crowding distance
    4. Tournament selection
    5. Crossover + mutation → offspring
    6. Merge parent + offspring
    7. Truncation selection to population_size
    """
    pop_size = config.get("population_size", 200)
    crossover_cfg = config.get("genetic_operators", {}).get("crossover", {})
    mutation_cfg = config.get("genetic_operators", {}).get("mutation", {})
    kodaira_cfg = config.get("genetic_operators", {}).get("kodaira_mutation", {})

    eta_c = crossover_cfg.get("eta_c", 20.0)
    cx_prob = crossover_cfg.get("probability", 0.9)
    eta_m = mutation_cfg.get("eta_m", 20.0)
    mut_prob = mutation_cfg.get("probability", 0.1)
    kod_prob = kodaira_cfg.get("probability", 0.05)
    valid_types = kodaira_cfg.get("valid_types", ["I_1", "II", "IV*"])

    # 1. Evaluate
    population = evaluator.evaluate_population(population)

    # 2. Non-dominated sort
    fronts = non_dominated_sort(population)

    # 3. Crowding distance & ranks
    ranks: Dict[int, int] = {}
    all_crowding: Dict[int, float] = {}
    for rank, front in enumerate(fronts):
        cd = crowding_distance(population, front)
        for idx in front:
            ranks[idx] = rank
            all_crowding[idx] = cd[idx]

    # 4–5. Generate offspring
    offspring: List[K3T2Candidate] = []
    while len(offspring) < pop_size:
        p1_idx = tournament_selection(population, ranks, all_crowding, rng)
        p2_idx = tournament_selection(population, ranks, all_crowding, rng)
        while p2_idx == p1_idx and len(population) > 1:
            p2_idx = tournament_selection(population, ranks, all_crowding, rng)

        child_a, child_b = sbx_crossover(
            population[p1_idx], population[p2_idx], rng, eta_c=eta_c, prob=cx_prob
        )

        child_a = polynomial_mutation(child_a, rng, eta_m=eta_m, prob=mut_prob, bounds=bounds)
        child_b = polynomial_mutation(child_b, rng, eta_m=eta_m, prob=mut_prob, bounds=bounds)

        child_a = kodaira_mutation(child_a, rng, valid_types=valid_types, prob=kod_prob)
        child_b = kodaira_mutation(child_b, rng, valid_types=valid_types, prob=kod_prob)

        offspring.append(child_a)
        if len(offspring) < pop_size:
            offspring.append(child_b)

    # 6. Merge
    combined = population + offspring
    combined = evaluator.evaluate_population(combined)

    # 7. Truncation selection
    combined_fronts = non_dominated_sort(combined)
    new_population: List[K3T2Candidate] = []
    for front in combined_fronts:
        if len(new_population) + len(front) <= pop_size:
            new_population.extend([combined[i] for i in front])
        else:
            cd = crowding_distance(combined, front)
            sorted_front = sorted(front, key=lambda idx: cd[idx], reverse=True)
            remaining = pop_size - len(new_population)
            new_population.extend([combined[i] for i in sorted_front[:remaining]])
            break

    return new_population


def run_nsga2(
    initial_population: List[K3T2Candidate],
    evaluator: FitnessEvaluator,
    config: Dict[str, Any],
    bounds: Dict[str, Any] = None,
    logger=None,
) -> Dict[str, Any]:
    """
    Main NSGA-II loop. Runs G generations and returns the final Pareto front.
    """
    max_gen = config.get("max_generations", 500)
    seed = config.get("random_seed", 42)
    rng = np.random.default_rng(seed)

    population = list(initial_population)
    log_every = config.get("logging", {}).get("log_every_n_generations", 10)

    for gen in range(1, max_gen + 1):
        population = evolve_generation(population, evaluator, rng, config, bounds=bounds)

        if gen % log_every == 0 or gen == max_gen:
            fronts = non_dominated_sort(population)
            pareto_front = [population[i] for i in fronts[0]]
            best_fit = max(
                (c.surrogate_fitness for c in pareto_front if c.surrogate_fitness is not None),
                default=0.0,
            )
            best_comp = min(
                (c.complexity_score for c in pareto_front if c.complexity_score is not None),
                default=1.0,
            )
            print(
                f"Gen {gen}/{max_gen}: Pareto size={len(pareto_front)}, "
                f"best_fitness={best_fit:.6f}, best_complexity={best_comp:.6f}"
            )
            if logger is not None:
                logger.log_generation(gen, population, pareto_front)

    # Extract final Pareto front
    final_fronts = non_dominated_sort(population)
    final_pareto = [population[i] for i in final_fronts[0]]

    return {
        "status": "CONVERGED",
        "generations": max_gen,
        "pareto_front_size": len(final_pareto),
        "pareto_front": final_pareto,
        "final_population": population,
    }
