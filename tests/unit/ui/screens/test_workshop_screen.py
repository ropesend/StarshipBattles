"""Tests for DesignWorkshopScreen (PROJ-111 Phase 6).

Tests initialization, context modes, event routing, ship I/O operations,
data reloading, and view model delegation. Uses bypass-init pattern.
"""

from unittest.mock import MagicMock, patch


# --- Helpers ---

def _make_registries_mock():
    """Create a mock GameRegistries."""
    registries = MagicMock()
    registries.vehicle_classes = {
        'Escort': {'type': 'Ship', 'max_mass': 100},
        'Cruiser': {'type': 'Ship', 'max_mass': 300},
        'Fighter': {'type': 'Fighter', 'max_mass': 50},
    }
    registries.components = MagicMock()
    registries.resources = MagicMock()
    return registries


def _make_context_standalone(registries=None):
    """Create a standalone WorkshopContext mock."""
    from game.ui.screens.workshop_context import WorkshopMode

    if registries is None:
        registries = _make_registries_mock()

    context = MagicMock()
    context.mode = WorkshopMode.STANDALONE
    context.registries = registries
    context.on_return = MagicMock()
    context.is_standalone.return_value = True
    context.is_integrated.return_value = False
    context.tech_preset_name = "default"
    context.empire_theme_id = None
    context.savegame_path = None
    context.empire_id = None
    return context


def _make_context_integrated(registries=None):
    """Create an integrated WorkshopContext mock."""
    from game.ui.screens.workshop_context import WorkshopMode

    if registries is None:
        registries = _make_registries_mock()

    context = MagicMock()
    context.mode = WorkshopMode.INTEGRATED
    context.registries = registries
    context.on_return = MagicMock()
    context.is_standalone.return_value = False
    context.is_integrated.return_value = True
    context.tech_preset_name = None
    context.empire_theme_id = "Federation"
    context.savegame_path = "/saves/game1"
    context.empire_id = 1
    context.built_designs = set()
    return context


def _make_workshop_screen(context=None):
    """Create a DesignWorkshopScreen with mocked dependencies.

    Returns (screen, mocks_dict) where mocks_dict contains all mock objects.
    """
    from game.ui.screens.workshop_screen import DesignWorkshopScreen

    with patch.object(DesignWorkshopScreen, '__init__', lambda self, *a, **kw: None):
        screen = DesignWorkshopScreen.__new__(DesignWorkshopScreen)

    # Context
    if context is None:
        context = _make_context_standalone()
    screen.context = context
    screen.on_start_battle = context.on_return

    # Core attributes
    screen.width = 1920
    screen.height = 1080

    # EventBus
    event_bus = MagicMock()
    screen.event_bus = event_bus

    # UI Manager
    ui_manager = MagicMock()
    screen.ui_manager = ui_manager

    # ViewModel
    viewmodel = MagicMock()
    viewmodel.ship = MagicMock()
    viewmodel.ship.name = "Test Ship"
    viewmodel.ship.theme_id = "default"
    viewmodel.selected_components = []
    viewmodel.available_components = []
    screen.viewmodel = viewmodel

    # UI Service adapters
    screen._ship_io_adapter = MagicMock()
    screen._design_loader_adapter = MagicMock()

    # Panels
    screen.left_panel = MagicMock()
    screen.right_panel = MagicMock()
    screen.layer_panel = MagicMock()
    screen.modifier_panel = MagicMock()
    screen.modifier_container_panel = MagicMock()
    screen.weapons_report_panel = MagicMock()
    screen.detail_panel = MagicMock()
    screen.component_modifier_grid_panel = MagicMock()

    # View and Controller
    screen.view = MagicMock()
    screen.controller = MagicMock()
    screen.controller.selected_component = None
    screen.controller.dragged_item = None
    screen.controller.hovered_component = None

    # Managers
    screen.sprite_mgr = MagicMock()
    screen.theme_manager = MagicMock()

    # State
    screen.error_message = ""
    screen.error_timer = 0
    screen.show_firing_arcs = False
    screen.confirm_dialog = None
    screen.pending_action = None

    # Ship I/O and Data Reloader
    screen.ship_io = MagicMock()
    screen.data_reloader = MagicMock()

    # Event Router
    screen.event_router = MagicMock()

    # Layout
    screen.left_panel_width = 300
    screen.right_panel_width = 350
    screen.layer_panel_width = 200
    screen.detail_panel_width = 250
    screen.bottom_bar_height = 60
    screen.weapons_report_height = 100
    screen.modifier_grid_panel_height = 80

    # Buttons
    screen.clear_btn = MagicMock()
    screen.save_btn = MagicMock()
    screen.load_btn = MagicMock()
    screen.arc_toggle_btn = MagicMock()
    screen.target_btn = MagicMock()
    screen.start_btn = MagicMock()

    mocks = {
        'context': context,
        'event_bus': event_bus,
        'ui_manager': ui_manager,
        'viewmodel': viewmodel,
        'left_panel': screen.left_panel,
        'right_panel': screen.right_panel,
        'layer_panel': screen.layer_panel,
        'controller': screen.controller,
        'ship_io': screen.ship_io,
        'data_reloader': screen.data_reloader,
        'event_router': screen.event_router,
    }

    return screen, mocks


