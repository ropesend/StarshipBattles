"""PROJ-382 Phase 5: split sub-module of ``planetary.py``.

The original 913-LOC ``planetary.py`` was decomposed into a package
(``planetary/``) with one sub-module per responsibility. The package
``__init__`` re-exports every Ability so legacy imports
``from game.simulation.components.abilities.planetary import X``
continue to resolve.
"""

from typing import Dict, Any, List
from ..base import Ability, AbilityLayer, AbilityScope
from ..stat_keys import AbilityStatBinding
from ._shared import _STORM_SCOPES
from ..ui_colors import (
    HINT_ACCURACY, HINT_DEFAULT, HINT_WARP_ENERGY, HINT_COLONIZE,
    HINT_SHIELD_CAP, HINT_DAMAGE,
)


class ShieldModifierAbility(Ability):
    """Multiplies shield capacity for entities within scope.

    Strategic-layer ability that modifies shield effectiveness in combat.
    Values below 1.0 suppress shields; values above 1.0 boost them.
    Applied pre-battle by the combat modifier collector when ACTIVE.

    Planetary complex variants are activatable (have energy_drain_rate and
    activation_time). Ship-mounted fleet variants can omit these fields
    to remain passive (always-on).

    Data fields:
        multiplier: Shield capacity multiplier (e.g., 0.75 for 25% reduction)
        energy_drain_rate: Energy consumed per turn while active (0 = passive)
        activation_time: Ticks to activate (0 = passive/instant)
        deactivation_time: Ticks to deactivate
    """

    layer = AbilityLayer.STRATEGIC
    allowed_scopes = [
        AbilityScope.SELF, AbilityScope.FLEET,
        AbilityScope.SECTOR, AbilityScope.ALLIED_SECTOR,
        AbilityScope.PLAYER_SECTOR, AbilityScope.ENEMY_SECTOR,
        AbilityScope.SYSTEM, AbilityScope.ALLIED_SYSTEM,
        AbilityScope.PLAYER_SYSTEM, AbilityScope.ENEMY_SYSTEM,
    ]
    default_scope = AbilityScope.ALLIED_SYSTEM

    STAT_BINDINGS: List[AbilityStatBinding] = []

    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)

        if isinstance(data, dict):
            self.multiplier = data.get("multiplier", 1.0)
            self.energy_drain_rate = data.get("energy_drain_rate", 0.0)
            self.activation_time = data.get("activation_time", 0)
            self.deactivation_time = data.get("deactivation_time", 0)
        else:
            self.multiplier = 1.0
            self.energy_drain_rate = 0.0
            self.activation_time = 0
            self.deactivation_time = 0

    def get_primary_value(self) -> float:
        return self.multiplier

    def get_ui_rows(self) -> List[Dict[str, str]]:
        rows = [
            {
                'label': 'Shield Modifier',
                'value': f'{self.multiplier:.2f}x',
                'color_hint': HINT_SHIELD_CAP
            },
            {
                'label': 'Scope',
                'value': self.scope.value.replace('_', ' ').title(),
                'color_hint': HINT_SHIELD_CAP
            },
        ]
        if self.energy_drain_rate > 0:
            rows.append({
                'label': 'Energy Drain',
                'value': f'{self.energy_drain_rate:.1f}/turn',
                'color_hint': HINT_WARP_ENERGY
            })
        if self.activation_time > 0:
            rows.append({
                'label': 'Activation',
                'value': f'{self.activation_time} ticks',
                'color_hint': HINT_DEFAULT
            })
        return rows


