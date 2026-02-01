"""
Tests for ShipStatsCalculator - component toggle functionality.

PROJ-48: Split from test_ship_stats_calculator.py
"""

import pytest

from .conftest import create_mock_registries, MockComponent, make_design_data


class TestComponentToggles:
    """Tests for component toggle functionality (PROJ-08)."""

    def test_toggled_off_component_mass_still_counted(self):
        """Toggled off components should still contribute mass."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        engine = MockComponent(
            'engine', mass=200, max_hp=100,
            abilities={'StrategicMovement': 100}
        )
        design_data = make_design_data({'OUTER': ['engine']})

        registries = create_mock_registries(components={'engine': engine})
        service = ShipStatsCalculator(registries=registries)
        stats = service.calculate_stats(
            design_data, {}, component_toggles={'engine': False}
        )

        assert stats['mass'] == 200  # Mass still counted

    def test_toggled_off_component_no_hp_contribution(self):
        """Toggled off components should not contribute HP."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        hull = MockComponent('hull', mass=100, max_hp=500)
        design_data = make_design_data({'CORE': ['hull']})

        registries = create_mock_registries(components={'hull': hull})
        service = ShipStatsCalculator(registries=registries)

        # Enabled
        stats_on = service.calculate_stats(design_data, {})
        assert stats_on['max_hp'] == 500

        # Disabled
        stats_off = service.calculate_stats(
            design_data, {}, component_toggles={'hull': False}
        )
        assert stats_off['max_hp'] == 0

    def test_toggled_off_component_no_strategic_movement(self):
        """Toggled off engines should not contribute strategic movement."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        engine = MockComponent(
            'engine', mass=80, max_hp=100,
            abilities={'StrategicMovement': 150}
        )
        design_data = make_design_data({'OUTER': ['engine']})

        registries = create_mock_registries(components={'engine': engine})
        service = ShipStatsCalculator(registries=registries)

        stats_on = service.calculate_stats(design_data, {})
        assert stats_on['strategic_movement'] == 150

        stats_off = service.calculate_stats(
            design_data, {}, component_toggles={'engine': False}
        )
        assert stats_off['strategic_movement'] == 0

    def test_toggled_off_warp_drive_no_warp_capability(self):
        """Toggled off warp drive should contribute no warp capability."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        warp = MockComponent(
            'warp_drive', mass=60, max_hp=100,
            abilities={'WarpJump': {'max_tonnage': 8000, 'energy_cost': 600}}
        )
        design_data = make_design_data({'OUTER': ['warp_drive']})

        registries = create_mock_registries(components={'warp_drive': warp})
        service = ShipStatsCalculator(registries=registries)

        stats_on = service.calculate_stats(design_data, {})
        assert stats_on['warp_max_tonnage'] == 8000

        stats_off = service.calculate_stats(
            design_data, {}, component_toggles={'warp_drive': False}
        )
        assert stats_off['warp_max_tonnage'] == 0

    def test_toggled_off_resource_storage_not_counted(self):
        """Toggled off storage components should not contribute storage capacity."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        tank = MockComponent(
            'fuel_tank', mass=30, max_hp=50,
            abilities={'ResourceStorage': [{'resource': 'fuel', 'amount': 10000}]}
        )
        design_data = make_design_data({'OUTER': ['fuel_tank']})

        registries = create_mock_registries(components={'fuel_tank': tank})
        service = ShipStatsCalculator(registries=registries)

        stats_on = service.calculate_stats(design_data, {})
        assert stats_on['resource_storage']['fuel'] == 10000

        stats_off = service.calculate_stats(
            design_data, {}, component_toggles={'fuel_tank': False}
        )
        assert stats_off['resource_storage'].get('fuel', 0) == 0

    def test_mixed_enabled_disabled_components(self):
        """Mix of enabled and disabled components should calculate correctly."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        engine1 = MockComponent(
            'engine_a', mass=80, max_hp=100,
            abilities={'StrategicMovement': 100}
        )
        engine2 = MockComponent(
            'engine_b', mass=80, max_hp=100,
            abilities={'StrategicMovement': 100}
        )
        design_data = make_design_data({'OUTER': ['engine_a', 'engine_b']})

        registries = create_mock_registries(components={'engine_a': engine1, 'engine_b': engine2})
        service = ShipStatsCalculator(registries=registries)

        stats = service.calculate_stats(
            design_data, {},
            component_toggles={'engine_a': True, 'engine_b': False}
        )

        # Mass from both (80 + 80 = 160)
        assert stats['mass'] == 160
        # Movement only from enabled engine
        assert stats['strategic_movement'] == 100
        # HP only from enabled engine
        assert stats['max_hp'] == 100

    def test_missing_toggle_defaults_to_enabled(self):
        """Components not in toggle dict should default to enabled."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        engine = MockComponent(
            'engine', mass=80, max_hp=100,
            abilities={'StrategicMovement': 100}
        )
        design_data = make_design_data({'OUTER': ['engine']})

        registries = create_mock_registries(components={'engine': engine})
        service = ShipStatsCalculator(registries=registries)

        # Pass empty toggle dict - should default to enabled
        stats = service.calculate_stats(
            design_data, {}, component_toggles={}
        )

        assert stats['strategic_movement'] == 100
        assert stats['max_hp'] == 100

    def test_toggled_off_custom_resource_consumption_not_counted(self):
        """Toggled off components should not contribute resource consumption."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        engine = MockComponent(
            'advanced_engine', mass=100, max_hp=100,
            abilities={
                'StrategicMovement': 200,
                'ResourceConsumption': [
                    {'resource': 'fuel', 'amount': 200, 'trigger': 'strategic_per_hex'},
                    {'resource': 'coolant', 'amount': 50, 'trigger': 'per_turn'}
                ]
            }
        )
        design_data = make_design_data({'OUTER': ['advanced_engine']})

        registries = create_mock_registries(components={'advanced_engine': engine})
        service = ShipStatsCalculator(registries=registries)

        stats_on = service.calculate_stats(design_data, {})
        assert stats_on['resource_consumption_per_hex']['fuel'] == 200
        assert stats_on['resource_consumption_per_turn']['coolant'] == 50

        stats_off = service.calculate_stats(
            design_data, {}, component_toggles={'advanced_engine': False}
        )
        # Should be empty dicts or not have the keys
        assert stats_off['resource_consumption_per_hex'].get('fuel', 0) == 0
        assert stats_off['resource_consumption_per_turn'].get('coolant', 0) == 0
