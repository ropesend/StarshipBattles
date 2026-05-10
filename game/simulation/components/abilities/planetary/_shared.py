"""Shared constants for the planetary-abilities sub-modules.

PROJ-382 Phase 5: extracted from the pre-decomposition ``planetary.py``.
``_STORM_SCOPES`` is the canonical list of scopes that storm-style
abilities (thrust modifier, strategic-speed modifier, environmental
damage, fuel drain) accept; consolidated here so the four sub-modules
referencing it stay in sync.
"""
from ..base import AbilityScope


_STORM_SCOPES = [
    AbilityScope.SELF, AbilityScope.SECTOR, AbilityScope.ALLIED_SECTOR,
    AbilityScope.PLAYER_SECTOR, AbilityScope.ENEMY_SECTOR,
    AbilityScope.SYSTEM, AbilityScope.ALLIED_SYSTEM,
    AbilityScope.PLAYER_SYSTEM, AbilityScope.ENEMY_SYSTEM,
]
