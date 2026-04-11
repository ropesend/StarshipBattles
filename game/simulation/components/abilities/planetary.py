"""
Strategic-layer abilities for shields, stabilizers, boosters, and resource generation.

PROJ-237: Created for planetary complexes.
PROJ-238: PlanetaryEnergyGeneratorAbility renamed to StrategicResourceGenerationAbility
          (generic, works on ships and planets). PlanetaryEnergyStorageAbility deleted
          (reuse combat ResourceStorage).
"""

from typing import Dict, Any, List
from .base import Ability, AbilityLayer, AbilityScope
from .stat_keys import AbilityStatBinding
from .ui_colors import (
    HINT_ACCURACY, HINT_DEFAULT, HINT_WARP_ENERGY, HINT_COLONIZE,
    HINT_SHIELD_CAP, HINT_DAMAGE,
)


class PlanetaryShieldAbility(Ability):
    """Enables planetary shield protection.

    When active, consumes energy per turn and blocks planet destroyer
    superweapons. Activation and deactivation take time (in ticks).

    Data fields:
        energy_drain_rate: Energy consumed per turn while active
        activation_time: Ticks required to activate the shield
        deactivation_time: Ticks required to deactivate the shield
        shield_hp: Combat shield hit points (placeholder for future combat integration)
        shield_regen: Combat shield regeneration rate (placeholder for future combat integration)
    """

    STAT_BINDINGS: List[AbilityStatBinding] = []  # Strategic marker ability

    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)

        if isinstance(data, dict):
            self.energy_drain_rate = data.get("energy_drain_rate", 0.0)
            self.activation_time = data.get("activation_time", 1)
            self.deactivation_time = data.get("deactivation_time", 1)
            # Combat placeholders (future integration)
            self.shield_hp = data.get("shield_hp", 0.0)
            self.shield_regen = data.get("shield_regen", 0.0)
        else:
            self.energy_drain_rate = 0.0
            self.activation_time = 1
            self.deactivation_time = 1
            self.shield_hp = 0.0
            self.shield_regen = 0.0

    def get_primary_value(self) -> float:
        """Return the energy drain rate as primary value."""
        return self.energy_drain_rate

    def get_ui_rows(self) -> List[Dict[str, str]]:
        """Return UI rows showing shield stats."""
        return [
            {
                'label': 'Energy Drain',
                'value': f'{self.energy_drain_rate:.1f}/turn',
                'color_hint': HINT_WARP_ENERGY
            },
            {
                'label': 'Activation Time',
                'value': f'{self.activation_time} ticks',
                'color_hint': HINT_DEFAULT
            },
            {
                'label': 'Deactivation Time',
                'value': f'{self.deactivation_time} ticks',
                'color_hint': HINT_DEFAULT
            },
        ]


class StrategicResourceGenerationAbility(Ability):
    """Generates resources per turn on the strategy layer.

    Each instance generates a specific resource type at a given rate per turn
    (spread across 100 ticks). Works on any entity with facilities (planets,
    space stations, ships).

    Separate from combat ResourceGeneration which operates per second.

    Data fields:
        resource: Resource type identifier (e.g. from resources.json). Required.
        generation_rate: Amount produced per turn.
    """

    STAT_BINDINGS: List[AbilityStatBinding] = []  # Strategic marker ability

    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)

        if isinstance(data, dict):
            self.resource = data.get("resource", "")
            self.generation_rate = data.get("generation_rate", 0.0)
        else:
            self.resource = ""
            self.generation_rate = 0.0

    def get_primary_value(self) -> float:
        """Return the generation rate as primary value."""
        return self.generation_rate

    def get_ui_rows(self) -> List[Dict[str, str]]:
        """Return UI rows showing strategic generation stats."""
        return [
            {
                'label': 'Resource',
                'value': self.resource,
                'color_hint': HINT_COLONIZE
            },
            {
                'label': 'Strategic Rate',
                'value': f'{self.generation_rate:,.0f}/turn',
                'color_hint': HINT_ACCURACY
            },
        ]


