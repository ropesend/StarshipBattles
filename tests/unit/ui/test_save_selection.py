"""
Tests for SaveSelectionWindow with turn list feature.

PROJ-322 Task 2.18 (S09-CAT5-001): the three byte-identical
`setup_tmpdir` autouse fixtures formerly on
`TestSaveSelectionTurnList`, `TestSaveSelectionListSaves` and
`TestSaveSelectionEmpireInfo` are now provided by the module-level
`patched_saves_tmpdir` autouse fixture below.
"""
import pytest
import tempfile
import shutil
import os
from unittest.mock import MagicMock, patch

from game.strategy.systems.save_game_service import SaveGameService
from game.strategy.engine.game_config import GameConfig
from game.core import paths as paths_module


@pytest.fixture(autouse=True)
def _patched_saves_tmpdir():
    """Per-test temporary saves directory + Paths.SAVES_DIR patch.

    PROJ-322 Task 2.18 (S09-CAT5-001): hoisted from three duplicate
    class-local autouse fixtures.
    PROJ-494 Task 1.1: promoted to module-level autouse so per-class
    thin wrappers can be deleted.
    """
    tmpdir = tempfile.mkdtemp()
    saves_dir = os.path.join(tmpdir, "saves")
    os.makedirs(saves_dir, exist_ok=True)
    with patch.object(paths_module.Paths, 'SAVES_DIR', saves_dir):
        yield tmpdir
    shutil.rmtree(tmpdir, ignore_errors=True)


@pytest.fixture
def _pygame_manager(request):
    """Set up pygame + pygame_gui UIManager and attach to the test instance.

    PROJ-494 Task 1.1: extracted from TestSaveSelectionWindowButtons and
    TestSaveSelectionTimestampParsing setup_tmpdir fixtures so they no
    longer duplicate this block.
    """
    import pygame
    import pygame_gui
    os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
    if not pygame.get_init():
        pygame.init()
    pygame.display.set_mode((1440, 900), pygame.NOFRAME)
    request.instance.manager = pygame_gui.UIManager((1440, 900))
    yield request.instance.manager


# PROJ-479 Task 6.1 (HLP-001): MockGameSession moved to
# tests/unit/strategy/save_game_service/conftest.py. The canonical version
# accepts an optional `config=` kwarg this file doesn't pass, but the default
# `GameConfig()` is equivalent.
from tests.unit.strategy.save_game_service.conftest import (  # noqa: E402
    MockGameSession,
)


class TestSaveSelectionTurnList:
    """Tests for turn list functionality in save selection."""

    def test_list_turns_returns_all_turns(self):
        """list_turns() returns metadata for each turn file."""
        session = MockGameSession(turn_number=1)

        # Create save with multiple turns
        success, _, save_path = SaveGameService.save_game(session, "TurnListTest")
        session.save_path = save_path

        session.turn_number = 2
        SaveGameService.save_game(session)

        session.turn_number = 3
        SaveGameService.save_game(session)

        # List turns
        turns = SaveGameService.list_turns(save_path)

        assert len(turns) == 3
        turn_numbers = [t['turn_number'] for t in turns]
        assert turn_numbers == [1, 2, 3]

    def test_list_turns_includes_metadata(self):
        """Each turn entry includes filename, timestamp, and size."""
        session = MockGameSession(turn_number=1)
        success, _, save_path = SaveGameService.save_game(session, "MetadataTest")

        turns = SaveGameService.list_turns(save_path)

        assert len(turns) == 1
        turn = turns[0]

        assert 'turn_number' in turn
        assert 'filename' in turn
        assert 'timestamp' in turn
        assert 'size' in turn
        assert 'path' in turn

        assert turn['turn_number'] == 1
        assert turn['filename'] == 'turn_1.json'

    def test_loading_save_defaults_to_latest(self):
        """Loading without turn_number loads latest turn."""
        session = MockGameSession(turn_number=1)
        success, _, save_path = SaveGameService.save_game(session, "LatestTest")
        session.save_path = save_path

        session.turn_number = 2
        SaveGameService.save_game(session)

        session.turn_number = 5
        SaveGameService.save_game(session)

        # Load without specifying turn
        loaded, message = SaveGameService.load_game(save_path)

        assert loaded is not None
        assert loaded.turn_number == 5

    def test_loading_specific_turn(self):
        """load_game(path, turn_number=N) loads specific turn state."""
        session = MockGameSession(turn_number=1)
        success, _, save_path = SaveGameService.save_game(session, "SpecificTurnTest")
        session.save_path = save_path

        session.turn_number = 2
        SaveGameService.save_game(session)

        session.turn_number = 3
        SaveGameService.save_game(session)

        # Load specific turn
        loaded, message = SaveGameService.load_game(save_path, turn_number=2)

        assert loaded is not None
        assert loaded.turn_number == 2

    def test_loading_nonexistent_turn_fails(self):
        """Loading turn that doesn't exist returns error."""
        session = MockGameSession(turn_number=1)
        success, _, save_path = SaveGameService.save_game(session, "NonexistentTest")

        # Try to load turn 5 when only turn 1 exists
        loaded, message = SaveGameService.load_game(save_path, turn_number=5)

        assert loaded is None
        assert "5" in message


