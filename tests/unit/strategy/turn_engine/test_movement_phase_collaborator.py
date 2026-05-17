"""
PROJ-428 Phase 3 — Tests for ``MovementPhaseCollaborator``.

The collaborator owns the four-step movement post-phase pipeline:

1. ``snapshot_before(ctx, result)`` — replaces the old
   ``_capture_move_queue`` module-level hook. Stores ``move_queue`` and
   ``pre_movement_locations`` on the context.
2. ``resolve_after(engine, ctx)`` — replaces the old
   ``_derive_moved_fleet_ids`` module-level hook. Diffs locations,
   flips ``_booster_dirty`` on moved-empire fleets, calls
   ``MinefieldResolver.resolve_minefield_entry(..., registries=engine._registries)``
   inside the existing broad catch, and prunes destroyed fleets from
   their owning empire.

These tests pin those behaviors at the collaborator boundary so any
later refactor of the post-phase pipeline cannot regress them silently.
"""
from __future__ import annotations

from types import SimpleNamespace

from game.strategy.engine.movement_phase_collaborator import (
    MovementPhaseCollaborator,
)
from game.strategy.engine.turn_phase_registry import TickContext


class TestSnapshotBefore:
    """Pin the ``snapshot_before`` capture semantics."""

    def test_snapshot_before_stores_move_queue_and_locations(self):
        fleet_a = SimpleNamespace(id=1, location='A')
        fleet_b = SimpleNamespace(id=2, location='B')
        ctx = TickContext(
            tick=20,
            empires=[SimpleNamespace(fleets=[fleet_a, fleet_b])],
            galaxy=object(),
        )
        move_queue = [(fleet_a, 'C')]

        collab = MovementPhaseCollaborator()
        collab.snapshot_before(ctx, move_queue)

        assert ctx.move_queue is move_queue
        assert ctx.pre_movement_locations == {1: 'A', 2: 'B'}


