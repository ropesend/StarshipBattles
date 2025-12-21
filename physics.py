import pygame

class Vector2(pygame.math.Vector2):
    """
    Wrapper around pygame.math.Vector2 to ensure we have it if needed, 
    but mostly we will use pygame.math.Vector2 directly.
    """
    pass

class PhysicsBody:
    def __init__(self, x, y, angle=0):
        self.position = pygame.math.Vector2(x, y)
        self.velocity = pygame.math.Vector2(0, 0)
        self.acceleration = pygame.math.Vector2(0, 0)
        self.angle = angle  # Degrees
        self.angular_velocity = 0  # Degrees per second
        self.mass = 1.0  # Default, will be overridden by ship stats
        self.drag = 0.5  # Linear drag to prevent infinite drift stability issues
        self.angular_drag = 0.5

    def update(self, dt):
        # Apply Acceleration
        self.velocity += self.acceleration * dt
        self.acceleration = pygame.math.Vector2(0, 0) # Reset acceleration

        # Apply Drag
        self.velocity *= (1 - self.drag * dt)
        self.angular_velocity *= (1 - self.angular_drag * dt)
        
        # Apply Movement
        self.position += self.velocity * dt
        self.angle += self.angular_velocity * dt

    def apply_force(self, force: pygame.math.Vector2):
        """Applies a force vector to the body."""
        if self.mass > 0:
            self.acceleration += force / self.mass

    def forward_vector(self):
        """Returns the forward directional vector based on angle."""
        # Pygame Vector2.rotate rotates counter-clockwise.
        # Assuming 0 degrees is UP (0, -1) or RIGHT (1, 0)?
        # Let's standardize: 0 degrees is RIGHT (1, 0) in standard math,
        # but in games often UP. Let's stick to standard math: 0 = Right, 90 = Down (screen coords)
        # Actually, for top down space shooter, usually 0 is UP or RIGHT.
        # Let's say 0 is RIGHT (1, 0).
        vec = pygame.math.Vector2(1, 0)
        return vec.rotate(self.angle)