class GeologicStabilizerAbility(Ability):
    """Prevents planet-destroying superweapons within scope.

    When active, protects planets from IMPLODE_PLANET superweapon.
    Scope determines range of protection:
    - PLANET: protects only the planet this facility is on
    - SECTOR: protects all planets in the same hex
    - SYSTEM: protects all planets in the star system

    Requires energy and manual activation (same mechanism as PlanetaryShield).

    Data fields:
        energy_drain_rate: Energy consumed per turn while active
        activation_time: Ticks required to activate
        deactivation_time: Ticks required to deactivate
    """

    layer = AbilityLayer.STRATEGIC
    allowed_scopes = [AbilityScope.PLANET, AbilityScope.SECTOR, AbilityScope.SYSTEM]
    default_scope = AbilityScope.SECTOR

    STAT_BINDINGS: List[AbilityStatBinding] = []

    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)

        if isinstance(data, dict):
            self.energy_drain_rate = data.get("energy_drain_rate", 0.0)
            self.activation_time = data.get("activation_time", 1)
            self.deactivation_time = data.get("deactivation_time", 1)
        else:
            self.energy_drain_rate = 0.0
            self.activation_time = 1
            self.deactivation_time = 1

    def get_primary_value(self) -> float:
        return self.energy_drain_rate

    def get_ui_rows(self) -> List[Dict[str, str]]:
        return [
            {
                'label': 'Energy Drain',
                'value': f'{self.energy_drain_rate:.1f}/turn',
                'color_hint': HINT_WARP_ENERGY
            },
            {
                'label': 'Scope',
                'value': self.scope.value.replace('_', ' ').title(),
                'color_hint': HINT_SHIELD_CAP
            },
            {
                'label': 'Activation',
                'value': f'{self.activation_time} ticks',
                'color_hint': HINT_DEFAULT
            },
        ]


class StellarStabilizerAbility(Ability):
    """Prevents star-destroying superweapons (DestroyStar, CreateDysonSphere) within scope.

    When active, blocks STELLERATE_STAR and CREATE_DYSON_SPHERE superweapon orders
    from affecting any star in the system. Requires energy and manual activation.

    Data fields:
        energy_drain_rate: Energy consumed per turn while active
        activation_time: Ticks required to activate
        deactivation_time: Ticks required to deactivate
    """

    layer = AbilityLayer.STRATEGIC
    allowed_scopes = [AbilityScope.SECTOR, AbilityScope.SYSTEM]
    default_scope = AbilityScope.SYSTEM

    STAT_BINDINGS: List[AbilityStatBinding] = []

    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)

        if isinstance(data, dict):
            self.energy_drain_rate = data.get("energy_drain_rate", 0.0)
            self.activation_time = data.get("activation_time", 1)
            self.deactivation_time = data.get("deactivation_time", 1)
        else:
            self.energy_drain_rate = 0.0
            self.activation_time = 1
            self.deactivation_time = 1

    def get_primary_value(self) -> float:
        return self.energy_drain_rate

    def get_ui_rows(self) -> List[Dict[str, str]]:
        return [
            {
                'label': 'Energy Drain',
                'value': f'{self.energy_drain_rate:.1f}/turn',
                'color_hint': HINT_WARP_ENERGY
            },
            {
                'label': 'Scope',
                'value': self.scope.value.replace('_', ' ').title(),
                'color_hint': HINT_SHIELD_CAP
            },
            {
                'label': 'Activation',
                'value': f'{self.activation_time} ticks',
                'color_hint': HINT_DEFAULT
            },
        ]


