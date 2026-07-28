"""
Cost Tracker Module for Gemini API Usage.
Tracks per-call token usage and costs across model tiers, enforces monthly budget thresholds,
and supports thread-safe ledger exports.
"""

import threading
from typing import Dict, Any, List
from core.config_loader import load_gemini_config


class CostTracker:
    """
    Thread-safe ledger for recording Gemini API calls and monitoring budget limits.
    """

    def __init__(self, config: Dict[str, Any] = None):
        if config is None:
            config = load_gemini_config()
        self.cfg = config.get("gemini_model_config", {})
        self.cost_cfg = self.cfg.get("cost_management", {})
        self.tiers_cfg = self.cfg.get("tiers", {})

        self.monthly_budget = float(self.cost_cfg.get("monthly_budget_usd", 100.0))
        self.alert_percent = float(self.cost_cfg.get("alert_at_percent", 80))

        self.lock = threading.Lock()
        self.ledger: List[Dict[str, Any]] = []
        self.total_spend_usd = 0.0
        self.calls_by_tier: Dict[str, int] = {"low": 0, "mid": 0, "high": 0}

    def record_call(
        self,
        model_name: str,
        tier: str,
        input_tokens: int,
        output_tokens: int,
        action: str = "UNKNOWN",
    ) -> float:
        """
        Calculates call cost, records it in the ledger, and returns call cost in USD.
        """
        tier_key = tier.lower().replace("t-", "")
        tier_info = self.tiers_cfg.get(tier_key, {})

        cost_in_rate = tier_info.get("cost_per_million_input_tokens_usd", 0.0)
        cost_out_rate = tier_info.get("cost_per_million_output_tokens_usd", 0.0)

        cost = (input_tokens / 1_000_000.0 * cost_in_rate) + (output_tokens / 1_000_000.0 * cost_out_rate)

        with self.lock:
            self.total_spend_usd += cost
            if tier_key in self.calls_by_tier:
                self.calls_by_tier[tier_key] += 1
            else:
                self.calls_by_tier[tier_key] = 1

            record = {
                "action": action,
                "model_name": model_name,
                "tier": tier,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "cost_usd": cost,
            }
            self.ledger.append(record)

        return cost

    def get_summary(self) -> Dict[str, Any]:
        """
        Returns summary of cumulative costs, total calls, tier breakdown, and budget status.
        """
        with self.lock:
            percent_used = (self.total_spend_usd / self.monthly_budget) * 100.0 if self.monthly_budget > 0 else 0.0
            return {
                "total_spend_usd": self.total_spend_usd,
                "monthly_budget_usd": self.monthly_budget,
                "percent_budget_used": percent_used,
                "alert_triggered": percent_used >= self.alert_percent,
                "is_over_budget": self.total_spend_usd >= self.monthly_budget,
                "total_calls": len(self.ledger),
                "calls_by_tier": dict(self.calls_by_tier),
            }

    def is_over_budget(self) -> bool:
        """
        Returns True if total spend has exceeded monthly budget.
        """
        with self.lock:
            return self.total_spend_usd >= self.monthly_budget
