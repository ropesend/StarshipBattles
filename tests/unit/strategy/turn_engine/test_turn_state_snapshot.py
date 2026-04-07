"""
Tests for TurnStateSnapshot capture and restore.

PROJ-251 Phase 4: Turn State Snapshot & Rollback
"""
import time
import pytest
from unittest.mock import MagicMock, patch

from game.core.exceptions import PersistenceException
from game.core.hex_math import HexCoord


class TestTurnStateSnapshotCapture:
    """Tests for capturing pre-turn state."""

    def test_capture_stores_turn_number(self, minimal_game_session):
        from game.strategy.engine.turn_state_snapshot import TurnStateSnapshot
        session = minimal_game_session
        snapshot = TurnStateSnapshot.capture(
            turn_number=5, empires=session.empires, galaxy=session.galaxy
        )
        assert snapshot.turn_number == 5

    def test_capture_stores_empire_dicts(self, minimal_game_session):
        from game.strategy.engine.turn_state_snapshot import TurnStateSnapshot
        session = minimal_game_session
        snapshot = TurnStateSnapshot.capture(
            turn_number=1, empires=session.empires, galaxy=session.galaxy
        )
        assert len(snapshot.empire_dicts) == len(session.empires)
        assert isinstance(snapshot.empire_dicts[0], dict)

    def test_capture_stores_galaxy_dict(self, minimal_game_session):
        from game.strategy.engine.turn_state_snapshot import TurnStateSnapshot
        session = minimal_game_session
        snapshot = TurnStateSnapshot.capture(
            turn_number=1, empires=session.empires, galaxy=session.galaxy
        )
        assert isinstance(snapshot.galaxy_dict, dict)

    def test_capture_stores_timestamp(self, minimal_game_session):
        from game.strategy.engine.turn_state_snapshot import TurnStateSnapshot
        session = minimal_game_session
        before = time.time()
        snapshot = TurnStateSnapshot.capture(
            turn_number=1, empires=session.empires, galaxy=session.galaxy
        )
        after = time.time()
        assert before <= snapshot.timestamp <= after

    def test_capture_isolates_from_mutations(self, minimal_game_session):
        """Modifying live objects after capture does NOT change snapshot data."""
        from game.strategy.engine.turn_state_snapshot import TurnStateSnapshot
        session = minimal_game_session

        snapshot = TurnStateSnapshot.capture(
            turn_number=1, empires=session.empires, galaxy=session.galaxy
        )

        # Mutate live state
        original_name = session.empires[0].name
        session.empires[0].name = "MUTATED"

        # Snapshot should still have original
        assert snapshot.empire_dicts[0]['name'] == original_name

    def test_capture_raises_on_serialization_failure(self):
        """If to_dict() raises, capture raises PersistenceException."""
        from game.strategy.engine.turn_state_snapshot import TurnStateSnapshot

        bad_empire = MagicMock()
        bad_empire.to_dict.side_effect = TypeError("not serializable")

        galaxy = MagicMock()
        galaxy.to_dict.return_value = {}

        with pytest.raises(PersistenceException):
            TurnStateSnapshot.capture(
                turn_number=1, empires=[bad_empire], galaxy=galaxy
            )


class TestTurnStateSnapshotRestore:
    """Tests for restoring pre-turn state from snapshot."""

    def test_restore_resets_empires(self, minimal_game_session):
        """Capture → mutate → restore → empires match original."""
        from game.strategy.engine.turn_state_snapshot import TurnStateSnapshot
        session = minimal_game_session

        original_name = session.empires[0].name
        snapshot = TurnStateSnapshot.capture(
            turn_number=1, empires=session.empires, galaxy=session.galaxy
        )

        # Mutate
        session.empires[0].name = "DESTROYED"

        # Restore
        snapshot.restore(session)

        assert session.empires[0].name == original_name

    def test_restore_resets_galaxy(self, minimal_game_session):
        """Capture → mutate galaxy → restore → galaxy matches original."""
        from game.strategy.engine.turn_state_snapshot import TurnStateSnapshot
        session = minimal_game_session

        original_system_count = len(session.galaxy.systems)
        snapshot = TurnStateSnapshot.capture(
            turn_number=1, empires=session.empires, galaxy=session.galaxy
        )

        # Mutate galaxy (clear systems)
        session.galaxy.systems.clear()
        assert len(session.galaxy.systems) == 0

        # Restore
        snapshot.restore(session)

        assert len(session.galaxy.systems) == original_system_count

    def test_restore_preserves_empire_count(self, minimal_game_session):
        """Restore preserves the number of empires."""
        from game.strategy.engine.turn_state_snapshot import TurnStateSnapshot
        session = minimal_game_session

        snapshot = TurnStateSnapshot.capture(
            turn_number=1, empires=session.empires, galaxy=session.galaxy
        )

        # Remove an empire
        session.empires.pop()

        # Restore
        snapshot.restore(session)

        assert len(session.empires) == len(snapshot.empire_dicts)


# Fixtures
@pytest.fixture
def minimal_game_session():
    """Create a minimal game session for snapshot testing."""
    from game.strategy.engine.game_session import GameSession
    from game.strategy.engine.game_config import GameConfig, PlayerConfig

    config = GameConfig()
    config.galaxy_radius = 300
    config.system_count = 2
    config.players = [
        PlayerConfig(name="TestPlayer", is_human=True, color=(0, 100, 200)),
        PlayerConfig(name="TestEnemy", is_human=False, color=(200, 100, 0)),
    ]
    return GameSession(config=config)
