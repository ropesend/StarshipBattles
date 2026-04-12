"""
ShipInstanceSerializer - Serialization for ShipInstance.

Extracted from ShipInstance to separate persistence concerns from core game logic.
Follows OrderSerializer pattern (PROJ-210): static methods, called from ShipInstance facades.

PROJ-234: Extracted as part of ShipInstance god object decomposition.
"""
import copy
import json
import uuid
from typing import Dict, Any, Optional, TYPE_CHECKING

from game.core.validation_helpers import require_keys, validate_non_negative

if TYPE_CHECKING:
    from game.core.registry import GameRegistries
    from game.strategy.data.ship_instance import ShipInstance


class ShipInstanceSerializer:
    """Handles serialization/deserialization/cloning for ShipInstance."""

    @staticmethod
    def to_dict(ship: 'ShipInstance') -> Dict[str, Any]:
        """Serialize a ShipInstance for save game."""
        data = {
            'instance_id': ship.instance_id,
            'design_id': ship.design_id,
            'name': ship.name,
            'owner_id': ship.owner_id,
            'design_data': ship.design_data,
            'current_hp': ship.current_hp,
            'component_damage': ship.component_damage,
            'consumable_levels': ship.consumable_levels,
            'component_toggles': ship.component_toggles,
            'activation_states': ship.activation_states if ship.activation_states else {},
            'is_alive': ship.is_alive,
            'is_derelict': ship.is_derelict,
            'is_operational': ship.is_operational,
            'experience': ship.experience,
            'kills': ship.kills,
            'battles_survived': ship.battles_survived,
            'serial': ship.serial,
        }
        # Only include cargo_contents if non-empty
        if ship.cargo_contents:
            data['cargo_contents'] = ship.cargo_contents
        if ship.carried_items:
            data['carried_items'] = ship.carried_items
        # Design role fields (omit when None for backward compat)
        if ship.design_role is not None:
            data['design_role'] = ship.design_role
        if ship.role_override is not None:
            data['role_override'] = ship.role_override
        # PROJ-269 Phase 2: per-component persistent state.
        if ship.components:
            data['components'] = {
                key: cs.to_dict() for key, cs in ship.components.items()
            }
        return data

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
        registries: Optional['GameRegistries'] = None,
    ) -> 'ShipInstance':
        """
        Deserialize a ShipInstance from save game data.

        Args:
            data: Dict with ship instance data
            registries: GameRegistries for stats calculation. Optional during
                       deserialization but must be set before calling
                       get_calculated_stats().

        Returns:
            Reconstructed ShipInstance

        Raises:
            PersistenceException: If required keys missing or values invalid
        """
        from game.strategy.data.ship_instance import ShipInstance

        require_keys(data, ['instance_id', 'design_id', 'name', 'owner_id'], 'ShipInstance')

        # Validate non-negative numeric fields (if present in data)
        if data.get('current_hp') is not None:
            validate_non_negative(data['current_hp'], 'current_hp', 'ShipInstance')
        if data.get('experience') is not None:
            validate_non_negative(data['experience'], 'experience', 'ShipInstance')
        if data.get('kills') is not None:
            validate_non_negative(data['kills'], 'kills', 'ShipInstance')
        if data.get('battles_survived') is not None:
            validate_non_negative(data['battles_survived'], 'battles_survived', 'ShipInstance')

        instance = ShipInstance(
            instance_id=data['instance_id'],
            design_id=data['design_id'],
            name=data['name'],
            owner_id=data['owner_id'],
            design_data=data.get('design_data', {}),
            current_hp=data.get('current_hp'),
            component_damage=data.get('component_damage', {}),
            consumable_levels=data.get('consumable_levels', data.get('resource_levels', {})),
            component_toggles=data.get('component_toggles', {}),
            activation_states=data.get('activation_states', {}),
            cargo_contents=data.get('cargo_contents', {}),
            carried_items=data.get('carried_items', []),
            is_alive=data.get('is_alive', True),
            is_derelict=data.get('is_derelict', False),
            is_operational=data.get('is_operational', True),
            experience=data.get('experience', 0),
            kills=data.get('kills', 0),
            battles_survived=data.get('battles_survived', 0),
            serial=data.get('serial'),
        )
        instance._registries = registries
        # Restore design role fields (absent in old saves → None)
        instance.design_role = data.get('design_role')
        instance.role_override = data.get('role_override')

        # PROJ-269 Phase 2: restore per-component persistent state.
        # Missing key defaults to empty — legacy saves without
        # `components` gracefully degrade (CLAUDE.md "saves are disposable").
        from game.strategy.data.component_state import ComponentState as _ComponentState
        raw_components = data.get('components', {})
        if raw_components:
            instance.components = {
                key: _ComponentState.from_dict(cs_data)
                for key, cs_data in raw_components.items()
            }
        else:
            instance.components = {}

        return instance

    @staticmethod
    def to_json(ship: 'ShipInstance', indent: int = 2) -> str:
        """Serialize a ShipInstance to JSON string."""
        return json.dumps(ShipInstanceSerializer.to_dict(ship), indent=indent)

    @staticmethod
    def from_json(json_str: str) -> 'ShipInstance':
        """Deserialize a ShipInstance from JSON string."""
        data = json.loads(json_str)
        return ShipInstanceSerializer.from_dict(data)

    @staticmethod
    def clone(ship: 'ShipInstance') -> 'ShipInstance':
        """Create a deep copy of a ShipInstance with a new instance_id."""
        from game.strategy.data.ship_instance import ShipInstance

        return ShipInstance(
            instance_id=str(uuid.uuid4()),
            design_id=ship.design_id,
            name=ship.name,
            owner_id=ship.owner_id,
            design_data=copy.deepcopy(ship.design_data),
            current_hp=ship.current_hp,
            component_damage=copy.deepcopy(ship.component_damage),
            consumable_levels=copy.deepcopy(ship.consumable_levels),
            component_toggles=copy.deepcopy(ship.component_toggles),
            cargo_contents=copy.deepcopy(ship.cargo_contents),
            carried_items=copy.deepcopy(ship.carried_items),
            is_alive=ship.is_alive,
            is_derelict=ship.is_derelict,
            is_operational=ship.is_operational,
            experience=ship.experience,
            kills=ship.kills,
            battles_survived=ship.battles_survived,
            components=copy.deepcopy(ship.components),
        )
