"""PROJ-FMS-A Phase 5 — recovery ability skeletons.

Two strategic-layer skeleton classes: one for fighters, one for
satellites. Mines are one-way and never recovered.

These hold ``recovery_per_action`` from component config and nothing
else. Behavior lands later:
  - ``RecoverFightersAbility`` -> PROJ-FMS-C Phase 3, ``OrderType.RECOVER_FIGHTERS``
  - ``RecoverSatellitesAbility`` -> PROJ-FMS-D Phase 2, ``OrderType.RECOVER_SATELLITES``
"""
from __future__ import annotations

from typing import Any, Dict, List

from .base import Ability, AbilityLayer
from .stat_keys import AbilityStatBinding
from .ui_colors import HINT_NEUTRAL


class _RecoveryAbilityBase(Ability):
    """Shared parsing for the two recovery ability classes."""

    STAT_BINDINGS: List[AbilityStatBinding] = []
    ui_label: str = "Recovery"

    def _parse_attrs(self, data: Any) -> None:
        if isinstance(data, dict):
            self.recovery_per_action = int(data.get("recovery_per_action", 0))
        elif isinstance(data, (int, float)):
            self.recovery_per_action = int(data)
        else:
            self.recovery_per_action = 0

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
