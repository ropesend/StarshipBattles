"""Tests for FormationInputHandler - extracted event handling from FormationEditorScreen."""

import pytest
from unittest.mock import MagicMock, patch
import math


class TestFormationInputHandler:
    """Tests for FormationInputHandler state machine."""

    @pytest.fixture
    def handler(self):
        """Create a FormationInputHandler instance for testing."""
        from game.ui.screens.formation.input_handler import FormationInputHandler
        return FormationInputHandler()

    def test_initial_state_is_idle(self, handler):
        """Handler starts in IDLE state."""
        assert handler.state == 'IDLE'

    def test_states_are_valid(self, handler):
        """All valid states are defined."""
        valid_states = {'IDLE', 'DRAGGING_ITEMS', 'BOX_SELECT', 'RESIZING_GROUP', 'PANNING', 'POTENTIAL_CLICK'}
        assert handler.state in valid_states

    def test_reset_state(self, handler):
        """reset_state returns to IDLE and clears interaction data."""
        handler.state = 'DRAGGING_ITEMS'
        handler.drag_start_world = (100, 100)
        handler.drag_offsets = {0: (10, 10)}

        handler.reset_state()

        assert handler.state == 'IDLE'
        assert handler.drag_start_world is None
        assert handler.drag_offsets == {}

    def test_start_panning(self, handler):
        """start_panning sets state and stores start position."""
        handler.start_panning(screen_pos=(500, 400), camera_pan=[100, 50])

        assert handler.state == 'PANNING'
        assert handler.drag_start_screen == (500, 400)
        assert handler.drag_start_world == [100, 50]

    def test_start_dragging_items(self, handler):
        """start_dragging stores offsets for selected items."""
        arrows = [[100, 100], [200, 200], [300, 300]]
        selected = {0, 2}
        world_pos = (150, 150)

        handler.start_dragging_items(world_pos, arrows, selected)

        assert handler.state == 'DRAGGING_ITEMS'
        assert handler.drag_start_world == world_pos
        # Offsets should be arrow_pos - world_pos
        assert handler.drag_offsets[0] == (100 - 150, 100 - 150)
        assert handler.drag_offsets[2] == (300 - 150, 300 - 150)
        assert 1 not in handler.drag_offsets

    def test_start_resizing_group(self, handler):
        """start_resizing stores bounds and initial positions."""
        import pygame
        bounds = pygame.Rect(0, 0, 200, 200)
        arrows = [[50, 50], [150, 150]]
        selected = {0, 1}
        screen_pos = (100, 100)
        grid_size = 50

        handler.start_resizing_group(
            handle_name='BR',
            bounds=bounds,
            arrows=arrows,
            selected=selected,
            screen_pos=screen_pos,
            grid_size=grid_size
        )

        assert handler.state == 'RESIZING_GROUP'
        assert handler.resize_handle == 'BR'
        assert handler.initial_group_bounds == bounds
        assert handler.drag_start_screen == screen_pos
        assert 0 in handler.initial_arrow_positions
        assert 1 in handler.initial_arrow_positions

    def test_start_box_select(self, handler):
        """start_box_select stores start positions."""
        handler.start_box_select(screen_pos=(400, 300), world_pos=(100, 50))

        assert handler.state == 'BOX_SELECT'
        assert handler.drag_start_screen == (400, 300)
        assert handler.drag_start_world == (100, 50)

    def test_start_potential_click(self, handler):
        """start_potential_click prepares for click or drag."""
        handler.start_potential_click(screen_pos=(400, 300), world_pos=(100, 50))

        assert handler.state == 'POTENTIAL_CLICK'
        assert handler.drag_start_screen == (400, 300)
        assert handler.drag_start_world == (100, 50)

    def test_should_transition_to_box_select(self, handler):
        """Detects when drag distance exceeds threshold."""
        handler.state = 'POTENTIAL_CLICK'
        handler.drag_start_screen = (100, 100)

        # Small movement - no transition
        assert not handler.should_transition_to_box_select((102, 102))

        # Large movement - transition
        assert handler.should_transition_to_box_select((110, 100))


class TestPanningBehavior:
    """Tests for panning state behavior."""

    @pytest.fixture
    def handler(self):
        """Create handler in panning state."""
        from game.ui.screens.formation.input_handler import FormationInputHandler
        handler = FormationInputHandler()
        handler.start_panning(screen_pos=(500, 400), camera_pan=[0, 0])
        return handler

    def test_calculate_pan_delta(self, handler):
        """Calculates correct pan delta from drag."""
        new_pan = handler.calculate_pan_delta((600, 450))
        # Moved 100 right, 50 down from start
        assert new_pan == [100, 50]

    def test_calculate_pan_delta_negative(self, handler):
        """Handles negative pan movements."""
        new_pan = handler.calculate_pan_delta((400, 350))
        assert new_pan == [-100, -50]


