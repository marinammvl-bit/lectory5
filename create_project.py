import os

files = {
    "task_manager.py": """from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

class Status(Enum):
    TODO = "To Do"
    IN_PROGRESS = "In Progress"
    REVIEW = "Review"
    DONE = "Done"

class User:
    def __init__(self, user_id: int, name: str, email: str):
        self.user_id = user_id
        self.name = name
        self.email = email

    def __str__(self):
        return f"User({self.name}, {self.email})"

class Task:
    def __init__(self, task_id: int, title: str, description: str,
                 priority: Priority, due_date: datetime):
        self.task_id = task_id
        self.title = title
        self.description = description
        self.priority = priority
        self.due_date = due_date
        self.status = Status.TODO
        self.assignee: Optional[User] = None
        self.created_at = datetime.now()

    def assign_to(self, user: User):
        self.assignee = user
        self.status = Status.IN_PROGRESS

    def update_status(self, new_status: Status):
        self.status = new_status

    def is_overdue(self) -> bool:
        return datetime.now() > self.due_date

    def __str__(self):
        return f"Task '{self.title}' ({self.status.value})"

class TaskManager:
    def __init__(self):
        self.tasks: Dict[int, Task] = {}
        self.users: Dict[int, User] = {}
        self.next_task_id = 1
        self.next_user_id = 1

    def create_user(self, name: str, email: str) -> User:
        user = User(self.next_user_id, name, email)
        self.users[self.next_user_id] = user
        self.next_user_id += 1
        return user

    def create_task(self, title: str, description: str,
                    priority: Priority, due_date: datetime) -> Task:
        task = Task(self.next_task_id, title, description, priority, due_date)
        self.tasks[self.next_task_id] = task
        self.next_task_id += 1
        return task

    def assign_task(self, task_id: int, user_id: int) -> bool:
        task = self.tasks.get(task_id)
        user = self.users.get(user_id)
        if task and user:
            task.assign_to(user)
            return True
        return False

    def get_overdue_tasks(self) -> List[Task]:
        return [t for t in self.tasks.values() if t.is_overdue()]

    def get_user_tasks(self, user_id: int) -> List[Task]:
        return [t for t in self.tasks.values()
                if t.assignee and t.assignee.user_id == user_id]

    def generate_report(self) -> Dict:
        total_tasks = len(self.tasks)
        overdue_tasks = len(self.get_overdue_tasks())
        status_count = {}
        for task in self.tasks.values():
            status_count[task.status] = status_count.get(task.status, 0) + 1
        return {
            "total_tasks": total_tasks,
            "overdue_tasks": overdue_tasks,
            "status_distribution": {s.value: c for s, c in status_count.items()},
            "report_generated_at": datetime.now().isoformat(),
        }""",

    "time_tracking.py": """import json
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from task_manager import TaskManager

@dataclass
class TimeSession:
    task_id: int
    start: datetime
    end: Optional[datetime] = None

    def duration(self) -> timedelta:
        return (self.end or datetime.now()) - self.start

    def is_active(self) -> bool:
        return self.end is None

    def to_dict(self) -> dict:
        return {
            "task_id": self.task_id,
            "start": self.start.isoformat(),
            "end": self.end.isoformat() if self.end else None,
            "duration_seconds": round(self.duration().total_seconds(), 2),
        }

class TimeTracker:
    def __init__(self, task_manager: TaskManager):
        self.task_manager = task_manager
        self.sessions: Dict[int, List[TimeSession]] = {}

    def start_timer(self, task_id: int) -> bool:
        if task_id not in self.task_manager.tasks:
            raise ValueError(f"Задача {task_id} не найдена")
        if self.is_active(task_id):
            return False
        self.sessions.setdefault(task_id, []).append(
            TimeSession(task_id=task_id, start=datetime.now())
        )
        return True

    def stop_timer(self, task_id: int) -> Optional[TimeSession]:
        active = self._get_active_session(task_id)
        if active is None:
            return None
        active.end = datetime.now()
        return active

    def get_total_time(self, task_id: int) -> timedelta:
        total = timedelta()
        for s in self.sessions.get(task_id, []):
            total += s.duration()
        return total

    def get_active_task_ids(self) -> List[int]:
        return [tid for tid in self.sessions if self.is_active(tid)]

    def generate_time_report(self, task_id: Optional[int] = None) -> dict:
        if task_id is not None:
            sessions = self.sessions.get(task_id, [])
            return {
                "task_id": task_id,
                "task_title": self.task_manager.tasks[task_id].title,
                "sessions_count": len(sessions),
                "total_seconds": round(self.get_total_time(task_id).total_seconds(), 2),
                "sessions": [s.to_dict() for s in sessions],
                "report_generated_at": datetime.now().isoformat(),
            }

        rows = []
        grand_total = 0.0
        for tid, sessions in self.sessions.items():
            total_s = self.get_total_time(tid).total_seconds()
            grand_total += total_s
            rows.append({
                "task_id": tid,
                "task_title": self.task_manager.tasks[tid].title,
                "sessions_count": len(sessions),
                "total_seconds": round(total_s, 2),
            })
        return {
            "tasks": rows,
            "grand_total_seconds": round(grand_total, 2),
            "active_timers": self.get_active_task_ids(),
            "report_generated_at": datetime.now().isoformat(),
        }

    def is_active(self, task_id: int) -> bool:
        return self._get_active_session(task_id) is not None

    def _get_active_session(self, task_id: int) -> Optional[TimeSession]:
        for s in self.sessions.get(task_id, []):
            if s.is_active():
                return s
        return None""",

    "demo_time_tracking.py": """from datetime import datetime, timedelta
import json
from task_manager import TaskManager, Priority
from time_tracking import TimeTracker

def main():
    manager = TaskManager()
    dev = manager.create_user("Алексей Кодлов", "alexey@company.com")
    task = manager.create_task(
        "Разработать модуль учёта времени",
        "Реализовать TimeTracker с отчётами",
        Priority.HIGH,
        datetime.now() + timedelta(days=7),
    )
    manager.assign_task(task.task_id, dev.user_id)

    tracker = TimeTracker(manager)
    tracker.start_timer(task.task_id)
    tracker.stop_timer(task.task_id)
    tracker.start_timer(task.task_id)

    print("Активные таймеры:", tracker.get_active_task_ids())
    print("Отчёт по задаче:")
    print(json.dumps(tracker.generate_time_report(task.task_id), indent=2, ensure_ascii=False))

    tracker.stop_timer(task.task_id)
    print("\\nСводный отчёт:")
    print(json.dumps(tracker.generate_time_report(), indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()""",

    "test_time_tracking.py": """import unittest
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
    unittest.main(verbosity=2)"""
}

for filename, content in files.items():
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Создан файл: {filename}")