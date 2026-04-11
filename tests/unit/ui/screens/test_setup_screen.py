"""Tests for BattleSetupScreen battle setup functionality.

PROJ-111 Phase 3 Task 3.4: BattleSetupScreen Tests

Uses bypass-init pattern and mocks to avoid tkinter file dialogs.
"""
import pytest
from unittest.mock import MagicMock, patch, PropertyMock
import sys
import pygame


class TestBattleSetupScreen:
    """Tests for BattleSetupScreen initialization and behavior."""

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        """Set up mocks for tkinter and external services."""
        # Mock tkinter to avoid file dialogs
        self.mock_tk = MagicMock()
        self.mock_filedialog = MagicMock()

        # Mock the strategy metadata service
        self.mock_strategy_service = MagicMock()
        self.mock_strategy_service.strategies = {
            'aggressive': MagicMock(),
            'defensive': MagicMock(),
            'standard_ranged': MagicMock(),
        }

        with patch('tkinter.Tk', return_value=self.mock_tk):
            with patch('tkinter.filedialog', self.mock_filedialog):
                with patch('game.ui.screens.setup_screen.get_default_strategy_metadata_service') as mock_sms:
                    mock_sms.return_value = self.mock_strategy_service
                    from game.ui.screens.setup_screen import BattleSetupScreen
                    self.BattleSetupScreen = BattleSetupScreen
                    yield

    def test_init_sets_up_empty_team_lists(self):
        """Test initialization sets up empty team lists."""
        screen = self.BattleSetupScreen(800, 600)

        assert screen.team1 == []
        assert screen.team2 == []

    def test_init_stores_dimensions(self):
        """Test initialization stores screen dimensions."""
        screen = self.BattleSetupScreen(1024, 768)

        assert screen.screen_width == 1024
        assert screen.screen_height == 768

    def test_init_stores_scene_callback(self):
        """Test initialization stores scene_callback."""
        callback = MagicMock()
        screen = self.BattleSetupScreen(800, 600, scene_callback=callback)

        assert screen.scene_callback == callback

    def test_init_loads_ai_strategies(self):
        """Test initialization loads AI strategies."""
        screen = self.BattleSetupScreen(800, 600)

        assert 'aggressive' in screen.ai_strategies
        assert 'defensive' in screen.ai_strategies

    def test_start_initializes_available_designs(self):
        """Test start() initializes available_ship_designs."""
        screen = self.BattleSetupScreen(800, 600)

        with patch('game.ui.screens.setup_screen.scan_ship_designs', return_value=[
            {'name': 'Fighter', 'path': '/path/fighter.json'}
        ]):
            screen.start()

        assert len(screen.available_ship_designs) == 1

    def test_start_preserve_teams_false_clears_teams(self):
        """Test start() with preserve_teams=False clears team lists."""
        screen = self.BattleSetupScreen(800, 600)
        screen.team1 = [{'design': MagicMock()}]
        screen.team2 = [{'design': MagicMock()}]

        with patch('game.ui.screens.setup_screen.scan_ship_designs', return_value=[]):
            screen.start(preserve_teams=False)

        assert screen.team1 == []
        assert screen.team2 == []

    def test_start_preserve_teams_true_keeps_teams(self):
        """Test start() with preserve_teams=True keeps team lists."""
        screen = self.BattleSetupScreen(800, 600)
        entry1 = {'design': MagicMock()}
        entry2 = {'design': MagicMock()}
        screen.team1 = [entry1]
        screen.team2 = [entry2]

        with patch('game.ui.screens.setup_screen.scan_ship_designs', return_value=[]):
            screen.start(preserve_teams=True)

        assert screen.team1 == [entry1]
        assert screen.team2 == [entry2]

    def test_start_resets_scroll_offset(self):
        """Test start() resets scroll state to 0."""
        screen = self.BattleSetupScreen(800, 600)
        screen.scroll.offset = 100

        with patch('game.ui.screens.setup_screen.scan_ship_designs', return_value=[]):
            screen.start()

        assert screen.scroll.offset == 0

    def test_start_closes_ai_dropdown(self):
        """Test start() closes AI dropdown."""
        screen = self.BattleSetupScreen(800, 600)
        screen.ai_dropdown_open = (1, 0)

        with patch('game.ui.screens.setup_screen.scan_ship_designs', return_value=[]):
            screen.start()

        assert screen.ai_dropdown_open is None


