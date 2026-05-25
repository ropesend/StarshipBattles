"""Extended tests for BattleScreen simulation lifecycle, win/loss, events, ticks.

PROJ-111 Phase 3 Task 3.1: BattleScreen Extended Coverage
"""
import copy
import pytest
from unittest.mock import MagicMock, patch
import pygame

from game.ui.screens.battle_screen import (
    BattleScreen, MIN_SPEED_MULTIPLIER, MAX_SPEED_MULTIPLIER,
    NORMAL_SPEED, UI_PAUSE_SPEED
)
from game.simulation.entities.ship import Ship
from game.simulation.components.component import create_component
from game.core.constants import LayerType
from tests.fixtures.battle import start_battle_screen_with_minimal_spec


def _build_ship(name, x, y, color, registries):
    """Build a ship with standard components and calculated stats."""
    ship = Ship(name, x, y, color, registries=registries)
    ship.add_component(create_component('bridge', registries=registries), LayerType.CORE)
    ship.add_component(create_component('crew_quarters', registries=registries), LayerType.CORE)
    ship.add_component(create_component('life_support', registries=registries), LayerType.CORE)
    ship.add_component(create_component('standard_engine', registries=registries), LayerType.OUTER)
    ship.recalculate_stats()
    return ship


@pytest.fixture(scope="module")
def ship_templates(session_registries):
    """Module-scoped ship templates built once, deepcopied per test.

    Building ships with create_component + recalculate_stats is expensive.
    This fixture creates them once per module; tests deepcopy as needed.
    """
    ship1 = _build_ship("Ship1", 0, 0, (0, 0, 255), session_registries)
    ship2 = _build_ship("Ship2", 1000, 0, (255, 0, 0), session_registries)
    ship3 = _build_ship("Ship3", 500, 500, (0, 255, 0), session_registries)
    return ship1, ship2, ship3


class TestBattleScreenSimulationLifecycle:
    """Test BattleScreen simulation lifecycle methods."""

    @pytest.fixture(autouse=True)
    def setup_scene(self, ship_templates, fresh_registries):
        """Set up BattleScreen with mocked BattleUI."""
        with patch('game.ui.screens.battle_screen.BattleUI') as MockUI:
            self.scene = BattleScreen(800, 600)
            self.scene.ui = MockUI.return_value
            self.scene.ui.show_overlay = False
            self.scene.ui.expanded_ships = set()
            self.scene.ui.stats_scroll_offset = 0
            self.scene.ui.seeker_panel = MagicMock()
            self.scene.ui.seeker_panel.rect = MagicMock()
            self.scene.ui.seeker_panel.rect.width = 300

            self.ship1 = copy.deepcopy(ship_templates[0])
            self.ship2 = copy.deepcopy(ship_templates[1])

            self.fresh_registries = fresh_registries
            yield

    def test_start_headless_true_sets_headless_mode(self):
        """Test start() with headless=True sets headless_mode."""
        start_battle_screen_with_minimal_spec(
            self.scene, {0: [self.ship1], 1: [self.ship2]}, headless=True,
        )

        assert self.scene.headless_mode is True

    def test_start_headless_false_mode_difference(self):
        """Test start() with headless=False does not set headless mode."""
        self.scene.camera = MagicMock()  # Mock camera for fit_objects

        start_battle_screen_with_minimal_spec(
            self.scene, {0: [self.ship1], 1: [self.ship2]}, headless=False,
        )

        assert self.scene.headless_mode is False
        self.scene.camera.fit_objects.assert_called_once()

    def test_start_assigns_correct_team_ids(self):
        """Test start() assigns team_id 0 to team0 and 1 to team1."""
        start_battle_screen_with_minimal_spec(
            self.scene, {0: [self.ship1], 1: [self.ship2]}, headless=True,
        )

        # Ships are added via battle service which sets team_id
        team0_ships = [s for s in self.scene.ships if s.team_id == 0]
        team1_ships = [s for s in self.scene.ships if s.team_id == 1]

        assert len(team0_ships) == 1
        assert len(team1_ships) == 1
        assert team0_ships[0].name == "Ship1"
        assert team1_ships[0].name == "Ship2"

    def test_start_creates_battle_service_and_ui_service(self):
        """Test start() creates BattleService and BattleUIService."""
        from game.simulation.services import BattleService
        from game.ui.services.battle_ui_service import BattleUIService

        start_battle_screen_with_minimal_spec(
            self.scene, {0: [self.ship1], 1: [self.ship2]}, headless=True,
        )

        assert self.scene._battle_service is not None
        assert isinstance(self.scene._battle_service, BattleService)
        assert self.scene._ui_service is not None
        assert isinstance(self.scene._ui_service, BattleUIService)

    def test_pause_unpause_toggle(self):
        """Test pause/unpause via sim_paused toggle."""
        start_battle_screen_with_minimal_spec(
            self.scene, {0: [self.ship1], 1: [self.ship2]}, headless=False,
        )

        assert self.scene.sim_paused is False

        self.scene.sim_paused = True
        assert self.scene.sim_paused is True

        self.scene.sim_paused = False
        assert self.scene.sim_paused is False

    def test_start_paused_parameter(self):
        """Test start() with start_paused=True starts paused."""
        start_battle_screen_with_minimal_spec(
            self.scene, {0: [self.ship1], 1: [self.ship2]}, headless=False, start_paused=True,
        )

        assert self.scene.sim_paused is True

    def test_speed_multiplier_changes_affect_tick_accumulation(self):
        """Test speed multiplier changes affect tick accumulation."""
        start_battle_screen_with_minimal_spec(
            self.scene, {0: [self.ship1], 1: [self.ship2]}, headless=False,
        )
        self.scene.sim_paused = False

        # At 2x speed, accumulator should add more time
        self.scene.sim_speed_multiplier = 2.0
        self.scene._accumulator = 0.0
        dt = 0.016  # 16ms frame

        # Manually call the visual update logic
        self.scene._update_visual(dt)

        # With 2x speed, accumulator would have added 0.032 worth
        # Depends on tick rate, but the key is that multiplier affects it
        # At 1x with 0.016s dt, we'd run 1 tick (if tick_rate is 0.016)
        # At 2x with 0.016s dt, we'd run ~2 ticks
        assert self.scene.sim_tick_counter >= 1


