"""
Integration tests for PROJ-08: Data-Driven Resource System.

Tests end-to-end functionality of the resource system using real registries
where possible. Verifies resource loading, consumption, component toggling,
and fleet operations.
"""

import pytest
import json
import tempfile
import os
from pathlib import Path
from typing import Dict, Any, List
from dataclasses import dataclass

from game.core.resources import load_resources
from game.core.registry import RegistryManager, get_component_registry
from game.strategy.data.ship_instance import ShipInstance
from game.strategy.data.fleet import Fleet
from game.strategy.data.hex_math import HexCoord
from game.strategy.services.ship_stats_service import ShipStatsService
from game.strategy.engine.turn_engine import TurnEngine
from tests.fixtures.paths import get_data_dir, get_project_root


# -----------------------------------------------------------------------------
# Test Fixtures
# -----------------------------------------------------------------------------

@pytest.fixture
def registry_manager():
    """Get a clean registry manager for each test."""
    mgr = RegistryManager.instance()
    # Store original state
    orig_components = dict(mgr.components)
    orig_resources = dict(mgr.resources)

    yield mgr

    # Restore original state
    mgr.components.clear()
    mgr.components.update(orig_components)
    mgr.resources.clear()
    mgr.resources.update(orig_resources)


@pytest.fixture
def loaded_registry(global_ship_data, registry_manager):
    """
    Registry with real component data loaded.

    Uses the global_ship_data fixture to ensure components are loaded.
    """
    return registry_manager


@dataclass
class MockComponentDef:
    """Mock component definition for testing."""
    id: str
    mass: float
    max_hp: float
    type_str: str
    abilities: Dict[str, Any]


def create_mock_component(
    comp_id: str,
    mass: float = 100,
    max_hp: float = 100,
    comp_type: str = "Generic",
    abilities: Dict[str, Any] = None
) -> MockComponentDef:
    """Create a mock component definition."""
    return MockComponentDef(
        id=comp_id,
        mass=mass,
        max_hp=max_hp,
        type_str=comp_type,
        abilities=abilities or {}
    )


def create_test_ship_design(
    name: str,
    components: List[Dict[str, Any]],
    vehicle_type: str = "Ship"
) -> Dict[str, Any]:
    """Create a test ship design dictionary."""
    return {
        'name': name,
        'vehicle_type': vehicle_type,
        'layers': {
            'CORE': components
        },
        'expected_stats': {}
    }


def make_ship_instance(
    design_data: Dict[str, Any],
    owner_id: int = 0,
    name: str = None
) -> ShipInstance:
    """Create a ShipInstance from design data."""
    return ShipInstance.create(
        design_data=design_data,
        owner_id=owner_id,
        name=name or design_data.get('name', 'Test Ship')
    )


# -----------------------------------------------------------------------------
# Test 1: Custom Resource Type Full Pipeline
# -----------------------------------------------------------------------------

class TestCustomResourceTypeFullPipeline:
    """Test loading custom resource and using it through the entire pipeline."""

    def test_custom_resource_type_full_pipeline(self, loaded_registry, tmp_path):
        """
        Load custom resource from JSON, create component with that resource type,
        create ship with that component, verify resource appears in stats,
        and verify consumption works.
        """
        registry = loaded_registry

        # Step 1: Create custom resource JSON and load it
        custom_resources = {
            "resources": [
                {"id": "fuel"},
                {"id": "energy"},
                {"id": "ammo"},
                {"id": "plasma", "display_name": "Plasma Coolant"}
            ]
        }
        resources_file = tmp_path / "test_resources.json"
        resources_file.write_text(json.dumps(custom_resources))

        load_resources(str(resources_file))

        # Verify custom resource is loaded
        assert 'plasma' in registry.resources

        # Step 2: Create component with custom resource storage
        plasma_tank = create_mock_component(
            comp_id='plasma_tank',
            mass=50,
            max_hp=80,
            comp_type='Tank',
            abilities={
                'ResourceStorage': [
                    {'resource': 'plasma', 'amount': 5000}
                ]
            }
        )
        registry.components['plasma_tank'] = plasma_tank

        # Step 3: Create ship design with that component
        design_data = create_test_ship_design(
            name='Plasma Test Ship',
            components=[
                {'id': 'plasma_tank'}
            ]
        )

        # Step 4: Create ship instance
        ship = make_ship_instance(design_data)

        # Step 5: Verify resource appears in stats
        stats = ship.get_calculated_stats()
        resource_storage = stats.get('resource_storage', {})

        assert 'plasma' in resource_storage, "Custom resource 'plasma' should appear in storage"
        assert resource_storage['plasma'] == 5000, "Plasma capacity should be 5000"

        # Step 6: Verify consumption works
        # Set initial resource level
        ship.resource_levels['plasma'] = 5000

        # Consume some plasma
        success = ship.consume_resource('plasma', 1500)
        assert success is True
        assert ship.get_current_resource('plasma') == 3500

        # Try to consume more than available
        success = ship.consume_resource('plasma', 5000)
        assert success is False
        assert ship.get_current_resource('plasma') == 3500  # Unchanged


