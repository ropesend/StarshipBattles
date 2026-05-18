"""PROJ-438 Phase 1: parity between the two restore paths.

Pins that ``SessionPersistenceAdapter.rehydrate_state()`` and
``TurnStateSnapshot.restore()`` perform the same four graph-restoration
steps against the same input dicts. The individual ratchets per side
already exist (``test_persistence_adapter.py`` and
``test_turn_state_snapshot.py``); this file exercises both paths against
**one** fixture so any future divergence on the post-Phase-1 collaborator
is caught even if one side's individual ratchet was updated and the other
was not.

The 4-step parity tests (``test_parity_*``) MUST pass before Task 1.2
extraction and again after — they are the safety net for the refactor.

The DesignCatalog test (``test_documented_design_catalog_asymmetry``)
pins the **intentional asymmetry** resolved in Task 1.3 under option (b):
only the save-load path rebuilds the per-empire ``DesignCatalog`` map;
the snapshot path preserves the in-memory map by design because a turn
rollback never crosses a process boundary.
"""
from __future__ import annotations

import pytest

from game.core.hex_math import HexCoord
from game.strategy.data.fleet import Fleet
from game.strategy.data.order_types import Order, OrderType
from game.strategy.engine.game_config import GameConfig, PlayerConfig
from game.strategy.engine.game_session import GameSession
from game.strategy.engine.session.persistence_adapter import (
    SessionPersistenceAdapter,
)
from game.strategy.engine.turn_state_snapshot import TurnStateSnapshot


def _small_config() -> GameConfig:
    return GameConfig(
        players=[
            PlayerConfig(name="A", theme="Federation", color=(255, 0, 0)),
            PlayerConfig(name="B", theme="Atlantians", color=(0, 255, 0)),
        ],
        system_count=2,
    )


def _session_with_join_fleet_order() -> GameSession:
    """Build a session with one source-and-target fleet pair so the
    pursuer-tracker rebuild step has something to do."""
    return _session_with_pursuit_order(OrderType.JOIN_FLEET)


def _session_with_pursuit_order(order_type: OrderType) -> GameSession:
    """Build a session with a source fleet carrying a pursuit-style order
    (``JOIN_FLEET`` or ``MOVE_TO_FLEET``) at a target fleet, so the
    pursuer-tracker rebuild step in ``restore_graph_wiring`` has something
    to do."""
    session = GameSession(config=_small_config())
    empire = session.empires[0]
    target = Fleet(
        fleet_id=7002,
        owner_id=empire.id,
        location=HexCoord(2, 2),
        speed=5.0,
    )
    source = Fleet(
        fleet_id=7001,
        owner_id=empire.id,
        location=HexCoord(1, 1),
        speed=5.0,
    )
    source.add_order(Order(order_type, target))
    empire.add_fleet(target)
    empire.add_fleet(source)
    return session


def _rehydrate_path(session: GameSession):
    """Run the save-load restore path against the session's serialize()
    output. Returns ``(galaxy, empires)`` from the resulting
    ``SessionBootstrapState`` so the two paths can be compared structurally
    without a session-vs-state shape mismatch."""
    data = SessionPersistenceAdapter.serialize(session)
    state = SessionPersistenceAdapter.rehydrate_state(data)
    return state.galaxy, state.empires


def _snapshot_path(session: GameSession):
    """Run the rollback restore path. Captures a snapshot from the source
    session, then restores into a *fresh* session shell (built from the
    same config) so the source session is not mutated. Returns
    ``(galaxy, empires)`` from the restored shell."""
    snapshot = TurnStateSnapshot.capture(
        turn_number=session.turn_number,
        empires=session.empires,
        galaxy=session.galaxy,
    )
    shell = GameSession(config=_small_config())
    snapshot.restore(shell)
    return shell.galaxy, shell.empires


