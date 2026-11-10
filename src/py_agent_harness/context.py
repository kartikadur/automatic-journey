from datetime import datetime
import os

from py_agent_harness.tasks import current_task_list


SEEN = {}

def check_if_updated(file_path: str):
    """Update the SEEN dictionary with the last modified time of the given file."""
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"The file '{file_path}' does not exist.")

    last_modified_time = os.path.getmtime(file_path)
    SEEN[file_path] = last_modified_time

def changed_files_list() -> list:
    """Return a list of all files that have been changed since the last check."""
    changed_files = []
    for file_path in SEEN:
        if has_file_changed(file_path):
            changed_files.append(file_path)
    return changed_files

def has_file_changed(file_path: str) -> bool:
    """Check if the given file has changed since the last check."""
    if not os.path.isfile(file_path):
        if file_path in SEEN:
            return True # If the file is deleted, consider it as changed.
        raise FileNotFoundError(f"The file '{file_path}' does not exist.")

    last_modified_time = os.path.getmtime(file_path)
    if file_path in SEEN:
        return last_modified_time != SEEN[file_path]
    else:
        # If the file hasn't been seen before, consider it as changed.
        return True

def file_was_changed_prompt() -> str:
    """Return a note indicating that the file was changed."""
    changed = changed_files_list()
    if not changed:
        return ""
    else:
        return "\n".join(
            [
                "\n<changed-files>",
                "The following files have changed since you last read them. Read them again before editing.",
                "\n".join(changed),
                "</changed-files>\n"
            ]
        )

def task_prompt() -> str:
    return f"<tasks>\n{current_task_list()}\n</tasks>\n"

def reminder() -> dict[str, str]:
    """Additional context that is added at the end of every prompt"""
    content = (
        f"<env>\ntime: {datetime.now():%Y-%m-%d %H:%M}\n</env>\n"
        f"{task_prompt()}"
        f"{file_was_changed_prompt()}"
    )
    return {"role": "user", "content": content}