# -----------------------------------------------------------------------------
# Test 2: Per-Turn Consumption Across Full Turn
# -----------------------------------------------------------------------------

class TestPerTurnConsumptionAcrossFullTurn:
    """Test per-turn resource consumption spreads correctly across 100 ticks."""

    def test_per_turn_consumption_across_full_turn(self, loaded_registry):
        """
        Create ship with per-turn consumption, run 100 ticks,
        verify exact amount consumed (not more, not less).
        """
        registry = loaded_registry

        # Create component with per-turn consumption
        life_support = create_mock_component(
            comp_id='test_life_support',
            mass=30,
            max_hp=50,
            comp_type='LifeSupport',
            abilities={
                'ResourceConsumption': [
                    {'resource': 'energy', 'amount': 100, 'trigger': 'per_turn'}
                ],
                'ResourceStorage': [
                    {'resource': 'energy', 'amount': 10000}
                ]
            }
        )
        registry.components['test_life_support'] = life_support

        # Create ship design
        design_data = create_test_ship_design(
            name='Life Support Ship',
            components=[
                {'id': 'test_life_support'}
            ]
        )

        # Create ship instance with full energy
        ship = make_ship_instance(design_data)
        ship.resource_levels['energy'] = 10000  # Start at full

        # Create fleet with this ship
        fleet = Fleet(fleet_id=1, owner_id=0, location=HexCoord(0, 0))
        fleet.add_ship_instance(ship)

        # Create mock empire
        class MockEmpire:
            def __init__(self):
                self.fleets = [fleet]

        empires = [MockEmpire()]

        # Run turn engine for 100 ticks
        turn_engine = TurnEngine()

        for tick in range(1, 101):
            turn_engine.resource_engine.process_per_turn_consumption(tick, empires)

        # Verify exact consumption: 100 energy per turn total
        # 100 ticks * (100/100) = 100 energy consumed
        expected_remaining = 10000 - 100
        actual_remaining = ship.get_current_resource('energy')

        assert actual_remaining == pytest.approx(expected_remaining, abs=0.01), \
            f"Expected {expected_remaining}, got {actual_remaining}"


# -----------------------------------------------------------------------------
# Test 3: Auto-Disable Component Chain on Resource Depletion
# -----------------------------------------------------------------------------

class TestAutoDisableComponentChainOnResourceDepletion:
    """Test that components are auto-disabled when resources deplete."""

    def test_auto_disable_component_chain_on_resource_depletion(self, loaded_registry):
        """
        Create ship with per-turn component, deplete resource during ticks,
        verify component auto-disabled and stats recalculated.
        """
        registry = loaded_registry

        # Create component that consumes energy per turn and provides strategic movement
        plasma_engine = create_mock_component(
            comp_id='test_plasma_engine',
            mass=100,
            max_hp=150,
            comp_type='Engine',
            abilities={
                'ResourceConsumption': [
                    {'resource': 'energy', 'amount': 100, 'trigger': 'per_turn'}
                ],
                'StrategicMovement': 100
            }
        )
        registry.components['test_plasma_engine'] = plasma_engine

        # Create energy storage component
        battery = create_mock_component(
            comp_id='test_battery',
            mass=30,
            max_hp=50,
            comp_type='Tank',
            abilities={
                'ResourceStorage': [
                    {'resource': 'energy', 'amount': 50}  # Only 50 energy capacity
                ]
            }
        )
        registry.components['test_battery'] = battery

        # Create ship with both components
        design_data = create_test_ship_design(
            name='Low Energy Ship',
            components=[
                {'id': 'test_plasma_engine'},
                {'id': 'test_battery'}
            ]
        )

        ship = make_ship_instance(design_data)
        # Start with only 30 energy (will deplete before turn ends)
        ship.resource_levels['energy'] = 30

        # Create fleet
        fleet = Fleet(fleet_id=1, owner_id=0, location=HexCoord(0, 0))
        fleet.add_ship_instance(ship)

        class MockEmpire:
            def __init__(self):
                self.fleets = [fleet]

        empires = [MockEmpire()]
        turn_engine = TurnEngine()

        # Component should be enabled initially
        assert ship.is_component_enabled('test_plasma_engine') is True

        # Run ticks until resource depletes
        for tick in range(1, 101):
            turn_engine.resource_engine.process_per_turn_consumption(tick, empires)

        # Verify component was auto-disabled
        assert ship.is_component_enabled('test_plasma_engine') is False, \
            "Engine should be auto-disabled after energy depletion"

        # Verify stats are recalculated (strategic movement should be 0 now)
        ship.invalidate_stats_cache()
        stats = ship.get_calculated_stats()

        # Movement should be 0 because engine is disabled
        assert stats.get('strategic_movement', 0) == 0, \
            "Strategic movement should be 0 with engine disabled"


