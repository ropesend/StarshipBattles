"""
Spatial Grid - Efficient spatial partitioning for proximity queries.

Used by the physics/combat system for fast neighbor lookups during
collision detection and target acquisition.
"""
import math
from typing import Any, Dict, List, Tuple

from game.core.config import PhysicsConfig


class SpatialGrid:
    """Grid-based spatial partitioning for efficient proximity queries."""

    def __init__(self, cell_size: float = PhysicsConfig.SPATIAL_GRID_CELL_SIZE) -> None:
        self.cell_size: float = cell_size
        self.buckets: Dict[Tuple[int, int], List[Any]] = {}

    def clear(self) -> None:
        """Clear all objects from the grid."""
        self.buckets = {}

    def _get_cell(self, pos: Any) -> Tuple[int, int]:
        """Get the cell coordinates for a position."""
        return (int(pos.x // self.cell_size), int(pos.y // self.cell_size))

    def insert(self, obj: Any) -> None:
        """Insert an object into the grid based on its position."""
        cell = self._get_cell(obj.position)
        if cell not in self.buckets:
            self.buckets[cell] = []
        self.buckets[cell].append(obj)

    def query_radius(self, pos: Any, radius: float) -> List[Any]:
        """Returns a list of objects in cells overlapping the circle."""
        cx, cy = self._get_cell(pos)
        # Determine range of cells to check
        steps = int(math.ceil(radius / self.cell_size))

        candidates: List[Any] = []
        for x in range(cx - steps, cx + steps + 1):
            for y in range(cy - steps, cy + steps + 1):
                cell = (x, y)
                if cell in self.buckets:
                    candidates.extend(self.buckets[cell])
        return candidates
