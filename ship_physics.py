import pygame
from physics import PhysicsBody
from components import Engine, Thruster

class ShipPhysicsMixin:
    """
    Mixin class handling ship movement and physics.
    Requires the host class to inherit from PhysicsBody and have:
    - current_fuel, current_speed, max_speed, acceleration_rate, drag
    - angle, angular_velocity, turn_speed
    """
    
    def update_physics_movement(self, dt):
        """
        Update ship position and rotation based on arcade physics.
        This handles:
        1. Velocity calculation based on forward vector and current_speed
        2. Damping/Drag
        3. Angular updates
        """
        # Explicitly set velocity based on direction and speed (Arcade Style)
        forward = self.forward_vector()
        self.velocity = forward * self.current_speed
        self.position += self.velocity * dt
        
        # Apply Drag/Friction to Speed (Simple damping)
        # Note: We assume dt is around 1/60 usually, but we scale for it.
        # Ensure we don't flip speed direction if dt is huge
        drag_factor = self.drag * dt / 60.0
        if drag_factor > 1: drag_factor = 1
        
        self.current_speed *= (1 - drag_factor)
        if self.current_speed < 0.1: self.current_speed = 0
        
        # Angular Update
        # Note: self.angular_velocity might be set by rotate(), or we just use turn_speed directly in rotate?
        # In Ship.rotate(), we added to angle directly? No, Ship.rotate updated angle.
        # PhysicsBody.update() usually integrates angular_velocity.
        # Let's align with the existing logic:
        # self.angle += self.angular_velocity * dt
        
        # Wait, if we inherit from PhysicsBody, it has simple integration.
        # But `Ship.update` was overriding it.
        # Let's keep the override logic here.
        # But we must be careful not to double-integrate if we call super().update()!
        # The Ship class will likely delegate to this INSTEAD of super().update() for movement.
        
        # Angular integration
        self.angle += self.angular_velocity * dt
        self.angle %= 360
        self.angular_velocity = 0 # Reset each frame for direct control style if desired

    def thrust_forward(self, dt):
        """Apply thrust, consuming fuel and increasing speed."""
        if self.current_fuel > 0:
            # Consume Fuel
            fuel_cost = 0
            
            # Calculate cost from active engines
            # We assume self.layers exists
            if hasattr(self, 'layers'):
                for layer in self.layers.values():
                    for comp in layer['components']:
                        if isinstance(comp, Engine) and comp.is_active:
                            fuel_cost += comp.fuel_cost_per_sec * dt / 60.0
            
            if self.current_fuel >= fuel_cost:
                self.current_fuel -= fuel_cost
                
                # Apply Acceleration
                self.current_speed += self.acceleration_rate * dt
                # Hard cap
                if self.current_speed > self.max_speed:
                    self.current_speed = self.max_speed
            else:
                self.current_fuel = 0

    def rotate(self, dt, direction):
        """
        Rotate the ship.
        direction: -1 for left, 1 for right
        """
        # Direct angle modification (Arcade style)
        self.angle += direction * self.turn_speed * dt
