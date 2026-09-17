"""The provider-neutral agent runtime loop."""

from __future__ import annotations

from dataclasses import dataclass

from ai_runtime.exceptions import MaxStepsExceededError, ProviderError
from ai_runtime.models import (
    AssistantMessage,
    ModelRequest,
    ToolCallMessage,
    ToolResultMessage,
    UserMessage,
)
from ai_runtime.providers.base import ModelProvider
from ai_runtime.state import RuntimeState
from ai_runtime.tools import ToolRegistry


@dataclass(frozen=True, slots=True)
class RuntimeResult:
    """A final answer together with the state that produced it."""

    output: str
    state: RuntimeState


class AgentRuntime:
    """Run a bounded synchronous model/tool loop."""

    def __init__(
        self,
        provider: ModelProvider,
        *,
        tools: ToolRegistry | None = None,
        max_steps: int = 8,
    ) -> None:
        if max_steps < 1:
            raise ValueError("max_steps must be at least 1")
        self.provider = provider
        self.tools = tools or ToolRegistry()
        self.max_steps = max_steps

    def run(
        self, user_input: str, *, state: RuntimeState | None = None
    ) -> RuntimeResult:
        """Run until the provider returns final text or the step limit is reached."""

        if not user_input.strip():
            raise ValueError("user_input must not be empty")

        active_state = state or RuntimeState()
        active_state.append(UserMessage(content=user_input.strip()))

        for _ in range(self.max_steps):
            request = ModelRequest(
                messages=active_state.snapshot(),
                tools=self.tools.specs(),
            )
            active_state.provider_calls += 1
            try:
                response = self.provider.complete(request)
            except ProviderError:
                raise
            except Exception as exc:
                raise ProviderError(
                    f"Provider {self.provider.name!r} failed: {exc}"
                ) from exc

            if response.tool_calls:
                for call in response.tool_calls:
                    active_state.append(
                        ToolCallMessage(
                            call_id=call.call_id,
                            name=call.name,
                            arguments=dict(call.arguments),
                        )
                    )
                    active_state.tool_calls += 1
                    output = self.tools.execute(call)
                    active_state.append(
                        ToolResultMessage(
                            call_id=call.call_id,
                            name=call.name,
                            output=output,
                        )
                    )
                continue

            assert response.content is not None
            active_state.append(AssistantMessage(content=response.content))
            return RuntimeResult(output=response.content, state=active_state)

        raise MaxStepsExceededError(
            f"Runtime exceeded its {self.max_steps}-step limit without a final answer"
        )
