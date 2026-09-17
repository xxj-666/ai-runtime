"""Run the optional OpenAI adapter with an explicit model selection."""

import os

from ai_runtime import AgentRuntime, ToolRegistry
from ai_runtime.providers import OpenAIProvider


def add(a: int, b: int) -> int:
    return a + b


api_key = os.getenv("OPENAI_API_KEY")
model = os.getenv("OPENAI_MODEL")
if not api_key or not model:
    raise SystemExit(
        "Set OPENAI_API_KEY and OPENAI_MODEL before running this optional example."
    )

tools = ToolRegistry()
tools.register(
    name="add",
    description="Add two integers.",
    parameters={
        "type": "object",
        "properties": {
            "a": {"type": "integer"},
            "b": {"type": "integer"},
        },
        "required": ["a", "b"],
        "additionalProperties": False,
    },
    handler=add,
)

runtime = AgentRuntime(
    OpenAIProvider(model=model, api_key=api_key),
    tools=tools,
)
result = runtime.run("Use the add tool to calculate 19 + 23, then explain the result.")
print(result.output)
