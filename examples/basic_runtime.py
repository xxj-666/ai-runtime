"""Run a complete provider -> tool -> provider loop without an API key."""

from ai_runtime import AgentRuntime, ModelResponse, ToolCall, ToolRegistry
from ai_runtime.providers import MockProvider


def add(a: int, b: int) -> int:
    return a + b


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

provider = MockProvider(
    [
        ModelResponse(
            tool_calls=(
                ToolCall(
                    call_id="example-call",
                    name="add",
                    arguments={"a": 2, "b": 3},
                ),
            )
        ),
        ModelResponse(content="2 + 3 = 5"),
    ]
)

result = AgentRuntime(provider, tools=tools).run("Add 2 and 3")

print(result.output)
print(
    f"provider_calls={result.state.provider_calls} tool_calls={result.state.tool_calls}"
)
