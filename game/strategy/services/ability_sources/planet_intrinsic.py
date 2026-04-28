"""PlanetIntrinsicAbilitySource — wraps a Planet's intrinsic abilities (PROJ-301).

A planet's intrinsic abilities are distinct from facilities built on it; they
come from the planet's `planet_type` (volcanic, gas giant, etc.) and may carry
generation-time-rolled values via `roll_intrinsic_abilities`. Both
`FacilityAbilitySource` (one per facility) and `PlanetIntrinsicAbilitySource`
(one per planet) wrap the same Planet — both contribute to Sector Effects.
"""
from dataclasses import dataclass
from typing import Any, Dict, Optional

from game.strategy.services.ability_sources.labels import format_intrinsic_source_label


@dataclass(frozen=True)
class PlanetIntrinsicAbilitySource:
    """IAbilitySource adapter for a Planet's intrinsic abilities."""
    planet: Any  # game.strategy.data.planet.Planet
    system: Any  # parent StarSystem (for global hex math)

    @property
    def source_kind(self) -> str:
        return 'planet'

    @property
    def source_label(self) -> str:
        planet_type = getattr(self.planet, 'planet_type', None)
        type_name = planet_type.name.title() if planet_type is not None else 'Planet'
        return format_intrinsic_source_label(
            entity_name=getattr(self.planet, 'name', 'Planet'),
            type_name=type_name,
        )

    @property
    def source_id(self) -> str:
        planet_id = getattr(self.planet, 'id', None)
        if planet_id is None or planet_id == -1:
            planet_id = getattr(self.planet, 'name', id(self.planet))
        return f"planet:{planet_id}"

    @property
    def owner_id(self) -> Optional[int]:
        # PROJ-301 D2: planet INTRINSIC abilities are ownerless — the volcano
        # damages friend and foe equally. Empire-scoped behavior would be
        # declared as `scope: allied_sector` on the ability itself, not via
        # owner_id.
        return None

    def get_abilities(self) -> Dict[str, Any]:
        return dict(getattr(self.planet, 'intrinsic_abilities', None) or {})

    def affects_hex(self, hex_coord) -> bool:
        """True if the queried hex is anywhere within the planet's footprint.

        Operates in the GLOBAL galaxy-map frame; local entity coordinates are
        translated via `system.global_location`.

        PROJ-301 D8: multi-hex bodies (Dyson sphere with `radius_hexes > 0`)
        project intrinsic abilities from EVERY occupied hex, not just the
        center. Standard single-hex planets reduce to the center match.
        """
        planet_loc = getattr(self.planet, 'location', None)
        sys_loc = getattr(self.system, 'global_location', None) or getattr(self.system, 'location', None)
        if planet_loc is None or sys_loc is None:
            return False

        # Multi-hex: walk every occupied local-hex, translated to global.
        radius_hexes = getattr(self.planet, 'radius_hexes', 0)
        if not isinstance(radius_hexes, int):
            radius_hexes = 0
        if radius_hexes > 0:
            occupied = getattr(self.planet, 'occupied_hexes', None)
            if occupied is None:
                # Fallback: compute from radius_hexes.
                from game.core.hex_math import hex_circle_filled
                occupied = hex_circle_filled(planet_loc, max(0, radius_hexes - 1))
            try:
                return any(hex_coord == sys_loc + local for local in occupied)
            except TypeError:
                return False

        try:
            return hex_coord == sys_loc + planet_loc
        except TypeError:
            return False

    def affects_system(self, system) -> bool:
        return system is self.system

    def get_activation_state(self, ability_name: str) -> Optional[Any]:
        return None  # Intrinsic abilities are always-on.