class DamageModifierAbility(Ability):
    """Multiplies damage output for entities within scope.

    Strategic-layer ability that modifies weapon damage in combat.
    Values below 1.0 suppress damage; values above 1.0 boost it.
    Applied pre-battle by the combat modifier collector when ACTIVE.

    Planetary complex variants are activatable (have energy_drain_rate and
    activation_time). Ship-mounted fleet variants can omit these fields
    to remain passive (always-on).

    Data fields:
        multiplier: Damage output multiplier (e.g., 1.25 for 25% increase)
        energy_drain_rate: Energy consumed per turn while active (0 = passive)
        activation_time: Ticks to activate (0 = passive/instant)
        deactivation_time: Ticks to deactivate
    """

    layer = AbilityLayer.STRATEGIC
    allowed_scopes = [
        AbilityScope.SELF, AbilityScope.FLEET,
        AbilityScope.SECTOR, AbilityScope.ALLIED_SECTOR,
        AbilityScope.PLAYER_SECTOR, AbilityScope.ENEMY_SECTOR,
        AbilityScope.SYSTEM, AbilityScope.ALLIED_SYSTEM,
        AbilityScope.PLAYER_SYSTEM, AbilityScope.ENEMY_SYSTEM,
    ]
    default_scope = AbilityScope.ALLIED_SYSTEM

    STAT_BINDINGS: List[AbilityStatBinding] = []

    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)

        if isinstance(data, dict):
            self.multiplier = data.get("multiplier", 1.0)
            self.energy_drain_rate = data.get("energy_drain_rate", 0.0)
            self.activation_time = data.get("activation_time", 0)
            self.deactivation_time = data.get("deactivation_time", 0)
        else:
            self.multiplier = 1.0
            self.energy_drain_rate = 0.0
            self.activation_time = 0
            self.deactivation_time = 0

    def get_primary_value(self) -> float:
        return self.multiplier

    def get_ui_rows(self) -> List[Dict[str, str]]:
        rows = [
            {
                'label': 'Damage Modifier',
                'value': f'{self.multiplier:.2f}x',
                'color_hint': HINT_DAMAGE
            },
            {
                'label': 'Scope',
                'value': self.scope.value.replace('_', ' ').title(),
                'color_hint': HINT_SHIELD_CAP
            },
        ]
        if self.energy_drain_rate > 0:
            rows.append({
                'label': 'Energy Drain',
                'value': f'{self.energy_drain_rate:.1f}/turn',
                'color_hint': HINT_WARP_ENERGY
            })
        if self.activation_time > 0:
            rows.append({
                'label': 'Activation',
                'value': f'{self.activation_time} ticks',
                'color_hint': HINT_DEFAULT
            })
        return rows


class ThrustModifierAbility(Ability):
    """Multiplies effective combat thrust for entities within scope (PROJ-300).

    Strategic-layer multiplier consumed pre-battle by the combat propulsion
    stat aggregator (decisions.md D14 wires this end-to-end). Storm-projected
    `gravitational_anomaly` reduces effective thrust to 0.6x; multiple sources
    multiply per-provider (no shared stack_group on storms).

    Data fields:
        multiplier: Thrust multiplier (e.g., 0.6 for -40%; 1.25 for +25%)
    """

    layer = AbilityLayer.STRATEGIC
    allowed_scopes = _STORM_SCOPES
    default_scope = AbilityScope.SECTOR

    STAT_BINDINGS: List[AbilityStatBinding] = []

    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)
        self.multiplier = data.get("multiplier", 1.0) if isinstance(data, dict) else 1.0

    def get_primary_value(self) -> float:
        return self.multiplier

    def get_ui_rows(self) -> List[Dict[str, str]]:
        return [
            {'label': 'Thrust Modifier', 'value': f'{self.multiplier:.2f}x',
             'color_hint': HINT_DEFAULT},
            {'label': 'Scope', 'value': self.scope.value.replace('_', ' ').title(),
             'color_hint': HINT_DEFAULT},
        ]


class StrategicSpeedModifierAbility(Ability):
    """Multiplies fleet strategic-map movement speed for entities within scope.

    Consumed by `fleet_movement_engine` to compute effective movement points.
    Storm-projected `dark_nebula` slows fleets to 0.4x speed.

    Data fields:
        multiplier: Speed multiplier (e.g., 0.4 for -60%)
    """

    layer = AbilityLayer.STRATEGIC
    allowed_scopes = _STORM_SCOPES
    default_scope = AbilityScope.SECTOR

    STAT_BINDINGS: List[AbilityStatBinding] = []

    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)
        self.multiplier = data.get("multiplier", 1.0) if isinstance(data, dict) else 1.0

    def get_primary_value(self) -> float:
        return self.multiplier

    def get_ui_rows(self) -> List[Dict[str, str]]:
        return [
            {'label': 'Strategic Speed', 'value': f'{self.multiplier:.2f}x',
             'color_hint': HINT_DEFAULT},
            {'label': 'Scope', 'value': self.scope.value.replace('_', ' ').title(),
             'color_hint': HINT_DEFAULT},
        ]
