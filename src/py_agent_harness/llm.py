from py_agent_harness.tools import TOOL_SCHEMAS


def call_client(client, model, messages):
    if not model:
        raise ValueError("model is required")

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        tools=TOOL_SCHEMAS,
    )

    if not response.choices:
        raise RuntimeError("The API returned no completion choices")

    message = response.choices[0].message
    usage_info = getattr(response, "usage", None)
    completion_details = getattr(usage_info, "completion_tokens_details", None)
    prompt_details = getattr(usage_info, "prompt_tokens_details", None)

    usage = {
        "prompt_tokens": getattr(usage_info, "prompt_tokens", 0),
        "completion_tokens": getattr(usage_info, "completion_tokens", 0),
        "reasoning_tokens": getattr(completion_details, "reasoning_tokens", None),
        "cached_tokens": getattr(prompt_details, "cached_tokens", None),
    }

    return message, usage
