"""
Physics Engine - 2D Space Physics Foundation

Provides PhysicsBody, the base class for all entities with physical
properties (position, velocity, rotation, mass).

Architecture Note — Two Physics Models:
    PhysicsBody serves TWO roles in the codebase:

    1. **Property container** (used by ALL subclasses):
       Position, velocity, angle, mass, forward_vector() — these are the
       shared spatial properties that Ship, Projectile, and any future
       entity type need.

    2. **Newtonian force-accumulation model** (apply_force + update):
       A complete physics model with drag, acceleration, and force
       integration. Currently NOT used by any subclass at runtime:
       - Ship uses ShipPhysicsMixin.update_physics_movement() which
         implements arcade-style physics (velocity always aligned with
         heading, thrust-based acceleration).
       - Projectile directly updates self.position += self.velocity
         without calling super().update().

       The force-accumulation model is retained and unit-tested as the
       base physics implementation. Subclasses override with their own
       physics appropriate to their entity type.

Coordinate System:
    - Origin: (0, 0) is the center of the battle space
    - X-axis: Positive X is RIGHT
    - Y-axis: Positive Y is DOWN (screen coordinates)
    - Angles: Measured in DEGREES, 0° = RIGHT (East)
              Positive rotation is clockwise
              90° = DOWN (South), 180° = LEFT (West), 270° = UP (North)
"""
from game.core.math import Vector2
from game.core.config import PhysicsConfig


class PhysicsBody:
    """Base class for all entities with physical presence in the game world.

    Provides shared spatial properties (position, velocity, angle, mass) and
    a default Newtonian physics model (apply_force/update). Subclasses may
    override the physics model while retaining the property container:

    - Ship: Uses ShipPhysicsMixin for arcade physics (velocity = heading * speed)
    - Projectile: Direct velocity integration (position += velocity per tick)
    """

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
