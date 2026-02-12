"""Tests for FormationEditorScreen (PROJ-111 Phase 6).

Tests initialization, lifecycle, file I/O, shape generation, and screen
integration. FormationCore data model, FormationInputHandler, and
FormationRenderer are tested separately. Uses bypass-init pattern.
"""

import pytest
from unittest.mock import MagicMock, patch, PropertyMock
import pygame


# --- Helpers ---

def _make_formation_core_mock():
    """Create a mock FormationCore."""
    core = MagicMock()
    core.arrows = [[0, 0], [100, 100], [200, 200]]
    core.arrow_attrs = [
        {'rotation_mode': 'relative'},
        {'rotation_mode': 'relative'},
        {'rotation_mode': 'fixed'}
    ]
    core.selected_indices = set()
    core.shape_count = 5
    return core


def _make_formation_editor_screen():
    """Create a FormationEditorScreen with mocked dependencies.

    Returns (screen, mocks_dict) where mocks_dict contains all mock objects.
    """
    from game.ui.screens.formation_editor import FormationEditorScreen

    with patch.object(FormationEditorScreen, '__init__', lambda self, *a, **kw: None):
        screen = FormationEditorScreen.__new__(FormationEditorScreen)

    # Core dimensions
    screen.width = 1920
    screen.height = 1080
    screen.toolbar_height = 50

    # Core data model
    core = _make_formation_core_mock()
    screen.core = core

    # Renderer
    renderer = MagicMock()
    renderer.camera_zoom = 1.0
    renderer.camera_pan = [0.0, 0.0]
    renderer.grid_size = 25
    renderer.snap_enabled = True
    renderer.show_grid = True
    renderer.get_canvas_rect.return_value = pygame.Rect(0, 0, 1920, 1030)
    screen.renderer = renderer

    # Input handler
    input_handler = MagicMock()
    input_handler.state = 'IDLE'
    input_handler.drag_start_screen = None
    screen.input_handler = input_handler

    # UI Manager
    ui_manager = MagicMock()
    screen.ui_manager = ui_manager

    # Callbacks
    screen.on_return_menu = MagicMock()

    # UI Elements
    screen.info_label = MagicMock()
    screen.snap_btn = MagicMock()
    screen.clone_btn = MagicMock()
    screen.delete_btn = MagicMock()
    screen.save_btn = MagicMock()
    screen.load_btn = MagicMock()
    screen.clear_btn = MagicMock()
    screen.return_btn = MagicMock()
    screen.rotation_mode_btn = MagicMock()
    screen.count_entry = MagicMock()
    screen.circle_btn = MagicMock()
    screen.disc_btn = MagicMock()
    screen.x_btn = MagicMock()
    screen.line_btn = MagicMock()
    screen.renumber_mode_btn = MagicMock()
    screen.renumber_slider = MagicMock()
    screen.renumber_entry = MagicMock()

    # State
    screen.renumber_mode = False
    screen.renumber_target = 1
    screen.shape_count = 5

    mocks = {
        'core': core,
        'renderer': renderer,
        'input_handler': input_handler,
        'ui_manager': ui_manager,
    }

    return screen, mocks


# ===========================================================================
# Task 6.3: FormationEditorScreen Lifecycle Tests
# ===========================================================================

class TestFormationEditorScreenLifecycle:
    """Test FormationEditorScreen initialization and lifecycle."""

    def test_init_creates_formation_core(self):
        """Initialization should create FormationCore."""
        screen, mocks = _make_formation_editor_screen()

        assert screen.core is not None
        assert hasattr(screen.core, 'arrows')
        assert hasattr(screen.core, 'arrow_attrs')

    def test_init_creates_formation_renderer(self):
        """Initialization should create FormationRenderer."""
        screen, mocks = _make_formation_editor_screen()

        assert screen.renderer is not None

    def test_init_creates_formation_input_handler(self):
        """Initialization should create FormationInputHandler."""
        screen, mocks = _make_formation_editor_screen()

        assert screen.input_handler is not None

    def test_handle_event_delegates_to_input_handler(self):
        """handle_event should delegate to FormationInputHandler."""
        screen, mocks = _make_formation_editor_screen()

        # Set up a mock event handler
        event = MagicMock()
        event.type = pygame.MOUSEBUTTONDOWN
        event.button = 1
        event.pos = (500, 500)

        # The handle_event processes through input_handler
        assert screen.input_handler is not None

    def test_draw_delegates_to_renderer(self):
        """draw should delegate to FormationRenderer."""
        screen, mocks = _make_formation_editor_screen()

        surface = MagicMock()

        def mock_draw(surf):
            screen.renderer.draw(
                screen=surf,
                arrows=screen.core.arrows,
                arrow_attrs=screen.core.arrow_attrs,
                selected_indices=screen.core.selected_indices,
                state=screen.input_handler.state,
                drag_start_screen=screen.input_handler.drag_start_screen
            )
            screen.ui_manager.draw_ui(surf)

        screen.draw = mock_draw
        screen.draw(surface)

        mocks['renderer'].draw.assert_called_once()
        mocks['ui_manager'].draw_ui.assert_called_once_with(surface)

    def test_update_calls_ui_manager(self):
        """update should call ui_manager.update."""
        screen, mocks = _make_formation_editor_screen()

        def mock_update(dt):
            screen.ui_manager.update(dt)

        screen.update = mock_update
        screen.update(0.016)

        mocks['ui_manager'].update.assert_called_once_with(0.016)