class WarpFieldStabilizerAbility(Ability):
    """Prevents warp point creation and destruction within scope.

    When active, blocks OPEN_WARP_POINT and CLOSE_WARP_POINT superweapon orders
    from affecting the system. Requires energy and manual activation.

    Data fields:
        energy_drain_rate: Energy consumed per turn while active
        activation_time: Ticks required to activate
        deactivation_time: Ticks required to deactivate
    """

    layer = AbilityLayer.STRATEGIC
    allowed_scopes = [AbilityScope.SECTOR, AbilityScope.SYSTEM]
    default_scope = AbilityScope.SYSTEM

    STAT_BINDINGS: List[AbilityStatBinding] = []

    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)

        if isinstance(data, dict):
            self.energy_drain_rate = data.get("energy_drain_rate", 0.0)
            self.activation_time = data.get("activation_time", 1)
            self.deactivation_time = data.get("deactivation_time", 1)
        else:
            self.energy_drain_rate = 0.0
            self.activation_time = 1
            self.deactivation_time = 1

    def get_primary_value(self) -> float:
        return self.energy_drain_rate

    def get_ui_rows(self) -> List[Dict[str, str]]:
        return [
            {
                'label': 'Energy Drain',
                'value': f'{self.energy_drain_rate:.1f}/turn',
                'color_hint': HINT_WARP_ENERGY
            },
            {
                'label': 'Scope',
                'value': self.scope.value.replace('_', ' ').title(),
                'color_hint': HINT_SHIELD_CAP
            },
            {
                'label': 'Activation',
                'value': f'{self.activation_time} ticks',
                'color_hint': HINT_DEFAULT
            },
        ]


class ResourceHarvestBoosterAbility(Ability):
    """Increases resource harvesting rate for a specific resource within scope.

    Multiplies the base_harvest_rate of matching ResourceHarvester abilities
    on colonies within the configured scope.

    Data fields:
        resource_type: Which resource to boost (e.g., "metals")
        multiplier: Harvest rate multiplier (e.g., 1.5 for 50% increase)
    """

    layer = AbilityLayer.STRATEGIC
    allowed_scopes = [
        AbilityScope.SELF, AbilityScope.PLANET, AbilityScope.SECTOR,
        AbilityScope.SYSTEM, AbilityScope.EMPIRE, AbilityScope.ALLIED_EMPIRE,
    ]
    default_scope = AbilityScope.PLANET

    STAT_BINDINGS: List[AbilityStatBinding] = []

    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)

        if isinstance(data, dict):
            self.resource_type = data.get("resource_type", "")
            self.multiplier = data.get("multiplier", 1.0)
        else:
            self.resource_type = ""
            self.multiplier = 1.0

    def get_primary_value(self) -> float:
        return self.multiplier

    def get_ui_rows(self) -> List[Dict[str, str]]:
        return [
            {
                'label': 'Resource',
                'value': self.resource_type.title(),
                'color_hint': HINT_COLONIZE
            },
            {
                'label': 'Boost',
                'value': f'{self.multiplier:.2f}x',
                'color_hint': HINT_ACCURACY
            },
            {
                'label': 'Scope',
                'value': self.scope.value.replace('_', ' ').title(),
                'color_hint': HINT_SHIELD_CAP
            },
        ]


class BuildRateBoosterAbility(Ability):
    """Increases construction/production rate within scope.

    Multiplies the production rate of all build queues on colonies
    within the configured scope.

    Data fields:
        multiplier: Build rate multiplier (e.g., 1.25 for 25% faster)
    """

    layer = AbilityLayer.STRATEGIC
    allowed_scopes = [
        AbilityScope.SELF, AbilityScope.PLANET, AbilityScope.SECTOR,
        AbilityScope.SYSTEM, AbilityScope.EMPIRE, AbilityScope.ALLIED_EMPIRE,
    ]
    default_scope = AbilityScope.SECTOR

    STAT_BINDINGS: List[AbilityStatBinding] = []

    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)

        if isinstance(data, dict):
            self.multiplier = data.get("multiplier", 1.0)
        else:
            self.multiplier = 1.0

    def get_primary_value(self) -> float:
        return self.multiplier

    def get_ui_rows(self) -> List[Dict[str, str]]:
        return [
            {
                'label': 'Build Rate',
                'value': f'{self.multiplier:.2f}x',
                'color_hint': HINT_ACCURACY
            },
            {
                'label': 'Scope',
                'value': self.scope.value.replace('_', ' ').title(),
                'color_hint': HINT_SHIELD_CAP
            },
        ]


