"""
Fleet movement simulation for the strategy layer.
Provides a single source of truth for fleet movement logic.
"""
from dataclasses import dataclass, field
from typing import Optional

from game.strategy.data.hex_math import HexCoord, hex_distance
from game.strategy.data.fleet import Fleet, FleetOrder, OrderType
from game.core.logger import log_warning


@dataclass
class FleetState:
    """
    Immutable snapshot of fleet movement state for simulation.
    Used for projecting movement without modifying actual fleet.
    """
    location: HexCoord
    path: list  # list[HexCoord]
    orders: list  # list[FleetOrder]
    speed: float
    
    @classmethod
    def from_fleet(cls, fleet: Fleet) -> 'FleetState':
        """Create a FleetState snapshot from an actual Fleet."""
        return cls(
            location=fleet.location,
            path=list(fleet.path),  # Copy to avoid mutation
            orders=list(fleet.orders),  # Copy to avoid mutation
            speed=fleet.speed
        )


@dataclass 
class PathSegment:
    """Represents one step in a projected path."""
    start: HexCoord
    end: HexCoord
    turn: int
    is_warp: bool
    
    @property
    def hex(self) -> HexCoord:
        """Alias for end, for backward compatibility."""
        return self.end
    
    def to_dict(self) -> dict:
        """Convert to dict for backward compatibility with existing code."""
        return {
            'start': self.start,
            'end': self.end,
            'hex': self.end,
            'turn': self.turn,
            'is_warp': self.is_warp
        }