# -----------------------------------------------------------------------------
# Test 4: Warp Jump Uses Resource Consumption Trigger
# -----------------------------------------------------------------------------

class TestWarpJumpUsesResourceConsumptionTrigger:
    """Test warp drive with ResourceConsumption trigger='warp_jump'."""

    def test_warp_jump_uses_resource_consumption_trigger(self, loaded_registry):
        """
        Create warp drive with ResourceConsumption trigger='warp_jump',
        verify get_warp_resource_costs() returns that resource,
        verify consume_warp_resources() consumes it.
        """
        registry = loaded_registry

        # Create warp drive that consumes plasma on warp
        plasma_warp_drive = create_mock_component(
            comp_id='test_plasma_warp',
            mass=80,
            max_hp=100,
            comp_type='WarpDrive',
            abilities={
                'WarpJump': {
                    'max_tonnage': 5000
                },
                'ResourceConsumption': [
                    {'resource': 'plasma', 'amount': 500, 'trigger': 'warp_jump'},
                    {'resource': 'energy', 'amount': 1000, 'trigger': 'warp_jump'}
                ]
            }
        )
        registry.components['test_plasma_warp'] = plasma_warp_drive

        # Create plasma storage
        plasma_tank = create_mock_component(
            comp_id='test_plasma_storage',
            mass=40,
            max_hp=60,
            comp_type='Tank',
            abilities={
                'ResourceStorage': [
                    {'resource': 'plasma', 'amount': 2000}
                ]
            }
        )
        registry.components['test_plasma_storage'] = plasma_tank

        # Create energy storage
        energy_tank = create_mock_component(
            comp_id='test_energy_storage',
            mass=30,
            max_hp=50,
            comp_type='Tank',
            abilities={
                'ResourceStorage': [
                    {'resource': 'energy', 'amount': 5000}
                ]
            }
        )
        registry.components['test_energy_storage'] = energy_tank

        # Create ship design
        design_data = create_test_ship_design(
            name='Plasma Warp Ship',
            components=[
                {'id': 'test_plasma_warp'},
                {'id': 'test_plasma_storage'},
                {'id': 'test_energy_storage'}
            ]
        )

        ship = make_ship_instance(design_data)
        ship.resource_levels['plasma'] = 2000
        ship.resource_levels['energy'] = 5000

        # Verify get_warp_resource_costs() returns both resources
        warp_costs = ship.get_warp_resource_costs()

        assert 'plasma' in warp_costs, "Warp costs should include plasma"
        assert 'energy' in warp_costs, "Warp costs should include energy"
        assert warp_costs['plasma'] == 500
        assert warp_costs['energy'] == 1000

        # Create fleet and consume warp resources
        fleet = Fleet(fleet_id=1, owner_id=0, location=HexCoord(0, 0))
        fleet.add_ship_instance(ship)

        # Verify consume_warp_resources() works
        success = fleet.consume_warp_resources()
        assert success is True

        # Verify both resources were consumed
        assert ship.get_current_resource('plasma') == 1500
        assert ship.get_current_resource('energy') == 4000


# -----------------------------------------------------------------------------
# Test 5: Movement With Multi-Resource Consumption
# -----------------------------------------------------------------------------

