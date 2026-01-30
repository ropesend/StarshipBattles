"""Shared fixtures for battle coordinator tests."""
import pytest
from unittest.mock import Mock


@pytest.fixture
def mock_game():
    """Create a mock Game object."""
    game = Mock()
    game._battle_accumulator = 0.0
    return game


@pytest.fixture
def mock_battle_scene():
    """Create a mock BattleScreen object."""
    scene = Mock()
    scene.sim_tick_counter = 0
    scene.sim_paused = False
    scene.sim_speed_multiplier = 1.0
    scene.headless_mode = True
    scene.test_mode = False
    scene.is_battle_over.return_value = False
    scene.ships = []
    scene.tick_rate_count = 0
    scene.tick_rate_timer = 0.0
    scene.current_tick_rate = 0

    # Camera
    scene.camera = Mock()
    scene.camera.zoom = 1.0

    # UI
    scene.ui = Mock()
    scene.ui.seeker_panel = Mock()
    scene.ui.seeker_panel.rect = Mock()
    scene.ui.seeker_panel.rect.width = 200

    # Engine
    scene.engine = Mock()

    return scene


@pytest.fixture
def mock_screen():
    """Create a mock pygame screen surface."""
    screen = Mock()
    screen.get_width.return_value = 1920
    screen.get_height.return_value = 1080
    return screen


@pytest.fixture
def mock_font():
    """Create a mock pygame font."""
    font = Mock()
    font.render.return_value = Mock()
    return font