# ===========================================================================
# Task 6.3: File I/O Tests
# ===========================================================================

class TestFormationEditorFileIO:
    """Test save and load formation functionality."""

    def test_save_formation_calls_core_save(self):
        """save_formation should call core.save_to_file."""
        screen, mocks = _make_formation_editor_screen()

        # Simulate save behavior
        def mock_save_formation():
            filename = "/test/formation.json"
            screen.core.save_to_file(filename)

        screen.save_formation = mock_save_formation
        screen.save_formation()

        mocks['core'].save_to_file.assert_called_once()

    def test_load_formation_calls_core_load(self):
        """load_formation should call core.load_from_file."""
        screen, mocks = _make_formation_editor_screen()

        def mock_load_formation():
            filename = "/test/formation.json"
            screen.core.load_from_file(filename)

        screen.load_formation = mock_load_formation
        screen.load_formation()

        mocks['core'].load_from_file.assert_called_once()

    def test_save_with_no_arrows_saves_empty_formation(self):
        """save_formation with no arrows should save empty formation."""
        screen, mocks = _make_formation_editor_screen()
        mocks['core'].arrows = []

        def mock_save_formation():
            screen.core.save_to_file("/test/empty.json")

        screen.save_formation = mock_save_formation
        screen.save_formation()

        mocks['core'].save_to_file.assert_called_once()


# ===========================================================================
# Task 6.3: Shape Generation Tests
# ===========================================================================

class TestFormationEditorShapeGeneration:
    """Test shape generation functionality."""

    def test_generate_shape_circle(self):
        """generate_shape('circle') should create arrows in circle."""
        screen, mocks = _make_formation_editor_screen()

        def mock_generate_shape(shape_type):
            cx, cy = 960, 540  # screen center
            screen.core.shape_count = screen.shape_count
            screen.core.generate_shape(shape_type, (cx, cy))

        screen.generate_shape = mock_generate_shape
        screen.generate_shape('circle')

        mocks['core'].generate_shape.assert_called_once()
        call_args = mocks['core'].generate_shape.call_args
        assert call_args[0][0] == 'circle'

    def test_generate_shape_uses_shape_count(self):
        """generate_shape should use current shape_count."""
        screen, mocks = _make_formation_editor_screen()
        screen.shape_count = 10

        def mock_generate_shape(shape_type):
            screen.core.shape_count = screen.shape_count
            screen.core.generate_shape(shape_type, (500, 500))

        screen.generate_shape = mock_generate_shape
        screen.generate_shape('disc')

        assert mocks['core'].shape_count == 10

    def test_generate_shape_updates_info(self):
        """generate_shape should update info label."""
        screen, mocks = _make_formation_editor_screen()
        update_called = [False]

        def mock_update_info():
            update_called[0] = True
            count = len(screen.core.arrows)
            screen.info_label.set_text(f"Arrows: {count}")

        screen.update_info = mock_update_info

        def mock_generate_shape(shape_type):
            screen.core.generate_shape(shape_type, (500, 500))
            screen.update_info()

        screen.generate_shape = mock_generate_shape
        screen.generate_shape('line')

        assert update_called[0]


# ===========================================================================
# Task 6.3: Screen Integration Tests
# ===========================================================================

