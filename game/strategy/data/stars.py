"""``Star`` data class.

``Spectrum`` lives in ``game/strategy/data/spectrum.py``; ``StarGenerator``
lives in ``game/strategy/generation/star_generator.py``; solar/Kelvin
constants and spectral math live in ``game/core/spectrum_math.py``. Import
those symbols directly from their canonical modules — this module no
longer re-exports them.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, FrozenSet

from game.core.hex_math import HexCoord, hex_circle_filled
from game.core.validation_helpers import (
    require_keys,
    safe_from_dict,
    validate_enum,
    validate_non_negative,
    validate_positive,
)

# Internal use only: ``Star.from_dict`` calls ``Spectrum.from_dict`` and the
# ``Star.spectrum`` field is typed as ``Spectrum``. The canonical public
# module for Spectrum is ``game.strategy.data.spectrum``; this private alias
# is not part of the ``stars`` module's public surface.
from game.strategy.data.spectrum import Spectrum as _Spectrum


__all__ = [
    "StarType",
    "Star",
]


class StarType(Enum):
    MAIN_SEQUENCE = auto()
    RED_GIANT = auto()
    BLUE_GIANT = auto()
    WHITE_DWARF = auto()
    RED_DWARF = auto()
    NEUTRON_STAR = auto()
    BLACK_HOLE = auto()
    BROWN_DWARF = auto()


@dataclass
class Star:
    name: str
    mass: float  # Solar Masses
    radius_hexes: int  # Radius in hexes (1 = center only, 2 = center + ring 1, etc.)
    temperature: float  # Kelvin
    luminosity: float  # Solar Luminosity
    spectrum: _Spectrum
    star_type: StarType
    color: tuple  # (R, G, B)
    age: float  # Years

    # Location relative to system center (0,0,0)
    location: HexCoord = field(default_factory=lambda: HexCoord(0, 0))

    # Visual representation (assigned during generation, persisted in saves)
    image_id: str = ""  # Filename from star assets (e.g., "StarBlueVariant_3.png")

    # PROJ-302: star intrinsic abilities (system-scope by default — a pulsar
    # affects every hex of the system, not just the star's hex). Populated at
    # galaxy generation via roll_intrinsic_abilities against data/star_types.json.
    intrinsic_abilities: Dict[str, Any] = field(default_factory=dict)

    @property
    def occupied_hexes(self) -> FrozenSet[HexCoord]:
        """Return all hexes occupied by this star (PROJ-139 IZoneOccupant)."""
        return hex_circle_filled(self.location, max(0, self.radius_hexes - 1))

    def to_dict(self) -> Dict[str, Any]:
        """Serialize Star to dict."""
        from game.core.hex_math import hex_to_dict
        return {
            "name": self.name,
            "mass": self.mass,
            "radius_hexes": self.radius_hexes,
            "temperature": self.temperature,
            "luminosity": self.luminosity,
            "spectrum": self.spectrum.to_dict(),
            "star_type": self.star_type.name,  # Enum to string
            "color": list(self.color),  # Tuple to list for JSON
            "age": self.age,
            "location": hex_to_dict(self.location),
            "image_id": self.image_id,
            # PROJ-302: star intrinsic abilities (rolled at gen).
            "intrinsic_abilities": dict(self.intrinsic_abilities),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Star":
        """Deserialize Star from dict.

        Raises:
            PersistenceException: If required keys missing or values invalid.
        """
        from game.core.error_codes import ErrorCode
        from game.core.exceptions import PersistenceException
        from game.core.hex_math import hex_from_dict

        require_keys(
            data,
            [
                "name", "mass", "radius_hexes", "temperature", "luminosity",
                "spectrum", "star_type", "color", "age", "location",
            ],
            "Star",
        )

        star_type = validate_enum(data["star_type"], StarType, "star_type", "Star")

        validate_positive(data["mass"], "mass", "Star")
        # Temperature can be 0 for BLACK_HOLE stars (event horizon).
        validate_non_negative(data["temperature"], "temperature", "Star")
        validate_positive(data["luminosity"], "luminosity", "Star")

        spectrum = safe_from_dict(_Spectrum.from_dict, data["spectrum"], "Star.spectrum")

        try:
            location = hex_from_dict(data["location"])
        except (KeyError, TypeError) as e:
            raise PersistenceException(
                f"Star: invalid location data - {type(e).__name__}: {e}",
                code=ErrorCode.CORRUPT_DATA.value,
                context={
                    "source": "Star",
                    "field": "location",
                    "error_type": type(e).__name__,
                    "error": str(e),
                },
            ) from e

        return cls(
            name=data["name"],
            mass=data["mass"],
            radius_hexes=data["radius_hexes"],
            temperature=data["temperature"],
            luminosity=data["luminosity"],
            spectrum=spectrum,
            star_type=star_type,
            color=tuple(data["color"]),
            age=data["age"],
            location=location,
            image_id=data.get("image_id", ""),
            # PROJ-302: backward compat — old saves load with empty dict.
            intrinsic_abilities=dict(data.get("intrinsic_abilities") or {}),
        )


# ``StarGenerator`` lives in ``game.strategy.generation.star_generator``;
# this module-level ``__getattr__`` preserves the legacy import path
# ``from game.strategy.data.stars import StarGenerator`` for current
# non-test consumers (galaxy_test UI and the diagnose_blueprints tool).
# Late import avoids a circular dep — ``star_generator`` itself imports
# ``Star`` / ``StarType`` from this module.
def __getattr__(name: str) -> Any:
    if name == "StarGenerator":
        from game.strategy.generation.star_generator import StarGenerator
        return StarGenerator
    raise AttributeError(f"module 'game.strategy.data.stars' has no attribute {name!r}")
