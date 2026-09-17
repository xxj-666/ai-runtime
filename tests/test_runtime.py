import pytest

from ai_runtime.exceptions import MaxStepsExceededError, ProviderError
from ai_runtime.models import (
    AssistantMessage,
    ModelResponse,
    ToolCall,
    ToolCallMessage,
    ToolResultMessage,
    UserMessage,
)
from ai_runtime.providers.mock import MockProvider
from ai_runtime.runtime import AgentRuntime
from ai_runtime.state import RuntimeState
from ai_runtime.tools import ToolRegistry


def _add_registry() -> ToolRegistry:
    registry = ToolRegistry()
    registry.register(
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
        handler=lambda a, b: a + b,
    )
    return registry


def test_runtime_returns_final_text() -> None:
    runtime = AgentRuntime(MockProvider([ModelResponse(content="Hello!")]))

    result = runtime.run("Hello")

    assert result.output == "Hello!"
    assert isinstance(result.state.messages[0], UserMessage)
    assert isinstance(result.state.messages[1], AssistantMessage)
    assert result.state.provider_calls == 1
    assert result.state.tool_calls == 0


def test_runtime_executes_tool_and_preserves_portable_state() -> None:
    provider = MockProvider(
        [
            ModelResponse(
                tool_calls=(
                    ToolCall(
                        call_id="call-add",
                        name="add",
                        arguments={"a": 2, "b": 3},
                    ),
                )
            ),
            ModelResponse(content="2 + 3 = 5"),
        ]
    )
    runtime = AgentRuntime(provider, tools=_add_registry())

    result = runtime.run("Add 2 and 3")

    assert result.output == "2 + 3 = 5"
    assert result.state.provider_calls == 2
    assert result.state.tool_calls == 1
    assert isinstance(result.state.messages[1], ToolCallMessage)
    assert result.state.messages[2] == ToolResultMessage(
        call_id="call-add", name="add", output=5
    )
    assert provider.requests[1].messages == tuple(result.state.messages[:-1])


def test_runtime_can_continue_existing_state() -> None:
    state = RuntimeState()
    runtime = AgentRuntime(MockProvider([ModelResponse(content="First")]))
    runtime.run("One", state=state)

    second_runtime = AgentRuntime(MockProvider([ModelResponse(content="Second")]))
    result = second_runtime.run("Two", state=state)

    assert result.state is state
    assert [
        message.content for message in state.messages if hasattr(message, "content")
    ] == [
        "One",
        "First",
        "Two",
        "Second",
    ]


def test_runtime_stops_after_max_steps() -> None:
    call = ToolCall(call_id="1", name="add", arguments={"a": 1, "b": 1})
    runtime = AgentRuntime(
        MockProvider(
            [
                ModelResponse(tool_calls=(call,)),
                ModelResponse(tool_calls=(call,)),
            ]
        ),
        tools=_add_registry(),
        max_steps=2,
    )

    with pytest.raises(MaxStepsExceededError, match="2-step"):
        runtime.run("Keep adding")


def test_runtime_wraps_unexpected_provider_errors() -> None:
    class BrokenProvider:
        name = "broken"

        def complete(self, request):
            raise RuntimeError("network down")

    runtime = AgentRuntime(BrokenProvider())

    with pytest.raises(ProviderError, match="network down"):
        runtime.run("Hello")


def test_runtime_rejects_empty_input() -> None:
    runtime = AgentRuntime(MockProvider([ModelResponse(content="unused")]))

    with pytest.raises(ValueError, match="must not be empty"):
        runtime.run("  ")
