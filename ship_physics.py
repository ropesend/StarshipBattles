import pygame
from physics import PhysicsBody
# Engine, Thruster imports removed - using ability-based checks (Phase 3)

class ShipPhysicsMixin:
    """
    Mixin class handling ship movement and physics.
    Requires the host class to inherit from PhysicsBody and have:
    - current_fuel, current_speed, max_speed, acceleration_rate, drag
    - angle, angular_velocity, turn_speed
    """
    
    def update_physics_movement(self):
        """
        """
        # Determine target speed based on input state
        if getattr(self, 'is_thrusting', False):
            # Calculate Dynamic Thrust based on OPERATIONAL engines (Phase 3: ability-based)
            current_total_thrust = self.get_total_ability_value('CombatPropulsion', operational_only=True)
            
            # Recalculate acceleration for this frame based on available thrust
            # Mass constant for now
            K_THRUST = 2500
            if self.mass > 0:
                current_accel = (current_total_thrust * K_THRUST) / (self.mass * self.mass)
                # Cap at max potential accel? Or just use it.
                # Just use it.
                # Update Max Speed potential too? 
                # If we have half engines, we have half top speed?
                # Physics says Force / Drag ~ Speed. 
                # self.max_speed is currently pre-calculated based on ALL engines.
                # We should scale target_speed?
                
                # Simple logic: target_speed is max_speed * throttle.
                # But if engines are down, we can't reach max_speed.
                # With less thrust, we just accelerate slower?
                # Arcade physics: max_speed is usually a limit, but if Force is lower, do we cap speed lower?
                # Formula: max_speed = (total_thrust * K_SPEED) / mass
                # Let's dynamically calculate this frame's max speed potential.
                K_SPEED = 25
                potential_max_speed = (current_total_thrust * K_SPEED) / self.mass
                
                # Apply Throttle
                target_v = potential_max_speed * getattr(self, 'engine_throttle', 1.0)
                
                # Override self.acceleration_rate temporarily for this update? 
                # Or just use the local current_accel
                step = current_accel
                
                # Logic copied from original but dynamic step/target
                diff = target_v - self.current_speed
                if diff != 0:
                     if abs(diff) <= step:
                         self.current_speed = target_v
                     else:
                         self.current_speed += step if diff > 0 else -step
            
        else:
            # Coasting / Decelerating
            # Drag? 
            self.target_speed = 0
            step = self.acceleration_rate # Use base accel as deceleration? Or Drag?
            # Original code used self.acceleration_rate for decel too.
            diff = 0 - self.current_speed
            if diff != 0:
                if abs(diff) <= step:
                    self.current_speed = 0
                else:
                    self.current_speed += step if diff > 0 else -step
            
        # Reset input flag for next frame
        self.is_thrusting = False
    
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
        """
        Apply thrust input. 
        Note: Actual fuel consumption happens in Ship.update -> Component.update.
        This simply flags the desire to move.
        """
        self.is_thrusting = True
        
    def rotate(self, direction):
        """
        Rotate the ship.
        direction: -1 for left, 1 for right
        """
        turn_per_tick = (self.turn_speed * getattr(self, 'turn_throttle', 1.0)) / 100.0
        self.angle += direction * turn_per_tick
        

