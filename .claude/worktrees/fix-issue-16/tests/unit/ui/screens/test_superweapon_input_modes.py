"""Tests for superweapon input mode transitions (Phase 7)."""

import pytest
from unittest.mock import MagicMock, patch
from game.core.input_actions import InputAction


class MockScene:
    """Mock scene for testing input handler."""

    def __init__(self):
        self.selected_fleet = MagicMock()
        self.ui = MagicMock()
        self._superweapons = MagicMock()
        self.camera = MagicMock()
        self._camera_nav = MagicMock()


class MockInputMapper:
    """Mock input mapper for testing."""

    def __init__(self, action_to_return):
        self._action = action_to_return

    def resolve(self, event, contexts):
        return self._action


class TestSuperweaponInputModeTransitions:
    """Tests for superweapon input mode transitions."""

    @pytest.fixture
    def handler(self):
        """Create a StrategyInputHandler for testing."""
        from game.ui.screens.strategy_input_handler import StrategyInputHandler
        scene = MockScene()
        handler = StrategyInputHandler(scene, input_mapper=None)
        return handler

    @pytest.fixture
    def handler_with_mapper(self):
        """Create a StrategyInputHandler with a mock mapper."""
        from game.ui.screens.strategy_input_handler import StrategyInputHandler
        scene = MockScene()
        # We'll set the mapper per-test
        handler = StrategyInputHandler(scene, input_mapper=None)
        return handler

    def test_implode_planet_sets_mode(self, handler_with_mapper):
        """FLEET_IMPLODE_PLANET sets IMPLODE_PLANET_TARGET mode."""
        mapper = MockInputMapper(InputAction.FLEET_IMPLODE_PLANET)
        handler_with_mapper._mapper = mapper
        handler_with_mapper.scene.selected_fleet = MagicMock()

        event = MagicMock()
        handler_with_mapper._handle_keydown_mapped(event)

        assert handler_with_mapper.input_mode == 'IMPLODE_PLANET_TARGET'

    def test_stellerate_star_sets_mode(self, handler_with_mapper):
        """FLEET_STELLERATE_STAR sets STELLERATE_STAR_TARGET mode."""
        mapper = MockInputMapper(InputAction.FLEET_STELLERATE_STAR)
        handler_with_mapper._mapper = mapper
        handler_with_mapper.scene.selected_fleet = MagicMock()

        event = MagicMock()
        handler_with_mapper._handle_keydown_mapped(event)

        assert handler_with_mapper.input_mode == 'STELLERATE_STAR_TARGET'

    def test_open_warp_sets_mode(self, handler_with_mapper):
        """FLEET_OPEN_WARP_POINT sets OPEN_WARP_TARGET mode."""
        mapper = MockInputMapper(InputAction.FLEET_OPEN_WARP_POINT)
        handler_with_mapper._mapper = mapper
        handler_with_mapper.scene.selected_fleet = MagicMock()

        event = MagicMock()
        handler_with_mapper._handle_keydown_mapped(event)

        assert handler_with_mapper.input_mode == 'OPEN_WARP_TARGET'

    def test_close_warp_sets_mode(self, handler_with_mapper):
        """FLEET_CLOSE_WARP_POINT sets CLOSE_WARP_TARGET mode."""
        mapper = MockInputMapper(InputAction.FLEET_CLOSE_WARP_POINT)
        handler_with_mapper._mapper = mapper
        handler_with_mapper.scene.selected_fleet = MagicMock()

        event = MagicMock()
        handler_with_mapper._handle_keydown_mapped(event)

        assert handler_with_mapper.input_mode == 'CLOSE_WARP_TARGET'

    def test_dyson_sphere_sets_mode(self, handler_with_mapper):
        """FLEET_CREATE_DYSON_SPHERE sets DYSON_SPHERE_TARGET mode."""
        mapper = MockInputMapper(InputAction.FLEET_CREATE_DYSON_SPHERE)
        handler_with_mapper._mapper = mapper
        handler_with_mapper.scene.selected_fleet = MagicMock()

        event = MagicMock()
        handler_with_mapper._handle_keydown_mapped(event)

        assert handler_with_mapper.input_mode == 'DYSON_SPHERE_TARGET'

    def test_self_destruct_calls_handler(self, handler_with_mapper):
        """FLEET_SELF_DESTRUCT calls superweapons handler directly."""
        mapper = MockInputMapper(InputAction.FLEET_SELF_DESTRUCT)
        handler_with_mapper._mapper = mapper
        fleet = MagicMock()
        handler_with_mapper.scene.selected_fleet = fleet

        event = MagicMock()
        handler_with_mapper._handle_keydown_mapped(event)

        handler_with_mapper.scene._superweapons.handle_self_destruct.assert_called_once_with(fleet)


