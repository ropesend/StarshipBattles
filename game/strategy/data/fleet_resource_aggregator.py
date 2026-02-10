"""Fleet resource aggregation delegate.

Extracted from Fleet class (PROJ-87 Phase 3) to consolidate
fleet-wide resource calculation and consumption logic.
"""

from typing import Dict, Any, TYPE_CHECKING
from game.core.constants import ResourceType

if TYPE_CHECKING:
    from game.strategy.data.fleet import Fleet


class FleetResourceAggregator:
    """
    Handles resource aggregation across all ships in a fleet.

    Extracted from Fleet to centralize the loop-over-ships pattern
    used in movement cost, warp cost, and cargo calculations.
    """

    def __init__(self, fleet: 'Fleet'):
        """
        Initialize with reference to parent fleet.

        Args:
            fleet: The Fleet instance this aggregator serves.
        """
        self._fleet = fleet

    # --- Generic Movement Resource Methods ---

    def get_movement_resource_costs(self) -> Dict[str, float]:
        """
        Get total fleet resource costs per hex of movement.

        Returns:
            Dict mapping resource type to total fleet cost per hex.
        """
        total_costs: Dict[str, float] = {}
        for ship in self._fleet.get_combat_capable_ships():
            ship_costs = ship.get_all_resource_costs_per_hex()
            for resource_type, cost in ship_costs.items():
                total_costs[resource_type] = total_costs.get(resource_type, 0) + cost
        return total_costs

    def has_resources_for_movement(self) -> bool:
        """
        Check if fleet has resources for at least one hex of movement.

        This is data-driven - checks all resource types that have per-hex costs.

        Returns:
            True if all combat-capable ships have enough of all required resources.
        """
        for ship in self._fleet.get_combat_capable_ships():
            costs = ship.get_all_resource_costs_per_hex()
            for resource_type, cost in costs.items():
                if cost > 0:
                    current = ship.get_current_resource(resource_type)
                    if current < cost:
                        return False
        return True

    def consume_movement_resources(self, hexes: int = 1) -> bool:
        """
        Consume all movement resources from all ships.

        This is data-driven - consumes all resource types that have per-hex costs.

        Args:
            hexes: Number of hexes moved (default 1)

        Returns:
            True if all ships had sufficient resources, False otherwise.
            Note: If False, no resources are consumed (atomic operation).
        """
        ships = self._fleet.get_combat_capable_ships()

        # First, verify all ships have enough resources
        for ship in ships:
            costs = ship.get_all_resource_costs_per_hex()
            for resource_type, cost in costs.items():
                total_cost = cost * hexes
                if total_cost > 0:
                    if ship.get_current_resource(resource_type) < total_cost:
                        return False

        # All ships have enough, now consume
        for ship in ships:
            costs = ship.get_all_resource_costs_per_hex()
            for resource_type, cost in costs.items():
                total_cost = cost * hexes
                if total_cost > 0:
                    ship.consume_resource(resource_type, total_cost)

        return True

    # --- Warp Resource Methods ---

    def get_warp_resource_costs(self) -> Dict[str, float]:
        """
        Get total fleet resource costs for a warp jump.

        Returns:
            Dict mapping resource type to total fleet cost per warp jump.
        """
        total_costs: Dict[str, float] = {}
        for ship in self._fleet.get_combat_capable_ships():
            ship_costs = ship.get_warp_resource_costs()
            for resource_type, cost in ship_costs.items():
                total_costs[resource_type] = total_costs.get(resource_type, 0) + cost
        return total_costs

    def has_resources_for_warp(self) -> bool:
        """
        Check if fleet has all required resources for a warp jump.

        This is data-driven - checks all resource types defined in warp costs.
        If no resource cost is specified, no resource check is performed.

        Returns:
            True if all combat-capable ships have enough resources for one warp.
        """
        for ship in self._fleet.get_combat_capable_ships():
            warp_costs = ship.get_warp_resource_costs()
            for resource_type, cost in warp_costs.items():
                if cost > 0:
                    current = ship.get_current_resource(resource_type)
                    if current < cost:
                        return False
        return True

    def consume_warp_resources(self) -> bool:
        """
        Consume all required resources from all ships for a warp jump.

        This is data-driven - consumes all resource types defined in warp costs.
        If no resource cost is specified, no resources are consumed.

        Returns:
            True if all ships had sufficient resources, False otherwise.
            Note: If False, no resources are consumed (atomic operation).
        """
        ships = self._fleet.get_combat_capable_ships()

        # First, verify all ships have enough resources
        for ship in ships:
            warp_costs = ship.get_warp_resource_costs()
            for resource_type, cost in warp_costs.items():
                if cost > 0:
                    if ship.get_current_resource(resource_type) < cost:
                        return False

        # All ships have enough, now consume
        for ship in ships:
            warp_costs = ship.get_warp_resource_costs()
            for resource_type, cost in warp_costs.items():
                if cost > 0:
                    ship.consume_resource(resource_type, cost)

        return True

    # --- Capability Summary Methods ---

    def fuel_endurance(self) -> int:
        """
        Calculate fleet fuel endurance in hexes.

        Returns:
            Minimum hexes any ship can travel before running out of fuel.
            Returns -1 if fleet has unlimited endurance (no fuel consumption).
        """
        min_endurance = float('inf')

        for ship in self._fleet.get_combat_capable_ships():
            cost_per_hex = ship.get_all_resource_costs_per_hex().get(ResourceType.FUEL, 0.0)
            if cost_per_hex <= 0:
                continue  # This ship doesn't consume fuel

            current_fuel = ship.get_current_resource(ResourceType.FUEL)
            endurance = int(current_fuel / cost_per_hex) if cost_per_hex > 0 else float('inf')
            min_endurance = min(min_endurance, endurance)

        return int(min_endurance) if min_endurance != float('inf') else -1

    def warp_jumps_remaining(self) -> int:
        """
        Calculate how many warp jumps fleet can make.

        This is data-driven - considers all resource costs as
        specified by the warp drive components.

        Returns:
            Minimum jumps any ship can make based on resources.
            Returns 0 if fleet cannot use warp at all.
            Returns -1 if fleet has unlimited jumps (no resource cost).
        """
        if not self._fleet.can_use_warp():
            return 0

        min_jumps = float('inf')

        for ship in self._fleet.get_combat_capable_ships():
            warp_costs = ship.get_warp_resource_costs()
            for resource_type, cost in warp_costs.items():
                if cost > 0:
                    current = ship.get_current_resource(resource_type)
                    jumps = int(current / cost)
                    min_jumps = min(min_jumps, jumps)

        return int(min_jumps) if min_jumps != float('inf') else -1

    def get_capability_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive fleet capability summary for UI.

        Returns:
            Dict with all fleet capability information.
        """
        return {
            'speed': self._fleet.speed,
            'can_warp': self._fleet.can_use_warp(),
            'warp_limiting_ship': self._fleet.get_warp_limiting_ship(),
            'fuel_endurance': self.fuel_endurance(),
            'warp_jumps': self.warp_jumps_remaining(),
            'movement_resource_costs': self.get_movement_resource_costs(),
            'warp_resource_costs': self.get_warp_resource_costs(),
        }

    # --- Cargo Methods ---

    def get_fleet_cargo_capacity(self, cargo_type: str) -> int:
        """
        Get total fleet cargo capacity for a specific cargo type.

        Args:
            cargo_type: Type of cargo (e.g., 'passengers', 'generic')

        Returns:
            Total capacity summed across all combat-capable ships.
        """
        total = 0
        for ship in self._fleet.get_combat_capable_ships():
            total += ship.get_cargo_capacity(cargo_type)
        return total

    def get_fleet_cargo_current(self, cargo_type: str) -> int:
        """
        Get total current cargo loaded in the fleet for a specific type.

        Args:
            cargo_type: Type of cargo (e.g., 'passengers', 'generic')

        Returns:
            Total cargo amount summed across all ships.
        """
        total = 0
        for ship in self._fleet.ships:
            total += ship.get_current_cargo(cargo_type)
        return total

    def load_cargo_to_fleet(self, cargo_type: str, amount: int) -> int:
        """
        Load cargo to the fleet, distributing across ships with capacity.

        Args:
            cargo_type: Type of cargo to load
            amount: Total amount to load

        Returns:
            Actual amount loaded (may be less than requested if capacity limited).
        """
        if amount <= 0:
            return 0

        remaining = amount
        total_loaded = 0

        for ship in self._fleet.get_combat_capable_ships():
            if remaining <= 0:
                break
            loaded = ship.load_cargo(cargo_type, remaining)
            total_loaded += loaded
            remaining -= loaded

        return total_loaded

    def unload_cargo_from_fleet(self, cargo_type: str, amount: int) -> int:
        """
        Unload cargo from the fleet, collecting from ships.

        Args:
            cargo_type: Type of cargo to unload
            amount: Total amount to unload

        Returns:
            Actual amount unloaded (may be less than requested if not enough cargo).
        """
        if amount <= 0:
            return 0

        remaining = amount
        total_unloaded = 0

        for ship in self._fleet.ships:
            if remaining <= 0:
                break
            unloaded = ship.unload_cargo(cargo_type, remaining)
            total_unloaded += unloaded
            remaining -= unloaded

        return total_unloaded