class TestSaveSelectionListSaves:
    """Tests for save listing functionality."""

    def test_list_saves_returns_all_saves(self):
        """list_saves() returns all available saves."""
        # Create multiple saves - each needs a fresh session to avoid save_path reuse
        session1 = MockGameSession(turn_number=1)
        session2 = MockGameSession(turn_number=1)
        session3 = MockGameSession(turn_number=1)

        SaveGameService.save_game(session1, "Save1")
        SaveGameService.save_game(session2, "Save2")
        SaveGameService.save_game(session3, "Save3")

        saves = SaveGameService.list_saves()

        assert len(saves) == 3
        save_names = [s['save_name'] for s in saves]
        assert "Save1" in save_names
        assert "Save2" in save_names
        assert "Save3" in save_names

    def test_list_saves_includes_metadata(self):
        """Each save includes relevant metadata for display."""
        session = MockGameSession(turn_number=1)
        session.config.players[0].name = "Test Player"

        SaveGameService.save_game(session, "MetadataTest")

        saves = SaveGameService.list_saves()

        assert len(saves) == 1
        save = saves[0]

        assert 'save_name' in save
        assert 'save_path' in save
        assert 'player_name' in save
        assert 'turn_number' in save
        assert 'timestamp' in save

    def test_list_saves_sorted_by_timestamp(self):
        """Saves are sorted by timestamp (newest first).

        PROJ-322 Task 4.8 (S09-CAT7-001): replaced the sleep(0.1) with
        an explicit os.utime backdating of the older save's metadata
        file, so the ordering is deterministic instead of depending on
        wall-clock progression and filesystem mtime resolution.
        """
        # Create separate sessions to avoid save_path reuse
        session1 = MockGameSession(turn_number=1)
        session2 = MockGameSession(turn_number=1)

        success_old, _, old_path = SaveGameService.save_game(session1, "OldSave")
        success_new, _, new_path = SaveGameService.save_game(session2, "NewSave")
        assert success_old and success_new

        # Backdate the OldSave's metadata file by ~10 seconds so the
        # st_mtime-based sort in SaveGameService.list_saves places
        # NewSave first regardless of how close the two saves landed.
        old_metadata = os.path.join(old_path, "save_metadata.json")
        new_metadata = os.path.join(new_path, "save_metadata.json")
        new_mtime_ns = os.stat(new_metadata).st_mtime_ns
        backdated_ns = new_mtime_ns - 10 * 1_000_000_000  # 10 s earlier
        os.utime(old_metadata, ns=(backdated_ns, backdated_ns))

        saves = SaveGameService.list_saves()

        # Newest first
        assert saves[0]['save_name'] == "NewSave"
        assert saves[1]['save_name'] == "OldSave"