class TestSuperweaponModeCancel:
    """Tests for ESC canceling superweapon modes."""

    @pytest.fixture
    def handler_with_mapper(self):
        """Create a StrategyInputHandler with a mock mapper."""
        from game.ui.screens.strategy_input_handler import StrategyInputHandler
        scene = MockScene()
        handler = StrategyInputHandler(scene, input_mapper=None)
        return handler

    @pytest.mark.parametrize("mode", [
        'IMPLODE_PLANET_TARGET',
        'STELLERATE_STAR_TARGET',
        'OPEN_WARP_TARGET',
        'CLOSE_WARP_TARGET',
        'DYSON_SPHERE_TARGET',
    ])
    def test_escape_cancels_superweapon_modes(self, handler_with_mapper, mode):
        """ESC returns to SELECT from all superweapon modes."""
        mapper = MockInputMapper(InputAction.FLEET_CANCEL_MODE)
        handler_with_mapper._mapper = mapper
        handler_with_mapper.input_mode = mode

        event = MagicMock()
        handler_with_mapper._handle_keydown_mapped(event)

        assert handler_with_mapper.input_mode == 'SELECT'


class TestSuperweaponClickRouting:
    """Tests for superweapon click routing."""

    @pytest.fixture
    def handler(self):
        """Create a StrategyInputHandler for testing."""
        from game.ui.screens.strategy_input_handler import StrategyInputHandler
        scene = MockScene()
        scene.ui.handle_click = MagicMock(return_value=False)
        handler = StrategyInputHandler(scene, input_mapper=None)
        return handler

    def test_implode_planet_click_delegates_to_superweapons(self, handler):
        """IMPLODE_PLANET_TARGET click delegates to superweapons handler."""
        handler.input_mode = 'IMPLODE_PLANET_TARGET'
        handler.scene._superweapons.handle_implode_planet_designation = MagicMock(return_value=True)

        result = handler.handle_click(100, 200, 1)  # Left click

        assert result is True
        handler.scene._superweapons.handle_implode_planet_designation.assert_called_once()
        assert handler.input_mode == 'SELECT'

    def test_stellerate_star_click_delegates_to_superweapons(self, handler):
        """STELLERATE_STAR_TARGET click delegates to superweapons handler."""
        handler.input_mode = 'STELLERATE_STAR_TARGET'
        handler.scene._superweapons.handle_stellerate_star_designation = MagicMock(return_value=True)

        result = handler.handle_click(100, 200, 1)  # Left click

        assert result is True
        handler.scene._superweapons.handle_stellerate_star_designation.assert_called_once()
        assert handler.input_mode == 'SELECT'

    def test_open_warp_click_delegates_to_superweapons(self, handler):
        """OPEN_WARP_TARGET click delegates to superweapons handler."""
        handler.input_mode = 'OPEN_WARP_TARGET'
        handler.scene._superweapons.handle_open_warp_designation = MagicMock(return_value=True)

        result = handler.handle_click(100, 200, 1)  # Left click

        assert result is True
        handler.scene._superweapons.handle_open_warp_designation.assert_called_once()
        assert handler.input_mode == 'SELECT'

    def test_close_warp_click_delegates_to_superweapons(self, handler):
        """CLOSE_WARP_TARGET click delegates to superweapons handler."""
        handler.input_mode = 'CLOSE_WARP_TARGET'
        handler.scene._superweapons.handle_close_warp_designation = MagicMock(return_value=True)

        result = handler.handle_click(100, 200, 1)  # Left click

        assert result is True
        handler.scene._superweapons.handle_close_warp_designation.assert_called_once()
        assert handler.input_mode == 'SELECT'

    def test_dyson_sphere_click_delegates_to_superweapons(self, handler):
        """DYSON_SPHERE_TARGET click delegates to superweapons handler."""
        handler.input_mode = 'DYSON_SPHERE_TARGET'
        handler.scene._superweapons.handle_dyson_sphere_designation = MagicMock(return_value=True)

        result = handler.handle_click(100, 200, 1)  # Left click

        assert result is True
        handler.scene._superweapons.handle_dyson_sphere_designation.assert_called_once()
        assert handler.input_mode == 'SELECT'

    @pytest.mark.parametrize("mode", [
        'IMPLODE_PLANET_TARGET',
        'STELLERATE_STAR_TARGET',
        'OPEN_WARP_TARGET',
        'CLOSE_WARP_TARGET',
        'DYSON_SPHERE_TARGET',
    ])
    def test_right_click_cancels_superweapon_modes(self, handler, mode):
        """Right click cancels all superweapon modes."""
        handler.input_mode = mode

        result = handler.handle_click(100, 200, 3)  # Right click

        assert result is True
        assert handler.input_mode == 'SELECT'
