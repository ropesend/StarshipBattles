"""EmpireWriteService — owns Empire writes from outside the data class.

PROJ-370 Phase 4: implements ``IEmpireMutator``. Single owner service for
the 6 Empire mutation surfaces (colonies, fleets, _fleet_resource_pool,
max_storage, built_ship_designs/designed_ships) plus the post-battle
empty-fleet pruning that previously lived inline at
``combat/post_battle_hook.py:200-218``.

Wiring:
    Constructed in ``GameSession.__init__``. Threaded through
    ``TurnEngineConfig.create_default()``.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from game.strategy.data.empire import Empire
    from game.strategy.data.fleet import Fleet
    from game.strategy.data.planet import Planet


__all__ = ["EmpireWriteService"]


class EmpireWriteService:
    """Concrete ``IEmpireMutator`` implementation."""

    # ------------------------------------------------------------------
    # Colonies
    # ------------------------------------------------------------------
    def add_colony(self, empire: "Empire", planet: "Planet") -> None:
        # Delegate so existing semantics (sets planet.owner_id = empire.id)
        # are preserved.
        empire.add_colony(planet)

    def remove_colony(self, empire: "Empire", planet: "Planet") -> bool:
        # Direct list operation rather than delegating to
        # ``Empire.remove_colony`` (asymmetric with ``add_colony``, intentional).
        # PROJ-370 review MIN-004: a hasattr-based delegation pattern was
        # tried and reverted because ``MagicMock`` makes ``hasattr`` return
        # True for any attribute name, which silently routes test mocks
        # through Mock methods that don't actually mutate ``empire.colonies``.
        # When ``Empire.remove_colony`` grows side effects (e.g. owner_id
        # reset, event emission), revisit by replacing test fakes with
        # ``spec=Empire``-bound mocks instead of bare ``MagicMock``.
        if planet in empire.colonies:
            empire.colonies.remove(planet)
            return True
        return False

    def clear_colonies(self, empire: "Empire") -> None:
        empire.colonies.clear()

    # ------------------------------------------------------------------
    # Fleets
    # ------------------------------------------------------------------
    def add_fleet(self, empire: "Empire", fleet: "Fleet") -> None:
        empire.add_fleet(fleet)

    def remove_fleet(
        self, empire: "Empire", fleet: "Fleet", *, event_bus: Any = None
    ) -> bool:
        # Empire.remove_fleet returns None today; preserve that behavior
        # but report whether the fleet was actually removed for callers
        # that want it.
        was_present = fleet in empire.fleets
        empire.remove_fleet(fleet, event_bus=event_bus)
        return was_present

    # ------------------------------------------------------------------
    # Storage / resources / built designs
    # ------------------------------------------------------------------
    def set_max_storage_amount(
        self, empire: "Empire", resource_id: str, amount: float
    ) -> None:
        empire.max_storage[resource_id] = amount

    def replace_max_storage(
        self, empire: "Empire", new_max_storage: dict
    ) -> None:
        """Replace empire.max_storage wholesale (clear + populate).

        Used by HarvestingEngine to recompute the empire-level aggregate
        each turn from per-colony caps. Tolerates a missing/None
        ``max_storage`` (initialises a fresh dict) so callers don't have
        to pre-seed Mock instances.
        """
        existing = getattr(empire, "max_storage", None)
        if isinstance(existing, dict):
            existing.clear()
            existing.update(new_max_storage)
        else:
            empire.max_storage = dict(new_max_storage)

    def add_built_design(self, empire: "Empire", design_id: str) -> None:
        empire.built_ship_designs.add(design_id)

    # ------------------------------------------------------------------
    # Post-battle empty-fleet pruning (lifted from PostBattleHook)
    # ------------------------------------------------------------------
    def prune_empty_fleets(
        self,
        empires_by_team_id: dict,
        fleets_by_team_id: dict,
        *,
        event_bus: Any = None,
    ) -> list:
        """Prune fleets that lost all their ships in a battle.

        Lifted from the legacy inline ``_prune_empty_fleets`` in
        ``combat/post_battle_hook`` (deleted PROJ-370 review MAJ-001 cleanup).
        When the empire exposes a ``remove_fleet`` method (production
        ``Empire`` class), delegate so the pursuer-cancellation +
        galaxy-unregister + event-bus semantics are preserved. When it
        doesn't (test fakes), fall back to a direct ``fleets.remove(...)``
        list operation — bit-identical to the legacy inline pruning.

        Returns the list of removed fleet IDs (for caller logging).
        """
        import logging
        log = logging.getLogger(__name__)
        from game.strategy.data.deployed_group import DeployedGroup
        removed_ids: list = []
        for team_id, fleets in list(fleets_by_team_id.items()):
            empire = empires_by_team_id.get(team_id)
            if empire is None:
                continue
            empire_fleets = getattr(empire, "fleets", None)
            empire_groups = getattr(empire, "deployed_groups", None)
            for fleet in list(fleets):
                if fleet.ships:
                    continue
                # PROJ-431 Phase 3: empty deployed groups
                # (FighterWing / SatelliteConstellation) prune from
                # ``empire.deployed_groups``; empty real Fleets prune
                # from ``empire.fleets``.
                if isinstance(fleet, DeployedGroup):
                    if empire_groups is not None and fleet in empire_groups:
                        try:
                            empire_groups.remove(fleet)
                        except ValueError:
                            log.warning(
                                f"DeployedGroup {fleet.id} not found on empire "
                                f"while pruning."
                            )
                        removed_ids.append(fleet.id)
                    continue
                if empire_fleets is None:
                    continue
                if fleet in empire_fleets:
                    if hasattr(empire, "remove_fleet"):
                        empire.remove_fleet(fleet, event_bus=event_bus)
                    else:
                        try:
                            empire_fleets.remove(fleet)
                        except ValueError:
                            log.warning(
                                f"Fleet {fleet.id} not found on empire while pruning."
                            )
                    removed_ids.append(fleet.id)
        return removed_ids
