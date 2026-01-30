from game.strategy.data.hex_math import HexCoord
from game.strategy.data.ship_instance import ShipInstance
from enum import Enum, auto
from typing import List, Optional, Tuple, TYPE_CHECKING, Any, Dict

if TYPE_CHECKING:
    from game.simulation.entities.ship import Ship


class OrderType(Enum):
    MOVE = auto()
    COLONIZE = auto()
    MOVE_TO_FLEET = auto()
    JOIN_FLEET = auto()


class FleetOrder:
    def __init__(self, order_type, target=None):
        self.type = order_type
        self.target = target  # HexCoord for MOVE, Planet for COLONIZE, Fleet for MOVE_TO_FLEET/JOIN_FLEET

    def __repr__(self):
        return f"FleetOrder({self.type.name}, {self.target})"

    def to_dict(self) -> Dict[str, Any]:
        """Serialize for save game."""
        target_data = None
        if self.target is not None:
            if hasattr(self.target, 'to_dict'):
                target_data = self.target.to_dict()
            elif hasattr(self.target, 'id'):
                # Fleet reference - store ID
                target_data = {'type': 'fleet_ref', 'id': self.target.id}
            elif isinstance(self.target, tuple):
                target_data = {'type': 'coord', 'value': list(self.target)}
            else:
                target_data = {'type': 'raw', 'value': str(self.target)}

        return {
            'type': self.type.name,
            'target': target_data,
        }


