"""Race-config resolution shared between strategy engines.

Extracted in PROJ-319 (DUP-X-01) to remove the duplicated `_get_race_config`
method that previously lived in both `HappinessEngine` and `PopulationEngine`.
A drift between the two copies would silently produce different growth and
happiness values for multi-species colonies.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from game.core.protocols import IRaceRegistry
    from game.strategy.data.empire import Empire
    from game.strategy.data.race_config import RaceConfig


def resolve_race_config(
    race_id: str,
    empire: "Empire",
    race_registry: Optional["IRaceRegistry"],
) -> Optional["RaceConfig"]:
    """Resolve the `RaceConfig` for a given species on this empire.

    PROJ-291 C3 resolution order:
      1. If a race registry is wired, consult it first. When it returns a
         `RaceConfig`, use that — this is the multi-species path.
      2. Otherwise (or when the registry doesn't know the race_id), fall
         back to `empire.race_config` ONLY when the race_id matches the
         empire's primary race. Return None for any mismatch so non-primary
         species are gracefully skipped instead of silently computed
         against the wrong base value (the pre-PROJ-291 bug).
    """
    if race_registry is not None:
        race_config = race_registry.get_race(race_id)
        if race_config is not None:
            return race_config
    race_config = empire.race_config
    if race_config is None:
        return None
    if race_config.race_id == race_id:
        return race_config
    return None  # PROJ-291 C3: stop returning the wrong race silently
