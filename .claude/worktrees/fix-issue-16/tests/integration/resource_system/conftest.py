"""
Shared fixtures for resource system tests.

PROJ-211: Updated make_ship_instance to use DI.
"""

import pytest
from dataclasses import dataclass
from typing import Dict, Any, List

from game.core.registry import get_default_registry_manager, GameRegistries
from game.strategy.data.ship_instance import ShipInstance


@pytest.fixture
def loaded_registry():
    """
    Registry with real component data loaded.

    # PROJ-195: Legitimate — integration tests that add test components to the
    # default registry manager for full-pipeline testing.
    # ShipInstance.get_calculated_stats() internally uses
    # get_default_registry_provider() which reads from the default manager,
    # so these tests must add components there.

    Relies on reset_game_state (autouse) for isolation.
    That fixture clears, hydrates from SessionRegistryCache,
    and cleans up after each test automatically.
    """
    return get_default_registry_manager()


@pytest.fixture
def singleton_registries(loaded_registry):
    """
    GameRegistries backed by the singleton RegistryManager.

    PROJ-211: Use this when you need GameRegistries that tracks the singleton's
    state (e.g., when dynamically adding components during tests).

    The returned GameRegistries references the singleton's dictionaries directly,
    so any components added to loaded_registry.components will be visible.
    """
    return GameRegistries(
        components=loaded_registry.components,
        modifiers=loaded_registry.modifiers,
        vehicle_classes=loaded_registry.vehicle_classes,
        resources=loaded_registry.resources
    )


@dataclass
class MockComponentDef:
    """Mock component definition for testing.

    Supports clone() so it can be used in component registries that
    Ship.from_dict() iterates via calculate_design_stats().
    """
    id: str
    mass: float
    max_hp: float
    type_str: str
    abilities: Dict[str, Any]

    def clone(self):
        """Return a copy for Ship.from_dict() compatibility."""
        import copy
        return copy.deepcopy(self)


def create_mock_component(
    comp_id: str,
    mass: float = 100,
    max_hp: float = 100,
    comp_type: str = "Generic",
    abilities: Dict[str, Any] = None
):
    """Create a real Component with custom data for integration testing.

    Uses the simulation Component class so Ship.from_dict() and
    calculate_design_stats() work correctly with these components.
    """
    from game.simulation.components.component import Component
    from game.core.registry import get_default_registry_provider
    registries = get_default_registry_provider()
    data = {
        'id': comp_id,
        'name': comp_id,
        'type': comp_type,
        'mass': mass,
        'hp': max_hp,
        'abilities': abilities or {},
    }
    return Component(data, registries=registries)


def create_test_ship_design(
    name: str,
    components: List[Dict[str, Any]],
    vehicle_type: str = "Ship",
    registries: GameRegistries = None,
) -> Dict[str, Any]:
    """Create a test ship design dictionary.

    If registries is provided, builds expected_stats from mock component
    abilities so the design works with calculate_design_stats fallback.
    """
    design = {
        'name': name,
        'vehicle_type': vehicle_type,
        'layers': {
            'CORE': components
        },
    }
    # Build expected_stats from component abilities in the registry
    expected_stats = _build_expected_stats(components, registries)
    design['expected_stats'] = expected_stats
    return design


def _build_expected_stats(
    components: List[Dict[str, Any]],
    registries: GameRegistries = None,
) -> Dict[str, Any]:
    """Build expected_stats from mock component abilities."""
    total_mass = 0.0
    total_hp = 0.0
    resource_storage: Dict[str, float] = {}
    cargo_storage: Dict[str, float] = {}
    warp_resource_costs: Dict[str, float] = {}
    strategic_movement = 0.0
    warp_max_tonnage = 0
    pod_storage_mass = 0.0
    resource_consumption_per_hex: Dict[str, float] = {}
    resource_consumption_per_turn: Dict[str, float] = {}

    comp_registry = registries.components if registries else {}

    for comp_entry in components:
        comp_id = comp_entry.get('id', '')
        comp_def = comp_registry.get(comp_id)
        if comp_def is None:
            continue
        total_mass += getattr(comp_def, 'mass', 0)
        total_hp += getattr(comp_def, 'max_hp', 0)
        abilities = getattr(comp_def, 'abilities', {})

        # ResourceStorage
        for ab in _ability_list(abilities, 'ResourceStorage'):
            rt = ab.get('resource', '')
            amt = ab.get('amount', ab.get('max_amount', 0))
            if rt:
                resource_storage[rt] = resource_storage.get(rt, 0) + float(amt)

        # CargoStorage
        for ab in _ability_list(abilities, 'CargoStorage'):
            ct = ab.get('cargo_type', 'generic')
            cap = ab.get('capacity', 0)
            cargo_storage[ct] = cargo_storage.get(ct, 0) + float(cap)

        # WarpJump
        wj = abilities.get('WarpJump')
        if isinstance(wj, dict):
            tonnage = wj.get('max_tonnage', 0)
            if tonnage > warp_max_tonnage:
                warp_max_tonnage = tonnage

        # ResourceConsumption
        for ab in _ability_list(abilities, 'ResourceConsumption'):
            rt = ab.get('resource', '')
            amt = float(ab.get('amount', 0))
            trigger = ab.get('trigger', 'constant')
            if trigger == 'warp_jump' and rt:
                warp_resource_costs[rt] = warp_resource_costs.get(rt, 0) + amt
            elif trigger == 'strategic_per_hex' and rt:
                resource_consumption_per_hex[rt] = resource_consumption_per_hex.get(rt, 0) + amt
            elif trigger == 'per_turn' and rt:
                resource_consumption_per_turn[rt] = resource_consumption_per_turn.get(rt, 0) + amt

        # StrategicMovement
        sm = abilities.get('StrategicMovement')
        if isinstance(sm, (int, float)):
            strategic_movement += float(sm)
        elif isinstance(sm, dict):
            strategic_movement += float(sm.get('movement_points', sm.get('value', 0)))

        # PodStorage
        ps = abilities.get('PodStorage')
        if isinstance(ps, dict):
            pod_storage_mass += float(ps.get('capacity_mass', 0))

    return {
        'max_hp': int(total_hp),
        'mass': total_mass,
        'resource_storage': resource_storage,
        'cargo_storage': cargo_storage,
        'pod_storage_mass': pod_storage_mass,
        'strategic_movement': strategic_movement,
        'warp_max_tonnage': warp_max_tonnage,
        'warp_resource_costs': warp_resource_costs,
        'resource_consumption_per_hex': resource_consumption_per_hex,
        'resource_consumption_per_turn': resource_consumption_per_turn,
    }


def _ability_list(abilities: Dict, key: str) -> List[Dict]:
    """Get ability as list of dicts."""
    val = abilities.get(key)
    if val is None:
        return []
    if isinstance(val, list):
        return val
    if isinstance(val, dict):
        return [val]
    return []


def make_ship_instance(
    design_data: Dict[str, Any],
    owner_id: int = 0,
    name: str = None,
    registries: GameRegistries = None,
) -> ShipInstance:
    """Create a ShipInstance from design data.

    PROJ-211: Added registries parameter for DI compliance.
    """
    return ShipInstance.create(
        design_data=design_data,
        owner_id=owner_id,
        name=name or design_data.get('name', 'Test Ship'),
        registries=registries
    )
