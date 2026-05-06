"""``PlanetHabitabilityService`` — injectable population-weighted habitability calculator.

PROJ-372 Phase 2. Implements ``IHabitabilityCalculator`` from
``game/strategy/data/galaxy_protocols.py``. The default implementation
delegates to ``planet_habitability_multiplier`` from
``game/strategy/formulas/colony_output.py`` and caches per-turn on the
planet's transient fields (PROJ-285 invariant).

Modders inject custom calculators via::

    from game.context import set_default_planet_habitability_service
    set_default_planet_habitability_service(MyCustomCalculator())

Tests inject stubs the same way (see
``tests/unit/strategy/services/test_planet_habitability_service.py``).
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from game.strategy.data.planet import Planet


__all__ = ["PlanetHabitabilityService"]


class PlanetHabitabilityService:
    """Default ``IHabitabilityCalculator`` implementation.

    Reads / writes the transient cache fields
    ``Planet._cached_habitability_multiplier`` and
    ``Planet._cached_multiplier_turn`` (PROJ-285 invariant — cache lives
    on the planet, not on the service, so multiple service instances
    stay coherent).
    """

    def get_cached(
        self, planet: "Planet", race_registry: Any, turn: int
    ) -> float:
        """Return the population-weighted habitability multiplier in [0, 1].

        Cache miss policy: re-computes when ``planet._cached_multiplier_turn``
        differs from ``turn``. PROJ-285: populations only change at turn
        boundaries, so one compute per turn is enough — all 100 harvest /
        production ticks within the same turn reuse the cached value.
        """
        if planet._cached_multiplier_turn != turn:
            planet._cached_habitability_multiplier = self._compute(
                planet, race_registry,
            )
            planet._cached_multiplier_turn = turn
        return planet._cached_habitability_multiplier

    def _compute(self, planet: "Planet", race_registry: Any) -> float:
        """Pure recomputation — no cache interaction.

        Late-imported to dodge the historic
        ``planet.py <- colony_output.py <- habitability.py`` cycle.
        Subclasses may override to inject alternate formulas.
        """
        from game.strategy.formulas.colony_output import (
            planet_habitability_multiplier,
        )
        return planet_habitability_multiplier(planet, race_registry)
