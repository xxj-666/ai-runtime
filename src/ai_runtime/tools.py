"""Registration and bounded execution of local function tools."""

from __future__ import annotations

import inspect
import json
import re
from collections.abc import Callable, Mapping
from copy import deepcopy
from dataclasses import dataclass
from typing import Any

from ai_runtime.exceptions import (
    DuplicateToolError,
    InvalidToolArgumentsError,
    ToolExecutionError,
    UnknownToolError,
)
from ai_runtime.models import ToolCall, ToolSpec

_TOOL_NAME_PATTERN = re.compile(r"^[A-Za-z0-9_-]{1,64}$")


@dataclass(frozen=True, slots=True)
class _RegisteredTool:
    spec: ToolSpec
    handler: Callable[..., Any]


class ToolRegistry:
    """A small explicit registry for JSON-schema-described Python callables."""

    def __init__(self) -> None:
        self._tools: dict[str, _RegisteredTool] = {}

    def register(
        self,
        *,
        name: str,
        description: str,
        parameters: Mapping[str, Any],
        handler: Callable[..., Any],
        strict: bool = True,
    ) -> ToolSpec:
        """Register a tool and return its portable specification."""

        if not _TOOL_NAME_PATTERN.fullmatch(name):
            raise ValueError(
                "Tool names must contain 1-64 letters, numbers, underscores, or hyphens"
            )
        if name in self._tools:
            raise DuplicateToolError(f"Tool {name!r} is already registered")
        if not description.strip():
            raise ValueError("Tool description must not be empty")
        if not callable(handler):
            raise TypeError("Tool handler must be callable")

        schema = deepcopy(dict(parameters))
        self._validate_schema(schema, strict=strict)
        spec = ToolSpec(
            name=name,
            description=description.strip(),
            parameters=schema,
            strict=strict,
        )
        self._tools[name] = _RegisteredTool(spec=spec, handler=handler)
        return spec

    def specs(self) -> tuple[ToolSpec, ...]:
        """Return tool specifications in registration order."""

        return tuple(tool.spec for tool in self._tools.values())

    def execute(self, call: ToolCall) -> Any:
        """Validate Python arguments, execute a tool, and require JSON output."""

        registered = self._tools.get(call.name)
        if registered is None:
            raise UnknownToolError(f"Provider requested unknown tool {call.name!r}")

        try:
            inspect.signature(registered.handler).bind(**call.arguments)
        except TypeError as exc:
            raise InvalidToolArgumentsError(
                f"Invalid arguments for tool {call.name!r}: {exc}"
            ) from exc

        try:
            result = registered.handler(**call.arguments)
        except Exception as exc:
            raise ToolExecutionError(f"Tool {call.name!r} failed: {exc}") from exc

        try:
            json.dumps(result)
        except (TypeError, ValueError) as exc:
            raise ToolExecutionError(
                f"Tool {call.name!r} returned a non-JSON-serializable value"
            ) from exc
        return result

    @staticmethod
    def _validate_schema(schema: dict[str, Any], *, strict: bool) -> None:
        if schema.get("type") != "object":
            raise ValueError("Tool parameters must be a JSON Schema object")
        properties = schema.get("properties", {})
        if not isinstance(properties, dict):
            raise ValueError("Tool schema properties must be an object")
        required = schema.get("required", [])
        if not isinstance(required, list) or not all(
            isinstance(item, str) for item in required
        ):
            raise ValueError("Tool schema required must be a list of property names")
        unknown_required = set(required) - set(properties)
        if unknown_required:
            raise ValueError(
                "Tool schema requires undefined properties: "
                + ", ".join(sorted(unknown_required))
            )
        if strict:
            if schema.get("additionalProperties") is not False:
                raise ValueError(
                    "Strict tool schemas must set additionalProperties to false"
                )
            if set(required) != set(properties):
                raise ValueError(
                    "Strict tool schemas must list every property as required"
                )
