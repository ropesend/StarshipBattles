"""
Tests for ShipStatsCalculator - resource system tests.

PROJ-48: Split from test_ship_stats_calculator.py
Contains: TestGenericDictAccumulators, TestTriggerTypes, TestCustomResources
"""

import pytest

from .conftest import create_mock_registries, MockComponent, make_design_data


class TestGenericDictAccumulators:
    """Tests for generic dict accumulator fields (PROJ-08)."""

    def test_resource_storage_generic_dict_structure(self):
        """resource_storage should be a dict with resource types as keys."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        tank = MockComponent(
            'multi_tank', mass=50, max_hp=100,
            abilities={
                'ResourceStorage': [
                    {'resource': 'fuel', 'max_amount': 5000},
                    {'resource': 'water', 'max_amount': 1000}
                ]
            }
        )
        design_data = make_design_data({'OUTER': ['multi_tank']})

        registries = create_mock_registries(components={'multi_tank': tank})
        service = ShipStatsCalculator(registries=registries)
        stats = service.calculate_stats(design_data, {})

        assert isinstance(stats['resource_storage'], dict)
        assert stats['resource_storage']['fuel'] == 5000
        assert stats['resource_storage']['water'] == 1000

    def test_resource_consumption_per_hex_generic_dict(self):
        """resource_consumption_per_hex should be a dict with resource types."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        engine = MockComponent(
            'advanced_engine', mass=80, max_hp=100,
            abilities={
                'ResourceConsumption': [
                    {'resource': 'fuel', 'amount': 100, 'trigger': 'strategic_per_hex'},
                    {'resource': 'coolant', 'amount': 10, 'trigger': 'strategic_per_hex'}
                ]
            }
        )
        design_data = make_design_data({'OUTER': ['advanced_engine']})

        registries = create_mock_registries(components={'advanced_engine': engine})
        service = ShipStatsCalculator(registries=registries)
        stats = service.calculate_stats(design_data, {})

        assert isinstance(stats['resource_consumption_per_hex'], dict)
        assert stats['resource_consumption_per_hex']['fuel'] == 100
        assert stats['resource_consumption_per_hex']['coolant'] == 10

    def test_resource_consumption_per_turn_generic_dict(self):
        """resource_consumption_per_turn should be a dict with resource types."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        life_support = MockComponent(
            'life_support', mass=30, max_hp=50,
            abilities={
                'ResourceConsumption': [
                    {'resource': 'oxygen', 'amount': 5, 'trigger': 'per_turn'},
                    {'resource': 'food', 'amount': 2, 'trigger': 'per_turn'}
                ]
            }
        )
        design_data = make_design_data({'CORE': ['life_support']})

        registries = create_mock_registries(components={'life_support': life_support})
        service = ShipStatsCalculator(registries=registries)
        stats = service.calculate_stats(design_data, {})

        assert isinstance(stats['resource_consumption_per_turn'], dict)
        assert stats['resource_consumption_per_turn']['oxygen'] == 5
        assert stats['resource_consumption_per_turn']['food'] == 2

    def test_warp_resource_costs_generic_dict(self):
        """warp_resource_costs should be a dict with resource types."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        warp_drive = MockComponent(
            'warp_drive', mass=100, max_hp=100,
            abilities={
                'WarpJump': {'max_tonnage': 5000},
                'ResourceConsumption': [
                    {'resource': 'energy', 'amount': 500, 'trigger': 'warp_jump'},
                    {'resource': 'antimatter', 'amount': 10, 'trigger': 'warp_jump'}
                ]
            }
        )
        design_data = make_design_data({'OUTER': ['warp_drive']})

        registries = create_mock_registries(components={'warp_drive': warp_drive})
        service = ShipStatsCalculator(registries=registries)
        stats = service.calculate_stats(design_data, {})

        assert isinstance(stats['warp_resource_costs'], dict)
        assert stats['warp_resource_costs']['energy'] == 500
        assert stats['warp_resource_costs']['antimatter'] == 10

    def test_multiple_custom_resources_accumulate(self):
        """Multiple components should accumulate custom resources in same dict."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        tank1 = MockComponent(
            'fuel_tank', mass=20, max_hp=50,
            abilities={
                'ResourceStorage': [
                    {'resource': 'fuel', 'max_amount': 3000}
                ]
            }
        )
        tank2 = MockComponent(
            'fuel_tank_2', mass=20, max_hp=50,
            abilities={
                'ResourceStorage': [
                    {'resource': 'fuel', 'max_amount': 2000}
                ]
            }
        )
        design_data = make_design_data({'OUTER': ['fuel_tank', 'fuel_tank_2']})

        registries = create_mock_registries(components={'fuel_tank': tank1, 'fuel_tank_2': tank2})
        service = ShipStatsCalculator(registries=registries)
        stats = service.calculate_stats(design_data, {})

        # Should accumulate: 3000 + 2000 = 5000
        assert stats['resource_storage']['fuel'] == 5000


class TestTriggerTypes:
    """Tests for ResourceConsumption trigger types (PROJ-08)."""

    def test_trigger_strategic_per_hex_accumulates_correctly(self):
        """strategic_per_hex trigger should accumulate in resource_consumption_per_hex."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        engine1 = MockComponent(
            'engine_1', mass=50, max_hp=100,
            abilities={
                'ResourceConsumption': [
                    {'resource': 'fuel', 'amount': 75, 'trigger': 'strategic_per_hex'}
                ]
            }
        )
        engine2 = MockComponent(
            'engine_2', mass=50, max_hp=100,
            abilities={
                'ResourceConsumption': [
                    {'resource': 'fuel', 'amount': 25, 'trigger': 'strategic_per_hex'}
                ]
            }
        )
        design_data = make_design_data({'OUTER': ['engine_1', 'engine_2']})

        registries = create_mock_registries(components={'engine_1': engine1, 'engine_2': engine2})
        service = ShipStatsCalculator(registries=registries)
        stats = service.calculate_stats(design_data, {})

        assert stats['resource_consumption_per_hex']['fuel'] == 100

    def test_trigger_per_turn_accumulates_correctly(self):
        """per_turn trigger should accumulate in resource_consumption_per_turn."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        life_support_1 = MockComponent(
            'ls_1', mass=20, max_hp=50,
            abilities={
                'ResourceConsumption': [
                    {'resource': 'oxygen', 'amount': 10, 'trigger': 'per_turn'}
                ]
            }
        )
        life_support_2 = MockComponent(
            'ls_2', mass=20, max_hp=50,
            abilities={
                'ResourceConsumption': [
                    {'resource': 'oxygen', 'amount': 15, 'trigger': 'per_turn'}
                ]
            }
        )
        design_data = make_design_data({'CORE': ['ls_1', 'ls_2']})

        registries = create_mock_registries(components={'ls_1': life_support_1, 'ls_2': life_support_2})
        service = ShipStatsCalculator(registries=registries)
        stats = service.calculate_stats(design_data, {})

        assert stats['resource_consumption_per_turn']['oxygen'] == 25

    def test_trigger_warp_jump_accumulates_correctly(self):
        """warp_jump trigger should accumulate in warp_resource_costs."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        warp1 = MockComponent(
            'warp_1', mass=60, max_hp=100,
            abilities={
                'WarpJump': {'max_tonnage': 5000},
                'ResourceConsumption': [
                    {'resource': 'energy', 'amount': 300, 'trigger': 'warp_jump'}
                ]
            }
        )
        warp2 = MockComponent(
            'warp_2', mass=60, max_hp=100,
            abilities={
                'WarpJump': {'max_tonnage': 3000},
                'ResourceConsumption': [
                    {'resource': 'energy', 'amount': 200, 'trigger': 'warp_jump'}
                ]
            }
        )
        design_data = make_design_data({'OUTER': ['warp_1', 'warp_2']})

        registries = create_mock_registries(components={'warp_1': warp1, 'warp_2': warp2})
        service = ShipStatsCalculator(registries=registries)
        stats = service.calculate_stats(design_data, {})

        # Energy costs accumulate
        assert stats['warp_resource_costs']['energy'] == 500

    def test_different_triggers_dont_cross_buckets(self):
        """Different trigger types should go into separate buckets."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        multi_consumer = MockComponent(
            'multi', mass=100, max_hp=100,
            abilities={
                'WarpJump': {'max_tonnage': 5000},  # Required for warp_jump trigger to work
                'ResourceConsumption': [
                    {'resource': 'fuel', 'amount': 100, 'trigger': 'strategic_per_hex'},
                    {'resource': 'fuel', 'amount': 50, 'trigger': 'per_turn'},
                    {'resource': 'fuel', 'amount': 200, 'trigger': 'warp_jump'}
                ]
            }
        )
        design_data = make_design_data({'CORE': ['multi']})

        registries = create_mock_registries(components={'multi': multi_consumer})
        service = ShipStatsCalculator(registries=registries)
        stats = service.calculate_stats(design_data, {})

        # Each should be in its own bucket, not mixed
        assert stats['resource_consumption_per_hex']['fuel'] == 100
        assert stats['resource_consumption_per_turn']['fuel'] == 50
        assert stats['warp_resource_costs']['fuel'] == 200

    def test_trigger_per_turn_degrades_with_damage(self):
        """per_turn consumption should degrade with component damage."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        life_support = MockComponent(
            'life_support', mass=30, max_hp=100, damage_threshold=0.3,
            abilities={
                'ResourceConsumption': [
                    {'resource': 'oxygen', 'amount': 100, 'trigger': 'per_turn'}
                ]
            }
        )
        design_data = make_design_data({'CORE': ['life_support']})

        registries = create_mock_registries(components={'life_support': life_support})
        service = ShipStatsCalculator(registries=registries)

        # Full HP
        stats_full = service.calculate_stats(design_data, {})
        assert stats_full['resource_consumption_per_turn']['oxygen'] == 100

        # At 65% HP (50% effectiveness)
        stats_damaged = service.calculate_stats(
            design_data, {'life_support': 65}
        )
        assert abs(stats_damaged['resource_consumption_per_turn']['oxygen'] - 50) < 1

    def test_trigger_warp_jump_requires_full_hp(self):
        """warp_jump consumption requires full HP (warp resource costs are 0 if damaged)."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        # warp_jump trigger now uses warp effectiveness: either 0 (damaged) or 1 (100% HP)
        # If warp drive is damaged, warp_resource_costs should be 0 (no warp possible)
        warp = MockComponent(
            'warp', mass=60, max_hp=100, damage_threshold=0.3,
            abilities={
                'WarpJump': {'max_tonnage': 5000},
                'ResourceConsumption': [
                    {'resource': 'energy', 'amount': 500, 'trigger': 'warp_jump'}
                ]
            }
        )
        design_data = make_design_data({'OUTER': ['warp']})

        registries = create_mock_registries(components={'warp': warp})
        service = ShipStatsCalculator(registries=registries)

        # Full HP - warp works
        stats_full = service.calculate_stats(design_data, {})
        assert stats_full['warp_max_tonnage'] == 5000
        assert stats_full['warp_resource_costs']['energy'] == 500

        # 99% HP - warp drive disabled (0 tonnage)
        # warp_resource_costs should also be 0 (no warp = no cost)
        stats_damaged = service.calculate_stats(
            design_data, {'warp': 99}
        )
        assert stats_damaged['warp_max_tonnage'] == 0
        # When warp is disabled, warp_resource_costs should be empty or 0
        assert stats_damaged['warp_resource_costs'].get('energy', 0) == 0

    def test_trigger_unknown_type_ignored(self):
        """Unknown trigger types should be ignored (no error)."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        comp = MockComponent(
            'strange', mass=50, max_hp=100,
            abilities={
                'ResourceConsumption': [
                    {'resource': 'mystery', 'amount': 999, 'trigger': 'unknown_trigger_type'}
                ]
            }
        )
        design_data = make_design_data({'CORE': ['strange']})

        registries = create_mock_registries(components={'strange': comp})
        service = ShipStatsCalculator(registries=registries)
        stats = service.calculate_stats(design_data, {})

        # Should not appear in any bucket
        assert stats['resource_consumption_per_hex'].get('mystery', 0) == 0
        assert stats['resource_consumption_per_turn'].get('mystery', 0) == 0
        assert stats['warp_resource_costs'].get('mystery', 0) == 0


