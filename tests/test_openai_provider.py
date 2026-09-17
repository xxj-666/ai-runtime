from types import SimpleNamespace

import pytest

from ai_runtime.exceptions import ProviderError, ProviderResponseError
from ai_runtime.models import (
    ModelRequest,
    ToolCallMessage,
    ToolResultMessage,
    ToolSpec,
    UserMessage,
)
from ai_runtime.providers.openai import OpenAIProvider


class FakeResponses:
    def __init__(self, response) -> None:
        self.response = response
        self.calls: list[dict[str, object]] = []

    def create(self, **payload):
        self.calls.append(payload)
        if isinstance(self.response, Exception):
            raise self.response
        return self.response


def _provider(response) -> tuple[OpenAIProvider, FakeResponses]:
    responses = FakeResponses(response)
    client = SimpleNamespace(responses=responses)
    return OpenAIProvider(model="test-model", client=client), responses


def test_openai_provider_maps_final_text() -> None:
    provider, responses = _provider(
        SimpleNamespace(output=[], output_text="A portable answer")
    )

    result = provider.complete(ModelRequest(messages=(UserMessage("Hello"),)))

    assert result.content == "A portable answer"
    assert responses.calls[0]["model"] == "test-model"
    assert responses.calls[0]["store"] is False
    assert responses.calls[0]["input"] == [{"role": "user", "content": "Hello"}]


def test_openai_provider_maps_function_call_and_tool_schema() -> None:
    item = SimpleNamespace(
        type="function_call",
        call_id="call-1",
        name="add",
        arguments='{"a": 2, "b": 3}',
    )
    provider, responses = _provider(SimpleNamespace(output=[item], output_text=""))
    tool = ToolSpec(
        name="add",
        description="Add integers.",
        parameters={
            "type": "object",
            "properties": {
                "a": {"type": "integer"},
                "b": {"type": "integer"},
            },
            "required": ["a", "b"],
            "additionalProperties": False,
        },
    )

    result = provider.complete(
        ModelRequest(messages=(UserMessage("Add"),), tools=(tool,))
    )

    assert result.tool_calls[0].arguments == {"a": 2, "b": 3}
    assert responses.calls[0]["tools"] == [
        {
            "type": "function",
            "name": "add",
            "description": "Add integers.",
            "parameters": tool.parameters,
            "strict": True,
        }
    ]


def test_openai_provider_maps_portable_tool_history() -> None:
    provider, responses = _provider(SimpleNamespace(output=[], output_text="Done"))
    request = ModelRequest(
        messages=(
            UserMessage("Add"),
            ToolCallMessage("call-1", "add", {"a": 2, "b": 3}),
            ToolResultMessage("call-1", "add", 5),
        )
    )

    provider.complete(request)

    assert responses.calls[0]["input"][1:] == [
        {
            "type": "function_call",
            "call_id": "call-1",
            "name": "add",
            "arguments": '{"a": 2, "b": 3}',
        },
        {"type": "function_call_output", "call_id": "call-1", "output": "5"},
    ]


def test_openai_provider_rejects_invalid_tool_arguments() -> None:
    item = SimpleNamespace(
        type="function_call",
        call_id="call-1",
        name="add",
        arguments="not-json",
    )
    provider, _ = _provider(SimpleNamespace(output=[item], output_text=""))

    with pytest.raises(ProviderResponseError, match="invalid JSON"):
        provider.complete(ModelRequest(messages=(UserMessage("Add"),)))


def test_openai_provider_wraps_sdk_errors() -> None:
    provider, _ = _provider(RuntimeError("service unavailable"))

    with pytest.raises(ProviderError, match="service unavailable"):
        provider.complete(ModelRequest(messages=(UserMessage("Hello"),)))
