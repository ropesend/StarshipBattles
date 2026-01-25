"""
Physics Engine - 2D Space Physics Simulation

This module provides PhysicsBody, the base class for all entities with
physical properties (position, velocity, rotation).

Coordinate System:
    - Origin: (0, 0) is the center of the battle space
    - X-axis: Positive X is RIGHT
    - Y-axis: Positive Y is DOWN (screen coordinates)
    - Angles: Measured in DEGREES, 0° = RIGHT (East)
              Positive rotation is clockwise
              90° = DOWN (South), 180° = LEFT (West), 270° = UP (North)

Drag Model:
    Linear drag reduces velocity each tick:
        new_velocity = velocity * (1 - drag)

    Angular drag reduces rotation each tick:
        new_angular_velocity = angular_velocity * (1 - angular_drag)

    Default values from PhysicsConfig:
        - DEFAULT_LINEAR_DRAG: ~0.02 (2% velocity loss per tick)
        - DEFAULT_ANGULAR_DRAG: ~0.1 (10% rotation loss per tick)

Update Sequence (per tick):
    1. Apply accumulated acceleration to velocity
    2. Reset acceleration to zero
    3. Apply linear drag to velocity
    4. Apply angular drag to angular velocity
    5. Update position from velocity
    6. Update angle from angular velocity

Force Application:
    Forces are applied via apply_force(vector):
        acceleration += force / mass

    This allows multiple forces to accumulate within a tick before
    being integrated into velocity during update().

Note:
    Ship class extends PhysicsBody with additional cycle-based mechanics
    via ShipPhysicsMixin. The base update() is rarely called directly
    for ships - instead, their mixin's update handles the physics.

Example:
    body = PhysicsBody(x=100, y=200, angle=45)
    body.apply_force(Vector2(10, 0))  # Push right
    body.update()  # Integrate physics
"""
from game.core.math import Vector2
from game.core.config import PhysicsConfig


class PhysicsBody:
    def __init__(self, x, y, angle=0):
        self.position = Vector2(x, y)
        self.velocity = Vector2(0, 0)
        self.acceleration = Vector2(0, 0)
        self.angle = angle  # Degrees
        self.angular_velocity = 0  # Degrees per second
        self.mass = 1.0  # Default, will be overridden by ship stats
        self.drag = PhysicsConfig.DEFAULT_LINEAR_DRAG
        self.angular_drag = PhysicsConfig.DEFAULT_ANGULAR_DRAG

    @property
    def x(self):
        return self.position.x

    @x.setter
    def x(self, value):
        self.position.x = value

    @property
    def y(self):
        return self.position.y

    @y.setter
    def y(self, value):
        self.position.y = value

    def update(self, dt=1.0):
        """
        Update physics. dt is ignored (1 tick = fixed step).
        NOTE: Ship class overrides this with its own cycle-based mixins.
        This base implementation is here for non-ship PhysicsBody entities if any.
        """
        # Apply Acceleration (per tick)
        self.velocity += self.acceleration
        self.acceleration = Vector2(0, 0)  # Reset acceleration

        # Apply Drag (fixed percentage per tick)
        drag_factor = self.drag
        if drag_factor > 1:
            drag_factor = 1
        self.velocity *= (1 - drag_factor)
        self.angular_velocity *= (1 - self.angular_drag)

        # Apply Movement (per tick)
        self.position += self.velocity
        self.angle += self.angular_velocity

    def apply_force(self, force: Vector2):
        """Applies a force vector to the body."""
        if self.mass > 0:
            self.acceleration += force / self.mass

    def forward_vector(self):
        """Returns the forward directional vector based on angle."""
        # 0 degrees is RIGHT (1, 0) in standard math.
        vec = Vector2(1, 0)
        return vec.rotate(self.angle)
