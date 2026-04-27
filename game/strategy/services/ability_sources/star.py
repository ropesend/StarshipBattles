"""StarAbilitySource — wraps a Star's intrinsic abilities (PROJ-302).

Stars project mostly system-scope abilities (radiation field, gravitational
interference, stellar heat) — the entire system is affected, not just the
star's own hex. Per PROJ-302 D7, hostile star systems are intentional design
with no balance cap; the System panel's hazard hint (D8) lets players see
the danger before flying in.
"""
from dataclasses import dataclass
from typing import Any, Dict, Optional

from game.strategy.services.ability_sources.labels import format_intrinsic_source_label


@dataclass(frozen=True)
class StarAbilitySource:
    """IAbilitySource adapter for a Star's intrinsic abilities."""
    star: Any  # game.strategy.data.stars.Star
    system: Any  # parent StarSystem

    @property
    def source_kind(self) -> str:
        return 'star'

    @property
    def source_label(self) -> str:
        star_type = getattr(self.star, 'star_type', None)
        type_name = star_type.name.replace('_', ' ').title() if star_type is not None else 'Star'
        return format_intrinsic_source_label(
            entity_name=getattr(self.star, 'name', 'Star'),
            type_name=type_name,
        )

    @property
    def source_id(self) -> str:
        return f"star:{getattr(self.star, 'name', id(self.star))}"

    @property
    def owner_id(self) -> Optional[int]:
        return None  # Stars are ownerless.

    def get_abilities(self) -> Dict[str, Any]:
        return dict(getattr(self.star, 'intrinsic_abilities', None) or {})

    def affects_hex(self, hex_coord) -> bool:
        """Stars project sector-scope abilities at the star's own hex.

        System-scope abilities are picked up by the system iterator (iterator
        passes hex_coord=None for system-wide queries). This method only
        guards sector-scope filtering at the collector level.
        """
        star_loc = getattr(self.star, 'location', None)
        sys_loc = getattr(self.system, 'global_location', None) or getattr(self.system, 'location', None)
        if star_loc is None or sys_loc is None:
            return False
        try:
            star_global = sys_loc + star_loc
        except TypeError:
            return False
        return hex_coord == star_global

    def affects_system(self, system) -> bool:
        return system is self.system

    def get_activation_state(self, ability_name: str) -> Optional[Any]:
        return None
