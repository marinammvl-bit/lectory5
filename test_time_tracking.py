import unittest
from datetime import datetime, timedelta
from task_manager import TaskManager, Priority
from time_tracking import TimeTracker

class TestTimeTracker(unittest.TestCase):
    def setUp(self):
        self.manager = TaskManager()
        self.user = self.manager.create_user("Тест", "t@t.com")
        self.task = self.manager.create_task(
            "Задача", "Описание", Priority.MEDIUM,
            datetime.now() + timedelta(days=1))
        self.tracker = TimeTracker(self.manager)

    def test_start_timer(self):
        self.assertTrue(self.tracker.start_timer(self.task.task_id))
        self.assertTrue(self.tracker.is_active(self.task.task_id))

    def test_no_double_start(self):
        self.tracker.start_timer(self.task.task_id)
        self.assertFalse(self.tracker.start_timer(self.task.task_id))

    def test_start_unknown_task(self):
        with self.assertRaises(ValueError):
            self.tracker.start_timer(999)

    def test_stop_timer(self):
        self.tracker.start_timer(self.task.task_id)
        session = self.tracker.stop_timer(self.task.task_id)
        self.assertIsNotNone(session)
        self.assertIsNotNone(session.end)
        self.assertFalse(self.tracker.is_active(self.task.task_id))

    def test_stop_without_start(self):
        self.assertIsNone(self.tracker.stop_timer(self.task.task_id))

    def test_total_time_accumulates(self):
        self.tracker.start_timer(self.task.task_id)
        self.tracker.stop_timer(self.task.task_id)
        self.tracker.start_timer(self.task.task_id)
        self.tracker.stop_timer(self.task.task_id)
        total = self.tracker.get_total_time(self.task.task_id)
        self.assertGreaterEqual(total.total_seconds(), 0)
        self.assertEqual(len(self.tracker.sessions[self.task.task_id]), 2)

    def test_report_structure(self):
        self.tracker.start_timer(self.task.task_id)
        self.tracker.stop_timer(self.task.task_id)
        report = self.tracker.generate_time_report(self.task.task_id)
        for key in ("task_id", "task_title", "sessions_count",
                    "total_seconds", "sessions", "report_generated_at"):
            self.assertIn(key, report)

    def test_summary_report(self):
        self.tracker.start_timer(self.task.task_id)
        self.tracker.stop_timer(self.task.task_id)
        report = self.tracker.generate_time_report()
        self.assertEqual(len(report["tasks"]), 1)
        self.assertIn("grand_total_seconds", report)

if __name__ == "__main__":
    unittest.main(verbosity=2)
