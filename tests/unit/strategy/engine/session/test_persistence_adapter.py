"""PROJ-423 Phase 3: tests for SessionPersistenceAdapter.

Pins the save schema byte-for-byte and proves the load-only steps (galaxy
back-references, fleet registration, order reference resolution, pursuer
tracker rebuild) execute on rehydrate. Returns `SessionBootstrapState`
rather than `GameSession`.
"""
from __future__ import annotations

from game.core.hex_math import HexCoord
from game.strategy.data.fleet import Fleet
from game.strategy.data.order_types import Order, OrderType
from game.strategy.engine.game_config import GameConfig, PlayerConfig
from game.strategy.engine.game_session import GameSession
from game.strategy.engine.session.persistence_adapter import (
    SessionPersistenceAdapter,
)
from game.strategy.engine.session.runtime_services import (
    SessionBootstrapState,
)


def _small_config() -> GameConfig:
    return GameConfig(
        players=[
            PlayerConfig(name="A", theme="Federation", color=(255, 0, 0)),
            PlayerConfig(name="B", theme="Atlantians", color=(0, 255, 0)),
        ],
        system_count=2,
    )


_EXPECTED_SAVE_KEYS = {
    "turn_number",
    "save_path",
    "config",
    "galaxy",
    "empires",
    "human_player_ids",
    "event_log",
}


class TestSerialize:
    def test_serialize_preserves_existing_save_schema(self) -> None:
        session = GameSession(config=_small_config())
        data = SessionPersistenceAdapter.serialize(session)

        # Exact key set — no additions, no renames, no reorderings.
        assert set(data.keys()) == _EXPECTED_SAVE_KEYS
        assert isinstance(data["turn_number"], int)
        assert data["save_path"] is None
        assert isinstance(data["config"], dict)
        assert isinstance(data["galaxy"], dict)
        assert isinstance(data["empires"], list)
        assert isinstance(data["human_player_ids"], list)
        assert isinstance(data["event_log"], dict)

    def test_serialize_matches_to_dict_output(self) -> None:
        """The thin `to_dict()` delegate must be a one-to-one wrapper."""
        session = GameSession(config=_small_config())
        adapter_data = SessionPersistenceAdapter.serialize(session)
        legacy_data = session.to_dict()
        assert adapter_data == legacy_data


class TestRehydrate:
    def test_rehydrate_returns_bootstrap_state(self) -> None:
        session = GameSession(config=_small_config())
        data = session.to_dict()

        state = SessionPersistenceAdapter.rehydrate_state(data)
        assert isinstance(state, SessionBootstrapState)
        # NOT a GameSession.
        assert not isinstance(state, GameSession)

    def test_rehydrate_wires_galaxy_back_refs(self) -> None:
        """game_session.py lines 566-567: each empire holds a back-ref to
        the loaded galaxy."""
        session = GameSession(config=_small_config())
        data = session.to_dict()
        state = SessionPersistenceAdapter.rehydrate_state(data)

        for empire in state.empires:
            # `Empire.set_galaxy(galaxy)` stores into `_galaxy`.
            assert empire._galaxy is state.galaxy

    def test_rehydrate_registers_loaded_fleets(self) -> None:
        """PROJ-219: deserialized fleets must be registered with galaxy."""
        session = GameSession(config=_small_config())
        empire = session.empires[0]
        fleet = Fleet(
            fleet_id=8001,
            owner_id=empire.id,
            location=HexCoord(0, 0),
            speed=5.0,
        )
        empire.add_fleet(fleet)
        data = session.to_dict()

        state = SessionPersistenceAdapter.rehydrate_state(data)
        # The fleet must be retrievable by id from the galaxy registry.
        assert state.galaxy.get_fleet_by_id(8001) is not None

    def test_rehydrate_resolves_order_references(self) -> None:
        """PROJ-207: marker dicts in fleet orders are resolved to live
        Fleet / Planet objects post-rehydrate."""
        session = GameSession(config=_small_config())
        empire = session.empires[0]
        source = Fleet(
            fleet_id=8101,
            owner_id=empire.id,
            location=HexCoord(1, 1),
            speed=5.0,
        )
        target = Fleet(
            fleet_id=8102,
            owner_id=empire.id,
            location=HexCoord(2, 2),
            speed=5.0,
        )
        source.add_order(Order(OrderType.MOVE_TO_FLEET, target))
        empire.add_fleet(target)
        empire.add_fleet(source)
        data = session.to_dict()

        state = SessionPersistenceAdapter.rehydrate_state(data)
        restored_source = state.galaxy.get_fleet_by_id(8101)
        restored_target = state.galaxy.get_fleet_by_id(8102)
        assert restored_source is not None
        assert restored_target is not None
        # The marker dict should now be a live Fleet reference.
        assert restored_source.orders[0].target is restored_target

    def test_rehydrate_rebuilds_pursuer_trackers(self) -> None:
        """PROJ-222: pursuer tracker is rebuilt from the resolved order
        target."""
        session = GameSession(config=_small_config())
        empire = session.empires[0]
        source = Fleet(
            fleet_id=8201,
            owner_id=empire.id,
            location=HexCoord(1, 1),
            speed=5.0,
        )
        target = Fleet(
            fleet_id=8202,
            owner_id=empire.id,
            location=HexCoord(2, 2),
            speed=5.0,
        )
        source.add_order(Order(OrderType.JOIN_FLEET, target))
        empire.add_fleet(target)
        empire.add_fleet(source)
        data = session.to_dict()

        state = SessionPersistenceAdapter.rehydrate_state(data)
        restored_source = state.galaxy.get_fleet_by_id(8201)
        restored_target = state.galaxy.get_fleet_by_id(8202)
        assert restored_source in restored_target.pursuer_tracker.pursuers

    def test_rehydrate_preserves_human_player_ids_fallback(self) -> None:
        """The current `[0, 1]` fallback in the load path is preserved
        exactly — preserved behavior, not a cleanup target for this
        refactor."""
        session = GameSession(config=_small_config())
        data = session.to_dict()
        # Delete the key to trigger the fallback.
        del data["human_player_ids"]

        state = SessionPersistenceAdapter.rehydrate_state(data)
        assert state.human_player_ids == [0, 1]

    def test_rehydrate_uses_saved_human_player_ids_when_present(self) -> None:
        session = GameSession(config=_small_config())
        data = session.to_dict()
        data["human_player_ids"] = [0]

        state = SessionPersistenceAdapter.rehydrate_state(data)
        assert state.human_player_ids == [0]
