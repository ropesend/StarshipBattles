"""Tests for builder I/O integration.

PROJ-43: Updated to use mock _ship_io_adapter instead of patching ShipIO directly.
PROJ-61: Updated to test WorkshopShipIO class directly since workshop_screen now delegates.
"""
from unittest.mock import MagicMock
from game.ui.screens.workshop_ship_io import WorkshopShipIO
from game.ui.screens.workshop_context import WorkshopMode


class TestBuilderIOIntegration:

    def _create_ship_io_standalone(self):
        """Create a WorkshopShipIO configured for standalone mode."""
        context = MagicMock()
        context.mode = WorkshopMode.STANDALONE

        ui_manager = MagicMock()
        ship_io_adapter = MagicMock()
        design_loader_adapter = MagicMock()
        viewmodel = MagicMock()
        viewmodel.ship = MagicMock()
        get_weapons_panel = MagicMock()
        show_error = MagicMock()
        apply_loaded_ship = MagicMock()

        ship_io = WorkshopShipIO(
            context=context,
            ui_manager=ui_manager,
            screen_width=1920,
            screen_height=1080,
            ship_io_adapter=ship_io_adapter,
            design_loader_adapter=design_loader_adapter,
            viewmodel=viewmodel,
            weapons_report_panel_ref=get_weapons_panel,
            show_error_callback=show_error,
            apply_loaded_ship_callback=apply_loaded_ship
        )

        return ship_io, ship_io_adapter, show_error, apply_loaded_ship, viewmodel

    def test_save_ship_success_flow(self):
        """Verify save flow when save is successful."""
        ship_io, adapter, show_error, _, viewmodel = self._create_ship_io_standalone()
        adapter.save_ship.return_value = (True, "Saved successfully")

        ship_io.save_ship()

        # Verify adapter save_ship called
        adapter.save_ship.assert_called_once_with(viewmodel.ship)

        # Verify show_error NOT called (success)
        show_error.assert_not_called()

    def test_save_ship_failure_flow(self):
        """Verify save flow when save fails."""
        ship_io, adapter, show_error, _, viewmodel = self._create_ship_io_standalone()
        adapter.save_ship.return_value = (False, "Permission Denied")

        ship_io.save_ship()

        # Verify error shown
        show_error.assert_called_once_with("Permission Denied")

    def test_load_ship_success_flow(self):
        """Verify load flow when load is successful."""
        mock_new_ship = MagicMock()
        ship_io, adapter, show_error, apply_loaded_ship, _ = self._create_ship_io_standalone()
        adapter.load_ship.return_value = (mock_new_ship, "Loaded successfully")

        ship_io.load_ship()

        # Verify adapter load_ship called with correct dimensions
        adapter.load_ship.assert_called_once_with(1920, 1080)

        # Verify _apply_loaded_ship was called with the loaded ship
        apply_loaded_ship.assert_called_once()
        call_args = apply_loaded_ship.call_args
        assert call_args[0][0] == mock_new_ship  # First arg is the ship
        assert call_args[0][1] == "Loaded successfully"  # Second arg is message

        # Verify no error
        show_error.assert_not_called()

    def test_load_ship_failure_flow(self):
        """Verify load flow when load fails."""
        ship_io, adapter, show_error, apply_loaded_ship, _ = self._create_ship_io_standalone()
        adapter.load_ship.return_value = (None, "Corrupt File")

        ship_io.load_ship()

        # Verify error shown
        show_error.assert_called_once_with("Corrupt File")

        # Verify apply_loaded_ship NOT called
        apply_loaded_ship.assert_not_called()