class AtmosphereModifierAbility(Ability):
    """Modifies a planet's atmosphere toward target gas compositions.

    Slowly adds or removes atmospheric gases each turn. The rate is in kg of
    gas that can be processed per turn. Conversion to pressure change depends
    on the planet's surface area and gravity.

    Data fields:
        modification_rate: kg of atmosphere that can be added/removed per turn
    """

    layer = AbilityLayer.STRATEGIC
    allowed_scopes = [AbilityScope.SELF]
    default_scope = AbilityScope.SELF

    STAT_BINDINGS: List[AbilityStatBinding] = []

    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)

        if isinstance(data, dict):
            self.modification_rate = data.get("modification_rate", 0.0)
        else:
            self.modification_rate = 0.0

    def get_primary_value(self) -> float:
        return self.modification_rate

    def get_ui_rows(self) -> List[Dict[str, str]]:
        return [
            {
                'label': 'Modification Rate',
                'value': f'{self.modification_rate:.2e} kg/turn',
                'color_hint': HINT_COLONIZE
            },
        ]


class ShieldModifierAbility(Ability):
    """Multiplies shield capacity for entities within scope.

    Strategic-layer ability that modifies shield effectiveness in combat.
    Values below 1.0 suppress shields; values above 1.0 boost them.
    Applied pre-battle by the combat modifier collector.

    Data fields:
        multiplier: Shield capacity multiplier (e.g., 0.75 for 25% reduction)
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
        else:
            self.multiplier = 1.0

    def get_primary_value(self) -> float:
        return self.multiplier

    def get_ui_rows(self) -> List[Dict[str, str]]:
        return [
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


class DamageModifierAbility(Ability):
    """Multiplies damage output for entities within scope.

    Strategic-layer ability that modifies weapon damage in combat.
    Values below 1.0 suppress damage; values above 1.0 boost it.
    Applied pre-battle by the combat modifier collector.

    Data fields:
        multiplier: Damage output multiplier (e.g., 1.25 for 25% increase)
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
        else:
            self.multiplier = 1.0

    def get_primary_value(self) -> float:
        return self.multiplier

    def get_ui_rows(self) -> List[Dict[str, str]]:
        return [
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


class QualityImprovementAbility(Ability):
    """Permanently improves resource deposit quality on a planet.

    Each turn, adds improvement_rate to the quality value of the specified
    resource on the planet. The change is permanent — it persists even if
    the facility is later removed. Quality caps at 100.

    Data fields:
        resource_type: Which resource to improve (e.g., "metals")
        improvement_rate: Quality increase per turn (e.g., 0.1)
    """

    layer = AbilityLayer.STRATEGIC
    allowed_scopes = [AbilityScope.SELF]
    default_scope = AbilityScope.SELF

    STAT_BINDINGS: List[AbilityStatBinding] = []

    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)

        if isinstance(data, dict):
            self.resource_type = data.get("resource_type", "")
            self.improvement_rate = data.get("improvement_rate", 0.0)
        else:
            self.resource_type = ""
            self.improvement_rate = 0.0

    def get_primary_value(self) -> float:
        return self.improvement_rate

    def get_ui_rows(self) -> List[Dict[str, str]]:
        return [
            {
                'label': 'Resource',
                'value': self.resource_type.title(),
                'color_hint': HINT_COLONIZE
            },
            {
                'label': 'Improvement',
                'value': f'+{self.improvement_rate:.1f}/turn',
                'color_hint': HINT_ACCURACY
            },
        ]


