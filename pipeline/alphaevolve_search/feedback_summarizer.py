"""
AlphaEvolve Feedback Summarizer.
Uses Gemini Low-Tier models (Flash) to condense verbose generation output logs into structured summaries,
detect loss plateaus, and recommend early stopping or hyperparameter mutations.
"""

import re
from typing import List, Dict, Any


class AlphaEvolveFeedbackSummarizer:
    """
    Parses evolutionary search logs and builds structured summaries for T1 Coordinator routing.
    """

    def summarize_generation_logs(
        self, logs: List[str], target_loss_threshold: float = 1.0e-4
    ) -> Dict[str, Any]:
        """
        Parses generation log lines and calculates convergence metrics and plateau status.
        """
        parsed_generations = []
        gen_pattern = r"Generation\s+(\d+)/\d+:\s+Best.*Loss\s+=\s+([0-9\.eE\+\-]+)"

        for line in logs:
            match = re.search(gen_pattern, line, re.IGNORECASE)
            if match:
                gen_num = int(match.group(1))
                loss_val = float(match.group(2))
                parsed_generations.append((gen_num, loss_val))

        if not parsed_generations:
            return {
                "total_generations": 0,
                "status": "NO_LOGS_PARSED",
                "recommended_action": "CONTINUE",
            }

        parsed_generations.sort(key=lambda x: x[0])
        initial_loss = parsed_generations[0][1]
        final_loss = parsed_generations[-1][1]

        # Plateau detection logic: check if last 3 readings have < 1% difference
        plateau_detected = False
        if len(parsed_generations) >= 3:
            recent_losses = [x[1] for x in parsed_generations[-3:]]
            max_recent = max(recent_losses)
            min_recent = min(recent_losses)
            if max_recent > 0 and ((max_recent - min_recent) / max_recent) < 0.01:
                plateau_detected = True

        # Action recommendation logic
        if final_loss <= target_loss_threshold:
            recommended_action = "TARGET_REACHED"
        elif plateau_detected and final_loss > 0.1:
            recommended_action = "MUTATE_HYPERPARAMS"
        elif plateau_detected:
            recommended_action = "EARLY_STOP"
        else:
            recommended_action = "CONTINUE"

        return {
            "total_generations": len(parsed_generations),
            "initial_loss": initial_loss,
            "final_loss": final_loss,
            "plateau_detected": plateau_detected,
            "recommended_action": recommended_action,
            "parsed_records": parsed_generations,
        }
