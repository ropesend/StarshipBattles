"""FleetWriteService — owns Fleet writes outside of navigation.

PROJ-370 Phase 2: implements ``IFleetMutator`` for the non-navigation slice
(orders, ships, hierarchy, construction queue, display name, fleet policy).
The navigation slice (`set_location`, `set_path`) is co-implemented by
``FleetNavigationService``; ``FleetWriteService`` forwards those two methods
to the nav service so engines see one ``IFleetMutator`` interface.

Wiring:
    Constructed in ``GameSession.__init__`` and threaded through
    ``TurnEngineConfig.create_default()`` (post-PROJ-369). Engines accept
    ``fleet_mutator: IFleetMutator | None = None`` and pull from the
    config when ``None``.

Boundary:
    The mutator delegates to existing ``Fleet`` public methods where they
    exist (``add_ship``, ``remove_ship``, ``add_order``, ``pop_order``,
    ``clear_orders``, ``add_task_force``, ``remove_task_force``). It does
    NOT re-implement fleet semantics — speed recalculation, pursuer
    unregistration, etc. continue to flow through the data class.

See ``Projects/active_projects/PROJ-370/`` for the full design.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

from game.core.error_codes import ErrorCode
from game.core.exceptions import ValidationException

if TYPE_CHECKING:
    from game.core.hex_math import HexCoord
    from game.strategy.data.fleet import Fleet
    from game.strategy.data.order_types import Order
    from game.strategy.services.fleet_navigation_service import FleetNavigationService


__all__ = ["FleetWriteService"]


class FleetWriteService:
    """Concrete ``IFleetMutator`` implementation.

    Two-construction shape: callers pass an optional ``FleetNavigationService``
    to satisfy the navigation slice. Without it, ``set_location`` /
    ``set_path`` raise ``ValidationException`` (``MISSING_DEPENDENCY``).
    """

    def __init__(
        self,
        navigation_service: "FleetNavigationService | None" = None,
    ) -> None:
        self._nav = navigation_service

    # ------------------------------------------------------------------
    # Navigation slice (delegated to FleetNavigationService)
    # ------------------------------------------------------------------
    def set_location(self, fleet: "Fleet", new_location: "HexCoord") -> None:
        if self._nav is None:
            raise ValidationException(
                "FleetWriteService requires FleetNavigationService for "
                "navigation writes; pass navigation_service=... at construction.",
                code=ErrorCode.MISSING_DEPENDENCY.value,
            )
        self._nav.set_location(fleet, new_location)

    def set_path(self, fleet: "Fleet", new_path: "list[HexCoord]") -> None:
        if self._nav is None:
            raise ValidationException(
                "FleetWriteService requires FleetNavigationService for "
                "navigation writes; pass navigation_service=... at construction.",
                code=ErrorCode.MISSING_DEPENDENCY.value,
            )
        self._nav.set_path(fleet, new_path)

    # ------------------------------------------------------------------
    # Order queue
    # ------------------------------------------------------------------
    def append_order(self, fleet: "Fleet", order: "Order") -> None:
        fleet.add_order(order)

    def insert_order(self, fleet: "Fleet", index: int, order: "Order") -> None:
        fleet.add_order(order, index=index)

    def pop_order(self, fleet: "Fleet", index: int = 0) -> "Order | None":
        if index == 0:
            return fleet.pop_order()
        return fleet.remove_order_at(index)

    def clear_orders(self, fleet: "Fleet") -> None:
        fleet.clear_orders()

    def swap_orders(
        self, fleet: "Fleet", index_a: int, index_b: int
    ) -> None:
        """Swap two orders in the fleet's queue by index."""
        fleet.orders[index_a], fleet.orders[index_b] = (
            fleet.orders[index_b],
            fleet.orders[index_a],
        )

    # ------------------------------------------------------------------
    # Ship membership
    # ------------------------------------------------------------------
    def add_ship(self, fleet: "Fleet", ship: Any) -> None:
        fleet.add_ship(ship)

    def remove_ship(self, fleet: "Fleet", ship: Any) -> bool:
        return fleet.remove_ship(ship)

    # ------------------------------------------------------------------
    # Identity / policy
    # ------------------------------------------------------------------
    def set_display_name(self, fleet: "Fleet", name: str) -> None:
        fleet.display_name = name

    def set_fleet_policy(self, fleet: "Fleet", policy: Any) -> None:
        fleet.fleet_policy = policy

    # ------------------------------------------------------------------
    # Construction queue
    # ------------------------------------------------------------------
    def append_construction_item(self, fleet: "Fleet", item: dict) -> None:
        fleet.construction_queue.append(item)

    def pop_construction_item(self, fleet: "Fleet", index: int = 0) -> dict:
        return fleet.construction_queue.pop(index)

    def set_construction_queue_paused(
        self, fleet: "Fleet", paused: bool
    ) -> None:
        fleet.construction_queue_paused = bool(paused)

    # ------------------------------------------------------------------
    # Hierarchy (TaskForce membership)
    # ------------------------------------------------------------------
    def add_task_force(self, fleet: "Fleet", tf: Any) -> None:
        fleet.add_task_force(tf)

    def remove_task_force(self, fleet: "Fleet", tf: Any) -> bool:
        return fleet.remove_task_force(tf)