class GravityModifierAbility(Ability):
    """Modifies planet gravity when active. Reverts on deactivation.

    Activatable ability that changes the planet's effective gravity to a
    player-set target. Requires energy and uses the ComponentActivationEngine
    timer system. When the facility is deactivated or destroyed, gravity
    reverts to the original value.

    Data fields:
        energy_drain_rate: Energy consumed per turn while active
        activation_time: Ticks required to activate
        deactivation_time: Ticks required to deactivate
    """

    layer = AbilityLayer.STRATEGIC
    allowed_scopes = [AbilityScope.SELF]
    default_scope = AbilityScope.SELF

    STAT_BINDINGS: List[AbilityStatBinding] = []

    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)

        if isinstance(data, dict):
            self.energy_drain_rate = data.get("energy_drain_rate", 0.0)
            self.activation_time = data.get("activation_time", 1)
            self.deactivation_time = data.get("deactivation_time", 1)
        else:
            self.energy_drain_rate = 0.0
            self.activation_time = 1
            self.deactivation_time = 1

    def get_primary_value(self) -> float:
        return self.energy_drain_rate

    def get_ui_rows(self) -> List[Dict[str, str]]:
        return [
            {
                'label': 'Energy Drain',
                'value': f'{self.energy_drain_rate:.1f}/turn',
                'color_hint': HINT_WARP_ENERGY
            },
            {
                'label': 'Activation',
                'value': f'{self.activation_time} ticks',
                'color_hint': HINT_DEFAULT
            },
        ]


class WaterModifierAbility(Ability):
    """Gradually changes planet water level toward target. Permanent.

    Passive ability that modifies surface_water each turn. The rate is the
    fraction of water coverage that can be changed per turn. Processed by
    WaterEngine once per turn, similar to AtmosphereEngine.

    Data fields:
        modification_rate: Fraction of water coverage change per turn (e.g., 0.005)
    """

    layer = AbilityLayer.STRATEGIC
    allowed_scopes = [AbilityScope.SELF]
    default_scope = AbilityScope.SELF

    STAT_BINDINGS: List[AbilityStatBinding] = []

    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)

        if isinstance(data, dict):
            self.modification_rate = data.get("modification_rate", 0.0)
        else:
            self.modification_rate = 0.0

    def get_primary_value(self) -> float:
        return self.modification_rate

    def get_ui_rows(self) -> List[Dict[str, str]]:
        return [
            {
                'label': 'Modification Rate',
                'value': f'{self.modification_rate:.4f}/turn',
                'color_hint': HINT_COLONIZE
            },
        ]


class RadiationShieldAbility(Ability):
    """Provides radiation shielding when active. Reverts on deactivation.

    Activatable ability that adds artificial radiation protection to a planet.
    The shielding value is additive with the planet's natural magnetic_field
    in habitability calculations. When deactivated or destroyed, the shielding
    reverts to zero.

    Data fields:
        energy_drain_rate: Energy consumed per turn while active
        activation_time: Ticks required to activate
        deactivation_time: Ticks required to deactivate
        max_shielding: Maximum radiation shielding strength (additive with magnetic_field)
    """

    layer = AbilityLayer.STRATEGIC
    allowed_scopes = [AbilityScope.SELF]
    default_scope = AbilityScope.SELF

    STAT_BINDINGS: List[AbilityStatBinding] = []

    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)

        if isinstance(data, dict):
            self.energy_drain_rate = data.get("energy_drain_rate", 0.0)
            self.activation_time = data.get("activation_time", 1)
            self.deactivation_time = data.get("deactivation_time", 1)
            self.max_shielding = data.get("max_shielding", 1.0)
        else:
            self.energy_drain_rate = 0.0
            self.activation_time = 1
            self.deactivation_time = 1
            self.max_shielding = 1.0

    def get_primary_value(self) -> float:
        return self.energy_drain_rate

    def get_ui_rows(self) -> List[Dict[str, str]]:
        return [
            {
                'label': 'Energy Drain',
                'value': f'{self.energy_drain_rate:.1f}/turn',
                'color_hint': HINT_WARP_ENERGY
            },
            {
                'label': 'Max Shielding',
                'value': f'{self.max_shielding:.1f}',
                'color_hint': HINT_SHIELD_CAP
            },
            {
                'label': 'Activation',
                'value': f'{self.activation_time} ticks',
                'color_hint': HINT_DEFAULT
            },
        ]
