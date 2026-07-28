import unittest
import numpy as np
import tempfile
import os
from src.alpha_evolve.neural_surrogate import NeuralSurrogate


class TestNeuralSurrogate(unittest.TestCase):
    def test_predict_batch_shape(self):
        model = NeuralSurrogate(feature_dim=8, hidden_layers=[32, 16])
        X = np.random.randn(10, 8)
        preds = model.predict_batch(X)
        self.assertEqual(preds.shape, (10, 1))

    def test_predictions_in_range(self):
        model = NeuralSurrogate(feature_dim=8, hidden_layers=[32, 16])
        X = np.random.randn(100, 8)
        preds = model.predict_batch(X)
        self.assertTrue(np.all(preds >= 0.0))
        self.assertTrue(np.all(preds <= 1.0))

    def test_training_reduces_loss(self):
        model = NeuralSurrogate(feature_dim=8, hidden_layers=[32, 16])
        X, y = NeuralSurrogate.generate_synthetic_training_data(n_samples=500, pf_order=4)
        result = model.train(X, y, epochs=50, lr=0.01)
        self.assertLess(result["final_loss"], result["loss_history"][0])

    def test_save_load_round_trip(self):
        model = NeuralSurrogate(feature_dim=8, hidden_layers=[32, 16])
        X = np.random.randn(5, 8)
        preds_before = model.predict_batch(X)

        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "model.npz")
            model.save(path)

            loaded = NeuralSurrogate(feature_dim=8, hidden_layers=[32, 16])
            loaded.load(path)
            preds_after = loaded.predict_batch(X)

        np.testing.assert_array_almost_equal(preds_before, preds_after)

    def test_synthetic_data_generation(self):
        X, y = NeuralSurrogate.generate_synthetic_training_data(n_samples=100, pf_order=4)
        self.assertEqual(X.shape, (100, 8))
        self.assertEqual(y.shape, (100,))
        self.assertTrue(np.all(y >= 0.0))
        self.assertTrue(np.all(y <= 1.0))

    def test_throughput(self):
        """Ensure ≥ 10,000 predictions/sec on CPU."""
        import time
        model = NeuralSurrogate(feature_dim=8, hidden_layers=[128, 64, 32])
        X = np.random.randn(10000, 8)
        start = time.time()
        model.predict_batch(X)
        elapsed = time.time() - start
        throughput = 10000 / elapsed
        self.assertGreater(throughput, 10000, f"Throughput too low: {throughput:.0f}/sec")


if __name__ == "__main__":
    unittest.main()
