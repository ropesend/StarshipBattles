"""
Integration tests for resource system pipeline.

Tests custom resource types, per-turn consumption, and auto-disable chains.
"""

import pytest
import json

from game.core.resources import ResourceCatalog
from game.strategy.data.fleet import Fleet
from game.core.hex_math import HexCoord
from game.strategy.engine.turn_engine import TurnEngine
from tests.fixtures.turn_engine import build_test_turn_engine

from .conftest import create_mock_component, create_test_ship_design, make_ship_instance


class TestCustomResourceTypeFullPipeline:
    """Test loading custom resource and using it through the entire pipeline."""

    def test_custom_resource_type_full_pipeline(self, loaded_registry, singleton_registries, tmp_path):
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

        # Use DI pattern: load data then update registry
        catalog = ResourceCatalog.from_json(str(resources_file))
        for defn in catalog.all_definitions():
            registry.resources[defn.id] = {'id': defn.id, 'name': defn.name}

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
            ],
            registries=singleton_registries,
        )

        # Step 4: Create ship instance (PROJ-211: pass registries for DI)
        ship = make_ship_instance(design_data, registries=singleton_registries)

        # Step 5: Verify resource appears in stats
        stats = ship.get_calculated_stats()
        resource_storage = stats.get('resource_storage', {})

        assert 'plasma' in resource_storage, "Custom resource 'plasma' should appear in storage"
        assert resource_storage['plasma'] == 5000, "Plasma capacity should be 5000"

        # Step 6: Verify consumption works
        # Set initial resource level
        ship.consumable_levels['plasma'] = 5000

        # Consume some plasma
        success = ship.consume_resource('plasma', 1500)
        assert success is True
        assert ship.get_current_resource('plasma') == 3500

        # Try to consume more than available
        success = ship.consume_resource('plasma', 5000)
        assert success is False
        assert ship.get_current_resource('plasma') == 3500  # Unchanged


class TestPerTurnConsumptionAcrossFullTurn:
    """Test per-turn resource consumption spreads correctly across 100 ticks."""

    def test_per_turn_consumption_across_full_turn(self, loaded_registry, singleton_registries):
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
            ],
            registries=singleton_registries,
        )

        # Create ship instance with full energy (PROJ-211: pass registries for DI)
        ship = make_ship_instance(design_data, registries=singleton_registries)
        ship.consumable_levels['energy'] = 10000  # Start at full

        # Create fleet with this ship
        fleet = Fleet(fleet_id=1, owner_id=0, location=HexCoord(0, 0))
        fleet.add_ship(ship)

        # Create mock empire
        class MockEmpire:
            def __init__(self):
                self.fleets = [fleet]

        empires = [MockEmpire()]

        # Run turn engine for 100 ticks
        turn_engine = build_test_turn_engine(loaded_registry)

        for tick in range(1, 101):
            turn_engine.resource_engine.process_per_turn_consumption(tick, empires)

        # Verify exact consumption: 100 energy per turn total
        # 100 ticks * (100/100) = 100 energy consumed
        expected_remaining = 10000 - 100
        actual_remaining = ship.get_current_resource('energy')

        assert actual_remaining == pytest.approx(expected_remaining, abs=0.01), \
            f"Expected {expected_remaining}, got {actual_remaining}"


class TestAutoDisableComponentChainOnResourceDepletion:
    """Test that components are auto-disabled when resources deplete."""

    def test_auto_disable_component_chain_on_resource_depletion(self, loaded_registry, singleton_registries):
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
            ],
            registries=singleton_registries,
        )

        # PROJ-211: pass registries for DI
        ship = make_ship_instance(design_data, registries=singleton_registries)
        # Start with only 30 energy (will deplete before turn ends)
        ship.consumable_levels['energy'] = 30

        # Create fleet
        fleet = Fleet(fleet_id=1, owner_id=0, location=HexCoord(0, 0))
        fleet.add_ship(ship)

        class MockEmpire:
            def __init__(self):
                self.fleets = [fleet]

        empires = [MockEmpire()]
        turn_engine = build_test_turn_engine(loaded_registry)

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


class TestBackwardCompatLoadOldSaveWithoutComponentToggles:
    """Test loading old save games that don't have component_toggles field."""

    def test_backward_compat_load_old_save_without_component_toggles(self, fresh_registries):
        """
        Create ShipInstance.from_dict() with data missing component_toggles,
        verify defaults to empty dict, verify ship still works.
        """
        from game.strategy.data.ship_instance import ShipInstance

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
            'consumable_levels': {'fuel': 25000},
            # Note: component_toggles is intentionally missing
            'is_alive': True,
            'is_derelict': False,
            'experience': 10,
            'kills': 2,
            'battles_survived': 3
        }

        # Load from old format (PROJ-211: pass registries for DI)
        ship = ShipInstance.from_dict(old_save_data, registries=fresh_registries)

        # Verify component_toggles defaults to empty dict
        assert ship.component_toggles == {}, \
            "component_toggles should default to empty dict"

        # Verify ship still works
        assert ship.instance_id == 'test-12345'
        assert ship.name == 'USS Legacy'
        assert ship.current_hp == 800
        assert ship.consumable_levels == {'fuel': 25000}

        # Verify stats calculation works
        stats = ship.get_calculated_stats()
        assert 'max_hp' in stats

        # Verify component toggle methods work
        assert ship.is_component_enabled('any_component') is True  # Default enabled
        ship.set_component_enabled('some_component', False)
        assert ship.is_component_enabled('some_component') is False


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
