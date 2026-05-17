"""Launch ability skeletons + scaling bindings.

PROJ-FMS-A Phase 5 introduced six classes (three strategic, three
tactical) covering the launch surface for mines, fighters, and
satellites. QA Observation C extends them:

- The tactical classes now expose ``launch_rate_tons_per_sec`` — a
  mass-tons/sec budget consumed by :class:`CarrierAIController`. The
  legacy ``capacity_per_action`` / ``cycle_time`` attributes are kept
  so the design-workshop UI can still report a per-cycle headline,
  and so the strategic-layer skeleton remains a count-of-vehicles
  surface.
- All six classes now consume ``launch_rate_mult`` via
  :class:`AbilityStatBinding` so :mod:`data.modifiers.json` size_mount
  scales the launch throughput linearly with the modifier param.

Data shape (tactical)::

    {
        "capacity_per_action": <int>,             # Strategic-style headline
        "cycle_time": <float>,                    # Strategic-style headline
        "launch_rate_tons_per_sec": <float>,      # Tactical mass-budget
    }

Data shape (strategic)::

    {"capacity_per_action": <int>, "cycle_time": <float>}

Scalar fallback (any class): integer treated as ``capacity_per_action``.
"""
from __future__ import annotations

from typing import Any, Dict, List

from .base import Ability, AbilityLayer
from .stat_keys import AbilityStatBinding, StatKey
from .ui_colors import HINT_NEUTRAL


class _LaunchAbilityBase(Ability):
    """Shared parsing for the six launch ability classes.

    Each class only differs in its ``layer`` (STRATEGIC vs COMBAT) and
    its registry key. ``launch_rate_tons_per_sec`` is read on tactical
    classes; strategic classes ignore it (count + cycle is their
    surface).
    """

    # Both strategic + tactical scale by ``launch_rate_mult``:
    #   - ``capacity_per_action`` directly scales (more launched per cycle).
    #   - ``launch_rate_tons_per_sec`` directly scales (more tons/sec).
    #   - ``cycle_time`` does NOT scale — gating cadence is independent
    #     of size for the strategic skeleton; the tactical budget is
    #     the authoritative throughput dial.
    STAT_BINDINGS: List[AbilityStatBinding] = [
        AbilityStatBinding(
            StatKey.LAUNCH_RATE_MULT,
            attribute_name="capacity_per_action",
            operation="multiply",
            base_attribute="_base_capacity_per_action",
        ),
        AbilityStatBinding(
            StatKey.LAUNCH_RATE_MULT,
            attribute_name="launch_rate_tons_per_sec",
            operation="multiply",
            base_attribute="_base_launch_rate_tons_per_sec",
        ),
    ]

    # Identifier exposed in UI rows; subclasses override.
    ui_label: str = "Launch"

    def _parse_attrs(self, data: Any) -> None:
        if isinstance(data, dict):
            cap = int(data.get("capacity_per_action", 0))
            cycle = float(data.get("cycle_time", 5.0))
            rate = float(data.get("launch_rate_tons_per_sec", 0.0))
        elif isinstance(data, (int, float)):
            cap = int(data)
            cycle = 5.0
            rate = 0.0
        else:
            cap = 0
            cycle = 5.0
            rate = 0.0

        self._base_capacity_per_action = cap
        self._base_launch_rate_tons_per_sec = rate
        self.capacity_per_action = cap
        self.cycle_time = cycle
        self.launch_rate_tons_per_sec = rate

    def recalculate(self) -> None:
        """Apply ``launch_rate_mult`` to ``capacity_per_action`` and rate."""
        mult = self.get_effective_stat("launch_rate_mult", 1.0)
        # capacity_per_action is conceptually an int; round to keep the
        # downstream UI/stat headlines clean.
        self.capacity_per_action = int(
            round(self._base_capacity_per_action * mult)
        )
        self.launch_rate_tons_per_sec = (
            self._base_launch_rate_tons_per_sec * mult
        )

    def get_primary_value(self) -> float:
        return float(self.capacity_per_action)

    def get_ui_rows(self) -> List[Dict[str, Any]]:
        rows: List[Dict[str, Any]] = [{
            "label": self.ui_label,
            "value": f"{self.capacity_per_action}/cycle ({self.cycle_time:g}s)",
            "color_hint": HINT_NEUTRAL,
        }]
        if self.launch_rate_tons_per_sec > 0:
            rows.append({
                "label": f"{self.ui_label} Rate",
                "value": f"{self.launch_rate_tons_per_sec:.1f} t/s",
                "color_hint": HINT_NEUTRAL,
            })
        return rows


# --- Strategic-layer skeletons -----------------------------------------

class StrategicMineLayerAbility(_LaunchAbilityBase):
    """Strategic-layer ability: lays mines from carried bay into a hex."""

    layer = AbilityLayer.STRATEGIC
    ui_label = "Mine Layer"


class StrategicFighterLaunchAbility(_LaunchAbilityBase):
    """Strategic-layer ability: launches carried fighters into a hex."""

    layer = AbilityLayer.STRATEGIC
    ui_label = "Fighter Launch"


class StrategicSatelliteLaunchAbility(_LaunchAbilityBase):
    """Strategic-layer ability: launches carried satellites into a hex."""

    layer = AbilityLayer.STRATEGIC
    ui_label = "Satellite Launch"


# --- Tactical (combat) skeletons ---------------------------------------

class TacticalMineLayerAbility(_LaunchAbilityBase):
    """Combat-layer ability: lays mines during a tactical battle."""

    layer = AbilityLayer.COMBAT
    ui_label = "Tactical Mine Layer"


class TacticalFighterLaunchAbility(_LaunchAbilityBase):
    """Combat-layer ability: launches a wave of fighters mid-battle.

    QA-C: ``launch_rate_tons_per_sec`` is the authoritative tactical
    throughput dial. :class:`CarrierAIController` accumulates a per-tick
    mass budget from this attribute and pops carried fighters whose mass
    fits, so variable-mass fighter fleets launch at variable rates from
    the same bay.
    """

    layer = AbilityLayer.COMBAT
    ui_label = "Tactical Fighter Launch"


class TacticalSatelliteLaunchAbility(_LaunchAbilityBase):
    """Combat-layer ability: deploys carried satellites mid-battle.

    Same mass-budget semantics as :class:`TacticalFighterLaunchAbility`.
    """

    layer = AbilityLayer.COMBAT
    ui_label = "Tactical Satellite Launch"
