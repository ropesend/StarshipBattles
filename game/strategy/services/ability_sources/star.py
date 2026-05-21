"""StarAbilitySource — wraps a Star's intrinsic abilities (PROJ-302).

Stars project mostly system-scope abilities (radiation field, gravitational
interference, stellar heat) — the entire system is affected, not just the
star's own hex. Per PROJ-302 D7, hostile star systems are intentional design
with no balance cap; the System panel's hazard hint (D8) lets players see
the danger before flying in.
"""
from dataclasses import dataclass
from typing import Any, Dict, Optional
from game.core.protocols import SourceKind

from game.strategy.services.ability_sources.labels import format_intrinsic_source_label


@dataclass(frozen=True)
class StarAbilitySource:
    """IAbilitySource adapter for a Star's intrinsic abilities."""
    star: Any  # game.strategy.data.stars.Star
    system: Any  # parent StarSystem

    @property
    def source_kind(self) -> SourceKind:
        return SourceKind.STAR

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
        """Whether this star's abilities apply at the queried (global) hex.

        Returns True in two cases:

        1. Sector-scope: the star's own global hex matches ``hex_coord`` —
           any sector-scope ability fires there.
        2. System-scope: the star declares at least one ability with a
           system-shaped scope (``system``, ``allied_system``,
           ``player_system``, ``enemy_system``). System-scope abilities
           apply at every hex of the system, so the source must surface
           wherever the system's hexes are queried.

        Operates in the GLOBAL galaxy-map frame; local entity coordinates are
        translated via ``system.global_location``.

        The collector still filters by scope (``_SECTOR_SCOPES`` /
        ``_SYSTEM_SCOPES``), so widening this predicate to "yes for
        system-scope" does not leak system abilities into sector queries —
        it only ensures the source is *visible* to system-scope queries
        that arrive via a hex query path. PROJ-398, FND-041: this fold-in
        lets ``_star_provider`` use the shared ``_iter_hex_filtered_sources``
        skeleton.
        """
        star_loc = getattr(self.star, 'location', None)
        sys_loc = getattr(self.system, 'global_location', None) or getattr(self.system, 'location', None)
        if star_loc is None or sys_loc is None:
            return False
        try:
            star_global = sys_loc + star_loc
        except TypeError:
            return False
        if hex_coord == star_global:
            return True
        return self._has_system_scope_ability()

    def _has_system_scope_ability(self) -> bool:
        """Whether any intrinsic ability on the star has a system-shaped scope."""
        abilities = getattr(self.star, 'intrinsic_abilities', None)
        if not abilities:
            return False
        system_scopes = {'system', 'allied_system', 'player_system', 'enemy_system'}
        for entry in abilities.values():
            entries = entry if isinstance(entry, list) else [entry]
            for e in entries:
                if isinstance(e, dict) and e.get('scope') in system_scopes:
                    return True
        return False

    def affects_system(self, system) -> bool:
        return system is self.system

    def get_activation_state(self, ability_name: str) -> Optional[Any]:
        return None
