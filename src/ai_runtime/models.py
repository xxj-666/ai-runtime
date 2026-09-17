"""Provider-neutral request, response, and message models."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal, TypeAlias

JsonObject: TypeAlias = dict[str, Any]


@dataclass(frozen=True, slots=True)
class UserMessage:
    """A user message recorded in runtime state."""

    content: str


@dataclass(frozen=True, slots=True)
class AssistantMessage:
    """A final assistant message recorded in runtime state."""

    content: str


@dataclass(frozen=True, slots=True)
class ToolCallMessage:
    """A provider request to execute a named tool."""

    call_id: str
    name: str
    arguments: JsonObject


@dataclass(frozen=True, slots=True)
class ToolResultMessage:
    """The local result of a tool call."""

    call_id: str
    name: str
    output: Any


RuntimeMessage: TypeAlias = (
    UserMessage | AssistantMessage | ToolCallMessage | ToolResultMessage
)


@dataclass(frozen=True, slots=True)
class ToolSpec:
    """A provider-neutral function tool definition using JSON Schema."""

    name: str
    description: str
    parameters: JsonObject
    strict: bool = True


@dataclass(frozen=True, slots=True)
class ToolCall:
    """A provider-neutral request to invoke a tool."""

    call_id: str
    name: str
    arguments: JsonObject


@dataclass(frozen=True, slots=True)
class ModelRequest:
    """The complete portable input supplied to a model provider."""

    messages: tuple[RuntimeMessage, ...]
    tools: tuple[ToolSpec, ...] = ()


@dataclass(frozen=True, slots=True)
class ModelResponse:
    """A provider response containing either final text or tool calls."""

    content: str | None = None
    tool_calls: tuple[ToolCall, ...] = ()

    def __post_init__(self) -> None:
        has_content = self.content is not None and bool(self.content.strip())
        has_tool_calls = bool(self.tool_calls)
        if has_content == has_tool_calls:
            raise ValueError(
                "ModelResponse must contain exactly one of content or tool_calls"
            )


MessageRole: TypeAlias = Literal["user", "assistant", "tool"]
