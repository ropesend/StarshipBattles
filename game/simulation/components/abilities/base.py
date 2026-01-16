from typing import Dict, Any, List


class Ability:
    """
    Base class for component abilities.
    Abilities represent functional capabilities (Consumption, Storage, Generation, special effects)
    that are data-driven and attached to Components.
    """
    def __init__(self, component, data: Dict[str, Any]):
        self.component = component
        self.data = data
        self._tags = set(data.get('tags', [])) if isinstance(data, dict) else set()
        self.stack_group = data.get('stack_group') if isinstance(data, dict) else None

    def sync_data(self, data: Any):
        """Update internal state when component data changes."""
        self.data = data
        if isinstance(data, dict):
            self._tags = set(data.get('tags', []))
            self.stack_group = data.get('stack_group')
        else:
            pass

    @property
    def tags(self):
        return self._tags

    def update(self) -> bool:
        """
        Called every tick (0.01s).
        Used for constant resource consumption or continuous effects.
        Returns True if operational, False if failed (e.g. starvation).
        """
        return True

    def on_activation(self) -> bool:
        """
        Called when component tries to activate (e.g. fire weapon).
        Used for checking activation costs or conditions.
        Returns True if allowed.
        """
        return True

    def recalculate(self) -> None:
        """
        Called when component stats have changed (e.g. modifiers applied).
        Override to update internal values derived from component stats.
        """
        pass

    def get_primary_value(self) -> float:
        """
        Return the primary numeric value for aggregation.
        Override in subclasses to return the appropriate value (e.g., thrust_force, capacity).
        Marker abilities return 0.0 by default.
        """
        return 0.0

    def get_ui_rows(self) -> List[Dict[str, str]]:
        """
        Return list of UI rows for the capability scanner/details panel.
        Format: [{'label': 'Thrust', 'value': '1500 N', 'color_hint': '#FFFFFF'}]
        """
        return []
