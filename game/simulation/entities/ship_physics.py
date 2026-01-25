from game.engine.physics import PhysicsBody
from game.simulation.physics_constants import K_SPEED, K_THRUST


class ShipPhysicsMixin:
    """
    Mixin class handling ship movement and physics.
    Requires the host class to inherit from PhysicsBody and have:
    - current_fuel, current_speed, max_speed, acceleration_rate, drag
    - angle, angular_velocity, turn_speed
    """
    
    def update_physics_movement(self):
        """
        Update ship physics for one tick.

        When thrusting:
        - Calculates dynamic thrust from operational engines only
        - Derives acceleration: (thrust * K_THRUST) / mass^2
        - Derives max speed: (thrust * K_SPEED) / mass
        - Applies throttle to determine target speed

        When coasting:
        - Decelerates using base acceleration_rate until stopped

        Uses arcade-style physics: velocity always matches heading direction.
        """
        if getattr(self, 'is_thrusting', False):
            current_total_thrust = self.get_total_ability_value('CombatPropulsion', operational_only=True)

            if self.mass > 0:
                current_accel = (current_total_thrust * K_THRUST) / (self.mass * self.mass)
                potential_max_speed = (current_total_thrust * K_SPEED) / self.mass
                target_v = potential_max_speed * getattr(self, 'engine_throttle', 1.0)
                step = current_accel

                diff = target_v - self.current_speed
                if diff != 0:
                     if abs(diff) <= step:
                         self.current_speed = target_v
                     else:
                         self.current_speed += step if diff > 0 else -step
            
        else:
            # Decelerate toward zero using base acceleration rate
            self.target_speed = 0
            step = self.acceleration_rate
            diff = 0 - self.current_speed
            if diff != 0:
                if abs(diff) <= step:
                    self.current_speed = 0
                else:
                    self.current_speed += step if diff > 0 else -step

        self.is_thrusting = False

        # Update position based on current speed and heading
        forward = self.forward_vector()
        self.velocity = forward * self.current_speed
        self.position += self.velocity

        # Update rotation
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
        

