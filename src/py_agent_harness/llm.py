
from py_agent_harness.config import API_MODEL
from py_agent_harness.tools import BASH_TOOL


def call_client(client, model, messages):
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        tools=[BASH_TOOL],
    )

    message = response.choices[0].message

    completion_details = response.usage.completion_tokens_details
    prompt_details = response.usage.prompt_tokens_details

    usage = {
        "prompt_tokens": response.usage.prompt_tokens,
        "completion_tokens": response.usage.completion_tokens,
        "reasoning_tokens": getattr(completion_details, "reasoning_tokens", None),
        "cached_tokens": getattr(prompt_details, "cached_tokens", None),
    }

    return message, usage