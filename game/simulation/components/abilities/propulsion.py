from typing import Dict, Any

from .base import Ability


class CombatPropulsion(Ability):
    """Provides Thrust."""
    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)
        # Handle 'val' if primitive shortcut used, else explicit 'value'
        val = data if isinstance(data, (int, float)) else data.get('value', 0)
        self.base_thrust = float(val)
        self.thrust_force = self.base_thrust

    def recalculate(self):
        self.thrust_force = self.base_thrust * self.component.stats.get('thrust_mult', 1.0)

    def get_ui_rows(self):
        return [{'label': 'Thrust', 'value': f"{self.thrust_force:.0f} N", 'color_hint': '#64FF64'}]  # Light Green

    def get_primary_value(self) -> float:
        return self.thrust_force


class ManeuveringThruster(Ability):
    """Provides Rotation."""
    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)
        val = data if isinstance(data, (int, float)) else data.get('value', 0)
        self.base_turn_rate = float(val)
        self.turn_rate = self.base_turn_rate

    def recalculate(self):
        self.turn_rate = self.base_turn_rate * self.component.stats.get('turn_mult', 1.0)

    def get_ui_rows(self):
        return [{'label': 'Turn Speed', 'value': f"{self.turn_rate:.1f} deg/s", 'color_hint': '#64FF96'}]  # Slightly different green

    def get_primary_value(self) -> float:
        return self.turn_rate
