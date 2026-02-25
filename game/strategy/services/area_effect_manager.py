"""AreaEffectManager service for aggregating environmental effects (PROJ-189).

This service queries zones at a hex location and aggregates environmental
effects from all storms at that location.
"""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from game.core.hex_math import HexCoord
    from game.strategy.data.galaxy import Galaxy


@dataclass
class EnvironmentalEffects:
    """Aggregated environmental effects at a hex location.

    All multipliers default to 1.0 (no effect), all rates default to 0.0.
    When multiple storms overlap, multiplicative effects stack multiplicatively
    and additive effects sum.

    Attributes:
        shield_capacity_mult: Multiplier for shield capacity (0.5 = 50% shields).
        thrust_mult: Multiplier for thrust/tactical movement.
        strategic_mult: Multiplier for strategic map movement speed.
        damage_per_tick: Hull damage applied per tick while in storm.
        fuel_drain_per_tick: Fuel consumed per tick while in storm.
        in_storm: True if any storm is present at this location.
        storm_names: List of storm names affecting this location.
    """

    shield_capacity_mult: float = 1.0
    thrust_mult: float = 1.0
    strategic_mult: float = 1.0
    damage_per_tick: float = 0.0
    fuel_drain_per_tick: float = 0.0
    in_storm: bool = False
    storm_names: List[str] = field(default_factory=list)


class AreaEffectManager:
    """Service for aggregating environmental effects at hex locations.

    Queries the galaxy's zone index and aggregates effects from all storms
    at a given hex. Non-storm zones (stars, planets, Dyson Spheres) are
    filtered out.
    """

    def get_effects_at_global_hex(
        self, galaxy: 'Galaxy', global_hex: 'HexCoord'
    ) -> EnvironmentalEffects:
        """Get aggregated environmental effects at a global hex location.

        Queries the galaxy's zone index for all zones at the hex, filters
        to storms only, and aggregates their effects:
        - Multiplicative effects (shield_capacity_mult, thrust_mult, strategic_mult)
          stack multiplicatively
        - Additive effects (damage_per_tick, fuel_drain_per_tick) sum

        Args:
            galaxy: Galaxy instance with zone spatial index.
            global_hex: Global hex coordinate to query.

        Returns:
            EnvironmentalEffects with aggregated storm effects, or neutral
            effects if no storms present.
        """
        # Import Storm here to avoid circular imports
        from game.strategy.data.storm import Storm

        # Query all zones at this hex using O(1) spatial index
        zones = galaxy.get_zones_at_global_hex(global_hex)

        # Filter to storms only
        storms = [zone for zone in zones if isinstance(zone, Storm)]

        if not storms:
            return EnvironmentalEffects()

        # Aggregate effects from all storms
        result = EnvironmentalEffects(
            in_storm=True,
            storm_names=[],
        )

        for storm in storms:
            # Multiplicative effects stack multiplicatively
            result.shield_capacity_mult *= storm.effects.shield_capacity_mult
            result.thrust_mult *= storm.effects.thrust_mult
            result.strategic_mult *= storm.effects.strategic_mult

            # Additive effects sum
            result.damage_per_tick += storm.effects.damage_per_tick
            result.fuel_drain_per_tick += storm.effects.fuel_drain_per_tick

            # Collect storm names
            result.storm_names.append(storm.name)

        return result
