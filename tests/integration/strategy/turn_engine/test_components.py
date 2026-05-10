"""Turn engine component tests - auto-disable logic and toggle integration."""
import logging
from game.strategy.engine.turn_engine import TurnEngine
from tests.fixtures.turn_engine import build_test_turn_engine
from game.core.registry import GameRegistries
from unittest.mock import MagicMock

from .conftest import create_mock_ship_instance, create_mock_component_def


class TestAutoDisableLogic:
    """Group 5.3: Auto-Disable Logic Tests"""

    def test_auto_disable_finds_components_with_per_turn_trigger(self):
        """Verify auto-disable finds and disables components with per_turn trigger."""
        # Create mock component with per_turn ability
        mock_comp_def = create_mock_component_def(
            abilities={
                'ResourceConsumption': {
                    'trigger': 'per_turn',
                    'resource': 'energy',
                    'amount': 10
                }
            }
        )

        # Create registries with the mock component
        registries = GameRegistries(
            components={'shield_generator': mock_comp_def},
            modifiers={},
            vehicle_classes={},
            resources={}
        )
        engine = build_test_turn_engine(registries)

        # Create ship with a component that has per_turn energy consumption
        ship = create_mock_ship_instance(
            design_data={
                'name': 'TestShip',
                'layers': {
                    'CORE': [{'id': 'shield_generator'}]
                }
            }
        )
        ship.set_component_enabled = MagicMock()

        engine.resource_engine._auto_disable_components_for_resource(ship, 'energy')

        ship.set_component_enabled.assert_called_once_with('shield_generator', False)

    def test_auto_disable_multiple_components_same_resource(self):
        """Verify multiple components using same resource are all disabled."""
        # Two components use energy, one uses fuel
        mock_energy_comp = create_mock_component_def(
            abilities={
                'ResourceConsumption': {
                    'trigger': 'per_turn',
                    'resource': 'energy',
                    'amount': 5
                }
            }
        )
        mock_fuel_comp = create_mock_component_def(
            abilities={
                'ResourceConsumption': {
                    'trigger': 'per_turn',
                    'resource': 'fuel',
                    'amount': 5
                }
            }
        )

        # Create registries with the mock components
        registries = GameRegistries(
            components={
                'comp_a': mock_energy_comp,
                'comp_b': mock_energy_comp,
                'comp_c': mock_fuel_comp
            },
            modifiers={},
            vehicle_classes={},
            resources={}
        )
        engine = build_test_turn_engine(registries)

        ship = create_mock_ship_instance(
            design_data={
                'name': 'TestShip',
                'layers': {
                    'CORE': [{'id': 'comp_a'}, {'id': 'comp_b'}, {'id': 'comp_c'}]
                }
            }
        )
        ship.set_component_enabled = MagicMock()

        engine.resource_engine._auto_disable_components_for_resource(ship, 'energy')

        # Should disable comp_a and comp_b (energy), not comp_c (fuel)
        calls = ship.set_component_enabled.call_args_list
        assert len(calls) == 2
        disabled_ids = [call[0][0] for call in calls]
        assert 'comp_a' in disabled_ids
        assert 'comp_b' in disabled_ids
        assert 'comp_c' not in disabled_ids

    def test_auto_disable_skips_unregistered_components(self):
        """Verify unregistered components don't cause errors."""
        # Create empty registries - component not registered
        registries = GameRegistries(
            components={},
            modifiers={},
            vehicle_classes={},
            resources={}
        )
        engine = build_test_turn_engine(registries)

        ship = create_mock_ship_instance(
            design_data={
                'name': 'TestShip',
                'layers': {
                    'CORE': [{'id': 'unknown_component'}]
                }
            }
        )
        ship.set_component_enabled = MagicMock()

        # Should not raise exception
        engine.resource_engine._auto_disable_components_for_resource(ship, 'energy')
        ship.set_component_enabled.assert_not_called()

    def test_auto_disable_handles_layer_formats(self):
        """Verify auto-disable handles both list and dict layer formats."""
        mock_comp_def = create_mock_component_def(
            abilities={
                'ResourceConsumption': {
                    'trigger': 'per_turn',
                    'resource': 'energy',
                    'amount': 10
                }
            }
        )

        # Create registries with the mock components
        registries = GameRegistries(
            components={
                'comp_list': mock_comp_def,
                'comp_dict': mock_comp_def
            },
            modifiers={},
            vehicle_classes={},
            resources={}
        )
        engine = build_test_turn_engine(registries)

        # Mixed layer formats
        ship = create_mock_ship_instance(
            design_data={
                'name': 'TestShip',
                'layers': {
                    'CORE': [{'id': 'comp_list'}],
                    'INNER': {'components': [{'id': 'comp_dict'}]}
                }
            }
        )
        ship.set_component_enabled = MagicMock()

        engine.resource_engine._auto_disable_components_for_resource(ship, 'energy')

        # Both formats should be handled
        calls = ship.set_component_enabled.call_args_list
        assert len(calls) == 2
        disabled_ids = [call[0][0] for call in calls]
        assert 'comp_list' in disabled_ids
        assert 'comp_dict' in disabled_ids

    def test_auto_disable_invalidates_stats_cache(self):
        """Verify auto-disable invalidates the ship's stats cache."""
        mock_comp_def = create_mock_component_def(
            abilities={
                'ResourceConsumption': {
                    'trigger': 'per_turn',
                    'resource': 'energy',
                    'amount': 10
                }
            }
        )

        # Create registries with the mock component
        registries = GameRegistries(
            components={'test_comp': mock_comp_def},
            modifiers={},
            vehicle_classes={},
            resources={}
        )
        engine = build_test_turn_engine(registries)

        ship = create_mock_ship_instance(
            design_data={
                'name': 'TestShip',
                'layers': {
                    'CORE': [{'id': 'test_comp'}]
                }
            }
        )

        # Track if invalidate was called via set_component_enabled
        invalidate_called = []
        def tracking_set(comp_id, enabled):
            ship.component_toggles[comp_id] = enabled
            ship._cached_stats = None  # This is what set_component_enabled does
            invalidate_called.append(comp_id)
        ship.set_component_enabled = tracking_set

        # Populate cache first
        ship._cached_stats = {'some': 'cached_data'}

        engine.resource_engine._auto_disable_components_for_resource(ship, 'energy')

        # Cache should be invalidated
        assert ship._cached_stats is None
        assert len(invalidate_called) == 1

    def test_auto_disable_logs_info_message(self, caplog):
        """Verify auto-disable logs an info message for each disabled component."""
        mock_comp_def = create_mock_component_def(
            abilities={
                'ResourceConsumption': {
                    'trigger': 'per_turn',
                    'resource': 'energy',
                    'amount': 10
                }
            }
        )

        # Create registries with the mock component
        registries = GameRegistries(
            components={'shield_gen': mock_comp_def},
            modifiers={},
            vehicle_classes={},
            resources={}
        )
        engine = build_test_turn_engine(registries)

        ship = create_mock_ship_instance(
            name="TestCruiser",
            design_data={
                'name': 'TestCruiser',
                'layers': {
                    'CORE': [{'id': 'shield_gen'}]
                }
            }
        )
        ship.set_component_enabled = MagicMock()

        with caplog.at_level(logging.INFO):
            engine.resource_engine._auto_disable_components_for_resource(ship, 'energy')

            # Check that appropriate log message was created
            assert any('TestCruiser' in record.message and
                      'shield_gen' in record.message and
                      'energy' in record.message
                      for record in caplog.records)


