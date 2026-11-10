
import json
import os

from openai import OpenAI

from py_agent_harness.config import get_runtime_config
from py_agent_harness.context import reminder
from py_agent_harness.llm import call_client
from py_agent_harness.skills import skills_prompt
from py_agent_harness.tools import TOOLS


def build_system_prompt() -> str:
    return f"""
You are a coding agent. Your job is to code. Always code.
Use the bash tool to inspect files.
Answer back to the user once exploration is done.

Your current working directory is {os.getcwd()}.

You have skills available. Each is a set of instructions for a task.
If a skill is relevant to the user prompt, use the read_skill tool to read it and follow it.

{skills_prompt()}
"""


def run_agent(prompt: str, max_turns: int = 12) -> None:
    runtime_config = get_runtime_config()
    client = OpenAI(
        api_key=runtime_config["API_KEY"],
        base_url=runtime_config["BASE_URL"],
    )
    messages = [
        {"role": "system", "content": build_system_prompt()},
        {"role": "user", "content": prompt},
    ]

    for _ in range(max_turns):
        late_injection = reminder()
        message, usage = call_client(client, runtime_config["API_MODEL"], messages + [late_injection])
        messages.append(message.model_dump(exclude_none=True))

        if message.content:
            print("\nAgent: {}\n".format(message.content.strip()))

        if not message.tool_calls:
            print("\nStatus: \n{}\n".format(reminder()["content"])) # Prints status when no tool calls happen
            break

        print("\nTool Calls:\n")
        for tool_call in message.tool_calls:
            command = tool_call.function.name
            raw_arguments = tool_call.function.arguments or "{}"

            try:
                arguments = json.loads(raw_arguments)
            except json.JSONDecodeError as exc:
                error = f"Invalid JSON arguments: {exc}"
            else:
                error = None

            if error is None and not isinstance(arguments, dict):
                error = "Tool arguments must be a JSON object"
            if error is None and command not in TOOLS:
                error = f"Unknown tool: {command}"

            if error is not None:
                print(f"  {error}\n")
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps({"error": error}),
                })
                continue

            result = TOOLS[command](**arguments)
            print("  Tool: {} {} \n".format(command, arguments))
            print("  Output: {}\n".format(result))

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result,
            })

        print("\nStatus: \n{}\n".format(reminder()["content"])) # Prints status after tool calls happen

        tokens_usage = []
        tokens_usage.extend(
            "  {} {} ".format(tokens, category.split('_')[0])
            for category, tokens in (usage or {}).items()
        )
        print("\nUsage: {}\n".format(" . ".join(tokens_usage)))
    else:
        print("\nAgent stopped after reaching the maximum tool-call budget.\n")


if __name__ == "__main__":
    user_input = input("Enter your prompt: ")
    run_agent(user_input)
