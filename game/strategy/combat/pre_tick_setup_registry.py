"""PROJ-426 — pre-tick setup callback registry.

`PreTickBattleSetupRegistry` owns the ordered list of
`(engine, spec) -> None` callbacks that `run_battle` invokes once via its
single `pre_tick_loop_callback` parameter, immediately after the engine
is constructed and before the first tick. Each callback can install
state on the engine (e.g., mine resolvers, reboard trackers) so the
post-battle hook has the references it needs.

Phase 1 introduces this registry as the typed seam for
`StrategyBattleAssembly`. Phase 3 populates it with the mine and reboard
setup callbacks (moved out of `spec_compiler.py`). Phase 4 makes the
adapter consume `composed_callback()` instead of composing callbacks
manually.

Composition order is registration order — deterministic and stable.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, List, Optional, Tuple

if TYPE_CHECKING:
    from game.simulation.battle_spec import BattleSpec


__all__ = ["PreTickBattleSetupRegistry"]


# Public callback signature. The current production callbacks accept only
# `engine`; the registry passes `spec` as a second positional arg so
# future setups can read the spec without an extra closure. Existing
# `engine`-only setups are wrapped at registration time.
PreTickSetupCallback = Callable[[Any, "BattleSpec"], None]


class PreTickBattleSetupRegistry:
    """Named registry composing pre-tick setup callbacks deterministically.

    Callbacks register with a string name so duplicate registration is
    rejected explicitly (a 5th unrelated setup should not silently
    overwrite an existing one). Composition order is registration order.
    `composed_callback()` returns `None` for an empty registry so the
    adapter can pass `None` straight through to `run_battle`.
    """

    def __init__(self) -> None:
        # Insertion-ordered list of (name, callback) tuples. A plain dict
        # would work for Python 3.7+, but the explicit list makes the
        # ordering contract visible at the call site.
        self._entries: List[Tuple[str, PreTickSetupCallback]] = []

    def register(self, name: str, setup: Callable[..., None]) -> None:
        """Add a setup callback under `name`.

        `setup` may be a `(engine, spec) -> None` callable or the legacy
        `(engine) -> None` shape; the latter is adapted so the unified
        signature reaches `composed_callback`. Duplicate names raise
        `ValueError`.
        """
        if any(existing == name for existing, _ in self._entries):
            raise ValueError(
                f"PreTickBattleSetupRegistry: duplicate setup name {name!r}"
            )
        # Detect legacy `(engine) -> None` callables by parameter count.
        # Accept both signatures so Phase 3's setup builders can register
        # without rewriting their internals.
        try:
            import inspect

            sig = inspect.signature(setup)
            param_count = len(
                [
                    p
                    for p in sig.parameters.values()
                    if p.kind
                    in (
                        inspect.Parameter.POSITIONAL_ONLY,
                        inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    )
                ]
            )
        except (TypeError, ValueError):  # Intentional broad-ish catch: opaque callables (builtins, C extensions) — fall back to two-arg invocation.
            param_count = 2

        if param_count == 1:
            wrapped: PreTickSetupCallback = lambda engine, _spec, _cb=setup: _cb(  # noqa: E731
                engine
            )
        else:
            wrapped = setup  # type: ignore[assignment]

        self._entries.append((name, wrapped))

    def composed_callback(
        self,
    ) -> Optional[Callable[[Any, "BattleSpec"], None]]:
        """Return a single callback that invokes all registered setups in order.

        Returns `None` when the registry is empty so the adapter can pass
        a falsy value straight to `run_battle(..., pre_tick_loop_callback=None)`.
        """
        if not self._entries:
            return None

        entries = list(self._entries)

        def _composed(engine: Any, spec: "BattleSpec | None" = None) -> None:
            for _name, cb in entries:
                cb(engine, spec)

        return _composed

    def __len__(self) -> int:
        return len(self._entries)

    def names(self) -> Tuple[str, ...]:
        """Return registered names in registration order (for tests / debug)."""
        return tuple(name for name, _ in self._entries)
