import unittest
from pipeline.antigravity_compute.dispatch_pre_validator import TPUDispatchPreValidator


class TestDispatchPreValidator(unittest.TestCase):
    def setUp(self):
        self.validator = TPUDispatchPreValidator()

    def test_all_checks_pass(self):
        res = self.validator.validate_dispatch()
        self.assertTrue(res["dispatch_allowed"])
        self.assertEqual(res["overall_status"], "PASS")

    def test_gcs_check_fails(self):
        res = self.validator.validate_dispatch(gcs_bucket="http://invalid-bucket")
        self.assertFalse(res["dispatch_allowed"])
        self.assertEqual(res["overall_status"], "BLOCKED")

    def test_cell_count_fails(self):
        res = self.validator.validate_dispatch(grid_cells=32)
        self.assertFalse(res["dispatch_allowed"])
        self.assertEqual(res["overall_status"], "BLOCKED")


if __name__ == "__main__":
    unittest.main()
