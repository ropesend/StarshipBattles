"""
Integration tests for fleet operations with resources.

Tests warp jumps, movement with multi-resource consumption, and component toggles.
"""

import pytest

from game.strategy.data.fleet import Fleet
from game.core.hex_math import HexCoord

from .conftest import create_mock_component, create_test_ship_design, make_ship_instance


class TestWarpJumpUsesResourceConsumptionTrigger:
    """Test warp drive with ResourceConsumption trigger='warp_jump'."""

    def test_warp_jump_uses_resource_consumption_trigger(self, loaded_registry, singleton_registries):
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
            ],
            registries=singleton_registries,
        )

        # PROJ-211: pass registries for DI
        ship = make_ship_instance(design_data, registries=singleton_registries)
        ship.consumable_levels['plasma'] = 2000
        ship.consumable_levels['energy'] = 5000

        # Verify get_warp_resource_costs() returns both resources
        warp_costs = ship.get_warp_resource_costs()

        assert 'plasma' in warp_costs, "Warp costs should include plasma"
        assert 'energy' in warp_costs, "Warp costs should include energy"
        assert warp_costs['plasma'] == 500
        assert warp_costs['energy'] == 1000

        # Create fleet and consume warp resources
        fleet = Fleet(fleet_id=1, owner_id=0, location=HexCoord(0, 0))
        fleet.add_ship(ship)

        # Verify consume_warp_resources() works
        success = fleet.resources.consume_warp_resources()
        assert success is True

        # Verify both resources were consumed
        assert ship.get_current_resource('plasma') == 1500
        assert ship.get_current_resource('energy') == 4000


class TestMovementWithMultiResourceConsumption:
    """Test movement consuming multiple resource types per hex."""

    def test_movement_with_multi_resource_consumption(self, loaded_registry, singleton_registries):
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
            ],
            registries=singleton_registries,
        )

        # PROJ-211: pass registries for DI
        ship = make_ship_instance(design_data, registries=singleton_registries)
        ship.consumable_levels['fuel'] = 50000
        ship.consumable_levels['coolant'] = 1000

        # Create fleet
        fleet = Fleet(fleet_id=1, owner_id=0, location=HexCoord(0, 0))
        fleet.add_ship(ship)

        # Verify movement resource costs
        costs = fleet.resources.get_movement_resource_costs()
        assert 'fuel' in costs
        assert 'coolant' in costs
        assert costs['fuel'] == 100
        assert costs['coolant'] == 25

        # Move 3 hexes
        success = fleet.resources.consume_movement_resources(3)
        assert success is True

        # Verify both resources consumed
        assert ship.get_current_resource('fuel') == 50000 - (100 * 3)
        assert ship.get_current_resource('coolant') == 1000 - (25 * 3)


class TestComponentToggleAffectsMovementAndWarp:
    """Test that disabling components affects movement and warp capabilities."""

    def test_component_toggle_affects_movement_and_warp(self, loaded_registry, singleton_registries):
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
            ],
            registries=singleton_registries,
        )

        # PROJ-211: pass registries for DI
        ship = make_ship_instance(design_data, registries=singleton_registries)
        ship.consumable_levels['fuel'] = 50000
        ship.consumable_levels['energy'] = 5000

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
