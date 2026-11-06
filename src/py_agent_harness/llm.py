import json
import subprocess

from openai import OpenAI

from py_agent_harness.config import API_KEY, API_MODEL, BASE_URL

client = OpenAI(
    api_key=API_KEY, 
    base_url=BASE_URL
)

user_input = input("Enter your prompt: ")

SYSTEM_PROMPT = """
You are a coding agent. Your job is to code. Always code.
Use the bash tool to inspect files.
Answer back to the user once exploration is done.
"""
BASH_TOOL = {
    "type": "function",
    "function": {
        "name": "bash",
        "description": "Execute a bash command and return result",
        "parameters": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The bash command to execute"
                }
            },
            "required": ["command"]
        }
    }
}

def bash(command: str) -> str:
    """Execute a bash command and return the output."""
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        return f"Error: {result.stderr.strip()}"
    return result.stdout.strip()

response = client.chat.completions.create(
    model=API_MODEL,
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_input}
    ],
    tools=[BASH_TOOL]
)

message = response.choices[0].message
output = message.content

completion_details = response.usage.completion_tokens_details
prompt_details = response.usage.prompt_tokens_details

usage = {
    "prompt_tokens": response.usage.prompt_tokens,
    "completion_tokens": response.usage.completion_tokens,
    "reasoning_tokens": getattr(completion_details, "reasoning_tokens", None),
    "cached_tokens": getattr(prompt_details, "cached_tokens", None),
}

print("\nAgent: {}".format(output))

if message.tool_calls:
    print("\nTool Calls:")
    for tool_call in message.tool_calls:
        command = json.loads(tool_call.function.arguments).get("command", "")
        print("  Tool: bash {}".format(command))
        print("  Output: {}".format(bash(command)))

print("\nUsage:")
for category, tokens in usage.items():
    print("  {}: {}".format(category.replace('_', ' ').title(), tokens))