class TestSaveSelectionEmpireInfo:
    """Tests for empire information in save metadata."""

    def test_save_metadata_includes_empire_count(self):
        """Metadata includes number of empires."""
        session = MockGameSession(turn_number=1, num_empires=3)
        success, _, save_path = SaveGameService.save_game(session, "EmpireCountTest")

        info = SaveGameService.get_save_info(save_path)

        assert info['empire_count'] == 3

    def test_save_metadata_includes_empire_names(self):
        """Metadata includes list of empire names."""
        session = MockGameSession(turn_number=1, num_empires=2)
        session.empires[0].name = "Federation"
        session.empires[1].name = "Romulans"

        success, _, save_path = SaveGameService.save_game(session, "EmpireNamesTest")

        info = SaveGameService.get_save_info(save_path)

        assert "Federation" in info['empire_names']
        assert "Romulans" in info['empire_names']


class TestSaveSelectionWindowButtons:
    """Tests for SaveSelectionWindow button enable/disable behavior (BUG-30)."""

    @pytest.fixture(autouse=True)
    def _setup(self, _pygame_manager):
        """PROJ-494 T1.1: pygame+manager init now lives in `_pygame_manager`
        module fixture; `_patched_saves_tmpdir` is module-level autouse."""
        yield

    def test_buttons_enable_after_selection(self):
        """BUG-30: Load/Show Turns/Delete buttons should enable when save is selected."""
        import pygame
        import pygame_gui
        from game.ui.screens.save_selection_window import SaveSelectionWindow

        # Create a save first
        session = MockGameSession(turn_number=1)
        success, message, save_path = SaveGameService.save_game(session, "TestSave")
        assert success, f"Save failed: {message}"

        # Create window
        load_callback = MagicMock()
        cancel_callback = MagicMock()

        window = SaveSelectionWindow(
            rect=pygame.Rect(100, 100, 600, 500),
            manager=self.manager,
            on_load_callback=load_callback,
            on_cancel_callback=cancel_callback
        )

        # Verify buttons start disabled
        assert not window.btn_load.is_enabled
        assert not window.btn_expand.is_enabled
        assert not window.btn_delete.is_enabled

        # Verify save is in the list
        assert len(window.saves_list) == 1
        assert len(window.list_item_mapping) == 1

        # Simulate selecting the first save
        # UISelectionList.item_list returns dicts with "text", "selected", etc.
        items = window.saves_listbox.item_list
        assert len(items) > 0, "No items in saves list"

        # Get the first item - it's a dict with "text" key
        first_item = items[0]
        assert isinstance(first_item, dict)
        assert "text" in first_item

        # Simulate selection by marking the item as selected in the internal list
        first_item["selected"] = True

        # Process the selection change (this is what the event handler calls)
        window._handle_selection_change()

        # BUG-30: After selection, buttons should be enabled
        assert window.btn_load.is_enabled, "Load button should be enabled after selecting a save"
        assert window.btn_expand.is_enabled, "Show Turns button should be enabled after selecting a save"
        assert window.btn_delete.is_enabled, "Delete button should be enabled after selecting a save"

        # Clean up
        window.kill()


