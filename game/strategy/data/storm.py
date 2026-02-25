"""Storm entity for environmental hazards (PROJ-189).

Storms are multi-hex environmental hazards that affect ships within their area.
They apply effects like shield reduction, speed reduction, damage, and fuel drain.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, FrozenSet

from game.core.hex_math import HexCoord, hex_to_dict, hex_from_dict
from game.core.validation_helpers import require_keys
from game.core.exceptions import PersistenceException
from game.core.error_codes import ErrorCode


@dataclass
class StormEffect:
    """Environmental effects applied by a storm.

    All multipliers default to 1.0 (no effect), all rates default to 0.0.

    Attributes:
        shield_capacity_mult: Multiplier for shield capacity (0.5 = 50% shields).
        thrust_mult: Multiplier for thrust/tactical movement.
        strategic_mult: Multiplier for strategic map movement speed.
        damage_per_tick: Hull damage applied per tick while in storm.
        fuel_drain_per_tick: Fuel consumed per tick while in storm.
    """
    shield_capacity_mult: float = 1.0
    thrust_mult: float = 1.0
    strategic_mult: float = 1.0
    damage_per_tick: float = 0.0
    fuel_drain_per_tick: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Serialize StormEffect to dict."""
        return {
            'shield_capacity_mult': self.shield_capacity_mult,
            'thrust_mult': self.thrust_mult,
            'strategic_mult': self.strategic_mult,
            'damage_per_tick': self.damage_per_tick,
            'fuel_drain_per_tick': self.fuel_drain_per_tick,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StormEffect':
        """Deserialize StormEffect from dict.

        Missing keys use default values.

        Args:
            data: Dict with optional effect fields.

        Returns:
            StormEffect instance.
        """
        return cls(
            shield_capacity_mult=data.get('shield_capacity_mult', 1.0),
            thrust_mult=data.get('thrust_mult', 1.0),
            strategic_mult=data.get('strategic_mult', 1.0),
            damage_per_tick=data.get('damage_per_tick', 0.0),
            fuel_drain_per_tick=data.get('fuel_drain_per_tick', 0.0),
        )


@dataclass
class Storm:
    """Multi-hex environmental hazard in a star system.

    Storms occupy multiple hexes defined by a center location and relative offsets.
    Ships within storm hexes are subject to environmental effects.

    Attributes:
        name: Display name (e.g., "Ion Storm Alpha").
        storm_type: Type ID from storms.json (e.g., "ion_storm").
        location: Center hex, local to star system.
        hex_offsets: Relative offsets from location (includes HexCoord(0,0) for center).
        effects: Environmental effects applied to ships in the storm.
        image_variant: Index into nebulae image group (1-6).
        intensity: 0.0-1.0, controls rendering alpha.
    """
    name: str
    storm_type: str
    location: HexCoord
    hex_offsets: FrozenSet[HexCoord]
    effects: StormEffect
    image_variant: int = 1
    intensity: float = 1.0

    @property
    def occupied_hexes(self) -> FrozenSet[HexCoord]:
        """Return all hexes occupied by this storm in local system coordinates.

        Computes global positions by adding each offset to the center location.

        Returns:
            FrozenSet of HexCoord representing occupied hexes.
        """
        return frozenset(self.location + offset for offset in self.hex_offsets)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize Storm to dict.

        Returns:
            Dict suitable for JSON serialization.
        """
        return {
            'name': self.name,
            'storm_type': self.storm_type,
            'location': hex_to_dict(self.location),
            'hex_offsets': [hex_to_dict(offset) for offset in self.hex_offsets],
            'effects': self.effects.to_dict(),
            'image_variant': self.image_variant,
            'intensity': self.intensity,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Storm':
        """Deserialize Storm from dict.

        Args:
            data: Dict with storm data.

        Returns:
            Storm instance.

        Raises:
            PersistenceException: If required keys missing or location is malformed.
        """
        require_keys(data, ['name', 'storm_type', 'location', 'hex_offsets'], 'Storm')

        # Parse location
        try:
            location = hex_from_dict(data['location'])
        except (KeyError, TypeError) as e:
            raise PersistenceException(
                f"Storm: invalid location format - {type(e).__name__}: {e}",
                code=ErrorCode.CORRUPT_DATA.value,
                context={
                    "source": "Storm",
                    "field": "location",
                    "value": data.get('location'),
                    "error": str(e),
                }
            ) from e

        # Parse hex_offsets
        try:
            hex_offsets = frozenset(
                hex_from_dict(offset) for offset in data['hex_offsets']
            )
        except (KeyError, TypeError) as e:
            raise PersistenceException(
                f"Storm: invalid hex_offsets format - {type(e).__name__}: {e}",
                code=ErrorCode.CORRUPT_DATA.value,
                context={
                    "source": "Storm",
                    "field": "hex_offsets",
                    "value": data.get('hex_offsets'),
                    "error": str(e),
                }
            ) from e

        # Parse effects (optional, defaults to neutral effects)
        effects_data = data.get('effects', {})
        effects = StormEffect.from_dict(effects_data)

        return cls(
            name=data['name'],
            storm_type=data['storm_type'],
            location=location,
            hex_offsets=hex_offsets,
            effects=effects,
            image_variant=data.get('image_variant', 1),
            intensity=data.get('intensity', 1.0),
        )
