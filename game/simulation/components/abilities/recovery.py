"""Recovery ability skeletons + scaling bindings.

PROJ-FMS-A Phase 5 introduced two strategic-layer skeleton classes:
one for fighters, one for satellites. Mines are one-way and never
recovered.

QA Observation C: both classes consume ``recovery_rate_mult`` via
:class:`AbilityStatBinding` so ``simple_size_mount`` scales
``recovery_per_action`` linearly with the modifier param. Even though
strategic recovery is "all in one turn" today, exposing this dial
keeps the surface symmetric with the launch path and ready for a
future per-tick tactical recovery hook.
"""
from __future__ import annotations

from typing import Any, Dict, List

from .base import Ability, AbilityLayer
from .stat_keys import AbilityStatBinding, StatKey
from .ui_colors import HINT_NEUTRAL


class _RecoveryAbilityBase(Ability):
    """Shared parsing for the two recovery ability classes."""

    STAT_BINDINGS: List[AbilityStatBinding] = [
        AbilityStatBinding(
            StatKey.RECOVERY_RATE_MULT,
            attribute_name="recovery_per_action",
            operation="multiply",
            base_attribute="_base_recovery_per_action",
        ),
    ]
    ui_label: str = "Recovery"

    def _parse_attrs(self, data: Any) -> None:
        if isinstance(data, dict):
            rec = int(data.get("recovery_per_action", 0))
        elif isinstance(data, (int, float)):
            rec = int(data)
        else:
            rec = 0
        self._base_recovery_per_action = rec
        self.recovery_per_action = rec

    def recalculate(self) -> None:
        """Apply ``recovery_rate_mult`` to ``recovery_per_action``."""
        mult = self.get_effective_stat("recovery_rate_mult", 1.0)
        self.recovery_per_action = int(
            round(self._base_recovery_per_action * mult)
        )

    def get_primary_value(self) -> float:
        return float(self.recovery_per_action)

    def get_ui_rows(self) -> List[Dict[str, Any]]:
        return [{
            "label": self.ui_label,
            "value": f"{self.recovery_per_action}/cycle",
            "color_hint": HINT_NEUTRAL,
        }]


class RecoverFightersAbility(_RecoveryAbilityBase):
    """Strategic ability: explicit fighter recovery from same-hex groups."""

    layer = AbilityLayer.STRATEGIC
    ui_label = "Fighter Recovery"


class RecoverSatellitesAbility(_RecoveryAbilityBase):
    """Strategic ability: explicit satellite recovery from same-hex groups."""

    layer = AbilityLayer.STRATEGIC
    ui_label = "Satellite Recovery"
