"""`ReturnDestination` — navigation target after a battle ends.

Moved from `game/simulation/battle_config.py` by PROJ-270 Phase 5.2.
Lives in `game/core/` because both simulation (`BattleConfig`) and UI
(navigation handlers) consume it; `game/core` is the dependency-free
layer that all others can import from.

Pre-PROJ-270 the enum lived in the simulation layer, which meant the
simulation layer named UI scene contexts. `game/core/` is the correct
home — layer-neutral and dependency-free.
"""
from enum import Enum


class ReturnDestination(Enum):
    """Where to navigate after the battle ends."""

    BATTLE_SETUP = "battle_setup"
    TEST_LAB = "test_lab"
    STRATEGY = "strategy"


__all__ = ["ReturnDestination"]
