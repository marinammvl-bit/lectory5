from datetime import datetime
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
        }
