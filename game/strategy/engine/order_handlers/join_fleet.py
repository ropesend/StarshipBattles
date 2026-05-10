"""JoinFleetHandler — handles `OrderType.JOIN_FLEET` (PROJ-368 Phase 1).

Owns:
    - Single-fleet `process_join_fleet` path (lifted from `OrderProcessor`)
    - BUG-122 three-phase `process_instant_orders` pipeline (Phase A
      collect, Phase B mutual-pair canonicalize, Phase C aliveness
      re-validate + execute)
    - Helpers: `_validate_tick_inputs`, `_execute_fleet_merge`,
      `_elect_canonical_merges`, `_emit_join_cancelled`

Architectural decision (PROJ-368 Phase 1 Task 1.4 — resolves
`decisions.md` row 8):

    `process_instant_orders` is a `JoinFleetHandler`-only public method
    (Option B). The facade calls it explicitly via
    `registry.get(OrderType.JOIN_FLEET).process_instant_orders(empires)`.
    Adding the method to the `IOrderHandler` Protocol with
    `NotImplementedError` defaults on the other 4 handlers (Option A)
    was rejected: the instant path is JOIN_FLEET-only by design, and
    the protocol stays minimal (one method) so non-instant handlers
    don't carry a no-op shim.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, TYPE_CHECKING, Tuple
import logging

from game.strategy.data.fleet import Fleet
from game.strategy.data.order_types import OrderType
from game.strategy.engine.order_handlers.base import (
    BaseOrderHandler,
    OrderExecutionResult,
)
from game.strategy.events.event_types import EventCategory, EventType

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from game.strategy.data.empire import Empire
    from game.strategy.data.galaxy import Galaxy


class JoinFleetHandler(BaseOrderHandler):
    """Handler for `OrderType.JOIN_FLEET` (single-fleet + instant batch)."""

    @property
    def supported_order_types(self) -> Tuple[OrderType, ...]:
        return (OrderType.JOIN_FLEET,)

    def execute_action_order(
        self,
        fleet: Fleet,
        empire: "Empire",
        galaxy: "Galaxy",
        component_registry: Optional[Dict[str, Any]] = None,
        empires: Optional[List["Empire"]] = None,
    ) -> OrderExecutionResult:
        """Process a single JOIN_FLEET order.

        Lifted from `OrderProcessor.process_join_fleet` (lines 110-149).
        Merges fleet into target if at same location.
        """
        order = fleet.get_current_order()
        if not order or order.type != OrderType.JOIN_FLEET:
            return OrderExecutionResult(success=False, merged=False)

        target_fleet = order.target

        # Validation: target must be a valid Fleet (Fleet always has location)
        if target_fleet is None:
            logger.warning("JoinFleetHandler: Join Fleet failed - Target invalid/destroyed.")
            fleet.pop_order()
            return OrderExecutionResult(success=False, merged=False, cancelled=True)

        if fleet.location == target_fleet.location:
            logger.debug(f"JoinFleetHandler: Fleet {fleet.id} merging into {target_fleet.id}")
            self._execute_fleet_merge(fleet, target_fleet, empire)
            return OrderExecutionResult(success=True, merged=True)
        else:
            # Not at location yet
            logger.warning("JoinFleetHandler: Join Fleet failed - Not at same location.")
            fleet.pop_order()
            return OrderExecutionResult(success=False, merged=False)

    def process_instant_orders(
        self,
        empires: List["Empire"],
    ) -> List[Tuple["Empire", Fleet]]:
        """Process JOIN_FLEET orders for co-located fleets during a tick.

        BUG-122: Three-phase implementation with mutual-pair canonicalisation
        and per-iteration aliveness re-validation:

          Phase A - collect candidate (empire, source, target) tuples.
          Phase B - collapse mutual A<->B pairs to a single canonical merge,
                    most-ships-wins (smaller id breaks ties). Cycles of 3+
                    are NOT pre-collapsed - Phase C's re-validation handles
                    them naturally (whichever direction iterates first wins).
          Phase C - execute, re-checking that source AND target are still
                    in empire.fleets at execution time. Skipped entries fire
                    FLEET_JOIN_CANCELLED with a `reason` field.

        Args:
            empires: List of Empire objects.

        Returns:
            List of (empire, fleet) tuples for removed fleets.
        """
        self._validate_tick_inputs(empires)

        # Phase A: collect candidates
        candidates: List[Tuple["Empire", Fleet, Fleet]] = []
        for empire in empires:
            for fleet in list(empire.fleets):
                order = fleet.get_current_order()
                if order and order.type == OrderType.JOIN_FLEET:
                    target_fleet = order.target
                    if target_fleet is not None and fleet.location == target_fleet.location:
                        logger.debug(
                            f"JoinFleetHandler [Instant]: Fleet {fleet.id} candidate merge into {target_fleet.id}"
                        )
                        candidates.append((empire, fleet, target_fleet))

        # Phase B: canonicalise mutual pairs (most ships wins, smaller id breaks ties)
        canonical = self._elect_canonical_merges(candidates)

        # Phase C: execute with re-validation
        result: List[Tuple["Empire", Fleet]] = []
        for empire, fleet, target_fleet in canonical:
            if fleet not in empire.fleets:
                logger.warning(
                    f"[BUG-122] Skip merge: source Fleet {fleet.id} no longer in "
                    f"Empire {empire.id} (absorbed by earlier merge this tick)"
                )
                self._emit_join_cancelled(
                    fleet, target_fleet, empire,
                    reason="absorbed_by_other_merge",
                )
                continue
            if target_fleet not in empire.fleets:
                logger.warning(
                    f"[BUG-122] Skip merge: target Fleet {target_fleet.id} no longer in "
                    f"Empire {empire.id} (absorbed mid-iteration)"
                )
                self._emit_join_cancelled(
                    fleet, target_fleet, empire,
                    reason="target_absorbed_mid_iteration",
                )
                # Pop the now-stale JOIN_FLEET order so the source can move on
                current = fleet.get_current_order()
                if current and current.type == OrderType.JOIN_FLEET and current.target is target_fleet:
                    fleet.pop_order()
                continue
            self._execute_fleet_merge(fleet, target_fleet, empire)
            result.append((empire, fleet))

        return result

    def _validate_tick_inputs(self, empires: List["Empire"]) -> None:
        """PROJ-251: Validate preconditions before mutating state."""
        from game.core.exceptions import ValidationException
        for empire in empires:
            for fleet in empire.fleets:
                if fleet.orders is None:
                    raise ValidationException(
                        f"Empire {empire.id}: fleet '{fleet.id}' has None orders list",
                        context={"empire_id": empire.id, "fleet_id": fleet.id}
                    )

    def _execute_fleet_merge(
        self,
        fleet: Fleet,
        target_fleet: Fleet,
        empire: "Empire",
    ) -> None:
        """Merge fleet into target and log the event.

        Shared logic for both single-fleet processing (execute_action_order)
        and batch processing (process_instant_orders).

        Args:
            fleet: Fleet being merged (will be removed).
            target_fleet: Fleet receiving the merged ships.
            empire: Empire that owns both fleets.
        """
        fleet.merge_with(target_fleet, event_bus=self._event_bus)
        empire.remove_fleet(fleet, event_bus=self._event_bus)
        self._emit_event(
            EventType.FLEET_JOINED,
            category=EventCategory.FLEET_OPERATIONS,
            empire_id=empire.id,
            message=f"Fleet {fleet.id} joined Fleet {target_fleet.id}",
            fleet_id=fleet.id,
            target_fleet_id=target_fleet.id,
            ship_count=len(target_fleet.ships),
        )

    def _elect_canonical_merges(
        self,
        candidates: List[Tuple["Empire", Fleet, Fleet]],
    ) -> List[Tuple["Empire", Fleet, Fleet]]:
        """Collapse mutual A<->B JOIN_FLEET pairs into a single canonical merge.

        Election rule (BUG-122 Q2): the fleet with more ships absorbs the
        other. On equal ship counts, the smaller fleet id wins (deterministic
        for tests). Ship counts are read at election time and do NOT change
        during the rest of this tick - the rule is fixed once decided.

        Cycles of 3+ are NOT collapsed here; Phase C's per-iteration
        aliveness check handles them: whichever direction iterates first
        runs, the rest skip with `target_absorbed_mid_iteration`. This
        keeps cycle handling simple and parallel to PROJ-275's N-team
        battle pattern (no pairwise decomposition).

        Args:
            candidates: [(empire, source, target), ...] from Phase A.

        Returns:
            Filtered list with mutual pairs collapsed to one tuple each.
        """
        # Index candidates by source for O(1) mutual lookup
        by_source: Dict[Fleet, Tuple["Empire", Fleet, Fleet]] = {
            source: (empire, source, target)
            for empire, source, target in candidates
        }
        result: List[Tuple["Empire", Fleet, Fleet]] = []
        consumed: set = set()

        for empire, source, target in candidates:
            if source in consumed:
                continue
            mutual = by_source.get(target)
            if mutual is not None and mutual[2] is source:
                # Mutual pair: source <-> target. Elect the winner.
                source_ships = len(source.ships)
                target_ships = len(target.ships)
                if source_ships > target_ships:
                    winner, loser = source, target
                elif target_ships > source_ships:
                    winner, loser = target, source
                else:
                    # Tie on ship count: smaller id wins (deterministic).
                    if str(source.id) < str(target.id):
                        winner, loser = source, target
                    else:
                        winner, loser = target, source
                logger.warning(
                    f"[BUG-122] Mutual JOIN_FLEET: Fleet {loser.id} ({len(loser.ships)} ships) "
                    f"absorbed by Fleet {winner.id} ({len(winner.ships)} ships)"
                )
                result.append((empire, loser, winner))
                consumed.add(source)
                consumed.add(target)
            else:
                result.append((empire, source, target))
                consumed.add(source)

        return result

    def _emit_join_cancelled(
        self,
        fleet: Fleet,
        target_fleet: Fleet,
        empire: "Empire",
        *,
        reason: str,
    ) -> None:
        """Emit a FLEET_JOIN_CANCELLED event with a structured reason field.

        BUG-122: reasons used by process_instant_orders are
        `absorbed_by_other_merge` and `target_absorbed_mid_iteration`.
        Fleet.merge_with uses `self_target_after_redirect`. Empire.remove_fleet
        uses an unstructured cancellation message (PROJ-222 path).
        """
        self._emit_event(
            EventType.FLEET_JOIN_CANCELLED,
            category=EventCategory.FLEET_OPERATIONS,
            empire_id=empire.id,
            message=f"Fleet {fleet.id} join order cancelled: {reason}",
            fleet_id=fleet.id,
            target_fleet_id=target_fleet.id,
            reason=reason,
        )
