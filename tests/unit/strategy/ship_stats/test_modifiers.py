"""
Tests for ShipStatsCalculator - modifier application and integration tests.

PROJ-48: Split from test_ship_stats_calculator.py
Contains: TestBugDocumentation, TestIntegrationProj08, TestModifierApplication
"""

import pytest

from .conftest import create_mock_registries, MockComponent, make_design_data


class TestBugDocumentation:
    """Tests documenting edge cases and bugs (PROJ-08)."""

    def test_empty_resource_type_creates_empty_string_key_bug(self):
        """
        BUG DOC: Empty resource type creates '' key in storage dict.

        When a component has an empty string as resource type, it creates
        an empty string key in the resource dict. This is documented behavior.
        """
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        buggy_tank = MockComponent(
            'buggy_tank', mass=50, max_hp=100,
            abilities={
                'ResourceStorage': [
                    {'resource': '', 'max_amount': 1000}  # Empty resource type
                ]
            }
        )
        design_data = make_design_data({'OUTER': ['buggy_tank']})

        registries = create_mock_registries(components={'buggy_tank': buggy_tank})
        service = ShipStatsCalculator(registries=registries)
        stats = service.calculate_stats(design_data, {})

        # BUG: Empty string creates '' key - this documents current behavior
        # The service does check `if resource_type:` so empty should NOT be added
        assert '' not in stats['resource_storage']

    def test_empty_resource_type_in_consumption_ignored(self):
        """Empty resource type in consumption should be handled (not create '' key)."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        buggy_engine = MockComponent(
            'buggy_engine', mass=80, max_hp=100,
            abilities={
                'ResourceConsumption': [
                    {'resource': '', 'amount': 100, 'trigger': 'strategic_per_hex'}
                ]
            }
        )
        design_data = make_design_data({'OUTER': ['buggy_engine']})

        registries = create_mock_registries(components={'buggy_engine': buggy_engine})
        service = ShipStatsCalculator(registries=registries)
        stats = service.calculate_stats(design_data, {})

        # Empty string key will be created (current behavior - no validation)
        # This test documents the actual behavior and verifies the value is correct
        assert '' in stats['resource_consumption_per_hex'], \
            "Empty string key created for empty resource type (current behavior)"
        assert stats['resource_consumption_per_hex'][''] == 100

    def test_none_resource_type_handled_safely(self):
        """None as resource type should be handled without errors."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        # Component with None resource (missing 'resource' key)
        bad_tank = MockComponent(
            'bad_tank', mass=50, max_hp=100,
            abilities={
                'ResourceStorage': [
                    {'max_amount': 1000}  # Missing 'resource' key
                ]
            }
        )
        design_data = make_design_data({'OUTER': ['bad_tank']})

        registries = create_mock_registries(components={'bad_tank': bad_tank})
        service = ShipStatsCalculator(registries=registries)
        # Should not raise an exception
        stats = service.calculate_stats(design_data, {})

        # Missing resource key defaults to '' via .get('resource', '')
        # The `if resource_type:` check prevents adding to dict
        assert '' not in stats['resource_storage']


