"""
Tests for SpatialGrid.query_radius_exact() (PROJ-254 Phase 1).

Verifies that narrow-phase distance filtering eliminates false positives
from grid cell overlap in the broad-phase query.
"""
from game.engine.spatial import SpatialGrid
from game.core.math import Vector2


class _FakeEntity:
    """Minimal entity with position for spatial grid tests."""
    def __init__(self, x, y, name="entity"):
        self.position = Vector2(x, y)
        self.name = name

    def __repr__(self):
        return f"Entity({self.name}, {self.position.x}, {self.position.y})"


class TestQueryRadiusExact:
    """query_radius_exact should return only entities within exact distance."""

    def test_entity_within_radius_included(self):
        grid = SpatialGrid(cell_size=100)
        e = _FakeEntity(50, 50)
        grid.insert(e)
        result = grid.query_radius_exact(Vector2(0, 0), 200)
        assert e in result

    def test_entity_beyond_radius_excluded(self):
        grid = SpatialGrid(cell_size=100)
        e = _FakeEntity(300, 300)  # distance ~424, beyond 200
        grid.insert(e)
        result = grid.query_radius_exact(Vector2(0, 0), 200)
        assert e not in result

    def test_entity_at_exact_radius_included(self):
        grid = SpatialGrid(cell_size=100)
        e = _FakeEntity(200, 0)  # distance = 200, exactly at radius
        grid.insert(e)
        result = grid.query_radius_exact(Vector2(0, 0), 200)
        assert e in result

    def test_entity_in_adjacent_cell_beyond_radius_excluded(self):
        """Key test: entity in overlapping grid cell but beyond actual radius."""
        grid = SpatialGrid(cell_size=100)
        # Query at origin with radius 150. Cell steps = ceil(150/100) = 2.
        # So cells (-2,-2) to (2,2) are checked = 25 cells.
        # Place entity at (180, 180) = distance ~254, in cell (1,1) which IS checked.
        e = _FakeEntity(180, 180)
        grid.insert(e)

        # Broad-phase would include it (cell 1,1 is within 2 steps)
        broad = grid.query_radius(Vector2(0, 0), 150)
        assert e in broad

        # Narrow-phase should exclude it (distance 254 > 150)
        exact = grid.query_radius_exact(Vector2(0, 0), 150)
        assert e not in exact

    def test_empty_grid_returns_empty(self):
        grid = SpatialGrid(cell_size=100)
        result = grid.query_radius_exact(Vector2(0, 0), 500)
        assert result == []

    def test_multiple_entities_filtered_correctly(self):
        grid = SpatialGrid(cell_size=100)
        e_close = _FakeEntity(50, 50, "close")    # ~70 units
        e_mid = _FakeEntity(140, 0, "mid")          # 140 units
        e_far = _FakeEntity(300, 300, "far")        # ~424 units
        for e in [e_close, e_mid, e_far]:
            grid.insert(e)

        result = grid.query_radius_exact(Vector2(0, 0), 150)
        assert e_close in result
        assert e_mid in result
        assert e_far not in result