class FleetMovementSimulator:
    """
    Stateless fleet movement simulation.
    
    Provides a single source of truth for movement logic used by both
    the TurnEngine (actual movement) and path projection (UI visualization).
    """
    
    def calculate_destination(self, state: FleetState, order: FleetOrder, galaxy) -> Optional[HexCoord]:
        """
        Determine the destination hex for a given order.
        
        Args:
            state: Current fleet state
            order: The order to process
            galaxy: Galaxy object for pathfinding context
            
        Returns:
            HexCoord destination or None if order has no movement component
        """
        if order.type == OrderType.MOVE:
            return order.target
        elif order.type == OrderType.MOVE_TO_FLEET:
            target_fleet = order.target
            if not target_fleet or not hasattr(target_fleet, 'location'):
                return None
            # For intercept, we need the pathfinding module
            from game.strategy.data.pathfinding import calculate_intercept_point
            return calculate_intercept_point(
                # Create a minimal fleet-like object for the chaser
                type('Fleet', (), {'location': state.location, 'speed': state.speed, 'id': -1})(),
                target_fleet, 
                galaxy
            )
        else:
            # COLONIZE, JOIN_FLEET etc. have no movement component
            return None
    
    def calculate_path(self, state: FleetState, destination: HexCoord, galaxy) -> list:
        """
        Calculate path from current location to destination.
        
        Args:
            state: Current fleet state
            destination: Target hex
            galaxy: Galaxy object for pathfinding
            
        Returns:
            List of HexCoords representing the path (excluding start if it matches location)
        """
        from game.strategy.data.pathfinding import find_hybrid_path
        
        if state.location == destination:
            return []
            
        path = find_hybrid_path(galaxy, state.location, destination)
        
        # Remove start hex if it matches current location
        if path and path[0] == state.location:
            path = path[1:]
            
        return path if path else []
    
    def calculate_next_step(self, state: FleetState, galaxy) -> tuple[Optional[HexCoord], FleetState]:
        """
        Calculate the next hex for movement without mutating the input state.
        
        This is a pure function: given a state, it returns the next hex to move to
        and a new state reflecting that movement.
        
        Args:
            state: Current fleet state (immutable)
            galaxy: Galaxy object for pathfinding
            
        Returns:
            Tuple of (next_hex or None, new_state)
            - next_hex is None if no movement should occur
            - new_state is a copy with updated path/orders
        """
        if not state.orders:
            return None, state
            
        order = state.orders[0]
        destination = self.calculate_destination(state, order, galaxy)
        
        if destination is None:
            # Non-movement order, skip it
            new_orders = state.orders[1:]
            return None, FleetState(
                location=state.location,
                path=[],
                orders=new_orders,
                speed=state.speed
            )
        
        # Check if we need to recalculate path (destination changed)
        current_path = state.path
        if current_path:
            current_dest = current_path[-1]
            if current_dest != destination:
                current_path = []  # Force recalc
        
        # Calculate path if needed
        if not current_path:
            if state.location == destination:
                # Already at destination, complete order
                new_orders = state.orders[1:]
                return None, FleetState(
                    location=state.location,
                    path=[],
                    orders=new_orders,
                    speed=state.speed
                )
            
            current_path = self.calculate_path(state, destination, galaxy)
            
            if not current_path:
                # No path found, cannot move
                return None, state
        
        # Pop next hex from path
        if current_path:
            next_hex = current_path[0]
            remaining_path = current_path[1:]
            
            # Check if order completes after this move
            if not remaining_path:
                new_orders = state.orders[1:]
            else:
                new_orders = state.orders
            
            new_state = FleetState(
                location=next_hex,
                path=remaining_path,
                orders=new_orders,
                speed=state.speed
            )
            return next_hex, new_state
        
        return None, state
    
    def project_path(self, fleet: Fleet, galaxy, max_turns: int = 10) -> list[PathSegment]:
        """
        Project fleet movement over multiple turns.
        
        Simulates future movement based on current orders and speed,
        returning a list of path segments for UI visualization.
        
        Args:
            fleet: The fleet to project
            galaxy: Galaxy object for pathfinding
            max_turns: Maximum turns to project
            
        Returns:
            List of PathSegment objects
        """
        segments = []
        state = FleetState.from_fleet(fleet)
        
        moves_per_turn = int(state.speed)
        if moves_per_turn <= 0:
            return segments
            
        moves_left_in_turn = moves_per_turn
        current_turn = 0
        
        # Safety limit
        max_steps = max_turns * moves_per_turn + 100
        iterations = 0
        
        while (state.path or state.orders) and current_turn < max_turns:
            iterations += 1
            if iterations > max_steps:
                log_warning("project_path exceeded max iterations")
                break
            
            # If no path but have orders, generate path for current order
            if not state.path and state.orders:
                order = state.orders[0]
                
                if order.type not in (OrderType.MOVE, OrderType.MOVE_TO_FLEET):
                    # Skip non-movement orders
                    state = FleetState(
                        location=state.location,
                        path=[],
                        orders=state.orders[1:],
                        speed=state.speed
                    )
                    continue
                
                destination = self.calculate_destination(state, order, galaxy)
                if destination is None:
                    break
                    
                new_path = self.calculate_path(state, destination, galaxy)
                if not new_path:
                    break
                    
                state = FleetState(
                    location=state.location,
                    path=new_path,
                    orders=state.orders,
                    speed=state.speed
                )
            
            if not state.path:
                break
            
            # Execute one step
            start_hex = state.location
            next_hex = state.path[0]
            remaining_path = state.path[1:]
            
            # Detect warp jump (distance > 1)
            is_warp = hex_distance(start_hex, next_hex) > 1
            
            segment = PathSegment(
                start=start_hex,
                end=next_hex,
                turn=current_turn,
                is_warp=is_warp
            )
            segments.append(segment)
            
            # Update state
            if not remaining_path:
                # Order complete
                new_orders = state.orders[1:] if state.orders else []
            else:
                new_orders = state.orders
                
            state = FleetState(
                location=next_hex,
                path=remaining_path,
                orders=new_orders,
                speed=state.speed
            )
            
            # Movement cost
            moves_left_in_turn -= 1
            if moves_left_in_turn <= 0:
                current_turn += 1
                moves_left_in_turn = moves_per_turn
        
        return segments
    
    def project_path_as_dicts(self, fleet: Fleet, galaxy, max_turns: int = 10) -> list[dict]:
        """
        Project fleet path and return as list of dicts for backward compatibility.
        
        This is a wrapper around project_path() that converts PathSegments to dicts.
        """
        segments = self.project_path(fleet, galaxy, max_turns)
        return [seg.to_dict() for seg in segments]