class TestMovementWithMultiResourceConsumption:
    """Test movement consuming multiple resource types per hex."""

    def test_movement_with_multi_resource_consumption(self, loaded_registry):
        """
        Create ship consuming fuel + custom resource per hex,
        move fleet, verify both resources consumed.
        """
        registry = loaded_registry

        # Create custom resource
        registry.resources['coolant'] = {'id': 'coolant'}

        # Create engine that consumes both fuel and coolant
        hybrid_engine = create_mock_component(
            comp_id='test_hybrid_engine',
            mass=100,
            max_hp=120,
            comp_type='Engine',
            abilities={
                'StrategicMovement': 100,
                'ResourceConsumption': [
                    {'resource': 'fuel', 'amount': 100, 'trigger': 'strategic_per_hex'},
                    {'resource': 'coolant', 'amount': 25, 'trigger': 'strategic_per_hex'}
                ]
            }
        )
        registry.components['test_hybrid_engine'] = hybrid_engine

        # Create storage for both resources
        fuel_tank = create_mock_component(
            comp_id='test_fuel_tank',
            mass=40,
            max_hp=80,
            comp_type='Tank',
            abilities={
                'ResourceStorage': [
                    {'resource': 'fuel', 'amount': 50000}
                ]
            }
        )
        registry.components['test_fuel_tank'] = fuel_tank

        coolant_tank = create_mock_component(
            comp_id='test_coolant_tank',
            mass=30,
            max_hp=60,
            comp_type='Tank',
            abilities={
                'ResourceStorage': [
                    {'resource': 'coolant', 'amount': 1000}
                ]
            }
        )
        registry.components['test_coolant_tank'] = coolant_tank

        # Create ship
        design_data = create_test_ship_design(
            name='Hybrid Engine Ship',
            components=[
                {'id': 'test_hybrid_engine'},
                {'id': 'test_fuel_tank'},
                {'id': 'test_coolant_tank'}
            ]
        )

        ship = make_ship_instance(design_data)
        ship.resource_levels['fuel'] = 50000
        ship.resource_levels['coolant'] = 1000

        # Create fleet
        fleet = Fleet(fleet_id=1, owner_id=0, location=HexCoord(0, 0))
        fleet.add_ship_instance(ship)

        # Verify movement resource costs
        costs = fleet.get_movement_resource_costs()
        assert 'fuel' in costs
        assert 'coolant' in costs
        assert costs['fuel'] == 100
        assert costs['coolant'] == 25

        # Move 3 hexes
        success = fleet.consume_movement_resources(3)
        assert success is True

        # Verify both resources consumed
        assert ship.get_current_resource('fuel') == 50000 - (100 * 3)
        assert ship.get_current_resource('coolant') == 1000 - (25 * 3)


# -----------------------------------------------------------------------------
# Test 6: Backward Compatibility - Load Old Save Without Component Toggles
# -----------------------------------------------------------------------------

class TestBackwardCompatLoadOldSaveWithoutComponentToggles:
    """Test loading old save games that don't have component_toggles field."""

    def test_backward_compat_load_old_save_without_component_toggles(self):
        """
        Create ShipInstance.from_dict() with data missing component_toggles,
        verify defaults to empty dict, verify ship still works.
        """
        # Old save format - missing component_toggles
        old_save_data = {
            'instance_id': 'test-12345',
            'design_id': 'destroyer_mk1',
            'name': 'USS Legacy',
            'owner_id': 0,
            'design_data': {
                'name': 'Destroyer Mk1',
                'vehicle_type': 'Ship',
                'layers': {},
                'expected_stats': {
                    'max_hp': 1000,
                    'mass': 2000,
                    'max_fuel': 50000,
                    'strategic_fuel_per_hex': 100
                }
            },
            'current_hp': 800,
            'component_damage': {'engine_0': 50},
            'resource_levels': {'fuel': 25000},
            # Note: component_toggles is intentionally missing
            'is_destroyed': False,
            'is_derelict': False,
            'experience': 10,
            'kills': 2,
            'battles_survived': 3
        }

        # Load from old format
        ship = ShipInstance.from_dict(old_save_data)

        # Verify component_toggles defaults to empty dict
        assert ship.component_toggles == {}, \
            "component_toggles should default to empty dict"

        # Verify ship still works
        assert ship.instance_id == 'test-12345'
        assert ship.name == 'USS Legacy'
        assert ship.current_hp == 800
        assert ship.resource_levels == {'fuel': 25000}

        # Verify stats calculation works
        stats = ship.get_calculated_stats()
        assert 'max_hp' in stats

        # Verify component toggle methods work
        assert ship.is_component_enabled('any_component') is True  # Default enabled
        ship.set_component_enabled('some_component', False)
        assert ship.is_component_enabled('some_component') is False


