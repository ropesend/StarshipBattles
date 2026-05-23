"""Shared fixtures for SaveGameService tests."""
import pytest
import tempfile
import shutil
import os
from unittest.mock import MagicMock, patch

from game.strategy.engine.game_config import GameConfig, PlayerConfig
from game.core import paths as paths_module


class MockGameSession:
    """Mock GameSession for testing save operations.

    PROJ-479 Task 6.1 (HLP-001): canonical home for the MockGameSession
    stub used across the save-game test suite. Extended with `save_path`
    kwarg per Task 6.1 to subsume `tests/unit/strategy/test_auto_save.py`.
    """

    def __init__(self, config=None, turn_number=1, num_empires=2, save_path=None):
        self.config = config or GameConfig()
        self.turn_number = turn_number
        self.save_path = save_path
        self.systems = [MagicMock()]  # At least one system

        # Create mock empires
        self.empires = []
        for i in range(num_empires):
            empire = MagicMock()
            empire.id = i
            empire.name = f"Empire {i}"
            self.empires.append(empire)

    def to_dict(self):
        return {
            'turn_number': self.turn_number,
            'save_path': self.save_path,
            'config': self.config.to_dict(),
            'galaxy': {'systems': {}, 'warp_lanes': [], 'radius': 4000},
            'empires': [{'id': e.id, 'name': e.name, 'color': (0, 0, 255),
                         'colony_ids': [], 'fleets': [], 'built_ship_designs': []}
                        for e in self.empires],
            'human_player_ids': [0, 1]
        }


@pytest.fixture
def setup_tmpdir():
    """Create temporary directory for tests and patch Paths.SAVES_DIR."""
    tmpdir = tempfile.mkdtemp()
    saves_dir = os.path.join(tmpdir, "saves")
    os.makedirs(saves_dir, exist_ok=True)
    with patch.object(paths_module.Paths, 'SAVES_DIR', saves_dir):
        yield tmpdir
    shutil.rmtree(tmpdir)
