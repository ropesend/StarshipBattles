"""
Fleet pursuer tracking delegate (PROJ-222).

Tracks which fleets are actively pursuing this fleet via MOVE_TO_FLEET
or JOIN_FLEET orders. Enables automatic redirect-on-merge and
cancel-on-destruction.

Not serialized — rebuilt from order targets on load.
"""

import logging
from typing import FrozenSet, List, Set, Tuple, TYPE_CHECKING

from game.strategy.data.order_types import OrderType

if TYPE_CHECKING:
    from game.strategy.data.fleet import Fleet

logger = logging.getLogger(__name__)

# Order types that constitute "pursuing" another fleet
PURSUIT_ORDER_TYPES = frozenset({OrderType.MOVE_TO_FLEET, OrderType.JOIN_FLEET})


class FleetPursuerTracker:
    """Tracks fleets that are pursuing this fleet.

    When Fleet B is being pursued by Fleet A (via MOVE_TO_FLEET or
    JOIN_FLEET orders), Fleet B's tracker holds a reference to A.

    On merge (B into C): all pursuers of B are redirected to C.
    On destruction of B: all pursuers have their orders cancelled.
    """

    def __init__(self, fleet: 'Fleet') -> None:
        self._fleet = fleet
        self._pursuers: Set['Fleet'] = set()

    @property
    def pursuers(self) -> FrozenSet['Fleet']:
        """Read-only view of all fleets pursuing this fleet."""
        return frozenset(self._pursuers)

    @property
    def pursuer_count(self) -> int:
        """Number of fleets currently pursuing this fleet."""
        return len(self._pursuers)

    def add_pursuer(self, fleet: 'Fleet') -> None:
        """Register a fleet as pursuing this fleet."""
        self._pursuers.add(fleet)

    def remove_pursuer(self, fleet: 'Fleet') -> None:
        """Unregister a fleet from pursuing this fleet."""
        self._pursuers.discard(fleet)

    def redirect_pursuers(
        self,
        new_target: 'Fleet',
        *,
        exclude: FrozenSet['Fleet'] = frozenset(),
    ) -> Tuple[List[Tuple['Fleet', 'Fleet']], List['Fleet']]:
        """Redirect all pursuers from this fleet to new_target.

        Called when this fleet merges into new_target. Rewrites all
        MOVE_TO_FLEET/JOIN_FLEET order targets on each pursuer from
        self._fleet to new_target, and transfers the pursuer
        registration to new_target's tracker.

        BUG-122: Pursuers in `exclude` are NOT rewritten and NOT transferred
        to new_target. They are returned in the second tuple element so the
        caller can drop their now-stale orders. The typical case is when
        new_target itself is one of self._pursuers (mutual JOIN_FLEET),
        which would otherwise create a self-targeting order.

        Args:
            new_target: Fleet to redirect pursuit to.
            exclude: Pursuers to skip (kept out of redirect AND new target).

        Returns:
            (redirected, excluded):
              redirected: [(pursuer, old_target), ...] for actually-redirected pursuers
              excluded: [pursuer, ...] for pursuers that were skipped
        """
        old_target = self._fleet
        redirected: List[Tuple['Fleet', 'Fleet']] = []
        excluded_list: List['Fleet'] = []

        if not self._pursuers:
            return redirected, excluded_list

        for pursuer in list(self._pursuers):
            if pursuer in exclude:
                excluded_list.append(pursuer)
                continue

            # Rewrite order targets
            for order in pursuer.orders:
                if order.type in PURSUIT_ORDER_TYPES and order.target is old_target:
                    order.target = new_target

            # Transfer registration to new target
            if hasattr(new_target, '_pursuer_tracker'):
                new_target._pursuer_tracker.add_pursuer(pursuer)
            redirected.append((pursuer, old_target))

        # Excluded pursuers are removed from this fleet's pursuer set too —
        # this fleet is being absorbed, so they aren't "still pursuing" anything.
        self._pursuers.clear()
        return redirected, excluded_list

    def notify_target_destroyed(self) -> List['Fleet']:
        """Cancel all pursuer orders targeting this fleet.

        Called when this fleet is destroyed or removed. Removes all
        MOVE_TO_FLEET/JOIN_FLEET orders that target this fleet from
        each pursuer.

        Returns:
            List of affected pursuer fleets for event logging.
        """
        if not self._pursuers:
            return []

        affected: List['Fleet'] = []

        for pursuer in list(self._pursuers):
            self._remove_orders_targeting_fleet(pursuer)
            affected.append(pursuer)

        self._pursuers.clear()
        return affected

    def _remove_orders_targeting_fleet(self, pursuer: 'Fleet') -> None:
        """Remove all orders from pursuer that target this fleet."""
        target = self._fleet
        # Iterate in reverse to safely remove by index
        for i in range(len(pursuer.orders) - 1, -1, -1):
            order = pursuer.orders[i]
            if order.type in PURSUIT_ORDER_TYPES and order.target is target:
                pursuer.orders.pop(i)

        # Clear path if active order was removed
        if not pursuer.orders or (pursuer.path and not pursuer.orders):
            pursuer.path = []
