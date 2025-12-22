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
    
    def update_physics_movement(self, dt=1.0):
        """
        Update ship position and rotation based on cycle-based physics.
        dt is ignored/assumed to be 1 tick.
        """
        # Explicitly set velocity based on direction and speed (Arcade Style)
        forward = self.forward_vector()
        self.velocity = forward * self.current_speed
        self.position += self.velocity # Velocity is effectively pixels/tick
        
        # Apply Drag/Friction to Speed (Simple damping)
        # Drag is now a fixed percentage loss per tick
        # e.g. drag 0.05 = 5% speed loss per tick
        drag_factor = getattr(self, 'drag', 0.01) # Default small drag
        if drag_factor > 1: drag_factor = 1
        
        self.current_speed *= (1 - drag_factor)
        if self.current_speed < 0.001: self.current_speed = 0
        
        # Angular Update
        self.angle += self.angular_velocity # Angular velocity is degrees/tick
        self.angle %= 360
        self.angular_velocity = 0 # Reset each frame for direct control style if desired

    def thrust_forward(self, dt=1.0):
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
                            # 100 ticks = 1 second.
                            # Input Rate: X/sec -> X/100 per tick
                            fuel_cost += comp.fuel_cost_per_sec / 100.0
            
            if self.current_fuel >= fuel_cost:
                self.current_fuel -= fuel_cost
                
                # Apply Acceleration
                # Input Rate: accel_rate (pixels/sec^2? No, pixels/tick increment?)
                # Assuming accel_rate is derived from Thrust/Mass (pixels/sec^2)
                # We need to scale it to Per Tick.
                # If accel is pixels/sec/sec... 
                # speed += accel * dt ; pos += speed * dt
                # speed (pixels/sec) += accel (pixels/sec^2) * dt (sec)
                # Converted to ticks:
                # speed (pixels/tick) = speed(pixels/sec) / 100
                # accel (pixels/tick^2) = accel(pixels/sec^2) / 10000 ?
                # 
                # Let's assume acceleration_rate stored on ship is ALREADY scaled or 
                # we treat it as "Speed increment per tick". 
                # Physics model says: Accel = (Thrust * 2500) / Mass^2
                # If we assume that formula produces a "Per Second" acceleration...
                # We should divide by 100 to get "Per Tick speed increase".
                
                accel_per_tick = self.acceleration_rate / 100.0
                self.current_speed += accel_per_tick
                
                # Max Speed Check
                # Max Speed is typically pixels/sec. 
                # We need current_speed to be pixels/tick. 
                # So we compare current_speed to max_speed / 100.
                max_speed_per_tick = self.max_speed / 100.0
                
                if self.current_speed > max_speed_per_tick:
                    self.current_speed = max_speed_per_tick
            else:
                self.current_fuel = 0

    def rotate(self, dt, direction):
        """
        Rotate the ship.
        direction: -1 for left, 1 for right
        dt: ignored
        """
        # Direct angle modification (Arcade style)
        # Turn speed is degrees/sec. Convert to degrees/tick.
        turn_per_tick = self.turn_speed / 100.0
        self.angle += direction * turn_per_tick
