"""
Neural Surrogate Model for Tier 1 fast fitness prediction.
Pure NumPy MLP that predicts empirical fitness from K3T2Candidate feature vectors.
"""

import numpy as np
from typing import List, Dict, Tuple, Optional


class NeuralSurrogate:
    """
    Lightweight MLP surrogate that predicts empirical fitness from candidate feature vectors.
    Pure NumPy implementation — no PyTorch/TensorFlow dependency.
    """

    def __init__(self, feature_dim: int, hidden_layers: List[int] = None):
        if hidden_layers is None:
            hidden_layers = [128, 64, 32]
        self.feature_dim = feature_dim
        self.hidden_layers = hidden_layers

        # Initialize weights (Xavier initialization)
        self.weights: List[np.ndarray] = []
        self.biases: List[np.ndarray] = []

        layer_sizes = [feature_dim] + hidden_layers + [1]
        rng = np.random.default_rng(42)
        for i in range(len(layer_sizes) - 1):
            fan_in = layer_sizes[i]
            fan_out = layer_sizes[i + 1]
            scale = np.sqrt(2.0 / (fan_in + fan_out))
            self.weights.append(rng.normal(0, scale, (fan_in, fan_out)))
            self.biases.append(np.zeros(fan_out))

        # Adam optimizer state
        self.m_w = [np.zeros_like(w) for w in self.weights]
        self.v_w = [np.zeros_like(w) for w in self.weights]
        self.m_b = [np.zeros_like(b) for b in self.biases]
        self.v_b = [np.zeros_like(b) for b in self.biases]
        self.t = 0

    @staticmethod
    def _relu(x: np.ndarray) -> np.ndarray:
        return np.maximum(0, x)

    @staticmethod
    def _relu_grad(x: np.ndarray) -> np.ndarray:
        return (x > 0).astype(np.float64)

    @staticmethod
    def _sigmoid(x: np.ndarray) -> np.ndarray:
        return 1.0 / (1.0 + np.exp(-np.clip(x, -500, 500)))

    def _forward(self, X: np.ndarray) -> Tuple[np.ndarray, List[np.ndarray], List[np.ndarray]]:
        """Forward pass returning output, pre-activations, and activations."""
        activations = [X]
        pre_activations = []

        for i in range(len(self.weights) - 1):
            z = activations[-1] @ self.weights[i] + self.biases[i]
            pre_activations.append(z)
            activations.append(self._relu(z))

        # Output layer with sigmoid
        z_out = activations[-1] @ self.weights[-1] + self.biases[-1]
        pre_activations.append(z_out)
        output = self._sigmoid(z_out)
        activations.append(output)

        return output, pre_activations, activations

    def predict_batch(self, X: np.ndarray) -> np.ndarray:
        """Batch predict fitness from feature matrix (N × feature_dim) → (N, 1)."""
        output, _, _ = self._forward(X)
        return output

    def predict(self, candidates) -> np.ndarray:
        """Predict fitness for a list of K3T2Candidate objects."""
        X = np.array([c.to_feature_vector() for c in candidates])
        return self.predict_batch(X).flatten()

    def train(
        self,
        X: np.ndarray,
        y: np.ndarray,
        epochs: int = 100,
        lr: float = 0.001,
        batch_size: int = 64,
        beta1: float = 0.9,
        beta2: float = 0.999,
        eps: float = 1e-8,
    ) -> Dict:
        """
        Train on (feature_vector, ground_truth_fitness) pairs using Adam optimizer.
        """
        y = y.reshape(-1, 1)
        n_samples = X.shape[0]
        losses = []

        for epoch in range(epochs):
            # Shuffle
            perm = np.random.permutation(n_samples)
            X_shuffled = X[perm]
            y_shuffled = y[perm]

            epoch_loss = 0.0
            n_batches = 0

            for start in range(0, n_samples, batch_size):
                end = min(start + batch_size, n_samples)
                X_batch = X_shuffled[start:end]
                y_batch = y_shuffled[start:end]
                bs = X_batch.shape[0]

                # Forward
                output, pre_acts, acts = self._forward(X_batch)

                # MSE loss
                loss = np.mean((output - y_batch) ** 2)
                epoch_loss += loss
                n_batches += 1

                # Backward pass
                d_out = 2.0 * (output - y_batch) / bs
                # Sigmoid gradient
                d_out = d_out * output * (1 - output)

                d_weights = []
                d_biases = []

                delta = d_out
                for i in range(len(self.weights) - 1, -1, -1):
                    dw = acts[i].T @ delta
                    db = np.sum(delta, axis=0)
                    d_weights.insert(0, dw)
                    d_biases.insert(0, db)

                    if i > 0:
                        delta = (delta @ self.weights[i].T) * self._relu_grad(pre_acts[i - 1])

                # Adam update
                self.t += 1
                for i in range(len(self.weights)):
                    self.m_w[i] = beta1 * self.m_w[i] + (1 - beta1) * d_weights[i]
                    self.v_w[i] = beta2 * self.v_w[i] + (1 - beta2) * d_weights[i] ** 2
                    m_hat_w = self.m_w[i] / (1 - beta1 ** self.t)
                    v_hat_w = self.v_w[i] / (1 - beta2 ** self.t)
                    self.weights[i] -= lr * m_hat_w / (np.sqrt(v_hat_w) + eps)

                    self.m_b[i] = beta1 * self.m_b[i] + (1 - beta1) * d_biases[i]
                    self.v_b[i] = beta2 * self.v_b[i] + (1 - beta2) * d_biases[i] ** 2
                    m_hat_b = self.m_b[i] / (1 - beta1 ** self.t)
                    v_hat_b = self.v_b[i] / (1 - beta2 ** self.t)
                    self.biases[i] -= lr * m_hat_b / (np.sqrt(v_hat_b) + eps)

            avg_loss = epoch_loss / max(n_batches, 1)
            losses.append(avg_loss)

        return {"epochs": epochs, "final_loss": losses[-1] if losses else 0.0, "loss_history": losses}

    def save(self, path: str) -> None:
        """Serialize model weights to .npz file."""
        data = {}
        for i, (w, b) in enumerate(zip(self.weights, self.biases)):
            data[f"w_{i}"] = w
            data[f"b_{i}"] = b
        data["feature_dim"] = np.array([self.feature_dim])
        data["hidden_layers"] = np.array(self.hidden_layers)
        np.savez(path, **data)

    def load(self, path: str) -> None:
        """Load model weights from .npz file."""
        data = np.load(path)
        n_layers = (len(data.files) - 2) // 2
        self.weights = [data[f"w_{i}"] for i in range(n_layers)]
        self.biases = [data[f"b_{i}"] for i in range(n_layers)]
        self.feature_dim = int(data["feature_dim"][0])
        self.hidden_layers = data["hidden_layers"].tolist()

    @staticmethod
    def generate_synthetic_training_data(
        n_samples: int = 5000,
        pf_order: int = 4,
        rng: Optional[np.random.Generator] = None,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate synthetic K3×T² samples with analytic fitness approximation.
        Fitness is an inverse function of the L1 norm of Picard-Fuchs coefficients
        combined with the complex structure stability measure.
        """
        if rng is None:
            rng = np.random.default_rng(42)

        pf_coeffs = rng.uniform(-5.0, 5.0, (n_samples, pf_order))
        tau1 = rng.uniform(-0.5, 0.5, (n_samples, 1))
        tau2 = rng.uniform(0.1, 3.0, (n_samples, 1))
        rho1 = rng.uniform(0.0, 5.0, (n_samples, 1))
        rho2 = rng.uniform(0.1, 5.0, (n_samples, 1))

        X = np.hstack([pf_coeffs, tau1, tau2, rho1, rho2])

        # Analytic fitness: inverse of PF complexity + τ₂ stability bonus
        pf_complexity = np.sum(np.abs(pf_coeffs), axis=1)
        tau_stability = tau2.flatten() / (1.0 + np.abs(tau1.flatten()))
        raw_fitness = tau_stability / (1.0 + pf_complexity)
        # Normalize to [0, 1]
        y = (raw_fitness - raw_fitness.min()) / (raw_fitness.max() - raw_fitness.min() + 1e-10)

        return X, y