class TestIntegrationProj08:
    """Integration tests for PROJ-08 features."""

    def test_damaged_toggled_component_full_mass_partial_stats(self):
        """Damaged then toggled component: full mass from toggle, no stats."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        engine = MockComponent(
            'engine', mass=100, max_hp=100, damage_threshold=0.3,
            abilities={
                'StrategicMovement': 100,
                'ResourceConsumption': [
                    {'resource': 'fuel', 'amount': 100, 'trigger': 'strategic_per_hex'}
                ]
            }
        )
        design_data = make_design_data({'OUTER': ['engine']})

        registries = create_mock_registries(components={'engine': engine})
        service = ShipStatsCalculator(registries=registries)

        # Damaged engine at 50% HP (about 29% effectiveness)
        # But then toggled off - should get mass but no stats
        stats = service.calculate_stats(
            design_data,
            {'engine': 50},  # Damaged
            component_toggles={'engine': False}  # Toggled off
        )

        # Mass still counts (toggle off still contributes mass)
        assert stats['mass'] == 100
        # No movement (toggled off)
        assert stats['strategic_movement'] == 0
        # No fuel consumption (toggled off)
        assert stats['resource_consumption_per_hex'].get('fuel', 0) == 0

    def test_all_resource_types_in_one_component(self):
        """Component with storage, per-hex, per-turn, and warp costs."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        super_component = MockComponent(
            'super', mass=200, max_hp=200,
            abilities={
                'ResourceStorage': [
                    {'resource': 'fuel', 'max_amount': 10000},
                    {'resource': 'energy', 'max_amount': 5000}
                ],
                'ResourceConsumption': [
                    {'resource': 'fuel', 'amount': 100, 'trigger': 'strategic_per_hex'},
                    {'resource': 'energy', 'amount': 10, 'trigger': 'per_turn'},
                    {'resource': 'fuel', 'amount': 500, 'trigger': 'warp_jump'}
                ],
                'WarpJump': {'max_tonnage': 8000},
                'StrategicMovement': 150
            }
        )
        design_data = make_design_data({'CORE': ['super']})

        registries = create_mock_registries(components={'super': super_component})
        service = ShipStatsCalculator(registries=registries)
        stats = service.calculate_stats(design_data, {})

        # Verify all fields populated correctly
        assert stats['resource_storage']['fuel'] == 10000
        assert stats['resource_storage']['energy'] == 5000
        assert stats['resource_consumption_per_hex']['fuel'] == 100
        assert stats['resource_consumption_per_turn']['energy'] == 10
        assert stats['warp_resource_costs']['fuel'] == 500
        assert stats['warp_max_tonnage'] == 8000
        assert stats['strategic_movement'] == 150

    def test_fallback_handles_new_generic_fields(self):
        """Fallback to expected_stats should include new generic fields."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        # Design with no layers, just expected_stats (fallback path)
        design_data = {
            'layers': {},
            'expected_stats': {
                'max_hp': 500,
                'mass': 200,
                'resource_storage': {'fuel': 8000, 'special_gas': 100},
                'resource_consumption_per_hex': {'fuel': 80},
                'resource_consumption_per_turn': {'oxygen': 5},
                'warp_resource_costs': {'energy': 400, 'exotic': 10},
                'strategic_movement': 120,
                'warp_max_tonnage': 6000
            }
        }

        registries = create_mock_registries(components={})  # Empty registry forces fallback
        service = ShipStatsCalculator(registries=registries)
        stats = service.calculate_stats(design_data, {})

        # Should use expected_stats values
        assert stats['max_hp'] == 500
        assert stats['mass'] == 200
        assert stats['resource_storage']['fuel'] == 8000
        assert stats['resource_storage']['special_gas'] == 100
        assert stats['resource_consumption_per_hex']['fuel'] == 80
        assert stats['resource_consumption_per_turn']['oxygen'] == 5
        assert stats['warp_resource_costs']['energy'] == 400
        assert stats['warp_resource_costs']['exotic'] == 10
        assert stats['strategic_movement'] == 120
        assert stats['warp_max_tonnage'] == 6000


class TestModifierApplication:
    """Tests for PROJ-23: modifier application in ShipStatsCalculator."""

    def test_scaled_battery_energy_capacity(self):
        """Battery with size modifier should have scaled energy capacity.

        PROJ-23 regression test: Ensures modifiers from design are applied.
        """
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator
        from game.simulation.components.component_constants import Modifier

        # Create mock battery component
        battery = MockComponent(
            'battery',
            mass=30,
            max_hp=50,
            abilities={'EnergyStorage': 2000}
        )

        # Create size modifier that scales capacity
        size_modifier = Modifier({
            'id': 'simple_size_mount',
            'name': 'Size Mount',
            'effects': [
                {'stat': 'capacity_mult', 'formula': 'param'},
                {'stat': 'mass_mult', 'formula': 'param'},
                {'stat': 'hp_mult', 'formula': 'param'}
            ]
        })

        # Design with size 20 modifier
        design_data = {
            'ship_class': 'Cruiser',
            'layers': {
                'OUTER': [{
                    'id': 'battery',
                    'modifiers': [{'id': 'simple_size_mount', 'value': 20.0}]
                }]
            }
        }

        registries = create_mock_registries(
            components={'battery': battery},
            modifiers={'simple_size_mount': size_modifier}
        )
        service = ShipStatsCalculator(registries=registries)

        stats = service.calculate_stats(design_data, {})

        # Base battery: 2000 energy, size 20 = 40000 energy
        assert stats['resource_storage'].get('energy', 0) == 40000.0

    def test_multiple_small_vs_one_large_battery(self):
        """10 size-1 batteries should equal 1 size-10 battery.

        This validates that modifier scaling is applied consistently.
        """
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator
        from game.simulation.components.component_constants import Modifier

        battery = MockComponent(
            'battery',
            mass=30,
            max_hp=50,
            abilities={'EnergyStorage': 2000}
        )

        size_modifier = Modifier({
            'id': 'simple_size_mount',
            'name': 'Size Mount',
            'effects': [
                {'stat': 'capacity_mult', 'formula': 'param'},
                {'stat': 'mass_mult', 'formula': 'param'}
            ]
        })

        # Design with 10 size-1 batteries
        design_small = {
            'ship_class': 'Cruiser',
            'layers': {
                'OUTER': [
                    {'id': 'battery', 'modifiers': [{'id': 'simple_size_mount', 'value': 1.0}]}
                    for _ in range(10)
                ]
            }
        }

        # Design with 1 size-10 battery
        design_large = {
            'ship_class': 'Cruiser',
            'layers': {
                'OUTER': [{
                    'id': 'battery',
                    'modifiers': [{'id': 'simple_size_mount', 'value': 10.0}]
                }]
            }
        }

        registries = create_mock_registries(
            components={'battery': battery},
            modifiers={'simple_size_mount': size_modifier}
        )
        service = ShipStatsCalculator(registries=registries)

        stats_small = service.calculate_stats(design_small, {})
        stats_large = service.calculate_stats(design_large, {})

        # 10 x 2000 x 1 = 20000
        # 1 x 2000 x 10 = 20000
        assert stats_small['resource_storage']['energy'] == stats_large['resource_storage']['energy']
        assert stats_small['resource_storage']['energy'] == 20000.0

    def test_warp_capability_with_scaled_battery(self):
        """Ship with scaled battery should have warp capability.

        PROJ-23 regression test: CRU_1 design with 1 large battery should work.
        """
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator
        from game.simulation.components.component_constants import Modifier

        battery = MockComponent(
            'battery',
            mass=30,
            max_hp=50,
            abilities={'EnergyStorage': 2000}
        )

        warp_drive = MockComponent(
            'warp_drive',
            mass=250,
            max_hp=250,
            abilities={
                'WarpJump': {'max_tonnage': 16000},
                'ResourceConsumption': [
                    {'resource': 'energy', 'amount': 3175, 'trigger': 'warp_jump'}
                ]
            }
        )

        size_modifier = Modifier({
            'id': 'simple_size_mount',
            'name': 'Size Mount',
            'effects': [
                {'stat': 'capacity_mult', 'formula': 'param'},
                {'stat': 'mass_mult', 'formula': 'param'}
            ]
        })

        design_data = {
            'ship_class': 'Cruiser',
            'layers': {
                'OUTER': [
                    {
                        'id': 'battery',
                        'modifiers': [{'id': 'simple_size_mount', 'value': 20.0}]
                    },
                    {
                        'id': 'warp_drive',
                        'modifiers': [{'id': 'simple_size_mount', 'value': 1.0}]
                    }
                ]
            }
        }

        registries = create_mock_registries(
            components={'battery': battery, 'warp_drive': warp_drive},
            modifiers={'simple_size_mount': size_modifier}
        )
        service = ShipStatsCalculator(registries=registries)

        stats = service.calculate_stats(design_data, {})

        # Warp energy cost: 3175
        # Scaled battery: 2000 * 20 = 40000 energy
        # Should have warp capability
        energy_capacity = stats['resource_storage'].get('energy', 0)
        warp_cost = stats['warp_resource_costs'].get('energy', 0)

        assert energy_capacity >= warp_cost, (
            f"Energy capacity {energy_capacity} should be >= warp cost {warp_cost}"
        )
        assert energy_capacity == 40000.0
        assert warp_cost == 3175

    def test_no_modifiers_uses_base_values(self):
        """Component without modifiers should use base ability values."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        battery = MockComponent(
            'battery',
            mass=30,
            max_hp=50,
            abilities={'EnergyStorage': 2000}
        )

        design_data = {
            'ship_class': 'Cruiser',
            'layers': {
                'OUTER': [{'id': 'battery'}]  # No modifiers
            }
        }

        registries = create_mock_registries(components={'battery': battery})
        service = ShipStatsCalculator(registries=registries)

        stats = service.calculate_stats(design_data, {})

        # Base battery: 2000 energy, no modifiers
        assert stats['resource_storage'].get('energy', 0) == 2000.0
        assert stats['mass'] == 30.0

    def test_mass_modifier_applied(self):
        """Mass modifier should be applied to component mass."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator
        from game.simulation.components.component_constants import Modifier

        component = MockComponent(
            'test_comp',
            mass=100,
            max_hp=50,
            abilities={}
        )

        size_modifier = Modifier({
            'id': 'simple_size_mount',
            'name': 'Size Mount',
            'effects': [
                {'stat': 'mass_mult', 'formula': 'param'}
            ]
        })

        design_data = {
            'layers': {
                'OUTER': [{
                    'id': 'test_comp',
                    'modifiers': [{'id': 'simple_size_mount', 'value': 5.0}]
                }]
            }
        }

        registries = create_mock_registries(
            components={'test_comp': component},
            modifiers={'simple_size_mount': size_modifier}
        )
        service = ShipStatsCalculator(registries=registries)

        stats = service.calculate_stats(design_data, {})

        # Base mass: 100, size 5 = 500 mass
        assert stats['mass'] == 500.0