class TestBattleScreenWinLossDetection:
    """Test BattleScreen win/loss detection logic."""

    @pytest.fixture(autouse=True)
    def setup_scene(self, ship_templates, fresh_registries):
        """Set up BattleScreen with ships."""
        with patch('game.ui.screens.battle_screen.BattleUI') as MockUI:
            self.scene = BattleScreen(800, 600)
            self.scene.ui = MockUI.return_value
            self.scene.ui.show_overlay = False

            self.ship1 = copy.deepcopy(ship_templates[0])
            self.ship2 = copy.deepcopy(ship_templates[1])

            self.fresh_registries = fresh_registries
            yield

    # PROJ-494 T5.1: 3 single-target winner-determination tests parametrized
    # on `(kill_indices, expected_winner, expect_battle_over)`. The
    # `test_is_battle_over_with_partial_deaths` test stays distinct (it adds
    # a third ship and asserts the opposite observable: NOT battle-over).
    @pytest.mark.parametrize(
        "kill_indices,expected_winner,expect_battle_over",
        [
            pytest.param((0,), 1, True, id='team0_dead_team1_wins'),
            pytest.param((1,), 0, True, id='team1_dead_team0_wins'),
            pytest.param((0, 1), -1, True, id='all_dead_draw'),
        ],
    )
    def test_get_winner_for_team_deaths(
        self, kill_indices, expected_winner, expect_battle_over
    ):
        """get_winner()/is_battle_over() classify single-ship-per-team outcomes."""
        start_battle_screen_with_minimal_spec(
            self.scene, {0: [self.ship1], 1: [self.ship2]}, headless=True,
        )

        ships = (self.ship1, self.ship2)
        for idx in kill_indices:
            ships[idx].is_alive = False

        assert self.scene.is_battle_over() is expect_battle_over
        assert self.scene.get_winner() == expected_winner

    def test_is_battle_over_with_partial_deaths(self, ship_templates):
        """Test is_battle_over() with some ships dead but not all."""
        # Create additional ship from template
        ship3 = copy.deepcopy(ship_templates[2])

        start_battle_screen_with_minimal_spec(
            self.scene, {0: [self.ship1, ship3], 1: [self.ship2]}, headless=True,
        )

        # Kill one team0 ship but not all
        self.ship1.is_alive = False

        assert not self.scene.is_battle_over()  # ship3 still alive


