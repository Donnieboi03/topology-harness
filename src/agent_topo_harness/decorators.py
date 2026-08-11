"""Fail-closed topology gates for hosts that wrap spawn/write callables."""
from __future__ import annotations

import functools
from typing import Any, Callable, TypeVar, Union

from .sticky import StickyRegistry

F = TypeVar("F", bound=Callable[..., Any])
RegistryLike = Union[StickyRegistry, Callable[[], StickyRegistry]]


class TopicNotOpenError(PermissionError):
    """Topic has no sticky Topic Orchestrator handle in the registry."""


def _resolve_registry(registry: RegistryLike) -> StickyRegistry:
    return registry() if callable(registry) else registry


def _extract_topic(
    topic_arg: str | int,
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
) -> str | None:
    if isinstance(topic_arg, str):
        value = kwargs.get(topic_arg)
        if value is None and topic_arg == "topic" and args:
            # Common positional: fn(topic, ...)
            value = args[0] if not isinstance(args[0], (StickyRegistry, dict)) else None
        return str(value).strip() if value is not None and str(value).strip() else None
    if isinstance(topic_arg, int) and len(args) > topic_arg:
        value = args[topic_arg]
        return str(value).strip() if value is not None and str(value).strip() else None
    return None


def assert_topic_open(registry: RegistryLike, topic: str) -> None:
    """Fail closed unless ``topic`` has a sticky TO handle."""
    t = (topic or "").strip()
    if not t:
        raise ValueError("topic is required")
    reg = _resolve_registry(registry)
    if reg.get_orchestrator(t) is None:
        raise TopicNotOpenError(
            f"topic {t!r} is not open; call open_topic / "
            f"get_or_create_orchestrator first"
        )


def topo_gate(
    registry: RegistryLike,
    *,
    topic_arg: str | int = "topic",
) -> Callable[[F], F]:
    """Require an open sticky TO for ``topic`` before calling ``func``.

    Hosts pass the live registry (or a zero-arg provider)::

        @topo_gate(reg)
        def spawn_tt(topic: str, lane: str) -> None: ...

        @topo_gate(lambda: ctx.registry, topic_arg="topic")
        def resume(...): ...
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            topic = _extract_topic(topic_arg, args, kwargs)
            if not topic:
                raise ValueError(f"topo_gate could not find topic in {topic_arg!r}")
            assert_topic_open(registry, topic)
            return func(*args, **kwargs)

        return wrapper  # type: ignore[return-value]

    return decorator
