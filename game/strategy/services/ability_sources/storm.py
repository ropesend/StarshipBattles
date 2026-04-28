"""StormAbilitySource adapter — wraps a Storm entity (PROJ-300).

Storms are sector-scope ability sources with no owner. The adapter accepts
an optional `system` reference so `affects_hex` can translate the storm's
local-frame `location + hex_offsets` into global galaxy-map coordinates,
matching the `PlanetIntrinsicAbilitySource` / `StarAbilitySource` /
`WarpPointAbilitySource` convention. When `system` is None (legacy mock
fixtures with an `occupied_hexes` attribute and no parent system), the
adapter falls back to a local-frame `in occupied_hexes` check.
"""
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class StormAbilitySource:
    """IAbilitySource adapter for Storm entities."""
    storm: Any  # game.strategy.data.storm.Storm
    system: Any = None  # parent StarSystem (for global-frame hex match)

    @property
    def source_kind(self) -> str:
        return 'storm'

    @property
    def source_label(self) -> str:
        return getattr(self.storm, 'name', 'Storm')

    @property
    def source_id(self) -> str:
        # Storm.name is a stable display id (Storms have no UUID); prefix to
        # disambiguate from other source kinds.
        return f"storm:{getattr(self.storm, 'name', id(self.storm))}"

    @property
    def owner_id(self) -> Optional[int]:
        return None  # Storms are ownerless — apply to all empires.

    def get_abilities(self) -> Dict[str, Any]:
        """Return storm abilities dict (PROJ-300 v2.0 shape only)."""
        abilities_attr = getattr(self.storm, 'abilities', None)
        return abilities_attr if isinstance(abilities_attr, dict) else {}

    def affects_hex(self, hex_coord) -> bool:
        """True if the storm covers `hex_coord` in the GLOBAL galaxy-map frame.

        Operates in the GLOBAL galaxy-map frame; local entity coordinates are
        translated via `system.global_location`. When `self.system` is None
        (unparented adapter, e.g. mock fixtures that supply `occupied_hexes`
        directly), falls back to a local-frame match against `occupied_hexes`.
        """
        sys_loc = (
            getattr(self.system, 'global_location', None)
            or getattr(self.system, 'location', None)
        )
        storm_loc = getattr(self.storm, 'location', None)
        offsets = getattr(self.storm, 'hex_offsets', None)
        if sys_loc is None or storm_loc is None or offsets is None:
            # Fallback for unparented / mock storms with `occupied_hexes` only.
            try:
                occupied = self.storm.occupied_hexes
            except AttributeError:
                return False
            return hex_coord in occupied
        try:
            return any(hex_coord == sys_loc + storm_loc + off for off in offsets)
        except TypeError:
            return False

    def affects_system(self, system) -> bool:
        # A storm belongs to exactly one system. The iterator is responsible
        # for only calling adapters from the right system; if asked, we
        # return True (the system that produced this adapter).
        return True

    def get_activation_state(self, ability_name: str) -> Optional[Any]:
        return None  # Storms are always active.
