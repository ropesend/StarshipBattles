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
from game.strategy.data.bay_inventory import BayInventory

if TYPE_CHECKING:
    from game.core.registry import GameRegistries
    from game.strategy.data.ship_instance import ShipInstance


class ShipInstanceSerializer:
    """Handles serialization/deserialization/cloning for ShipInstance."""

    @staticmethod
    def to_dict(ship: 'ShipInstance') -> Dict[str, Any]:
        """Serialize a ShipInstance for save game.

        PROJ-276 Phase 5: `component_damage` is NOT emitted. Per-component
        HP lives under the `components` key as `ComponentState` dicts.
        """
        # PROJ-436 Phase 3d: read consumable / cargo state via the
        # stable manager APIs. Phase 3f flips the durable substrate to
        # ``Container`` and reroutes the manager bodies; this serializer
        # keeps emitting the same ``consumable_levels`` / ``cargo_contents``
        # dict-shaped JSON keys for now — Phase 3f decides the final
        # save-schema name (per CLAUDE.md the old format is disposable
        # so a key rename is acceptable).
        data = {
            'instance_id': ship.instance_id,
            'design_id': ship.design_id,
            'name': ship.name,
            'owner_id': ship.owner_id,
            'design_data': ship.design_data,
            'current_hp': ship.current_hp,
            'consumable_levels': ship._resource_mgr.get_all_levels(),
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
        # Only include cargo_contents if non-empty.
        cargo_snapshot = ship._cargo_mgr.get_all_cargo()
        if cargo_snapshot:
            data['cargo_contents'] = cargo_snapshot
        # PROJ-431 Phase 1f: emit the typed bay_inventory substrate. The
        # legacy ``carried_items`` dict-list shape is no longer the
        # storage surface; the typed BayInventory.to_dict() schema is
        # ``{"bay": [CarriedVehicle.to_dict()...], "pods": [DropPod.to_dict()...]}``.
        if not ship.bay_inventory.is_empty():
            data['bay_inventory'] = ship.bay_inventory.to_dict()
        # Design role fields (omit when None for backward compat)
        if ship.design_role is not None:
            data['design_role'] = ship.design_role
        if ship.role_override is not None:
            data['role_override'] = ship.role_override
        # PROJ-269 Phase 2: per-component persistent state.
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

        require_keys(
            data,
            ['instance_id', 'design_id', 'name', 'owner_id', 'components'],
            'ShipInstance',
        )

        # Validate non-negative numeric fields (if present in data)
        if data.get('current_hp') is not None:
            validate_non_negative(data['current_hp'], 'current_hp', 'ShipInstance')
        if data.get('experience') is not None:
            validate_non_negative(data['experience'], 'experience', 'ShipInstance')
        if data.get('kills') is not None:
            validate_non_negative(data['kills'], 'kills', 'ShipInstance')
        if data.get('battles_survived') is not None:
            validate_non_negative(data['battles_survived'], 'battles_survived', 'ShipInstance')

        # PROJ-431 Phase 1f: typed ``bay_inventory`` is the canonical
        # save payload. Pre-Phase-1f saves used a mixed-shape
        # ``carried_items`` dict list; those saves are disposable per
        # the project's no-migration rule, so we do not migrate the old
        # key.
        bay_inventory_data = data.get('bay_inventory')
        bay_inventory = (
            BayInventory.from_dict(bay_inventory_data)
            if bay_inventory_data is not None
            else BayInventory()
        )

        # PROJ-436 Phase 3f: ``consumable_levels`` and ``cargo_contents``
        # are no longer dataclass fields; pass via the renamed private
        # dataclass fields ``_consumable_levels`` / ``_cargo_contents``.
        # The public property of the same name reads / writes the same
        # dict.
        instance = ShipInstance(
            instance_id=data['instance_id'],
            design_id=data['design_id'],
            name=data['name'],
            owner_id=data['owner_id'],
            design_data=data.get('design_data', {}),
            current_hp=data.get('current_hp'),
            _consumable_levels=data.get('consumable_levels', {}),
            component_toggles=data.get('component_toggles', {}),
            activation_states=data.get('activation_states', {}),
            _cargo_contents=data.get('cargo_contents', {}),
            bay_inventory=bay_inventory,
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
        from game.core.component_state import ComponentState as _ComponentState
        raw_components = data['components']
        instance.components = {
            key: _ComponentState.from_dict(cs_data)
            for key, cs_data in raw_components.items()
        }

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
        """Create a deep copy of a ShipInstance with a new instance_id.

        PROJ-436 Phase 3d: read consumable / cargo state via the stable
        manager APIs so Phase 3f's substrate cutover doesn't have to
        touch this clone path.
        """
        from game.strategy.data.ship_instance import ShipInstance

        # PROJ-436 Phase 3f: see ``from_dict`` comment about the
        # private ``_consumable_levels`` / ``_cargo_contents`` field
        # rename.
        return ShipInstance(
            instance_id=str(uuid.uuid4()),
            design_id=ship.design_id,
            name=ship.name,
            owner_id=ship.owner_id,
            design_data=copy.deepcopy(ship.design_data),
            current_hp=ship.current_hp,
            _consumable_levels=copy.deepcopy(ship._resource_mgr.get_all_levels()),
            component_toggles=copy.deepcopy(ship.component_toggles),
            _cargo_contents=copy.deepcopy(ship._cargo_mgr.get_all_cargo()),
            bay_inventory=copy.deepcopy(ship.bay_inventory),
            is_alive=ship.is_alive,
            is_derelict=ship.is_derelict,
            is_operational=ship.is_operational,
            experience=ship.experience,
            kills=ship.kills,
            battles_survived=ship.battles_survived,
            components=copy.deepcopy(ship.components),
        )
