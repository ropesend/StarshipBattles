import math

from game.core.config import PhysicsConfig


class SpatialGrid:
    def __init__(self, cell_size=PhysicsConfig.SPATIAL_GRID_CELL_SIZE):
        self.cell_size = cell_size
        self.buckets = {}
        
    def clear(self):
        self.buckets = {}
        
    def _get_cell(self, pos):
        return (int(pos.x // self.cell_size), int(pos.y // self.cell_size))
        
    def insert(self, obj):
        cell = self._get_cell(obj.position)
        if cell not in self.buckets:
            self.buckets[cell] = []
        self.buckets[cell].append(obj)
        
    def query_radius(self, pos, radius):
        """Returns a list of objects in cells overlapping the circle."""
        cx, cy = self._get_cell(pos)
        # Determine range of cells to check
        steps = int(math.ceil(radius / self.cell_size))
        
        candidates = []
        for x in range(cx - steps, cx + steps + 1):
            for y in range(cy - steps, cy + steps + 1):
                cell = (x, y)
                if cell in self.buckets:
                    candidates.extend(self.buckets[cell])
        return candidates