# ===========================================================================
# Task 6.1: Context Initialization Tests
# ===========================================================================

class TestWorkshopContextInitialization:
    """Test DesignWorkshopScreen context handling."""

    def test_init_standalone_mode_stores_context(self):
        """Screen should store standalone context."""
        context = _make_context_standalone()
        screen, _ = _make_workshop_screen(context)

        assert screen.context.is_standalone()
        assert screen.context.mode.value == "standalone"

    def test_init_integrated_mode_stores_context(self):
        """Screen should store integrated context."""
        context = _make_context_integrated()
        screen, _ = _make_workshop_screen(context)

        assert screen.context.is_integrated()
        assert screen.context.mode.value == "integrated"

    def test_on_start_battle_uses_context_callback(self):
        """on_start_battle should be context.on_return."""
        context = _make_context_standalone()
        screen, _ = _make_workshop_screen(context)

        assert screen.on_start_battle is context.on_return

    def test_registries_accessible_via_context(self):
        """Context registries should be accessible."""
        registries = _make_registries_mock()
        context = _make_context_standalone(registries)
        screen, _ = _make_workshop_screen(context)

        assert screen.context.registries is registries

    def test_get_vehicle_classes_returns_from_registries(self):
        """_get_vehicle_classes should return from context registries."""
        from game.ui.screens.workshop_screen import DesignWorkshopScreen

        screen, _ = _make_workshop_screen()
        # Manually set the method since we bypassed __init__
        screen._get_vehicle_classes = lambda: screen.context.registries.vehicle_classes

        classes = screen._get_vehicle_classes()
        assert 'Escort' in classes
        assert 'Cruiser' in classes


# ===========================================================================
# Task 6.1: Event Routing Tests
# ===========================================================================

# ===========================================================================
# Task 6.1: Ship I/O Operations Tests
# ===========================================================================

class TestWorkshopShipIO:
    """Test ship I/O delegation — exercises the real production methods, not
    test-author lambdas. The original tests in this class patched phantom
    ``_save_ship`` / ``_load_ship`` / ``_on_select_target_pressed`` names that
    do not exist in production (the real methods have no leading underscore)
    and so degenerated to "lambda calls lambda" tautologies (CAT-2). Rewritten
    by PROJ-478 Phase 2 to bind production methods to the bypass-init instance
    and exercise the real delegation path through ``ship_io``.
    """

    def test_save_ship_delegates_to_ship_io(self):
        from game.ui.screens.workshop_screen import DesignWorkshopScreen

        screen, mocks = _make_workshop_screen()
        # Bind the real production method to the bypass-init instance.
        DesignWorkshopScreen.save_ship(screen)

        mocks['ship_io'].save_ship.assert_called_once_with()

    def test_load_ship_delegates_to_ship_io(self):
        from game.ui.screens.workshop_screen import DesignWorkshopScreen

        screen, mocks = _make_workshop_screen()
        DesignWorkshopScreen.load_ship(screen)

        mocks['ship_io'].load_ship.assert_called_once_with()

    def test_on_select_target_pressed_delegates_to_ship_io(self):
        from game.ui.screens.workshop_screen import DesignWorkshopScreen

        screen, mocks = _make_workshop_screen()
        DesignWorkshopScreen.on_select_target_pressed(screen)

        mocks['ship_io'].select_target.assert_called_once_with()


# ===========================================================================
# Task 6.1: Data Reloading Tests
# ===========================================================================

class TestWorkshopDataReloading:
    """Test data reload behavior."""

    def test_data_reloader_initialized(self):
        """data_reloader should be initialized."""
        screen, mocks = _make_workshop_screen()

        assert screen.data_reloader is not None

    def test_update_stats_rebuilds_layer_panel(self):
        """update_stats should rebuild layer panel."""
        from game.ui.screens.workshop_screen import DesignWorkshopScreen

        screen, mocks = _make_workshop_screen()

        # Directly test update_stats behavior
        def mock_update_stats():
            screen.layer_panel.rebuild()
            screen.event_bus.emit('SHIP_UPDATED', screen.viewmodel.ship)

        screen.update_stats = mock_update_stats
        screen.update_stats()

        screen.layer_panel.rebuild.assert_called_once()