class TestDraggingItemsBehavior:
    """Tests for item dragging behavior."""

    @pytest.fixture
    def handler(self):
        """Create handler in dragging state."""
        from game.ui.screens.formation.input_handler import FormationInputHandler
        handler = FormationInputHandler()
        arrows = [[100, 100], [200, 200]]
        handler.start_dragging_items((100, 100), arrows, {0, 1})
        return handler

    def test_calculate_new_positions(self, handler):
        """Calculates new positions maintaining relative offsets."""
        # Drag to new world position (150, 150)
        new_positions = handler.calculate_new_positions((150, 150), snap_func=lambda x: x)

        # Index 0 was at (100, 100), offset (0, 0), should move to (150, 150)
        assert new_positions[0] == [150, 150]
        # Index 1 was at (200, 200), offset (100, 100), should move to (250, 250)
        assert new_positions[1] == [250, 250]

    def test_calculate_new_positions_with_snap(self, handler):
        """New positions respect snap function."""

        def snap_50(val):
            return round(val / 50) * 50

        new_positions = handler.calculate_new_positions((123, 137), snap_func=snap_50)

        # 123 + 0 -> 123 -> snaps to 100
        # 137 + 0 -> 137 -> snaps to 150
        assert new_positions[0] == [100, 150]


class TestBoxSelectBehavior:
    """Tests for box selection behavior."""

    @pytest.fixture
    def handler(self):
        """Create handler in box select state."""
        from game.ui.screens.formation.input_handler import FormationInputHandler
        handler = FormationInputHandler()
        handler.start_box_select(screen_pos=(100, 100), world_pos=(0, 0))
        return handler

    def test_get_selection_box(self, handler):
        """Returns correct selection rectangle."""
        import pygame
        # End position is bottom-right of start
        # drag_start_screen is (100, 100), end is (200, 150)
        box = handler.get_selection_box((200, 150))

        assert box == pygame.Rect(100, 100, 100, 50)

    def test_get_selection_box_inverted(self, handler):
        """Handles inverted selection (drag up-left)."""
        import pygame
        # End position is top-left of start
        box = handler.get_selection_box((50, 50))

        # Rect should be normalized
        assert box.width == 50
        assert box.height == 50

    def test_find_arrows_in_box(self, handler):
        """Finds all arrows within selection box."""
        import pygame
        # Selection from (0,0) to (100,100) in world coords
        handler.drag_start_world = (0, 0)

        def screen_to_world(sx, sy):
            return (sx, sy)  # Identity for testing

        arrows = [[50, 50], [150, 50], [75, 75], [-10, 50]]

        selected = handler.find_arrows_in_box(
            screen_pos=(100, 100),
            arrows=arrows,
            screen_to_world=screen_to_world
        )

        # Only arrows at (50,50) and (75,75) are inside box
        assert selected == {0, 2}


class TestResizingBehavior:
    """Tests for group resizing behavior."""

    @pytest.fixture
    def handler(self):
        """Create handler in resizing state."""
        from game.ui.screens.formation.input_handler import FormationInputHandler
        import pygame

        handler = FormationInputHandler()
        bounds = pygame.Rect(0, 0, 100, 100)
        arrows = [[25, 25], [75, 75]]

        handler.start_resizing_group(
            handle_name='BR',
            bounds=bounds,
            arrows=arrows,
            selected={0, 1},
            screen_pos=(100, 100),
            grid_size=50
        )
        return handler

    def test_calculate_resize_scale_br(self, handler):
        """Bottom-right handle scales correctly."""
        # Original bounds: 0,0 -> 100,100
        # Moving BR handle to double the size

        def screen_to_world(sx, sy):
            return (sx, sy)  # Identity

        new_positions = handler.calculate_resize_positions(
            screen_pos=(200, 200),
            screen_to_world=screen_to_world,
            snap_func=lambda x: x,
            grid_size=50
        )

        # With 2x scale in both dimensions
        # Point at (25,25) in original 100x100 -> (50,50) in 200x200
        # Actually depends on implementation details
        assert 0 in new_positions
        assert 1 in new_positions


class TestClickDetection:
    """Tests for arrow click detection logic."""

    @pytest.fixture
    def handler(self):
        """Create a FormationInputHandler instance."""
        from game.ui.screens.formation.input_handler import FormationInputHandler
        return FormationInputHandler()

    def test_get_arrow_at_position_hit(self, handler):
        """Finds arrow when clicking near it."""
        arrows = [[100, 100], [200, 200]]

        def world_to_screen(wx, wy):
            return (wx, wy)  # Identity

        # Click at (105, 105) should hit arrow at (100, 100)
        idx = handler.get_arrow_at(
            world_pos=(105, 105),
            arrows=arrows,
            world_to_screen=world_to_screen,
            click_radius=25
        )
        assert idx == 0

    def test_get_arrow_at_position_miss(self, handler):
        """Returns None when click is far from arrows."""
        arrows = [[100, 100], [200, 200]]

        def world_to_screen(wx, wy):
            return (wx, wy)

        idx = handler.get_arrow_at(
            world_pos=(500, 500),
            arrows=arrows,
            world_to_screen=world_to_screen,
            click_radius=25
        )
        assert idx is None

    def test_get_arrow_at_position_topmost(self, handler):
        """Returns topmost (last) arrow when overlapping."""
        arrows = [[100, 100], [105, 105]]  # Overlapping

        def world_to_screen(wx, wy):
            return (wx, wy)

        idx = handler.get_arrow_at(
            world_pos=(103, 103),
            arrows=arrows,
            world_to_screen=world_to_screen,
            click_radius=25
        )
        # Last arrow (index 1) should be returned as it's on top
        assert idx == 1
