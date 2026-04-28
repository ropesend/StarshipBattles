"""WarpPointAbilitySource — wraps a WarpPoint's intrinsic abilities (PROJ-303).

Warp points are single-hex entities. Most are 'stable' with no intrinsic
abilities; rarer types ('unstable', 'dimensional_rift', 'precursor_gateway')
add sector-scope hazards or perks at the warp point's hex.
"""
from dataclasses import dataclass
from typing import Any, Dict, Optional

from game.strategy.services.ability_sources.labels import format_intrinsic_source_label


@dataclass(frozen=True)
class WarpPointAbilitySource:
    """IAbilitySource adapter for a WarpPoint's intrinsic abilities."""
    warp_point: Any
    system: Any

    @property
    def source_kind(self) -> str:
        return 'warp_point'

    @property
    def source_label(self) -> str:
        warp_type = getattr(self.warp_point, 'warp_type', 'stable')
        # Warp points have no name field; fall back to "Warp Point -> {dest}".
        dest = getattr(self.warp_point, 'destination_id', '?')
        return format_intrinsic_source_label(
            entity_name=f"Warp Point → {dest}",
            type_name=warp_type,
        )

    @property
    def source_id(self) -> str:
        dest = getattr(self.warp_point, 'destination_id', id(self.warp_point))
        return f"warp_point:{dest}"

    @property
    def owner_id(self) -> Optional[int]:
        return None  # Warp points are ownerless.

    def get_abilities(self) -> Dict[str, Any]:
        return dict(getattr(self.warp_point, 'intrinsic_abilities', None) or {})

    def affects_hex(self, hex_coord) -> bool:
        """True if the queried hex is the warp point's hex.

        Operates in the GLOBAL galaxy-map frame; local entity coordinates are
        translated via `system.global_location`.
        """
        wp_loc = getattr(self.warp_point, 'location', None)
        sys_loc = getattr(self.system, 'global_location', None) or getattr(self.system, 'location', None)
        if wp_loc is None or sys_loc is None:
            return False
        try:
            return hex_coord == sys_loc + wp_loc
        except TypeError:
            return False

    def affects_system(self, system) -> bool:
        return system is self.system

    def get_activation_state(self, ability_name: str) -> Optional[Any]:
        return None
