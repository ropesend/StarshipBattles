"""StormAbilitySource adapter — wraps a Storm entity (PROJ-300).

Storms are sector-scope ability sources with no owner. Phase 3 supports both
the legacy `Storm.effects: StormEffect` shape (translates to abilities dict
on-the-fly) AND the new `Storm.abilities: Dict[str, Any]` shape introduced in
Phase 5. After Phase 5 lands, the legacy translation path is removed.
"""
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class StormAbilitySource:
    """IAbilitySource adapter for Storm entities."""
    storm: Any  # game.strategy.data.storm.Storm

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
        # Storm.occupied_hexes is in local-system coordinates; the iterator
        # passes the GLOBAL hex it's queried for. Caller-specified hex match
        # logic; for symmetry with the legacy AreaEffectManager check, we
        # delegate to the storm's `occupied_hexes` property.
        try:
            occupied = self.storm.occupied_hexes
        except AttributeError:
            return False
        return hex_coord in occupied

    def affects_system(self, system) -> bool:
        # A storm belongs to exactly one system. The iterator is responsible
        # for only calling adapters from the right system; if asked, we
        # return True (the system that produced this adapter).
        return True

    def get_activation_state(self, ability_name: str) -> Optional[Any]:
        return None  # Storms are always active.
