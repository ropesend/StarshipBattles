"""Shared protocol for the per-screen test UI builders (PROJ-321..328 audit S4.5).

Each ``tests/fixtures/<screen>_ui_builder.py`` module exports a
``Null{Foo}UiBuilder`` (no-op) and ``Mock{Foo}UiBuilder`` (populates widget
slots). Both implement a single ``build(screen) -> None`` method matching
the corresponding production builder protocol.

This file pins that contract so a future seventh builder gets a type-check
hit if it forgets the ``build`` signature, and so the production UI builder
classes can be type-checked against the same protocol.

The protocol is intentionally `Generic[ScreenT]` so each per-screen builder
narrows the screen type for editor tooling (without forcing a runtime
ABC inheritance — `Protocol` is structural).
"""

from __future__ import annotations

from typing import Protocol, TypeVar, runtime_checkable

ScreenT = TypeVar("ScreenT", contravariant=True)


@runtime_checkable
class UiBuilder(Protocol[ScreenT]):
    """Structural protocol every per-screen UI builder satisfies.

    A class implements this protocol if it has a ``build(screen) -> None``
    method. The Null* / Mock* / production builders all match.

    Runtime-checkable so tests can assert ``isinstance(builder, UiBuilder)``
    when collecting builders dynamically.
    """

    def build(self, screen: ScreenT) -> None: ...


__all__ = ["UiBuilder"]
