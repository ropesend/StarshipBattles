"""
Tests for TurnStateSnapshot capture and restore.

PROJ-251 Phase 4: Turn State Snapshot & Rollback
"""
import json
import logging
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

    def test_restore_wires_galaxy_back_refs(self, minimal_game_session):
        """PROJ-432: each restored empire must hold a galaxy back-reference.

        Mirrors `test_rehydrate_wires_galaxy_back_refs` on the canonical
        save-load path. `Empire.set_galaxy(galaxy)` stores into
        `empire._galaxy`; this test asserts identity (not equality) post-
        restore so any future regression of the missing wiring step is
        caught.
        """
        from game.strategy.engine.turn_state_snapshot import TurnStateSnapshot
        session = minimal_game_session

        snapshot = TurnStateSnapshot.capture(
            turn_number=1, empires=session.empires, galaxy=session.galaxy
        )

        # Mutate empire back-refs so a restore that fails to re-wire is
        # observable (without this, the pre-restore back-ref might happen
        # to still match the freshly-rebuilt galaxy).
        for empire in session.empires:
            empire._galaxy = None

        snapshot.restore(session)

        for empire in session.empires:
            assert empire._galaxy is session.galaxy

    def test_restore_rebuilds_pursuer_trackers(self, minimal_game_session):
        """PROJ-432: pursuer tracker is rebuilt from resolved order targets.

        Mirrors `test_rehydrate_rebuilds_pursuer_trackers` on the canonical
        save-load path. Source fleet 9001 carries a `MOVE_TO_FLEET` order
        at target fleet 9002; after a snapshot round-trip the restored
        source must appear in the restored target's `pursuer_tracker.pursuers`.
        """
        from game.strategy.engine.turn_state_snapshot import TurnStateSnapshot
        from game.strategy.data.fleet import Fleet
        from game.strategy.data.order_types import Order, OrderType
        session = minimal_game_session
        empire = session.empires[0]

        target = Fleet(
            fleet_id=9002,
            owner_id=empire.id,
            location=HexCoord(2, 2),
            speed=5.0,
        )
        source = Fleet(
            fleet_id=9001,
            owner_id=empire.id,
            location=HexCoord(1, 1),
            speed=5.0,
        )
        source.add_order(Order(OrderType.MOVE_TO_FLEET, target))
        empire.add_fleet(target)
        empire.add_fleet(source)

        snapshot = TurnStateSnapshot.capture(
            turn_number=1, empires=session.empires, galaxy=session.galaxy
        )

        # Mutate live state to force the restore path to actually rebuild.
        empire.fleets.clear()

        snapshot.restore(session)

        restored_source = session.galaxy.get_fleet_by_id(9001)
        restored_target = session.galaxy.get_fleet_by_id(9002)
        assert restored_source is not None
        assert restored_target is not None
        # Order-reference resolution (already wired today) — sanity check.
        assert restored_source.orders[0].target is restored_target
        # Pursuer-tracker rebuild — the wiring step Phase 1 adds.
        assert restored_source in restored_target.pursuer_tracker.pursuers


class TestTurnStateSnapshotCrashDump:
    """Tests for crash snapshot disk-writing helpers."""

    def test_dump_crash_snapshot_writes_summary_json(self, tmp_path):
        from game.strategy.engine.turn_state_snapshot import TurnStateSnapshot

        snapshot = TurnStateSnapshot(
            turn_number=7,
            empire_dicts=[{"id": 1}, {"id": 2}],
            galaxy_dict={"systems": [{"name": "Alpha"}, {"name": "Beta"}]},
            timestamp=123.5,
        )

        snapshot.dump_crash_snapshot(
            str(tmp_path),
            {
                "tick": 42,
                "phase_name": "PlanetEnergy",
                "error": "boom",
            },
        )

        crash_path = tmp_path / "crash_turn7_tick42_phase_PlanetEnergy.json"
        assert crash_path.exists()
        data = json.loads(crash_path.read_text())
        assert data == {
            "turn_number": 7,
            "timestamp": 123.5,
            "error": {
                "tick": 42,
                "phase_name": "PlanetEnergy",
                "error": "boom",
            },
            "empire_count": 2,
            "system_count": 2,
        }

    def test_dump_crash_snapshot_logs_oserror_without_raising(
        self, tmp_path, caplog
    ):
        """PROJ-381 Phase 3 (ERR-02-005): dump_crash_snapshot routes
        through `save_json`, which returns False on write failure. The
        method must log the error and not raise."""
        from game.strategy.engine.turn_state_snapshot import TurnStateSnapshot

        snapshot = TurnStateSnapshot(turn_number=3)

        with patch(
            "game.strategy.engine.turn_state_snapshot.save_json",
            return_value=False,
        ):
            with caplog.at_level(logging.ERROR):
                snapshot.dump_crash_snapshot(
                    str(tmp_path),
                    {"tick": 9, "phase_name": "Movement"},
                )

        # PROJ-395 MAJ-010: assert on the structural contract — at
        # least one ERROR-level record was emitted — rather than
        # exact message wording. The previous "Failed to write crash
        # snapshot" substring would break under cosmetic copy edits
        # (e.g., "Could not write..." or "Crash snapshot write
        # failed") despite identical behavior. The behavior under
        # test is "log at ERROR and do not raise"; the message text
        # is documentation, not contract.
        error_records = [
            rec for rec in caplog.records if rec.levelno == logging.ERROR
        ]
        assert error_records, (
            f"Expected at least one ERROR record; got: "
            f"{[(r.levelname, r.getMessage()) for r in caplog.records]}"
        )
        # The record should mention the snapshot path so log mining
        # can correlate the error with the failed write — but accept
        # any rendering that includes the path component.
        assert any(
            str(tmp_path) in rec.getMessage() or "crash" in rec.getMessage().lower()
            for rec in error_records
        ), (
            "Expected the ERROR record to reference the crash snapshot "
            "(by path or by the word 'crash'); got: "
            f"{[r.getMessage() for r in error_records]}"
        )


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
