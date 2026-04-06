"""
Planetary facility dataclass.

Extracted from planet.py (PROJ-210) to reduce module size.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any

from game.core.patterns.layer_iterator import iter_components, get_component_id
from game.core.validation_helpers import require_keys
from game.strategy.services.component_inspector import get_component_abilities
from game.strategy.data.component_activation_state import (
    ActivationPhase,
    ComponentActivationState,
)


@dataclass
class PlanetaryFacility:
    """Represents a built complex on a planet."""
    instance_id: str          # Unique ID (uuid)
    design_id: str            # Reference to design file
    name: str                 # Facility name
    design_data: Dict[str, Any]  # Full complex design (from JSON)
    is_operational: bool = True
    construction_queue: List[Dict[str, Any]] = field(default_factory=list)
    consumable_levels: Dict[str, float] = field(default_factory=dict)
    # PROJ-237: Per-component state tracking (e.g., shield active/inactive)
    component_states: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize facility to dict for save games."""
        return {
            'instance_id': self.instance_id,
            'design_id': self.design_id,
            'name': self.name,
            'design_data': self.design_data,
            'is_operational': self.is_operational,
            'construction_queue': list(self.construction_queue),
            'consumable_levels': self.consumable_levels.copy(),
            'component_states': self.component_states.copy() if self.component_states else {},
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'PlanetaryFacility':
        """
        Deserialize facility from dict.

        Args:
            data: Dict with facility data

        Returns:
            Reconstructed PlanetaryFacility

        Raises:
            PersistenceException: If required keys missing
        """
        require_keys(data, ['instance_id', 'design_id', 'name', 'design_data'], 'PlanetaryFacility')
        return cls(
            instance_id=data['instance_id'],
            design_id=data['design_id'],
            name=data['name'],
            design_data=data['design_data'],
            is_operational=data.get('is_operational', True),
            construction_queue=data.get('construction_queue', []),
            consumable_levels=data.get('consumable_levels', data.get('resource_levels', {})),
            component_states=data.get('component_states', {}),
        )

    def is_component_active(self, component_id: str) -> bool:
        """Check if a component is functionally active.

        Uses ComponentActivationState if available, falls back to legacy
        {'active': bool} format for backward compatibility.

        Args:
            component_id: Component identifier (composite key or legacy ID).

        Returns:
            True if the component is fully active (ACTIVE phase).
        """
        state = self.get_activation_state(component_id)
        return state.is_functionally_active

    def set_component_active(self, component_id: str, active: bool) -> None:
        """Set a component's active state (legacy interface).

        Creates a ComponentActivationState in ACTIVE or INACTIVE phase.
        For new code, prefer set_activation_state() directly.

        Args:
            component_id: Component identifier to update.
            active: Whether the component should be active.
        """
        phase = ActivationPhase.ACTIVE if active else ActivationPhase.INACTIVE
        state = ComponentActivationState(phase=phase)
        self.set_activation_state(component_id, state)

    def get_activation_state(self, component_key: str) -> ComponentActivationState:
        """Get the activation state for a component.

        Returns INACTIVE state if the component has no stored state.
        Handles backward compatibility with old {'active': bool} format.

        Args:
            component_key: Composite component key or legacy component ID.

        Returns:
            ComponentActivationState for this component.
        """
        data = self.component_states.get(component_key)
        if data is None:
            return ComponentActivationState()
        if isinstance(data, dict):
            return ComponentActivationState.from_dict(data)
        return ComponentActivationState()

    def set_activation_state(
        self, component_key: str, state: ComponentActivationState
    ) -> None:
        """Store the activation state for a component.

        Args:
            component_key: Composite component key.
            state: The activation state to store.
        """
        self.component_states[component_key] = state.to_dict()

    def get_fuel_storage(self) -> float:
        """Get current fuel level in this facility."""
        return self.consumable_levels.get("fuel", 0.0)

    def get_max_fuel_storage(self, registries) -> float:
        """Calculate max fuel capacity from design_data components.

        Scans all components in the facility's design_data for ResourceStorage
        abilities with resource type 'fuel' and sums their amounts.

        Args:
            registries: GameRegistries with component definitions.

        Returns:
            Total fuel storage capacity.
        """
        total = 0.0
        for comp in iter_components(self.design_data):
            comp_id = get_component_id(comp)
            comp_def = registries.components.get(comp_id)
            if not comp_def:
                continue
            abilities = get_component_abilities(comp_def)
            for storage in (abilities.get('ResourceStorage') or []):
                if isinstance(storage, dict) and storage.get('resource') == "fuel":
                    total += storage.get('amount', 0)
        return total

    def add_fuel(self, amount: float, registries) -> float:
        """Add fuel up to max capacity.

        Args:
            amount: Amount of fuel to add.
            registries: GameRegistries for max capacity lookup.

        Returns:
            Overflow amount that could not be stored.
        """
        max_storage = self.get_max_fuel_storage(registries)
        current = self.get_fuel_storage()
        space = max_storage - current
        added = min(amount, space)
        self.consumable_levels["fuel"] = current + added
        return amount - added

    def withdraw_fuel(self, amount: float) -> float:
        """Withdraw fuel from this facility.

        Args:
            amount: Amount of fuel to withdraw.

        Returns:
            Actual amount withdrawn (may be less than requested).
        """
        current = self.get_fuel_storage()
        withdrawn = min(amount, current)
        self.consumable_levels["fuel"] = current - withdrawn
        return withdrawn

    @property
    def is_shipyard(self) -> bool:
        """Check if this facility is a space shipyard.

        Scans design_data layers for component id 'space_shipyard' or
        SpaceShipyard ability.

        Returns:
            True if the facility is an operational space shipyard.
        """
        if not self.is_operational:
            return False

        for comp in iter_components(self.design_data):
            if isinstance(comp, dict):
                if comp.get("id") == "space_shipyard":
                    return True
                if "SpaceShipyard" in comp.get("abilities", {}):
                    return True
        return False
