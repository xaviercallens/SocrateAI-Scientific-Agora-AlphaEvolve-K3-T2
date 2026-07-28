import unittest
import subprocess
import json

class TestGCPIntegration(unittest.TestCase):
    def test_gcloud_cli_available(self):
        result = subprocess.run(["gcloud", "--version"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertIn("Google Cloud SDK", result.stdout)

    def test_gcp_active_project(self):
        result = subprocess.run(["gcloud", "config", "get-value", "project"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        project_id = result.stdout.strip()
        self.assertEqual(project_id, "gen-lang-client-0625573011")

    def test_gcp_active_account(self):
        result = subprocess.run(["gcloud", "config", "get-value", "account"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        account = result.stdout.strip()
        is_valid_account = ("callensxavier@gmail.com" in account) or ("developer.gserviceaccount.com" in account)
        self.assertTrue(is_valid_account, f"Unexpected account: {account}")

    def test_gcp_socrateai_project_exists(self):
        result = subprocess.run(
            ["gcloud", "projects", "describe", "gen-lang-client-0625573011", "--format=json"],
            capture_output=True,
            text=True
        )
        self.assertEqual(result.returncode, 0)
        project_info = json.loads(result.stdout)
        self.assertEqual(project_info["projectId"], "gen-lang-client-0625573011")
        self.assertIn("SocrateAI", project_info["name"])

    def test_alphaevolve_gcp_configuration(self):
        # 1. Verify Artifact Registry repository
        ar_result = subprocess.run(
            ["gcloud", "artifacts", "repositories", "describe", "stream2-alphaevolve", "--location=us-central1", "--format=json"],
            capture_output=True,
            text=True
        )
        self.assertEqual(ar_result.returncode, 0)
        ar_info = json.loads(ar_result.stdout)
        self.assertEqual(ar_info["format"], "DOCKER")

        # 2. Verify Service Account
        sa_result = subprocess.run(
            ["gcloud", "iam", "service-accounts", "describe", "alphaevolve-runner-sa@gen-lang-client-0625573011.iam.gserviceaccount.com", "--format=json"],
            capture_output=True,
            text=True
        )
        self.assertEqual(sa_result.returncode, 0)
        sa_info = json.loads(sa_result.stdout)
        self.assertEqual(sa_info["email"], "alphaevolve-runner-sa@gen-lang-client-0625573011.iam.gserviceaccount.com")

if __name__ == '__main__':
    unittest.main()