class TestBattleScreenEventHandling:
    """Test BattleScreen event handling."""

    @pytest.fixture(autouse=True)
    def setup_scene(self, ship_templates):
        """Set up BattleScreen with mocked UI."""
        with patch('game.ui.screens.battle_screen.BattleUI') as MockUI:
            self.scene = BattleScreen(800, 600)
            self.scene.ui = MockUI.return_value
            self.scene.ui.show_overlay = False
            self.scene.ui.handle_click = MagicMock(return_value=False)
            self.scene.ui.handle_scroll = MagicMock()

            self.ship1 = copy.deepcopy(ship_templates[0])
            self.ship2 = copy.deepcopy(ship_templates[1])

            yield

    def test_handle_event_keyboard_space_toggles_pause(self):
        """Test handle_event() with SPACE key toggles pause."""
        start_battle_screen_with_minimal_spec(
            self.scene, {0: [self.ship1], 1: [self.ship2]}, headless=False,
        )
        self.scene.sim_paused = False

        event = MagicMock()
        event.type = pygame.KEYDOWN
        event.key = pygame.K_SPACE

        self.scene.handle_event(event)

        assert self.scene.sim_paused is True

        # Toggle back
        self.scene.handle_event(event)
        assert self.scene.sim_paused is False

    # PROJ-494 T3.14: 4 speed-multiplier-key tests parametrized on
    # `(key, start_speed, expected_speed)`. The M key reads NORMAL_SPEED and
    # SLASH reads UI_PAUSE_SPEED — those constants are imported above.
    @pytest.mark.parametrize(
        "key,start_speed,get_expected",
        [
            pytest.param(pygame.K_COMMA, 1.0, lambda: 0.5, id='comma_decreases'),
            pytest.param(pygame.K_PERIOD, 1.0, lambda: 2.0, id='period_increases'),
            pytest.param(pygame.K_m, 4.0, lambda: NORMAL_SPEED, id='m_resets'),
            pytest.param(pygame.K_SLASH, 1.0, lambda: UI_PAUSE_SPEED, id='slash_ui_pause'),
        ],
    )
    def test_handle_event_speed_multiplier_keys(self, key, start_speed, get_expected):
        """Each speed-multiplier key sets sim_speed_multiplier to the matching value."""
        start_battle_screen_with_minimal_spec(
            self.scene, {0: [self.ship1], 1: [self.ship2]}, headless=False,
        )
        self.scene.sim_speed_multiplier = start_speed

        event = MagicMock()
        event.type = pygame.KEYDOWN
        event.key = key

        self.scene.handle_event(event)

        assert self.scene.sim_speed_multiplier == get_expected()

    def test_handle_event_forwards_to_battle_ui(self):
        """Test handle_event() forwards mouse clicks to BattleUI."""
        start_battle_screen_with_minimal_spec(
            self.scene, {0: [self.ship1], 1: [self.ship2]}, headless=False,
        )

        event = MagicMock()
        event.type = pygame.MOUSEBUTTONDOWN
        event.pos = (100, 100)
        event.button = 1

        self.scene.handle_event(event)

        self.scene.ui.handle_click.assert_called_with(100, 100, 1)

    def test_handle_event_mouse_scroll_forwards_to_camera(self):
        """Test handle_event() forwards mouse scroll to camera for zoom."""
        start_battle_screen_with_minimal_spec(
            self.scene, {0: [self.ship1], 1: [self.ship2]}, headless=False,
        )

        event = MagicMock()
        event.type = pygame.MOUSEWHEEL
        event.y = 1

        with patch.object(self.scene.camera, 'update_input') as mock_cam:
            self.scene.handle_event(event)

            mock_cam.assert_called_once_with(0, [event], allow_wasd=False)

    def test_handle_event_focus_ship_from_ui_click(self):
        """Test handle_event() sets camera target from UI focus_ship result."""
        start_battle_screen_with_minimal_spec(
            self.scene, {0: [self.ship1], 1: [self.ship2]}, headless=False,
        )
        self.scene.ui.handle_click.return_value = ("focus_ship", self.ship1.id)

        event = MagicMock()
        event.type = pygame.MOUSEBUTTONDOWN
        event.pos = (100, 100)
        event.button = 1

        self.scene.handle_event(event)

        assert self.scene.camera.target == self.ship1

    def test_handle_event_end_battle_from_ui_click(self):
        """Test handle_event() with 'end_battle' result triggers return."""
        callback = MagicMock()
        self.scene.scene_callback = callback
        start_battle_screen_with_minimal_spec(
            self.scene, {0: [self.ship1], 1: [self.ship2]}, headless=False,
        )
        self.scene.ui.handle_click.return_value = "end_battle"

        event = MagicMock()
        event.type = pygame.MOUSEBUTTONDOWN
        event.pos = (100, 100)
        event.button = 1

        self.scene.handle_event(event)

        callback.assert_called_once()
        assert callback.call_args[0][0] == "show_results"

    def test_handle_event_left_click_clears_camera_target(self):
        """Test handle_event() left click with no UI hit clears camera target."""
        start_battle_screen_with_minimal_spec(
            self.scene, {0: [self.ship1], 1: [self.ship2]}, headless=False,
        )
        self.scene.camera.target = self.ship1
        self.scene.ui.handle_click.return_value = False

        event = MagicMock()
        event.type = pygame.MOUSEBUTTONDOWN
        event.pos = (100, 100)
        event.button = 1

        self.scene.handle_event(event)

        assert self.scene.camera.target is None


