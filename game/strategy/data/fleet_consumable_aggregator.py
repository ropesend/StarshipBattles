"""Fleet consumable aggregation delegate.

Extracted from Fleet class (PROJ-87 Phase 3) to consolidate
fleet-wide resource calculation and consumption logic.
"""

from typing import Callable, Dict, Any, TYPE_CHECKING
if TYPE_CHECKING:
    from game.strategy.data.fleet import Fleet
    from game.strategy.data.ship_instance import ShipInstance


class FleetConsumableAggregator:
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

    # --- Helper Methods (PROJ-204) ---

    def _accumulate_ship_costs(
        self, cost_getter: Callable[['ShipInstance'], Dict[str, float]]
    ) -> Dict[str, float]:
        """
        Accumulate resource costs from all combat-capable ships.

        PROJ-204 Phase 2: Consolidates duplicated cost accumulation (CQ-07).

        Args:
            cost_getter: Function that returns a dict of costs for a ship.

        Returns:
            Dict mapping resource type to total fleet cost.
        """
        total_costs: Dict[str, float] = {}
        for ship in self._fleet.get_combat_capable_ships():
            ship_costs = cost_getter(ship)
            for resource_type, cost in ship_costs.items():
                total_costs[resource_type] = total_costs.get(resource_type, 0) + cost
        return total_costs

    def _verify_and_consume_resources(
        self,
        cost_getter: Callable[['ShipInstance'], Dict[str, float]],
        consume: bool = False,
        multiplier: int = 1
    ) -> bool:
        """
        Verify and optionally consume resources from all combat-capable ships.

        PROJ-204 Phase 4: Consolidates duplicated verify/consume patterns (CQ-02).
        This is an atomic operation - either all ships have enough resources
        and consumption happens, or no resources are consumed.

        Args:
            cost_getter: Function that returns a dict of costs for a ship.
            consume: If True, consume resources after verification passes.
            multiplier: Multiply costs by this factor (e.g., hexes moved).

        Returns:
            True if all ships have sufficient resources, False otherwise.
        """
        ships = self._fleet.get_combat_capable_ships()

        # Phase 1: Verify all ships have enough resources
        for ship in ships:
            costs = cost_getter(ship)
            for resource_type, cost in costs.items():
                total_cost = cost * multiplier
                if total_cost > 0:
                    if ship.get_current_resource(resource_type) < total_cost:
                        return False

        # Phase 2: Consume resources if requested
        if consume:
            for ship in ships:
                costs = cost_getter(ship)
                for resource_type, cost in costs.items():
                    total_cost = cost * multiplier
                    if total_cost > 0:
                        ship.consume_resource(resource_type, total_cost)

        return True

    # --- Generic Movement Resource Methods ---

    def get_movement_resource_costs(self) -> Dict[str, float]:
        """
        Get total fleet resource costs per hex of movement.

        Returns:
            Dict mapping resource type to total fleet cost per hex.
        """
        return self._accumulate_ship_costs(lambda ship: ship.get_all_resource_costs_per_hex())

    def has_resources_for_movement(self) -> bool:
        """
        Check if fleet has resources for at least one hex of movement.

        This is data-driven - checks all resource types that have per-hex costs.

        Returns:
            True if all combat-capable ships have enough of all required resources.
        """
        return self._verify_and_consume_resources(
            lambda ship: ship.get_all_resource_costs_per_hex(),
            consume=False
        )

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
        return self._verify_and_consume_resources(
            lambda ship: ship.get_all_resource_costs_per_hex(),
            consume=True,
            multiplier=hexes
        )

    # --- Warp Resource Methods ---

    def get_warp_resource_costs(self) -> Dict[str, float]:
        """
        Get total fleet resource costs for a warp jump.

        Returns:
            Dict mapping resource type to total fleet cost per warp jump.
        """
        return self._accumulate_ship_costs(lambda ship: ship.get_warp_resource_costs())

    def has_resources_for_warp(self) -> bool:
        """
        Check if fleet has all required resources for a warp jump.

        This is data-driven - checks all resource types defined in warp costs.
        If no resource cost is specified, no resource check is performed.

        Returns:
            True if all combat-capable ships have enough resources for one warp.
        """
        return self._verify_and_consume_resources(
            lambda ship: ship.get_warp_resource_costs(),
            consume=False
        )

    def consume_warp_resources(self) -> bool:
        """
        Consume all required resources from all ships for a warp jump.

        This is data-driven - consumes all resource types defined in warp costs.
        If no resource cost is specified, no resources are consumed.

        Returns:
            True if all ships had sufficient resources, False otherwise.
            Note: If False, no resources are consumed (atomic operation).
        """
        return self._verify_and_consume_resources(
            lambda ship: ship.get_warp_resource_costs(),
            consume=True
        )

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
            cost_per_hex = ship.get_all_resource_costs_per_hex().get("fuel", 0.0)
            if cost_per_hex <= 0:
                continue  # This ship doesn't consume fuel

            current_fuel = ship.get_current_resource("fuel")
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
        if not self._fleet.capabilities.can_use_warp():
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
            'can_warp': self._fleet.capabilities.can_use_warp(),
            'warp_limiting_ship': self._fleet.capabilities.get_warp_limiting_ship(),
            'fuel_endurance': self.fuel_endurance(),
            'warp_jumps': self.warp_jumps_remaining(),
            'movement_resource_costs': self.get_movement_resource_costs(),
            'warp_resource_costs': self.get_warp_resource_costs(),
        }

    # --- Pod Storage Methods ---

    def get_fleet_pod_capacity(self) -> float:
        """Get total pod storage mass capacity across all ships in fleet."""
        return sum(ship._cargo_mgr.get_pod_storage_capacity() for ship in self._fleet.ships)

    def get_fleet_pod_mass_used(self) -> float:
        """Get total mass of carried items across all ships in fleet."""
        return sum(ship._cargo_mgr.get_pod_storage_used() for ship in self._fleet.ships)

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
        for ship in self._fleet.ships:
            total += ship._cargo_mgr.get_cargo_capacity(cargo_type)
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
            total += ship._cargo_mgr.get_current_cargo(cargo_type)
        return total

    def _distribute_cargo_to_fleet(
        self,
        cargo_type: str,
        amount: int,
        ship_method: Callable[['ShipInstance', str, int], int],
    ) -> int:
        """Iterate ships, calling ``ship_method`` per ship until ``amount`` is exhausted.

        Shared skeleton for :meth:`load_cargo_to_fleet` and
        :meth:`unload_cargo_from_fleet` (PROJ-380, DUP-X-06).

        Args:
            cargo_type: Type of cargo to move.
            amount: Total amount to move; values <= 0 short-circuit to 0.
            ship_method: A callable ``(ship, cargo_type, remaining) -> moved``
                — typically a bound ``ship.load_cargo`` or ``ship.unload_cargo``.

        Returns:
            Actual amount moved (may be less than requested when ships are
            capacity-limited or out of cargo).
        """
        if amount <= 0:
            return 0

        remaining = amount
        total_moved = 0

        for ship in self._fleet.ships:
            if remaining <= 0:
                break
            moved = ship_method(ship, cargo_type, remaining)
            total_moved += moved
            remaining -= moved

        return total_moved

    def load_cargo_to_fleet(self, cargo_type: str, amount: int) -> int:
        """
        Load cargo to the fleet, distributing across ships with capacity.

        Args:
            cargo_type: Type of cargo to load
            amount: Total amount to load

        Returns:
            Actual amount loaded (may be less than requested if capacity limited).
        """
        return self._distribute_cargo_to_fleet(
            cargo_type, amount, lambda ship, t, a: ship._cargo_mgr.load_cargo(t, a)
        )

    def unload_cargo_from_fleet(self, cargo_type: str, amount: int) -> int:
        """
        Unload cargo from the fleet, collecting from ships.

        Args:
            cargo_type: Type of cargo to unload
            amount: Total amount to unload

        Returns:
            Actual amount unloaded (may be less than requested if not enough cargo).
        """
        return self._distribute_cargo_to_fleet(
            cargo_type, amount, lambda ship, t, a: ship._cargo_mgr.unload_cargo(t, a)
        )
