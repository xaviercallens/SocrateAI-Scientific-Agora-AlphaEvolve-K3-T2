import unittest
import time
from core.escalation_protocol import EscalationProtocol


class TestEscalationProtocol(unittest.TestCase):
    def test_successful_execution_on_first_try(self):
        escalation = EscalationProtocol()

        def dummy_exec(route_info):
            return {"data": "ok"}

        res = escalation.execute_with_escalation(
            action="ROUTE_TASK",
            execution_func=dummy_exec,
        )
        self.assertEqual(res["status"], "SUCCESS")
        self.assertEqual(res["final_tier"], "T-Low")
        self.assertEqual(len(res["attempts"]), 1)

    def test_escalation_on_validation_failure(self):
        escalation = EscalationProtocol()

        attempts = 0

        def dummy_exec(route_info):
            nonlocal attempts
            attempts += 1
            if route_info["tier"] == "T-Low":
                return {"valid": False}
            return {"valid": True}

        res = escalation.execute_with_escalation(
            action="ROUTE_TASK",
            execution_func=dummy_exec,
            validator_func=lambda r: r.get("valid") is True,
        )
        self.assertEqual(res["status"], "SUCCESS")
        self.assertEqual(res["final_tier"], "T-Mid")
        self.assertEqual(len(res["attempts"]), 2)

    def test_circuit_breaker_bypasses_low_tier(self):
        escalation = EscalationProtocol(cb_threshold=2, cb_window_sec=60)

        # Trigger escalations to fill timestamps window with current time
        now = time.time()
        escalation.escalation_timestamps = [now, now]

        def dummy_exec(route_info):
            return {"tier_seen": route_info["tier"]}

        res = escalation.execute_with_escalation(
            action="ROUTE_TASK",
            execution_func=dummy_exec,
        )
        self.assertEqual(res["status"], "SUCCESS")
        self.assertEqual(res["final_tier"], "T-Mid")


if __name__ == "__main__":
    unittest.main()
