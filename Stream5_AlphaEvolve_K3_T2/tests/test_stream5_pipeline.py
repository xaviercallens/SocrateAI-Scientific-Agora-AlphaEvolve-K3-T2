import unittest
import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

from alphaevolve_core.monge_ampere_evaluator import evaluate_k3_t2_monge_ampere_loss
from alphaevolve_core.topology_search import run_k3_t2_alphaevolve_search
from accelerators.tpu_sharding_accelerator import setup_tpu_pod_sharding, stream_gcs_k3_data

class TestStream5Pipeline(unittest.TestCase):
    def test_monge_ampere_evaluator(self):
        predicted = [1.0, 1.0, 1.0]
        target = [1.0, 1.0, 1.0]
        loss = evaluate_k3_t2_monge_ampere_loss(predicted, target)
        self.assertAlmostEqual(loss, 0.0)

    def test_alphaevolve_topology_search(self):
        results = run_k3_t2_alphaevolve_search(generations=100)
        self.assertEqual(results["status"], "CONVERGED")
        self.assertEqual(results["stream"], "STREAM_5_K3_T2")
        self.assertLess(results["min_monge_ampere_loss"], 0.5)

    def test_accelerators(self):
        mesh = setup_tpu_pod_sharding(32)
        self.assertEqual(mesh["cores"], 32)
        stream = stream_gcs_k3_data("gs://socrateai-datalake-gen-lang-client-0625573011")
        self.assertEqual(stream["status"], "STREAMING_ACTIVE")

if __name__ == "__main__":
    unittest.main()
