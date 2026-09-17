"""Deterministic provider for examples and offline tests."""

from __future__ import annotations

from collections import deque
from collections.abc import Iterable

from ai_runtime.exceptions import ProviderResponseError
from ai_runtime.models import ModelRequest, ModelResponse


class MockProvider:
    """Return a predefined sequence of responses without network access."""

    name = "mock"

    def __init__(self, responses: Iterable[ModelResponse]) -> None:
        self._responses = deque(responses)
        self.requests: list[ModelRequest] = []

    def complete(self, request: ModelRequest) -> ModelResponse:
        """Record the request and return the next scripted response."""

        self.requests.append(request)
        if not self._responses:
            raise ProviderResponseError("MockProvider has no responses remaining")
        return self._responses.popleft()
