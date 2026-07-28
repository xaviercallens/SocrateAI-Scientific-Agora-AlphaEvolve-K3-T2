"""
MLOps Experiment Logger — Pluggable backend for tracking evolution metrics.
Supports W&B, MLflow, or no-op (for testing/CI).
"""

from typing import List, Dict, Any, Optional


class MLOpsLogger:
    """
    Pluggable experiment logger that records generation-level metrics,
    Pareto front snapshots, and candidate lineage.
    """

    def __init__(self, backend: str = "none", project_name: str = "socrateai-k3t2-evolution"):
        self.backend = backend.lower()
        self.project_name = project_name
        self._run = None
        self._logged_generations = []

        if self.backend == "wandb":
            try:
                import wandb
                self._run = wandb.init(project=project_name, reinit=True)
                self._wandb = wandb
            except ImportError:
                print("Warning: wandb not installed. Falling back to 'none' backend.")
                self.backend = "none"
        elif self.backend == "mlflow":
            try:
                import mlflow
                mlflow.set_experiment(project_name)
                mlflow.start_run()
                self._mlflow = mlflow
            except ImportError:
                print("Warning: mlflow not installed. Falling back to 'none' backend.")
                self.backend = "none"

    def log_generation(self, generation: int, population, pareto_front) -> None:
        """Log population statistics and Pareto front metrics."""
        fitnesses = [
            c.surrogate_fitness for c in population if c.surrogate_fitness is not None
        ]
        complexities = [
            c.complexity_score for c in population if c.complexity_score is not None
        ]

        metrics = {
            "generation": generation,
            "population_size": len(population),
            "pareto_front_size": len(pareto_front),
            "best_fitness": max(fitnesses) if fitnesses else 0.0,
            "avg_fitness": sum(fitnesses) / len(fitnesses) if fitnesses else 0.0,
            "best_complexity": min(complexities) if complexities else 1.0,
            "avg_complexity": sum(complexities) / len(complexities) if complexities else 1.0,
        }

        self._logged_generations.append(metrics)

        if self.backend == "wandb" and self._run is not None:
            self._wandb.log(metrics, step=generation)
        elif self.backend == "mlflow":
            for key, val in metrics.items():
                self._mlflow.log_metric(key, val, step=generation)

    def log_pareto_front(self, front) -> None:
        """Log full Pareto front candidates."""
        if self.backend == "none":
            return
        # Serialize front for artifact logging
        front_data = [c.to_dict() for c in front]
        if self.backend == "wandb" and self._run is not None:
            self._wandb.log({"pareto_front_candidates": len(front_data)})

    def log_hyperparameters(self, config: Dict[str, Any]) -> None:
        """Log evolution configuration for reproducibility."""
        if self.backend == "wandb" and self._run is not None:
            self._wandb.config.update(config)
        elif self.backend == "mlflow":
            self._mlflow.log_params(
                {k: str(v) for k, v in config.items() if not isinstance(v, dict)}
            )

    def get_logged_metrics(self) -> List[Dict[str, Any]]:
        """Returns all logged generation metrics (useful for testing)."""
        return self._logged_generations

    def finish(self) -> None:
        """Flush logs and close connection."""
        if self.backend == "wandb" and self._run is not None:
            self._wandb.finish()
        elif self.backend == "mlflow":
            self._mlflow.end_run()