class TestCustomResources:
    """Tests for custom resource type support (PROJ-08)."""

    def test_custom_resource_type_in_storage(self):
        """Custom resource types should work in ResourceStorage."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        tank = MockComponent(
            'plasma_tank', mass=40, max_hp=80,
            abilities={
                'ResourceStorage': [
                    {'resource': 'plasma', 'max_amount': 2500}
                ]
            }
        )
        design_data = make_design_data({'OUTER': ['plasma_tank']})

        registries = create_mock_registries(components={'plasma_tank': tank})
        service = ShipStatsCalculator(registries=registries)
        stats = service.calculate_stats(design_data, {})

        assert stats['resource_storage']['plasma'] == 2500

    def test_custom_resource_per_hex_consumption(self):
        """Custom resource types should work in per-hex consumption."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        drive = MockComponent(
            'plasma_drive', mass=100, max_hp=100,
            abilities={
                'ResourceConsumption': [
                    {'resource': 'plasma', 'amount': 75, 'trigger': 'strategic_per_hex'}
                ]
            }
        )
        design_data = make_design_data({'OUTER': ['plasma_drive']})

        registries = create_mock_registries(components={'plasma_drive': drive})
        service = ShipStatsCalculator(registries=registries)
        stats = service.calculate_stats(design_data, {})

        assert stats['resource_consumption_per_hex']['plasma'] == 75

    def test_custom_resource_per_turn_consumption(self):
        """Custom resource types should work in per-turn consumption."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        reactor = MockComponent(
            'fusion_reactor', mass=80, max_hp=100,
            abilities={
                'ResourceConsumption': [
                    {'resource': 'deuterium', 'amount': 5, 'trigger': 'per_turn'}
                ]
            }
        )
        design_data = make_design_data({'CORE': ['fusion_reactor']})

        registries = create_mock_registries(components={'fusion_reactor': reactor})
        service = ShipStatsCalculator(registries=registries)
        stats = service.calculate_stats(design_data, {})

        assert stats['resource_consumption_per_turn']['deuterium'] == 5

    def test_custom_resource_warp_costs(self):
        """Custom resource types should work in warp costs."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        warp = MockComponent(
            'exotic_warp', mass=100, max_hp=100,
            abilities={
                'WarpJump': {'max_tonnage': 10000},
                'ResourceConsumption': [
                    {'resource': 'exotic_matter', 'amount': 50, 'trigger': 'warp_jump'}
                ]
            }
        )
        design_data = make_design_data({'OUTER': ['exotic_warp']})

        registries = create_mock_registries(components={'exotic_warp': warp})
        service = ShipStatsCalculator(registries=registries)
        stats = service.calculate_stats(design_data, {})

        assert stats['warp_resource_costs']['exotic_matter'] == 50

    def test_many_different_custom_resources_coexist(self):
        """Many different custom resources should coexist without conflict."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        multi_tank = MockComponent(
            'multi_resource', mass=100, max_hp=100,
            abilities={
                'ResourceStorage': [
                    {'resource': 'fuel', 'max_amount': 1000},
                    {'resource': 'water', 'max_amount': 500},
                    {'resource': 'oxygen', 'max_amount': 300},
                    {'resource': 'food', 'max_amount': 200},
                    {'resource': 'spare_parts', 'max_amount': 100}
                ]
            }
        )
        design_data = make_design_data({'CORE': ['multi_resource']})

        registries = create_mock_registries(components={'multi_resource': multi_tank})
        service = ShipStatsCalculator(registries=registries)
        stats = service.calculate_stats(design_data, {})

        storage = stats['resource_storage']
        assert storage['fuel'] == 1000
        assert storage['water'] == 500
        assert storage['oxygen'] == 300
        assert storage['food'] == 200
        assert storage['spare_parts'] == 100
