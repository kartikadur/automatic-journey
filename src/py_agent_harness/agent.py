
import json
import os

from openai import OpenAI

from py_agent_harness.config import API_KEY, API_MODEL, BASE_URL
from py_agent_harness.llm import call_client
from py_agent_harness.tools import TOOLS


client = OpenAI(
    api_key=API_KEY, 
    base_url=BASE_URL
)

user_input = input("Enter your prompt: ")

SYSTEM_PROMPT = f"""
You are a coding agent. Your job is to code. Always code.
Use the bash tool to inspect files.
Answer back to the user once exploration is done.

Your current working directory is {os.getcwd()}.
"""

messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_input}
    ]

while True:
    message, usage = call_client(client, API_MODEL, messages)
    messages.append(message.model_dump(exclude_none=True))

    if message.content:
        print("\nAgent: {}\n".format(message.content))

    if not message.tool_calls:
        break

    if message.tool_calls:
        print("\nTool Calls:\n")
        for tool_call in message.tool_calls:
            command = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)
            result = TOOLS[command](**arguments)
            print("  Tool: {} {} \n".format(command, arguments))
            print("  Output: {}\n".format(result))

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result
            })

    print("\nUsage:")
    for category, tokens in usage.items():
        print("  {}: {}\n".format(category.replace('_', ' ').title(), tokens))


