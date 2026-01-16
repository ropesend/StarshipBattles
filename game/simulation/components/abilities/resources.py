from typing import Dict, Any

from game.core.config import PhysicsConfig
from .base import Ability


class ResourceConsumption(Ability):
    """
    Ability to consume resources.
    Data: { "resource": "fuel", "amount": 10, "trigger": "constant"|"activation" }
    """
    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)
        self.resource_name = data.get('resource', '')
        self.amount = data.get('amount', 0.0)
        self.trigger = data.get('trigger', 'constant')  # 'constant' or 'activation'

    def sync_data(self, data: Any):
        super().sync_data(data)
        if isinstance(data, dict):
            self.resource_name = data.get('resource', self.resource_name)
            self.amount = data.get('amount', 0.0)
            self.trigger = data.get('trigger', 'constant')
        elif isinstance(data, (int, float)):
            self.amount = float(data)
            self.trigger = 'constant'  # Default for shortcut

    def update(self) -> bool:
        if self.trigger == 'constant':
            # Need access to ship's resources
            if self.component.ship and self.component.ship.resources:
                res = self.component.ship.resources.get_resource(self.resource_name)
                if res:
                    # Constant consumption is per second, multiply by tick duration
                    cost = self.amount * PhysicsConfig.TICK_RATE
                    if not res.consume(cost):
                        return False  # Starvation
                else:
                    if self.amount > 0:
                        return False
        return True

    def check_and_consume(self) -> bool:
        """Explicitly call for one-shot consumption checks."""
        if self.component.ship and self.component.ship.resources:
            res = self.component.ship.resources.get_resource(self.resource_name)
            if res:
                return res.consume(self.amount)
            else:
                return self.amount <= 0
        return False

    def check_available(self) -> bool:
        if self.component.ship and self.component.ship.resources:
            res = self.component.ship.resources.get_resource(self.resource_name)
            if res:
                return res.check(self.amount)
            else:
                return self.amount <= 0
        return False

    def get_ui_rows(self):
        trigger_str = "/s" if self.trigger == 'constant' else "/use"

        # Color mapping based on resource type
        color = '#FFFFFF'
        if self.resource_name == 'fuel':
            color = '#FFA500'  # Orange
        elif self.resource_name == 'energy':
            color = '#64C8FF'  # Light Blue
        elif self.resource_name == 'ammo':
            color = '#C8C832'  # Dirty Yellow

        label_text = f"{self.resource_name.title()} {'Cost' if self.trigger != 'constant' else 'Use'}"
        return [{'label': label_text, 'value': f"{self.amount:.1f}{trigger_str}", 'color_hint': color}]

    def get_primary_value(self) -> float:
        return self.amount


class ResourceStorage(Ability):
    """
    Ability to store resources.
    Data: { "resource": "fuel", "amount": 100 }
    """
    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)
        self.resource_type = data.get('resource', '')
        self.max_amount = data.get('amount', 0.0)

    def sync_data(self, data: Any):
        super().sync_data(data)
        if isinstance(data, dict):
            self.resource_type = data.get('resource', self.resource_type)
            self.max_amount = data.get('amount', 0.0)
        elif isinstance(data, (int, float)):
            self.max_amount = float(data)

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
    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)
        self.resource_type = data.get('resource', '')
        self.rate = data.get('amount', 0.0)

    def sync_data(self, data: Any):
        super().sync_data(data)
        if isinstance(data, dict):
            self.resource_type = data.get('resource', self.resource_type)
            self.rate = data.get('amount', 0.0)
        elif isinstance(data, (int, float)):
            self.rate = float(data)

    def get_ui_rows(self):
        color = '#FFFFFF'
        if self.resource_type == 'energy':
            color = '#FFFF00'  # Yellow

        return [{'label': f"{self.resource_type.title()} Gen", 'value': f"{self.rate:.1f}/s", 'color_hint': color}]

    def get_primary_value(self) -> float:
        return self.rate
