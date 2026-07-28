"""
Configuration loader for Gemini Model Tiering system.
Parses config/gemini_model_config.yaml with fallback to hardcoded defaults
and support for environment variable overrides.
"""

import os
import yaml
from typing import Dict, Any

DEFAULT_CONFIG: Dict[str, Any] = {
    "gemini_model_config": {
        "version": "1.0.0",
        "tiers": {
            "low": {
                "model_name": "gemini-2.0-flash-lite",
                "cost_per_million_input_tokens_usd": 0.075,
                "cost_per_million_output_tokens_usd": 0.30,
                "rpm_limit": 1500,
                "timeout_seconds": 10,
            },
            "mid": {
                "model_name": "gemini-1.5-pro",
                "cost_per_million_input_tokens_usd": 3.50,
                "cost_per_million_output_tokens_usd": 10.50,
                "rpm_limit": 360,
                "timeout_seconds": 30,
            },
            "high": {
                "model_name": "gemini-1.5-ultra",
                "cost_per_million_input_tokens_usd": 7.00,
                "cost_per_million_output_tokens_usd": 21.00,
                "rpm_limit": 60,
                "timeout_seconds": 60,
            },
        },
        "escalation": {
            "max_attempts": 3,
            "circuit_breaker_threshold": 5,
            "circuit_breaker_window_seconds": 60,
            "confidence_threshold": 0.7,
        },
        "cost_management": {
            "monthly_budget_usd": 100.0,
            "alert_at_percent": 80,
        },
        "routing_defaults": {
            "unknown_action_tier": "mid",
            "fallback_on_error_tier": "mid",
        },
    }
}


def load_gemini_config(config_path: str = None) -> Dict[str, Any]:
    """
    Loads Gemini configuration from file and applies environment variable overrides.
    """
    if config_path is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(base_dir, "config", "gemini_model_config.yaml")

    config = DEFAULT_CONFIG.copy()

    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                file_cfg = yaml.safe_load(f)
                if file_cfg and "gemini_model_config" in file_cfg:
                    config = file_cfg
        except Exception as e:
            print(f"Warning: Failed to load config from {config_path}: {e}. Using defaults.")

    cfg = config["gemini_model_config"]

    # Environment variable overrides
    env_budget = os.environ.get("SOCRATEAI_GEMINI_COST_MANAGEMENT_MONTHLY_BUDGET_USD")
    if env_budget:
        try:
            cfg["cost_management"]["monthly_budget_usd"] = float(env_budget)
        except ValueError:
            pass

    env_max_attempts = os.environ.get("SOCRATEAI_GEMINI_ESCALATION_MAX_ATTEMPTS")
    if env_max_attempts:
        try:
            cfg["escalation"]["max_attempts"] = int(env_max_attempts)
        except ValueError:
            pass

    return config
