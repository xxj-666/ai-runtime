"""Model provider interface."""

from typing import Protocol, runtime_checkable

from ai_runtime.models import ModelRequest, ModelResponse


@runtime_checkable
class ModelProvider(Protocol):
    """A synchronous, provider-independent model interface."""

    name: str

    def complete(self, request: ModelRequest) -> ModelResponse:
        """Produce final text or one or more tool calls."""

        ...
