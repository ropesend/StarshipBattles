"""PROJ-426 — pre-tick battle setup builders.

Each module here exports a `build_*_setup(...)` function that returns a
`(engine) -> None` (legacy) or `(engine, spec) -> None` callback. The
`PreTickBattleSetupRegistry` composes them in deterministic registration
order via a single `pre_tick_loop_callback` for `run_battle`.

Phase 3 lifts the mine and reboard setup builders out of
`spec_compiler.py`; new pre-tick setups (e.g., environmental hazard
initialization) register here without touching the compiler.
"""
from game.strategy.combat.pre_tick_setup.mine_setup import build_mine_resolver_setup
from game.strategy.combat.pre_tick_setup.reboard_setup import (
    build_fighter_reboard_setup,
)

__all__ = [
    "build_mine_resolver_setup",
    "build_fighter_reboard_setup",
]
