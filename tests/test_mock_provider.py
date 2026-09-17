import pytest

from ai_runtime.exceptions import ProviderResponseError
from ai_runtime.models import ModelRequest, ModelResponse, UserMessage
from ai_runtime.providers.mock import MockProvider


def test_mock_provider_is_deterministic_and_records_requests() -> None:
    provider = MockProvider([ModelResponse(content="first")])
    request = ModelRequest(messages=(UserMessage("hello"),))

    response = provider.complete(request)

    assert response.content == "first"
    assert provider.requests == [request]


def test_mock_provider_reports_script_exhaustion() -> None:
    provider = MockProvider([])

    with pytest.raises(ProviderResponseError, match="no responses"):
        provider.complete(ModelRequest(messages=(UserMessage("hello"),)))
