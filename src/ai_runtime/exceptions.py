"""Exception hierarchy for ai-runtime."""


class AiRuntimeError(Exception):
    """Base exception for runtime failures."""


class ProviderError(AiRuntimeError):
    """A model provider failed to produce a usable response."""


class ProviderConfigurationError(ProviderError):
    """A provider cannot start because configuration is missing or invalid."""


class ProviderResponseError(ProviderError):
    """A provider returned a response the runtime cannot interpret."""


class ToolError(AiRuntimeError):
    """Base exception for tool registry and execution failures."""


class DuplicateToolError(ToolError):
    """A tool was registered more than once."""


class UnknownToolError(ToolError):
    """A model requested a tool that is not registered."""


class InvalidToolArgumentsError(ToolError):
    """A model supplied arguments that do not match the Python handler."""


class ToolExecutionError(ToolError):
    """A registered tool raised or returned a non-JSON value."""


class MaxStepsExceededError(AiRuntimeError):
    """The runtime did not reach a final answer within its step limit."""
