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

# --- Ability System ---

class Ability:
    """
    Base class for component abilities.
    Abilities represent functional capabilities (Consumption, Storage, Generation, special effects)
    that are data-driven and attached to Components.
    """
    def __init__(self, component, data: Dict[str, Any]):
        self.component = component
        self.data = data
    
    def update(self) -> bool:
        """
        Called every tick (0.01s). 
        Used for constant resource consumption or continuous effects.
        Returns True if operational, False if failed (e.g. starvation).
        """
        pass
        return True

    def on_activation(self) -> bool:
        """
        Called when component tries to activate (e.g. fire weapon). 
        Used for checking activation costs or conditions.
        Returns True if allowed.
        """
        return True

class ResourceConsumption(Ability):
    """
    Ability to consume resources.
    Data: { "resource": "fuel", "amount": 10, "trigger": "constant"|"activation" }
    """
    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)
        self.resource_name = data.get('resource', '')
        self.amount = data.get('amount', 0.0)
        self.trigger = data.get('trigger', 'constant') # 'constant' or 'activation'

    def update(self) -> bool:
        TICK_DURATION = 0.01  # Fixed tick duration
        if self.trigger == 'constant':
            # Need access to ship's resources
            if self.component.ship and self.component.ship.resources:
                res = self.component.ship.resources.get_resource(self.resource_name)
                if res:
                    # Constant consumption is per second, multiply by tick duration
                    cost = self.amount * TICK_DURATION
                    if not res.consume(cost):
                        # Starvation!
                        return False
                else:
                    if self.amount > 0: return False
        return True
                    
    def check_and_consume(self) -> bool:
        """Explicitly call for one-shot consumption checks."""
        if self.component.ship and self.component.ship.resources:
            res = self.component.ship.resources.get_resource(self.resource_name)
            if res:
                return res.consume(self.amount)
            else:
                return self.amount <= 0
        return False
        
    def check_available(self) -> bool:
        if self.component.ship and self.component.ship.resources:
            res = self.component.ship.resources.get_resource(self.resource_name)
            if res:
               return res.check(self.amount)
            else:
               return self.amount <= 0
        return False

class ResourceStorage(Ability):
    """
    Ability to store resources.
    Data: { "resource": "fuel", "amount": 100 }
    """
    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)
        self.resource_type = data.get('resource', '')
        self.max_amount = data.get('amount', 0.0)
        
    # Note: Logic for registering this is handled in ShipStatsCalculator / Component.recalculate
    # This class mainly serves as a data holder in this implementation phase, 
    # unless we move registration logic to 'on_equip' style events.

class ResourceGeneration(Ability):
    """
    Ability to generate resources.
    Data: { "resource": "energy", "amount": 10 }
    """
    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)
        self.resource_type = data.get('resource', '')
        self.rate = data.get('amount', 0.0)

ABILITY_REGISTRY = {
    "ResourceConsumption": ResourceConsumption,
    "ResourceStorage": ResourceStorage,
    "ResourceGeneration": ResourceGeneration,
    "EnergyGeneration": lambda c, d: ResourceGeneration(c, {"resource": "energy", "amount": d} if isinstance(d, (int, float)) else {**d, "resource": "energy"}),
    "FuelStorage": lambda c, d: ResourceStorage(c, {"resource": "fuel", "amount": d} if isinstance(d, (int, float)) else {**d, "resource": "fuel"}),
    "EnergyStorage": lambda c, d: ResourceStorage(c, {"resource": "energy", "amount": d} if isinstance(d, (int, float)) else {**d, "resource": "energy"}),
    "AmmoStorage": lambda c, d: ResourceStorage(c, {"resource": "ammo", "amount": d} if isinstance(d, (int, float)) else {**d, "resource": "ammo"}),
    "EnergyConsumption": lambda c, d: ResourceConsumption(c, {"resource": "energy", "amount": d, "trigger": "conditional"} if isinstance(d, (int, float)) else {**d, "resource": "energy"})
}

def create_ability(name: str, component, data: Dict[str, Any]) -> Optional[Ability]:
    if name in ABILITY_REGISTRY:
        return ABILITY_REGISTRY[name](component, data)
    return None
