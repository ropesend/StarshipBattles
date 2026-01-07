import typing
from typing import Dict, List, Optional, Any, Union

class ResourceState:
    """
    Tracks the state of a single resource (e.g., 'fuel', 'energy').
    """
    def __init__(self, name: str, max_value: float = 0.0, current_value: float = 0.0, regen_rate: float = 0.0):
        self.name = name
        self.max_value = max_value
        self.current_value = current_value
        self.regen_rate = regen_rate # Units per second

    def consume(self, amount: float) -> bool:
        """
        Attempt to consume resource. Returns True if successful.
        """
        if self.current_value >= amount:
            self.current_value -= amount
            return True
        return False

    def check(self, amount: float) -> bool:
        """Check if enough resource is available without consuming."""
        return self.current_value >= amount

    def add(self, amount: float):
        """Add resource, clamping to max."""
        self.current_value = min(self.max_value, self.current_value + amount)
    
    def set_max(self, value: float):
        self.max_value = value
        # Clamp current if max reduced? Usually yes.
        if self.current_value > self.max_value:
            self.current_value = self.max_value
            
    def update(self):
        """Apply regeneration for one tick."""
        # Tick duration is fixed at 0.01 (100 ticks per second)
        TICK_DURATION = 0.01
        if self.regen_rate > 0 and self.current_value < self.max_value:
            self.current_value = min(self.max_value, self.current_value + (self.regen_rate * TICK_DURATION))

class ResourceRegistry:
    """
    Registry of all resources on a ship. 
    Acts as the Source of Truth for current resource state (fuel, energy, ammo).
    
    Responsibilities:
    - Tracking current vs max values.
    - Handling regeneration ticks (update).
    - Providing thread-safe(ish) consume/check methods.
    """
    def __init__(self):
        self._resources: Dict[str, ResourceState] = {}

    def get_resource(self, name: str) -> Optional[ResourceState]:
        return self._resources.get(name)

    def get_value(self, name: str) -> float:
        """Get current value of a resource, or 0.0 if not found."""
        res = self._resources.get(name)
        return res.current_value if res else 0.0

    def get_max_value(self, name: str) -> float:
        """Get max value of a resource, or 0.0 if not found."""
        res = self._resources.get(name)
        return res.max_value if res else 0.0

    def register_storage(self, name: str, amount: float):
        """
        Add storage capacity for a resource. Increase max_value.
        Note: Does not automatically fill current_value unless initialized implicitly elsewhere.
        """
        if name not in self._resources:
            self._resources[name] = ResourceState(name)
        
        # Increase max capacity
        res = self._resources[name]
        res.max_value += amount

    def register_generation(self, name: str, rate: float):
        """Add generation rate (units/sec) for a resource."""
        if name not in self._resources:
            self._resources[name] = ResourceState(name)
        
        self._resources[name].regen_rate += rate

    def reset_stats(self):
        """
        Reset max values and regeneration rates to 0 before a full stat recalculation.
        Current resource values are PERSISTED to maintain game state.
        """
        for res in self._resources.values():
            res.max_value = 0.0
            res.regen_rate = 0.0
            # Note: We DON'T reset current_value here, as that is the game state.

    def update(self):
        """Update all resources for one tick (apply regeneration)."""
        for res in self._resources.values():
            res.update()

    def set_value(self, name: str, value: float):
        """Set current value of a resource."""
        res = self._resources.get(name)
        if res:
            res.current_value = value
            # Ensure we don't exceed max if strict, but for init sometimes we want to overflow? 
            # Usually strict.
            if res.current_value > res.max_value:
                 res.current_value = res.max_value

    def modify_value(self, name: str, amount: float):
        """Modify current value of a resource by amount."""
        res = self._resources.get(name)
        if res:
            res.current_value += amount
            # Clamp to bounds
            if res.current_value > res.max_value:
                res.current_value = res.max_value
            elif res.current_value < 0:
                res.current_value = 0.0

    def set_max_value(self, name: str, value: float) -> None:
        """Helper for initializing max values directly."""
        res = self.get_resource(name)
        if not res:
            self.register_storage(name, value)
        else:
            res.max_value = value
            
    def set_regen_rate(self, name: str, value: float) -> None:
        """Helper for initializing regen rates directly."""
        res = self.get_resource(name)
        if res:
            res.regen_rate = value


# --- Ability System ---

# --- Ability System ---
# Forwarding to new module
from game.simulation.components.abilities import (
    Ability, 
    ResourceConsumption, 
    ResourceStorage, 
    ResourceGeneration, 
    ABILITY_REGISTRY, 
    create_ability
)
