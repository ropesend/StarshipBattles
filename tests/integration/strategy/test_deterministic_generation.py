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


def _sorted_systems(session):
    """Sort a session's systems by global hex coordinates for stable
    pairwise comparison across two seeded sessions."""
    return sorted(
        session.galaxy.systems.values(),
        key=lambda s: (s.global_location.q, s.global_location.r),
    )


def _extract_coords(session):
    return sorted(session.galaxy.systems.keys(), key=lambda c: (c.q, c.r))


def _extract_star_counts(session):
    return [len(s.stars) for s in _sorted_systems(session)]


def _extract_planet_counts(session):
    return [len(s.planets) for s in _sorted_systems(session)]


def _extract_star_types(session):
    return [
        [star.star_type.name for star in s.stars]
        for s in _sorted_systems(session)
    ]


# PROJ-496 T2.2 (origin PROJ-480 T3.31): the 4 same-seed determinism
# tests have identical structure — build two sessions with identical
# config, extract some attribute, compare. They differ only in
# (galaxy_type, seed, system_count, attribute_getter). Parametrize.
_DETERMINISTIC_GEN_CASES = [
    ("random",  42424, 10, _extract_coords),
    ("cluster", 55555,  5, _extract_star_counts),
    ("spiral",  77777,  5, _extract_planet_counts),
    ("ring",    88888,  5, _extract_star_types),
]


class TestDeterministicGeneration:
    """Tests for deterministic galaxy generation with seeds."""

    @pytest.mark.parametrize(
        "galaxy_type,seed,system_count,attribute_getter",
        _DETERMINISTIC_GEN_CASES,
        ids=[
            f"{gtype}-{attr.__name__.removeprefix('_extract_')}"
            for gtype, _, _, attr in _DETERMINISTIC_GEN_CASES
        ],
    )
    def test_same_seed_produces_identical_galaxy_attribute(
        self, galaxy_type, seed, system_count, attribute_getter
    ):
        """Same seed + same config produces identical attribute under
        all sampled galaxy types and attribute extractors."""
        config1 = GameConfig(
            galaxy_type=galaxy_type,
            galaxy_seed=seed,
            galaxy_radius=500,
            system_count=system_count,
        )
        config2 = GameConfig(
            galaxy_type=galaxy_type,
            galaxy_seed=seed,
            galaxy_radius=500,
            system_count=system_count,
        )

        session1 = GameSession(config=config1)
        session2 = GameSession(config=config2)

        assert attribute_getter(session1) == attribute_getter(session2)

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
