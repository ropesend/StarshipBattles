"""
Integration tests for deterministic galaxy generation.

Verifies that same seed produces identical galaxies, including:
- System coordinates
- Star properties
- Planet properties
"""

import pytest
from game.strategy.engine.game_config import GameConfig
from game.strategy.engine.game_session import GameSession


class TestDeterministicGeneration:
    """Tests for deterministic galaxy generation with seeds."""

    def test_same_seed_produces_identical_system_coordinates(self):
        """Same seed should produce identical system coordinates."""
        config1 = GameConfig(
            galaxy_type="random",
            galaxy_seed=42424,
            galaxy_radius=500,
            system_count=10
        )
        config2 = GameConfig(
            galaxy_type="random",
            galaxy_seed=42424,
            galaxy_radius=500,
            system_count=10
        )

        session1 = GameSession(config=config1)
        session2 = GameSession(config=config2)

        coords1 = sorted(session1.galaxy.systems.keys(), key=lambda c: (c.q, c.r))
        coords2 = sorted(session2.galaxy.systems.keys(), key=lambda c: (c.q, c.r))

        assert coords1 == coords2

    def test_same_seed_produces_identical_star_counts(self):
        """Same seed should produce identical star counts per system."""
        config1 = GameConfig(
            galaxy_type="cluster",
            galaxy_seed=55555,
            galaxy_radius=500,
            system_count=5
        )
        config2 = GameConfig(
            galaxy_type="cluster",
            galaxy_seed=55555,
            galaxy_radius=500,
            system_count=5
        )

        session1 = GameSession(config=config1)
        session2 = GameSession(config=config2)

        # Compare star counts per system (by sorted coordinates)
        systems1 = sorted(session1.galaxy.systems.values(),
                         key=lambda s: (s.global_location.q, s.global_location.r))
        systems2 = sorted(session2.galaxy.systems.values(),
                         key=lambda s: (s.global_location.q, s.global_location.r))

        star_counts1 = [len(s.stars) for s in systems1]
        star_counts2 = [len(s.stars) for s in systems2]

        assert star_counts1 == star_counts2

    def test_same_seed_produces_identical_planet_counts(self):
        """Same seed should produce identical planet counts per system."""
        config1 = GameConfig(
            galaxy_type="spiral",
            galaxy_seed=77777,
            galaxy_radius=500,
            system_count=5
        )
        config2 = GameConfig(
            galaxy_type="spiral",
            galaxy_seed=77777,
            galaxy_radius=500,
            system_count=5
        )

        session1 = GameSession(config=config1)
        session2 = GameSession(config=config2)

        # Compare planet counts per system
        systems1 = sorted(session1.galaxy.systems.values(),
                         key=lambda s: (s.global_location.q, s.global_location.r))
        systems2 = sorted(session2.galaxy.systems.values(),
                         key=lambda s: (s.global_location.q, s.global_location.r))

        planet_counts1 = [len(s.planets) for s in systems1]
        planet_counts2 = [len(s.planets) for s in systems2]

        assert planet_counts1 == planet_counts2

    def test_same_seed_produces_identical_star_types(self):
        """Same seed should produce identical star types."""
        config1 = GameConfig(
            galaxy_type="ring",
            galaxy_seed=88888,
            galaxy_radius=500,
            system_count=5
        )
        config2 = GameConfig(
            galaxy_type="ring",
            galaxy_seed=88888,
            galaxy_radius=500,
            system_count=5
        )

        session1 = GameSession(config=config1)
        session2 = GameSession(config=config2)

        # Compare star types per system
        systems1 = sorted(session1.galaxy.systems.values(),
                         key=lambda s: (s.global_location.q, s.global_location.r))
        systems2 = sorted(session2.galaxy.systems.values(),
                         key=lambda s: (s.global_location.q, s.global_location.r))

        for s1, s2 in zip(systems1, systems2):
            types1 = [star.star_type.name for star in s1.stars]
            types2 = [star.star_type.name for star in s2.stars]
            assert types1 == types2

    def test_different_seeds_produce_different_galaxies(self):
        """Different seeds should produce different galaxies."""
        config1 = GameConfig(
            galaxy_type="random",
            galaxy_seed=11111,
            galaxy_radius=500,
            system_count=10
        )
        config2 = GameConfig(
            galaxy_type="random",
            galaxy_seed=99999,
            galaxy_radius=500,
            system_count=10
        )

        session1 = GameSession(config=config1)
        session2 = GameSession(config=config2)

        coords1 = sorted(session1.galaxy.systems.keys(), key=lambda c: (c.q, c.r))
        coords2 = sorted(session2.galaxy.systems.keys(), key=lambda c: (c.q, c.r))

        # At least some coordinates should differ
        assert coords1 != coords2

    def test_no_seed_produces_varying_galaxies(self):
        """Without seed, galaxies should vary (non-deterministic)."""
        config1 = GameConfig(
            galaxy_type="random",
            galaxy_radius=500,
            system_count=5
        )
        config2 = GameConfig(
            galaxy_type="random",
            galaxy_radius=500,
            system_count=5
        )

        session1 = GameSession(config=config1)
        session2 = GameSession(config=config2)

        coords1 = sorted(session1.galaxy.systems.keys(), key=lambda c: (c.q, c.r))
        coords2 = sorted(session2.galaxy.systems.keys(), key=lambda c: (c.q, c.r))

        # Highly likely to be different (not guaranteed but statistically certain)
        # Note: This test could theoretically fail with astronomically low probability
        # If it fails, re-run - if it fails consistently, there's a bug
        assert coords1 != coords2

    def test_all_galaxy_types_work_with_seed(self):
        """All galaxy types should work with seeded generation."""
        galaxy_types = ["random", "cluster", "spiral", "barred_spiral",
                       "ring", "irregular", "diamond", "uniform"]

        for gtype in galaxy_types:
            config = GameConfig(
                galaxy_type=gtype,
                galaxy_seed=12345,
                galaxy_radius=300,
                system_count=3
            )

            # Should not raise
            session = GameSession(config=config)

            # Should have generated at least some systems
            assert len(session.systems) >= 1, f"Galaxy type {gtype} failed to generate systems"
