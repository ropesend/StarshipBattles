"""
Engine package for Starship Battles.

Provides low-level physics simulation, collision detection, and spatial indexing.

Public API
==========

Physics (game.engine.physics):
    PhysicsBody - Base class for physical entities with position, velocity, rotation

Collision (game.engine.collision):
    CollisionSystem - Handles hit detection, raycasting, and ramming

Spatial (game.engine.spatial):
    SpatialGrid - Spatial hash grid for efficient proximity queries
"""

# Physics
from game.engine.physics import PhysicsBody

# Collision
from game.engine.collision import CollisionSystem

# Spatial indexing
from game.engine.spatial import SpatialGrid


__all__ = [
    # Physics
    'PhysicsBody',
    # Collision
    'CollisionSystem',
    # Spatial
    'SpatialGrid',
]
