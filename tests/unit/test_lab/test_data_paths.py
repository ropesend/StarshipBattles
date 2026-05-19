"""Tests for Combat Lab data path construction.

Ensures that ship JSON and component JSON files are loaded from the correct
paths (combat_lab/data/) rather than incorrect relative paths.
"""
import os
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock


class TestDataPathConstruction:
    """Tests that data paths resolve to combat_lab/data/ directory."""

    def test_combat_lab_data_directory_exists(self):
        """The combat_lab/data directory should exist at project root."""
        # Get project root (go up from tests/unit/test_lab/)
        project_root = Path(__file__).parent.parent.parent.parent
        data_dir = project_root / 'combat_lab' / 'data'

        assert data_dir.exists(), f"Expected {data_dir} to exist"
        assert data_dir.is_dir(), f"Expected {data_dir} to be a directory"

    def test_ships_directory_exists(self):
        """The combat_lab/data/ships directory should exist."""
        project_root = Path(__file__).parent.parent.parent.parent
        ships_dir = project_root / 'combat_lab' / 'data' / 'ships'

        assert ships_dir.exists(), f"Expected {ships_dir} to exist"
        assert ships_dir.is_dir(), f"Expected {ships_dir} to be a directory"

    def test_components_json_exists(self):
        """The combat_lab/data/components.json file should exist."""
        project_root = Path(__file__).parent.parent.parent.parent
        components_file = project_root / 'combat_lab' / 'data' / 'components.json'

        assert components_file.exists(), f"Expected {components_file} to exist"
        assert components_file.is_file(), f"Expected {components_file} to be a file"


class TestExtractShipsFromScenario:
    """Tests for _extract_ships_from_scenario path construction."""

    @pytest.fixture
    def mock_test_lab_screen(self):
        """Create a minimal TestLabScreen for testing path construction."""
        from game.ui.screens.test_lab import TestLabScreen
        from game.ui.screens.test_lab.data_extractor import TestLabDataExtractor

        with patch.object(TestLabScreen, '__init__', lambda self, game, w, h: None):
            screen = TestLabScreen.__new__(TestLabScreen)
            screen.registry = Mock()
            # Create data extractor (delegated methods require this)
            screen._data_extractor = TestLabDataExtractor(screen.registry)
            return screen

    def test_extract_ships_uses_correct_path(self, mock_test_lab_screen):
        """_extract_ships_from_scenario should use project root for data paths."""
        # Setup mock scenario with a ship file reference
        mock_metadata = Mock()
        mock_metadata.conditions = ["Attacker: Test_Attacker_Beam360_Low.json"]

        mock_test_lab_screen.registry.get_by_id.return_value = {
            'metadata': mock_metadata,
            'class': None
        }

        # Track what path is used for loading
        loaded_paths = []

        def track_load_json(path, **kwargs):
            loaded_paths.append(path)
            # Return valid ship data
            return {
                'name': 'Test Ship',
                'layers': {
                    'CORE': [{'id': 'test_component'}],
                    'ARMOR': [],
                    'HULL': []
                }
            }

        with patch('game.ui.screens.test_lab.data_extractor.load_json', side_effect=track_load_json):
            ships = mock_test_lab_screen._extract_ships_from_scenario('TEST-001')

        # Verify path was constructed correctly
        assert len(loaded_paths) == 1
        loaded_path = loaded_paths[0]

        # Path should end with combat_lab/data/ships/filename
        assert 'combat_lab' in loaded_path, \
            f"Path should contain 'combat_lab': {loaded_path}"
        assert loaded_path.endswith('Test_Attacker_Beam360_Low.json'), \
            f"Path should end with ship filename: {loaded_path}"

        # Critical: Path should NOT contain 'game/ui/combat_lab'
        assert 'game\\ui\\combat_lab' not in loaded_path and \
               'game/ui/combat_lab' not in loaded_path, \
            f"Path should NOT be relative to game/ui/: {loaded_path}"

    def test_extract_ships_returns_ship_data(self, mock_test_lab_screen):
        """_extract_ships_from_scenario should return ship data when file exists."""
        mock_metadata = Mock()
        mock_metadata.conditions = ["Ship: Test_Engine_1x_LowMass.json"]

        mock_test_lab_screen.registry.get_by_id.return_value = {
            'metadata': mock_metadata,
            'class': None
        }

        def mock_load_json(path, **kwargs):
            return {
                'name': 'Test Engine Ship',
                'layers': {
                    'CORE': [{'id': 'test_engine'}],
                    'ARMOR': [],
                    'HULL': []
                }
            }

        with patch('game.ui.screens.test_lab.data_extractor.load_json', side_effect=mock_load_json):
            ships = mock_test_lab_screen._extract_ships_from_scenario('TEST-001')

        assert len(ships) == 1
        assert ships[0]['role'] == 'Ship'
        assert ships[0]['filename'] == 'Test_Engine_1x_LowMass.json'
        assert ships[0]['ship_data']['name'] == 'Test Engine Ship'
        assert 'test_engine' in ships[0]['component_ids']


