"""Storm entity for environmental hazards (PROJ-189; migrated PROJ-300).

Storms are multi-hex environmental hazards that affect ships within their area.
After PROJ-300 they project `abilities: Dict[str, Any]` (the unified shape).
The legacy `StormEffect` dataclass and `Storm.effects` field were eradicated
in PROJ-300 Phase 7.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, FrozenSet

from game.core.hex_math import HexCoord, hex_to_dict, hex_from_dict
from game.core.validation_helpers import require_keys
from game.core.exceptions import PersistenceException
from game.core.error_codes import ErrorCode


@dataclass
class Storm:
    """Multi-hex environmental hazard in a star system.

    Storms occupy multiple hexes defined by a center location and relative offsets.
    Ships within storm hexes are subject to environmental effects.

    PROJ-300 migrated `effects: StormEffect` to `abilities: Dict[str, Any]`
    matching components.json. Phase 7 removed the StormEffect class and the
    Storm.effects field entirely. Old saves with the legacy `effects` shape
    FAIL TO LOAD per PROJ-300 D19 — save files are disposable per CLAUDE.md.

    Attributes:
        name: Display name (e.g., "Ion Storm Alpha").
        storm_type: Type ID from storms.json (e.g., "ion_storm").
        description: Lore blurb shown in the storm detail panel.
        location: Center hex, local to star system.
        hex_offsets: Relative offsets from location (includes HexCoord(0,0) for center).
        abilities: PROJ-300 abilities dict matching components.json shape.
        image_variant: Index into nebulae image group (1-6).
        intensity: 0.0-1.0, controls rendering alpha.
    """
    name: str
    storm_type: str
    location: HexCoord
    hex_offsets: FrozenSet[HexCoord]
    abilities: Dict[str, Any] = field(default_factory=dict)
    description: str = ""
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

        PROJ-300: emits `abilities` (new shape) and `description`. Legacy
        `effects` field is NOT serialized — old saves are disposable.

        Returns:
            Dict suitable for JSON serialization.
        """
        return {
            'name': self.name,
            'storm_type': self.storm_type,
            'description': self.description,
            'location': hex_to_dict(self.location),
            'hex_offsets': [hex_to_dict(offset) for offset in self.hex_offsets],
            'abilities': dict(self.abilities),
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

        abilities_data = data.get('abilities', {})
        if not isinstance(abilities_data, dict):
            raise PersistenceException(
                f"Storm: 'abilities' must be a dict, got {type(abilities_data).__name__}",
                code=ErrorCode.CORRUPT_DATA.value,
                context={"source": "Storm", "field": "abilities", "value": abilities_data},
            )

        return cls(
            name=data['name'],
            storm_type=data['storm_type'],
            description=data.get('description', ''),
            location=location,
            hex_offsets=hex_offsets,
            abilities=abilities_data,
            image_variant=data.get('image_variant', 1),
            intensity=data.get('intensity', 1.0),
        )