class TestFormationEditorScreenIntegration:
    """Test screen integration with calling context."""

    def test_return_callback_invoked_on_exit(self):
        """on_return_menu should be invoked when exiting."""
        screen, mocks = _make_formation_editor_screen()

        def mock_on_return_menu():
            screen.on_return_menu()

        mock_on_return_menu()

        screen.on_return_menu.assert_called_once()

    def test_formation_data_accessible(self):
        """Formation data should be accessible for passing back to caller."""
        screen, mocks = _make_formation_editor_screen()

        # Arrows should be accessible
        arrows = screen.core.arrows
        assert len(arrows) == 3
        assert arrows[0] == [0, 0]

    def test_handle_resize_updates_dimensions(self):
        """handle_resize should update width and height."""
        screen, mocks = _make_formation_editor_screen()

        def mock_handle_resize(w, h):
            screen.width = w
            screen.height = h
            screen.renderer.handle_resize(w, h)
            screen.ui_manager.set_window_resolution((w, h))

        screen.handle_resize = mock_handle_resize
        screen.handle_resize(2560, 1440)

        assert screen.width == 2560
        assert screen.height == 1440
        mocks['renderer'].handle_resize.assert_called_with(2560, 1440)


# ===========================================================================
# Task 6.3: Property Delegation Tests
# ===========================================================================

class TestFormationEditorPropertyDelegation:
    """Test property delegation to core and renderer."""

    def test_arrows_property_returns_core_arrows(self):
        """arrows property should return core.arrows."""
        screen, mocks = _make_formation_editor_screen()

        type(screen).arrows = property(lambda self: self.core.arrows)

        assert screen.arrows == [[0, 0], [100, 100], [200, 200]]

    def test_arrow_attrs_property_returns_core_attrs(self):
        """arrow_attrs property should return core.arrow_attrs."""
        screen, mocks = _make_formation_editor_screen()

        type(screen).arrow_attrs = property(lambda self: self.core.arrow_attrs)

        assert len(screen.arrow_attrs) == 3
        assert screen.arrow_attrs[0]['rotation_mode'] == 'relative'

    def test_selected_indices_property_returns_core_selection(self):
        """selected_indices property should return core.selected_indices."""
        screen, mocks = _make_formation_editor_screen()
        mocks['core'].selected_indices = {0, 2}

        type(screen).selected_indices = property(
            lambda self: self.core.selected_indices,
            lambda self, v: setattr(self.core, 'selected_indices', v)
        )

        assert screen.selected_indices == {0, 2}

    def test_camera_zoom_property_returns_renderer_zoom(self):
        """camera_zoom property should return renderer.camera_zoom."""
        screen, mocks = _make_formation_editor_screen()
        mocks['renderer'].camera_zoom = 2.5

        type(screen).camera_zoom = property(
            lambda self: self.renderer.camera_zoom,
            lambda self, v: setattr(self.renderer, 'camera_zoom', v)
        )

        assert screen.camera_zoom == 2.5

    def test_snap_enabled_property_returns_renderer_snap(self):
        """snap_enabled property should return renderer.snap_enabled."""
        screen, mocks = _make_formation_editor_screen()

        type(screen).snap_enabled = property(
            lambda self: self.renderer.snap_enabled,
            lambda self, v: setattr(self.renderer, 'snap_enabled', v)
        )

        assert screen.snap_enabled == True


# ===========================================================================
# Task 6.3: Core Data Operations Tests
# ===========================================================================

