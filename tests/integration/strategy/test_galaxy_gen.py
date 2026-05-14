import pytest
import random
from game.core.hex_math import HexCoord, hex_distance
from game.strategy.data.galaxy import Galaxy
from game.strategy.data.star_system import StarSystem, WarpPoint
from game.strategy.generation.placement_strategies import (
    RandomPlacementStrategy,
    DensityBasedPlacementStrategy,
)
from game.strategy.generation.density.density_map import DensityMap
from game.strategy.generation.density.primitives.radial import RadialPrimitive


def _bfs_visited_names(galaxy: Galaxy) -> set[str]:
    """BFS over warp graph from an arbitrary system; returns set of visited
    system names. Empty set when galaxy has no systems.

    PROJ-323 Task 5.6: extracted from test_graph_connectivity.
    """
    if not galaxy.systems:
        return set()
    start_node = next(iter(galaxy.systems.values()))
    visited = {start_node.name}
    queue = [start_node]
    while queue:
        current = queue.pop(0)
        for wp in current.warp_points:
            # O(N) lookup for target obj, irrelevant for test size
            target = next(
                (s for s in galaxy.systems.values() if s.name == wp.destination_id),
                None,
            )
            if target and target.name not in visited:
                visited.add(target.name)
                queue.append(target)
    return visited

class TestGalaxyGen:
    def test_galaxy_init(self):
        g = Galaxy(radius=1000)
        assert g.radius == 1000
        assert len(g.systems) == 0

    def test_add_system(self):
        g = Galaxy(radius=100)
        coord = HexCoord(0, 0)
        sys = StarSystem(name="Sol", global_location=coord)
        g.add_system(sys)
        assert len(g.systems) == 1
        assert g.systems[coord] == sys

    def test_generation_constraints_min_distance(self):
        """Verify that generated systems obey the minimum distance rule."""
        g = Galaxy(radius=2000)
        # Try to generate 5 systems with min distance 101
        # Use a fixed seed in implementation if possible, or just checks
        systems = g.generate_systems(count=5, min_dist=101)
        
        assert len(systems) == 5
        assert len(g.systems) == 5
        
        # Check all pairs
        coords = list(g.systems.keys())
        for i in range(len(coords)):
            for j in range(i + 1, len(coords)):
                d = hex_distance(coords[i], coords[j])
                assert d >= 101, f"Systems at {coords[i]} and {coords[j]} are too close: {d}"

    def test_warp_point_linking(self):
        """Verify warp points capture target direction."""
        g = Galaxy(radius=1000)
        
        # Manually place two systems
        s1 = StarSystem("Alpha", HexCoord(0, 0))
        s2 = StarSystem("Beta", HexCoord(100, 0)) # East direction
        g.add_system(s1)
        g.add_system(s2)
        
        # Link them
        g.create_vars_link(s1, s2)
        
        # Check s1 has warp to s2
        assert len(s1.warp_points) == 1
        wp = s1.warp_points[0]
        assert wp.destination_id == "Beta"
        
        # Check orientation 
        # s2 is East of s1 (positive q, r=0)
        # Warp point should be on the East edge of s1's local grid
        assert isinstance(wp.location, HexCoord)
        # Check rough direction: q should be positive, r near 0?
        # WARP_DIST is 30 hexes approx.
        assert wp.location.q > 0 
        assert abs(wp.location.r) < 10 # Should be somewhat aligned east

    def test_graph_connectivity(self):
        """Verify that the generated galaxy is fully connected (no isolated islands)."""
        g = Galaxy(radius=1000)
        g.generate_systems(count=20, min_dist=50)
        g.generate_warp_lanes()

        visited = _bfs_visited_names(g)

        assert len(visited) == len(g.systems), f"Graph not connected! Visited {len(visited)}/{len(g.systems)}"

    def test_minimum_warp_points(self):
        """Verify every star has at least 1 warp point."""
        g = Galaxy(radius=1000)
        g.generate_systems(count=10, min_dist=50)
        g.generate_warp_lanes()

        for sys in g.systems.values():
            assert len(sys.warp_points) >= 1, f"System {sys.name} has no warp points!"


