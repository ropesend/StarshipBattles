"""
FleetOrderProcessor - Centralized order lifecycle management.

PROJ-12 Phase 3: Extracted from TurnEngine to decompose the god class.
STRAT-006: Centralize order lifecycle management.

Responsibilities:
- Order completion (pop_order in single location)
- Order cancellation (with reason tracking)
- JOIN_FLEET processing (instant and end-of-turn)
- COLONIZE processing
- Instant order processing during ticks
"""

from dataclasses import dataclass
from typing import Optional, List, Tuple, TYPE_CHECKING

from game.core.logger import log_debug, log_warning, log_info
from game.strategy.data.fleet import Fleet, FleetOrder, OrderType
from game.strategy.data.hex_math import HexCoord

if TYPE_CHECKING:
    pass


@dataclass
class JoinFleetResult:
    """Result of a JOIN_FLEET operation."""
    merged: bool
    cancelled: bool = False


@dataclass
class ColonizeResult:
    """Result of a COLONIZE operation."""
    colonized: bool
    planet_name: Optional[str] = None


class FleetOrderProcessor:
    """
    Processor for fleet order lifecycle management.

    Centralizes order state management:
    - complete_order() - mark order as done
    - cancel_order() - cancel with reason
    - process_join_fleet() - handle JOIN_FLEET orders
    - process_colonize() - handle COLONIZE orders
    - process_instant_orders() - tick-based instant orders
    - process_end_turn_orders() - end-of-turn orders
    """

    def __init__(self):
        """Initialize the fleet order processor."""
        pass

    def complete_order(self, fleet: Fleet) -> Optional[FleetOrder]:
        """
        Complete the current order for a fleet.

        Pops the order from the queue, centralizing order completion logic.

        Args:
            fleet: Fleet whose order completed

        Returns:
            The completed order, or None if no order
        """
        order = fleet.get_current_order()
        if not order:
            return None

        fleet.pop_order()
        return order

    def cancel_order(self, fleet: Fleet, reason: str = "") -> Optional[FleetOrder]:
        """
        Cancel the current order for a fleet.

        Pops the order and logs the cancellation reason.

        Args:
            fleet: Fleet whose order is cancelled
            reason: Reason for cancellation (for logging)

        Returns:
            The cancelled order, or None if no order
        """
        order = fleet.get_current_order()
        if not order:
            return None

        log_debug(f"Fleet {fleet.id} order cancelled: {reason}")
        fleet.pop_order()
        return order

    def cancel_all_orders(self, fleet: Fleet, reason: str = "") -> None:
        """
        Cancel all orders for a fleet.

        Clears the entire order queue.

        Args:
            fleet: Fleet whose orders are cancelled
            reason: Reason for cancellation (for logging)
        """
        log_debug(f"Fleet {fleet.id} all orders cancelled: {reason}")
        fleet.clear_orders()

    def process_join_fleet(
        self,
        fleet: Fleet,
        empire,
        galaxy
    ) -> JoinFleetResult:
        """
        Process a JOIN_FLEET order.

        Merges fleet into target if at same location.

        Args:
            fleet: Fleet with JOIN_FLEET order
            empire: Empire that owns the fleet
            galaxy: Galaxy for validation

        Returns:
            JoinFleetResult with merge status
        """
        order = fleet.get_current_order()
        if not order or order.type != OrderType.JOIN_FLEET:
            return JoinFleetResult(merged=False)

        target_fleet = order.target

        # Validation
        if not target_fleet or not hasattr(target_fleet, 'location'):
            log_warning("FleetOrderProcessor: Join Fleet failed - Target invalid/destroyed.")
            fleet.pop_order()
            return JoinFleetResult(merged=False, cancelled=True)

        if fleet.location == target_fleet.location:
            log_debug(f"FleetOrderProcessor: Fleet {fleet.id} merging into {target_fleet.id}")
            fleet.merge_with(target_fleet)
            empire.remove_fleet(fleet)
            return JoinFleetResult(merged=True)
        else:
            # Not at location yet
            log_warning("FleetOrderProcessor: Join Fleet failed - Not at same location.")
            fleet.pop_order()
            return JoinFleetResult(merged=False)

    def process_colonize(
        self,
        fleet: Fleet,
        empire,
        galaxy
    ) -> ColonizeResult:
        """
        Process a COLONIZE order.

        PROJ-36: Uses ColonizeValidator for validation.

        Claims a planet for the empire if valid.

        Args:
            fleet: Fleet with COLONIZE order
            empire: Empire that owns the fleet
            galaxy: Galaxy for planet lookup

        Returns:
            ColonizeResult with colonization status
        """
        from game.strategy.validation import ColonizeValidator

        order = fleet.get_current_order()
        if not order or order.type != OrderType.COLONIZE:
            return ColonizeResult(colonized=False)

        target_planet = order.target

        # PROJ-36: Use centralized validation
        validation = ColonizeValidator.validate(galaxy, fleet, target_planet)
        if not validation.is_valid:
            log_warning(f"FleetOrderProcessor: Colonize failed - {validation.message}")
            fleet.pop_order()
            return ColonizeResult(colonized=False)

        # Determine final planet (for "Any" case, pick first valid candidate)
        if target_planet is not None:
            final_planet = target_planet
        else:
            planets_at_loc = galaxy.get_planets_at_global_hex(fleet.location)
            valid_candidates = [p for p in planets_at_loc if p.owner_id is None]
            final_planet = valid_candidates[0]

        # Execute colonization
        empire.add_colony(final_planet)
        fleet.pop_order()
        empire.remove_fleet(fleet)

        log_info(f"FleetOrderProcessor: Colonization successful. {empire.name} claimed {final_planet.name}")
        return ColonizeResult(colonized=True, planet_name=final_planet.name)

    def process_end_turn_orders(
        self,
        fleet: Fleet,
        empire,
        galaxy
    ) -> bool:
        """
        Process static orders at end of turn (COLONIZE, JOIN_FLEET).

        Args:
            fleet: Fleet to process
            empire: Empire that owns the fleet
            galaxy: Galaxy for validation

        Returns:
            True if fleet was consumed/deleted by the order, False otherwise
        """
        order = fleet.get_current_order()
        if not order:
            return False

        if order.type == OrderType.COLONIZE:
            result = self.process_colonize(fleet, empire, galaxy)
            return result.colonized

        elif order.type == OrderType.JOIN_FLEET:
            result = self.process_join_fleet(fleet, empire, galaxy)
            return result.merged

        return False

    def process_instant_orders(
        self,
        empires: List
    ) -> List[Tuple]:
        """
        Process instant orders during tick (JOIN_FLEET when co-located).

        This processes JOIN_FLEET orders for any fleets that are already
        co-located with their target. Happens every subtick.

        Args:
            empires: List of Empire objects

        Returns:
            List of (empire, fleet) tuples for removed fleets
        """
        fleets_to_remove = []

        for empire in empires:
            for fleet in list(empire.fleets):  # Copy list since we may modify it
                order = fleet.get_current_order()
                if order and order.type == OrderType.JOIN_FLEET:
                    target_fleet = order.target
                    if target_fleet and hasattr(target_fleet, 'location'):
                        if fleet.location == target_fleet.location:
                            log_debug(f"FleetOrderProcessor [Instant]: Fleet {fleet.id} merging into {target_fleet.id}")
                            fleet.merge_with(target_fleet)
                            fleets_to_remove.append((empire, fleet))

        # Remove merged fleets
        for empire, fleet in fleets_to_remove:
            empire.remove_fleet(fleet)

        return fleets_to_remove
