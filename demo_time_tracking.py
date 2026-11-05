from datetime import datetime, timedelta
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
    print("\nСводный отчёт:")
    print(json.dumps(tracker.generate_time_report(), indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
