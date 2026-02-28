"""
FleetCargoProjector - Projects future cargo state by walking the order queue.

When queuing transfer orders, the validator needs to know what cargo the fleet
will have AFTER earlier queued orders execute. This utility walks the order
queue and computes projected cargo values.

Example: A fleet with 0 passengers and a queued "load 5000" order should
allow a subsequent "drop 5000" order to be queued, even though the fleet
currently has no passengers.
"""

from typing import Dict, Any
from game.strategy.data.fleet import Fleet
from game.strategy.data.order_types import OrderType


class FleetCargoProjector:
    """Projects future cargo state by simulating queued order effects."""

    @staticmethod
    def get_projected_cargo(fleet: Fleet, cargo_type: str) -> int:
        """
        Compute projected cargo after all queued orders execute.

        Walks the fleet's order queue and applies load/unload deltas
        to the current cargo level.

        Args:
            fleet: The fleet to project cargo for
            cargo_type: Type of cargo (e.g., 'passengers')

        Returns:
            Projected cargo amount after all queued orders
        """
        current = fleet.get_fleet_cargo_current(cargo_type)
        capacity = fleet.get_fleet_cargo_capacity(cargo_type)
        projected = current

        for order in fleet.orders:
            if order.type in (OrderType.TRANSFER, OrderType.LOAD_POPULATION, OrderType.UNLOAD_POPULATION):
                params = order.target
                if not isinstance(params, dict):
                    continue

                order_cargo_type = params.get('cargo_type', '')
                if order_cargo_type != cargo_type:
                    continue

                direction = params.get('direction', '')
                amount = params.get('amount', 0)

                if direction == 'load':
                    # Loading: add amount (0 means fill to capacity)
                    delta = amount if amount > 0 else (capacity - projected)
                    projected = min(projected + delta, capacity)
                elif direction == 'unload':
                    # Unloading: subtract amount (0 means unload all)
                    delta = amount if amount > 0 else projected
                    projected = max(projected - delta, 0)

        return projected

