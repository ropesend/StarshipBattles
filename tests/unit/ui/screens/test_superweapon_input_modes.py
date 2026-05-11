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

    # PROJ-323 Task 3.44: 5 mode-setting tests parametrized.
    @pytest.mark.parametrize("input_action,expected_mode", [
        pytest.param(InputAction.FLEET_IMPLODE_PLANET, 'IMPLODE_PLANET_TARGET', id="implode_planet"),
        pytest.param(InputAction.FLEET_STELLERATE_STAR, 'STELLERATE_STAR_TARGET', id="stellerate_star"),
        pytest.param(InputAction.FLEET_OPEN_WARP_POINT, 'OPEN_WARP_TARGET', id="open_warp"),
        pytest.param(InputAction.FLEET_CLOSE_WARP_POINT, 'CLOSE_WARP_TARGET', id="close_warp"),
        pytest.param(InputAction.FLEET_CREATE_DYSON_SPHERE, 'DYSON_SPHERE_TARGET', id="dyson_sphere"),
    ])
    def test_input_action_sets_corresponding_mode(
        self, handler_with_mapper, input_action, expected_mode,
    ):
        """Each fleet superweapon input action sets the matching target-input mode."""
        mapper = MockInputMapper(input_action)
        handler_with_mapper._mapper = mapper
        handler_with_mapper.scene.selected_fleet = MagicMock()

        event = MagicMock()
        handler_with_mapper._handle_keydown_mapped(event)

        assert handler_with_mapper.input_mode == expected_mode

    # Issue #19 AC2.5: fleet without OpenWarpPoint capability should NOT
    # enter target mode, and should surface a visible error message.
    def test_open_warp_without_inducer_blocks_target_mode_and_shows_error(
        self, handler_with_mapper,
    ):
        """Fleet without OpenWarpPoint ability: stays in SELECT, sees error."""
        mapper = MockInputMapper(InputAction.FLEET_OPEN_WARP_POINT)
        handler_with_mapper._mapper = mapper
        fleet = MagicMock()
        fleet.capabilities.has_ability.return_value = False
        handler_with_mapper.scene.selected_fleet = fleet
        handler_with_mapper.scene.ui.show_error_message = MagicMock()
        starting_mode = handler_with_mapper.input_mode

        event = MagicMock()
        handler_with_mapper._handle_keydown_mapped(event)

        assert handler_with_mapper.input_mode == starting_mode
        assert handler_with_mapper.input_mode != 'OPEN_WARP_TARGET'
        handler_with_mapper.scene.ui.show_error_message.assert_called_once()
        msg = handler_with_mapper.scene.ui.show_error_message.call_args[0][0]
        assert 'Quantum Tunneling' in msg
        fleet.capabilities.has_ability.assert_called_with("OpenWarpPoint")

    def test_open_warp_with_inducer_enters_target_mode(self, handler_with_mapper):
        """Fleet with OpenWarpPoint ability still enters OPEN_WARP_TARGET."""
        mapper = MockInputMapper(InputAction.FLEET_OPEN_WARP_POINT)
        handler_with_mapper._mapper = mapper
        fleet = MagicMock()
        fleet.capabilities.has_ability.return_value = True
        handler_with_mapper.scene.selected_fleet = fleet
        handler_with_mapper.scene.ui.show_error_message = MagicMock()

        event = MagicMock()
        handler_with_mapper._handle_keydown_mapped(event)

        assert handler_with_mapper.input_mode == 'OPEN_WARP_TARGET'
        handler_with_mapper.scene.ui.show_error_message.assert_not_called()

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

    # PROJ-323 Task 3.44: 5 click-routing tests parametrized.
    @pytest.mark.parametrize("mode,handler_attr", [
        pytest.param('IMPLODE_PLANET_TARGET', 'handle_implode_planet_designation', id="implode_planet"),
        pytest.param('STELLERATE_STAR_TARGET', 'handle_stellerate_star_designation', id="stellerate_star"),
        pytest.param('OPEN_WARP_TARGET', 'handle_open_warp_designation', id="open_warp"),
        pytest.param('CLOSE_WARP_TARGET', 'handle_close_warp_designation', id="close_warp"),
        pytest.param('DYSON_SPHERE_TARGET', 'handle_dyson_sphere_designation', id="dyson_sphere"),
    ])
    def test_click_delegates_to_superweapons(self, handler, mode, handler_attr):
        """Each superweapon target mode delegates left-click to its handler and resets to SELECT."""
        handler.input_mode = mode
        designation_mock = MagicMock(return_value=True)
        setattr(handler.scene._superweapons, handler_attr, designation_mock)

        result = handler.handle_click(100, 200, 1)  # Left click

        assert result is True
        designation_mock.assert_called_once()
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
