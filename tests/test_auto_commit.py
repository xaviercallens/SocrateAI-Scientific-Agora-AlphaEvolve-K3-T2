import unittest
import os
import tempfile
from src.utils.auto_commit import auto_commit, record_snapshot_manifest, get_file_hash


class TestAutoCommit(unittest.TestCase):
    def test_get_file_hash(self):
        with tempfile.NamedTemporaryFile("w", delete=False) as f:
            f.write("test content for hashing")
            temp_path = f.name
        try:
            h = get_file_hash(temp_path)
            self.assertTrue(len(h) == 64)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_record_snapshot_manifest(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = os.path.join(tmpdir, "test.txt")
            with open(test_file, "w") as f:
                f.write("hello auto commit")

            entry = record_snapshot_manifest(tmpdir, "test snapshot")
            self.assertEqual(entry["message"], "test snapshot")
            self.assertGreater(entry["total_tracked_files"], 0)
            self.assertTrue(os.path.exists(os.path.join(tmpdir, "results", "auto_commit_manifest.json")))

    def test_auto_commit_function(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = os.path.join(tmpdir, "code.py")
            with open(test_file, "w") as f:
                f.write("print('auto commit')")

            res = auto_commit(workspace_dir=tmpdir, message="unit test commit")
            self.assertTrue(res["committed"])
            self.assertIn(res["mode"], ["GIT_CLI", "MANIFEST_SNAPSHOT"])


if __name__ == "__main__":
    unittest.main()
