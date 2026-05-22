"""Fleet query slice (PROJ-309 sub-phase 3.7).

Owns fleet-shaped reads and the fleet-domain validation/colony-pod queries.
The lazy `_fleets_by_hex_cache` is held on `FacadeSessionState` so the
composer can expose it as a writable property for tests.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional, Tuple

from game.core.hex_math import HexCoord
from game.core.validation import ValidationResult
from game.strategy.facade.dto import ContainerSnapshotInfo, FleetInfo

if TYPE_CHECKING:
    from game.strategy.data.fleet import Fleet
    from game.strategy.facade.slices._facade_state import FacadeSessionState


class FleetSlice:
    """Fleet reads + fleet-shaped validation."""

    __slots__ = ("_state",)

    def __init__(self, state: "FacadeSessionState") -> None:
        self._state = state

    # ------------------------------------------------------------------
    # ID helpers (forwarded for legacy tests reading these on the facade)
    # ------------------------------------------------------------------

    def get_fleet_by_id(self, fleet_id: int) -> Optional["Fleet"]:
        """Internal helper to get a fleet by ID across all empires.

        Delegates to `GameSession._get_fleet_by_id()` for O(1) lookup with
        fallback.
        """
        return self._state.get_fleet_by_id(fleet_id)

    # ------------------------------------------------------------------
    # Hex index
    # ------------------------------------------------------------------

    def build_fleet_hex_index(self) -> dict:
        """Build HexCoord -> [Fleet] lookup dict (PROJ-254)."""
        index: dict = {}
        for empire in self._state._session.empires:
            for fleet in empire.fleets:
                loc = fleet.location
                if loc not in index:
                    index[loc] = []
                index[loc].append(fleet)
        return index

    # ------------------------------------------------------------------
    # Public reads
    # ------------------------------------------------------------------

    def get_fleet(self, fleet_id: int) -> Optional[FleetInfo]:
        """Get fleet information by ID."""
        fleet = self._state.get_fleet_by_id(fleet_id)
        if fleet is None:
            return None
        return FleetInfo.from_fleet(fleet)

    def get_fleets_at_hex(self, hex_coord: HexCoord) -> List[FleetInfo]:
        """Get all fleets at a specific hex coordinate.

        PROJ-254: uses per-turn cached hex index for O(1) lookup.
        """
        state = self._state
        current_turn = getattr(state._session, "turn_number", 0)
        if (
            state.fleets_by_hex_cache is None
            or state.fleets_by_hex_turn != current_turn
        ):
            state.fleets_by_hex_cache = self.build_fleet_hex_index()
            state.fleets_by_hex_turn = current_turn

        fleets = state.fleets_by_hex_cache.get(hex_coord, [])
        return [FleetInfo.from_fleet(f) for f in fleets]

    def get_fleet_path_preview(
        self, fleet_id: int, target_hex: HexCoord
    ) -> Optional[List[HexCoord]]:
        """Calculate a path preview for a fleet to a target.

        Used for UI pathfinding preview without committing to a move order.
        """
        fleet = self._state.get_fleet_by_id(fleet_id)
        if fleet is None:
            return None
        return self._state._session.preview_fleet_path(fleet, target_hex)

    def get_fleet_path_projection(
        self, fleet_id: int, max_turns: int = 50
    ) -> List[dict]:
        """Get turn-by-turn path projection for a fleet."""
        fleet = self._state.get_fleet_by_id(fleet_id)
        if fleet is None:
            return []
        return self._state._session.get_fleet_path_projection(fleet, max_turns)

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def can_move_to(self, fleet_id: int, target_hex: HexCoord) -> ValidationResult:
        """Check if a fleet can move to a target hex by previewing a path."""
        fleet = self._state.get_fleet_by_id(fleet_id)
        if fleet is None:
            return ValidationResult.error("Fleet not found.")

        path = self._state._session.preview_fleet_path(fleet, target_hex)
        if path is None:
            return ValidationResult.error("No path to target hex.")

        return ValidationResult.success()

    # ------------------------------------------------------------------
    # Colony pods (PROJ-55)
    # ------------------------------------------------------------------

    # ------------------------------------------------------------------
    # Container snapshots (PROJ-437 Phase 1a)
    # ------------------------------------------------------------------

    def get_fleet_containers(
        self, fleet_id: int,
    ) -> Tuple[ContainerSnapshotInfo, ...]:
        """Return a snapshot per ship's unified storage container.

        PROJ-437 Phase 1a substrate. Each ship in the fleet contributes
        one ``ContainerSnapshotInfo`` projected from
        ``ship.bay_inventory.container_view()``. Mutable Container
        instances do not cross the facade boundary — the UI receives
        only immutable snapshots.

        Returns an empty tuple when the fleet ID is unknown.
        """
        fleet = self._state.get_fleet_by_id(fleet_id)
        if fleet is None:
            return ()
        return tuple(
            _ship_container_snapshot(fleet_id, ship) for ship in fleet.ships
        )

    def get_fleet_remaining_pods(self, fleet_id: int) -> dict:
        """Get remaining colony pods for a fleet (available minus committed).

        Drop pods are universal — any pod works on any planet type.
        """
        from game.strategy.validation.colonize_validator import ColonizeValidator

        fleet = self._state.get_fleet_by_id(fleet_id)
        if fleet is None:
            return {}

        available = ColonizeValidator.count_drop_pods(fleet)
        committed = ColonizeValidator.count_committed_colonize_orders(fleet)
        return {"drop_pod": available - committed}


def _ship_container_snapshot(
    fleet_id: int, ship: "Fleet",
) -> ContainerSnapshotInfo:
    """Project a ship's ``bay_inventory`` into a ``ContainerSnapshotInfo``.

    F-A-013: the snapshot now projects at the bay's real
    ``capacity_mass`` so it matches what the engine load/unload
    handlers enforce. Falls back to ``inf`` only when the ship's cargo
    manager cannot supply a bay capacity (atypical test fixtures).
    """
    inventory = ship.bay_inventory
    try:
        _used, capacity_max = ship._cargo_mgr.get_vehicle_bay_capacity()
    except Exception:  # Intentional broad catch: fixtures may not wire a cargo mgr; treat as uncapped.
        capacity_max = float("inf")
    capacity_mass = float(capacity_max)
    view = inventory.container_view(capacity_mass=capacity_mass)
    return ContainerSnapshotInfo(
        container_id=f"ship:{ship.instance_id}:bay_inventory",
        owner_kind="fleet",
        owner_id=fleet_id,
        label=ship.name,
        capacity_mass=capacity_mass,
        mass_used=view.mass_used,
        allowed_kinds=view.policy.allowed_kinds,
        entries=tuple(view.contents()),
    )
