import subprocess

from py_agent_harness.skills import read_skill


def bash(command: str, timeout: int = 30) -> str:
    """Execute a bash command and return the output."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return f"Error: command timed out after {timeout} seconds"

    if result.returncode != 0:
        stderr = result.stderr.strip()
        if stderr:
            return f"Error: {stderr}"
        return f"Error: command exited with code {result.returncode}"
    return result.stdout.strip() or "No output"


def read_file(file_path: str) -> str:
    """Read the contents of a file and return it as a string."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    except Exception as exc:  # pragma: no cover - defensive logging is handled by callers
        return f"Error reading file: {exc}"


TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "bash",
            "description": "Execute a bash command and return result",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The bash command to execute",
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Maximum command runtime in seconds",
                    },
                },
                "required": ["command"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the contents of a file and return it as a string",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "The path to the file to read",
                    },
                },
                "required": ["file_path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_skill",
            "description": "Read the contents of a skill and return it as a string",
            "parameters": {
                "type": "object",
                "properties": {
                    "skill_name": {
                        "type": "string",
                        "description": "The name of the skill to read",
                    },
                },
                "required": ["skill_name"],
            },
        },
    }
]

TOOLS = {
    "bash": bash,
    "read_file": read_file,
    "read_skill": read_skill,
}
