import unittest
from src.utils.mlops_logger import MLOpsLogger


class TestMLOpsLogger(unittest.TestCase):
    def test_none_backend(self):
        logger = MLOpsLogger(backend="none")
        self.assertEqual(logger.backend, "none")

    def test_log_generation_noop(self):
        logger = MLOpsLogger(backend="none")
        logger.log_generation(1, [], [])
        self.assertEqual(len(logger.get_logged_metrics()), 1)

    def test_log_hyperparameters_noop(self):
        logger = MLOpsLogger(backend="none")
        logger.log_hyperparameters({"pop_size": 200})
        # Should not raise

    def test_finish_noop(self):
        logger = MLOpsLogger(backend="none")
        logger.finish()

    def test_fallback_on_missing_wandb(self):
        logger = MLOpsLogger(backend="wandb_nonexistent")
        self.assertEqual(logger.backend, "wandb_nonexistent")  # unknown backend


if __name__ == "__main__":
    unittest.main()
