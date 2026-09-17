import pytest

from ai_runtime.exceptions import (
    DuplicateToolError,
    InvalidToolArgumentsError,
    ToolExecutionError,
    UnknownToolError,
)
from ai_runtime.models import ToolCall
from ai_runtime.tools import ToolRegistry


def _schema() -> dict[str, object]:
    return {
        "type": "object",
        "properties": {"a": {"type": "integer"}, "b": {"type": "integer"}},
        "required": ["a", "b"],
        "additionalProperties": False,
    }


def test_register_and_execute_tool() -> None:
    registry = ToolRegistry()
    spec = registry.register(
        name="add",
        description="Add two integers.",
        parameters=_schema(),
        handler=lambda a, b: a + b,
    )

    result = registry.execute(
        ToolCall(call_id="call-1", name="add", arguments={"a": 2, "b": 3})
    )

    assert result == 5
    assert registry.specs() == (spec,)


def test_duplicate_tool_is_rejected() -> None:
    registry = ToolRegistry()
    registry.register(
        name="add",
        description="Add.",
        parameters=_schema(),
        handler=lambda a, b: a + b,
    )

    with pytest.raises(DuplicateToolError, match="already registered"):
        registry.register(
            name="add",
            description="Add again.",
            parameters=_schema(),
            handler=lambda a, b: a + b,
        )


def test_unknown_tool_is_rejected() -> None:
    registry = ToolRegistry()

    with pytest.raises(UnknownToolError, match="unknown tool"):
        registry.execute(ToolCall(call_id="1", name="missing", arguments={}))


def test_invalid_python_arguments_are_rejected() -> None:
    registry = ToolRegistry()
    registry.register(
        name="add",
        description="Add.",
        parameters=_schema(),
        handler=lambda a, b: a + b,
    )

    with pytest.raises(InvalidToolArgumentsError, match="Invalid arguments"):
        registry.execute(ToolCall(call_id="1", name="add", arguments={"a": 1}))


def test_handler_failure_is_wrapped() -> None:
    def fail() -> None:
        raise RuntimeError("boom")

    registry = ToolRegistry()
    registry.register(
        name="fail",
        description="Fail.",
        parameters={
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False,
        },
        handler=fail,
    )

    with pytest.raises(ToolExecutionError, match="boom"):
        registry.execute(ToolCall(call_id="1", name="fail", arguments={}))


def test_non_json_result_is_rejected() -> None:
    registry = ToolRegistry()
    registry.register(
        name="bad_result",
        description="Return a set.",
        parameters={
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False,
        },
        handler=lambda: {1, 2},
    )

    with pytest.raises(ToolExecutionError, match="non-JSON"):
        registry.execute(ToolCall(call_id="1", name="bad_result", arguments={}))


def test_strict_schema_must_be_closed_and_require_every_property() -> None:
    registry = ToolRegistry()

    with pytest.raises(ValueError, match="additionalProperties"):
        registry.register(
            name="open_schema",
            description="Invalid strict schema.",
            parameters={"type": "object", "properties": {}},
            handler=lambda: None,
        )
