# Concepts

## Provider independence

Applications depend on the `ModelProvider` protocol, not a vendor SDK. Each
adapter translates portable messages, tool definitions, and responses at the
boundary. Provider independence does not mean every provider behaves
identically; it means provider-specific behavior has an explicit location.

## Portable runtime state

The runtime records user messages, final assistant messages, function calls,
and function results using its own small data model. This state can be passed
back to a provider without exposing provider SDK objects to the application.

The current state is in memory only. Durable storage and a stable serialization
format are planned.

## Explicit tool boundaries

A tool consists of:

- a stable name;
- a human-readable description;
- a JSON Schema for model-visible arguments;
- a local Python handler.

The schema is sent to the provider, while execution remains under application
control. Registration does not make an unsafe handler safe: sandboxing,
authorization, confirmation, and side-effect controls remain application
responsibilities in this alpha.

## Deterministic development

`MockProvider` returns scripted responses. It makes the runtime loop, state
transitions, tool behavior, examples, and CI reproducible without credentials
or billable network requests.

## Bounded execution

Every run has a maximum number of provider steps. Reaching the limit raises an
explicit error instead of allowing an unbounded tool loop.
