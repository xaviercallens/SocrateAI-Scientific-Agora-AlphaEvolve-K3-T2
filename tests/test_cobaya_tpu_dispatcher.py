import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pipeline.antigravity_compute.cobaya_tpu_dispatcher import (
    build_antigravity_execution_graph,
    dispatch_tpu_parameter_sweep
)

class TestCobayaTpuDispatcher(unittest.TestCase):
    def test_build_antigravity_execution_graph(self):
        graph = build_antigravity_execution_graph(grid_cells=56)
        self.assertEqual(len(graph), 56)
        self.assertEqual(graph[0]["cell_id"], 1)
        self.assertEqual(graph[55]["cell_id"], 56)
        self.assertEqual(graph[0]["target"], "TPU_v4_POD")

    def test_dispatch_tpu_parameter_sweep(self):
        graph = build_antigravity_execution_graph(grid_cells=56)
        results = dispatch_tpu_parameter_sweep(graph)
        self.assertEqual(results["completed_cells"], 56)
        self.assertEqual(results["status"], "PROFILE_LIKELIHOOD_CONVERGED")

if __name__ == '__main__':
    unittest.main()
