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
    
    def update_physics_movement(self):
        """
        Update ship position and rotation based on cycle-based physics.
        Target Speed Logic: Accelerate/Decelerate linearly to match target_speed.
        """
        # Determine target speed based on input state
        if getattr(self, 'is_thrusting', False):
            self.target_speed = self.max_speed
        else:
            self.target_speed = 0
            
        # Reset input flag for next frame
        self.is_thrusting = False
    
        # 1. Update Speed (Linear Acceleration/Deceleration)
        # We move current_speed towards target_speed by acceleration_rate
        
        diff = self.target_speed - self.current_speed
        
        if diff != 0:
            # Determine step size (Acceleration rate)
            # Both accel and decel use the same rate as requested
            step = self.acceleration_rate
            
            if abs(diff) <= step:
                self.current_speed = self.target_speed
            else:
                self.current_speed += step if diff > 0 else -step
        
        # 2. Update Position
        # Velocity matches heading * speed (No drift, Arcade style)
        forward = self.forward_vector()
        self.velocity = forward * self.current_speed
        self.position += self.velocity
        
        # 3. Angular Update
        self.angle += self.angular_velocity
        self.angle %= 360
        self.angular_velocity = 0

    def thrust_forward(self):
        """Apply thrust logic: Consume fuel and set thrusting flag."""
        # Cost depends on Engines
        fuel_cost = 0
        if hasattr(self, 'layers'):
            for layer in self.layers.values():
                for comp in layer['components']:
                    if isinstance(comp, Engine) and comp.is_active:
                         fuel_cost += comp.fuel_cost_per_sec / 100.0
        
        # Only thrust if we have fuel
        if self.current_fuel >= fuel_cost:
            self.current_fuel -= fuel_cost
            self.is_thrusting = True
        else:
            self.current_fuel = 0
            self.is_thrusting = False

    def rotate(self, direction):
        """
        Rotate the ship.
        direction: -1 for left, 1 for right
        """
        turn_per_tick = (self.turn_speed * getattr(self, 'turn_throttle', 1.0)) / 100.0
        self.angle += direction * turn_per_tick
