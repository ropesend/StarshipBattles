"""PROJ-423 Phase 3: tests for SessionPersistenceAdapter.

Pins the save schema byte-for-byte and proves the load-only steps (galaxy
back-references, fleet registration, order reference resolution, pursuer
tracker rebuild) execute on rehydrate. Returns `SessionBootstrapState`
rather than `GameSession`.
"""
from __future__ import annotations

from game.core.hex_math import HexCoord
from game.strategy.data.fleet import Fleet
from game.strategy.data.galaxy import Galaxy
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


def _frozen_fixture_session() -> GameSession:
    """A fully deterministic minimal session for schema-shape pinning.

    Builds a normal `GameSession`, then swaps in a hand-rolled empty
    `Galaxy` and clears empires so the resulting `serialize()` output is
    byte-for-byte deterministic and free of stochastic galaxy generation
    (planet names, star image_ids, image_rotation, etc.). `asset_base_path`
    is forced to `""` to avoid leaking machine-specific paths into the
    frozen literal.
    """
    config = GameConfig(
        players=[
            PlayerConfig(name="A", theme="Federation", color=(255, 0, 0)),
            PlayerConfig(name="B", theme="Atlantians", color=(0, 255, 0)),
        ],
        system_count=2,
        galaxy_seed=42,
        galaxy_radius=100,
        asset_base_path="",
    )
    session = GameSession(config=config)
    # Replace the stochastic galaxy + empires with deterministic empties so
    # the serialize() output equals a hardcoded reference literal.
    session.galaxy = Galaxy(radius=100)
    session.empires = []
    session.human_player_ids = [0, 1]
    return session


_EXPECTED_SAVE_KEYS = {
    "turn_number",
    "save_path",
    "config",
    "galaxy",
    "empires",
    "human_player_ids",
    "event_log",
}

# PROJ-496 Phase 3 (Task 3.1): nested key contracts for the schema guard.
# `_EXPECTED_CONFIG_KEYS` mirrors `GameConfig.to_dict()` at
# `game/strategy/engine/game_config.py`; `_EXPECTED_PLAYER_KEYS` mirrors the
# always-emitted (non-sparse) subset of `PlayerConfig.to_dict()` — the fixture
# doesn't set race_id / flag_id / portrait_id / race_config, so those sparse
# keys are deliberately absent from the expected set.
_EXPECTED_CONFIG_KEYS = {
    "asset_base_path",
    "galaxy_radius",
    "system_count",
    "galaxy_type",
    "galaxy_seed",
    "save_name",
    "players",
}
_EXPECTED_PLAYER_KEYS = {"name", "theme", "color", "is_human"}


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

    def test_serialize_matches_frozen_schema_fixture(self) -> None:
        """Pin the on-disk save schema by validating the structural shape
        plus the intended values per spot-checked slot.

        The post-PROJ-423 `to_dict()` simply forwards to `serialize()`, so
        the earlier `test_serialize_matches_to_dict_output` is a
        self-delegate check. The real schema guard is **this** test.

        Three layers of drift are caught:
          1. Top-level: `set(actual.keys()) == _EXPECTED_SAVE_KEYS`.
          2. Nested key sets: `set(config.keys()) == _EXPECTED_CONFIG_KEYS`
             and `set(players[i].keys()) == _EXPECTED_PLAYER_KEYS` per slot.
             A rename, removal, or new always-emitted key in either nested
             dict fails this test.
          3. Spot-checked leaf values: the specific scalars listed below
             must match the fixture inputs (galaxy_seed=42, save_name="",
             player[0].name="A", ...). Drift in *unnamed* leaf values
             (e.g., a new optional field defaulting to None that is
             emitted sparsely) still passes by design.

        PROJ-480 T4.1 relaxed the earlier 35-line literal-dict equality to
        avoid churn from unrelated downstream defaults; PROJ-496 Phase 3
        Task 3.1 reinstates the structural shape check the docstring
        previously advertised but the assertions didn't enforce.
        """
        session = _frozen_fixture_session()
        actual = SessionPersistenceAdapter.serialize(session)

        # Top-level schema: exact key set + slot types + scalar values.
        assert set(actual.keys()) == _EXPECTED_SAVE_KEYS
        assert actual["turn_number"] == 1
        assert actual["save_path"] is None
        assert actual["empires"] == []
        assert actual["human_player_ids"] == [0, 1]
        assert actual["event_log"] == {"events": []}

        # Config: nested key set + spot-checked leaf values.
        config = actual["config"]
        assert isinstance(config, dict)
        assert set(config.keys()) == _EXPECTED_CONFIG_KEYS
        assert config["asset_base_path"] == ""
        assert config["galaxy_radius"] == 100
        assert config["system_count"] == 2
        assert config["galaxy_type"] == "random"
        assert config["galaxy_seed"] == 42
        # `_frozen_fixture_session` does not set save_name, so it must
        # serialize as the GameConfig default (empty string).
        assert config["save_name"] == ""
        # Players: exact length + per-player key contract + spot-checked
        # leaf values. The fixture leaves the sparse PlayerConfig fields
        # (race_id, flag_id, portrait_id, race_config) unset, so each
        # player dict must contain exactly the always-emitted subset.
        players = config["players"]
        assert len(players) == 2
        assert set(players[0].keys()) == _EXPECTED_PLAYER_KEYS
        assert set(players[1].keys()) == _EXPECTED_PLAYER_KEYS
        assert players[0]["name"] == "A"
        assert players[0]["theme"] == "Federation"
        assert players[0]["color"] == [255, 0, 0]
        assert players[0]["is_human"] is True
        assert players[1]["name"] == "B"
        assert players[1]["theme"] == "Atlantians"
        assert players[1]["color"] == [0, 255, 0]
        assert players[1]["is_human"] is True

        # Galaxy: the empty-galaxy contract.
        galaxy = actual["galaxy"]
        assert isinstance(galaxy, dict)
        assert galaxy["radius"] == 100
        assert galaxy["systems"] == []
        assert galaxy["_next_planet_id"] == 1
        assert galaxy["_next_fleet_id"] == 1


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