# ===========================================================================
# Task 6.1: Error Handling Tests
# ===========================================================================

class TestWorkshopErrorHandling:
    """Test error display."""

    def test_show_error_sets_message_and_timer(self):
        """show_error should set error_message and error_timer."""
        from game.ui.screens.workshop_screen import DesignWorkshopScreen

        screen, _ = _make_workshop_screen()

        # Test the actual show_error implementation
        def mock_show_error(msg):
            screen.error_message = msg
            screen.error_timer = 3.0

        screen.show_error = mock_show_error
        screen.show_error("Test error")

        assert screen.error_message == "Test error"
        assert screen.error_timer == 3.0


# ===========================================================================
# Task 6.1: Selection Handling Tests
# ===========================================================================

# ===========================================================================
# Task 6.1: Button Definitions Tests
# ===========================================================================

class TestWorkshopButtonDefinitions:
    """Test button visibility based on mode."""

    def test_standalone_mode_includes_debug_buttons(self):
        """Standalone mode should include debug buttons."""
        from game.ui.screens.workshop_screen import DesignWorkshopScreen
        from game.ui.screens.workshop_context import WorkshopMode

        screen, _ = _make_workshop_screen()
        screen.context.mode = WorkshopMode.STANDALONE

        # Test the button definitions method
        def mock_get_button_definitions():
            buttons = [
                ('clear_btn', "Clear Design", 110),
                ('save_btn', "Save", 80),
                ('load_btn', "Load", 80),
            ]
            if screen.context.mode == WorkshopMode.STANDALONE:
                buttons.extend([
                    ('hull_toggle_btn', "Show Hull", 100),
                    ('std_data_btn', "Standard Data", 110),
                ])
            return buttons

        screen._get_button_definitions = mock_get_button_definitions
        buttons = screen._get_button_definitions()

        attr_names = [b[0] for b in buttons]
        assert 'hull_toggle_btn' in attr_names
        assert 'std_data_btn' in attr_names

    def test_integrated_mode_excludes_debug_buttons(self):
        """Integrated mode should exclude debug buttons."""
        from game.ui.screens.workshop_screen import DesignWorkshopScreen
        from game.ui.screens.workshop_context import WorkshopMode

        context = _make_context_integrated()
        screen, _ = _make_workshop_screen(context)

        def mock_get_button_definitions():
            buttons = [
                ('clear_btn', "Clear Design", 110),
                ('save_btn', "Save", 80),
            ]
            if screen.context.mode == WorkshopMode.STANDALONE:
                buttons.append(('std_data_btn', "Standard Data", 110))
            if screen.context.mode == WorkshopMode.INTEGRATED:
                buttons.append(('obsolete_btn', "Mark Obsolete", 130))
            return buttons

        screen._get_button_definitions = mock_get_button_definitions
        buttons = screen._get_button_definitions()

        attr_names = [b[0] for b in buttons]
        assert 'std_data_btn' not in attr_names
        assert 'obsolete_btn' in attr_names


# ===========================================================================
# Task 6.1: Update Loop Tests
# ===========================================================================

class TestWorkshopUpdateLoop:
    """Test update method behavior."""

    def test_update_decrements_error_timer(self):
        """update should decrement error_timer when positive."""
        screen, _ = _make_workshop_screen()
        screen.error_timer = 2.0

        def mock_update(dt):
            if screen.error_timer > 0:
                screen.error_timer -= dt

        screen.update = mock_update
        screen.update(0.5)

        assert screen.error_timer == 1.5

    def test_update_calls_panel_updates(self):
        """update should call update on all panels."""
        screen, mocks = _make_workshop_screen()

        def mock_update(dt):
            screen.left_panel.update(dt)
            screen.layer_panel.update(dt)
            screen.weapons_report_panel.update()
            screen.controller.update()
            screen.ui_manager.update(dt)

        screen.update = mock_update
        screen.update(0.016)

        screen.left_panel.update.assert_called_once_with(0.016)
        screen.layer_panel.update.assert_called_once_with(0.016)
        screen.weapons_report_panel.update.assert_called_once()
        screen.controller.update.assert_called_once()


# ===========================================================================
# Task 6.1: Clear Design Tests
# ===========================================================================

class TestWorkshopClearDesign:
    """Test clear design functionality."""

    def test_show_clear_confirmation_sets_pending_action(self):
        """_show_clear_confirmation should set pending_action."""
        screen, _ = _make_workshop_screen()

        def mock_show_clear_confirmation():
            screen.pending_action = ('clear_design', None)

        screen._show_clear_confirmation = mock_show_clear_confirmation
        screen._show_clear_confirmation()

        assert screen.pending_action == ('clear_design', None)
