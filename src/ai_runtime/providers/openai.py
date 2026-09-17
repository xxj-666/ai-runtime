"""Optional OpenAI Responses API adapter."""

from __future__ import annotations

import json
from typing import Any

from ai_runtime.exceptions import (
    ProviderConfigurationError,
    ProviderError,
    ProviderResponseError,
)
from ai_runtime.models import (
    AssistantMessage,
    ModelRequest,
    ModelResponse,
    ToolCall,
    ToolCallMessage,
    ToolResultMessage,
    UserMessage,
)


class OpenAIProvider:
    """Adapt the OpenAI Responses API to the portable provider interface."""

    name = "openai"

    def __init__(
        self,
        *,
        model: str,
        api_key: str | None = None,
        client: Any | None = None,
        store: bool = False,
    ) -> None:
        if not model.strip():
            raise ProviderConfigurationError("OpenAI model must not be empty")
        self.model = model
        self.store = store
        self._client = client or self._build_client(api_key)

    @staticmethod
    def _build_client(api_key: str | None) -> Any:
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise ProviderConfigurationError(
                "OpenAI support is optional; install it with `uv sync --extra openai`"
            ) from exc

        try:
            return OpenAI(api_key=api_key) if api_key else OpenAI()
        except Exception as exc:
            raise ProviderConfigurationError(
                "Could not configure the OpenAI client. Set OPENAI_API_KEY or pass "
                "api_key explicitly."
            ) from exc

    def complete(self, request: ModelRequest) -> ModelResponse:
        """Create one OpenAI response and convert it to portable output."""

        payload: dict[str, Any] = {
            "model": self.model,
            "input": [self._message_to_input(message) for message in request.messages],
            "store": self.store,
        }
        if request.tools:
            payload["tools"] = [
                {
                    "type": "function",
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters,
                    "strict": tool.strict,
                }
                for tool in request.tools
            ]

        try:
            response = self._client.responses.create(**payload)
        except Exception as exc:
            raise ProviderError(f"OpenAI Responses API request failed: {exc}") from exc

        tool_calls: list[ToolCall] = []
        for item in response.output:
            if item.type != "function_call":
                continue
            try:
                arguments = json.loads(item.arguments)
            except (TypeError, json.JSONDecodeError) as exc:
                raise ProviderResponseError(
                    f"OpenAI returned invalid JSON arguments for tool {item.name!r}"
                ) from exc
            if not isinstance(arguments, dict):
                raise ProviderResponseError(
                    f"OpenAI returned non-object arguments for tool {item.name!r}"
                )
            tool_calls.append(
                ToolCall(
                    call_id=item.call_id,
                    name=item.name,
                    arguments=arguments,
                )
            )

        if tool_calls:
            return ModelResponse(tool_calls=tuple(tool_calls))

        output_text = getattr(response, "output_text", None)
        if not isinstance(output_text, str) or not output_text.strip():
            raise ProviderResponseError(
                "OpenAI returned neither text nor function calls"
            )
        return ModelResponse(content=output_text)

    @staticmethod
    def _message_to_input(message: Any) -> dict[str, Any]:
        if isinstance(message, UserMessage):
            return {"role": "user", "content": message.content}
        if isinstance(message, AssistantMessage):
            return {"role": "assistant", "content": message.content}
        if isinstance(message, ToolCallMessage):
            return {
                "type": "function_call",
                "call_id": message.call_id,
                "name": message.name,
                "arguments": json.dumps(message.arguments),
            }
        if isinstance(message, ToolResultMessage):
            return {
                "type": "function_call_output",
                "call_id": message.call_id,
                "output": json.dumps(message.output),
            }
        raise ProviderResponseError(
            f"Unsupported runtime message type: {type(message).__name__}"
        )
