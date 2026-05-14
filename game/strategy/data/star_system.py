"""``WarpPoint`` and ``StarSystem`` — system-level data classes.

PROJ-372 Phase 3: extracted from ``galaxy.py`` so the Galaxy facade
can fit under the 350 LOC ceiling. Save format unchanged. This is the
canonical module for both classes — import directly from here.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from game.core.error_codes import ErrorCode
from game.core.exceptions import PersistenceException
from game.core.hex_math import hex_from_dict, hex_to_dict
from game.core.validation_helpers import require_keys

__all__ = ["WarpPoint", "StarSystem"]


class WarpPoint:
    def __init__(self, destination_id, location, warp_type='stable', intrinsic_abilities=None):
        self.destination_id = destination_id
        self.location = location  # HexCoord (Local to system)
        # PROJ-303: warp point type (stable, unstable, dimensional_rift, etc.)
        # — drives intrinsic abilities. Defaults to 'stable' (no effects).
        self.warp_type = warp_type
        self.intrinsic_abilities = dict(intrinsic_abilities) if intrinsic_abilities else {}

    def to_dict(self) -> Dict[str, Any]:
        """Serialize WarpPoint to dict."""
        return {
            'destination_id': self.destination_id,
            'location': hex_to_dict(self.location),
            'warp_type': self.warp_type,
            'intrinsic_abilities': dict(self.intrinsic_abilities),
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'WarpPoint':
        """Deserialize WarpPoint from dict.

        Raises:
            PersistenceException: required keys missing or location malformed.
        """
        require_keys(data, ['destination_id', 'location'], 'WarpPoint')

        try:
            location = hex_from_dict(data['location'])
        except (KeyError, TypeError) as e:
            raise PersistenceException(
                f"WarpPoint: invalid location format - {type(e).__name__}: {e}",
                code=ErrorCode.CORRUPT_DATA.value,
                context={
                    "source": "WarpPoint",
                    "field": "location",
                    "value": data.get('location'),
                    "error": str(e),
                },
            ) from e

        return cls(
            destination_id=data['destination_id'],
            location=location,
            warp_type=data.get('warp_type', 'stable'),
            intrinsic_abilities=data.get('intrinsic_abilities') or {},
        )


class StarSystem:
    def __init__(self, name, global_location, stars=None, region_id=None,
                 archetype=None, intrinsic_abilities=None):
        self.name = name
        self.global_location = global_location  # HexCoord
        self.stars = stars if stars else []
        self.warp_points = []
        self.planets = []  # List[Planet]
        self.storms = []  # List[Storm] (PROJ-189)
        self.region_id = region_id
        # PROJ-304: system archetype + intrinsic_abilities (most are None).
        self.archetype: Optional[str] = archetype
        self.intrinsic_abilities: Dict[str, Any] = (
            dict(intrinsic_abilities) if intrinsic_abilities else {}
        )

    @property
    def primary_star(self):
        return self.stars[0] if self.stars else None

    def add_warp_point(self, destination_id, location) -> None:
        self.warp_points.append(WarpPoint(destination_id, location))

    def __repr__(self):
        star_count = len(self.stars)
        p_name = self.primary_star.name if self.primary_star else "Empty"
        return (
            f"System('{self.name}', Loc:{self.global_location}, "
            f"Stars:{star_count}, Primary:{p_name})"
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serialize StarSystem to dict."""
        result = {
            'name': self.name,
            'global_location': hex_to_dict(self.global_location),
            'stars': [star.to_dict() for star in self.stars],
            'warp_points': [wp.to_dict() for wp in self.warp_points],
            'planets': [planet.to_dict() for planet in self.planets],
            'storms': [s.to_dict() for s in self.storms],
        }
        if self.region_id is not None:
            result['region_id'] = self.region_id
        if self.archetype is not None:
            result['archetype'] = self.archetype
        if self.intrinsic_abilities:
            result['intrinsic_abilities'] = dict(self.intrinsic_abilities)
        return result

    @classmethod
    def from_dict(cls, data: dict) -> 'StarSystem':
        """Deserialize StarSystem from dict. Strict (PROJ-251) on children."""
        from game.core.json_utils import deserialize_list
        from game.strategy.data.planet import Planet
        from game.strategy.data.stars import Star
        from game.strategy.data.storm import Storm

        require_keys(data, ['name', 'global_location'], 'StarSystem')
        parent_name = f"StarSystem '{data['name']}'"

        stars = deserialize_list(
            data.get('stars', []), Star.from_dict, 'star', parent_name, strict=True,
        )

        system = cls(
            name=data['name'],
            global_location=hex_from_dict(data['global_location']),
            stars=stars,
            region_id=data.get('region_id'),
            archetype=data.get('archetype'),
            intrinsic_abilities=data.get('intrinsic_abilities') or {},
        )

        system.warp_points = deserialize_list(
            data.get('warp_points', []), WarpPoint.from_dict,
            'warp point', parent_name, strict=True,
        )
        system.planets = deserialize_list(
            data.get('planets', []), Planet.from_dict,
            'planet', parent_name, strict=True,
        )
        system.storms = deserialize_list(
            data.get('storms', []), Storm.from_dict,
            'storm', parent_name, strict=True,
        )
        return system
