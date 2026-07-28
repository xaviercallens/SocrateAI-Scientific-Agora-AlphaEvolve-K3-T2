import unittest
import sys
import os

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.agent_kit_orchestrator import (
    initialize_socrateai_coordinator,
    GCPComputeTool,
    VertexAIJobTool,
    BigQueryTool
)

class TestAgentKitOrchestrator(unittest.TestCase):
    def setUp(self):
        self.project_id = "gen-lang-client-0625573011"

    def test_tools_initialization(self):
        tools = initialize_socrateai_coordinator(self.project_id)
        self.assertEqual(len(tools), 3)
        tool_names = [t.name for t in tools]
        self.assertIn("GCP Compute Manager", tool_names)
        self.assertIn("Vertex AI Job Runner", tool_names)
        self.assertIn("BigQuery Results Store", tool_names)

    def test_gcp_compute_tool_attributes(self):
        tool = GCPComputeTool(self.project_id)
        self.assertEqual(tool.project_id, self.project_id)
        self.assertEqual(tool.name, "GCP Compute Manager")

    def test_vertex_ai_job_tool_attributes(self):
        tool = VertexAIJobTool(self.project_id)
        self.assertEqual(tool.project_id, self.project_id)
        self.assertEqual(tool.name, "Vertex AI Job Runner")

    def test_bigquery_tool_attributes(self):
        tool = BigQueryTool(self.project_id)
        self.assertEqual(tool.project_id, self.project_id)
        self.assertEqual(tool.name, "BigQuery Results Store")

if __name__ == '__main__':
    unittest.main()
