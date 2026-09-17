import pytest

from ai_runtime.models import ModelResponse, ToolCall


def test_model_response_accepts_text() -> None:
    response = ModelResponse(content="hello")

    assert response.content == "hello"


def test_model_response_accepts_tool_calls() -> None:
    call = ToolCall(call_id="call-1", name="add", arguments={"a": 1, "b": 2})

    response = ModelResponse(tool_calls=(call,))

    assert response.tool_calls == (call,)


@pytest.mark.parametrize(
    ("content", "tool_calls"),
    [(None, ()), ("", ()), ("text", (ToolCall("1", "add", {}),))],
)
def test_model_response_requires_exactly_one_output(
    content: str | None, tool_calls: tuple[ToolCall, ...]
) -> None:
    with pytest.raises(ValueError, match="exactly one"):
        ModelResponse(content=content, tool_calls=tool_calls)
