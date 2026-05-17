"""Tests for CargoQuickDialog (PROJ-100 Phase 4).

Verifies:
- Dialog initialization for unload (drop) direction
- Dialog initialization for load direction
- All button sets slider to max
- Confirm dispatches transfer commands
- Cancel closes dialog
- Empty cargo handling
"""
import pytest
import pygame
import pygame_gui
from unittest.mock import MagicMock, patch
from game.ui.screens.cargo_quick_dialog import CargoQuickDialog
from game.strategy.facade.dto import FleetInfo, PlanetInfo


class TestCargoQuickDialog:
    """Tests for CargoQuickDialog UI and logic."""

    @pytest.fixture
    def mock_manager(self):
        return pygame_gui.UIManager((800, 600))

    @pytest.fixture
    def mock_scene(self):
        scene = MagicMock()
        scene._facade = MagicMock()
        scene.facade = scene._facade  # Public accessor
        return scene

    @pytest.fixture
    def mock_fleet(self):
        fleet = MagicMock()
        fleet.id = 1
        fleet.fleet_id = 1
        fleet.location = (0, 0)
        return fleet

    def test_init_populates_items_for_unload(self, mock_manager, mock_scene, mock_fleet):
        """Dialog with direction='unload' should populate cargo items from fleet data."""
        # Arrange: Fleet with passengers, colony at hex
        mock_fleet_info = MagicMock(spec=FleetInfo)
        mock_fleet_info.passengers_current = 50
        mock_scene._facade.fleets.get.return_value = mock_fleet_info

        # Colony at hex
        mock_colony = MagicMock()
        mock_colony.planet_id = 10
        mock_colony.owner_id = 0
        mock_colony.name = "Colony One"
        mock_scene._facade.planets.at_hex.return_value = [mock_colony]

        # Act
        rect = pygame.Rect(100, 100, 450, 300)
        dialog = CargoQuickDialog(
            rect, mock_manager, mock_fleet, (0, 0), 'unload', mock_scene, window_manager=None
        )

        # Assert
        assert len(dialog.cargo_items) == 1
        assert dialog.cargo_items[0]['type'] == 'passengers'
        assert dialog.cargo_items[0]['max'] == 50
        assert 'Passengers' in dialog.cargo_items[0]['label']

    def test_init_populates_items_for_load(self, mock_manager, mock_scene, mock_fleet):
        """Dialog with direction='load' should populate cargo items from colony data."""
        # Arrange: Colony with population at hex
        mock_colony = MagicMock()
        mock_colony.planet_id = 10
        mock_colony.owner_id = 0
        mock_colony.name = "Terra"
        mock_scene._facade.planets.at_hex.return_value = [mock_colony]

        mock_planet_info = MagicMock(spec=PlanetInfo)
        mock_planet_info.population_details = (
            ("human", 100, 1.0),
            ("vulcan", 25, 0.8)
        )
        mock_scene._facade.planets.get.return_value = mock_planet_info

        # Act
        rect = pygame.Rect(100, 100, 450, 300)
        dialog = CargoQuickDialog(
            rect, mock_manager, mock_fleet, (0, 0), 'load', mock_scene, window_manager=None
        )

        # Assert: Two population types
        assert len(dialog.cargo_items) == 2
        assert any('human' in item['label'] for item in dialog.cargo_items)
        assert any('vulcan' in item['label'] for item in dialog.cargo_items)
        assert dialog.cargo_items[0]['type'] == 'passengers'

    def test_all_button_sets_slider_to_max(self, mock_manager, mock_scene, mock_fleet):
        """Clicking 'All' button should set slider value to maximum."""
        # Arrange: Fleet with passengers
        mock_fleet_info = MagicMock(spec=FleetInfo)
        mock_fleet_info.passengers_current = 75
        mock_scene._facade.fleets.get.return_value = mock_fleet_info

        mock_colony = MagicMock()
        mock_colony.planet_id = 10
        mock_colony.owner_id = 0
        mock_scene._facade.planets.at_hex.return_value = [mock_colony]

        rect = pygame.Rect(100, 100, 450, 300)
        dialog = CargoQuickDialog(
            rect, mock_manager, mock_fleet, (0, 0), 'unload', mock_scene, window_manager=None
        )

        # Verify we have an item
        assert len(dialog.cargo_items) == 1
        item = dialog.cargo_items[0]

        # Act: Simulate button press
        event = pygame.event.Event(
            pygame_gui.UI_BUTTON_PRESSED,
            {'ui_element': item['btn_all']}
        )
        dialog.process_event(event)

        # Assert
        assert item['slider'].get_current_value() == 75

    def test_confirm_dispatches_transfer_commands(self, mock_manager, mock_scene, mock_fleet):
        """Confirming transfer should dispatch IssueTransferCommand via facade."""
        # Arrange
        mock_fleet_info = MagicMock(spec=FleetInfo)
        mock_fleet_info.passengers_current = 80
        mock_scene._facade.fleets.get.return_value = mock_fleet_info

        mock_colony = MagicMock()
        mock_colony.planet_id = 10
        mock_colony.owner_id = 0
        mock_colony.name = "Alpha"
        mock_scene._facade.planets.at_hex.return_value = [mock_colony]

        mock_result = MagicMock()
        mock_result.is_valid = True
        mock_scene._facade.handle_command.return_value = mock_result

        rect = pygame.Rect(100, 100, 450, 300)
        dialog = CargoQuickDialog(
            rect, mock_manager, mock_fleet, (0, 0), 'unload', mock_scene, window_manager=None
        )

        # Set slider to a value
        dialog.cargo_items[0]['slider'].set_current_value(30)

        # Act
        with patch('game.strategy.engine.commands.IssueTransferCommand') as mock_cmd_class:
            mock_cmd_instance = MagicMock()
            mock_cmd_class.return_value = mock_cmd_instance
            event = pygame.event.Event(
                pygame_gui.UI_BUTTON_PRESSED,
                {'ui_element': dialog.btn_confirm}
            )
            dialog.process_event(event)

            # Assert
            mock_cmd_class.assert_called_once_with(
                fleet_id=1,
                planet_id=10,
                cargo_type='passengers',
                direction='unload',
                amount=30,
                species_id=None
            )
            mock_scene._facade.handle_command.assert_called_once()

    def test_confirm_with_max_amount_uses_zero(self, mock_manager, mock_scene, mock_fleet):
        """When slider at max, confirm sends amount=0 (engine convention for 'all')."""
        # Arrange
        mock_fleet_info = MagicMock(spec=FleetInfo)
        mock_fleet_info.passengers_current = 40
        mock_scene._facade.fleets.get.return_value = mock_fleet_info

        mock_colony = MagicMock()
        mock_colony.planet_id = 10
        mock_colony.owner_id = 0
        mock_scene._facade.planets.at_hex.return_value = [mock_colony]

        mock_result = MagicMock()
        mock_result.is_valid = True
        mock_scene._facade.handle_command.return_value = mock_result

        rect = pygame.Rect(100, 100, 450, 300)
        dialog = CargoQuickDialog(
            rect, mock_manager, mock_fleet, (0, 0), 'unload', mock_scene, window_manager=None
        )

        # Set slider to max
        dialog.cargo_items[0]['slider'].set_current_value(40)

        # Act
        with patch('game.strategy.engine.commands.IssueTransferCommand') as mock_cmd_class:
            mock_cmd_instance = MagicMock()
            mock_cmd_class.return_value = mock_cmd_instance
            event = pygame.event.Event(
                pygame_gui.UI_BUTTON_PRESSED,
                {'ui_element': dialog.btn_confirm}
            )
            dialog.process_event(event)

            # Assert: amount=0 for "all"
            mock_cmd_class.assert_called_once()
            call_kwargs = mock_cmd_class.call_args[1]
            assert call_kwargs['amount'] == 0

    def test_cancel_closes_dialog(self, mock_manager, mock_scene, mock_fleet):
        """Clicking cancel should kill the dialog."""
        # Arrange
        mock_fleet_info = MagicMock(spec=FleetInfo)
        mock_fleet_info.passengers_current = 20
        mock_scene._facade.fleets.get.return_value = mock_fleet_info

        mock_colony = MagicMock()
        mock_colony.planet_id = 10
        mock_colony.owner_id = 0
        mock_scene._facade.planets.at_hex.return_value = [mock_colony]

        rect = pygame.Rect(100, 100, 450, 300)
        dialog = CargoQuickDialog(
            rect, mock_manager, mock_fleet, (0, 0), 'unload', mock_scene, window_manager=None
        )

        # Act
        event = pygame.event.Event(
            pygame_gui.UI_BUTTON_PRESSED,
            {'ui_element': dialog.btn_cancel}
        )

        # Check dialog is alive
        assert dialog.alive()

        dialog.process_event(event)

        # Assert: Dialog is killed (not alive)
        assert not dialog.alive()

    def test_empty_cargo_shows_no_items(self, mock_manager, mock_scene, mock_fleet):
        """Dialog with no cargo should show no items and graceful empty state."""
        # Arrange: Fleet with no passengers
        mock_fleet_info = MagicMock(spec=FleetInfo)
        mock_fleet_info.passengers_current = 0
        mock_scene._facade.fleets.get.return_value = mock_fleet_info

        # Colony at hex but fleet has nothing to unload
        mock_colony = MagicMock()
        mock_colony.planet_id = 10
        mock_colony.owner_id = 0
        mock_scene._facade.planets.at_hex.return_value = [mock_colony]

        # Act
        rect = pygame.Rect(100, 100, 450, 300)
        dialog = CargoQuickDialog(
            rect, mock_manager, mock_fleet, (0, 0), 'unload', mock_scene, window_manager=None
        )

        # Assert: No cargo items, but dialog handles it gracefully
        assert len(dialog.cargo_items) == 0
        # Should have the "no items" label
        assert hasattr(dialog, 'lbl_no_items')

    def test_no_colony_for_unload_shows_no_items(self, mock_manager, mock_scene, mock_fleet):
        """Unload at hex without colony should show no items."""
        # Arrange: Fleet with passengers, but no colony at hex
        mock_fleet_info = MagicMock(spec=FleetInfo)
        mock_fleet_info.passengers_current = 50
        mock_scene._facade.fleets.get.return_value = mock_fleet_info

        # No colony (empty list)
        mock_scene._facade.planets.at_hex.return_value = []

        # Act
        rect = pygame.Rect(100, 100, 450, 300)
        dialog = CargoQuickDialog(
            rect, mock_manager, mock_fleet, (0, 0), 'unload', mock_scene, window_manager=None
        )

        # Assert: No cargo items since no colony to unload to
        assert len(dialog.cargo_items) == 0
        assert hasattr(dialog, 'lbl_no_items')

    def test_load_with_no_colony_shows_no_items(self, mock_manager, mock_scene, mock_fleet):
        """Load at hex without colony should show no items message."""
        # Arrange: No colony at hex
        mock_scene._facade.planets.at_hex.return_value = []

        # Act
        rect = pygame.Rect(100, 100, 450, 300)
        dialog = CargoQuickDialog(
            rect, mock_manager, mock_fleet, (0, 0), 'load', mock_scene, window_manager=None
        )

        # Assert
        assert len(dialog.cargo_items) == 0
        assert hasattr(dialog, 'lbl_no_items')