class TestShowShipsJson:
    """Tests for _show_ships_json path construction."""

    @pytest.fixture
    def mock_test_lab_screen(self):
        """Create a minimal TestLabScreen for testing."""
        from game.ui.screens.test_lab import TestLabScreen
        from game.ui.screens.test_lab.screen_actions import TestLabScreenActions
        from game.ui.screens.test_lab.viewmodel import TestLabViewModel

        with patch.object(TestLabScreen, '__init__', lambda self, game, w, h: None):
            screen = TestLabScreen.__new__(TestLabScreen)
            screen.registry = Mock()
            screen.ui_manager = Mock()
            # PROJ-172: json_popup is now a property delegating to viewmodel
            screen._viewmodel = Mock(spec=TestLabViewModel)
            screen._viewmodel.json_popup = None
            # PROJ-457 Phase 3: _show_ships_json moved to TestLabScreenActions.
            screen._actions = TestLabScreenActions(screen)
            return screen

    def test_show_ships_json_uses_correct_path(self, mock_test_lab_screen):
        """_show_ships_json should use project root for data paths."""
        mock_metadata = Mock()
        mock_metadata.conditions = ["Attacker: Test_Attacker_Beam360_Low.json"]

        mock_test_lab_screen.registry.get_by_id.return_value = {
            'metadata': mock_metadata
        }

        loaded_paths = []

        def track_load_json(path, **kwargs):
            loaded_paths.append(path)
            return {'name': 'Test Ship'}

        with patch('game.ui.screens.test_lab.screen_actions.load_json', side_effect=track_load_json):
            with patch('game.ui.screens.test_lab.screen_actions.JSONPopup'):
                with patch('game.ui.screens.test_lab.screen_actions.WIDTH', 1920):
                    with patch('game.ui.screens.test_lab.screen_actions.HEIGHT', 1080):
                        mock_test_lab_screen._actions._show_ships_json('TEST-001')

        assert len(loaded_paths) == 1
        loaded_path = loaded_paths[0]

        # Path should contain combat_lab at project root
        assert 'combat_lab' in loaded_path
        assert 'game\\ui\\combat_lab' not in loaded_path and \
               'game/ui/combat_lab' not in loaded_path, \
            f"Path should NOT be relative to game/ui/: {loaded_path}"


