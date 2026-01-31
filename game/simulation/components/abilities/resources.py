from typing import Dict, Any, List

from game.core.config import PhysicsConfig
from .base import Ability
from .stat_keys import StatKey, AbilityStatBinding


class ResourceConsumption(Ability):
    """
    Ability to consume resources.
    Data: { "resource": "fuel", "amount": 10, "trigger": "constant"|"activation"|"strategic_per_hex" }

    Triggers:
    - "constant": Per-tick consumption during combat (e.g., engine fuel drain)
    - "activation": Per-use consumption (e.g., weapon ammo)
    - "strategic_per_hex": Per-hex consumption during strategic map movement
    """

    STAT_BINDINGS: List[AbilityStatBinding] = [
        AbilityStatBinding(StatKey.CONSUMPTION_MULT, 'amount', 'multiply', '_base_amount'),
    ]

    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)
        self.resource_name = data.get('resource', '')
        self.amount = data.get('amount', 0.0)
        self._base_amount = self.amount
        self.trigger = data.get('trigger', 'constant')  # 'constant' or 'activation'

    def sync_data(self, data: Any):
        super().sync_data(data)
        if isinstance(data, dict):
            self.resource_name = data.get('resource', self.resource_name)
            self.amount = data.get('amount', 0.0)
            self._base_amount = self.amount
            self.trigger = data.get('trigger', 'constant')
        elif isinstance(data, (int, float)):
            self.amount = float(data)
            self._base_amount = self.amount
            self.trigger = 'constant'  # Default for shortcut

    def recalculate(self):
        self.amount = self._base_amount * self.get_effective_stat('consumption_mult', 1.0)

    def _get_resource_registry(self, resources=None):
        """Get the resource registry to use.

        Args:
            resources: Optional ResourceRegistry to use instead of component.ship.resources.

        Returns:
            ResourceRegistry or None if not available.
        """
        if resources is not None:
            return resources
        if self.component.ship and self.component.ship.resources:
            return self.component.ship.resources
        return None

    def update(self, resources=None) -> bool:
        """Update resource consumption for one tick.

        Args:
            resources: Optional ResourceRegistry to use instead of component.ship.resources.
                       Supports decoupled operation without ship reference.
        """
        if self.trigger == 'constant':
            registry = self._get_resource_registry(resources)
            if registry:
                res = registry.get_resource(self.resource_name)
                if res:
                    # Constant consumption is per second, multiply by tick duration
                    cost = self.amount * PhysicsConfig.TICK_RATE
                    if not res.consume(cost):
                        return False  # Starvation
                else:
                    if self.amount > 0:
                        return False
        return True

    def check_and_consume(self, resources=None) -> bool:
        """Explicitly call for one-shot consumption checks.

        Args:
            resources: Optional ResourceRegistry to use instead of component.ship.resources.
        """
        registry = self._get_resource_registry(resources)
        if registry:
            res = registry.get_resource(self.resource_name)
            if res:
                return res.consume(self.amount)
            else:
                return self.amount <= 0
        return False

    def check_available(self, resources=None) -> bool:
        """Check if resource is available for consumption.

        Args:
            resources: Optional ResourceRegistry to use instead of component.ship.resources.
        """
        registry = self._get_resource_registry(resources)
        if registry:
            res = registry.get_resource(self.resource_name)
            if res:
                return res.has_sufficient(self.amount)
            else:
                return self.amount <= 0
        return False

    def get_strategic_cost(self) -> float:
        """
        Get per-hex strategic movement cost.

        Returns:
            Fuel/resource cost per hex if trigger is 'strategic_per_hex', else 0.
        """
        if self.trigger == 'strategic_per_hex':
            return self.amount
        return 0.0

    def get_ui_rows(self):
        if self.trigger == 'strategic_per_hex':
            trigger_str = "/hex"
        elif self.trigger == 'constant':
            trigger_str = "/s"
        else:
            trigger_str = "/use"

        # Color mapping based on resource type
        color = '#FFFFFF'
        if self.resource_name == 'fuel':
            color = '#FFA500'  # Orange
        elif self.resource_name == 'energy':
            color = '#64C8FF'  # Light Blue
        elif self.resource_name == 'ammo':
            color = '#C8C832'  # Dirty Yellow

        label_text = f"{self.resource_name.title()} {'Cost' if self.trigger != 'constant' else 'Use'}"
        # Handle both numeric and formula string amounts
        if isinstance(self.amount, str):
            value_str = f"{self.amount}{trigger_str}"
        else:
            value_str = f"{self.amount:.1f}{trigger_str}"
        return [{'label': label_text, 'value': value_str, 'color_hint': color}]

    def get_primary_value(self) -> float:
        return self.amount


class ResourceStorage(Ability):
    """
    Ability to store resources.
    Data: { "resource": "fuel", "amount": 100 }
    """

    STAT_BINDINGS: List[AbilityStatBinding] = [
        AbilityStatBinding(StatKey.CAPACITY_MULT, 'max_amount', 'multiply', '_base_max_amount'),
    ]

    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)
        self.resource_type = data.get('resource', '')
        self.max_amount = data.get('amount', 0.0)
        self._base_max_amount = self.max_amount

    def sync_data(self, data: Any):
        super().sync_data(data)
        if isinstance(data, dict):
            self.resource_type = data.get('resource', self.resource_type)
            self.max_amount = data.get('amount', 0.0)
            self._base_max_amount = self.max_amount
        elif isinstance(data, (int, float)):
            self.max_amount = float(data)
            self._base_max_amount = self.max_amount

    def recalculate(self):
        self.max_amount = self._base_max_amount * self.get_effective_stat('capacity_mult', 1.0)

    def get_ui_rows(self):
        color = '#64FFFF'  # Cyan default for caps
        if self.resource_type == 'shield':
            color = '#00FFFF'  # Standard Shield Cyan

        return [{'label': f"{self.resource_type.title()} Cap", 'value': f"{self.max_amount:.0f}", 'color_hint': color}]

    def get_primary_value(self) -> float:
        return self.max_amount


class ResourceGeneration(Ability):
    """
    Ability to generate resources.
    Data: { "resource": "energy", "amount": 10 }
    """

    STAT_BINDINGS: List[AbilityStatBinding] = [
        AbilityStatBinding(StatKey.ENERGY_GEN_MULT, 'rate', 'multiply', '_base_rate'),
    ]

    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)
        self.resource_type = data.get('resource', '')
        self.rate = data.get('amount', 0.0)
        self._base_rate = self.rate

    def sync_data(self, data: Any):
        super().sync_data(data)
        if isinstance(data, dict):
            self.resource_type = data.get('resource', self.resource_type)
            self.rate = data.get('amount', 0.0)
            self._base_rate = self.rate
        elif isinstance(data, (int, float)):
            self.rate = float(data)
            self._base_rate = self.rate

    def recalculate(self):
        self.rate = self._base_rate * self.get_effective_stat('energy_gen_mult', 1.0)

    def get_ui_rows(self):
        color = '#FFFFFF'
        if self.resource_type == 'energy':
            color = '#FFFF00'  # Yellow

        return [{'label': f"{self.resource_type.title()} Gen", 'value': f"{self.rate:.1f}/s", 'color_hint': color}]

    def get_primary_value(self) -> float:
        return self.rate