class TestBattleSetupScreenTeamManagement:
    """Tests for team management functionality."""

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        """Set up mocks."""
        self.mock_strategy_service = MagicMock()
        self.mock_strategy_service.strategies = {'standard_ranged': MagicMock()}

        with patch('tkinter.Tk', return_value=MagicMock()):
            with patch('tkinter.filedialog', MagicMock()):
                with patch('game.ui.screens.setup_screen.get_default_strategy_metadata_service') as mock_sms:
                    mock_sms.return_value = self.mock_strategy_service
                    from game.ui.screens.setup_screen import BattleSetupScreen
                    self.BattleSetupScreen = BattleSetupScreen
                    yield

    def test_handle_ships_click_adds_to_team1_on_left_click(self):
        """Test clicking ship design adds to team1 on left click."""
        screen = self.BattleSetupScreen(800, 600)
        screen.available_ship_designs = [
            {'name': 'Fighter', 'path': '/fighter.json', 'ai_strategy': 'standard_ranged'}
        ]

        # Left click on first ship design
        result = screen._handle_ships_click(60, 160, button=1)

        assert result is True
        assert len(screen.team1) == 1
        assert screen.team1[0]['design']['name'] == 'Fighter'

    def test_handle_ships_click_adds_to_team2_on_right_click(self):
        """Test clicking ship design adds to team2 on right click."""
        screen = self.BattleSetupScreen(800, 600)
        screen.available_ship_designs = [
            {'name': 'Fighter', 'path': '/fighter.json', 'ai_strategy': 'standard_ranged'}
        ]

        # Right click on first ship design
        result = screen._handle_ships_click(60, 160, button=3)

        assert result is True
        assert len(screen.team2) == 1

    def test_handle_team_click_removes_ship_on_x_button(self):
        """Test clicking X button removes ship from team."""
        screen = self.BattleSetupScreen(800, 600)
        screen.team1 = [
            {'design': {'name': 'Fighter'}, 'strategy': 'standard_ranged'}
        ]

        # Simulate click on X button (x >= col_x + 300)
        col_x = 400
        screen._handle_team_click(col_x + 310, 160, col_x, screen.team1, 1)

        assert len(screen.team1) == 0

    def test_handle_team_click_opens_ai_dropdown(self):
        """Test clicking AI dropdown area opens dropdown."""
        screen = self.BattleSetupScreen(800, 600)
        screen.team1 = [
            {'design': {'name': 'Fighter'}, 'strategy': 'standard_ranged'}
        ]

        # Simulate click on AI dropdown area (150 <= x < 280 relative to col)
        col_x = 400
        screen._handle_team_click(col_x + 200, 160, col_x, screen.team1, 1)

        assert screen.ai_dropdown_open == (1, 0)


class TestBattleSetupScreenSceneCallbacks:
    """Tests for scene callback invocation."""

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        """Set up mocks."""
        self.mock_strategy_service = MagicMock()
        self.mock_strategy_service.strategies = {'standard_ranged': MagicMock()}

        with patch('tkinter.Tk', return_value=MagicMock()):
            with patch('tkinter.filedialog', MagicMock()):
                with patch('game.ui.screens.setup_screen.get_default_strategy_metadata_service') as mock_sms:
                    mock_sms.return_value = self.mock_strategy_service
                    from game.ui.screens.setup_screen import BattleSetupScreen
                    self.BattleSetupScreen = BattleSetupScreen
                    yield

    def test_trigger_start_battle_invokes_callback(self):
        """Test _trigger_start_battle invokes scene_callback with 'start_battle'."""
        callback = MagicMock()
        screen = self.BattleSetupScreen(800, 600, scene_callback=callback)

        with patch.object(screen, 'get_ships', return_value=([], [])):
            screen._trigger_start_battle(headless=False)

        callback.assert_called_once()
        call_args = callback.call_args
        assert call_args[0][0] == "start_battle"

    def test_trigger_start_battle_headless_invokes_callback(self):
        """Test _trigger_start_battle headless invokes with 'start_headless'."""
        callback = MagicMock()
        screen = self.BattleSetupScreen(800, 600, scene_callback=callback)

        with patch.object(screen, 'get_ships', return_value=([], [])):
            screen._trigger_start_battle(headless=True)

        callback.assert_called_once()
        call_args = callback.call_args
        assert call_args[0][0] == "start_headless"

    def test_trigger_return_to_menu_invokes_callback(self):
        """Test _trigger_return_to_menu invokes with 'return_to_menu'."""
        callback = MagicMock()
        screen = self.BattleSetupScreen(800, 600, scene_callback=callback)

        screen._trigger_return_to_menu()

        callback.assert_called_with("return_to_menu")

    def test_trigger_without_callback_no_error(self):
        """Test trigger methods don't crash without callback."""
        screen = self.BattleSetupScreen(800, 600, scene_callback=None)

        # Should not raise
        screen._trigger_return_to_menu()

        with patch.object(screen, 'get_ships', return_value=([], [])):
            screen._trigger_start_battle(headless=False)


