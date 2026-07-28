"""
Model Router Module for Gemini Tier Management.
Maps task actions to appropriate model tiers (Low, Mid, High) and calculates token cost estimates.
"""

from typing import Dict, Any, Optional
from core.config_loader import load_gemini_config

# 18 Task Action Mappings
ACTION_TIER_MAP: Dict[str, str] = {
    # Tier Low (Flash)
    "ROUTE_TASK": "low",
    "AGGREGATE_STATUS": "low",
    "PRE_VALIDATE_DISPATCH": "low",
    "SUMMARIZE_LOGS": "low",
    "FORMAT_RESULTS": "low",
    "HEALTH_CHECK": "low",
    # Tier Mid (Pro)
    "ANALYZE_LOSS_TRAJECTORY": "mid",
    "ERROR_RECOVERY": "mid",
    "CROSS_VALIDATION": "mid",
    "PARAMETER_RECOMMENDATION": "mid",
    "PLAN_WORKFLOW": "mid",
    "DIAGNOSE_FAILURE": "mid",
    "GENERATE_CODE_SNIPPET": "mid",
    "OPTIMIZE_HYPERPARAMETERS": "mid",
    # Tier High (Ultra)
    "NOVEL_TOPOLOGY_EVALUATION": "high",
    "PUBLICATION_ANALYSIS": "high",
    "CROSS_STREAM_SYNTHESIS": "high",
    "THEOREM_PROVING_ASSIST": "high",
}


class ModelRouter:
    """
    Routes task actions to corresponding Gemini model tiers and calculates cost estimates.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        if config is None:
            config = load_gemini_config()
        self.cfg = config.get("gemini_model_config", {})
        self.tiers = self.cfg.get("tiers", {})
        self.routing_defaults = self.cfg.get("routing_defaults", {})

    def route(
        self,
        task_action: str,
        input_tokens: int = 1000,
        output_tokens: int = 500,
        override_tier: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Determines model tier, model name, and estimated cost for a given task action.
        """
        if override_tier and override_tier in self.tiers:
            selected_tier_key = override_tier
        else:
            selected_tier_key = ACTION_TIER_MAP.get(
                task_action, self.routing_defaults.get("unknown_action_tier", "mid")
            )

        tier_info = self.tiers.get(selected_tier_key, self.tiers.get("mid", {}))

        model_name = tier_info.get("model_name", "gemini-1.5-pro")
        cost_in = (input_tokens / 1_000_000.0) * tier_info.get("cost_per_million_input_tokens_usd", 0.0)
        cost_out = (output_tokens / 1_000_000.0) * tier_info.get("cost_per_million_output_tokens_usd", 0.0)
        total_cost = cost_in + cost_out

        tier_name = f"T-{selected_tier_key.capitalize()}"

        return {
            "task_action": task_action,
            "tier": tier_name,
            "tier_key": selected_tier_key,
            "model_name": model_name,
            "estimated_cost_usd": total_cost,
            "rpm_limit": tier_info.get("rpm_limit", 360),
            "timeout_seconds": tier_info.get("timeout_seconds", 30),
        }
