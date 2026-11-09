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

def write_file(file_path:str, content:str) -> str:
    """Write the contents to a file and return a success message."""
    try:
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(content)
        return f"Successfully wrote to {file_path}"
    except Exception as exc:  # pragma: no cover - defensive logging is handled by callers
        return f"Error writing to file: {exc}"

def replace_once(file_path:str, old_str:str, new_str:str) -> str:
    """Replace the first occurrence of a string in a file and return a success message."""
    if old_str == "":
        return "Error: old_str cannot be an empty string"

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()

        if old_str not in content:
            return f"Error: '{old_str}' not found in {file_path}"

        new_content = content.replace(old_str, new_str, 1)

        with open(file_path, "w", encoding="utf-8") as file:
            file.write(new_content)

        return f"Successfully replaced first occurrence of '{old_str}' with '{new_str}' in {file_path}"
    except Exception as exc:  # pragma: no cover - defensive logging is handled by callers
        return f"Error replacing string in file: {exc}"

def replace_all(file_path:str, old_str:str, new_str:str, expected_matches: int) -> str:
    """Replace a string in a file and return a success message."""
    if old_str == "":
        return "Error: old_str cannot be an empty string"

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()

        match_count = content.count(old_str)

        if match_count == 0:
            return f"Error: '{old_str}' not found in {file_path}"

        if match_count != expected_matches:
            return f"Error: Expected {expected_matches} occurrences of '{old_str}' in {file_path}, but found {match_count}"

        new_content = content.replace(old_str, new_str)

        with open(file_path, "w", encoding="utf-8") as file:
            file.write(new_content)

        return f"Successfully replaced '{old_str}' with '{new_str}' in {file_path}"
    except Exception as exc:  # pragma: no cover - defensive logging is handled by callers
        return f"Error replacing string in file: {exc}"

def replace_at_index(file_path:str, old_str:str, new_str:str, index:int) -> str:
    """Replace a string in a file at a specific index and return a success message."""
    if old_str == "":
        return "Error: old_str cannot be an empty string"

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()

        occurrences = content.count(old_str)

        if index < 0 or index >= occurrences:
            return f"Error: Index {index} is out of bounds for occurrences of '{old_str}' in {file_path}"


        """Start with the first occurrence and find the index of the nth occurrence."""
        occurrence_index = content.find(old_str)
        for _ in range(index):
            occurrence_index = content.find(old_str, occurrence_index + len(old_str))

        new_content = content[:occurrence_index] + new_str + content[occurrence_index + len(old_str):]

        with open(file_path, "w", encoding="utf-8") as file:
            file.write(new_content)

        return f"Successfully replaced occurrence {index} of '{old_str}' with '{new_str}' in {file_path}"
    except Exception as exc:  # pragma: no cover - defensive logging is handled by callers
        return f"Error replacing string in file: {exc}"

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
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write the contents to a file and return a success message",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "The path to the file to write",
                    },
                    "content": {
                        "type": "string",
                        "description": "The content to write to the file",
                    },
                },
                "required": ["file_path", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "replace_once",
            "description": "Replace the first occurrence of a string in a file and return a success message",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "The path to the file in which to replace the string",
                    },
                    "old_str": {
                        "type": "string",
                        "description": "The string to be replaced",
                    },
                    "new_str": {
                        "type": "string",
                        "description": "The string to replace with",
                    },
                },
                "required": ["file_path", "old_str", "new_str"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "replace_all",
            "description": "Replace all occurrences of a string in a file and return a success message",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "The path to the file in which to replace the string",
                    },
                    "old_str": {
                        "type": "string",
                        "description": "The string to be replaced",
                    },
                    "new_str": {
                        "type": "string",
                        "description": "The string to replace with",
                    },
                    "expected_matches": {
                        "type": "integer",
                        "description": "The expected number of occurrences of the string to replace. It is a safeguard to prevent accidental replacements. If the actual number of occurrences does not match this value, the replacement will not be performed.",
                    },
                },
                "required": ["file_path", "old_str", "new_str", "expected_matches"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "replace_at_index",
            "description": "Replace a string in a file at a specific index and return a success message",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "The path to the file in which to replace the string",
                    },
                    "old_str": {
                        "type": "string",
                        "description": "The string to be replaced",
                    },
                    "new_str": {
                        "type": "string",
                        "description": "The string to replace with",
                    },
                    "index": {
                        "type": "integer",
                        "description": "The index of the occurrence of the string to replace (0-based)",
                    },
                },
                "required": ["file_path", "old_str", "new_str", "index"],
            },
        },
    },
]

TOOLS = {
    "bash": bash,
    "read_file": read_file,
    "read_skill": read_skill,
    "write_file": write_file,
    "replace_once": replace_once,
    "replace_all": replace_all,
    "replace_at_index": replace_at_index
}