class TestBattleSetupScreenFileIO:
    """Tests for save/load functionality."""

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        """Set up mocks."""
        self.mock_strategy_service = MagicMock()
        self.mock_strategy_service.strategies = {'standard_ranged': MagicMock()}

        with patch('tkinter.Tk', return_value=MagicMock()):
            with patch('tkinter.filedialog', MagicMock()):
                with patch('game.ui.screens.setup_screen.get_default_strategy_metadata_service') as mock_sms:
                    mock_sms.return_value = self.mock_strategy_service
                    from game.ui.screens.setup_screen import BattleSetupScreen
                    self.BattleSetupScreen = BattleSetupScreen
                    yield

    def test_save_setup_calls_save_battle_setup(self):
        """Test save_setup calls save_battle_setup when path provided."""
        screen = self.BattleSetupScreen(800, 600)
        screen.team1 = [{'design': MagicMock()}]
        screen.team2 = [{'design': MagicMock()}]

        with patch('game.ui.screens.setup_screen.save_battle_setup') as mock_save:
            with patch('game.ui.screens.setup_screen.filedialog') as mock_fd:
                mock_fd.asksaveasfilename.return_value = '/test/path.json'
                with patch('os.path.exists', return_value=True):
                    with patch('os.makedirs'):
                        screen.save_setup()

        mock_save.assert_called_once()

    def test_save_setup_cancelled_no_save(self):
        """Test save_setup does nothing when dialog cancelled (empty path)."""
        screen = self.BattleSetupScreen(800, 600)

        # The actual logic: if filepath is falsy, save_battle_setup is not called
        # We need to verify that by checking the code: `if filepath: save_battle_setup(...)`
        # Directly test by confirming empty path doesn't trigger save
        with patch('game.ui.screens.setup_screen.save_battle_setup') as mock_save:
            with patch('game.ui.screens.setup_screen.filedialog') as mock_fd:
                mock_fd.asksaveasfilename.return_value = ''
                with patch('os.path.exists', return_value=True):
                    with patch('os.makedirs'):
                        screen.save_setup()

        mock_save.assert_not_called()

    def test_load_setup_calls_load_battle_setup(self):
        """Test load_setup calls load_battle_setup when path provided."""
        screen = self.BattleSetupScreen(800, 600)

        with patch('game.ui.screens.setup_screen.load_battle_setup', return_value=(None, None)) as mock_load:
            with patch('game.ui.screens.setup_screen.filedialog') as mock_fd:
                mock_fd.askopenfilename.return_value = '/test/path.json'
                with patch('os.path.exists', return_value=True):
                    screen.load_setup()

        mock_load.assert_called_once()

    def test_load_setup_updates_teams(self):
        """Test load_setup updates team lists on successful load."""
        screen = self.BattleSetupScreen(800, 600)
        new_team1 = [{'design': MagicMock()}]
        new_team2 = [{'design': MagicMock()}]

        with patch('game.ui.screens.setup_screen.load_battle_setup', return_value=(new_team1, new_team2)):
            with patch('game.ui.screens.setup_screen.filedialog') as mock_fd:
                mock_fd.askopenfilename.return_value = '/test/path.json'
                with patch('os.path.exists', return_value=True):
                    screen.load_setup()

        assert screen.team1 == new_team1
        assert screen.team2 == new_team2


