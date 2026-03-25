from game.engine.physics import PhysicsBody
from game.simulation.physics_constants import compute_acceleration, compute_max_speed


class ShipPhysicsMixin:
    """
    Mixin class handling ship movement and physics.
    Requires the host class to inherit from PhysicsBody and have:
    - current_fuel, current_speed, max_speed, acceleration_rate, drag
    - angle, angular_velocity, turn_speed
    """
    
    def update_physics_movement(self) -> None:
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
        # is_thrusting and engine_throttle initialized in Ship.__init__
        if self.is_thrusting:
            current_total_thrust = self.get_total_ability_value('CombatPropulsion', operational_only=True)

            if self.mass > 0:
                current_accel = compute_acceleration(current_total_thrust, self.mass)
                potential_max_speed = compute_max_speed(current_total_thrust, self.mass)
                target_v = potential_max_speed * self.engine_throttle
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

    def thrust_forward(self) -> None:
        """
        Apply thrust input.
        Note: Actual fuel consumption happens in Ship.update -> Component.update.
        This simply flags the desire to move.
        """
        self.is_thrusting = True

    def rotate(self, direction: int) -> None:
        """
        Rotate the ship.

        Args:
            direction: -1 for left (counter-clockwise), 1 for right (clockwise)
        """
        # turn_throttle initialized in Ship.__init__
        turn_per_tick = (self.turn_speed * self.turn_throttle) / 100.0
        self.angle += direction * turn_per_tick
        