class TestResolveAfter:
    """Pin the ``resolve_after`` four-step pipeline."""

    def test_resolve_after_derives_moved_fleet_ids(self):
        fleet_a = SimpleNamespace(id=1, location='A')
        fleet_b = SimpleNamespace(id=2, location='B')
        ctx = TickContext(
            tick=20,
            empires=[SimpleNamespace(
                id=0, fleets=[fleet_a, fleet_b], _booster_dirty=False,
            )],
            galaxy=object(),
            pre_movement_locations={1: 'old-A', 2: 'B'},
        )

        collab = MovementPhaseCollaborator()
        engine = SimpleNamespace(_registries=None)
        collab.resolve_after(engine, ctx)

        assert ctx.moved_fleet_ids == {1}

    def test_resolve_after_flips_booster_dirty_only_for_moved_empires(self):
        fleet_a = SimpleNamespace(id=1, location='Y')  # moved
        fleet_b = SimpleNamespace(id=2, location='Z')  # stayed
        empire_a = SimpleNamespace(id=10, fleets=[fleet_a], _booster_dirty=False)
        empire_b = SimpleNamespace(id=20, fleets=[fleet_b], _booster_dirty=False)
        ctx = TickContext(
            tick=4,
            empires=[empire_a, empire_b],
            galaxy=object(),
            pre_movement_locations={1: 'X', 2: 'Z'},
        )

        collab = MovementPhaseCollaborator()
        engine = SimpleNamespace(_registries=None)
        collab.resolve_after(engine, ctx)

        assert empire_a._booster_dirty is True
        assert empire_b._booster_dirty is False

    def test_resolve_after_threads_registries_into_minefield_resolver(self):
        """The resolver must be invoked with
        ``registries=engine._registries`` (call-contract byte-for-byte
        match with the pre-refactor _derive_moved_fleet_ids).
        """
        captured: dict = {}

        moved_fleet = SimpleNamespace(
            id=1,
            location='B',
            ships=[SimpleNamespace(instance_id="s1", is_alive=True)],
            group_kind='fleet',
        )
        empire = SimpleNamespace(id=1, fleets=[moved_fleet], _booster_dirty=False)
        ctx = TickContext(
            tick=5,
            empires=[empire],
            galaxy=object(),
            pre_movement_locations={1: 'A'},
        )

        sentinel_registries = object()
        engine = SimpleNamespace(_registries=sentinel_registries)

        from game.strategy.engine import minefield_resolver as _mr_mod

        class _CaptureResolver:
            def __init__(self, *args, **kwargs) -> None:
                pass

            def resolve_minefield_entry(self, **kwargs):
                captured.update(kwargs)
                return _mr_mod.MinefieldResolutionResult()

        original = _mr_mod.MinefieldResolver
        _mr_mod.MinefieldResolver = _CaptureResolver
        try:
            collab = MovementPhaseCollaborator()
            collab.resolve_after(engine, ctx)
        finally:
            _mr_mod.MinefieldResolver = original

        assert captured.get("registries") is sentinel_registries
        assert captured.get("fleet") is moved_fleet
        assert captured.get("galaxy") is ctx.galaxy

    def test_resolve_after_prunes_emptied_fleets_from_empire(self):
        ship = SimpleNamespace(instance_id='s1', is_alive=True)
        moved_fleet = SimpleNamespace(
            id=42,
            location='B',
            ships=[ship],
            group_kind='fleet',
        )
        empire = SimpleNamespace(
            id=7, fleets=[moved_fleet], _booster_dirty=False,
        )
        ctx = TickContext(
            tick=5,
            empires=[empire],
            galaxy=object(),
            pre_movement_locations={42: 'A'},
        )
        engine = SimpleNamespace(_registries=object())

        from game.strategy.engine import minefield_resolver as _mr_mod

        class _DestroyAllResolver:
            def __init__(self, *args, **kwargs) -> None:
                pass

            def resolve_minefield_entry(self, **kwargs):
                fleet = kwargs['fleet']
                result = _mr_mod.MinefieldResolutionResult()
                result.destroyed_ship_ids = [s.instance_id for s in fleet.ships]
                return result

        original = _mr_mod.MinefieldResolver
        _mr_mod.MinefieldResolver = _DestroyAllResolver
        try:
            collab = MovementPhaseCollaborator()
            collab.resolve_after(engine, ctx)
        finally:
            _mr_mod.MinefieldResolver = original

        assert moved_fleet.ships == []
        assert moved_fleet not in empire.fleets

    def test_resolve_after_swallows_minefield_resolver_exceptions(self):
        """The broad catch around minefield resolution must remain intact.

        A resolver that raises must not break the turn loop; the
        collaborator continues with the next moved fleet.
        """
        moved_fleet = SimpleNamespace(
            id=1,
            location='B',
            ships=[SimpleNamespace(instance_id="s1", is_alive=True)],
            group_kind='fleet',
        )
        empire = SimpleNamespace(id=1, fleets=[moved_fleet], _booster_dirty=False)
        ctx = TickContext(
            tick=5,
            empires=[empire],
            galaxy=object(),
            pre_movement_locations={1: 'A'},
        )
        engine = SimpleNamespace(_registries=object())

        from game.strategy.engine import minefield_resolver as _mr_mod

        class _ExplodingResolver:
            def __init__(self, *args, **kwargs) -> None:
                pass

            def resolve_minefield_entry(self, **kwargs):
                raise RuntimeError("synthetic minefield resolver failure")

        original = _mr_mod.MinefieldResolver
        _mr_mod.MinefieldResolver = _ExplodingResolver
        try:
            collab = MovementPhaseCollaborator()
            # Must not raise.
            collab.resolve_after(engine, ctx)
        finally:
            _mr_mod.MinefieldResolver = original

        # Moved fleet id still derived prior to the resolver failure.
        assert ctx.moved_fleet_ids == {1}
