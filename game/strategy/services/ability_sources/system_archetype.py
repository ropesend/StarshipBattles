"""SystemAbilitySource — wraps a StarSystem's archetype abilities (PROJ-304).

Distinct from stars/planets/storms WITHIN the system: this is the system
itself projecting an archetype-flavored ability set across every hex of
the system. Most systems have archetype=None and produce no source.
"""
from dataclasses import dataclass
from typing import Any, Dict, Optional

from game.strategy.services.ability_sources.labels import format_intrinsic_source_label


@dataclass(frozen=True)
class SystemAbilitySource:
    """IAbilitySource adapter for the system itself."""
    system: Any  # StarSystem

    @property
    def source_kind(self) -> str:
        return 'system'

    @property
    def source_label(self) -> str:
        archetype = getattr(self.system, 'archetype', None) or 'unknown'
        return format_intrinsic_source_label(
            entity_name=getattr(self.system, 'name', 'System'),
            type_name=archetype.replace('_', ' ').title(),
        )

    @property
    def source_id(self) -> str:
        return f"system:{getattr(self.system, 'name', id(self.system))}"

    @property
    def owner_id(self) -> Optional[int]:
        return None  # Systems are ownerless.

    def get_abilities(self) -> Dict[str, Any]:
        return dict(getattr(self.system, 'intrinsic_abilities', None) or {})

    def affects_hex(self, hex_coord) -> bool:
        # Archetype abilities are all scope: system, applied via the system
        # iterator. Sector queries don't pick up system-scope abilities, so
        # affects_hex returning True is harmless — the collector's scope
        # filter handles it. Return True so per-hex iteration includes the
        # source for correctness.
        return True

    def affects_system(self, system) -> bool:
        return system is self.system

    def get_activation_state(self, ability_name: str) -> Optional[Any]:
        return None
