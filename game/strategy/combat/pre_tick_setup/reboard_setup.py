"""PROJ-426 Phase 3 — fighter reboard pre-tick setup builder.

Lifted from `spec_compiler.py::build_fighter_reboard_setup` (PROJ-FMS-C
Phase 3). Behavior unchanged.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, List, Optional, Sequence

if TYPE_CHECKING:
    from game.strategy.data.fleet import Fleet


__all__ = ["build_fighter_reboard_setup"]


def build_fighter_reboard_setup(
    participating_fleets: Sequence["Fleet"],
    *,
    engine_ref: Optional[List[Any]] = None,
) -> Optional[Callable[[Any], None]]:
    """Build a `pre_tick_loop_callback` that installs a reboard tracker.

    Returns a closure that installs a `ReboardTracker` on the engine and
    (when `engine_ref` is provided) appends the engine to that mutable
    one-slot list so the post-battle hook can call `apply_reboard`.

    Returns `None` when there are no combat fleets.
    """
    if not participating_fleets:
        return None

    from game.simulation.systems.fighter_reboard import ReboardTracker

    captured_engine_ref = engine_ref

    def _setup(engine: Any) -> None:
        tracker = ReboardTracker(battle_id=id(engine))
        try:
            setattr(engine, "reboard_tracker", tracker)
        except (AttributeError, TypeError):
            pass
        if captured_engine_ref is not None:
            captured_engine_ref.append(engine)

    return _setup