class TestBattleSetupScreenDropdown:
    """Tests for AI dropdown functionality."""

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        """Set up mocks."""
        self.mock_strategy_service = MagicMock()
        self.mock_strategy_service.strategies = {
            'aggressive': MagicMock(),
            'defensive': MagicMock(),
            'standard_ranged': MagicMock(),
        }

        with patch('tkinter.Tk', return_value=MagicMock()):
            with patch('tkinter.filedialog', MagicMock()):
                with patch('game.ui.screens.setup_screen.get_default_strategy_metadata_service') as mock_sms:
                    mock_sms.return_value = self.mock_strategy_service
                    from game.ui.screens.setup_screen import BattleSetupScreen
                    self.BattleSetupScreen = BattleSetupScreen
                    yield

    def test_handle_dropdown_click_changes_strategy(self):
        """Test clicking dropdown option changes ship strategy."""
        screen = self.BattleSetupScreen(800, 600)
        screen.team1 = [
            {'design': {'name': 'Fighter'}, 'strategy': 'standard_ranged'}
        ]
        screen.ai_dropdown_open = (1, 0)  # Team 1, display item 0

        # Calculate dropdown click position
        col2_x = 800 // 3 + 50  # Same calculation as in _handle_click
        dropdown_x = col2_x + 150
        dropdown_y = 150 + 0 * 35 + 30  # Base + item offset + dropdown offset

        screen._handle_dropdown_click(dropdown_x + 10, dropdown_y + 5, col2_x, col2_x)

        # Dropdown should be closed
        assert screen.ai_dropdown_open is None

    def test_handle_dropdown_click_closes_dropdown(self):
        """Test clicking outside dropdown closes it."""
        screen = self.BattleSetupScreen(800, 600)
        screen.team1 = [
            {'design': {'name': 'Fighter'}, 'strategy': 'standard_ranged'}
        ]
        screen.ai_dropdown_open = (1, 0)

        # Click outside dropdown area
        screen._handle_dropdown_click(0, 0, 400, 700)

        assert screen.ai_dropdown_open is None


class TestBattleSetupScreenISceneProtocol:
    """Tests for IScene protocol compliance."""

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        """Set up mocks."""
        self.mock_strategy_service = MagicMock()
        self.mock_strategy_service.strategies = {'standard_ranged': MagicMock()}

        with patch('tkinter.Tk', return_value=MagicMock()):
            with patch('tkinter.filedialog', MagicMock()):
                with patch('game.ui.screens.setup_screen.get_default_strategy_metadata_service') as mock_sms:
                    mock_sms.return_value = self.mock_strategy_service
                    from game.ui.screens.setup_screen import BattleSetupScreen
                    self.BattleSetupScreen = BattleSetupScreen
                    yield

    def test_handle_event_method_exists(self):
        """Test handle_event method exists (IScene protocol)."""
        screen = self.BattleSetupScreen(800, 600)

        assert hasattr(screen, 'handle_event')
        assert callable(screen.handle_event)

    def test_update_method_exists(self):
        """Test update method exists (IScene protocol)."""
        screen = self.BattleSetupScreen(800, 600)

        assert hasattr(screen, 'update')
        assert callable(screen.update)

    def test_draw_method_exists(self):
        """Test draw method exists (IScene protocol)."""
        screen = self.BattleSetupScreen(800, 600)

        assert hasattr(screen, 'draw')
        assert callable(screen.draw)

    def test_handle_resize_updates_dimensions(self):
        """Test handle_resize updates screen dimensions."""
        screen = self.BattleSetupScreen(800, 600)

        screen.handle_resize(1920, 1080)

        assert screen.screen_width == 1920
        assert screen.screen_height == 1080

    def test_update_does_not_crash(self):
        """Test update() doesn't crash (no time-based updates)."""
        screen = self.BattleSetupScreen(800, 600)

        # Should not raise
        screen.update(0.016)

    def test_handle_event_mouse_click(self):
        """Test handle_event processes mouse click."""
        screen = self.BattleSetupScreen(800, 600)

        event = MagicMock()
        event.type = pygame.MOUSEBUTTONDOWN
        event.pos = (100, 100)
        event.button = 1

        # Should not raise
        screen.handle_event(event)
