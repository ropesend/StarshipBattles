"""MovementPhaseCollaborator — PROJ-428 Phase 3 (TD-04).

Owns the post-movement-phase pipeline that previously lived in
``turn_phase_registry._derive_moved_fleet_ids``:

1. **Movement diff** — compute the set of fleets whose location changed
   between Phase 2 (``movement_calc``) and Phase 3 (``movement_apply``).
2. **`_booster_dirty` propagation** — flip the per-empire flag for
   every empire that had at least one moved fleet, so the harvesting
   engine's per-turn booster cache is invalidated.
3. **Minefield resolution** — call
   :meth:`MinefieldResolver.resolve_minefield_entry` for each moved
   fleet, threading ``registries=engine._registries`` so strategic mine
   damage routes through the full DamageCalculator pipeline. The call
   is wrapped in a broad catch (matching the pre-refactor contract) so
   resolver errors never abort the turn loop.
4. **Fleet pruning** — fleets emptied by minefield damage are removed
   from their owning empire's fleet list.

The collaborator is constructed by ``TurnEngine`` and dispatched by the
``movement_calc`` and ``movement_apply`` post-exec hooks in
``DEFAULT_TICK_PHASE_LIST``.
"""
from __future__ import annotations

import logging
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from game.strategy.engine.turn_phase_registry import TickContext


logger = logging.getLogger(__name__)


class MovementPhaseCollaborator:
    """Movement-phase snapshot + diff + minefield + pruning collaborator.

    Stateless; the same instance can be reused across ticks. All
    cross-phase state flows through ``TickContext`` (``move_queue``,
    ``pre_movement_locations``, ``moved_fleet_ids``).
    """

    # ------------------------------------------------------------------
    # Public surface — wired into the registry descriptor hooks.
    # ------------------------------------------------------------------

    def snapshot_before(self, ctx: 'TickContext', result: Any) -> None:
        """Capture the move queue + pre-Phase-3 fleet locations.

        Wired as the ``post_exec_hook`` on ``movement_calc``. Stores both
        the move queue (consumed by ``movement_apply``) and the
        location map used by :meth:`resolve_after` to derive
        ``moved_fleet_ids``.
        """
        ctx.move_queue = result
        ctx.pre_movement_locations = {
            f.id: f.location for emp in ctx.empires for f in emp.fleets
        }

    def resolve_after(self, engine: Any, ctx: 'TickContext') -> None:
        """Run the four-step pipeline after movement_apply.

        Wired as the ``post_exec_hook`` on ``movement_apply``. See
        module docstring for the four pipeline steps.
        """
        moved_owner_ids, moved_ids, moved_fleets = self._diff_moved_fleets(ctx)
        ctx.moved_fleet_ids = moved_ids
        self._mark_boosters_dirty(ctx.empires, moved_owner_ids)
        if moved_fleets:
            self._resolve_minefields(engine, ctx, moved_fleets)

    # ------------------------------------------------------------------
    # Private split — narrow single-responsibility helpers.
    # ------------------------------------------------------------------

    def _diff_moved_fleets(
        self, ctx: 'TickContext',
    ) -> tuple[set, set, list]:
        """Pure diff: pre vs. post locations.

        Returns ``(moved_owner_ids, moved_ids, moved_fleets)``.
        ``moved_fleets`` is a list of ``(empire, fleet)`` pairs to feed
        the minefield resolver.
        """
        pre = ctx.pre_movement_locations or {}
        moved_owner_ids: set = set()
        moved_ids: set = set()
        moved_fleets: list = []
        for emp in ctx.empires:
            emp_id = getattr(emp, 'id', None)
            for f in emp.fleets:
                if pre.get(f.id) != f.location:
                    moved_ids.add(f.id)
                    moved_fleets.append((emp, f))
                    if emp_id is not None:
                        moved_owner_ids.add(emp_id)
        return moved_owner_ids, moved_ids, moved_fleets

    def _mark_boosters_dirty(self, empires, moved_owner_ids: set) -> None:
        """Flip ``_booster_dirty`` on every empire with at least one
        moved fleet this tick. PROJ-412 Phase 5 invariant.
        """
        if not moved_owner_ids:
            return
        for emp in empires:
            if getattr(emp, 'id', None) in moved_owner_ids:
                emp._booster_dirty = True

    def _resolve_minefields(
        self, engine: Any, ctx: 'TickContext', moved_fleets: list,
    ) -> None:
        """Call MinefieldResolver for each moved real Fleet, then prune.

        PROJ-FMS-B Phase 1: minefield resolution runs after movement_apply
        and before combat so a fleet destroyed by mines never reaches
        conflict resolution.

        PROJ-FMS-B audit Fix 1: the resolver receives
        ``registries=engine._registries`` so strategic mine damage uses
        the full DamageCalculator pipeline (shields + emissive armor +
        SRA) instead of the direct-HP fallback. Tests that pass
        ``engine`` without ``_registries`` get ``None`` via ``getattr``
        and the resolver falls back gracefully.

        Defensive: only invoke for fleet objects that expose ``ships``
        and have ``group_kind == 'fleet'`` — SimpleNamespace test doubles
        without ``ships`` short-circuit cleanly so existing descriptor
        tests keep passing.
        """
        # Local import: ``MinefieldResolver`` lives under
        # ``game.strategy.engine``; importing it at module top is fine
        # for the collaborator file (not the registry module the AST
        # purity guard protects).
        from game.strategy.engine.minefield_resolver import MinefieldResolver

        runnable_movers = [
            (emp, f) for (emp, f) in moved_fleets
            if hasattr(f, "ships") and getattr(f, "ships", None)
            and getattr(f, "group_kind", "fleet") == "fleet"
        ]
        if not runnable_movers:
            return

        resolver = MinefieldResolver()
        registries = getattr(engine, "_registries", None)
        for owning_empire, fleet in runnable_movers:
            try:
                result = resolver.resolve_minefield_entry(
                    galaxy=ctx.galaxy,
                    empires=ctx.empires,
                    fleet=fleet,
                    registries=registries,
                )
            except Exception:  # Intentional broad catch: minefield resolution must never break the turn loop; log and continue.
                logger.exception(
                    "MinefieldResolver raised during turn tick"
                )
                continue
            if result.destroyed_ship_ids:
                self._prune_destroyed_fleet_contents(
                    owning_empire, fleet, result.destroyed_ship_ids,
                )

    def _prune_destroyed_fleet_contents(
        self, owning_empire, fleet, destroyed_ship_ids,
    ) -> None:
        """Remove destroyed ships from the fleet, and the fleet from
        its empire when emptied.
        """
        fleet.ships = [
            s for s in fleet.ships
            if s.instance_id not in destroyed_ship_ids
        ]
        if not fleet.ships and fleet in owning_empire.fleets:
            owning_empire.fleets.remove(fleet)