class TestSaveSelectionTimestampParsing:
    """Tests for timestamp parsing in save selection window (ERR-001)."""

    @pytest.fixture(autouse=True)
    def _setup(self, _pygame_manager):
        """PROJ-494 T1.1: pygame+manager init now lives in `_pygame_manager`
        module fixture; `_patched_saves_tmpdir` is module-level autouse."""
        yield

    def test_malformed_timestamp_handled_gracefully(self):
        """Malformed timestamp should not crash, should log warning."""
        import pygame
        from game.ui.screens.save_selection_window import SaveSelectionWindow
        from unittest.mock import patch

        # Patch SaveGameService where it's imported (inside the methods)
        with patch('game.strategy.systems.save_game_service.SaveGameService') as mock_svc:
            # Return a save with malformed timestamp
            mock_svc.list_saves.return_value = [{
                'save_name': 'TestSave',
                'player_name': 'Player',
                'latest_turn_number': 1,
                'empire_count': 1,
                'timestamp': 'not-a-valid-timestamp',
                'save_path': '/fake/path'
            }]
            mock_svc.list_turns.return_value = []

            with patch('game.ui.screens.save_selection_window.logger') as mock_log:
                window = SaveSelectionWindow(
                    rect=pygame.Rect(100, 100, 600, 500),
                    manager=self.manager,
                    on_load_callback=MagicMock(),
                    on_cancel_callback=MagicMock()
                )

                # Window should be created successfully
                assert window is not None
                assert len(window.saves_list) == 1

                # Should have logged a warning about the malformed timestamp
                mock_log.warning.assert_called()
                call_args = str(mock_log.warning.call_args)
                assert 'timestamp' in call_args.lower() or 'date' in call_args.lower()

                window.kill()

    def test_malformed_turn_timestamp_handled_gracefully(self):
        """Malformed turn timestamp should not crash, should log warning."""
        import pygame
        from game.ui.screens.save_selection_window import SaveSelectionWindow
        from unittest.mock import patch

        with patch('game.strategy.systems.save_game_service.SaveGameService') as mock_svc:
            # Return a valid save
            mock_svc.list_saves.return_value = [{
                'save_name': 'TestSave',
                'player_name': 'Player',
                'latest_turn_number': 2,
                'empire_count': 1,
                'timestamp': '2026-01-24T12:00:00',
                'save_path': '/fake/path'
            }]
            # Return turns with malformed timestamp
            mock_svc.list_turns.return_value = [
                {'turn_number': 1, 'timestamp': 'bad-timestamp'},
                {'turn_number': 2, 'timestamp': '2026-01-24T12:30:00'}
            ]

            with patch('game.ui.screens.save_selection_window.logger') as mock_log:
                window = SaveSelectionWindow(
                    rect=pygame.Rect(100, 100, 600, 500),
                    manager=self.manager,
                    on_load_callback=MagicMock(),
                    on_cancel_callback=MagicMock()
                )

                # Expand the save to trigger turn timestamp parsing
                window.expanded_save_idx = 0
                window._refresh_list_display()

                # Should have logged a warning about the malformed timestamp
                mock_log.warning.assert_called()

                window.kill()

    def test_valid_timestamps_parsed_correctly(self):
        """Valid ISO format timestamps should be parsed without warnings."""
        import pygame
        from game.ui.screens.save_selection_window import SaveSelectionWindow
        from unittest.mock import patch

        with patch('game.strategy.systems.save_game_service.SaveGameService') as mock_svc:
            mock_svc.list_saves.return_value = [{
                'save_name': 'TestSave',
                'player_name': 'Player',
                'latest_turn_number': 1,
                'empire_count': 1,
                'timestamp': '2026-01-24T14:30:00',
                'save_path': '/fake/path'
            }]
            mock_svc.list_turns.return_value = []

            with patch('game.ui.screens.save_selection_window.logger') as mock_log:
                window = SaveSelectionWindow(
                    rect=pygame.Rect(100, 100, 600, 500),
                    manager=self.manager,
                    on_load_callback=MagicMock(),
                    on_cancel_callback=MagicMock()
                )

                # With valid timestamp, no warning should be logged for timestamp parsing
                # (other warnings may occur, so we check the call args specifically)
                timestamp_warning_logged = False
                for call in mock_log.warning.call_args_list:
                    if 'timestamp' in str(call).lower():
                        timestamp_warning_logged = True
                        break

                assert not timestamp_warning_logged, "No timestamp warning should be logged for valid timestamps"

                window.kill()
