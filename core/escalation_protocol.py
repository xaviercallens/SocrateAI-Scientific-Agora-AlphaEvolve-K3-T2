"""
Escalation Protocol Module.
Manages automatic fallback across Gemini model tiers (Flash -> Pro -> Ultra) upon call failure
or low-confidence results, with built-in circuit breaker functionality.
"""

import time
from typing import Dict, Any, Callable, List, Optional
from core.model_router import ModelRouter
from core.cost_tracker import CostTracker


class EscalationProtocol:
    """
    Executes tiered model escalations and manages circuit breaker safety limits.
    """

    def __init__(
        self,
        router: Optional[ModelRouter] = None,
        cost_tracker: Optional[CostTracker] = None,
        max_attempts: int = 3,
        cb_threshold: int = 5,
        cb_window_sec: int = 60,
    ):
        self.router = router or ModelRouter()
        self.cost_tracker = cost_tracker or CostTracker()
        self.max_attempts = max_attempts
        self.cb_threshold = cb_threshold
        self.cb_window_sec = cb_window_sec

        self.escalation_timestamps: List[float] = []

    def _is_circuit_breaker_active(self) -> bool:
        """
        Checks if circuit breaker is active due to excessive escalations in recent window.
        """
        now = time.time()
        self.escalation_timestamps = [
            ts for ts in self.escalation_timestamps if (now - ts) <= self.cb_window_sec
        ]
        return len(self.escalation_timestamps) >= self.cb_threshold

    def execute_with_escalation(
        self,
        action: str,
        execution_func: Callable[[Dict[str, Any]], Any],
        validator_func: Optional[Callable[[Any], bool]] = None,
        start_tier: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Executes function with model tier parameters starting at the action's designated tier (or start_tier).
        If validation fails or exception is raised, escalates to higher tiers.
        """
        if start_tier is None:
            initial_route = self.router.route(action)
            start_tier = initial_route["tier_key"]

        tier_order = ["low", "mid", "high"]
        if start_tier in tier_order:
            start_idx = tier_order.index(start_tier)
            tiers_sequence = tier_order[start_idx:]
        else:
            tiers_sequence = ["mid", "high"]

        # If circuit breaker is active, force starting at mid tier (bypass Flash)
        if self._is_circuit_breaker_active() and start_tier == "low":
            print("Circuit breaker ACTIVE: Bypassing Low tier; routing directly to Mid tier.")
            tiers_sequence = ["mid", "high"]

        attempts_log = []

        for attempt, tier_key in enumerate(tiers_sequence[: self.max_attempts], start=1):
            route_info = self.router.route(action, override_tier=tier_key)
            start_time = time.time()

            try:
                result = execution_func(route_info)
                elapsed = time.time() - start_time

                # Record token usage/cost in cost tracker
                self.cost_tracker.record_call(
                    model_name=route_info["model_name"],
                    tier=route_info["tier"],
                    input_tokens=1000,
                    output_tokens=500,
                    action=action,
                )

                # Validate result if validator provided
                valid = validator_func(result) if validator_func else True

                attempts_log.append({
                    "attempt": attempt,
                    "tier": route_info["tier"],
                    "model": route_info["model_name"],
                    "status": "SUCCESS" if valid else "VALIDATION_FAILED",
                    "latency_sec": elapsed,
                })

                if valid:
                    return {
                        "status": "SUCCESS",
                        "final_tier": route_info["tier"],
                        "result": result,
                        "attempts": attempts_log,
                    }
                else:
                    self.escalation_timestamps.append(time.time())

            except Exception as e:
                elapsed = time.time() - start_time
                self.escalation_timestamps.append(time.time())
                attempts_log.append({
                    "attempt": attempt,
                    "tier": route_info["tier"],
                    "model": route_info["model_name"],
                    "status": "EXCEPTION",
                    "error": str(e),
                    "latency_sec": elapsed,
                })

        return {
            "status": "FAILED",
            "final_tier": "NONE",
            "error": "Exhausted all escalation tiers without valid response.",
            "attempts": attempts_log,
            "human_alert": True,
        }
