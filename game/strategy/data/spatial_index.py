"""
Grid-based spatial index for efficient neighbor queries.

Provides O(1) average case lookups for nearby systems instead of O(n) linear scan.
"""

from typing import List, Tuple, Optional, Any, Dict, Set
from collections import defaultdict
from game.core.hex_math import HexCoord, hex_distance


class SpatialIndex:
    """
    Grid-based spatial index for efficient neighbor queries.

    Divides space into cells of cell_size and maintains a mapping of
    cells to the objects they contain. Neighbor queries only check
    relevant cells rather than all objects.
    """

    def __init__(self, cell_size: int = 500):
        """
        Initialize spatial index.

        Args:
            cell_size: Size of each grid cell in hex units.
                       Larger cells = fewer cells but more objects per cell.
                       Smaller cells = more cells but faster queries.
        """
        self.cell_size = cell_size
        self._cells: Dict[Tuple[int, int], List[Tuple[HexCoord, Any]]] = defaultdict(list)

    def _get_cell_key(self, coord: HexCoord) -> Tuple[int, int]:
        """Convert a hex coordinate to its cell key."""
        # Use integer division to get cell coordinates
        cell_q = coord.q // self.cell_size
        cell_r = coord.r // self.cell_size
        return (cell_q, cell_r)

    def add(self, coord: HexCoord, data: Any) -> None:
        """
        Add an object to the spatial index.

        Args:
            coord: The hex coordinate of the object
            data: Any data associated with this location (e.g., system name)
        """
        cell_key = self._get_cell_key(coord)
        self._cells[cell_key].append((coord, data))

    def bulk_add(self, items: List[Tuple[HexCoord, Any]]) -> None:
        """
        Add multiple objects to the spatial index efficiently.

        Args:
            items: List of (coord, data) tuples to add
        """
        for coord, data in items:
            self.add(coord, data)

    def clear(self) -> None:
        """Remove all objects from the index."""
        self._cells.clear()

    def _get_nearby_cells(self, coord: HexCoord, radius: int) -> Set[Tuple[int, int]]:
        """Get all cell keys that could contain neighbors within radius."""
        # Calculate how many cells to check in each direction
        cells_to_check = (radius // self.cell_size) + 2

        center_key = self._get_cell_key(coord)
        nearby_cells = set()

        for dq in range(-cells_to_check, cells_to_check + 1):
            for dr in range(-cells_to_check, cells_to_check + 1):
                cell_key = (center_key[0] + dq, center_key[1] + dr)
                if cell_key in self._cells:
                    nearby_cells.add(cell_key)

        return nearby_cells

    def get_neighbors(
        self,
        coord: HexCoord,
        radius: int,
        exclude_coord: Optional[HexCoord] = None
    ) -> List[Tuple[HexCoord, Any]]:
        """
        Get all objects within radius of a coordinate.

        Args:
            coord: Center coordinate to search from
            radius: Maximum hex distance to include
            exclude_coord: Optional coordinate to exclude from results

        Returns:
            List of (coord, data) tuples for all neighbors within radius
        """
        neighbors = []
        nearby_cells = self._get_nearby_cells(coord, radius)

        for cell_key in nearby_cells:
            for obj_coord, obj_data in self._cells[cell_key]:
                if exclude_coord is not None and obj_coord == exclude_coord:
                    continue

                dist = hex_distance(coord, obj_coord)
                if dist <= radius:
                    neighbors.append((obj_coord, obj_data))

        return neighbors

    def get_k_nearest(
        self,
        coord: HexCoord,
        k: int,
        exclude_coord: Optional[HexCoord] = None,
        max_radius: Optional[int] = None,
    ) -> List[Tuple[HexCoord, Any]]:
        """
        Get the k nearest neighbors to a coordinate.

        Args:
            coord: Center coordinate to search from
            k: Number of nearest neighbors to return
            exclude_coord: Optional coordinate to exclude from results
            max_radius: Maximum search radius (default: search all populated cells)

        Returns:
            List of (coord, data) tuples for the k nearest neighbors,
            sorted by distance (closest first)
        """
        # When max_radius is None we visit every populated cell. The previous
        # iterative-expansion heuristic stopped once the candidate count
        # stopped changing, which is unsound in sparse indexes: empty cells
        # between the query point and the only neighbour leave the count at
        # zero and the search exits before reaching the populated cell.
        candidates: List[Tuple[int, HexCoord, Any]] = []

        if max_radius is None:
            cells_iter = self._cells.values()
        else:
            cells_iter = (
                self._cells[cell_key]
                for cell_key in self._get_nearby_cells(coord, max_radius)
            )

        for cell in cells_iter:
            for obj_coord, obj_data in cell:
                if exclude_coord is not None and obj_coord == exclude_coord:
                    continue
                dist = hex_distance(coord, obj_coord)
                if max_radius is not None and dist > max_radius:
                    continue
                candidates.append((dist, obj_coord, obj_data))

        candidates.sort(key=lambda x: x[0])
        return [(c[1], c[2]) for c in candidates[:k]]

    def has_neighbor_within_distance(
        self,
        coord: HexCoord,
        min_dist: int
    ) -> bool:
        """
        Check if there's any neighbor within a minimum distance.

        This is an optimized check for placement validation - it returns
        as soon as any neighbor is found within the distance.

        Args:
            coord: Coordinate to check from
            min_dist: Minimum distance threshold

        Returns:
            True if any neighbor exists within min_dist, False otherwise
        """
        nearby_cells = self._get_nearby_cells(coord, min_dist)

        for cell_key in nearby_cells:
            for obj_coord, _ in self._cells[cell_key]:
                dist = hex_distance(coord, obj_coord)
                if dist < min_dist:
                    return True

        return False
