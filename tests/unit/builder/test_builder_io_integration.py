"""Tests for builder I/O integration.

PROJ-43: Updated to use mock _ship_io_adapter instead of patching ShipIO directly.
PROJ-61: Updated to test WorkshopShipIO class directly since workshop_screen now delegates.
"""
from unittest.mock import MagicMock, patch
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

    def _create_ship_io_integrated(self):
        """Create a WorkshopShipIO configured for integrated (non-STANDALONE) mode."""
        context = MagicMock()
        context.mode = WorkshopMode.INTEGRATED
        context.savegame_path = "/fake/savegame"
        context.empire_id = "empire_1"

        ui_manager = MagicMock()
        ship_io_adapter = MagicMock()
        design_loader_adapter = MagicMock()
        viewmodel = MagicMock()
        viewmodel.ship = MagicMock()
        weapons_panel = MagicMock()
        get_weapons_panel = MagicMock(return_value=weapons_panel)
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

        return (
            ship_io,
            design_loader_adapter,
            get_weapons_panel,
            weapons_panel,
            show_error,
        )

    def test_select_target_integrated_calls_set_target_on_panel(self):
        """Regression test for issue #16.

        In integrated mode, select_target previously referenced a non-existent
        attribute `_weapons_report_panel_ref`, causing AttributeError when the
        user picked a target. Verify the on_target_selected callback resolves
        the weapons report panel via the stored callable and calls
        `set_target(ship)` on it.
        """
        (
            ship_io,
            design_loader_adapter,
            get_weapons_panel,
            weapons_panel,
            show_error,
        ) = self._create_ship_io_integrated()

        mock_ship = MagicMock()
        mock_ship.name = "TargetShip"
        design_loader_adapter.load_ship_from_design_data.return_value = mock_ship

        # PROJ-434 Phase 2: select_target routes through the per-empire
        # DesignCatalog resolved via context.facade_state. Wire a mock
        # catalog into the catalogs_by_empire map.
        mock_catalog = MagicMock()
        load_result = MagicMock()
        load_result.success = True
        load_result.data = {"design": "data"}
        mock_catalog.load_design_data.return_value = load_result
        ship_io.context.facade_state.session.services.design_catalogs_by_empire = {
            ship_io.context.empire_id: mock_catalog,
        }

        with patch("game.ui.screens.workshop_ship_io.DesignSelectorWindow") as mock_window_cls:
            ship_io.select_target()

            # Capture the on_target_selected callback registered with the selector window.
            assert mock_window_cls.called, "DesignSelectorWindow should have been constructed"
            kwargs = mock_window_cls.call_args.kwargs
            on_target_selected = kwargs["on_select_callback"]

            # Invoke as the selector window would when the user picks a row.
            on_target_selected("some-design-id")

        # The weapons report panel callable must be invoked, and set_target
        # called once on the returned panel with the loaded ship.
        get_weapons_panel.assert_called_once_with()
        weapons_panel.set_target.assert_called_once_with(mock_ship)
        show_error.assert_not_called()
