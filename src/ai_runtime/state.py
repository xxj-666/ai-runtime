"""In-memory runtime state."""

from __future__ import annotations

from dataclasses import dataclass, field
from uuid import uuid4

from ai_runtime.models import RuntimeMessage


@dataclass(slots=True)
class RuntimeState:
    """Portable state for one runtime conversation.

    State is intentionally in memory in the alpha. Persistence is planned but is
    not implied by this type.
    """

    run_id: str = field(default_factory=lambda: str(uuid4()))
    messages: list[RuntimeMessage] = field(default_factory=list)
    provider_calls: int = 0
    tool_calls: int = 0

    def append(self, message: RuntimeMessage) -> None:
        """Append a provider-neutral message to the conversation."""

        self.messages.append(message)

    def snapshot(self) -> tuple[RuntimeMessage, ...]:
        """Return an immutable view suitable for a provider request."""

        return tuple(self.messages)
