"""
Unit tests for TestLabPanelManager.

Regression test for load_component_callback wiring (PROJ-86 extraction bug).
"""
from unittest.mock import Mock, patch

from game.ui.screens.test_lab.panel_manager import TestLabPanelManager


class TestPanelManagerComponentCallback:
    """Verify panel manager wires the correct data_extractor method."""

    def _make_manager(self):
        """Create a TestLabPanelManager with a mock data_extractor."""
        data_extractor = Mock()
        data_extractor.load_component = Mock(return_value={'id': 'test_comp'})
        test_history = Mock()
        layout = {
            'header_height': 80,
            'category_width': 200,
            'test_list_width': 400,
            'metadata_width': 300,
        }
        return TestLabPanelManager(data_extractor, test_history, layout), data_extractor

    def _make_ship_info(self, name, comp_ids):
        return {
            'ship_name': name,
            'role': 'attacker',
            'ship_data': {'id': name},
            'component_ids': comp_ids,
        }

    @patch('game.ui.screens.test_lab.panel_manager.ComponentPanel')
    @patch('game.ui.screens.test_lab.panel_manager.ShipPanel')
    def test_create_ship_panels_uses_load_component(self, MockShipPanel, MockComponentPanel):
        """Regression: panel_manager must call data_extractor.load_component, not load_component_data."""
        manager, data_extractor = self._make_manager()

        screen = Mock()
        screen._extract_ships_from_scenario.return_value = [
            self._make_ship_info('Ship A', ['comp_1']),
            self._make_ship_info('Ship B', ['comp_2']),
        ]

        manager.create_ship_panels('TEST-001', screen)

        # Verify ComponentPanel was constructed with the correct callback
        for call in MockComponentPanel.call_args_list:
            assert call.kwargs['load_component_callback'] is data_extractor.load_component

    @patch('game.ui.screens.test_lab.panel_manager.ComponentPanel')
    @patch('game.ui.screens.test_lab.panel_manager.TabbedShipPanel')
    def test_create_ship_panels_tabbed_uses_load_component(self, MockTabbedPanel, MockComponentPanel):
        """Regression: tabbed path (3+ ships) must also use load_component."""
        manager, data_extractor = self._make_manager()

        screen = Mock()
        screen._extract_ships_from_scenario.return_value = [
            self._make_ship_info('Ship A', ['comp_1']),
            self._make_ship_info('Ship B', ['comp_2']),
            self._make_ship_info('Ship C', ['comp_3']),
        ]

        manager.create_ship_panels('TEST-001', screen)

        assert MockComponentPanel.call_count == 1
        assert MockComponentPanel.call_args.kwargs['load_component_callback'] is data_extractor.load_component
