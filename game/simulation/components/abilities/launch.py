"""PROJ-FMS-A Phase 5 — launch ability skeletons.

Six classes (three strategic, three tactical) cover the launch surface
for mines, fighters, and satellites. All six are pure data carriers
exposing ``capacity_per_action`` and ``cycle_time`` from component
config. **No execution methods** — the base ``Ability`` class has no
``apply()``. Strategic execution lands later via
``OrderType.LAY_MINES`` / ``LAUNCH_FIGHTERS`` / ``LAUNCH_SATELLITES``
order handlers (PROJ-FMS-B Phase 1, PROJ-FMS-C Phase 1, PROJ-FMS-D
Phase 1). Tactical execution lands via battle-engine /
weapon-firing-system hooks at the same phases.

PROJ-FMS-A only registers these classes so designs that include them
validate and can be persisted; they hold their config attributes and
participate in ability MRO lookups but do nothing at runtime.
"""
from __future__ import annotations

from typing import Any, Dict, List

from .base import Ability, AbilityLayer
from .stat_keys import AbilityStatBinding
from .ui_colors import HINT_NEUTRAL


class _LaunchAbilityBase(Ability):
    """Shared parsing for the six launch ability classes.

    Each class only differs in its ``layer`` (STRATEGIC vs COMBAT) and
    its registry key. Data shape:
        Dict:   ``{"capacity_per_action": <int>, "cycle_time": <float>}``
        Scalar: integer treated as ``capacity_per_action``.
    """

    STAT_BINDINGS: List[AbilityStatBinding] = []

    # Identifier exposed in UI rows; subclasses override.
    ui_label: str = "Launch"

    def _parse_attrs(self, data: Any) -> None:
        if isinstance(data, dict):
            self.capacity_per_action = int(data.get("capacity_per_action", 0))
            self.cycle_time = float(data.get("cycle_time", 5.0))
        elif isinstance(data, (int, float)):
            self.capacity_per_action = int(data)
            self.cycle_time = 5.0
        else:
            self.capacity_per_action = 0
            self.cycle_time = 5.0

    def get_primary_value(self) -> float:
        return float(self.capacity_per_action)

    def get_ui_rows(self) -> List[Dict[str, Any]]:
        return [{
            "label": self.ui_label,
            "value": f"{self.capacity_per_action}/cycle ({self.cycle_time:g}s)",
            "color_hint": HINT_NEUTRAL,
        }]


# --- Strategic-layer skeletons -----------------------------------------

class StrategicMineLayerAbility(_LaunchAbilityBase):
    """Strategic-layer ability: lays mines from carried bay into a hex.

    Wired in PROJ-FMS-B Phase 1 via ``OrderType.LAY_MINES`` +
    ``LayMinesOrderHandler``.
    """

    layer = AbilityLayer.STRATEGIC
    ui_label = "Mine Layer"


class StrategicFighterLaunchAbility(_LaunchAbilityBase):
    """Strategic-layer ability: launches carried fighters into a hex.

    Wired in PROJ-FMS-C Phase 1 via ``OrderType.LAUNCH_FIGHTERS`` +
    ``LaunchFightersOrderHandler``.
    """

    layer = AbilityLayer.STRATEGIC
    ui_label = "Fighter Launch"


class StrategicSatelliteLaunchAbility(_LaunchAbilityBase):
    """Strategic-layer ability: launches carried satellites into a hex.

    Wired in PROJ-FMS-D Phase 1 via ``OrderType.LAUNCH_SATELLITES`` +
    ``LaunchSatellitesOrderHandler``.
    """

    layer = AbilityLayer.STRATEGIC
    ui_label = "Satellite Launch"


# --- Tactical (combat) skeletons ---------------------------------------

class TacticalMineLayerAbility(_LaunchAbilityBase):
    """Combat-layer ability: lays mines during a tactical battle.

    Wired in PROJ-FMS-B Phase 3 via the tactical mine resolver hook
    inside :mod:`game.simulation.systems.battle_engine`.
    """

    layer = AbilityLayer.COMBAT
    ui_label = "Tactical Mine Layer"


class TacticalFighterLaunchAbility(_LaunchAbilityBase):
    """Combat-layer ability: launches a wave of fighters mid-battle.

    Replaces the legacy :class:`VehicleLaunchAbility` at
    :mod:`markers.py:9-61` once the firing-system rewrite at
    :mod:`weapon_firing_system.py:130-140` and the attack-processor
    rewrite at :mod:`attack_processor.py:68-97` land in PROJ-FMS-C
    Phase 1. For PROJ-FMS-A the legacy class is kept in place and the
    new skeleton is registered alongside.
    """

    layer = AbilityLayer.COMBAT
    ui_label = "Tactical Fighter Launch"


class TacticalSatelliteLaunchAbility(_LaunchAbilityBase):
    """Combat-layer ability: deploys carried satellites mid-battle.

    Wired in PROJ-FMS-D Phase 1.
    """

    layer = AbilityLayer.COMBAT
    ui_label = "Tactical Satellite Launch"