class TestBattleScreenCameraInput:
    """Test that battle screen processes camera input (panning, arrow keys) each frame."""

    @pytest.fixture(autouse=True)
    def setup_scene(self, ship_templates):
        """Set up BattleScreen with mocked UI."""
        with patch('game.ui.screens.battle_screen.BattleUI') as MockUI:
            self.scene = BattleScreen(800, 600)
            self.scene.ui = MockUI.return_value
            self.scene.ui.show_overlay = False

            self.ship1 = copy.deepcopy(ship_templates[0])
            self.ship2 = copy.deepcopy(ship_templates[1])

            yield

    def test_visual_update_calls_camera_update_input(self):
        """Camera input (panning, arrow keys) is processed each visual frame."""
        start_battle_screen_with_minimal_spec(
            self.scene, {0: [self.ship1], 1: [self.ship2]}, headless=False,
        )
        self.scene.sim_paused = True  # Pause to isolate camera update

        with patch.object(self.scene.camera, 'update_input') as mock_input:
            self.scene._update_visual(0.016)

            mock_input.assert_called_once()
            # Should pass dt and disable WASD (conflicts with speed keys)
            args, kwargs = mock_input.call_args
            assert args[0] == 0.016  # dt
            assert kwargs.get('allow_wasd', True) is False

    def _make_key_state(self, pressed_keys=None):
        """Create a mock key state with specific keys pressed."""
        # Use a defaultdict-like object that returns False for any index
        state = MagicMock()
        state.__getitem__ = lambda self_inner, key: key in (pressed_keys or [])
        return state

    def test_arrow_key_panning_moves_camera(self):
        """Arrow keys pan the camera during visual update."""
        start_battle_screen_with_minimal_spec(
            self.scene, {0: [self.ship1], 1: [self.ship2]}, headless=False,
        )
        self.scene.sim_paused = True
        self.scene.camera.target = None

        initial_pos = pygame.math.Vector2(self.scene.camera.position)

        with patch('pygame.key.get_pressed', return_value=self._make_key_state([pygame.K_RIGHT])), \
             patch('pygame.mouse.get_pressed', return_value=(False, False, False)), \
             patch('pygame.mouse.get_rel', return_value=(0, 0)):
            self.scene._update_visual(0.1)

        assert self.scene.camera.position.x > initial_pos.x

    def test_middle_mouse_panning_moves_camera(self):
        """Middle mouse drag pans the camera during visual update."""
        start_battle_screen_with_minimal_spec(
            self.scene, {0: [self.ship1], 1: [self.ship2]}, headless=False,
        )
        self.scene.sim_paused = True
        self.scene.camera.target = None
        self.scene.camera.position = pygame.math.Vector2(500, 500)

        with patch('pygame.key.get_pressed', return_value=self._make_key_state()), \
             patch('pygame.mouse.get_pressed', return_value=(False, True, False)), \
             patch('pygame.mouse.get_rel', return_value=(50, 30)):
            self.scene._update_visual(0.016)

        # Camera should have moved opposite to mouse drag direction
        assert self.scene.camera.position.x < 500
        assert self.scene.camera.position.y < 500

    def test_middle_mouse_panning_clears_target(self):
        """Middle mouse drag clears camera target follow."""
        start_battle_screen_with_minimal_spec(
            self.scene, {0: [self.ship1], 1: [self.ship2]}, headless=False,
        )
        self.scene.sim_paused = True
        self.scene.camera.target = self.ship1

        with patch('pygame.key.get_pressed', return_value=self._make_key_state()), \
             patch('pygame.mouse.get_pressed', return_value=(False, True, False)), \
             patch('pygame.mouse.get_rel', return_value=(10, 10)):
            self.scene._update_visual(0.016)

        assert self.scene.camera.target is None

    def test_headless_mode_does_not_process_camera_input(self):
        """Headless mode skips camera input processing entirely."""
        start_battle_screen_with_minimal_spec(
            self.scene, {0: [self.ship1], 1: [self.ship2]}, headless=True,
        )

        with patch.object(self.scene.camera, 'update_input') as mock_input, \
             patch.object(self.scene, '_run_single_tick'):
            self.scene.update(0.016)

            mock_input.assert_not_called()