class TestComponentToggleIntegration:
    """Group 5.6: Component Toggle Integration Tests"""

    def test_disabled_component_not_counted_in_stats(self, fresh_registries):
        """Verify toggled-off components don't contribute to aggregated stats.

        Uses the real `standard_engine` component which has a
        `strategic_per_hex` fuel consumption. Disabling it via
        component_toggles should drop its consumption from the
        aggregated resource_consumption_per_hex dict.
        """
        from game.simulation.entities.ship_design_stats import calculate_design_stats

        design_data = {
            'name': 'TestShip',
            'ship_class': 'frigate',
            'layers': {
                'CORE': [{'id': 'standard_engine'}]
            }
        }

        enabled_stats = calculate_design_stats(
            design_data,
            fresh_registries,
            component_toggles={'standard_engine': True},
        )
        disabled_stats = calculate_design_stats(
            design_data,
            fresh_registries,
            component_toggles={'standard_engine': False},
        )

        # Enabled: standard_engine contributes 100 fuel/hex
        assert enabled_stats['resource_consumption_per_hex'].get('fuel', 0) == 100.0

        # Disabled: engine is filtered out of the design before Ship
        # construction, so it contributes nothing
        assert disabled_stats['resource_consumption_per_hex'].get('fuel', 0) == 0.0

    def test_auto_disabled_component_reenabled_via_manual_toggle(self):
        """Verify manually re-enabling an auto-disabled component works."""
        from game.strategy.data.ship_instance import ShipInstance

        ship = ShipInstance(
            instance_id='test-1',
            design_id='TestShip',
            name='TestShip',
            owner_id=0,
            design_data={
                'name': 'TestShip',
                'layers': {'CORE': [{'id': 'shield_gen'}]}
            }
        )

        # Simulate auto-disable
        ship.set_component_enabled('shield_gen', False)
        assert ship.is_component_enabled('shield_gen') is False

        # Manual re-enable
        ship.set_component_enabled('shield_gen', True)
        assert ship.is_component_enabled('shield_gen') is True

        # Verify toggles dict state
        assert ship.component_toggles.get('shield_gen') is True
