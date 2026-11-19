import json
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
        return None