class TestBattleScreenTickMechanics:
    """Test BattleScreen tick mechanics and accumulator."""

    @pytest.fixture(autouse=True)
    def setup_scene(self, ship_templates):
        """Set up BattleScreen with mocked UI."""
        with patch('game.ui.screens.battle_screen.BattleUI') as MockUI:
            self.scene = BattleScreen(800, 600)
            self.scene.ui = MockUI.return_value
            self.scene.ui.show_overlay = False

            self.ship1 = copy.deepcopy(ship_templates[0])
            self.ship2 = copy.deepcopy(ship_templates[1])

            yield

    def test_accumulator_capped_to_prevent_spiral_of_death(self):
        """Test accumulator doesn't exceed max cap (prevents spiral-of-death)."""
        start_battle_screen_with_minimal_spec(
            self.scene, {0: [self.ship1], 1: [self.ship2]}, headless=False,
        )
        self.scene.sim_paused = False
        self.scene.sim_speed_multiplier = 1.0
        self.scene._accumulator = 0.0

        # Simulate very large dt (lag spike)
        large_dt = 10.0  # 10 seconds

        self.scene._update_visual(large_dt)

        # Accumulator should be capped at 1.0 in the code
        # After running ticks, it should be near 0 but started from 1.0 cap
        # The key test is that we didn't run 10 seconds worth of ticks (600+ ticks)
        assert self.scene.sim_tick_counter < 100  # Reasonable cap

    def test_multiple_ticks_per_frame_with_large_dt(self):
        """Test multiple ticks run per frame with large dt value."""
        start_battle_screen_with_minimal_spec(
            self.scene, {0: [self.ship1], 1: [self.ship2]}, headless=False,
        )
        self.scene.sim_paused = False
        self.scene.sim_speed_multiplier = 1.0
        self.scene._accumulator = 0.0

        # dt that should run multiple ticks
        # TICK_RATE is typically 0.016 (60 ticks/sec)
        dt = 0.05  # 50ms - should run ~3 ticks

        self.scene._update_visual(dt)

        assert self.scene.sim_tick_counter >= 2

    def test_turbo_mode_runs_fixed_ticks_per_frame(self):
        """Test turbo mode (>10x speed) runs fixed N ticks per frame."""
        start_battle_screen_with_minimal_spec(
            self.scene, {0: [self.ship1], 1: [self.ship2]}, headless=False,
        )
        self.scene.sim_paused = False
        self.scene.sim_speed_multiplier = 100.0  # Turbo mode
        self.scene._accumulator = 0.0

        self.scene._update_visual(0.016)

        # In turbo mode, ticks_to_run = int(speed_mult) = 100
        assert self.scene.sim_tick_counter >= 50  # Should run many ticks

    def test_speed_limits_enforced(self):
        """Test speed multiplier is bounded by MIN and MAX."""
        start_battle_screen_with_minimal_spec(
            self.scene, {0: [self.ship1], 1: [self.ship2]}, headless=False,
        )

        # Try to go below minimum
        self.scene.sim_speed_multiplier = MIN_SPEED_MULTIPLIER
        event = MagicMock()
        event.type = pygame.KEYDOWN
        event.key = pygame.K_COMMA

        self.scene.handle_event(event)

        assert self.scene.sim_speed_multiplier >= MIN_SPEED_MULTIPLIER

        # Try to go above maximum
        self.scene.sim_speed_multiplier = MAX_SPEED_MULTIPLIER
        event.key = pygame.K_PERIOD

        self.scene.handle_event(event)

        assert self.scene.sim_speed_multiplier <= MAX_SPEED_MULTIPLIER