# -----------------------------------------------------------------------------
# Test 7: Component Toggle Affects Movement and Warp
# -----------------------------------------------------------------------------

class TestComponentToggleAffectsMovementAndWarp:
    """Test that disabling components affects movement and warp capabilities."""

    def test_component_toggle_affects_movement_and_warp(self, loaded_registry):
        """
        Create ship with engine and warp drive,
        disable engine via toggle, verify movement affected,
        disable warp drive, verify warp affected.
        """
        registry = loaded_registry

        # Create engine
        engine = create_mock_component(
            comp_id='test_toggle_engine',
            mass=80,
            max_hp=100,
            comp_type='Engine',
            abilities={
                'StrategicMovement': 100,
                'ResourceConsumption': [
                    {'resource': 'fuel', 'amount': 100, 'trigger': 'strategic_per_hex'}
                ]
            }
        )
        registry.components['test_toggle_engine'] = engine

        # Create warp drive
        warp = create_mock_component(
            comp_id='test_toggle_warp',
            mass=50,
            max_hp=80,
            comp_type='WarpDrive',
            abilities={
                'WarpJump': {
                    'max_tonnage': 5000
                },
                'ResourceConsumption': [
                    {'resource': 'energy', 'amount': 500, 'trigger': 'warp_jump'}
                ]
            }
        )
        registry.components['test_toggle_warp'] = warp

        # Create storage tanks
        fuel_tank = create_mock_component(
            comp_id='test_toggle_fuel',
            mass=40,
            max_hp=80,
            comp_type='Tank',
            abilities={
                'ResourceStorage': [{'resource': 'fuel', 'amount': 50000}]
            }
        )
        registry.components['test_toggle_fuel'] = fuel_tank

        energy_tank = create_mock_component(
            comp_id='test_toggle_energy',
            mass=30,
            max_hp=50,
            comp_type='Tank',
            abilities={
                'ResourceStorage': [{'resource': 'energy', 'amount': 5000}]
            }
        )
        registry.components['test_toggle_energy'] = energy_tank

        # Create ship
        design_data = create_test_ship_design(
            name='Toggle Test Ship',
            components=[
                {'id': 'test_toggle_engine'},
                {'id': 'test_toggle_warp'},
                {'id': 'test_toggle_fuel'},
                {'id': 'test_toggle_energy'}
            ]
        )

        ship = make_ship_instance(design_data)
        ship.resource_levels['fuel'] = 50000
        ship.resource_levels['energy'] = 5000

        # Verify initial stats
        stats = ship.get_calculated_stats()
        assert stats.get('strategic_movement', 0) == 100
        assert stats.get('warp_max_tonnage', 0) == 5000

        per_hex = stats.get('resource_consumption_per_hex', {})
        assert per_hex.get('fuel', 0) == 100

        warp_costs = stats.get('warp_resource_costs', {})
        assert warp_costs.get('energy', 0) == 500

        # Disable engine
        ship.set_component_enabled('test_toggle_engine', False)

        stats_no_engine = ship.get_calculated_stats()
        assert stats_no_engine.get('strategic_movement', 0) == 0, \
            "Movement should be 0 with engine disabled"

        per_hex_no_engine = stats_no_engine.get('resource_consumption_per_hex', {})
        assert per_hex_no_engine.get('fuel', 0) == 0, \
            "Fuel consumption should be 0 with engine disabled"

        # Re-enable engine, disable warp
        ship.set_component_enabled('test_toggle_engine', True)
        ship.set_component_enabled('test_toggle_warp', False)

        stats_no_warp = ship.get_calculated_stats()
        assert stats_no_warp.get('strategic_movement', 0) == 100, \
            "Movement should work with only warp disabled"
        assert stats_no_warp.get('warp_max_tonnage', 0) == 0, \
            "Warp tonnage should be 0 with warp disabled"

        warp_costs_no_warp = stats_no_warp.get('warp_resource_costs', {})
        assert warp_costs_no_warp.get('energy', 0) == 0, \
            "Warp energy cost should be 0 with warp disabled"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
