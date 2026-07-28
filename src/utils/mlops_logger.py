import json
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class EvolutionCheckpoint:
    def __init__(self, checkpoint_dir: str = "./outputs/checkpoints"):
        self.checkpoint_dir = checkpoint_dir
        os.makedirs(self.checkpoint_dir, exist_ok=True)
        self.run_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    def save_generation(self, generation: int, population: list, best_candidate: dict):
        """Saves the current generation state to disk."""
        file_path = os.path.join(self.checkpoint_dir, f"run_{self.run_id}_gen_{generation}.json")
        state = {
            "generation": generation,
            "best_candidate": best_candidate,
            "population": population
        }
        with open(file_path, 'w') as f:
            json.dump(state, f, indent=2)
        logger.info(f"Checkpoint saved: {file_path}")

    def load_latest_checkpoint(self) -> dict:
        """Finds and loads the most recent checkpoint to resume evolution."""
        checkpoints = [f for f in os.listdir(self.checkpoint_dir) if f.endswith('.json')]
        if not checkpoints:
            return None
        
        # Sort by modified time to get the latest
        latest_file = max(checkpoints, key=lambda f: os.path.getmtime(os.path.join(self.checkpoint_dir, f)))
        with open(os.path.join(self.checkpoint_dir, latest_file), 'r') as f:
            logger.info(f"Resuming from checkpoint: {latest_file}")
            return json.load(f)
