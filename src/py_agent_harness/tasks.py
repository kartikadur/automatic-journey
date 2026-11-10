from dataclasses import dataclass
from enum import Enum


class StatusProfile(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    DONE = "done"


@dataclass
class TaskProfile:
    content: str
    status: StatusProfile

    def __post_init__(self) -> None:
        if not isinstance(self.content, str):
            raise TypeError("content must be a string")
        self.status = StatusProfile(self.status)


MARKS = {
    StatusProfile.PENDING: "[ ]",
    StatusProfile.ACTIVE: "[~]",
    StatusProfile.DONE: "[x]",
}
TASKS: list[TaskProfile] = [] # [{"content": ..., "status": ...}]


def create_task_profiles(tasks: list[TaskProfile]) -> str:
    """Create a task list with exactly one active task at a given time that should be completed."""
    if not tasks:
        return "Error: Task list must not be empty"

    active_count = sum(task.status == StatusProfile.ACTIVE for task in tasks)
    if tasks and active_count != 1:
        return "Error: A non-empty task list must have exactly one active task"

    TASKS[:] = tasks

    return current_task_list() or "There are no tasks in the task list"


def current_task_list() -> str:
    return "\n".join(f"{MARKS[task.status]} {task.content}" for task in TASKS)