class TestBattleScreenControllerIntegration:
    """Test BattleScreen controller integration methods."""

    @pytest.fixture(autouse=True)
    def setup_scene(self, fresh_registries):
        """Set up BattleScreen."""
        with patch('game.ui.screens.battle_screen.BattleUI') as MockUI:
            self.scene = BattleScreen(800, 600)
            self.scene.ui = MockUI.return_value
            self.scene.ui.show_overlay = False
            self.scene.ui.expanded_ships = set()
            self.scene.ui.stats_scroll_offset = 0

            self.fresh_registries = fresh_registries
            yield

    def test_start_battle_sets_controller_and_service(self):
        """Test start_battle() sets controller and service references."""
        mock_controller = MagicMock()
        mock_service = MagicMock()
        mock_controller.service = mock_service
        mock_controller.config = MagicMock()
        mock_controller.config.headless = False
        mock_controller.config.start_paused = True

        mock_engine = MagicMock()
        mock_engine.ships = []
        mock_engine.combat_events = MagicMock()
        mock_service.get_engine.return_value = mock_engine

        self.scene.start_battle(mock_controller)

        assert self.scene._controller == mock_controller
        assert self.scene._battle_service == mock_service
        assert self.scene.sim_paused is True

    def test_get_controller_returns_current_controller(self):
        """Test get_controller() returns current controller."""
        mock_controller = MagicMock()
        mock_controller.service = MagicMock()
        mock_controller.config = MagicMock()
        mock_controller.config.headless = False
        mock_controller.config.start_paused = False

        mock_engine = MagicMock()
        mock_engine.ships = []
        mock_engine.combat_events = MagicMock()
        mock_controller.service.get_engine.return_value = mock_engine

        self.scene.start_battle(mock_controller)

        assert self.scene.get_controller() == mock_controller


class TestBattleScreenCycleFocus:
    """Test BattleScreen cycle focus ship functionality."""

    @pytest.fixture(autouse=True)
    def setup_scene(self, ship_templates):
        """Set up BattleScreen with multiple ships."""
        with patch('game.ui.screens.battle_screen.BattleUI') as MockUI:
            self.scene = BattleScreen(800, 600)
            self.scene.ui = MockUI.return_value
            self.scene.ui.show_overlay = False

            self.ship1 = copy.deepcopy(ship_templates[0])
            self.ship2 = copy.deepcopy(ship_templates[1])
            self.ship3 = copy.deepcopy(ship_templates[2])

            yield

    def test_cycle_focus_forward(self):
        """Test cycling focus forward through ships."""
        start_battle_screen_with_minimal_spec(
            self.scene, {0: [self.ship1, self.ship3], 1: [self.ship2]}, headless=False,
        )
        self.scene.camera.target = None

        # Cycle forward
        self.scene._cycle_focus_ship(1)

        assert self.scene.camera.target is not None

    def test_cycle_focus_backward(self):
        """Test cycling focus backward through ships."""
        start_battle_screen_with_minimal_spec(
            self.scene, {0: [self.ship1, self.ship3], 1: [self.ship2]}, headless=False,
        )
        self.scene.camera.target = self.ship1

        # Cycle backward
        self.scene._cycle_focus_ship(-1)

        # Should wrap to last ship
        assert self.scene.camera.target is not None

    def test_cycle_focus_skips_dead_ships(self):
        """Test cycling focus skips dead ships."""
        start_battle_screen_with_minimal_spec(
            self.scene, {0: [self.ship1, self.ship3], 1: [self.ship2]}, headless=False,
        )
        self.ship1.is_alive = False
        self.scene.camera.target = self.ship3

        # Cycle forward
        self.scene._cycle_focus_ship(1)

        # Should skip dead ship1
        assert self.scene.camera.target != self.ship1 or self.scene.camera.target.is_alive

    def test_cycle_focus_no_ships_alive(self):
        """Test cycling focus when no ships are alive does nothing."""
        start_battle_screen_with_minimal_spec(
            self.scene, {0: [self.ship1], 1: [self.ship2]}, headless=False,
        )
        self.ship1.is_alive = False
        self.ship2.is_alive = False
        self.scene.camera.target = None

        # Should not crash with no alive ships
        self.scene._cycle_focus_ship(1)

        # Target should remain None
        assert self.scene.camera.target is None

    def test_keyboard_bracket_keys_cycle_focus(self):
        """Test keyboard bracket keys cycle focus."""
        start_battle_screen_with_minimal_spec(
            self.scene, {0: [self.ship1, self.ship3], 1: [self.ship2]}, headless=False,
        )
        self.scene.camera.target = None

        event = MagicMock()
        event.type = pygame.KEYDOWN
        event.key = pygame.K_RIGHTBRACKET

        self.scene.handle_event(event)

        assert self.scene.camera.target is not None