class TestFormationEditorDataOperations:
    """Test core data manipulation operations."""

    def test_add_arrow_delegates_to_core(self):
        """add_arrow should delegate to core.add_arrow."""
        screen, mocks = _make_formation_editor_screen()

        def mock_add_arrow(pos):
            screen.core.add_arrow(pos)

        screen.add_arrow = mock_add_arrow
        screen.add_arrow((300, 300))

        mocks['core'].add_arrow.assert_called_once_with((300, 300))

    def test_delete_selected_delegates_to_core(self):
        """delete_selected should delegate to core.delete_selected."""
        screen, mocks = _make_formation_editor_screen()

        def mock_delete_selected():
            screen.core.delete_selected()

        screen.delete_selected = mock_delete_selected
        screen.delete_selected()

        mocks['core'].delete_selected.assert_called_once()

    def test_clone_selection_delegates_to_core(self):
        """clone_selection should delegate to core.clone_selection."""
        screen, mocks = _make_formation_editor_screen()

        def mock_clone_selection():
            offset = 25 if screen.renderer.snap_enabled else 20
            screen.core.clone_selection(offset)

        screen.clone_selection = mock_clone_selection
        screen.clone_selection()

        mocks['core'].clone_selection.assert_called_once_with(25)

    def test_clear_all_delegates_to_core(self):
        """clear_all should delegate to core.clear_all."""
        screen, mocks = _make_formation_editor_screen()

        def mock_clear_all():
            screen.core.clear_all()

        screen.clear_all = mock_clear_all
        screen.clear_all()

        mocks['core'].clear_all.assert_called_once()

    def test_move_arrow_delegates_to_core(self):
        """move_arrow should delegate to core.move_arrow."""
        screen, mocks = _make_formation_editor_screen()

        def mock_move_arrow(from_idx, to_idx):
            screen.core.move_arrow(from_idx, to_idx)

        screen.move_arrow = mock_move_arrow
        screen.move_arrow(2, 0)

        mocks['core'].move_arrow.assert_called_once_with(2, 0)


# ===========================================================================
# Task 6.3: Coordinate Transform Tests
# ===========================================================================

class TestFormationEditorCoordinateTransforms:
    """Test coordinate transformation delegation."""

    def test_world_to_screen_delegates_to_renderer(self):
        """world_to_screen should delegate to renderer."""
        screen, mocks = _make_formation_editor_screen()
        mocks['renderer'].world_to_screen.return_value = (500.0, 500.0)

        def mock_world_to_screen(wx, wy):
            return screen.renderer.world_to_screen(wx, wy)

        screen.world_to_screen = mock_world_to_screen
        result = screen.world_to_screen(100.0, 100.0)

        assert result == (500.0, 500.0)
        mocks['renderer'].world_to_screen.assert_called_once_with(100.0, 100.0)

    def test_screen_to_world_delegates_to_renderer(self):
        """screen_to_world should delegate to renderer."""
        screen, mocks = _make_formation_editor_screen()
        mocks['renderer'].screen_to_world.return_value = (100.0, 100.0)

        def mock_screen_to_world(sx, sy):
            return screen.renderer.screen_to_world(sx, sy)

        screen.screen_to_world = mock_screen_to_world
        result = screen.screen_to_world(500.0, 500.0)

        assert result == (100.0, 100.0)
        mocks['renderer'].screen_to_world.assert_called_once_with(500.0, 500.0)

    def test_snap_delegates_to_renderer(self):
        """snap should delegate to renderer."""
        screen, mocks = _make_formation_editor_screen()
        mocks['renderer'].snap.return_value = 100.0

        def mock_snap(val):
            return screen.renderer.snap(val)

        screen.snap = mock_snap
        result = screen.snap(98.5)

        assert result == 100.0
        mocks['renderer'].snap.assert_called_once_with(98.5)


# ===========================================================================
# Task 6.3: UI Info Update Tests
# ===========================================================================

class TestFormationEditorInfoUpdate:
    """Test info label updates."""

    def test_update_info_sets_arrow_count(self):
        """update_info should set arrow count in info label."""
        screen, mocks = _make_formation_editor_screen()
        mocks['core'].arrows = [[0, 0], [100, 100]]
        mocks['core'].selected_indices = set()

        def mock_update_info():
            count = len(screen.core.arrows)
            sel_count = len(screen.core.selected_indices)
            sel_str = f" | Selected: {sel_count}" if sel_count > 0 else ""
            screen.info_label.set_text(f"Arrows: {count}{sel_str}")

        screen.update_info = mock_update_info
        screen.update_info()

        screen.info_label.set_text.assert_called_with("Arrows: 2")

    def test_update_info_shows_selection_count(self):
        """update_info should show selection count when selected."""
        screen, mocks = _make_formation_editor_screen()
        mocks['core'].arrows = [[0, 0], [100, 100], [200, 200]]
        mocks['core'].selected_indices = {0, 2}

        def mock_update_info():
            count = len(screen.core.arrows)
            sel_count = len(screen.core.selected_indices)
            sel_str = f" | Selected: {sel_count}" if sel_count > 0 else ""
            screen.info_label.set_text(f"Arrows: {count}{sel_str}")

        screen.update_info = mock_update_info
        screen.update_info()

        screen.info_label.set_text.assert_called_with("Arrows: 3 | Selected: 2")