class TestShowComponentsJson:
    """Tests for _show_components_json path construction."""

    @pytest.fixture
    def mock_test_lab_screen(self):
        """Create a minimal TestLabScreen for testing."""
        from game.ui.screens.test_lab import TestLabScreen
        from game.ui.screens.test_lab.screen_actions import TestLabScreenActions
        from game.ui.screens.test_lab.viewmodel import TestLabViewModel

        with patch.object(TestLabScreen, '__init__', lambda self, game, w, h: None):
            screen = TestLabScreen.__new__(TestLabScreen)
            screen.ui_manager = Mock()
            # PROJ-172: json_popup is now a property delegating to viewmodel
            screen._viewmodel = Mock(spec=TestLabViewModel)
            screen._viewmodel.json_popup = None
            # PROJ-457 Phase 3: _show_components_json moved to TestLabScreenActions.
            screen._actions = TestLabScreenActions(screen)
            return screen

    def test_show_components_json_uses_correct_path(self, mock_test_lab_screen):
        """_show_components_json should use project root for data paths."""
        loaded_paths = []

        def track_load_json(path, **kwargs):
            loaded_paths.append(path)
            return {'components': []}

        with patch('game.ui.screens.test_lab.screen_actions.load_json', side_effect=track_load_json):
            with patch('game.ui.screens.test_lab.screen_actions.JSONPopup'):
                with patch('game.ui.screens.test_lab.screen_actions.WIDTH', 1920):
                    with patch('game.ui.screens.test_lab.screen_actions.HEIGHT', 1080):
                        mock_test_lab_screen._actions._show_components_json()

        assert len(loaded_paths) == 1
        loaded_path = loaded_paths[0]

        # Path should be combat_lab/data/components.json
        assert 'combat_lab' in loaded_path
        assert 'components.json' in loaded_path
        assert 'game\\ui\\combat_lab' not in loaded_path and \
               'game/ui/combat_lab' not in loaded_path, \
            f"Path should NOT be relative to game/ui/: {loaded_path}"


class TestLoadComponentData:
    """Tests for _load_component_data path construction."""

    @pytest.fixture
    def mock_test_lab_screen(self):
        """Create a minimal TestLabScreen for testing."""
        from game.ui.screens.test_lab import TestLabScreen
        from game.ui.screens.test_lab.data_extractor import TestLabDataExtractor

        with patch.object(TestLabScreen, '__init__', lambda self, game, w, h: None):
            screen = TestLabScreen.__new__(TestLabScreen)
            screen.registry = Mock()
            # Create data extractor (delegated methods require this)
            screen._data_extractor = TestLabDataExtractor(screen.registry)
            return screen

    def test_load_component_data_uses_correct_path(self, mock_test_lab_screen):
        """_load_component_data should use project root for data paths."""
        loaded_paths = []

        def track_load_json(path, **kwargs):
            loaded_paths.append(path)
            return {
                'components': [
                    {'id': 'test_component', 'name': 'Test'}
                ]
            }

        with patch('game.ui.screens.test_lab.data_extractor.load_json', side_effect=track_load_json):
            result = mock_test_lab_screen._load_component_data('test_component')

        assert len(loaded_paths) == 1
        loaded_path = loaded_paths[0]

        assert 'combat_lab' in loaded_path
        assert 'components.json' in loaded_path
        assert 'game\\ui\\combat_lab' not in loaded_path and \
               'game/ui/combat_lab' not in loaded_path


class TestPathHelperFunction:
    """Tests for the get_test_data_dir helper function."""

    def test_get_test_data_dir_returns_correct_path(self):
        """get_test_data_dir should return path to combat_lab/data/."""
        from game.ui.screens.test_lab.data_extractor import get_test_data_dir

        data_dir = get_test_data_dir()

        # Should be a valid path
        assert os.path.isabs(data_dir) or data_dir.startswith('.'), \
            "Should return a path string"

        # Should end with combat_lab/data
        normalized = data_dir.replace('\\', '/')
        assert normalized.endswith('combat_lab/data'), \
            f"Path should end with 'combat_lab/data': {data_dir}"

        # Should actually exist
        assert os.path.exists(data_dir), \
            f"Path should exist: {data_dir}"

    def test_get_test_data_dir_ships_subdir_exists(self):
        """Ships subdirectory should exist within test data dir."""
        from game.ui.screens.test_lab.data_extractor import get_test_data_dir

        data_dir = get_test_data_dir()
        ships_dir = os.path.join(data_dir, 'ships')

        assert os.path.exists(ships_dir), \
            f"Ships directory should exist: {ships_dir}"
        assert os.path.isdir(ships_dir), \
            f"Ships path should be a directory: {ships_dir}"
