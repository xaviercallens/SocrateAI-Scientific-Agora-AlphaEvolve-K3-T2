"""
Tier Classifier Module.
Classifies incoming natural language directives into target action strings and confidence scores using high-speed pattern matching.
"""

import re
from typing import Dict, Any, List, Tuple

DIRECTIVE_PATTERNS: List[Tuple[str, str, float]] = [
    # High-Tier (Ultra)
    (r"\b(novel topology|publishable|breakthrough|new neural architecture)\b", "NOVEL_TOPOLOGY_EVALUATION", 0.98),
    (r"\b(draft paper|publication analysis|scientific report|write section)\b", "PUBLICATION_ANALYSIS", 0.98),
    (r"\b(cross-stream|synthesize streams|stream 2 and stream 3)\b", "CROSS_STREAM_SYNTHESIS", 0.98),

    # Mid-Tier (Pro)
    (r"\b(analyze|trajectory|loss curve|monge-ampere loss)\b", "ANALYZE_LOSS_TRAJECTORY", 0.95),
    (r"\b(cross-validate|kreuzer-skarke check|kreuzer-skarke)\b", "CROSS_VALIDATION", 0.95),
    (r"\b(recommend parameter|grid refinement|mcmc refine)\b", "PARAMETER_RECOMMENDATION", 0.95),
    (r"\b(error|recovery|failure|diagnose failure|fix pipeline)\b", "ERROR_RECOVERY", 0.92),
    (r"\b(plan|workflow|architect)\b", "PLAN_WORKFLOW", 0.85),
    (r"\b(stack trace|crash)\b", "DIAGNOSE_FAILURE", 0.90),

    # Low-Tier Specific (Flash)
    (r"\b(aggregate|merge|combine)\s+(status|results|reports)\b", "AGGREGATE_STATUS", 0.95),
    (r"\b(pre-validate|preflight|check tpu|check quota|check bucket)\b", "PRE_VALIDATE_DISPATCH", 0.95),
    (r"\b(summarize logs|condense logs|parse logs)\b", "SUMMARIZE_LOGS", 0.95),
    (r"\b(format|bigquery format|json format)\b", "FORMAT_RESULTS", 0.90),
    (r"\b(health check|ping endpoint|liveness)\b", "HEALTH_CHECK", 0.95),

    # Low-Tier General Fallback (Flash)
    (r"\b(check|route|dispatch|status|aggregate|health|validate|summary|summarize|format|log|ping)\b", "ROUTE_TASK", 0.75),
]


class TierClassifier:
    """
    Classifies raw directive text into action categories and confidence levels.
    """

    def __init__(self, confidence_threshold: float = 0.7):
        self.confidence_threshold = confidence_threshold

    def classify(self, directive: str, pipeline_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Analyzes directive text and returns classified action, confidence, and escalation recommendation.
        """
        text = directive.lower().strip()
        best_action = "ROUTE_TASK"
        best_confidence = 0.5

        for pattern, action, score in DIRECTIVE_PATTERNS:
            if re.search(pattern, text):
                if score > best_confidence:
                    best_confidence = score
                    best_action = action

        escalate = best_confidence < self.confidence_threshold

        return {
            "directive": directive,
            "classified_action": best_action,
            "confidence": best_confidence,
            "escalate": escalate,
        }
