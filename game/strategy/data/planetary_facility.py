"""
Planetary facility dataclass.

Extracted from planet.py (PROJ-210) to reduce module size.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any

from game.core.error_codes import ErrorCode
from game.core.exceptions import ValidationException
from game.core.patterns.layer_iterator import iter_components, get_component_id
from game.core.validation_helpers import require_keys
from game.strategy.services.component_abilities import get_component_abilities
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
    # FEAT-17: When True (and this facility is a shipyard), ProductionEngine
    # skips ticking this facility's queue — no resource draw, no progress
    # increment. The queue list itself is unaffected and remains reorderable.
    construction_queue_paused: bool = False
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
            'construction_queue_paused': self.construction_queue_paused,
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
            construction_queue_paused=data.get('construction_queue_paused', False),
            consumable_levels=data.get('consumable_levels', {}),
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

    # ------------------------------------------------------------------
    # Generic consumable API
    # ------------------------------------------------------------------
    #
    # ``consumable_levels`` stores per-resource amounts; the four
    # ``*_consumable`` methods below are the canonical entry points.

    def _validate_resource_id(self, resource_id: str) -> None:
        from game.core.resources import ResourceCatalog
        if not ResourceCatalog.from_json().has(resource_id):
            raise ValidationException(
                f"Unknown resource_id: {resource_id!r}",
                code=ErrorCode.RESOURCE_NOT_FOUND.value,
                context={"resource_id": str(resource_id)},
            )

    def get_consumable_storage(self, resource_id: str) -> float:
        """Return the current stored amount of ``resource_id``."""
        return float(self.consumable_levels.get(resource_id, 0.0))

    def get_max_consumable_storage(self, resource_id: str, registries) -> float:
        """Compute max capacity for ``resource_id`` from design_data.

        Scans the facility's design components for ``ResourceStorage``
        ability entries matching ``resource_id`` and sums their
        ``amount`` fields. Unknown resource IDs raise ``ValueError``.
        """
        self._validate_resource_id(resource_id)
        total = 0.0
        for comp in iter_components(self.design_data):
            comp_id = get_component_id(comp)
            comp_def = registries.components.get(comp_id)
            if not comp_def:
                continue
            abilities = get_component_abilities(comp_def)
            for storage in (abilities.get('ResourceStorage') or []):
                if isinstance(storage, dict) and storage.get('resource') == resource_id:
                    total += storage.get('amount', 0)
        return total

    def add_consumable(self, resource_id: str, amount: float, registries) -> float:
        """Add ``amount`` of ``resource_id`` up to max capacity.

        Returns the overflow amount that could not be stored.
        """
        max_storage = self.get_max_consumable_storage(resource_id, registries)
        current = self.get_consumable_storage(resource_id)
        space = max_storage - current
        added = min(amount, space)
        self.consumable_levels[resource_id] = current + added
        return amount - added

    def withdraw_consumable(self, resource_id: str, amount: float) -> float:
        """Withdraw ``amount`` of ``resource_id``; returns actual amount."""
        self._validate_resource_id(resource_id)
        current = self.get_consumable_storage(resource_id)
        withdrawn = min(amount, current)
        self.consumable_levels[resource_id] = current - withdrawn
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