class TestPlacementStrategyIntegration:
    """Integration tests for placement strategies with Galaxy."""

    def test_generate_with_explicit_random_strategy(self):
        """Generate systems with explicit RandomPlacementStrategy."""
        g = Galaxy(radius=1000)
        strategy = RandomPlacementStrategy()

        systems = g.generate_systems(count=10, min_dist=50, placement_strategy=strategy)

        assert len(systems) == 10
        assert len(g.systems) == 10

    def test_generate_with_density_strategy(self):
        """Generate systems with DensityBasedPlacementStrategy."""
        # Create a density map with a radial distribution
        dm = DensityMap(radius=500)
        dm.add_primitive(RadialPrimitive(sigma=200, peak_density=1.0))

        g = Galaxy(radius=500)
        strategy = DensityBasedPlacementStrategy(dm)
        rng = random.Random(42)

        systems = g.generate_systems(
            count=10,
            min_dist=30,
            placement_strategy=strategy,
            rng=rng
        )

        assert len(systems) >= 5  # Should get at least some systems
        assert len(g.systems) == len(systems)

        # Verify systems are within radius
        for coord in g.systems.keys():
            assert max(abs(coord.q), abs(coord.r), abs(coord.q + coord.r)) <= 500

    def test_density_strategy_clusters_near_center(self):
        """Density-based placement with tight radial should cluster near center."""
        # Create a density map with tight center
        dm = DensityMap(radius=500)
        dm.add_primitive(RadialPrimitive(sigma=50, peak_density=1.0))  # Tight peak

        g = Galaxy(radius=500)
        strategy = DensityBasedPlacementStrategy(dm)
        rng = random.Random(123)

        systems = g.generate_systems(
            count=10,
            min_dist=20,
            placement_strategy=strategy,
            rng=rng
        )

        # Most systems should be near center (within ~100 hexes)
        close_to_center = sum(
            1 for coord in g.systems.keys()
            if hex_distance(coord, HexCoord(0, 0)) < 150
        )
        # At least 50% should be close to center
        assert close_to_center >= len(systems) * 0.5

    def test_generate_with_rng_is_deterministic(self):
        """Same seed should produce same galaxy layout."""
        strategy = RandomPlacementStrategy()

        # First generation
        g1 = Galaxy(radius=500)
        rng1 = random.Random(99999)
        systems1 = g1.generate_systems(
            count=5,
            min_dist=50,
            placement_strategy=strategy,
            rng=rng1
        )

        # Second generation with same seed
        g2 = Galaxy(radius=500)
        rng2 = random.Random(99999)
        systems2 = g2.generate_systems(
            count=5,
            min_dist=50,
            placement_strategy=strategy,
            rng=rng2
        )

        # System coordinates should match
        coords1 = sorted([s.global_location for s in systems1], key=lambda c: (c.q, c.r))
        coords2 = sorted([s.global_location for s in systems2], key=lambda c: (c.q, c.r))

        assert coords1 == coords2


class TestGameSessionGalaxyType:
    """Integration tests for GameSession with different galaxy types."""

    def test_session_with_random_galaxy_type(self):
        """GameSession with galaxy_type='random' uses uniform distribution."""
        from game.strategy.engine.game_config import GameConfig
        from game.strategy.engine.game_session import GameSession

        config = GameConfig(
            galaxy_type="random",
            galaxy_radius=500,
            system_count=5,
            galaxy_seed=42
        )

        session = GameSession(config=config)

        assert len(session.systems) == 5
        assert len(session.galaxy.systems) == 5

    def test_session_with_spiral_galaxy_type(self):
        """GameSession with galaxy_type='spiral' generates systems."""
        from game.strategy.engine.game_config import GameConfig
        from game.strategy.engine.game_session import GameSession

        config = GameConfig(
            galaxy_type="spiral",
            galaxy_radius=500,
            system_count=5
        )

        session = GameSession(config=config)

        # Should generate systems (may be less than requested due to density)
        assert len(session.systems) >= 1
        assert len(session.galaxy.systems) >= 1

    def test_session_with_seed_is_deterministic(self):
        """Same seed produces same galaxy layout."""
        from game.strategy.engine.game_config import GameConfig
        from game.strategy.engine.game_session import GameSession

        config1 = GameConfig(
            galaxy_type="cluster",
            galaxy_seed=12345,
            galaxy_radius=500,
            system_count=5
        )

        config2 = GameConfig(
            galaxy_type="cluster",
            galaxy_seed=12345,
            galaxy_radius=500,
            system_count=5
        )

        session1 = GameSession(config=config1)
        session2 = GameSession(config=config2)

        # System coordinates should match
        coords1 = sorted(session1.galaxy.systems.keys(), key=lambda c: (c.q, c.r))
        coords2 = sorted(session2.galaxy.systems.keys(), key=lambda c: (c.q, c.r))

        assert coords1 == coords2

    def test_session_different_seeds_produce_different_layouts(self):
        """Different seeds produce different galaxy layouts."""
        from game.strategy.engine.game_config import GameConfig
        from game.strategy.engine.game_session import GameSession

        config1 = GameConfig(
            galaxy_type="random",
            galaxy_seed=11111,
            galaxy_radius=500,
            system_count=5
        )

        config2 = GameConfig(
            galaxy_type="random",
            galaxy_seed=22222,
            galaxy_radius=500,
            system_count=5
        )

        session1 = GameSession(config=config1)
        session2 = GameSession(config=config2)

        # System coordinates should be different
        coords1 = sorted(session1.galaxy.systems.keys(), key=lambda c: (c.q, c.r))
        coords2 = sorted(session2.galaxy.systems.keys(), key=lambda c: (c.q, c.r))

        assert coords1 != coords2