class TestRestorePathParity:
    """Side-by-side parity for the four shared graph-restoration steps.

    These tests pin behavior that is already aligned post-PROJ-432. They
    are the safety net for PROJ-438 Phase 1 Task 1.2's collaborator
    extraction: any refactor that regresses one side will break the
    matching parity test here.
    """

    def test_parity_galaxy_back_refs(self) -> None:
        """Step 1: every restored empire holds a back-ref to its galaxy."""
        session = _session_with_join_fleet_order()
        rehydrate_galaxy, rehydrate_empires = _rehydrate_path(session)
        snapshot_galaxy, snapshot_empires = _snapshot_path(session)

        for empire in rehydrate_empires:
            assert empire._galaxy is rehydrate_galaxy, (
                "Rehydrate path failed to wire galaxy back-ref"
            )
        for empire in snapshot_empires:
            assert empire._galaxy is snapshot_galaxy, (
                "Snapshot path failed to wire galaxy back-ref"
            )

    def test_parity_fleet_registration(self) -> None:
        """Step 2: deserialized fleets are reachable via galaxy.get_fleet_by_id."""
        session = _session_with_join_fleet_order()
        rehydrate_galaxy, _ = _rehydrate_path(session)
        snapshot_galaxy, _ = _snapshot_path(session)

        for fleet_id in (7001, 7002):
            assert rehydrate_galaxy.get_fleet_by_id(fleet_id) is not None, (
                f"Rehydrate path failed to register fleet {fleet_id}"
            )
            assert snapshot_galaxy.get_fleet_by_id(fleet_id) is not None, (
                f"Snapshot path failed to register fleet {fleet_id}"
            )

    def test_parity_order_reference_resolution(self) -> None:
        """Step 3: marker dicts in fleet orders become live Fleet refs."""
        session = _session_with_join_fleet_order()
        rehydrate_galaxy, _ = _rehydrate_path(session)
        snapshot_galaxy, _ = _snapshot_path(session)

        for galaxy, label in (
            (rehydrate_galaxy, "rehydrate"),
            (snapshot_galaxy, "snapshot"),
        ):
            src = galaxy.get_fleet_by_id(7001)
            tgt = galaxy.get_fleet_by_id(7002)
            assert src is not None and tgt is not None
            assert src.orders[0].target is tgt, (
                f"{label} path failed to resolve order target marker dict"
            )

    @pytest.mark.parametrize(
        "order_type",
        [OrderType.JOIN_FLEET, OrderType.MOVE_TO_FLEET],
        ids=["join_fleet", "move_to_fleet"],
    )
    def test_parity_pursuer_tracker_rebuild(self, order_type: OrderType) -> None:
        """Step 4: JOIN_FLEET *and* MOVE_TO_FLEET orders both re-add the
        source fleet to the target's pursuer tracker. Phase 9 / Codex
        consult 2026-05-18 finding 6a — the original test only covered
        JOIN_FLEET; this parametrization adds the sibling MOVE_TO_FLEET
        branch that the collaborator handles identically at
        `graph_restoration.py:70-79`."""
        session = _session_with_pursuit_order(order_type)
        rehydrate_galaxy, _ = _rehydrate_path(session)
        snapshot_galaxy, _ = _snapshot_path(session)

        for galaxy, label in (
            (rehydrate_galaxy, "rehydrate"),
            (snapshot_galaxy, "snapshot"),
        ):
            src = galaxy.get_fleet_by_id(7001)
            tgt = galaxy.get_fleet_by_id(7002)
            assert src is not None and tgt is not None
            assert src in tgt.pursuer_tracker.pursuers, (
                f"{label} path failed to rebuild pursuer tracker for "
                f"{order_type.name}"
            )


class TestDocumentedDesignCatalogAsymmetry:
    """Pin the DesignCatalog asymmetry as **intentional documented behavior**.

    Per PROJ-438 Phase 1 Task 1.3 decision (option **b** — document, do
    not canonicalize):

    - The save-load path (``rehydrate_state``) MUST replace the
      per-empire ``DesignCatalog`` map with freshly-built instances
      scanned from each empire's on-disk ``DesignRepository``. The
      replacement is load-bearing because the catalog state on disk is
      the source of truth across a process boundary.
    - The rollback path (``TurnStateSnapshot.restore``) MUST leave the
      in-memory ``DesignCatalog`` map untouched. A turn rollback never
      crosses a process boundary; the in-memory map built at session
      start (or refreshed at the last load) is still valid through the
      rollback and an unnecessary rebuild would only waste disk I/O.

    This is the same-meaning inverse of Phase 0's "anti-drift insurance"
    framing: the **shared** wiring steps are pinned identical by the
    ``TestRestorePathParity`` class above; this asymmetric step is pinned
    *non-identical* and load-bearing here, so a future refactor that
    accidentally collapses it into the shared collaborator will break
    this test.
    """

    def test_documented_design_catalog_asymmetry(self) -> None:
        """Rehydrate REPLACES the catalog map; snapshot PRESERVES it."""
        session = _session_with_join_fleet_order()

        # --- Save-load path: identity changes across rehydrate. ---
        src_ids_before = {
            k: id(v)
            for k, v in session.services.design_catalogs_by_empire.items()
        }
        data = SessionPersistenceAdapter.serialize(session)
        state = SessionPersistenceAdapter.rehydrate_state(data)
        rehydrate_ids = {
            k: id(v)
            for k, v in state.services.design_catalogs_by_empire.items()
        }
        rehydrate_replaced = all(
            rehydrate_ids[k] != src_ids_before.get(k)
            for k in rehydrate_ids
        )

        # --- Snapshot path: identity stable across snapshot restore. ---
        shell = GameSession(config=_small_config())
        shell_ids_before = {
            k: id(v)
            for k, v in shell.services.design_catalogs_by_empire.items()
        }
        snapshot = TurnStateSnapshot.capture(
            turn_number=session.turn_number,
            empires=session.empires,
            galaxy=session.galaxy,
        )
        snapshot.restore(shell)
        shell_ids_after = {
            k: id(v)
            for k, v in shell.services.design_catalogs_by_empire.items()
        }
        snapshot_preserved = all(
            shell_ids_after[k] == shell_ids_before.get(k)
            for k in shell_ids_after
        )

        assert rehydrate_replaced is True, (
            "rehydrate_state must rebuild design_catalogs_by_empire from "
            "disk per persistence_adapter.py docs."
        )
        assert snapshot_preserved is True, (
            "TurnStateSnapshot.restore must NOT touch design_catalogs_by_"
            "empire — rollback preserves the in-memory map by design."
        )