class Fleet:
    """
    Represents a fleet of ships on the Strategy Map.

    Ships are stored as ShipInstance objects with full state tracking.
    """

    def __init__(self, fleet_id, owner_id, location, speed=5.0):
        self.id = fleet_id
        self.owner_id = owner_id  # 0=Player, 1=Enemy, etc
        self.location = location  # HexCoord
        self.ships: List[ShipInstance] = []

        # Movement & Orders
        self.speed = float(speed)
        self.orders: List[FleetOrder] = []
        self.path: List[HexCoord] = []  # Current movement path for the ACTIVE Move order

    def add_ship(self, ship: ShipInstance):
        """Add a ShipInstance to the fleet."""
        self.ships.append(ship)
        self._trigger_speed_recalculation()

    def add_ship_instance(self, instance: ShipInstance):
        """Add a ShipInstance to the fleet."""
        self.ships.append(instance)
        self._trigger_speed_recalculation()

    def remove_ship(self, ship: ShipInstance) -> bool:
        """Remove a ship from the fleet. Returns True if found and removed."""
        if ship in self.ships:
            self.ships.remove(ship)
            self._trigger_speed_recalculation()
            return True
        return False

    def _trigger_speed_recalculation(self):
        """
        Trigger fleet speed recalculation based on current ship composition.

        Fleet speed is the minimum of all combat-capable ships' speeds,
        ensuring the fleet moves at the pace of its slowest member.
        """
        # INTENTIONAL LATE IMPORT: Edge operation (only on ship add/remove)
        # See docs/ARCHITECTURE.md "Intentional Late Imports" section
        from game.strategy.services.fleet_speed_calculator import FleetSpeedCalculator
        FleetSpeedCalculator.update_fleet_speed(self)

    def get_ship_names(self) -> List[str]:
        """Get names of all ships in the fleet."""
        return [s.name for s in self.ships]

    def get_combat_capable_ships(self) -> List[ShipInstance]:
        """Get ships capable of combat (not destroyed or derelict)."""
        return [s for s in self.ships if s.is_combat_capable()]

    def can_use_warp(self) -> bool:
        """
        Check if ALL ships in fleet can use warp points.

        A fleet can only use warp points if every combat-capable ship has
        a WarpJump ability with max_tonnage >= that ship's mass.

        Returns:
            True if all combat-capable ships are warp-capable, False otherwise.
            Returns False if fleet has no combat-capable ships.
        """
        # INTENTIONAL LATE IMPORT: Query operation, service encapsulates warp logic
        # See docs/ARCHITECTURE.md "Intentional Late Imports" section
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        combat_ships = self.get_combat_capable_ships()
        if not combat_ships:
            return False

        for ship in combat_ships:
            if not ShipStatsCalculator.has_warp_capability(ship):
                return False
        return True

    def get_warp_limiting_ship(self) -> Optional[ShipInstance]:
        """
        Get the ship that prevents the fleet from using warp, if any.

        Returns:
            The first ship without warp capability, or None if all ships are warp-capable.
        """
        # INTENTIONAL LATE IMPORT: Query operation, service encapsulates warp logic
        # See docs/ARCHITECTURE.md "Intentional Late Imports" section
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        for ship in self.get_combat_capable_ships():
            if not ShipStatsCalculator.has_warp_capability(ship):
                return ship
        return None

    # --- Fuel Consumption Methods ---

    def get_fuel_cost_per_hex(self) -> float:
        """
        Calculate total fleet fuel consumption per hex.

        Returns:
            Sum of all combat-capable ships' strategic fuel costs.
        """
        total = 0.0
        for ship in self.get_combat_capable_ships():
            total += ship.get_fuel_cost_per_hex()
        return total

    def has_fuel_for_movement(self) -> bool:
        """
        Check if fleet has fuel for at least one hex of movement.

        Returns:
            True if all combat-capable ships have enough fuel for one hex.
        """
        for ship in self.get_combat_capable_ships():
            cost = ship.get_fuel_cost_per_hex()
            if cost > 0:
                current = ship.get_current_fuel()
                if current < cost:
                    return False
        return True

    def consume_fleet_fuel(self, hexes: int = 1) -> bool:
        """
        Consume fuel from all ships for movement.

        Args:
            hexes: Number of hexes moved (default 1)

        Returns:
            True if all ships had sufficient fuel, False otherwise.
            Note: If False, no fuel is consumed (atomic operation).
        """
        ships = self.get_combat_capable_ships()

        # First, verify all ships have enough fuel
        for ship in ships:
            cost = ship.get_fuel_cost_per_hex() * hexes
            if cost > 0:
                current = ship.get_current_fuel()
                if current < cost:
                    return False

        # All ships have enough, now consume
        for ship in ships:
            cost = ship.get_fuel_cost_per_hex() * hexes
            if cost > 0:
                ship.consume_fuel(cost)

        return True

    # --- Generic Movement Resource Methods ---

    def get_movement_resource_costs(self) -> Dict[str, float]:
        """
        Get total fleet resource costs per hex of movement.

        Returns:
            Dict mapping resource type to total fleet cost per hex.
        """
        total_costs: Dict[str, float] = {}
        for ship in self.get_combat_capable_ships():
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
        for ship in self.get_combat_capable_ships():
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
        ships = self.get_combat_capable_ships()

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
        for ship in self.get_combat_capable_ships():
            ship_costs = ship.get_warp_resource_costs()
            for resource_type, cost in ship_costs.items():
                total_costs[resource_type] = total_costs.get(resource_type, 0) + cost
        return total_costs

    def get_warp_energy_cost(self) -> float:
        """
        Calculate total fleet energy cost for a warp jump.

        Returns:
            Sum of all combat-capable ships' warp energy costs.
        """
        total = 0.0
        for ship in self.get_combat_capable_ships():
            total += ship.get_warp_energy_cost()
        return total

    def get_warp_fuel_cost(self) -> float:
        """
        Calculate total fleet fuel cost for a warp jump.

        Returns:
            Sum of all combat-capable ships' warp fuel costs.
        """
        total = 0.0
        for ship in self.get_combat_capable_ships():
            total += ship.get_warp_fuel_cost()
        return total

    def has_resources_for_warp(self) -> bool:
        """
        Check if fleet has all required resources for a warp jump.

        This is data-driven - checks all resource types defined in warp costs.
        If no resource cost is specified, no resource check is performed.

        Returns:
            True if all combat-capable ships have enough resources for one warp.
        """
        for ship in self.get_combat_capable_ships():
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
        ships = self.get_combat_capable_ships()

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

        for ship in self.get_combat_capable_ships():
            cost_per_hex = ship.get_fuel_cost_per_hex()
            if cost_per_hex <= 0:
                continue  # This ship doesn't consume fuel

            current_fuel = ship.get_current_fuel()
            endurance = int(current_fuel / cost_per_hex) if cost_per_hex > 0 else float('inf')
            min_endurance = min(min_endurance, endurance)

        return int(min_endurance) if min_endurance != float('inf') else -1

    def warp_jumps_remaining(self) -> int:
        """
        Calculate how many warp jumps fleet can make.

        This is data-driven - considers both energy and fuel costs as
        specified by the warp drive components.

        Returns:
            Minimum jumps any ship can make based on resources.
            Returns 0 if fleet cannot use warp at all.
            Returns -1 if fleet has unlimited jumps (no resource cost).
        """
        if not self.can_use_warp():
            return 0

        min_jumps = float('inf')

        for ship in self.get_combat_capable_ships():
            # Check energy-limited jumps
            energy_cost = ship.get_warp_energy_cost()
            if energy_cost > 0:
                current_energy = ship.get_current_energy()
                energy_jumps = int(current_energy / energy_cost)
                min_jumps = min(min_jumps, energy_jumps)

            # Check fuel-limited jumps
            fuel_cost = ship.get_warp_fuel_cost()
            if fuel_cost > 0:
                current_fuel = ship.get_current_fuel()
                fuel_jumps = int(current_fuel / fuel_cost)
                min_jumps = min(min_jumps, fuel_jumps)

        return int(min_jumps) if min_jumps != float('inf') else -1

    def get_capability_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive fleet capability summary for UI.

        Returns:
            Dict with all fleet capability information.
        """
        return {
            'speed': self.speed,
            'can_warp': self.can_use_warp(),
            'warp_limiting_ship': self.get_warp_limiting_ship(),
            'fuel_endurance': self.fuel_endurance(),
            'warp_jumps': self.warp_jumps_remaining(),
            'fuel_cost_per_hex': self.get_fuel_cost_per_hex(),
            'warp_energy_cost': self.get_warp_energy_cost(),
            'warp_fuel_cost': self.get_warp_fuel_cost(),
        }

    def to_battle_ships(
        self,
        team_id: int,
        formation_positions: Optional[List[Tuple[float, float]]] = None
    ) -> List['Ship']:
        """
        Convert fleet ships to simulation Ship objects for battle.

        Only works with ShipInstance objects - legacy strings cannot be converted.

        Args:
            team_id: Team assignment for battle (0 or 1)
            formation_positions: Optional list of (x, y) positions for ships

        Returns:
            List of Ship objects ready for battle
        """
        ships = []

        if not self.ships:
            return []

        # Generate default positions if not provided
        if formation_positions is None:
            formation_positions = self._default_formation_positions(len(self.ships), team_id)

        for i, instance in enumerate(self.ships):
            if not instance.is_combat_capable():
                continue

            pos = formation_positions[i] if i < len(formation_positions) else (0, 0)
            ship = instance.to_ship(pos, team_id)
            ships.append(ship)

        return ships

    def _default_formation_positions(
        self,
        count: int,
        team_id: int
    ) -> List[Tuple[float, float]]:
        """Generate default formation positions for ships."""
        positions = []

        # Team 0 starts on the left, Team 1 on the right
        base_x = 20000 if team_id == 0 else 80000
        base_y = 50000

        # Simple line formation
        spacing = 2000

        for i in range(count):
            y = base_y + (i - count // 2) * spacing
            positions.append((base_x, y))

        return positions

    def update_from_battle_results(
        self,
        surviving_ships: List['Ship'],
    ) -> None:
        """
        Update fleet ships from battle results.

        Args:
            surviving_ships: Ships that survived the battle
        """
        # Build lookup for surviving ships by name
        survivors_by_name = {s.name: s for s in surviving_ships}

        # Update each ShipInstance - ships not in survivors were destroyed
        new_ships = []
        for s in self.ships:
            if s.name in survivors_by_name:
                # Update state from battle
                s.update_from_ship(survivors_by_name[s.name])
                new_ships.append(s)
            # else: ship was destroyed, don't include

        self.ships = new_ships

        # Recalculate speed (ships may have been destroyed or damaged)
        self._trigger_speed_recalculation()

    def add_order(self, order, index=None):
        """Add an order to the queue."""
        if index is None:
            self.orders.append(order)
        else:
            self.orders.insert(index, order)

    def clear_orders(self):
        self.orders.clear()
        self.path = []

    def get_current_order(self):
        if not self.orders:
            return None
        return self.orders[0]

    def pop_order(self):
        if self.orders:
            finished = self.orders.pop(0)
            self.path = []  # Clear path associated with that order
            return finished
        return None

    def merge_with(self, other_fleet: 'Fleet'):
        """
        Merge this fleet into other_fleet.
        Transfers all ships and clears this fleet.
        """
        if not isinstance(other_fleet, Fleet):
            return

        # Transfer ships
        other_fleet.ships.extend(self.ships)
        self.ships.clear()

        # Clear orders (this fleet is effectively gone)
        self.clear_orders()

        # Recalculate speed for the target fleet (new composition)
        other_fleet._trigger_speed_recalculation()

    def to_dict(self) -> Dict[str, Any]:
        """Serialize for save game."""
        ships_data = [s.to_dict() for s in self.ships]

        location_data = None
        if hasattr(self.location, 'to_dict'):
            location_data = self.location.to_dict()
        elif isinstance(self.location, tuple):
            location_data = list(self.location)

        return {
            'id': self.id,
            'owner_id': self.owner_id,
            'location': location_data,
            'speed': self.speed,
            'ships': ships_data,
            'orders': [o.to_dict() for o in self.orders],
            'path': [list(p) if isinstance(p, tuple) else p for p in self.path],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Fleet':
        """Deserialize from save game."""
        # ShipInstance imported at module level

        location = data.get('location')
        if isinstance(location, list):
            location = HexCoord(location[0], location[1])

        fleet = cls(
            fleet_id=data['id'],
            owner_id=data['owner_id'],
            location=location,
            speed=data.get('speed', 5.0),
        )

        # Restore ships
        for ship_data in data.get('ships', []):
            fleet.ships.append(ShipInstance.from_dict(ship_data))

        # Restore path
        for p in data.get('path', []):
            if isinstance(p, list):
                fleet.path.append(HexCoord(p[0], p[1]))
            else:
                fleet.path.append(p)

        # Restore orders
        # Note: Multiple formats supported for save file compatibility:
        # 1. {'q': x, 'r': y} - HexCoord.to_dict() format
        # 2. {'type': 'coord', 'value': [x, y]} - Tuple coordinate format
        # 3. {'type': 'fleet_ref', 'id': xxx} - Fleet reference for MOVE_TO_FLEET orders
        # 4. {'type': 'raw', 'value': str} - Fallback string representation
        # All formats are valid outputs from FleetOrder.to_dict() and must be preserved
        # for backward compatibility with existing save files. (PROJ-42)
        for order_data in data.get('orders', []):
            order_type = OrderType[order_data['type']]
            target = None

            target_data = order_data.get('target')
            if target_data is not None:
                if isinstance(target_data, dict):
                    if 'q' in target_data and 'r' in target_data:
                        # HexCoord.to_dict() format
                        target = HexCoord(target_data['q'], target_data['r'])
                    elif target_data.get('type') == 'coord':
                        # Tuple-style coord format
                        target = HexCoord(target_data['value'][0], target_data['value'][1])
                    elif target_data.get('type') == 'fleet_ref':
                        # Fleet reference - store ID for later resolution
                        target = {'_fleet_ref': target_data['id']}
                    elif target_data.get('type') == 'raw':
                        # Raw string fallback
                        target = target_data['value']

            fleet.orders.append(FleetOrder(order_type, target))

        return fleet

    def __repr__(self):
        ship_count = len(self.ships)
        return f"Fleet({self.id}, Owner:{self.owner_id}, Loc:{self.location}, Ships:{ship_count}, Spd:{self.speed})"

    def __eq__(self, other):
        if not isinstance(other, Fleet):
            return False
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)
